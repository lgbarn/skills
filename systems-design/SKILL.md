---
name: systems-design
description: >
  System design interview prep and architecture guide for DoD/Coast Guard IL2/IL4 environments
  on AWS GovCloud. Covers designing scalable, secure, compliant systems using EKS, PostgreSQL (RDS),
  Terraform, FluxCD, Prometheus/Grafana, and AWS managed services. Use this skill whenever someone
  is preparing for a system design interview, architecting a backend system, discussing database
  design or PostgreSQL patterns, planning Kubernetes deployments, designing for high availability
  or fault tolerance, evaluating replication or sharding strategies, working on CI/CD pipelines,
  discussing observability, or making any architecture decision. Also trigger when someone mentions:
  data modeling, scaling, load balancing, caching, message queues, event-driven architecture,
  microservices, API design, or compliance requirements (IL2, IL4, FedRAMP, STIG, CUI, ATO).
  Even casual questions like "how would you design X" or "what database should I use" should trigger this.
---

# Systems Design Interview & Architecture Guide

For developers building and designing systems in **DoD / Coast Guard IL2/IL4 environments** on
**AWS GovCloud** using **EKS, PostgreSQL, Terraform, FluxCD, Prometheus/Grafana**.

Based on principles from *Designing Data-Intensive Applications* (2nd ed., Kleppmann & Riccomini, 2026),
adapted for our specific stack and compliance requirements.

## System Design Interview Framework

Every system design interview answer should follow this structure. Practice thinking through each
step — interviewers care more about your reasoning process than arriving at a "perfect" answer.

### Step 1: Requirements & Constraints (3-5 minutes)

Don't jump into drawing boxes. Clarify what you're building first.

**Functional requirements** — What does the system do? What are the core user stories?

**Nonfunctional requirements** — Quantify these:
- **Scale**: How many users? Requests per second? Data volume? Growth rate?
- **Latency**: What p50/p95/p99 response times are acceptable? Percentiles matter more than averages — a few slow requests can cascade and block others (head-of-line blocking).
- **Availability**: What's the acceptable downtime? (99.9% = ~8.7 hours/year, 99.99% = ~52 min/year)
- **Durability**: What's the acceptable data loss window? (RPO) How fast must you recover? (RTO)
- **Consistency**: Does the app need strong consistency (reads always see latest writes) or is eventual consistency acceptable? Be specific — different parts of the system may need different guarantees.

**Compliance constraints** (always mention in our context):
- IL2/IL4 impact level — what data classification?
- Is this CUI? Does it need IL4 controls?
- AWS GovCloud region requirements
- Encryption at rest and in transit (mandatory)
- FedRAMP/STIG compliance requirements

**Back-of-envelope math** — Show you can estimate:
- If 1M users, 10% daily active, 5 actions each = 500K actions/day = ~6 req/sec average, ~60 req/sec peak
- Each record is ~1KB → 500K records/day = 500MB/day = ~180GB/year
- Does this fit on a single PostgreSQL instance? (Yes, easily. Don't over-engineer.)

### Step 2: High-Level Design (5-8 minutes)

Draw the core components and data flow. For our stack, a typical architecture looks like:

```
Client → ALB/NLB → Keycloak (OIDC/JWT) → EKS (application pods) → RDS PostgreSQL
                                                ↓                        ↓
                    CG ICAM (identity)     FluxCD (GitOps)          Read replicas
                                                ↓
                                          Prometheus → Grafana (observability)
```

**Key components to consider**:
- **Authentication**: Keycloak (OIDC provider) federated to CG ICAM. Issues JWTs with roles/claims. Services validate tokens stateless.
- **Load balancer**: ALB (HTTP/HTTPS, path-based routing) vs. NLB (TCP, lower latency, static IPs)
- **Compute**: EKS pods with HPA (Horizontal Pod Autoscaler) for scaling
- **Database**: RDS PostgreSQL (primary + read replicas), or Aurora PostgreSQL for higher availability
- **Caching**: ElastiCache Redis (if read-heavy and can tolerate stale data)
- **Async processing**: SQS + worker pods, or Amazon MSK (managed Kafka) for event streaming
- **Object storage**: S3 for files, backups, static assets (always encrypted with KMS)
- **DNS**: Route 53 with health checks for failover

### Step 3: Data Model & Storage Deep Dive (5-8 minutes)

This is where you show depth. See `references/postgresql-and-data-modeling.md` for detailed patterns.

**Start with the data model**:
- What are the core entities and relationships?
- Normalize first (3NF), then denormalize only where you have measured performance needs
- Consider read vs. write patterns — read-heavy workloads benefit from materialized views or read replicas

**PostgreSQL is almost always the right starting point** for our environment because:
- Mature, battle-tested, FedRAMP-authorized on RDS/Aurora
- Strong ACID guarantees, rich SQL support, excellent indexing
- JSONB columns for semi-structured data (avoids needing a separate document store for most cases)
- Full-text search built in (avoids needing Elasticsearch for many use cases)
- Extensions: PostGIS (geospatial), pgvector (vector/similarity search), pg_cron (scheduled jobs)

**When to reach beyond PostgreSQL**:
| Need | Solution | Why Not Just Postgres? |
|------|----------|----------------------|
| Sub-millisecond reads, high cache hit rate | ElastiCache Redis | Postgres can't match in-memory speeds for hot data |
| Full-text search at scale with ranking/facets | OpenSearch (managed Elasticsearch) | Postgres FTS works but doesn't scale for complex search UIs |
| Event streaming / CDC | Amazon MSK (Kafka) or SQS | Postgres LISTEN/NOTIFY doesn't scale for high-throughput streaming |
| Time-series metrics at massive scale | Amazon Timestream or InfluxDB | Postgres handles moderate time-series well, but struggles at extreme write rates |
| Large file/blob storage | S3 | Don't store large blobs in Postgres — store the S3 key instead |

### Step 4: Scaling & Reliability (5-8 minutes)

**Scaling PostgreSQL**:
- **Vertical first**: RDS instances go up to db.r6g.16xlarge (64 vCPU, 512GB RAM). That handles a LOT.
- **Read replicas**: For read-heavy workloads, add up to 5 RDS read replicas (up to 15 for Aurora). Application routes reads to replicas, writes to primary. Replicas may lag — acceptable for most reads.
- **Connection pooling**: PgBouncer or RDS Proxy. PostgreSQL creates a process per connection — without pooling, you'll exhaust connections with many EKS pods.
- **Sharding**: Last resort. If you mention sharding in an interview, explain why vertical scaling and read replicas aren't sufficient first. Citus (PostgreSQL extension) can shard while keeping the PostgreSQL interface.

**Scaling EKS**:
- **HPA**: Scale pods based on CPU, memory, or custom Prometheus metrics
- **Cluster Autoscaler / Karpenter**: Scale nodes when pods can't be scheduled
- **Pod Disruption Budgets**: Ensure minimum availability during node updates
- **Multi-AZ**: Spread pods across availability zones for fault tolerance

**Reliability patterns**:
- **Health checks**: Liveness probes (restart if stuck), readiness probes (stop sending traffic if not ready)
- **Circuit breakers**: Stop calling a failing downstream service; fail fast instead of cascading
- **Retries with exponential backoff and jitter**: For transient failures. Must be idempotent.
- **Graceful degradation**: Serve stale cache data when the database is slow rather than returning errors

See `references/replication-and-availability.md` for replication strategies and failure handling.

### Step 5: Security & Compliance (3-5 minutes)

Always cover this — it's table stakes in our environment. See `references/security-and-compliance.md`.

**Network security**:
- Private subnets for EKS worker nodes and RDS — no public internet access
- VPC endpoints for AWS services (S3, SQS, ECR) — traffic stays on AWS backbone
- Security groups as firewalls — least-privilege, deny by default
- Network policies in EKS (Calico or Cilium) for pod-to-pod traffic control

**Data protection**:
- Encryption at rest: KMS-managed keys for RDS, S3, EBS (mandatory for IL4)
- Encryption in transit: TLS everywhere — ALB to pod, pod to pod, pod to RDS
- No secrets in code or environment variables — use AWS Secrets Manager or sealed-secrets in FluxCD

**Authentication & authorization**:
- Keycloak (OIDC) federated to CG ICAM — centralized identity, JWT-based stateless auth
- Roles in Keycloak map to CG ICAM groups — applications read roles from JWT claims
- Service-to-service auth via client credentials grant (machine clients in Keycloak)
- IAM roles for service accounts (IRSA) — pods get AWS permissions without static credentials
- RBAC in EKS — least-privilege namespace-scoped roles

**Compliance posture**:
- All infrastructure defined in Terraform (auditable, version-controlled, reproducible)
- GitOps via FluxCD — all changes to cluster state go through Git (audit trail)
- Prometheus/Grafana for continuous monitoring and alerting
- Container image scanning (ECR scanning, Trivy) before deployment

### Step 6: Observability & Operations (2-3 minutes)

**Prometheus + Grafana stack**:
- Prometheus scrapes metrics from pods, nodes, RDS (via CloudWatch exporter)
- Grafana dashboards for application metrics, infrastructure health, SLO tracking
- Alertmanager for on-call notifications (PagerDuty, Slack, email)
- Key metrics: request rate, error rate, duration (RED), saturation (CPU, memory, disk, connections)

**Logging**: CloudWatch Logs or Fluent Bit → OpenSearch for centralized log aggregation

**Deployment via FluxCD**:
- Git is the source of truth for cluster state
- Changes merged to main → FluxCD reconciles → cluster updated
- Rollback = revert the Git commit
- Canary/progressive deployments with Flagger (FluxCD companion)

## Quick-Reference: Trade-Off Tables

### Choosing a Replication Strategy

| Strategy | Consistency | Write Throughput | Failure Tolerance | Our Context |
|----------|-------------|-----------------|-------------------|-------------|
| **Single-leader** (RDS primary + replicas) | Strong from primary | Limited by primary | Automatic failover (Multi-AZ) | Default for most workloads |
| **Multi-leader** (Aurora Global Database) | Eventual across regions | Higher | Cross-region resilience | Only if multi-region is required |
| **Leaderless** (DynamoDB) | Tunable | High | No failover needed | Rarely needed — prefer PostgreSQL |

### Choosing a PostgreSQL Isolation Level

| Level | Prevents | Cost | Use When |
|-------|----------|------|----------|
| **Read committed** (Postgres default) | Dirty reads/writes | Low | Most workloads |
| **Repeatable read** (snapshot isolation) | Non-repeatable reads | Medium | Reports running alongside OLTP |
| **Serializable** (SSI in Postgres) | All anomalies including write skew | Higher abort rate | Financial calculations, inventory, bookings |

### Sync vs. Async Communication

| Pattern | When to Use | AWS Service |
|---------|-------------|-------------|
| **Synchronous REST/gRPC** | Client needs immediate response | ALB + EKS service |
| **Async queue** | Fire-and-forget, work distribution | SQS + worker pods |
| **Event streaming** | Event-driven architecture, CDC, fan-out | MSK (Kafka) or Kinesis |
| **Pub/sub** | Notifications, loose coupling | SNS → SQS fan-out |

## Common Interview Anti-Patterns

Warn candidates about these:

1. **Jumping to microservices**: For a new system, start with a well-structured monolith on EKS. Split services only when team boundaries or scaling needs demand it.

2. **Premature sharding**: A single RDS PostgreSQL instance handles far more than most people think. Show the math before proposing sharding.

3. **Ignoring the network**: Distributed systems fail partially. Design for retries, timeouts, idempotency, and circuit breakers. TCP doesn't guarantee bounded delay.

4. **Trusting wall clocks for ordering**: Clocks drift between machines. For event ordering across services, use logical clocks or a centralized sequence (PostgreSQL sequences, Kafka offsets).

5. **No connection pooling**: PostgreSQL forks a process per connection. 200 EKS pods with 5 connections each = 1000 connections. You need PgBouncer or RDS Proxy.

6. **Skipping compliance**: In our environment, "we'll handle security later" is not an option. Network isolation, encryption, IRSA, and audit logging are part of the initial design.

7. **Over-engineering for scale you don't have**: Don't add Kafka, Redis, and a separate search engine on day one. PostgreSQL + EKS handles a remarkable amount of load. Add complexity only when you have evidence it's needed.

## Reference Files

Read these for detailed guidance on specific topics:

- `references/postgresql-and-data-modeling.md` — PostgreSQL internals, indexing strategies, JSONB, partitioning, connection pooling, migration patterns, Aurora vs. RDS, and when to use other databases
- `references/replication-and-availability.md` — RDS Multi-AZ, read replicas, Aurora replication, EKS multi-AZ, failure handling, quorum concepts, consistency models, conflict resolution
- `references/security-and-compliance.md` — IL2/IL4 requirements, network architecture, encryption, IAM/IRSA, STIG compliance, FedRAMP controls, data classification, audit logging
- `references/eks-and-infrastructure.md` — EKS architecture, Terraform patterns, FluxCD GitOps, Prometheus/Grafana observability, scaling strategies, deployment patterns, cost optimization
- `references/distributed-systems-theory.md` — Foundational concepts for interviews: CAP theorem, consensus, linearizability, transactions, batch/stream processing, event-driven architecture, encoding formats
