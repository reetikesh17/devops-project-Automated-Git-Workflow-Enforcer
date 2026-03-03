# Architecture Documentation

## Automated Git Workflow Enforcer - System Architecture

### Executive Summary

The Automated Git Workflow Enforcer is a comprehensive DevOps solution that enforces Git workflow standards across the entire development lifecycle, from local development to cloud deployment.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DEVELOPER WORKSTATION                           │
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐            │
│  │  Git Hooks   │───▶│  Validators  │───▶│  CLI Tool    │            │
│  │              │    │              │    │              │            │
│  │ • pre-commit │    │ • Commit     │    │ • Python     │            │
│  │ • commit-msg │    │ • Branch     │    │ • Standalone │            │
│  │ • pre-push   │    │ • Rules      │    │              │            │
│  └──────────────┘    └──────────────┘    └──────────────┘            │
│         │                    │                    │                    │
└─────────┼────────────────────┼────────────────────┼────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         VERSION CONTROL (GitHub)                        │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    GitHub Actions CI/CD                          │  │
│  │                                                                  │  │
│  │  Triggers:                    Actions:                          │  │
│  │  • Push to branch            • Run validators                   │  │
│  │  • Pull request              • Build Docker image               │  │
│  │  • Tag creation              • Run tests                        │  │
│  │                              • Deploy to K8s                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      CONTAINERIZATION LAYER                             │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                        Docker                                    │  │
│  │                                                                  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐               │  │
│  │  │   Image    │  │  Registry  │  │  Compose   │               │  │
│  │  │            │  │            │  │            │               │  │
│  │  │ • Multi-   │  │ • Docker   │  │ • Dev      │               │  │
│  │  │   stage    │  │   Hub      │  │ • Test     │               │  │
│  │  │ • Optimized│  │ • Private  │  │ • Prod     │               │  │
│  │  └────────────┘  └────────────┘  └────────────┘               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                                  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      Kubernetes                                  │  │
│  │                                                                  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐               │  │
│  │  │ ConfigMap  │  │    Job     │  │ Deployment │               │  │
│  │  │            │  │            │  │            │               │  │
│  │  │ • Rules    │  │ • One-time │  │ • Always-on│               │  │
│  │  │ • Config   │  │ • Validate │  │ • Service  │               │  │
│  │  │ • External │  │ • CI/CD    │  │ • Scaled   │               │  │
│  │  └────────────┘  └────────────┘  └────────────┘               │  │
│  │                                                                  │  │
│  │  ┌────────────┐  ┌────────────┐                                │  │
│  │  │  CronJob   │  │  Service   │                                │  │
│  │  │            │  │            │                                │  │
│  │  │ • Scheduled│  │ • Expose   │                                │  │
│  │  │ • Daily    │  │ • LB       │                                │  │
│  │  └────────────┘  └────────────┘                                │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER (AWS)                            │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                       Terraform                                  │  │
│  │                                                                  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐               │  │
│  │  │    VPC     │  │  Security  │  │    EC2     │               │  │
│  │  │            │  │   Group    │  │            │               │  │
│  │  │ • Default  │  │ • SSH      │  │ • t2.micro │               │  │
│  │  │ • Subnets  │  │ • Rules    │  │ • AL2      │               │  │
│  │  │            │  │ • Firewall │  │ • Tags     │               │  │
│  │  └────────────┘  └────────────┘  └────────────┘               │  │
│  │                                                                  │  │
│  │  ┌────────────┐  ┌────────────┐                                │  │
│  │  │    EBS     │  │  Elastic   │                                │  │
│  │  │            │  │     IP     │                                │  │
│  │  │ • 8GB      │  │ • Public   │                                │  │
│  │  │ • Encrypted│  │ • Static   │                                │  │
│  │  └────────────┘  └────────────┘                                │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Interaction Flow

### 1. Local Development Flow

```
Developer writes code
        ↓
Git commit/push triggered
        ↓
Git hooks execute
        ↓
┌─────────────────────────┐
│   pre-commit hook       │
│   • Validates commit    │
│   • Checks format       │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│   commit-msg hook       │
│   • Validates message   │
│   • Enforces convention │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│   pre-push hook         │
│   • Validates branch    │
│   • Checks naming       │
└─────────────────────────┘
        ↓
Push to remote (if valid)
```

### 2. CI/CD Pipeline Flow

```
Code pushed to GitHub
        ↓
GitHub Actions triggered
        ↓
┌─────────────────────────┐
│  Checkout code          │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│  Run validators         │
│  • Commit validation    │
│  • Branch validation    │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│  Build Docker image     │
│  • Multi-stage build    │
│  • Tag with version     │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│  Push to registry       │
│  • Docker Hub           │
│  • Private registry     │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│  Deploy to Kubernetes   │
│  • Apply manifests      │
│  • Update ConfigMap     │
└─────────────────────────┘
        ↓
Deployment complete
```

### 3. Kubernetes Execution Flow

```
Kubernetes receives deployment
        ↓
┌─────────────────────────┐
│  Load ConfigMap         │
│  • Read rules.json      │
│  • Mount as volume      │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│  Create Pod             │
│  • Pull image           │
│  • Mount config         │
│  • Start container      │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│  Execute validation     │
│  • Read mounted config  │
│  • Run CLI tool         │
│  • Validate input       │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│  Report results         │
│  • Log output           │
│  • Set exit code        │
│  • Update status        │
└─────────────────────────┘
        ↓
Pod completes/continues
```

### 4. Infrastructure Provisioning Flow

```
Terraform configuration defined
        ↓
┌─────────────────────────┐
│  terraform init         │
│  • Download providers   │
│  • Initialize backend   │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│  terraform plan         │
│  • Validate config      │
│  • Show changes         │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│  terraform apply        │
│  • Create VPC resources │
│  • Create security group│
│  • Launch EC2 instance  │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│  Configure instance     │
│  • Install dependencies │
│  • Setup application    │
│  • Start services       │
└─────────────────────────┘
        ↓
Infrastructure ready
```

---

## Detailed Component Descriptions

### Layer 1: Developer Workstation

**Git Hooks**
- **Purpose**: First line of defense for validation
- **Location**: `.git/hooks/`
- **Types**:
  - `pre-commit`: Validates before commit is created
  - `commit-msg`: Validates commit message format
  - `pre-push`: Validates branch name before push
- **Benefits**:
  - Immediate feedback
  - Prevents invalid commits
  - Reduces CI/CD failures

**Validators**
- **Commit Validator**: Enforces Conventional Commits
- **Branch Validator**: Enforces branch naming conventions
- **Configuration**: Reads from `src/config/rules.json`
- **Extensible**: Easy to add new rules

**CLI Tool**
- **Interface**: Command-line interface
- **Commands**:
  - `validate-commit`: Validate commit messages
  - `validate-branch`: Validate branch names
  - `validate-all`: Validate both
- **Output**: Human-readable with colors
- **Exit Codes**: Standard Unix exit codes

---

### Layer 2: Version Control (GitHub)

**GitHub Actions**
- **Workflow**: `.github/workflows/validate.yml`
- **Triggers**:
  - Push to any branch
  - Pull request creation
  - Tag creation
- **Jobs**:
  - Validate commits
  - Validate branches
  - Build Docker image
  - Run tests
  - Deploy to environments

**Benefits**:
- Automated validation
- Consistent enforcement
- Integration with PR process
- Deployment automation

---

### Layer 3: Containerization (Docker)

**Docker Image**
- **Base**: Python 3.11-slim
- **Build**: Multi-stage for optimization
- **Size**: ~327MB (test), ~13MB (optimized)
- **Security**:
  - Non-root user
  - Minimal dependencies
  - No secrets in image

**Docker Compose**
- **Services**:
  - `enforcer`: Production service
  - `enforcer-dev`: Development environment
  - `enforcer-test`: Testing environment
- **Benefits**:
  - Consistent environments
  - Easy local testing
  - Reproducible builds

---

### Layer 4: Orchestration (Kubernetes)

**ConfigMap**
- **Name**: `git-enforcer-config`
- **Purpose**: Externalize configuration
- **Content**: `rules.json` with validation rules
- **Benefits**:
  - No image rebuild for config changes
  - Environment-specific rules
  - Easy updates

**Job**
- **Purpose**: One-time validation tasks
- **Use Cases**:
  - CI/CD validation
  - Manual validation
  - Batch processing
- **Features**:
  - Retry on failure (3 attempts)
  - Auto-cleanup (TTL: 1 hour)
  - ConfigMap mounted

**Deployment**
- **Purpose**: Long-running validation service
- **Replicas**: Configurable (default: 1)
- **Features**:
  - Health checks
  - Rolling updates
  - Auto-restart
  - Scalable

**CronJob**
- **Purpose**: Scheduled validation
- **Schedule**: Daily at midnight (configurable)
- **Features**:
  - History retention
  - Concurrency control
  - Auto-cleanup

---

### Layer 5: Infrastructure (AWS via Terraform)

**VPC**
- **Type**: Default VPC
- **Reason**: Simplicity, no additional cost
- **Components**: Subnets, route tables, internet gateway

**Security Group**
- **Name**: `git-workflow-enforcer-sg`
- **Inbound Rules**:
  - SSH (22) from specific IP only
- **Outbound Rules**:
  - All traffic allowed
- **Security**: Minimal attack surface

**EC2 Instance**
- **Type**: t2.micro (free-tier eligible)
- **AMI**: Amazon Linux 2 (latest)
- **Storage**: 8GB GP3 EBS (encrypted)
- **Monitoring**: Detailed monitoring enabled
- **Security**:
  - IMDSv2 required
  - Non-root user
  - SSH key authentication

**User Data**
- **Purpose**: Automated setup
- **Installs**:
  - Git
  - Python 3
  - Docker
  - Docker Compose
- **Configuration**: Application directory setup

---

## Data Flow Diagram

```
┌──────────────┐
│  Developer   │
│   Commits    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                    Git Hooks                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │pre-commit  │→ │commit-msg  │→ │ pre-push   │        │
│  └────────────┘  └────────────┘  └────────────┘        │
└──────┬───────────────────────────────────────────────────┘
       │ (if valid)
       ▼
┌──────────────────────────────────────────────────────────┐
│                    GitHub                                │
│  ┌────────────────────────────────────────────────────┐ │
│  │              GitHub Actions                        │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │ │
│  │  │ Validate │→ │  Build   │→ │  Deploy  │        │ │
│  │  └──────────┘  └──────────┘  └──────────┘        │ │
│  └────────────────────────────────────────────────────┘ │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│              Docker Registry                             │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Docker Image                               │ │
│  │  • git-workflow-enforcer:latest                    │ │
│  │  • git-workflow-enforcer:v1.0.0                    │ │
│  └────────────────────────────────────────────────────┘ │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│              Kubernetes Cluster                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  ConfigMap (rules.json)                            │ │
│  └────────────────────────────────────────────────────┘ │
│         │                                                │
│         ▼                                                │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Pod (Job/Deployment/CronJob)                      │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │  Container                                   │ │ │
│  │  │  • Mounts ConfigMap                          │ │ │
│  │  │  • Reads rules.json                          │ │ │
│  │  │  • Executes validation                       │ │ │
│  │  │  • Outputs results                           │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────┘ │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│              Logging & Monitoring                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │  • kubectl logs                                    │ │
│  │  • CloudWatch (if AWS)                             │ │
│  │  • Prometheus/Grafana (optional)                   │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Core Technologies

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Language** | Python | 3.11+ | Core application logic |
| **Containerization** | Docker | 20.10+ | Application packaging |
| **Orchestration** | Kubernetes | 1.25+ | Container orchestration |
| **Infrastructure** | Terraform | 1.0+ | Infrastructure as Code |
| **CI/CD** | GitHub Actions | N/A | Automation pipeline |
| **Cloud** | AWS | N/A | Infrastructure hosting |

### Supporting Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Version Control** | Git | Source code management |
| **Container Registry** | Docker Hub | Image storage |
| **Configuration** | JSON | Rules and settings |
| **CLI Framework** | argparse | Command-line interface |
| **Testing** | pytest | Unit and integration tests |
| **Linting** | pylint/flake8 | Code quality |

---

## Deployment Strategies

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install git hooks
./install-hooks.sh

# Test locally
python -m src.main.cli validate-commit "feat: test"
```

### 2. Docker Deployment

```bash
# Build image
docker build -t git-workflow-enforcer:latest .

# Run container
docker run --rm git-workflow-enforcer:latest \
  python -m src.main.cli validate-commit "feat: test"

# Use Docker Compose
docker-compose up
```

### 3. Kubernetes Deployment

```bash
# Apply ConfigMap
kubectl apply -f infrastructure/kubernetes/configmap.yaml

# Deploy Job
kubectl apply -f infrastructure/kubernetes/job.yaml

# Deploy Deployment
kubectl apply -f infrastructure/kubernetes/deployment.yaml

# Deploy CronJob
kubectl apply -f infrastructure/kubernetes/cronjob.yaml
```

### 4. AWS Deployment (Terraform)

```bash
cd infrastructure/terraform

# Initialize
terraform init

# Plan
terraform plan -var-file=production.tfvars

# Apply
terraform apply -var-file=production.tfvars
```

---

## Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Network Security                              │
│  • Security Groups (AWS)                                │
│  • Network Policies (Kubernetes)                        │
│  • Firewall Rules                                       │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 2: Access Control                                │
│  • SSH Key Authentication                               │
│  • RBAC (Kubernetes)                                    │
│  • IAM Roles (AWS)                                      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 3: Container Security                            │
│  • Non-root user                                        │
│  • Read-only filesystem                                 │
│  • Minimal base image                                   │
│  • No secrets in image                                  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 4: Data Security                                 │
│  • EBS encryption                                       │
│  • Secrets management                                   │
│  • ConfigMap for non-sensitive data                     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 5: Monitoring & Auditing                         │
│  • CloudTrail (AWS)                                     │
│  • Audit logs (Kubernetes)                              │
│  • Log aggregation                                      │
└─────────────────────────────────────────────────────────┘
```

### Security Best Practices Implemented

1. **Principle of Least Privilege**
   - Minimal security group rules
   - Non-root container user
   - Read-only ConfigMap mounts

2. **Defense in Depth**
   - Multiple security layers
   - Network isolation
   - Access controls

3. **Secure by Default**
   - IMDSv2 required
   - EBS encryption enabled
   - Latest security patches

4. **Audit and Compliance**
   - All actions logged
   - Immutable infrastructure
   - Version controlled

---

## Scalability Architecture

### Horizontal Scaling

```
┌─────────────────────────────────────────────────────────┐
│              Load Balancer (Optional)                   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Kubernetes Service                         │
└─────────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Pod 1      │ │   Pod 2      │ │   Pod 3      │
│              │ │              │ │              │
│ Enforcer     │ │ Enforcer     │ │ Enforcer     │
│ Container    │ │ Container    │ │ Container    │
└──────────────┘ └──────────────┘ └──────────────┘
```

**Scaling Commands**:
```bash
# Scale up
kubectl scale deployment git-workflow-enforcer --replicas=5

# Auto-scaling (HPA)
kubectl autoscale deployment git-workflow-enforcer \
  --min=2 --max=10 --cpu-percent=80
```

### Vertical Scaling

```bash
# Update resource limits
kubectl set resources deployment git-workflow-enforcer \
  --limits=cpu=500m,memory=512Mi \
  --requests=cpu=200m,memory=256Mi
```

---

## High Availability Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Multi-AZ Deployment                        │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   AZ-1       │  │   AZ-2       │  │   AZ-3       │ │
│  │              │  │              │  │              │ │
│  │  ┌────────┐  │  │  ┌────────┐  │  │  ┌────────┐  │ │
│  │  │ Pod 1  │  │  │  │ Pod 2  │  │  │  │ Pod 3  │  │ │
│  │  └────────┘  │  │  └────────┘  │  │  └────────┘  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- Pod anti-affinity rules
- Multiple replicas across AZs
- Health checks and auto-restart
- Rolling updates with zero downtime

---

## Disaster Recovery

### Backup Strategy

1. **Configuration Backup**
   - ConfigMaps versioned in Git
   - Terraform state in S3 with versioning
   - Regular snapshots

2. **Data Backup**
   - EBS snapshots (daily)
   - Database backups (if applicable)
   - Log archival

3. **Recovery Procedures**
   ```bash
   # Restore from Git
   git checkout <commit-hash>
   kubectl apply -f infrastructure/kubernetes/
   
   # Restore Terraform state
   terraform state pull > backup.tfstate
   
   # Restore from snapshot
   aws ec2 create-volume --snapshot-id <snapshot-id>
   ```

---

## Monitoring and Observability

### Metrics Collection

```
┌─────────────────────────────────────────────────────────┐
│              Application Metrics                        │
│  • Validation success rate                              │
│  • Validation latency                                   │
│  • Error rate                                           │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Infrastructure Metrics                     │
│  • CPU usage                                            │
│  • Memory usage                                         │
│  • Network I/O                                          │
│  • Disk I/O                                             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Monitoring Stack                           │
│  • Prometheus (metrics)                                 │
│  • Grafana (visualization)                              │
│  • CloudWatch (AWS)                                     │
│  • ELK Stack (logs)                                     │
└─────────────────────────────────────────────────────────┘
```

### Logging Strategy

```
Application Logs → stdout/stderr
        ↓
Container Runtime (Docker)
        ↓
Kubernetes Logs (kubectl logs)
        ↓
Log Aggregation (Fluentd/Filebeat)
        ↓
Log Storage (Elasticsearch/CloudWatch)
        ↓
Log Visualization (Kibana/CloudWatch Insights)
```

---

## Cost Optimization

### AWS Cost Breakdown (Monthly)

| Resource | Type | Cost (Free Tier) | Cost (After) |
|----------|------|------------------|--------------|
| EC2 Instance | t2.micro | $0 | ~$8.50 |
| EBS Storage | 8GB GP3 | $0 | ~$0.80 |
| Data Transfer | 15GB out | $0 | ~$0.00 |
| **Total** | | **$0** | **~$9.30** |

### Kubernetes Cost Optimization

1. **Resource Limits**
   - Set appropriate CPU/memory limits
   - Avoid over-provisioning
   - Use resource quotas

2. **Auto-scaling**
   - Scale down during low usage
   - Use HPA for dynamic scaling
   - Schedule CronJobs efficiently

3. **Image Optimization**
   - Multi-stage builds
   - Minimal base images
   - Layer caching

---

## Performance Optimization

### Application Level

1. **Code Optimization**
   - Efficient regex patterns
   - Caching validation results
   - Async processing (if needed)

2. **Configuration**
   - Optimized rules.json
   - Minimal validation overhead
   - Fast startup time

### Infrastructure Level

1. **Container Optimization**
   - Smaller image size
   - Faster startup
   - Resource efficiency

2. **Kubernetes Optimization**
   - Appropriate resource requests/limits
   - Health check tuning
   - Pod disruption budgets

3. **Network Optimization**
   - Service mesh (optional)
   - CDN for static assets
   - Regional deployment

---

