# EKS, Terraform, FluxCD, and Observability

## Table of Contents
- [EKS Architecture Patterns](#eks-architecture-patterns)
- [Terraform Patterns](#terraform-patterns)
- [FluxCD GitOps](#fluxcd-gitops)
- [Prometheus and Grafana](#prometheus-and-grafana)
- [Deployment Strategies](#deployment-strategies)
- [Cost Optimization](#cost-optimization)
- [Interview: Infrastructure Design Questions](#interview-infrastructure-design-questions)

---

## EKS Architecture Patterns

### Cluster Topology
```
EKS Control Plane (AWS-managed)
├── Node Group: System (m6i.large, 2-4 nodes)
│   └── CoreDNS, kube-proxy, Calico, Prometheus, FluxCD
├── Node Group: Application (m6i.xlarge, 3-20 nodes, autoscaling)
│   └── Application workloads
└── Node Group: Compute-Intensive (c6i.2xlarge, 0-10 nodes, autoscaling)
    └── Batch jobs, data processing
```

**Key decisions**:
- **Managed node groups vs. self-managed**: Managed (default) — AWS handles AMI updates, drains. Self-managed only if you need custom AMIs for STIG hardening.
- **One cluster vs. many**: Start with one cluster per environment (dev, staging, prod). Separate clusters for different classification levels (IL2 vs. IL4).
- **Namespace isolation**: Use namespaces + RBAC + network policies to isolate teams/applications within a cluster. Cheaper and simpler than separate clusters when isolation requirements allow.

### Service Mesh (When Needed)
Istio or Linkerd provide:
- **mTLS between pods**: Encrypted pod-to-pod communication without application changes
- **Traffic management**: Canary deployments, traffic splitting, retries, timeouts
- **Observability**: Request-level metrics and traces without application instrumentation

**When to add a service mesh**: When you have 10+ services that need mTLS, traffic shaping, or
fine-grained observability. Don't add it for 3 services — the overhead isn't worth it.

### Ingress
- **AWS Load Balancer Controller**: Creates ALBs/NLBs from Kubernetes Ingress resources
- **NGINX Ingress Controller**: More configuration options, runs in-cluster
- For IL4: Terminate TLS at the ALB with ACM certificates, or use end-to-end TLS

---

## Terraform Patterns

### Module Structure
```
infrastructure/
├── modules/
│   ├── vpc/              # VPC, subnets, NAT, VPC endpoints
│   ├── eks/              # EKS cluster, node groups, IRSA
│   ├── rds/              # RDS PostgreSQL, parameter groups, security groups
│   ├── monitoring/       # Prometheus stack, Grafana, alerting
│   └── security/         # KMS keys, IAM policies, security groups
├── environments/
│   ├── dev/
│   │   ├── main.tf       # Compose modules with dev-sized parameters
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── prod/
└── backend.tf            # S3 + DynamoDB state backend (per environment)
```

### State Management
- **Remote state in S3** with DynamoDB locking (per environment, per account)
- **State encryption**: S3 bucket with KMS encryption (mandatory for IL4)
- **Separate state per environment**: Never share state between dev/staging/prod
- Enable versioning on the state bucket for recovery

### Key Patterns
- **Use `terraform plan` religiously**: Review every change before applying. In CI/CD, plan on PR, apply on merge.
- **Pin provider versions**: Avoid surprises from provider updates
- **Use data sources**: Reference existing resources instead of hardcoding ARNs
- **Outputs**: Export values that other modules or FluxCD need (cluster endpoint, RDS endpoint, IRSA role ARNs)
- **Avoid `count` for complex resources**: Use `for_each` with maps for predictable state management

### Terraform and Compliance
Encode compliance requirements as Terraform configuration:
```hcl
resource "aws_db_instance" "main" {
  # STIG/IL4: Encryption at rest
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn

  # STIG: Enforce SSL
  parameter_group_name = aws_db_parameter_group.enforced_ssl.name

  # HA: Multi-AZ
  multi_az = true

  # Audit: Enhanced monitoring
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn

  # Audit: Performance insights
  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.rds.arn
}
```

Every security control is in code, version-controlled, and reproducible across environments.

---

## FluxCD GitOps

### How It Works
1. Developer pushes Kubernetes manifests (or Helm charts, Kustomize overlays) to Git
2. FluxCD watches the Git repository
3. When changes are detected, FluxCD reconciles the cluster state to match Git
4. If someone manually changes the cluster, FluxCD reverts it to match Git (drift correction)

**Git is the single source of truth for cluster state.** This means:
- Every change is auditable (Git history)
- Rollback = revert a Git commit
- No `kubectl apply` in production (enforced via RBAC)
- Reproducible environments (same Git state = same cluster state)

### Repository Structure
```
fleet/
├── clusters/
│   ├── dev/
│   │   ├── flux-system/         # FluxCD bootstrap
│   │   └── kustomization.yaml   # Points to apps and infrastructure
│   ├── staging/
│   └── prod/
├── apps/
│   ├── base/                    # Shared app manifests
│   │   ├── api/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── kustomization.yaml
│   │   └── worker/
│   └── overlays/                # Environment-specific patches
│       ├── dev/
│       ├── staging/
│       └── prod/
└── infrastructure/
    ├── base/                    # Shared infra (monitoring, ingress, policies)
    └── overlays/
```

### Image Automation
FluxCD can automatically update image tags when new versions are pushed to ECR:
1. **Image Repository**: FluxCD scans ECR for new tags
2. **Image Policy**: Define which tags to track (e.g., semver `>=1.0.0`)
3. **Image Update Automation**: Commit updated image tags back to Git

This creates a full GitOps pipeline: code push → CI builds image → pushes to ECR → FluxCD detects → updates Git → reconciles cluster.

### Secrets in GitOps
Since Git repos should not contain plaintext secrets:
- **Sealed Secrets**: Encrypt secrets with a cluster-specific public key. Only the in-cluster controller can decrypt.
- **External Secrets Operator**: Sync secrets from AWS Secrets Manager into Kubernetes. FluxCD manages the ExternalSecret resources, not the secret values.
- **SOPS**: Mozilla's Secrets OPerationS — encrypt specific values in YAML files using KMS keys.

---

## Prometheus and Grafana

### Architecture
```
Application Pods ──(metrics endpoint)──→ Prometheus ──→ Grafana (dashboards)
                                              ↓
Node Exporter (host metrics) ──────────→ Prometheus ──→ Alertmanager ──→ PagerDuty/Slack
                                              ↓
CloudWatch Exporter (AWS metrics) ────→ Prometheus
                                              ↓
kube-state-metrics (K8s state) ────────→ Prometheus
```

### The RED Method (for services)
- **Rate**: Request throughput (requests/second)
- **Errors**: Error rate (errors/second or error percentage)
- **Duration**: Request latency distribution (p50, p95, p99)

### The USE Method (for resources)
- **Utilization**: How busy is the resource? (CPU %, memory %, disk %)
- **Saturation**: How much work is queued? (CPU run queue, disk I/O queue)
- **Errors**: Error count (disk errors, network errors, OOM kills)

### Key Dashboards
1. **Application Overview**: Request rate, error rate, latency percentiles per service
2. **PostgreSQL**: Active connections, transaction rate, replication lag, dead tuples, cache hit ratio
3. **EKS Cluster**: Node CPU/memory, pod count, pending pods, HPA status
4. **SQS/Kafka**: Queue depth, consumer lag, message age (processing delay)

### Alerting Philosophy
- **Page** (wake someone up): Service is down, data is being lost, users are impacted NOW
- **Ticket** (fix during business hours): Replication lag growing, disk filling up, certificate expiring soon
- **Log** (investigate when convenient): Elevated error rate that self-resolved, autoscaling events

Avoid alert fatigue. If an alert fires and no one needs to act, remove it or convert to a metric.

### PostgreSQL Metrics to Monitor
- `pg_stat_activity`: Active connections, long-running queries, idle-in-transaction
- `pg_stat_user_tables`: Sequential scans (missing indexes?), dead tuples (VACUUM needed?)
- `pg_stat_user_indexes`: Index usage (drop unused indexes)
- Replication lag (seconds behind primary)
- Connection count vs. `max_connections`
- Cache hit ratio (should be >99% for OLTP)
- Transaction rate and commit/rollback ratio

---

## Deployment Strategies

### Rolling Update (Default)
- Gradually replace old pods with new ones
- `maxUnavailable` and `maxSurge` control the pace
- Kubernetes waits for readiness probes before routing traffic
- Rollback: `kubectl rollout undo` or revert the Git commit (FluxCD reverts automatically)

### Canary Deployment (with Flagger)
FluxCD's companion tool Flagger automates canary releases:
1. Deploy new version alongside old version
2. Route a small percentage of traffic to the new version (e.g., 5%)
3. Monitor Prometheus metrics (error rate, latency)
4. If metrics are healthy, gradually increase traffic
5. If metrics degrade, automatically roll back

### Blue-Green Deployment
Run two identical environments (blue and green). Deploy to the inactive one, switch traffic
when verified. More resource-intensive but provides instant rollback.

### Database Migrations in GitOps
Separate database migrations from application deployment:
1. Migration job runs first (init container or separate Job resource)
2. Migration must be backward-compatible (old app version must still work with new schema)
3. Deploy new application version after migration succeeds
4. If rollback needed, app rolls back but migration stays (forward-only migrations)

---

## Cost Optimization

### EKS
- **Right-size pods**: Use VPA recommendations to set accurate resource requests (over-requesting wastes capacity)
- **Spot instances**: For non-critical workloads (batch jobs, dev environments). Not for production services or stateful workloads.
- **Karpenter**: More efficient bin-packing than Cluster Autoscaler (picks optimal instance types)
- **Scale to zero**: Dev/staging environments can scale down outside business hours

### RDS
- **Right-size instances**: Start small, monitor CPU/memory, scale up when needed
- **Reserved Instances**: 1-year or 3-year commitments for production databases (30-60% savings)
- **Stop dev instances**: RDS instances can be stopped for up to 7 days (no compute cost, storage still charged)

### General
- **S3 lifecycle policies**: Move infrequently accessed data to S3-IA or Glacier
- **NAT Gateway costs**: NAT Gateways charge per GB. Use VPC endpoints for AWS service traffic to avoid NAT charges.
- **Monitor with Cost Explorer**: Set budgets and alerts. Tag resources for cost allocation by team/project.

---

## Interview: Infrastructure Design Questions

When asked "how would you deploy X?", structure your answer:

1. **IaC**: "All infrastructure defined in Terraform modules — VPC, EKS, RDS, security groups, IAM roles."
2. **GitOps**: "Application manifests in Git, FluxCD reconciles cluster state. No manual kubectl in production."
3. **Security**: "Private subnets, VPC endpoints, encryption at rest and in transit, IRSA for pod permissions, network policies for pod isolation."
4. **Observability**: "Prometheus scrapes application and infrastructure metrics, Grafana dashboards for visibility, Alertmanager for on-call notifications."
5. **Availability**: "Multi-AZ EKS nodes, RDS Multi-AZ, pod disruption budgets, health checks, HPA for scaling."
6. **CI/CD**: "Code push → CI builds and tests → container image to ECR → FluxCD detects and deploys → Prometheus monitors → Flagger validates."

This demonstrates you think about infrastructure holistically, not just "put it in a container."
