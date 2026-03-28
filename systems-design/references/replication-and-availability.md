# Replication and Availability

## Table of Contents
- [Replication Concepts](#replication-concepts)
- [PostgreSQL Replication on AWS](#postgresql-replication-on-aws)
- [EKS High Availability](#eks-high-availability)
- [Consistency Models](#consistency-models)
- [Failure Handling Patterns](#failure-handling-patterns)
- [Conflict Resolution](#conflict-resolution)

---

## Replication Concepts

### Why Replicate?
1. **High availability**: If one node fails, another takes over (reduce downtime)
2. **Read scaling**: Distribute read queries across replicas (increase throughput)
3. **Geographic distribution**: Place data closer to users (reduce latency)

### Three Replication Strategies

**Single-leader** (what RDS PostgreSQL uses):
- One primary accepts all writes, replicates to followers via WAL streaming
- Followers serve read queries (may lag behind primary)
- Failover required when primary fails — automatic in RDS Multi-AZ

**Multi-leader** (Aurora Global Database, cross-region):
- Multiple nodes accept writes independently
- Changes replicate asynchronously between leaders
- Conflicts are possible when the same data is modified on multiple leaders concurrently
- Use case: Multi-region active-active deployment

**Leaderless** (DynamoDB-style):
- Any replica accepts reads and writes
- Quorum-based: with n replicas, write to w and read from r where w + r > n
- No failover needed — inherently resilient to individual node failures
- Trade-off: weaker consistency guarantees, need conflict resolution

### Synchronous vs. Asynchronous Replication
- **Synchronous**: Primary waits for replica to confirm write. Guarantees no data loss on failover, but higher write latency and blocks if replica is down.
- **Asynchronous**: Primary doesn't wait. Lower latency, higher throughput, but replica may lag. Failover can lose recent writes.
- **Semi-synchronous** (RDS Multi-AZ): One standby is synchronous (zero data loss on failover), other read replicas are asynchronous.

---

## PostgreSQL Replication on AWS

### RDS Multi-AZ (High Availability)
- Synchronous standby replica in a different Availability Zone
- Automatic failover (~60-120 seconds) — DNS endpoint switches to standby
- The standby is NOT a read replica — it doesn't serve read traffic
- This is your baseline for production. Always enable Multi-AZ.

### RDS Read Replicas (Read Scaling)
- Up to 5 asynchronous read replicas per instance
- Can be in same region or cross-region
- Replica lag is typically seconds but can spike under heavy write load
- Application must route reads explicitly (use a read-only connection string)
- Can be promoted to standalone instance (for disaster recovery or migration)

**Important**: Read replicas are eventually consistent. If your application wrote data and immediately
reads it, the read replica may not have it yet. Route reads-after-writes to the primary, or use
session-level stickiness.

### Aurora PostgreSQL Replication
- Shared storage layer replicated 6 ways across 3 AZs (no WAL shipping for replication)
- Up to 15 read replicas with typically <100ms replica lag
- Any reader can be promoted to writer in ~30 seconds
- Reader endpoint auto-balances reads across replicas
- Aurora Global Database: cross-region replication with <1 second lag, dedicated replication infrastructure

### Replication Lag Monitoring
Monitor replication lag in Prometheus/Grafana:
- RDS CloudWatch metric: `ReplicaLag` (seconds behind primary)
- Alert if lag exceeds your consistency tolerance (e.g., >5 seconds)
- Investigate causes: heavy write load, long-running queries on replica, network issues, insufficient replica instance size

---

## EKS High Availability

### Multi-AZ Pod Distribution
- Configure node groups across multiple AZs (minimum 2, prefer 3)
- Use pod topology spread constraints to distribute pods evenly across AZs:
  ```yaml
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
  ```
- Pod Disruption Budgets (PDB) ensure minimum availability during node drains/updates

### Scaling Layers
1. **HPA (Horizontal Pod Autoscaler)**: Scale pod replicas based on metrics (CPU, memory, custom Prometheus metrics like request rate)
2. **Cluster Autoscaler / Karpenter**: Add/remove EC2 nodes when pods can't be scheduled
3. **VPA (Vertical Pod Autoscaler)**: Right-size pod resource requests (use in recommendation mode, not auto-update, to avoid restarts)

### Health Checks
- **Liveness probe**: "Is this container stuck?" If it fails repeatedly, Kubernetes restarts the container. Use for detecting deadlocks/hangs. Don't point at downstream dependencies — a database outage shouldn't restart all your pods.
- **Readiness probe**: "Can this container serve traffic?" If it fails, Kubernetes stops routing traffic to it. Use for startup warmup and dependency checks.
- **Startup probe**: "Has this container finished starting?" Gives slow-starting containers time before liveness/readiness kick in.

---

## Consistency Models

### Strong Consistency (Linearizability)
Every read returns the most recent write, as if there's a single copy of the data.

**Where you need it** (and should read from the PostgreSQL primary):
- Uniqueness constraints (e.g., one username per user)
- Financial balances and inventory counts
- Leader election (exactly one leader at a time)
- Anything where reading stale data could violate an invariant

### Eventual Consistency
Replicas will converge to the same state eventually, but reads may return stale data.

**Where it's acceptable** (and you can read from replicas):
- Dashboard/reporting data (a few seconds of lag is fine)
- User profile display (stale by a few seconds is invisible to users)
- Search results (index lag is expected)
- Caches (by definition, serve stale data)

### Read-After-Write Consistency
After a user writes data, they should immediately see their own write. Other users may see it later.

**Implementation in our stack**: After a write to the primary, route that user's subsequent reads
to the primary for a short window (e.g., 5 seconds), then fall back to read replicas.

### Monotonic Reads
A user should never see data "go backward" — once they've seen a value, they shouldn't see an
older value. Solution: pin a user's reads to a specific replica (e.g., hash user ID to replica).

---

## Failure Handling Patterns

### Timeout Design
There is no "correct" timeout value. Too short causes false positives (healthy service declared dead).
Too long means slow failure detection.

- Set timeouts based on observed p99 latency + margin (e.g., if p99 is 200ms, timeout at 1-2s)
- Use different timeouts for different operations (database queries vs. external API calls)
- Always have a timeout — never wait indefinitely

### Retries
- Only retry idempotent operations (GET requests, operations with deduplication keys)
- Exponential backoff with jitter: `delay = min(base * 2^attempt + random_jitter, max_delay)`
- Limit retry attempts (3-5 is typical)
- Don't retry on client errors (4xx) — only on transient server errors (5xx) and timeouts

### Circuit Breakers
When a downstream service is failing, stop sending requests to it:
- **Closed** (normal): Requests flow through. Track error rate.
- **Open** (tripped): Requests fail immediately. After a timeout, move to half-open.
- **Half-open** (testing): Allow a few requests through. If they succeed, close the circuit.

This prevents cascading failures — a slow database shouldn't cause all your API pods to time out
and exhaust their thread pools.

### Idempotency
Design operations so that processing them twice has the same effect as processing them once.
Critical for retries, exactly-once processing, and failure recovery.

**Pattern**: Client generates a unique idempotency key (UUID) with each request. Server checks if
it's already processed that key before executing the operation.

```
POST /api/transfers
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
```

---

## Conflict Resolution

Relevant when using multi-leader replication or eventually consistent systems.

### Last Write Wins (LWW)
Attach a timestamp to each write; latest timestamp wins. Simple but causes silent data loss when
concurrent writes happen. Only acceptable when writes are truly independent.

### Application-Level Resolution
Present conflicting versions to application logic that understands the domain semantics.
E.g., for a shopping cart, merge by taking the union of items.

### CRDTs (Conflict-Free Replicated Data Types)
Data structures that merge automatically without conflicts:
- **G-Counter**: Grow-only counter (each node tracks its own count, sum for total)
- **PN-Counter**: Counter that supports increment and decrement
- **LWW-Register**: Single value with timestamp (same as LWW)
- **OR-Set**: Set where concurrent add and remove of the same element preserves the add

Used by: Redis Enterprise, Automerge (local-first apps), Yjs (collaborative editing).

### In Our Context
Most of our systems use single-leader PostgreSQL replication, so conflicts are rare — the primary
serializes all writes. Conflicts become relevant when:
- Building offline-capable applications (sync engines)
- Multi-region active-active deployments
- Eventually consistent caches that may serve stale data alongside fresher writes
