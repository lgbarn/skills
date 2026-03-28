# Security and Compliance for IL2/IL4

## Table of Contents
- [Impact Levels Overview](#impact-levels-overview)
- [Network Architecture](#network-architecture)
- [Encryption Requirements](#encryption-requirements)
- [Identity and Access Management](#identity-and-access-management)
- [EKS Security](#eks-security)
- [Data Classification and Handling](#data-classification-and-handling)
- [Audit and Logging](#audit-and-logging)
- [Compliance Frameworks](#compliance-frameworks)
- [Interview Talking Points](#interview-talking-points)

---

## Impact Levels Overview

### IL2 — Public and Low-Sensitivity Data
- Non-controlled unclassified information
- Publicly releasable data or low-sensitivity internal data
- Can run on standard AWS GovCloud
- FedRAMP Moderate baseline applies

### IL4 — Controlled Unclassified Information (CUI)
- Data that requires safeguarding per federal regulation (e.g., PII, PHI, law enforcement sensitive)
- Requires AWS GovCloud (US) regions
- FedRAMP High baseline or DoD CC SRG IL4 authorization
- Stricter access controls, encryption, and audit requirements
- Personnel with access must be U.S. persons
- Physical infrastructure within the continental United States

### Key Difference
IL2 → "don't be careless with it"
IL4 → "actively protect it — CUI markings, access controls, encryption, audit trails, U.S. persons only"

---

## Network Architecture

### VPC Design for IL4
```
VPC (10.0.0.0/16)
├── Public Subnets (10.0.0.0/20, 10.0.16.0/20, 10.0.32.0/20)
│   └── ALB/NLB (internet-facing, terminates TLS)
├── Private Subnets - Application (10.0.48.0/20, 10.0.64.0/20, 10.0.80.0/20)
│   └── EKS worker nodes (no public IPs, NAT for outbound only)
├── Private Subnets - Data (10.0.96.0/20, 10.0.112.0/20, 10.0.128.0/20)
│   └── RDS PostgreSQL, ElastiCache (no internet access at all)
└── VPC Endpoints
    └── S3, ECR, STS, Secrets Manager, CloudWatch, SQS, etc.
```

### Security Groups (Stateful Firewalls)
- **ALB SG**: Inbound HTTPS (443) from allowed CIDRs only
- **EKS Worker SG**: Inbound only from ALB SG and other workers. No direct internet inbound.
- **RDS SG**: Inbound PostgreSQL (5432) only from EKS Worker SG
- **Principle**: Least privilege. Only open what's required. Reference security groups by ID, not CIDR.

### VPC Endpoints (PrivateLink)
Traffic to AWS services (S3, ECR, STS, Secrets Manager, CloudWatch, SQS, KMS) stays on the AWS
backbone — never traverses the public internet. For IL4, this is strongly recommended for all
AWS service access.

### Network Policies in EKS
Use Calico or Cilium network policies to control pod-to-pod traffic within the cluster:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-db
spec:
  podSelector:
    matchLabels:
      app: api
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: database-proxy
      ports:
        - port: 5432
```
Default deny all, then allow specific flows. This is micro-segmentation — a compromise of one pod
doesn't give access to the entire cluster network.

---

## Encryption Requirements

### At Rest (Mandatory for IL4)
- **RDS/Aurora**: Enable encryption with KMS-managed keys (aws/rds or customer-managed CMK)
- **S3**: Server-side encryption with KMS (SSE-KMS) or S3-managed keys (SSE-S3). Bucket policies should deny unencrypted uploads.
- **EBS volumes**: Encrypt all EKS worker node volumes with KMS
- **Secrets Manager / SSM Parameter Store**: Encrypted by default with KMS

### In Transit (Mandatory for IL4)
- **ALB to client**: TLS 1.2+ (configure security policy to disable older protocols)
- **ALB to pods**: TLS termination at ALB or end-to-end TLS with pod certificates
- **Pod to pod**: mTLS via service mesh (Istio, Linkerd) or application-level TLS
- **Pod to RDS**: Require SSL connections (`sslmode=verify-full` in connection string)
- **Pod to AWS services**: All AWS SDK calls use HTTPS by default

### KMS Key Management
- Use customer-managed KMS keys (CMKs) for IL4 data — gives you control over key rotation and access policies
- Enable automatic key rotation (annual)
- Key policies should restrict access to specific IAM roles
- Separate keys for different data classifications if needed

---

## Identity and Access Management

### Authentication: Keycloak + CG ICAM

Our authentication stack uses **Keycloak** integrated with the **Coast Guard ICAM (Identity, Credential, and Access Management)** system.

**Architecture**:
```
User → Application → Keycloak (OIDC Provider) → CG ICAM (Identity Source)
                          ↓
                    JWT with roles/claims
                          ↓
                    Application validates JWT
```

**How it works**:
1. User authenticates through Keycloak, which federates to CG ICAM as the identity provider
2. Keycloak issues JWT (JSON Web Token) containing user identity, roles, and claims
3. Applications validate the JWT on each request (signature verification, expiry check, audience check)
4. Authorization decisions based on roles embedded in the token

**Keycloak on EKS**:
- Deploy Keycloak as a stateful service on EKS with PostgreSQL backend (can share RDS or use dedicated instance)
- High availability: Multiple Keycloak replicas with shared database session storage
- Configure realm with CG ICAM as an identity provider (SAML or OIDC federation)
- Client credentials for service-to-service authentication (machine clients)

**Role-Based Access Control (RBAC) via Keycloak**:
- Define roles in Keycloak that map to CG ICAM groups/attributes
- Roles embedded in JWT claims — applications read them without additional ICAM calls
- Composite roles for layered permissions (e.g., `admin` includes `editor` includes `viewer`)
- Realm roles for global permissions, client roles for application-specific permissions

**Token flow for APIs**:
```
1. Frontend redirects to Keycloak login → CG ICAM authenticates user
2. Keycloak returns authorization code → Frontend exchanges for tokens
3. Frontend sends access token (JWT) with each API request
4. API validates JWT signature (using Keycloak's public key / JWKS endpoint)
5. API checks token expiry, audience, and extracts roles for authorization
6. Refresh tokens used to get new access tokens without re-authentication
```

**Interview talking points for auth**:
- "We use OIDC with Keycloak federated to CG ICAM — centralized identity, decentralized authorization"
- "JWTs carry roles so services can authorize without calling back to the identity provider on every request"
- "Token validation is stateless — each service verifies the JWT signature locally using cached public keys"
- "Service-to-service auth uses client credentials grant — no user context, just machine identity"

**Common auth patterns in our stack**:
- **API Gateway / Ingress level**: NGINX Ingress or ALB can validate JWTs before requests reach application pods (offloads auth from application code)
- **Sidecar / service mesh**: Istio can enforce mTLS + JWT validation at the mesh level
- **Application level**: Middleware validates JWT, extracts roles, populates request context. Most control, most code.
- **PostgreSQL Row-Level Security (RLS)**: Set `current_setting('app.current_user_role')` from the JWT role, then PostgreSQL enforces data access policies per-query

### AWS IAM: Roles for Service Accounts (IRSA)
For AWS resource access (S3, SQS, KMS), pods use IRSA — not Keycloak. IRSA is for machine-to-AWS-service authentication.

1. Create an IAM role with the needed permissions (e.g., S3 read, SQS publish)
2. Create an OIDC trust between EKS and IAM
3. Annotate the Kubernetes service account with the IAM role ARN
4. Pods using that service account automatically receive temporary AWS credentials

**Never use**: AWS access keys in environment variables or mounted secrets. IRSA is the way.

**Keycloak vs. IRSA**: Keycloak handles user/human authentication and application-level authorization. IRSA handles pod-to-AWS-service authentication. They serve different purposes and both are needed.

### RDS IAM Authentication
Pods can authenticate to PostgreSQL using IAM instead of passwords:
- Generates short-lived authentication tokens
- No password to rotate or store
- Works with RDS Proxy for connection pooling
- Alternative: Keycloak client credentials → application validates → connects to RDS with stored credentials from Secrets Manager

### Kubernetes RBAC
- Namespace-scoped roles (not cluster-wide) for application service accounts
- Developers get read-only access to production namespaces
- CI/CD service account gets deployment permissions only in its namespace
- Use `kubectl auth can-i` to verify permissions

### Least Privilege Checklist
- **Keycloak roles**: Grant minimum roles needed per user/group. Review role assignments regularly.
- **IAM policies**: Specific resource ARNs, not `*`. Specific actions, not `*`.
- **Security groups**: Reference by SG ID, not `0.0.0.0/0`
- **Kubernetes RBAC**: Namespace-scoped, not cluster-admin
- **Database**: Application user has only necessary table/schema permissions, not `superuser`. Use RLS where appropriate.

---

## EKS Security

### Pod Security
- **Non-root containers**: Set `runAsNonRoot: true` and `runAsUser` in pod security context
- **Read-only root filesystem**: `readOnlyRootFilesystem: true` (mount writable volumes where needed)
- **Drop all capabilities**: `capabilities: { drop: ["ALL"] }`, add back only what's needed
- **No privilege escalation**: `allowPrivilegeEscalation: false`
- **Resource limits**: Always set CPU and memory limits to prevent noisy-neighbor issues

### Container Image Security
- Use private ECR repositories (no public images in IL4)
- Enable ECR image scanning (on push and periodic)
- Run Trivy or Grype in CI/CD pipeline — fail build on critical vulnerabilities
- Use minimal base images (distroless, alpine) to reduce attack surface
- Pin image tags to digests, not mutable tags like `latest`

### Secrets Management
- **AWS Secrets Manager**: Store database credentials, API keys, certificates
- **External Secrets Operator**: Sync secrets from AWS Secrets Manager into Kubernetes secrets
- **Sealed Secrets**: Encrypt secrets in Git (safe to store in FluxCD repo), decrypted only in-cluster
- **Never**: Hardcode secrets in code, Dockerfiles, Terraform, or Kubernetes manifests in plaintext

---

## Data Classification and Handling

### CUI Marking and Handling (IL4)
- Systems must support CUI banners/markings where applicable
- Data exports must maintain classification markings
- Cross-domain transfers require review
- Destruction/disposal must follow DoD 5220.22-M or NIST 800-88

### Data Retention and Deletion
- Define retention periods per data type
- Automated purging of expired data (PostgreSQL partitioning makes this efficient — drop old partitions)
- Backup retention aligned with retention policy
- For event-sourced systems: crypto-shredding (encrypt user data with per-user key, delete key to "delete" data without modifying the event log)

### PII/PHI Handling
- Identify fields containing PII/PHI in data models
- Encrypt sensitive fields at the application level (column-level encryption) in addition to at-rest encryption
- Mask PII in logs (never log SSNs, full names with identifiers, etc.)
- Access to PII data requires additional authorization

---

## Audit and Logging

### Required Audit Trails
- **AWS CloudTrail**: All API calls to AWS services (who did what, when)
- **RDS audit logging**: Database queries and connections (pgAudit extension for PostgreSQL)
- **EKS audit logging**: All API server requests (control plane logging to CloudWatch)
- **Application audit logging**: Business-significant actions (who accessed what data, what changed)
- **FluxCD Git history**: All infrastructure and deployment changes (Git is the audit log)

### Log Protection
- Logs must be immutable (write to S3 with Object Lock, or CloudWatch Logs)
- Separate log storage from application access (admins who can delete data shouldn't be able to delete audit logs)
- Retention per compliance requirements (typically 1-7 years for DoD)
- Centralize logs (Fluent Bit → CloudWatch or OpenSearch) for correlation and investigation

### Monitoring for Security Events
Prometheus/Grafana alerting for:
- Failed authentication attempts (brute force detection)
- Unusual API access patterns (anomalous request rates per user)
- Privilege escalation attempts (unexpected RBAC denials)
- Data exfiltration indicators (unusually large query results or data transfers)

---

## Compliance Frameworks

### FedRAMP
Federal Risk and Authorization Management Program. Standardized approach to security assessment
for cloud services. AWS GovCloud maintains FedRAMP High authorization.

**Your responsibility**: FedRAMP is a shared responsibility model. AWS secures the infrastructure;
you secure your workloads, data, configurations, and access controls. The ATO (Authority to Operate)
process validates that your system meets the required controls.

### STIG (Security Technical Implementation Guides)
DISA-published configuration standards for operating systems, databases, web servers, etc.
- EKS STIG: Node hardening, API server configuration, audit logging
- PostgreSQL STIG: Authentication, encryption, access controls, audit
- Container STIG: Image provenance, runtime security, network policies

In Terraform, encode STIG requirements as configuration (e.g., force encryption, enforce TLS versions,
require audit logging). This makes compliance auditable and reproducible.

### Continuous ATO (cATO)
Modern approach where compliance is continuously validated rather than point-in-time assessed:
- Infrastructure as Code (Terraform) ensures reproducible, auditable configurations
- Automated compliance scanning (AWS Config rules, Security Hub, custom Prometheus alerts)
- GitOps (FluxCD) provides complete change audit trail
- Continuous monitoring replaces periodic manual reviews

---

## Interview Talking Points

When security/compliance comes up in interviews, demonstrate you think about it as a first-class concern:

1. **"Security is not a bolt-on"** — Network isolation, encryption, IAM, and audit logging are part of the initial architecture, not something added before deployment.

2. **"Defense in depth"** — Multiple layers: network (VPC, SGs, NACLs), identity (IRSA, RBAC), data (encryption at rest and in transit), application (input validation, output encoding), monitoring (CloudTrail, audit logs, alerts).

3. **"Shared responsibility"** — AWS secures the infrastructure; we secure our workloads. Specific example: AWS encrypts RDS storage, but we configure security groups, enforce SSL connections, and manage database user permissions.

4. **"Compliance as code"** — Terraform encodes security controls. FluxCD provides audit trails. Automated scanning validates continuously. This is how you achieve cATO.

5. **"Least privilege everywhere"** — IAM policies with specific resource ARNs, security groups referencing SG IDs, namespace-scoped RBAC, database users with minimal grants.
