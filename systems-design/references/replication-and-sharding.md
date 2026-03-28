# Replication and Sharding

## Table of Contents
- [Replication Strategies](#replication-strategies)
- [Consistency Models for Replication](#consistency-models-for-replication)
- [Conflict Resolution](#conflict-resolution)
- [Sharding (Partitioning)](#sharding-partitioning)

---

## Replication Strategies

### Single-Leader Replication
One node (leader) accepts all writes. Followers replicate from the leader's write-ahead log.

**Synchronous vs. asynchronous replication**:
- Synchronous: Follower confirms write before leader reports success. Guarantees up-to-date copy
  but blocks writes if follower is slow/down.
- Asynchronous: Leader doesn't wait for followers. Higher throughput but followers may lag.
- Semi-synchronous: One follower is synchronous (guarantees at least one up-to-date copy), rest async.

**Setting up new followers**: Take a consistent snapshot of the leader, copy to the new follower,
then the follower requests all changes since the snapshot's position in the replication log.

**Failover challenges**:
- Detecting leader failure (timeouts are imprecise — too short causes unnecessary failovers, too long
  means longer downtime)
- Choosing a new leader (the follower with the most up-to-date data)
- Split-brain risk: Two nodes both believe they are leader. Fencing mechanisms are essential.
- Asynchronous followers may lose unreplicated writes after failover

**Replication log implementations**:
- Statement-based: Replay SQL statements (problematic with nondeterministic functions like NOW())
- WAL shipping: Send raw write-ahead log bytes (tied to storage engine version)
- Logical (row-based): Send row-level changes (INSERT/UPDATE/DELETE with column values) — most flexible
- Trigger-based: Application-level replication via database triggers (most flexible but highest overhead)

### Multi-Leader Replication
Multiple nodes accept writes independently and replicate to each other asynchronously.

**Use cases**:
- **Multi-datacenter operation**: One leader per datacenter, local writes with async cross-DC replication.
  Better latency and availability than single-leader, but conflicts are inevitable.
- **Sync engines and local-first software**: Each device has a local database that acts as a leader.
  Changes sync when connectivity is available. Days or weeks of offline operation create many conflicts
  that must be resolved automatically.
- **Collaborative editing**: Real-time collaboration (Google Docs, Figma) where each user's edits are
  immediately applied locally and then merged with others.

**The fundamental challenge**: Concurrent writes to the same data on different leaders create conflicts
that must be detected and resolved.

### Leaderless Replication
Any replica accepts reads and writes directly. No failover needed.

**Quorum reads and writes**: With n replicas, require w successful writes and r successful reads
where w + r > n. This ensures at least one read hits an up-to-date replica.

Common configuration: n=3, w=2, r=2 (tolerates 1 unavailable node).
Higher availability: n=5, w=3, r=3 (tolerates 2 unavailable nodes).

**Catching up on missed writes**:
- **Read repair**: Client detects stale values during reads and writes newer value back to stale replica
- **Hinted handoff**: Another replica stores writes on behalf of an unavailable replica, hands them off when it recovers
- **Anti-entropy**: Background process periodically syncs differences between replicas

**Limitations of quorum consistency** (even with w + r > n):
- Concurrent writes may be processed in different orders on different nodes
- A failed write may succeed on some replicas and not be rolled back
- Reads concurrent with writes may see inconsistent results
- Clock skew can cause LWW to silently drop writes
- Rebalancing can temporarily break quorum overlap

**Sloppy quorums**: When a network partition prevents reaching the usual n replicas, accept writes
on any reachable nodes. Increases availability but weakens consistency guarantees.

**Performance advantage**: Leaderless systems are resilient to gray failures (nodes that are slow
but not dead) because they don't need to decide whether a situation warrants failover. Request
hedging (using the fastest response from multiple replicas) reduces tail latency.

---

## Consistency Models for Replication

### Read-After-Write Consistency
After a user writes data, they should be able to read their own write. Techniques:
- Read from the leader for data the user may have modified
- Track the timestamp of the user's last write; route reads to replicas that are at least that current
- Use logical clocks to compare client and replica state

### Monotonic Reads
Once a user has seen a value, they should never see an older value on subsequent reads. Solution:
route all reads from the same user to the same replica (e.g., hash user ID to replica).

### Consistent Prefix Reads
If writes have a causal ordering (A happened before B), readers should see them in that order.
Especially tricky with sharded databases where different shards process independently.

---

## Conflict Resolution

### Last Write Wins (LWW)
Attach a timestamp to each write; the write with the highest timestamp wins. Simple but causes
data loss — concurrent writes are silently discarded. Used by Cassandra and ScyllaDB.

Only safe when writes are truly independent and data loss is acceptable (e.g., caching).

### Automatic Merge Algorithms

**CRDTs (Conflict-Free Replicated Data Types)**: Data structures that can be merged automatically
without conflicts. Each element gets a unique immutable ID; merges are deterministic based on IDs.
- Used by: Redis Enterprise, Riak, Azure Cosmos DB, Automerge, Yjs
- Work well for: counters, sets, text, lists, maps

**Operational Transformation (OT)**: Records operations (insert at index N, delete at index M) and
transforms indexes to account for concurrent operations.
- Used by: Google Docs, ShareDB
- Better for: real-time collaborative text editing

**Key difference**: CRDTs assign permanent IDs to elements (no transformation needed); OT uses
mutable indexes that must be transformed. Both can handle text, lists, maps, and counters.

### Manual Conflict Resolution
Present conflicts to users or application logic. Works for cases where automatic merging isn't
semantically meaningful (e.g., two people editing different fields of the same record where
business rules determine which edit takes priority).

---

## Sharding (Partitioning)

### Why Shard?
When a single node can't handle the data volume or throughput, distribute data across multiple nodes.
Each shard holds a subset of the data.

**Don't shard prematurely.** Sharding adds significant complexity (cross-shard queries, rebalancing,
distributed transactions). Start with a single node, replicate for read scaling and availability,
and only shard when you've exhausted vertical scaling.

### Sharding Strategies

**By key range**: Each shard handles a contiguous range of keys (e.g., dates, alphabetical ranges).
- Pro: Efficient range queries within a shard
- Con: Hot spots if access patterns cluster on certain ranges (e.g., all today's data hits one shard)

**By hash of key**: Hash the key and assign hash ranges to shards.
- Pro: Even distribution, avoids hot spots
- Con: Range queries require querying all shards (scatter-gather)
- Compromise: Compound key (hash first part for distribution, use second part for range queries within a shard)

**Hot spot mitigation**: For extremely hot keys (celebrity posts, popular products), add a random
prefix to split writes across shards. Reads then need to query all prefixed shards and merge results.

### Multitenancy as Sharding
SaaS applications can shard by tenant ID, giving each tenant (or group of tenants) their own shard.
This provides natural data isolation and allows routing tenants to different hardware tiers.

### Rebalancing
When adding/removing nodes, data must be redistributed.

- **Fixed number of partitions**: Create many more partitions than nodes (e.g., 1000 partitions for 10 nodes). When adding a node, move whole partitions. Simple but requires choosing partition count upfront.
- **Dynamic partitioning**: Split partitions when they grow too large, merge when they shrink. Adapts to data volume but more complex.
- **Consistent hashing**: Minimizes data movement when nodes join/leave. Each node owns a range on a hash ring.

**Automatic vs. manual rebalancing**: Automatic rebalancing is convenient but can cause cascading
failures if triggered during high load (a slow node looks overloaded, its data gets moved to other
nodes which become overloaded, etc.). Manual or operator-approved rebalancing is safer.

### Request Routing
How does a client know which shard holds the data it needs?

1. **Client contacts any node** → node forwards to correct shard (Cassandra, Riak)
2. **Routing tier** (partition-aware load balancer) → routes to correct shard
3. **Client is partition-aware** → connects directly to the right shard (requires client-side metadata)

Metadata about partition-to-node mapping is typically stored in a coordination service (ZooKeeper,
etcd) that notifies routing tiers of changes.

### Secondary Indexes on Sharded Data

**Local (document-partitioned) indexes**: Each shard maintains its own index of the data on that shard.
- Writes update only one shard's index
- Reads that filter by secondary index must scatter-gather across all shards ("scatter/gather")

**Global (term-partitioned) indexes**: The index itself is sharded by the indexed term.
- Reads can go to a single shard of the index
- Writes may need to update index entries on multiple shards (cross-shard coordination, usually async)
