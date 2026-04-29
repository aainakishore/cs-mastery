#!/usr/bin/env python3
"""
AWS Batch 2 — aws-ecs-fargate, aws-rds-advanced
Unit 18 (AWS), orders 126-127
Run: python3 scripts/gen_aws_batch2.py [--overwrite]
"""

import json, sys
from pathlib import Path

OUT = Path(__file__).parent.parent / "src/content/topics/aws"
OUT.mkdir(parents=True, exist_ok=True)

TOPICS = [
    {
        "id": "aws-ecs-fargate",
        "unit": 18,
        "order": 126,
        "title": "AWS ECS & Fargate",
        "summary": "Run containerised workloads without managing servers: ECS task definitions, services, Fargate, ECR, and auto-scaling.",
        "prereqs": ["aws-vpc-networking"],
        "guide": """# AWS ECS & Fargate — Containers Without the Ops

## Mental Model
ECS (Elastic Container Service) is AWS's container orchestrator. Think: Kubernetes but with less YAML.
Fargate is the serverless compute engine for ECS: you define CPU/memory requirements and AWS runs your containers — no EC2 instance fleet to manage.

```
You provide:  Docker image + CPU + memory + config
AWS provides: VM, OS, Docker daemon, network plumbing

ECS on EC2:                         ECS on Fargate:
  ┌─────────────────┐                 ┌─────────────────┐
  │ EC2 Instance    │                 │ AWS Managed     │
  │ ┌─────────────┐ │                 │ ┌─────────────┐ │
  │ │ ECS Agent   │ │                 │ │  Your Task  │ │
  │ │  Container  │ │                 │ │  Container  │ │
  │ └─────────────┘ │                 │ └─────────────┘ │
  └─────────────────┘                 └─────────────────┘
  You manage EC2 fleet                  AWS manages host
```

## Core Concepts

### Task Definition — The Blueprint
```json
{
  "family": "my-app",
  "cpu": "256",
  "memory": "512",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "containerDefinitions": [{
    "name": "app",
    "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:latest",
    "portMappings": [{"containerPort": 8080}],
    "environment": [{"name": "ENV", "value": "prod"}],
    "secrets": [{"name": "DB_PASS", "valueFrom": "arn:aws:secretsmanager:..."}],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/my-app",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }]
}
```

### Cluster, Service, Task
```
Cluster: logical group of tasks/services (like a namespace)
  └── Service: long-running tasks, maintains desired count, integrates with ALB
      └── Task: one running instance of a task definition (like a pod in K8s)
```

**Service**: "Always keep 3 copies of this task running. Attach to ALB. Replace unhealthy tasks."

### Fargate CPU/Memory Combinations
```
CPU (vCPU units)  |  Memory options
256  (0.25 vCPU)  |  0.5, 1, 2 GB
512  (0.5  vCPU)  |  1-4 GB
1024 (1    vCPU)  |  2-8 GB
2048 (2    vCPU)  |  4-16 GB
4096 (4    vCPU)  |  8-30 GB
```

## ECR — Elastic Container Registry
```bash
# Push workflow:
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com

docker build -t my-app .
docker tag my-app:latest <account>.dkr.ecr.<region>.amazonaws.com/my-app:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/my-app:latest
```
ECR is private, encrypted at rest, integrated with IAM. Enable image scanning for CVEs.

## Networking — awsvpc Mode
Each Fargate task gets its own ENI (Elastic Network Interface) with its own private IP:
```
ALB (public subnet)
└── Target Group (IP-based)
    ├── Task 1: 10.0.1.50:8080 (private subnet AZ-A)
    ├── Task 2: 10.0.2.51:8080 (private subnet AZ-B)
    └── Task 3: 10.0.1.52:8080 (private subnet AZ-A)
```
Security Group on the task directly controls inbound/outbound.

## Auto Scaling
```
Target Tracking: "Keep average CPU at 60%"
  → ECS automatically adds/removes tasks

Step Scaling: "Add 2 tasks when CPU > 70%, remove 1 when CPU < 30%"

Scheduled: "Scale up to 10 tasks at 9am, down to 2 at 10pm"
```

## IAM — Two Roles You Need
```
Task Execution Role: allows ECS agent to pull image from ECR, write logs to CloudWatch
  → AmazonECSTaskExecutionRolePolicy (managed policy)

Task Role: permissions your APPLICATION code needs (S3, DynamoDB, etc.)
  → Custom policy specific to what your code accesses
```
**Rule:** Never hardcode AWS credentials in containers. Use the Task Role — ECS injects temporary credentials via instance metadata.

## Fargate vs EC2 launch type
| | Fargate | EC2 |
|---|---|---|
| Server management | None | You manage fleet |
| Cost | Per-task billing | EC2 instance billing |
| Startup time | ~30-60s | Faster (pre-warm) |
| Use when | Default choice, variable load | GPU, custom AMI, spot instances needed |

## Blue/Green Deployments with CodeDeploy
```
Old version (Blue):  100% traffic → Task v1
Deploy starts:
  → Launch Task v2 (new ALB target group)
  → Shift traffic: 10% → v2
  → Monitor (alarms, X-Ray traces)
  → Shift: 100% → v2
  → Terminate v1 (Blue)
```
Instant rollback: flip traffic back to Blue if alarms fire.

## Common Pitfalls
- **Using task execution role for app permissions**: separate execution role (pulling image) from task role (app access)
- **Not setting resource limits**: Fargate tasks without memory limits can OOM and restart repeatedly
- **Storing secrets in environment variables as plain text**: use `secrets` array to pull from AWS Secrets Manager or SSM Parameter Store
- **Single AZ deployment**: run services in at least 2 AZs — ECS spreads tasks if you configure multiple subnets
- **Large container images**: slow cold starts. Use multi-stage builds, Alpine base images, and ECR lifecycle policies to remove old images

## Connections
- `aws-vpc-networking` — Fargate tasks live in VPC subnets, use Security Groups
- `aws-mastery` — ECS integrates with ALB, CloudWatch, CodeDeploy
- `docker` — Fargate runs Docker containers; know Dockerfiles before ECS
- `kubernetes` — ECS is the AWS alternative to K8s; compare orchestration models
""",
        "questions": [
            {"id": "ecs-q1", "type": "mcq", "prompt": "What does AWS Fargate eliminate compared to ECS on EC2?", "choices": ["Container management", "Managing the underlying EC2 instance fleet and ECS agent", "Load balancing", "IAM permissions"], "answerIndex": 1, "explanation": "Fargate is serverless compute for containers — you specify CPU/memory and AWS handles the host VM, OS, and Docker daemon. You only manage your container.", "tags": ["fargate", "ecs-basics"]},
            {"id": "ecs-q2", "type": "mcq", "prompt": "What is an ECS Task Definition?", "choices": ["A running container instance", "The blueprint: defines container image, CPU, memory, ports, env vars, IAM roles, logging", "A group of running tasks", "An auto-scaling rule"], "answerIndex": 1, "explanation": "Task Definition is immutable (versioned). It describes WHAT to run. A Service decides HOW MANY to run and maintains that count.", "tags": ["task-definition"]},
            {"id": "ecs-q3", "type": "mcq", "prompt": "What is the difference between a Task and a Service in ECS?", "choices": ["No difference", "Task: one-time job. Service: long-running, maintains desired count, integrates with ALB, replaces unhealthy tasks", "Service is a premium feature", "Tasks run on EC2, Services run on Fargate"], "answerIndex": 1, "explanation": "Tasks are ephemeral (batch jobs, one-off scripts). Services are for web APIs, microservices — ECS keeps N copies running and restarts failed tasks automatically.", "tags": ["ecs-basics"]},
            {"id": "ecs-q4", "type": "mcq", "prompt": "What does 'awsvpc' network mode give each Fargate task?", "choices": ["Shared IP with the host", "Its own ENI and private IP address — direct security group control", "A public IP automatically", "Bridge network access only"], "answerIndex": 1, "explanation": "In awsvpc mode, each task gets its own Elastic Network Interface. This allows task-level security groups (not instance-level), and ALB can target the task IP directly.", "tags": ["networking"]},
            {"id": "ecs-q5", "type": "mcq", "prompt": "What is the ECS Task Execution Role vs Task Role?", "choices": ["Same role", "Execution role: used by ECS agent (pull image, write logs). Task Role: used by your application code (S3, DynamoDB access)", "Task role is deprecated", "Execution role is optional"], "answerIndex": 1, "explanation": "These are separate IAM roles. Execution role has the `AmazonECSTaskExecutionRolePolicy` managed policy. Task role has your custom application permissions. Never mix them.", "tags": ["iam", "security"]},
            {"id": "ecs-q6", "type": "mcq", "prompt": "How should you provide database passwords to Fargate containers?", "choices": ["Hardcode in Dockerfile", "Plain text environment variable in task definition", "Use the `secrets` field in task definition pointing to Secrets Manager or SSM Parameter Store", "Store in S3 and download on startup"], "answerIndex": 2, "explanation": "The `secrets` field in the container definition pulls values from Secrets Manager/SSM at task startup and injects them as environment variables — never visible in the task definition JSON.", "tags": ["security", "secrets"]},
            {"id": "ecs-q7", "type": "mcq", "prompt": "What is ECR (Elastic Container Registry)?", "choices": ["A Docker Hub alternative provided by AWS, private, IAM-integrated, with image scanning", "An EC2 image registry", "A Kubernetes manifest store", "An AWS code repository"], "answerIndex": 0, "explanation": "ECR is a fully managed private Docker container registry. Integrated with IAM (no separate credentials needed from EC2/ECS). Supports vulnerability scanning via Amazon Inspector.", "tags": ["ecr"]},
            {"id": "ecs-q8", "type": "mcq", "prompt": "What is the minimum Fargate CPU allocation?", "choices": ["128 units (0.125 vCPU)", "256 units (0.25 vCPU)", "512 units (0.5 vCPU)", "1024 units (1 vCPU)"], "answerIndex": 1, "explanation": "Fargate minimum is 256 CPU units (0.25 vCPU) with 0.5-2GB memory. Useful for lightweight sidecars, cron jobs, or low-traffic APIs.", "tags": ["fargate"]},
            {"id": "ecs-q9", "type": "mcq", "prompt": "ECS auto-scaling with Target Tracking policy — what does it do?", "choices": ["Scales at specific times", "Maintains a target metric (e.g., average CPU 60%) by automatically adding/removing tasks", "Scales based on SQS depth only", "Only scale up, never down"], "answerIndex": 1, "explanation": "Target Tracking is the simplest scaling policy — set a target metric and ECS Application Auto Scaling handles the math. Works for CPU, memory, ALB request count, and custom metrics.", "tags": ["auto-scaling"]},
            {"id": "ecs-q10", "type": "mcq", "prompt": "For a Fargate task to pull an image from ECR, which IAM role needs the permission?", "choices": ["Task Role", "Task Execution Role", "EC2 Instance Role", "CodeDeploy Role"], "answerIndex": 1, "explanation": "The ECS agent runs as the Task Execution Role. It needs ECR pull permissions (`ecr:GetDownloadUrlForLayer`, `ecr:BatchGetImage`) to fetch the image before starting your container.", "tags": ["iam", "ecr"]},
            {"id": "ecs-q11", "type": "mcq", "prompt": "What is ECS Blue/Green deployment?", "choices": ["Deploying two container versions simultaneously", "Gradually shifting traffic from old (Blue) to new (Green) version via two ALB target groups, with instant rollback capability", "Running containers in two AZs", "Blue = EC2, Green = Fargate"], "answerIndex": 1, "explanation": "CodeDeploy manages the traffic shift between Blue (current) and Green (new). If CloudWatch alarms fire during shift, automatic rollback returns traffic to Blue instantly.", "tags": ["deployments"]},
            {"id": "ecs-q12", "type": "multi", "prompt": "Which are benefits of running ECS on Fargate vs EC2?", "choices": ["No EC2 fleet management", "Lower cost for steady high load", "Per-task resource billing", "Faster startup times vs EC2", "No server patching"], "answerIndexes": [0, 2, 4], "explanation": "Fargate: no fleet management, per-task billing, no OS patching. EC2 is cheaper for steady, predictable high load (EC2 Spot) and has faster startup (pre-warmed instances).", "tags": ["fargate"]},
            {"id": "ecs-q13", "type": "mcq", "prompt": "What CloudWatch log configuration should you always add to Fargate containers?", "choices": ["awslogs with log group, region, and stream prefix", "Logging is automatic — no config needed", "CloudTrail for container logs", "Only works with ECS on EC2"], "answerIndex": 0, "explanation": "The `awslogs` log driver sends container stdout/stderr to CloudWatch Logs. Without it, you have no visibility into your running containers.", "tags": ["logging", "observability"]},
            {"id": "ecs-q14", "type": "mcq", "prompt": "Why should Fargate services be deployed to multiple subnets in different AZs?", "choices": ["Required by AWS", "ECS distributes tasks across AZs — if one AZ fails, tasks in other AZs continue serving traffic", "Reduces load on a single subnet", "Multi-AZ is only for RDS"], "answerIndex": 1, "explanation": "Multi-subnet (multi-AZ) deployment ensures availability if an AZ becomes unavailable. ECS tries to spread tasks evenly across the provided subnets.", "tags": ["high-availability"]},
            {"id": "ecs-q15", "type": "mcq", "prompt": "How does ALB know which Fargate task to send requests to?", "choices": ["EC2 instance IDs", "IP-based target group pointing to the task's ENI private IP on the container port", "DNS resolution", "ECS does a round-robin via metadata service"], "answerIndex": 1, "explanation": "With awsvpc networking, ALB uses IP-based target groups. Each task registers its private IP and container port. ALB health-checks the IPs directly.", "tags": ["networking", "alb"]},
            {"id": "ecs-q16", "type": "mcq", "prompt": "What is an ECS Cluster?", "choices": ["A group of EC2 instances only", "A logical namespace grouping ECS services and tasks — can contain Fargate tasks, EC2 instances, or both", "An auto-scaling group", "A VPC subnet"], "answerIndex": 1, "explanation": "A cluster is a logical boundary. You can mix Fargate and EC2 tasks in the same cluster. Useful for separating prod/staging or different applications.", "tags": ["ecs-basics"]},
            {"id": "ecs-q17", "type": "mcq", "prompt": "What reduces Fargate cold start time significantly?", "choices": ["Using more memory", "Using smaller container images (multi-stage builds, Alpine base)", "More vCPUs", "Using ECS on EC2 instead"], "answerIndex": 1, "explanation": "Fargate pulls the container image before starting the task. A 2GB image takes much longer than a 50MB Alpine-based image. Multi-stage builds + minimal base images are critical for fast starts.", "tags": ["performance", "docker"]},
            {"id": "ecs-q18", "type": "mcq", "prompt": "ECS Service discovery allows services to find each other via:", "choices": ["Static IP addresses", "AWS Cloud Map DNS names (e.g., service.namespace.local)", "AWS Direct Connect", "API Gateway only"], "answerIndex": 1, "explanation": "ECS integrates with AWS Cloud Map for service discovery. Tasks register DNS names on creation and deregister on termination — services can call each other by DNS name.", "tags": ["service-discovery"]},
            {"id": "ecs-q19", "type": "mcq", "prompt": "Where should container secrets (API keys, DB passwords) come from in production?", "choices": ["Dockerfile ENV instructions", "Plain text in task definition environment variables", "AWS Secrets Manager or SSM Parameter Store via the secrets field", "Baked into the Docker image"], "answerIndex": 2, "explanation": "Environment variables are visible in AWS console and to anyone with DescribeTaskDefinition IAM permission. Secrets Manager/SSM integration encrypts secrets at rest and in transit.", "tags": ["security", "secrets"]},
            {"id": "ecs-q20", "type": "multi", "prompt": "Which AWS services integrate natively with ECS Fargate?", "choices": ["ALB (Application Load Balancer)", "AWS Secrets Manager", "Amazon ECR", "Amazon RDS (direct)", "CloudWatch Logs"], "answerIndexes": [0, 1, 2, 4], "explanation": "ALB, Secrets Manager, ECR, and CloudWatch Logs all have native ECS integration. RDS is used by applications inside Fargate tasks but doesn't integrate at the ECS level directly.", "tags": ["integrations"]},
        ],
        "flashcards": [
            {"id": "ecs-fc1", "front": "Task vs Service in ECS", "back": "Task: one-time or short-lived job. Service: always-running workload (web API) — ECS maintains desired count, replaces failed tasks, integrates with ALB.", "tags": ["ecs-basics"]},
            {"id": "ecs-fc2", "front": "Execution Role vs Task Role", "back": "Execution Role: ECS agent uses this to pull image from ECR + write logs to CloudWatch. Task Role: YOUR application uses this to call S3, DynamoDB, etc. Keep them separate.", "tags": ["iam"]},
            {"id": "ecs-fc3", "front": "awsvpc networking benefit", "back": "Each Fargate task gets its own ENI = own private IP = own Security Group. ALB targets task IPs directly. No port collision between tasks on the same host.", "tags": ["networking"]},
            {"id": "ecs-fc4", "front": "How to inject secrets into Fargate", "back": "Use `secrets` array in container definition. Point to Secrets Manager ARN or SSM Parameter Store path. ECS fetches at runtime, injects as env var. Never use plaintext env vars for secrets.", "tags": ["security"]},
            {"id": "ecs-fc5", "front": "Fargate cold start reduction", "back": "Smaller images = faster pulls = faster start. Use multi-stage Docker builds + Alpine/distroless base images. ECR image caching helps on subsequent starts in the same region.", "tags": ["performance"]},
            {"id": "ecs-fc6", "front": "ECS Service Auto Scaling modes", "back": "Target Tracking: maintain metric (CPU 60%). Step Scaling: rule-based add/remove. Scheduled: time-based. Target Tracking is the default recommendation — simple and reactive.", "tags": ["auto-scaling"]},
            {"id": "ecs-fc7", "front": "Blue/Green ECS deployment", "back": "CodeDeploy shifts traffic between two ALB target groups (Blue=old, Green=new). Monitor with CloudWatch alarms. Auto-rollback if alarms fire. Zero downtime.", "tags": ["deployments"]},
            {"id": "ecs-fc8", "front": "ECR image scanning", "back": "Enable `scanOnPush: true` on ECR repository. Amazon Inspector scans for OS and package CVEs. View findings in ECR console or Security Hub. No extra cost for basic scanning.", "tags": ["ecr", "security"]},
        ],
        "project": {
            "brief": "Design the containerised deployment architecture for a Node.js REST API. The API needs: 3 replicas minimum, automatic scaling from 3-20 based on HTTP request count, zero-downtime deployments, database password from Secrets Manager, logs in CloudWatch, and access to S3 for file storage. Design: task definition structure (CPU/memory/roles), Service configuration, scaling policy, deployment strategy, and networking (which subnets, SG rules). No code — architecture decisions only.",
            "checklist": [
                {"id": "ecs-p1", "text": "Define task definition: CPU/memory, both IAM roles, logging config, secrets reference", "weight": 20},
                {"id": "ecs-p2", "text": "Configure ECS Service: desired count, deployment circuit breaker, ALB integration", "weight": 20},
                {"id": "ecs-p3", "text": "Design auto-scaling: metric choice, min/max, target value", "weight": 20},
                {"id": "ecs-p4", "text": "Choose deployment strategy (rolling vs blue/green) and justify", "weight": 20},
                {"id": "ecs-p5", "text": "Define networking: private subnets, SG rules (ALB → task, task → RDS, task → S3 via endpoint)", "weight": 20},
            ],
            "hints": [
                "CPU: 512 (0.5 vCPU), Memory: 1024MB for a Node.js API. Scale by ALBRequestCountPerTarget metric.",
                "Secrets Manager: Task Execution Role needs secretsmanager:GetSecretValue. Task Role needs s3:GetObject for S3 access.",
                "Blue/Green (CodeDeploy) for zero-downtime. Rolling update also works but doesn't support instant rollback.",
                "SG: ALB SG allows 443 from 0.0.0.0/0. Task SG allows 8080 from ALB SG. RDS SG allows 5432 from Task SG. Task SG allows HTTPS out for Secrets Manager (or use VPC endpoint).",
            ],
        },
    },
    {
        "id": "aws-rds-advanced",
        "unit": 18,
        "order": 127,
        "title": "AWS RDS Advanced",
        "summary": "Master RDS Multi-AZ, read replicas, Aurora, RDS Proxy, parameter groups, and backup/restore strategies.",
        "prereqs": ["aws-ecs-fargate"],
        "guide": """# AWS RDS Advanced — Make Your Database Bulletproof

## Mental Model
RDS removes the undifferentiated heavy lifting of database operations: patching, backups, failover, scaling. But to use it well, you still need to understand WHAT it's doing under the hood.

```
RDS handles:          You still manage:
  OS patching          Schema design
  Disk management      Query optimisation
  Backups              Connection pooling
  Failover             Security groups
  Read scaling         Parameter tuning
```

## Multi-AZ — High Availability

```
Primary DB (AZ-A)  ──synchronous replication──►  Standby DB (AZ-B)
      │                                                  │
   Writes go here                              Hot standby (not readable)
      │                                                  │
   CNAME: mydb.cluster.us-east-1.rds.amazonaws.com
      │ (DNS switches on failover — ~60 seconds)
```

**Key facts:**
- Standby is NOT a read replica — it's an exact mirror, synchronously updated
- Failover is automatic: RDS detects loss of primary, promotes standby, updates DNS
- Failover takes ~60-120 seconds — applications must handle reconnection
- Multi-AZ doubles your storage cost but provides 99.95% availability SLA

**Failover triggers:** instance failure, AZ outage, OS maintenance reboot, storage failure, "Reboot with failover" in console.

## Read Replicas — Horizontal Read Scaling

```
Primary DB ──asynchronous replication──► Read Replica 1 (same region)
           ──asynchronous replication──► Read Replica 2 (different region)
           ──asynchronous replication──► Read Replica 3 (can be promoted to primary)
```

**Rules:**
- Asynchronous = slight replication lag (milliseconds to seconds)
- Read replicas ARE readable endpoints — send SELECT queries there
- One primary can have up to 5 read replicas (MySQL/PostgreSQL)
- Cross-region replicas add disaster recovery capability
- A read replica CAN be promoted to become a standalone primary (breaks replication)

**Use case:** Reporting queries, analytics dashboards, read-heavy mobile apps.

## RDS Proxy — Connection Pooling

```
Without proxy:
  Lambda/ECS tasks (1000 concurrent) ──────────────► RDS (500 max connections) ← OVERWHELMED

With proxy:
  Lambda/ECS tasks (1000 concurrent) ──► RDS Proxy (pools 50 DB connections) ──► RDS ← HAPPY
```

RDS Proxy maintains a warm pool of database connections and multiplexes thousands of application connections through them.

**When to use:** Lambda functions (each invocation would open a new connection), ECS services with high concurrency, any workload that frequently opens/closes connections.

**Supports:** MySQL/PostgreSQL/MariaDB. Integrates with Secrets Manager (no credentials in code). Failover detection: RDS Proxy detects failover and reconnects to new primary — reduces failover impact from ~60s to ~5s.

## Aurora — AWS's Managed Database Cluster

```
Aurora Cluster Architecture:
  Writer Instance (Primary) ─── Cluster Storage Volume (6 copies across 3 AZs) ───┐
  Reader Instance 1 ──────────────────────────────────────────────────────────────┤
  Reader Instance 2 ──────────────────────────────────────────────────────────────┘
         │
  Cluster endpoint: writes → writer
  Reader endpoint:  reads → auto load-balanced across readers
```

**Aurora vs RDS MySQL:**
| | RDS MySQL | Aurora MySQL |
|---|---|---|
| Storage | EBS per instance | Shared cluster volume |
| Replication | Async replication | All instances share same storage |
| Replication lag | Tens of ms | Sub-10ms |
| Read replicas | 5 max | 15 max |
| Failover | ~60s | ~30s |
| Storage auto-scaling | Manual (modify) | Automatic (up to 128TB) |
| Cost | Lower | ~20% higher |

**Aurora Serverless v2:** instances scale CPU/memory automatically between a min and max capacity — you pay per ACU-second. Great for dev/test or unpredictable workloads.

## Backups and Point-in-Time Recovery

```
Automated backups:
  - Daily snapshot during maintenance window
  - Transaction logs captured every 5 minutes
  - Retention: 1-35 days
  - Point-in-time restore: any point within retention window

Manual snapshots:
  - Persist until you delete them
  - Can be shared across accounts and regions
  - Basis for database migration

Restore creates a NEW RDS instance — update connection strings in app
```

## Parameter Groups — Tune Your Database

```
Default parameter group (read-only, managed by AWS)
Custom parameter group (you create, modify, assign to RDS instance)

Key parameters:
  max_connections:     max simultaneous DB connections
  innodb_buffer_pool_size: MySQL buffer pool (use 75% of instance RAM)
  work_mem:            PostgreSQL — per-query sort memory
  log_slow_queries:    Enable slow query log (HUGE for performance tuning)
  binlog_format:       Binary log format (ROW required for replication)
```

**Changes:** Static parameters require reboot. Dynamic parameters apply immediately.

## Security Best Practices

```
1. Private subnets only — no public access
2. Security groups: allow only app tier IPs (not 0.0.0.0/0)
3. Encryption at rest (KMS) — enables at creation, can't add later
4. Encryption in transit — use SSL/TLS for connections
5. IAM authentication — authenticate with temporary IAM tokens instead of passwords
6. Audit logging — enable CloudWatch logs (error, general, slow query logs)
```

## Common Pitfalls
- **Assuming Multi-AZ = read scaling**: Multi-AZ standby is NOT readable. Use read replicas for read scaling.
- **Not using connection pooling**: every Lambda invocation opening a new connection → RDS max_connections exhausted. Use RDS Proxy.
- **Modifying production during peak hours**: modifications (instance resize, storage) may cause brief downtime. Use maintenance windows.
- **Storing RDS password in env vars**: use Secrets Manager + IAM auth.
- **Not setting max_connections properly**: default is based on instance size but often too high for Aurora with many small instances.
- **Forgetting to encrypt at creation**: encryption can't be turned on after instance creation. Always check this box.

## Connections
- `aws-vpc-networking` — RDS lives in private subnets, protected by VPC security groups
- `aws-lambda-deep-dive` — Lambda + RDS = must use RDS Proxy
- `aws-ecs-fargate` — ECS task connects to RDS via security group rules
- `database-internals` — understanding B-Tree indexes, WAL helps tune RDS
- `caching-advanced` — ElastiCache (Redis) is the first line of defence before RDS reads
""",
        "questions": [
            {"id": "rds-adv-q1", "type": "mcq", "prompt": "What does RDS Multi-AZ provide?", "choices": ["Read scaling with a readable standby", "High availability with automatic failover — synchronous standby NOT readable", "Cross-region replication", "Horizontal write scaling"], "answerIndex": 1, "explanation": "Multi-AZ standby is hot-standby only — synchronously replicated but not readable. Failover is automatic (~60-120s). Multi-AZ is for HA, NOT for read scaling.", "tags": ["multi-az", "ha"]},
            {"id": "rds-adv-q2", "type": "mcq", "prompt": "What is the key difference between Multi-AZ and Read Replicas?", "choices": ["Both provide read scaling", "Multi-AZ: synchronous, not readable, for HA. Read Replicas: asynchronous, readable, for read scaling.", "Multi-AZ is cheaper", "Read Replicas provide faster failover"], "answerIndex": 1, "explanation": "These solve different problems. Multi-AZ = availability. Read Replicas = read throughput. You can and should use both simultaneously.", "tags": ["multi-az", "read-replicas"]},
            {"id": "rds-adv-q3", "type": "mcq", "prompt": "What happens to client connections during an RDS Multi-AZ failover?", "choices": ["No impact — transparent", "Existing connections break; new connections work after DNS TTL (~60s); app must reconnect", "Only new connections fail", "Writes are buffered and replayed"], "answerIndex": 1, "explanation": "RDS updates the CNAME DNS entry to point to the new primary. Applications must handle reconnection. RDS Proxy reduces this disruption by pre-connecting to the new primary.", "tags": ["multi-az", "failover"]},
            {"id": "rds-adv-q4", "type": "mcq", "prompt": "What is RDS Proxy primarily used for?", "choices": ["Read caching", "Connection pooling: reduces DB connection overhead for Lambda/ECS by multiplexing thousands of app connections through a small pool of DB connections", "Multi-region replication", "Query optimisation"], "answerIndex": 1, "explanation": "RDS Proxy sits between app and RDS, maintaining a warm pool of connections. Critical for Lambda (stateless, many short-lived connections) and ECS with high concurrency.", "tags": ["rds-proxy"]},
            {"id": "rds-adv-q5", "type": "mcq", "prompt": "Aurora read replicas vs RDS MySQL read replicas — key difference?", "choices": ["No difference", "Aurora replicas share the same storage with the writer — sub-10ms lag. RDS MySQL replicas have async replication with tens-of-ms lag.", "Aurora has fewer replicas", "RDS MySQL replicas are cheaper"], "answerIndex": 1, "explanation": "Aurora's shared cluster storage means reader instances see writes almost immediately (shared volume, not replication). RDS MySQL uses binary log replication — has measurable lag.", "tags": ["aurora", "read-replicas"]},
            {"id": "rds-adv-q6", "type": "mcq", "prompt": "What is Aurora Serverless v2?", "choices": ["Aurora that runs without storage", "Aurora capacity that auto-scales CPU/memory in fine-grained increments — pay per ACU-second", "Aurora that doesn't need a VPC", "Free-tier Aurora"], "answerIndex": 1, "explanation": "Aurora Serverless v2 scales from minimum capacity (0.5 ACU) to maximum (128 ACU) based on load — in seconds. Great for dev/test, variable workloads, or unpredictable traffic.", "tags": ["aurora", "serverless"]},
            {"id": "rds-adv-q7", "type": "mcq", "prompt": "What does RDS point-in-time recovery allow?", "choices": ["Restore to any snapshot", "Restore to any point within the backup retention window (1-35 days) from automated backups + transaction logs", "Undo last 10 queries", "Instant rollback of schema changes"], "answerIndex": 1, "explanation": "RDS captures daily snapshots + continuous transaction logs. You can restore to any second within the retention window by replaying logs from the nearest snapshot.", "tags": ["backups", "pitr"]},
            {"id": "rds-adv-q8", "type": "mcq", "prompt": "When restoring an RDS backup, what happens?", "choices": ["Original instance is restored in place", "A NEW RDS instance is created — you must update connection strings", "The instance is paused and snapshot is applied", "Only in-place restore is supported"], "answerIndex": 1, "explanation": "RDS restore always creates a NEW instance with a new endpoint. You must update your connection string or DNS alias. This is intentional — keeps old instance available while you validate.", "tags": ["backups"]},
            {"id": "rds-adv-q9", "type": "mcq", "prompt": "Why must RDS encryption be enabled at creation time?", "choices": ["It can be added anytime", "RDS cannot encrypt an existing unencrypted instance — you must snapshot, copy with encryption enabled, and restore", "Encryption is automatic", "Only Aurora supports encryption"], "answerIndex": 1, "explanation": "Encryption is tied to the underlying storage. To encrypt an existing unencrypted RDS: 1) take snapshot, 2) copy snapshot with encryption, 3) restore to new instance. Always enable encryption upfront.", "tags": ["security", "encryption"]},
            {"id": "rds-adv-q10", "type": "mcq", "prompt": "How many read replicas can Aurora MySQL support?", "choices": ["5", "10", "15", "Unlimited"], "answerIndex": 2, "explanation": "Aurora supports up to 15 read replicas (vs 5 for RDS MySQL). Aurora readers share the cluster storage — each reader adds read capacity without storage overhead.", "tags": ["aurora", "read-replicas"]},
            {"id": "rds-adv-q11", "type": "mcq", "prompt": "What is an RDS Parameter Group?", "choices": ["A group of RDS instances", "Database engine configuration settings (e.g., max_connections, buffer pool size) applied to an RDS instance", "IAM permission group for RDS", "Subnet routing configuration"], "answerIndex": 1, "explanation": "Parameter Groups contain engine-level config like `max_connections`, `innodb_buffer_pool_size`, and `log_slow_queries`. Default groups are managed by AWS (read-only). Create custom groups to change settings.", "tags": ["parameter-groups"]},
            {"id": "rds-adv-q12", "type": "mcq", "prompt": "When does a Parameter Group change take effect?", "choices": ["Always immediately", "Dynamic parameters: immediately. Static parameters: require DB instance reboot.", "Only after 24 hours", "On next backup window"], "answerIndex": 1, "explanation": "Static parameters (like `max_connections` in some configs) require a reboot. Dynamic parameters take effect without restart. Check the 'Apply type' column in the console.", "tags": ["parameter-groups"]},
            {"id": "rds-adv-q13", "type": "mcq", "prompt": "How does RDS Proxy improve failover for Lambda functions?", "choices": ["It prevents failovers", "RDS Proxy detects the failover and reconnects to the new primary — reduces connection interruption from ~60s to ~5s", "Lambda automatically reconnects", "Proxy caches queries during failover"], "answerIndex": 1, "explanation": "During Multi-AZ failover, RDS Proxy maintains connections and transparently reconnects to the new primary. Lambda functions using the proxy endpoint see much shorter disruption.", "tags": ["rds-proxy", "failover"]},
            {"id": "rds-adv-q14", "type": "multi", "prompt": "Which IAM authentication for RDS provides:", "choices": ["Temporary credentials that auto-expire (no long-lived passwords)", "Integration with IAM roles (ECS/Lambda don't need to store DB credentials)", "Audit trail in CloudTrail for every DB authentication", "Faster query execution", "Encryption at rest"], "answerIndexes": [0, 1, 2], "explanation": "IAM authentication generates short-lived authentication tokens. Applications authenticated via IAM role don't need stored DB passwords. Every auth attempt is logged in CloudTrail.", "tags": ["security", "iam"]},
            {"id": "rds-adv-q15", "type": "mcq", "prompt": "The primary Aurora cluster endpoint routes writes to:", "choices": ["All instances round-robin", "Always the current writer instance — transparently updated on failover", "The instance with lowest CPU", "A load balancer"], "answerIndex": 1, "explanation": "Aurora's cluster endpoint always resolves to the current writer. On failover, Aurora promotes a reader and updates the endpoint DNS (faster than RDS Multi-AZ thanks to shared storage).", "tags": ["aurora"]},
            {"id": "rds-adv-q16", "type": "mcq", "prompt": "Why would you use cross-region read replicas?", "choices": ["Reduce latency for global users + Disaster Recovery (DR)", "Cross-region replicas are bidirectional", "Required for Multi-AZ", "Only for compliance"], "answerIndex": 0, "explanation": "Cross-region read replicas serve two purposes: (1) local reads for globally distributed users; (2) DR — can be promoted to primary if entire primary region fails.", "tags": ["read-replicas", "disaster-recovery"]},
            {"id": "rds-adv-q17", "type": "mcq", "prompt": "What is the primary benefit of Aurora's shared cluster storage?", "choices": ["Lower cost", "All instances (writer + readers) share the same 6-copy storage — no replication lag for readers, instant consistency", "Larger storage capacity", "Better encryption"], "answerIndex": 1, "explanation": "Aurora's storage is automatically replicated 6 ways across 3 AZs. Readers access the SAME data as the writer (only separated by a distributed lock). This eliminates replication lag.", "tags": ["aurora"]},
            {"id": "rds-adv-q18", "type": "mcq", "prompt": "Enable slow query log in RDS Parameter Group to:", "choices": ["Breach compliance", "Identify queries taking longer than long_query_time — critical for finding and fixing performance bottlenecks", "Reduce query latency automatically", "Required for Multi-AZ"], "answerIndex": 1, "explanation": "Slow query logs reveal N+1 queries, missing indexes, and inefficient JOINs. Set `long_query_time=1` (1 second threshold) and `slow_query_log=1` in your Parameter Group.", "tags": ["parameter-groups", "performance"]},
            {"id": "rds-adv-q19", "type": "mcq", "prompt": "RDS automated backup retention window maximum is:", "choices": ["7 days", "14 days", "35 days", "90 days"], "answerIndex": 2, "explanation": "RDS automated backups can be retained for 1-35 days. For compliance or longer retention, take manual snapshots (they persist until manually deleted).", "tags": ["backups"]},
            {"id": "rds-adv-q20", "type": "multi", "prompt": "Which are true about RDS encryption?", "choices": ["Must be enabled at creation time", "Encrypts storage, automated backups, and read replicas", "Read replicas of encrypted instances are also encrypted", "Can be enabled on existing instances without data migration", "Uses AES-256 via AWS KMS"], "answerIndexes": [0, 1, 2, 4], "explanation": "Encryption: must enable at creation (0), covers all storage + backups + replicas (1, 2), uses KMS AES-256 (4). You CANNOT enable encryption on an existing unencrypted instance (4 is false).", "tags": ["security", "encryption"]},
        ],
        "flashcards": [
            {"id": "rds-adv-fc1", "front": "Multi-AZ vs Read Replica", "back": "Multi-AZ: synchronous standby, NOT readable, automatic HA failover. Read Replica: asynchronous, readable, for read scaling. Use both simultaneously for full HA + read scale.", "tags": ["multi-az", "read-replicas"]},
            {"id": "rds-adv-fc2", "front": "When to use RDS Proxy", "back": "Lambda functions (new DB connection per invocation), ECS services with high task count, any app that frequently opens/closes DB connections. Reduces max_connections pressure dramatically.", "tags": ["rds-proxy"]},
            {"id": "rds-adv-fc3", "front": "Aurora vs RDS MySQL key advantage", "back": "Aurora readers share cluster storage — sub-10ms read lag (vs async replication). 15 read replicas (vs 5). Faster failover (~30s vs ~60s). ~20% higher cost.", "tags": ["aurora"]},
            {"id": "rds-adv-fc4", "front": "RDS encryption rule", "back": "Enable at creation — cannot add later. Encrypts storage + backups + replicas + snapshots. Uses KMS (AES-256). Read replicas of encrypted DB must also be encrypted.", "tags": ["security"]},
            {"id": "rds-adv-fc5", "front": "RDS restore creates a new instance", "back": "Always. Restoring a backup or snapshot creates a NEW RDS instance with a new endpoint. Update app connection strings or use a CNAME/Route53 alias to reduce downtime.", "tags": ["backups"]},
            {"id": "rds-adv-fc6", "front": "Aurora Serverless v2 use case", "back": "Variable/unpredictable workloads (dev, staging, batch). Scales in ~seconds from 0.5 to 128 ACU. Pay per ACU-second. Not for latency-sensitive prod traffic with known steady load.", "tags": ["aurora", "serverless"]},
            {"id": "rds-adv-fc7", "front": "Slow query log parameter", "back": "`slow_query_log=1` + `long_query_time=1` in custom Parameter Group. Logs queries > 1 second to CloudWatch. Essential first step for RDS performance debugging.", "tags": ["performance"]},
            {"id": "rds-adv-fc8", "front": "Multi-AZ failover timing", "back": "~60-120 seconds. Involves DNS flip. Apps must handle reconnection (exponential backoff). RDS Proxy reduces this to ~5s by maintaining connection state.", "tags": ["multi-az", "failover"]},
        ],
        "project": {
            "brief": "Design the database tier for a high-traffic e-commerce platform. Requirements: 99.99% availability, < 100ms read latency, 10,000 concurrent app connections (from Lambda + ECS), point-in-time recovery, read-heavy traffic (80% reads, 20% writes). Choose between Aurora and RDS MySQL. Design: engine choice, Multi-AZ vs cluster, read replicas needed, RDS Proxy configuration, backup strategy, encryption, and how you'd route reads vs writes in application code.",
            "checklist": [
                {"id": "rds-adv-p1", "text": "Engine choice (Aurora vs RDS MySQL) with justification for all requirements", "weight": 20},
                {"id": "rds-adv-p2", "text": "Read replica strategy: count, placement (same/cross-region), how app routes reads", "weight": 20},
                {"id": "rds-adv-p3", "text": "RDS Proxy configuration: why needed, which connections it handles", "weight": 20},
                {"id": "rds-adv-p4", "text": "Backup strategy: automated retention, manual snapshots, PITR for compliance", "weight": 20},
                {"id": "rds-adv-p5", "text": "Security: encryption, IAM auth vs password, SG rules, VPC placement", "weight": 20},
            ],
            "hints": [
                "Aurora: 99.99% availability, up to 15 readers, sub-10ms replication lag — better for 99.99% SLA and 80% read traffic.",
                "RDS Proxy: essential for Lambda connections. 10,000 concurrent connections → Proxy maintains ~50-100 actual DB connections.",
                "Reads: use Aurora reader endpoint (auto load-balances). Writes: cluster endpoint. Use connection pool that separates read/write.",
                "IAM authentication: Lambda and ECS Task Roles request IAM tokens — no stored passwords, auto-rotated, CloudTrail audit.",
            ],
        },
    },
]


def write_topic(topic: dict, overwrite: bool = False) -> None:
    path = OUT / f"{topic['id']}.json"
    if path.exists() and not overwrite:
        if len(topic.get("questions", [])) >= 20:
            print(f"  SKIP {path.name}")
            return
    path.write_text(json.dumps(topic, indent=2, ensure_ascii=False))
    print(f"  WROTE {path.name} ({len(topic.get('questions',[]))}q, {len(topic.get('flashcards',[]))}fc)")


if __name__ == "__main__":
    overwrite = "--overwrite" in sys.argv
    print(f"Writing AWS batch 2 -> {OUT}/")
    for t in TOPICS:
        write_topic(t, overwrite)
    print("Done.")

