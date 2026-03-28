# Distributed Systems Theory for Interviews

## Table of Contents
- [Core Concepts](#core-concepts)
- [CAP Theorem and Consistency](#cap-theorem-and-consistency)
- [Transactions and Isolation](#transactions-and-isolation)
- [Consensus and Coordination](#consensus-and-coordination)
- [Clocks and Ordering](#clocks-and-ordering)
- [Batch and Stream Processing](#batch-and-stream-processing)
- [Encoding and Schema Evolution](#encoding-and-schema-evolution)
- [Common Interview Scenarios](#common-interview-scenarios)

---

## Core Concepts

### The Fundamental Problem with Distributed Systems
When you have multiple machines communicating over a network, three things can go wrong:
1. **Networks are unreliable**: Packets get lost, delayed, duplicated, or reordered. You can't distinguish a crashed node from a slow one from a network partition.
2. **Clocks are unreliable**: Different machines have different times. NTP synchronization has millisecond-level error. Clocks can jump forward or backward.
3. **Processes pause unpredictably**: Garbage collection, VM migration, context switches, disk I/O can pause a process for seconds. During the pause, its locks/leases may expire.

**The key insight**: In a distributed system, a node can't trust its own judgment. Decisions must be made by a quorum (majority) of nodes. A node can't declare itself leader or declare another node dead — a majority must agree.

### Why This Matters for Our Stack
Even though we primarily use managed services (EKS, RDS), these problems surface everywhere:
- EKS pod talking to RDS: What timeout do you set? What happens if the connection drops mid-transaction?
- Multiple pods handling the same queue message: How do you prevent duplicate processing?
- Read replicas lagging behind: A user writes data and immediately reads stale results from a replica.
- Rolling deployment: Old and new versions of your service running simultaneously with different schemas.

---

## CAP Theorem and Consistency

### What CAP Actually Says
In the presence of a **network partition** (some nodes can't communicate with others), you must choose:
- **Consistency** (C): Every read returns the most recent write (linearizability)
- **Availability** (A): Every request receives a response (even if it might be stale)

You can't have both during a partition. When the network is healthy, you can have both.

### More Useful Framing: PACELC
- During **Partition**: Choose **Availability** or **Consistency**
- **Else** (normal operation): Choose **Latency** or **Consistency**

This captures the real trade-off: even without partitions, strong consistency costs latency because
you need to coordinate between nodes.

### How This Maps to Our Stack
- **RDS PostgreSQL primary**: Strongly consistent (CP). Writes go to one leader. If the primary fails, Multi-AZ failover takes 60-120 seconds (brief unavailability for consistency).
- **RDS read replicas**: Eventually consistent (AP). Reads are available and fast but may be stale.
- **ElastiCache Redis**: Typically AP. Fast reads, but cached data may be stale.
- **SQS**: Provides at-least-once delivery — your consumer must be idempotent.

**Interview framing**: "We use strong consistency (reading from the primary) for operations where correctness matters — like uniqueness checks or financial calculations. For everything else — dashboards, search results, profile pages — we read from replicas or caches where eventual consistency is acceptable and gives us better latency and availability."

---

## Transactions and Isolation

### ACID Quick Reference
- **Atomicity**: All writes in a transaction succeed or all are rolled back. Not about concurrency — about abortability.
- **Consistency**: Application invariants are maintained. This is actually an application property, not a database property.
- **Isolation**: Concurrent transactions don't interfere with each other.
- **Durability**: Committed data survives crashes. In RDS: WAL written to disk + replicated to standby.

### Isolation Levels (PostgreSQL)

**Read Committed** (PostgreSQL default):
- No dirty reads (you only see committed data)
- No dirty writes (you can't overwrite uncommitted data)
- Vulnerable to: non-repeatable reads (read same row twice, get different results)

**Repeatable Read** (Snapshot Isolation):
- Each transaction sees a snapshot from its start time
- Uses MVCC — no read locks, readers never block writers
- Vulnerable to: write skew (two transactions read overlapping data, make decisions, write to different rows, combined result violates an invariant)

**Serializable** (SSI — Serializable Snapshot Isolation):
- Prevents all anomalies including write skew and phantoms
- Optimistic: transactions proceed without blocking, checked at commit time
- Higher abort rate under contention (aborted transactions must be retried)
- Use for: inventory reservation, seat booking, financial transfers

### Write Skew Example (Classic Interview Question)
Two doctors are on call. Both check "are at least 2 doctors on call?" (yes, there are 2). Both
decide to go off call. Result: zero doctors on call, violating the invariant.

**Fix**: Use SERIALIZABLE isolation, or use explicit locking (`SELECT ... FOR UPDATE`), or restructure
to avoid the race (single row that tracks on-call count).

### Distributed Transactions
When a single business operation spans multiple services or databases:

**Two-Phase Commit (2PC)**: Coordinator asks all participants to prepare, then commit. Problem: if
coordinator crashes after prepare, participants are stuck holding locks indefinitely. Blocks on
coordinator failure.

**Saga Pattern** (preferred in microservices):
Each step is a local transaction with a compensating transaction:
1. Create order (compensate: cancel order)
2. Reserve inventory (compensate: release inventory)
3. Charge payment (compensate: refund payment)
If step 3 fails, run compensating transactions for steps 2 and 1.
Eventually consistent, but doesn't block.

**Durable Execution** (Temporal, Step Functions):
Record each step's completion. If process crashes, resume from last checkpoint. Cleaner programming
model than sagas for complex workflows.

---

## Consensus and Coordination

### What Consensus Solves
Getting multiple nodes to agree on a value, even when some nodes fail. Enables:
- **Leader election**: Exactly one leader at a time
- **Distributed locks**: Mutual exclusion across nodes
- **Total order broadcast**: All nodes process events in the same order
- **Atomic commit**: All nodes commit or all abort

### Raft (Most Common in Practice)
- A leader is elected by majority vote
- Leader accepts writes and replicates to followers
- If leader fails, a new election happens (brief period of unavailability)
- Used by: etcd (which backs Kubernetes), CockroachDB, Consul

### Coordination Services (etcd, ZooKeeper, Consul)
Provide consensus-backed primitives so your application doesn't implement consensus directly:
- Leader election (e.g., which pod is the "primary" for a singleton job)
- Distributed locks (but be careful about lock expiry during pauses — use fencing tokens)
- Configuration management (consistent config across all nodes)
- Service discovery

**In our stack**: etcd backs the Kubernetes control plane. We rarely interact with it directly.
For distributed locking, prefer database-level constraints (PostgreSQL advisory locks) or
SQS FIFO queues with deduplication over building custom distributed locks.

### Fencing Tokens
When using distributed locks, a process might acquire a lock, pause (GC), and resume after the
lock expired and was given to another process. Both processes now think they have the lock.

**Solution**: The lock service issues a monotonically increasing fencing token with each lock grant.
Every write includes the token. The storage system rejects writes with old tokens.

---

## Clocks and Ordering

### Two Types of Clocks
- **Time-of-day clocks** (`System.currentTimeMillis()`): Synchronized via NTP, but can jump forward or backward. Not safe for ordering events across machines.
- **Monotonic clocks** (`System.nanoTime()`): Only move forward. Good for measuring elapsed time on a single machine. Not synchronized across machines.

### Ordering Events Across Services
Never use wall-clock timestamps to determine the order of events on different machines.

**Lamport timestamps**: Each node increments a counter. On receiving a message, advance to max(local, received) + 1. Gives a total order but can't distinguish concurrent from sequential events.

**Vector clocks / version vectors**: Each node maintains a counter per known node. Can detect truly concurrent operations (neither happened-before the other). Used for conflict detection.

**In practice for our stack**:
- PostgreSQL sequences provide total ordering within a single database
- Kafka offsets provide total ordering within a partition
- For cross-service ordering, use a centralized sequencer (PostgreSQL sequence) or accept that events may arrive out of order and handle it

---

## Batch and Stream Processing

### Batch Processing
Takes a bounded input dataset, produces a new output dataset. Input is immutable.

**Key insight**: Because input is immutable, batch jobs are inherently fault-tolerant — if they fail,
just rerun them. No side effects to undo.

**In our stack**: AWS Batch, EKS CronJobs, Step Functions for orchestration. Data in S3 (Parquet/CSV),
processed by Python/Spark, results back to S3 or loaded into PostgreSQL/Redshift.

### Stream Processing
Continuous processing of unbounded data.

**In our stack**: Amazon MSK (Kafka) or SQS for messaging, EKS pods as consumers.

**Key patterns**:
- **CDC (Change Data Capture)**: Capture database changes as a stream. Use to sync search indexes, caches, data warehouses with the primary database. Debezium reads the PostgreSQL WAL.
- **Event-driven architecture**: Services communicate via events rather than synchronous API calls. Loose coupling, better fault isolation, natural audit trail.
- **Exactly-once processing**: Actually means at-least-once delivery + idempotent consumers. Include a deduplication ID with each message.

### Stream Joins
- **Stream-stream join**: Correlate events from two streams within a time window (e.g., match login attempts with access logs within 5 minutes)
- **Stream-table join (enrichment)**: Enrich stream events with data from a table (e.g., look up user details for each event). Keep a local cache of the table, updated via CDC.

---

## Encoding and Schema Evolution

### Why It Matters
In a rolling deployment, old and new versions of your service coexist. They must be able to
read each other's data.

- **Forward compatibility**: Old code reads data written by new code (ignores unknown fields)
- **Backward compatibility**: New code reads data written by old code (new fields have defaults)

### Format Comparison
| Format | Schema Evolution | Compactness | Our Use Cases |
|--------|-----------------|-------------|---------------|
| JSON | Weak (no enforcement) | Poor | REST APIs, config files |
| Protocol Buffers | Strong (field tags) | Good | gRPC between services (if we adopt gRPC) |
| Avro | Strong (schema resolution) | Best | Data pipelines, Kafka messages |
| PostgreSQL schema | Strong (ALTER TABLE) | N/A | Primary data storage |

### Database Schema Evolution
The database contains data written by every version of your application that ever existed.
- Add columns as nullable or with defaults (safe, fast in PostgreSQL 11+)
- Don't rename or change column types directly on large tables — add new column, backfill, swap
- Application must handle both old and new schemas during rolling deployments
- Use migration tools (Flyway, golang-migrate, Alembic) with version tracking

---

## Common Interview Scenarios

### "Design a URL Shortener"
- **Data model**: PostgreSQL table with `short_code` (indexed, unique) and `long_url`. Generate short codes with a counter or hash.
- **Read-heavy**: ElastiCache Redis for hot URLs, PostgreSQL read replicas for the rest.
- **Scale**: A single RDS instance handles millions of redirects/day. Redis handles the hot path.
- **Compliance**: If URLs contain CUI, encrypt at rest, audit access logs.

### "Design a Notification System"
- **Async by nature**: SQS/SNS for delivery. Don't block the user action on notification delivery.
- **Fan-out**: SNS topic → multiple SQS queues (email worker, push worker, in-app worker).
- **Deduplication**: Idempotency key per notification to prevent duplicate delivery.
- **Preferences**: PostgreSQL table for user notification preferences, cached in Redis.

### "Design a File Upload Service"
- **Pre-signed S3 URLs**: Client uploads directly to S3 (never through your API pods — they'd become a bottleneck).
- **Metadata**: PostgreSQL stores file metadata (owner, name, size, S3 key). The file itself is in S3.
- **Scanning**: S3 event → SQS → scanner pod (antivirus/malware check before making available).
- **Compliance**: S3 server-side encryption with KMS. Bucket policy denies unencrypted uploads. VPC endpoint for S3 access.

### "Design a Real-Time Dashboard"
- **Data collection**: Application pods expose Prometheus metrics. Custom business metrics via StatsD or direct Prometheus instrumentation.
- **For live data**: WebSocket connection from browser to API pod, or Server-Sent Events (SSE).
- **For historical data**: Prometheus for short-term (15-30 days), push to S3/Athena for long-term analytics.
- **Visualization**: Grafana for operational dashboards. Custom frontend (React + chart library) for user-facing dashboards.

### "How Would You Handle a Database Migration to a New Schema?"
1. **Expand**: Add new columns/tables (backward compatible). Deploy new app version that writes to both old and new.
2. **Migrate**: Backfill data from old to new columns. Verify data integrity.
3. **Contract**: Deploy app version that reads/writes only from new schema. Drop old columns.
4. **In our stack**: Terraform manages RDS. Migration tool (Flyway) runs as a Kubernetes Job before app deployment via FluxCD. Test against production-sized replica first.
