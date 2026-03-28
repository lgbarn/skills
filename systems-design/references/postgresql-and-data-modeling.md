# PostgreSQL and Data Modeling

## Table of Contents
- [Why PostgreSQL First](#why-postgresql-first)
- [Data Modeling Patterns](#data-modeling-patterns)
- [Indexing Strategies](#indexing-strategies)
- [PostgreSQL Internals That Matter](#postgresql-internals-that-matter)
- [Connection Management](#connection-management)
- [Partitioning](#partitioning)
- [RDS vs. Aurora PostgreSQL](#rds-vs-aurora-postgresql)
- [Schema Migration Patterns](#schema-migration-patterns)
- [When to Reach Beyond PostgreSQL](#when-to-reach-beyond-postgresql)

---

## Why PostgreSQL First

In our IL2/IL4 AWS environment, PostgreSQL (via RDS or Aurora) is the default choice because:
- FedRAMP-authorized on AWS GovCloud
- Mature ACID transactions with strong isolation levels (including true serializable via SSI)
- Rich feature set reduces the need for additional databases:
  - JSONB for semi-structured/document data
  - Full-text search (tsvector/tsquery) for basic search needs
  - PostGIS for geospatial data
  - pgvector for vector/similarity search (RAG, semantic search)
  - Array and hstore types for flexible schemas
  - CTEs and window functions for complex queries
  - LISTEN/NOTIFY for simple pub/sub
- Excellent AWS integration (automated backups, Multi-AZ failover, read replicas, IAM auth)

**The interview instinct**: When someone asks "what database should I use?", start with PostgreSQL
and articulate specific reasons to add anything else. This shows maturity — junior engineers reach
for specialized databases too early.

---

## Data Modeling Patterns

### Normalize First, Denormalize When Measured
Start with Third Normal Form (3NF). Denormalization is an optimization — you need to know what
queries are slow before you can optimize them.

**Normalization benefits**: No data duplication, consistent updates, smaller tables fit in cache.
**Denormalization benefits**: Fewer joins for read-heavy queries, better locality.

### Star and Snowflake Schemas (Analytics)
For analytical/reporting workloads:
- **Fact table**: One row per event (transaction, page view, sensor reading). Contains foreign keys
  to dimension tables and numeric measures.
- **Dimension tables**: Descriptive attributes (who, what, where, when, how).
- **Star schema**: Fact table directly references dimension tables (simpler queries, some redundancy).
- **Snowflake schema**: Dimension tables are further normalized (less redundancy, more joins).

In our context, analytical queries often run against read replicas to avoid impacting OLTP workloads.

### JSONB for Flexibility
PostgreSQL's JSONB type gives you document-database flexibility within a relational model:
- Store semi-structured data alongside relational columns
- GIN indexes on JSONB for efficient querying
- Useful for: configuration blobs, audit metadata, user preferences, varying attributes

```sql
-- Example: storing flexible metadata alongside structured data
CREATE TABLE missions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    region TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for querying into JSONB
CREATE INDEX idx_missions_metadata ON missions USING GIN (metadata);

-- Query JSONB fields
SELECT * FROM missions WHERE metadata->>'priority' = 'high';
```

**When JSONB is NOT the answer**: If you're querying the same JSONB fields repeatedly, those should
probably be proper columns with proper indexes. JSONB is for truly variable data.

### Event Sourcing Pattern in PostgreSQL
Store events as the source of truth, derive current state via materialized views:

```sql
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    aggregate_id UUID NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Materialized view for current state
CREATE MATERIALIZED VIEW current_status AS
SELECT DISTINCT ON (aggregate_id)
    aggregate_id, event_type, payload, created_at
FROM events
ORDER BY aggregate_id, created_at DESC;
```

Benefits: Full audit trail (critical for compliance), reproducible state, temporal queries.
Cost: More storage, need to maintain materialized views, queries against the event log are slower.

---

## Indexing Strategies

### B-Tree (Default)
- Best for: equality and range queries, ORDER BY, UNIQUE constraints
- The default index type — use unless you have a specific reason not to

### GIN (Generalized Inverted Index)
- Best for: JSONB queries, full-text search, array containment
- Slower to update than B-tree, but very fast for lookups on multi-valued columns

### GiST (Generalized Search Tree)
- Best for: Geometric/spatial data (PostGIS), range types, full-text search
- Supports "nearest neighbor" queries

### BRIN (Block Range Index)
- Best for: Large tables where data is physically ordered (e.g., time-series by timestamp)
- Very small index size — stores min/max per block range
- Useless if data isn't physically correlated with the indexed column

### Partial Indexes
Index only the rows that matter:
```sql
CREATE INDEX idx_active_missions ON missions (status) WHERE status = 'active';
```
Dramatically smaller index for queries that always filter by a specific condition.

### Covering Indexes (INCLUDE)
Avoid table lookups by including extra columns in the index:
```sql
CREATE INDEX idx_missions_region ON missions (region) INCLUDE (name, status);
```
Queries that only need region, name, and status can be answered entirely from the index.

### Interview Tip
When discussing indexing, mention: "I'd look at `pg_stat_user_indexes` and `pg_stat_user_tables`
to identify unused indexes and sequential scans before adding new ones. Indexes speed up reads
but slow down writes and consume storage."

---

## PostgreSQL Internals That Matter

### MVCC (Multi-Version Concurrency Control)
PostgreSQL doesn't lock rows for reads. Instead, each transaction sees a snapshot of the database
at its start time. Writers create new row versions; old versions are kept until no transaction needs them.

**Why this matters**: Reads never block writes, writes never block reads. But dead row versions
accumulate and must be cleaned up by VACUUM.

### VACUUM and Autovacuum
Dead rows (from updates and deletes) consume space and slow down queries. VACUUM reclaims this space.
Autovacuum runs automatically but may need tuning for write-heavy tables:
- Increase `autovacuum_vacuum_scale_factor` for large tables
- Monitor `n_dead_tup` in `pg_stat_user_tables`
- Transaction ID wraparound prevention — if autovacuum can't keep up, PostgreSQL will refuse writes

### WAL (Write-Ahead Log)
Every write goes to the WAL before being applied to data files. This ensures durability (crash
recovery) and powers replication (followers read the WAL to stay in sync).

### TOAST (The Oversized-Attribute Storage Technique)
Large column values (>2KB) are automatically compressed and stored out-of-line. Relevant for JSONB
columns with large payloads — queries that don't access the JSONB column don't pay the I/O cost.

---

## Connection Management

PostgreSQL forks a process per connection. With many EKS pods (say 50 pods × 10 connections each = 500),
you'll exhaust the instance's connection limit or waste memory on idle connections.

**PgBouncer** (recommended):
- Connection pooler that sits between your app and PostgreSQL
- Transaction-mode pooling: connections returned to pool after each transaction
- Deploy as a sidecar in EKS or as a separate deployment
- Reduces database connections from hundreds to tens

**RDS Proxy** (AWS managed alternative):
- Fully managed, integrates with IAM authentication
- Handles failover transparently (connections pinned to new primary)
- Higher latency than PgBouncer but zero operational overhead
- Good for serverless/Lambda workloads; for EKS, PgBouncer is usually preferred

---

## Partitioning

PostgreSQL native table partitioning (not to be confused with sharding across multiple databases):

**Range partitioning** (most common):
```sql
CREATE TABLE sensor_data (
    id BIGSERIAL,
    sensor_id UUID,
    reading DOUBLE PRECISION,
    recorded_at TIMESTAMPTZ
) PARTITION BY RANGE (recorded_at);

CREATE TABLE sensor_data_2025_q1 PARTITION OF sensor_data
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
```

**Benefits**: Efficient queries on the partition key (partition pruning), fast bulk deletes
(drop a partition instead of DELETE), independent maintenance (VACUUM one partition at a time).

**When to partition**: Tables over ~100GB, or when you need to efficiently purge old data.
Don't partition small tables — it adds overhead with no benefit.

---

## RDS vs. Aurora PostgreSQL

| Feature | RDS PostgreSQL | Aurora PostgreSQL |
|---------|---------------|-------------------|
| **Storage** | EBS-backed, manual sizing | Auto-scaling up to 128TB, replicated 6 ways across 3 AZs |
| **Failover** | Multi-AZ: ~60-120s | ~30s, reader promotion is faster |
| **Read replicas** | Up to 5, async replication with lag | Up to 15, shared storage (typically <100ms lag) |
| **Cost** | Lower baseline | ~20% more expensive, but savings from auto-scaling storage |
| **Compatibility** | Exact PostgreSQL | Mostly compatible, occasional edge-case differences |
| **Global** | Cross-region read replicas | Aurora Global Database (dedicated replication, <1s lag) |

**Recommendation**: Start with RDS PostgreSQL for most workloads. Move to Aurora when you need:
faster failover, more read replicas, auto-scaling storage, or multi-region replication.

---

## Schema Migration Patterns

**Never run raw ALTER TABLE on production without planning.**

For large tables, schema changes can lock the table. Strategies:
- Use `CREATE INDEX CONCURRENTLY` (doesn't lock writes, takes longer)
- Add columns as nullable or with defaults (fast in PostgreSQL 11+, no table rewrite needed)
- For column type changes on large tables, create a new column → backfill → swap → drop old
- Use migration tools: Flyway, golang-migrate, Alembic, or Django migrations
- Test migrations against a production-sized replica first

**In our Terraform/FluxCD workflow**: Database migrations should be a separate deployment step from
application deployment. The application should handle both old and new schemas during the rollout
(forward and backward compatibility).

---

## When to Reach Beyond PostgreSQL

| Symptom | Consider | Why |
|---------|----------|-----|
| Read latency under 1ms needed for hot data | ElastiCache Redis | In-memory, sub-ms reads. Use for sessions, feature flags, rate limiting, hot caches |
| Complex search with facets, fuzzy matching, relevance scoring at scale | OpenSearch | Purpose-built inverted indexes, better query DSL for search UIs |
| High-throughput event streaming, multiple consumers, replay | Amazon MSK (Kafka) | Log-based broker with partitioned topics, consumer groups, retention |
| Millions of writes/sec with simple key-value access | DynamoDB | Single-digit-ms at any scale, but limited query flexibility |
| Large-scale analytics across petabytes | Redshift or Athena (S3 + Glue) | Columnar storage, massively parallel query execution |
| Graph traversals with many hops | Neptune | Purpose-built graph engine, but evaluate if PostgreSQL recursive CTEs suffice first |
