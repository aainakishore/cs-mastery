#!/usr/bin/env python3
"""
AWS — Batch 1
Topics: aws-lambda-deep-dive, aws-vpc-networking
Unit 18 (AWS), orders 124-125
Run: python3 scripts/gen_aws_batch1.py [--overwrite]
"""

import json, sys
from pathlib import Path

OUT = Path(__file__).parent.parent / "src/content/topics/aws"
OUT.mkdir(parents=True, exist_ok=True)

TOPICS = [
    {
        "id": "aws-lambda-deep-dive",
        "unit": 18,
        "order": 124,
        "title": "AWS Lambda Deep Dive",
        "summary": "Master Lambda internals: execution model, cold starts, layers, event sources, concurrency, and cost optimisation.",
        "prereqs": ["aws-practitioner"],
        "guide": """# AWS Lambda Deep Dive — Serverless at the Metal

## Mental Model
Lambda is a function-as-a-service: you give AWS a function, and it runs it in response to events. You don't manage servers, but you DO manage execution context, memory, concurrency, and cold starts.

```
Event source → Lambda trigger → Lambda function (your code)
                                       │
                               Execution environment
                               ├── Runtime (Node/Python/Java...)
                               ├── /tmp (ephemeral storage, 512MB-10GB)
                               ├── Environment variables
                               └── Lambda Layer (shared code/libs)
```

## Execution Model — What Happens When Lambda Runs

### Cold Start vs Warm Start
```
COLD START (new execution environment created):
  1. Download your code package from S3
  2. Spin up execution environment (VM/container)
  3. Start runtime (JVM, Node process, Python interpreter)
  4. Run initialization code (outside handler)
  5. Run your handler function

WARM START (existing environment reused):
  1. Run your handler function  ← only this step!

Cold start overhead (approximate):
  Node.js:     ~100-200ms
  Python:      ~100-200ms
  Java (JVM):  ~500ms–2s  ← worst offender
  Java (GraalVM native): ~50ms
```

**Rule:** Code outside your handler (DB connections, SDK clients) runs ONCE on cold start and is cached for subsequent warm invocations. Exploit this.

```python
import boto3

# GOOD: initialized once, reused across warm invocations
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')

def handler(event, context):
    # table is already initialized
    return table.get_item(Key={'id': event['id']})
```

## Memory, CPU, and Timeout

```
Memory: 128MB – 10,240MB
CPU:    Proportional to memory (more memory = more vCPU allocated)
Timeout: max 15 minutes

Rule: If your function is CPU-bound, increase memory — it also increases CPU.
      At 1,769MB you get 1 full vCPU. At 3,008MB you get 2 vCPUs.
```

### Pricing
```
Cost = (invocations × $0.20/million) + (duration × memory × $0.0000166667/GB-second)

Example: 1M invocations, 512MB, avg 200ms each:
  Invocations: 1,000,000 × $0.0000002 = $0.20
  Duration:    1,000,000 × 0.2s × 0.5GB × $0.0000166667 = $1.67
  Total: ~$1.87/month — very cheap!
```

## Lambda Layers — Shared Code and Dependencies

```
Lambda Layer structure:
  layer.zip
  └── python/
      └── lib/
          └── python3.12/
              └── site-packages/
                  ├── requests/
                  └── boto3/

Attach up to 5 layers to a function. Layers are versioned.
```

**Use cases:**
- Common libraries (requests, numpy) shared across functions
- Lambda Extensions (monitoring agents, secret fetchers)
- Custom runtimes

## Concurrency — The Critical Knob

```
Concurrency = number of simultaneous running executions

Account default: 1,000 concurrent executions across ALL functions
Reserved concurrency: guarantee N executions for one function (others can't use them)
Provisioned concurrency: pre-warm N environments (no cold starts) — costs more

Throttling: when concurrency limit hit → Lambda returns 429 → caller retries
```

### Concurrency formula
```
Concurrency = (invocations/second) × (average duration in seconds)
Example: 100 req/s, 500ms average → 100 × 0.5 = 50 concurrent executions
```

## Event Sources and Invocation Patterns

| Event Source | Invocation Type | Error Handling |
|---|---|---|
| API Gateway / ALB | Synchronous | Client gets error immediately |
| S3 / SNS | Asynchronous | Lambda retries 2x, then DLQ |
| SQS | Polling (Lambda pulls) | Messages return to queue on failure |
| DynamoDB Streams | Polling | Retry until success or expiry |
| EventBridge | Asynchronous | Retries + DLQ |

### Dead Letter Queue (DLQ) for async failures
```json
{
  "FunctionName": "my-function",
  "DeadLetterConfig": {
    "TargetArn": "arn:aws:sqs:us-east-1:123456789:my-dlq"
  }
}
```

## Lambda with SQS — The Standard Async Pattern
```
Producer → SQS queue → Lambda (event source mapping)
                │
                ├── Batch size: 10 messages per invocation
                ├── Concurrency: 1 Lambda per shard/partition
                └── On error: messages return to queue, retry
```

**Partial batch failure:** If your function processes 10 messages and fails on #7, report the failed items so only those are retried (not all 10).

## Common Pitfalls
- **Using Lambda for long-running tasks** (>15 min): use ECS/Fargate or Step Functions instead
- **Connecting to RDS directly**: each Lambda invocation opens a new DB connection → pool exhaustion. Use RDS Proxy.
- **Large deployment package**: >50MB slows cold starts. Use Layers for dependencies.
- **No provisioned concurrency for latency-sensitive paths**: cold starts will hit 1-5% of users. Use provisioned concurrency for critical paths.
- **Not setting reserved concurrency on downstream services**: a traffic spike can starve other functions.

## Connections
- `aws-practitioner` — foundational AWS concepts
- `aws-mastery` — API Gateway + Lambda combination patterns
- `serverless-patterns` — higher-level patterns using Lambda
- `scaling` — Lambda auto-scaling and concurrency model
""",
        "questions": [
            {"id": "lam-q1", "type": "mcq", "prompt": "What is a Lambda cold start?", "choices": ["When Lambda runs out of memory", "When a new execution environment must be created (download code, start runtime, run init code)", "When a Lambda function fails", "When Lambda scales down"], "answerIndex": 1, "explanation": "Cold start: AWS creates a new execution environment, downloads your code, starts the runtime, runs initialization code outside the handler. Subsequent invocations reuse the environment (warm start).", "tags": ["cold-start"]},
            {"id": "lam-q2", "type": "mcq", "prompt": "Code outside the Lambda handler function executes:", "choices": ["On every invocation", "Only on cold starts (once per execution environment)", "Never", "Only in production"], "answerIndex": 1, "explanation": "Initialization code (DB connections, SDK clients) runs once per environment. Warm invocations skip it. This is the key optimization: initialize expensive objects outside the handler.", "tags": ["cold-start", "optimization"]},
            {"id": "lam-q3", "type": "mcq", "prompt": "What happens when you increase Lambda memory allocation?", "choices": ["Only memory increases", "Both memory AND CPU increase proportionally — more memory = more vCPU", "Only CPU increases", "Cost decreases"], "answerIndex": 1, "explanation": "Lambda allocates CPU proportional to memory. At 1,769MB you get 1 full vCPU. At 3,008MB you get 2 vCPUs. For CPU-bound functions, increasing memory improves performance.", "tags": ["memory", "performance"]},
            {"id": "lam-q4", "type": "mcq", "prompt": "What is Lambda Reserved Concurrency?", "choices": ["Pre-warmed execution environments", "A guarantee that N executions are always available for one function, preventing it from consuming the entire account limit", "Minimum guaranteed executions per second", "Maximum memory allocation"], "answerIndex": 1, "explanation": "Reserved concurrency reserves N of your account's concurrency for one function. It guarantees availability AND caps maximum concurrency — both useful.", "tags": ["concurrency"]},
            {"id": "lam-q5", "type": "mcq", "prompt": "What is the key difference between Reserved Concurrency and Provisioned Concurrency?", "choices": ["No difference", "Reserved: caps and reserves slots (no cold start prevention). Provisioned: pre-warms environments (eliminates cold starts, costs more).", "Provisioned is cheaper", "Reserved runs code before invocation"], "answerIndex": 1, "explanation": "Reserved concurrency manages slots. Provisioned concurrency pre-warms execution environments so the first request is handled without cold start latency — important for user-facing APIs.", "tags": ["concurrency", "cold-start"]},
            {"id": "lam-q6", "type": "mcq", "prompt": "Lambda maximum timeout is:", "choices": ["30 seconds", "5 minutes", "15 minutes", "1 hour"], "answerIndex": 2, "explanation": "Lambda max timeout is 15 minutes. For longer tasks, use Step Functions (orchestrate multiple Lambdas), ECS Fargate, or AWS Batch.", "tags": ["limits"]},
            {"id": "lam-q7", "type": "mcq", "prompt": "Why should you use RDS Proxy with Lambda connecting to RDS?", "choices": ["RDS Proxy is required for Lambda", "Each Lambda invocation opens a new DB connection; at scale this exhausts RDS connection pool. RDS Proxy pools and reuses connections.", "RDS Proxy makes queries faster", "Lambda can't connect to RDS directly"], "answerIndex": 1, "explanation": "Lambda instances are ephemeral and don't maintain persistent connections. At scale (1000 concurrent Lambdas), you'd have 1000 DB connections. RDS Proxy acts as a connection pool between Lambda and RDS.", "tags": ["rds-proxy", "databases"]},
            {"id": "lam-q8", "type": "mcq", "prompt": "What is a Lambda Layer?", "choices": ["A VPC subnet for Lambda", "A versioned .zip archive containing libraries/code shared across multiple Lambda functions", "Lambda's execution log", "A Lambda event source"], "answerIndex": 1, "explanation": "Layers let you package common dependencies (numpy, requests) separately and attach them to up to 5 Lambda functions. Reduces deployment package size and enables sharing.", "tags": ["layers"]},
            {"id": "lam-q9", "type": "mcq", "prompt": "Lambda invocation concurrency formula is:", "choices": ["Invocations per second only", "Invocations per second × average duration in seconds", "Total invocations / runtime", "Memory × CPU"], "answerIndex": 1, "explanation": "If you have 100 requests/second each taking 500ms, you need 100 × 0.5 = 50 concurrent executions. This determines your required concurrency limit.", "tags": ["concurrency"]},
            {"id": "lam-q10", "type": "mcq", "prompt": "For Lambda triggered by SQS, what happens if the function fails on some messages in a batch?", "choices": ["All messages in the batch are retried", "Only successfully processed messages are deleted; failed ones return to queue", "All messages are deleted", "Function is disabled"], "answerIndex": 1, "explanation": "By default, the entire batch is retried. With partial batch failure reporting, Lambda can delete only the successful messages and return failed ones to the queue for retry.", "tags": ["sqs", "error-handling"]},
            {"id": "lam-q11", "type": "mcq", "prompt": "Which invocation type does API Gateway use with Lambda?", "choices": ["Asynchronous", "Synchronous", "Polling", "Streaming"], "answerIndex": 1, "explanation": "API Gateway invokes Lambda synchronously — it waits for the response to return to the HTTP client. The client gets a 502 if Lambda times out or throws.", "tags": ["api-gateway", "invocation"]},
            {"id": "lam-q12", "type": "mcq", "prompt": "What is a Dead Letter Queue (DLQ) used for in Lambda?", "choices": ["Storing Lambda logs", "Receiving events that Lambda failed to process after all retries", "Storing Lambda deployment packages", "Queuing cold-start requests"], "answerIndex": 1, "explanation": "For async invocations (S3, SNS), Lambda retries twice on failure then sends the event to the DLQ (SQS or SNS). Allows inspection and reprocessing of failed events.", "tags": ["dlq", "error-handling"]},
            {"id": "lam-q13", "type": "mcq", "prompt": "Lambda `/tmp` storage is:", "choices": ["Permanent across all invocations", "Persistent within an execution environment (same Lambda instance), but ephemeral overall — not shared between instances", "Shared across all Lambda instances", "Not available"], "answerIndex": 1, "explanation": "/tmp (512MB-10GB) persists for the lifetime of the execution environment. The same warm instance can reuse /tmp contents across invocations. It's NOT shared between different Lambda instances.", "tags": ["storage", "execution-environment"]},
            {"id": "lam-q14", "type": "multi", "prompt": "Which are valid strategies to reduce Lambda cold start times?", "choices": ["Use Provisioned Concurrency", "Use smaller deployment packages (layers for dependencies)", "Increase timeout", "Use Node.js or Python instead of Java", "Move initialization outside the handler"], "answerIndexes": [0, 1, 3, 4], "explanation": "Provisioned concurrency pre-warms environments. Smaller packages download faster. Node/Python runtimes start faster than JVM. Init outside handler runs once per environment. Timeout doesn't affect cold starts.", "tags": ["cold-start", "optimization"]},
            {"id": "lam-q15", "type": "mcq", "prompt": "Lambda pricing is based on:", "choices": ["Monthly flat fee", "Number of invocations + duration × memory allocated", "CPU usage only", "Number of executions per day"], "answerIndex": 1, "explanation": "Lambda charges for: (1) number of requests ($0.20/million) and (2) duration in GB-seconds (memory × duration). The generous free tier (1M invocations/month) makes it very cheap for low-traffic workloads.", "tags": ["pricing"]},
            {"id": "lam-q16", "type": "mcq", "prompt": "What is Lambda throttling?", "choices": ["Lambda slowing down execution", "Lambda rejecting requests (429) when concurrency limit is reached", "Network timeout", "Memory limit exceeded"], "answerIndex": 1, "explanation": "When Lambda's concurrency limit is hit, new requests get throttled (429). Synchronous callers (API Gateway) get 429 errors. Async callers (SQS) retry automatically.", "tags": ["concurrency", "throttling"]},
            {"id": "lam-q17", "type": "mcq", "prompt": "For a Java Lambda function, what significantly reduces cold start time?", "choices": ["Increasing memory", "Using GraalVM native compilation instead of JVM", "Using multiple layers", "Increasing timeout"], "answerIndex": 1, "explanation": "JVM cold starts take 500ms-2s (classloading, JIT warmup). GraalVM native image compiles to a native binary: ~50ms cold start — comparable to Node/Python. Trade-off: longer compile times, some reflection limitations.", "tags": ["java", "cold-start"]},
            {"id": "lam-q18", "type": "mcq", "prompt": "Lambda Environment Variables are:", "choices": ["Plain text only", "Encrypted at rest using AWS KMS by default", "Not encrypted", "Stored in S3"], "answerIndex": 1, "explanation": "Lambda encrypts environment variables at rest using AWS KMS. You can use the default Lambda service key or a customer-managed CMK for sensitive values.", "tags": ["security", "environment"]},
            {"id": "lam-q19", "type": "codeOutput", "prompt": "Where should you create a DynamoDB client in Lambda for best performance?", "choices": ["Inside the handler function", "Outside the handler at module level (initialized on cold start, reused on warm starts)", "In an environment variable", "In a Lambda Layer"], "answerIndex": 1, "explanation": "Module-level initialization runs once per execution environment. On warm invocations, the same client is reused — avoiding the overhead of creating the client on every request.", "tags": ["optimization", "cold-start"]},
            {"id": "lam-q20", "type": "multi", "prompt": "Which are valid Lambda event sources?", "choices": ["API Gateway", "S3 (object created/deleted)", "DynamoDB Streams", "EC2 instance state changes (via EventBridge)", "RDS query results"], "answerIndexes": [0, 1, 2, 3], "explanation": "Lambda can be triggered by API Gateway, S3, DynamoDB Streams, SQS, SNS, EventBridge, Kinesis, Cognito, and many more. RDS query results are NOT a direct Lambda trigger.", "tags": ["event-sources"]},
        ],
        "flashcards": [
            {"id": "lam-fc1", "front": "Cold start vs warm start", "back": "Cold: new environment (download code + start runtime + init code + handler) — adds 100ms-2s. Warm: same environment reused (only handler runs). Initialize expensive objects OUTSIDE the handler.", "tags": ["cold-start"]},
            {"id": "lam-fc2", "front": "Reserved vs Provisioned Concurrency", "back": "Reserved: caps max concurrent executions (guaranteed slots, prevents starving others). Provisioned: pre-warms N environments (eliminates cold starts, higher cost). Use provisioned for latency-sensitive APIs.", "tags": ["concurrency"]},
            {"id": "lam-fc3", "front": "Lambda + RDS = RDS Proxy", "back": "Lambda can't maintain persistent DB connections. At scale → connection pool exhaustion. RDS Proxy sits between Lambda and RDS, pooling connections. Always use it for RDS + Lambda.", "tags": ["databases"]},
            {"id": "lam-fc4", "front": "Lambda memory ↑ = CPU ↑", "back": "Memory and CPU are proportional. 128MB = tiny CPU. 1,769MB = 1 full vCPU. 3,008MB = 2 vCPUs. For CPU-bound work: increasing memory reduces duration, may reduce cost.", "tags": ["performance"]},
            {"id": "lam-fc5", "front": "SQS + Lambda error handling", "back": "Failed messages return to SQS queue for retry. Use partial batch failure reporting to only retry failed messages. After max retries, SQS sends to a DLQ.", "tags": ["sqs", "error-handling"]},
            {"id": "lam-fc6", "front": "Lambda timeout max + alternatives", "back": "Max 15 minutes. For longer: Step Functions (orchestrate Lambdas), ECS Fargate (container), AWS Batch (batch jobs).", "tags": ["limits"]},
            {"id": "lam-fc7", "front": "Lambda concurrency formula", "back": "Concurrent executions = requests/second × avg duration (seconds). 100 req/s at 500ms = 50 concurrent. Plan your reserved concurrency and account limit around this.", "tags": ["concurrency"]},
            {"id": "lam-fc8", "front": "Lambda Layers purpose", "back": "Package shared dependencies/code separately. Attach up to 5 layers per function. Reduces deployment package size. Enables code sharing across functions. Versioned (immutable).", "tags": ["layers"]},
        ],
        "project": {
            "brief": "Design a serverless image processing pipeline using Lambda. When a user uploads a photo to S3, it triggers: (1) a thumbnail generator Lambda, (2) a metadata extractor Lambda, (3) a DynamoDB write Lambda. The pipeline must handle: large files (50MB), occasional bursts of 1000 uploads/minute, failures in any step, and a tight cost budget. Design the architecture — Lambda configuration (memory/timeout), concurrency settings, error handling, and whether to chain directly or use SQS between steps.",
            "checklist": [
                {"id": "lam-p1", "text": "Choose memory/timeout for each Lambda based on workload characteristics", "weight": 20},
                {"id": "lam-p2", "text": "Design concurrency strategy for burst traffic (1000 uploads/minute)", "weight": 20},
                {"id": "lam-p3", "text": "Design error handling for each step (DLQ, retry policy, partial failure)", "weight": 20},
                {"id": "lam-p4", "text": "Justify whether to chain Lambda directly or use SQS between steps", "weight": 20},
                {"id": "lam-p5", "text": "Identify cold start concerns and mitigation strategy", "weight": 20},
            ],
            "hints": [
                "Thumbnail generation is CPU-bound: 512MB-1GB memory. Metadata extraction is I/O-bound: 256MB sufficient.",
                "1000 uploads/minute = ~17/second. If thumbnailing takes 3 seconds: 17×3 = 51 concurrent executions needed. Set reserved concurrency to 60.",
                "SQS between steps decouples failures: if DynamoDB write fails, it retries independently without re-processing the image.",
                "S3 → Lambda is async (2 retries then DLQ). Use a DLQ (SQS) to capture failed events for inspection.",
            ],
        },
    },
    {
        "id": "aws-vpc-networking",
        "unit": 18,
        "order": 125,
        "title": "AWS VPC & Networking",
        "summary": "Design secure, scalable AWS networks: VPCs, subnets, security groups, NACLs, route tables, NAT Gateway, and VPC peering.",
        "prereqs": ["aws-practitioner"],
        "guide": """# AWS VPC & Networking — Build Your Network in the Cloud

## Mental Model
A VPC (Virtual Private Cloud) is your own isolated network inside AWS. Think of it as renting a section of a datacenter where you control all the networking rules.

```
AWS Region
└── VPC (10.0.0.0/16 — 65,536 IPs)
    ├── Availability Zone A
    │   ├── Public Subnet  (10.0.1.0/24 — 256 IPs)  ← has route to Internet Gateway
    │   └── Private Subnet (10.0.2.0/24 — 256 IPs)  ← no direct internet access
    └── Availability Zone B
        ├── Public Subnet  (10.0.3.0/24)
        └── Private Subnet (10.0.4.0/24)
```

## Key VPC Components

### Subnets
```
Public subnet:  has a route to an Internet Gateway (0.0.0.0/0 → igw-xxx)
                Resources get public IPs, reachable from internet

Private subnet: no direct internet route
                Resources have only private IPs
                Need NAT Gateway to initiate outbound internet connections
```

### Internet Gateway (IGW)
- Allows bidirectional internet traffic for public subnets
- Attached to the VPC, not the subnet

### NAT Gateway
```
Private subnet resource → NAT Gateway (in public subnet) → Internet
                      ↑ outbound only — internet can't initiate connections to private resources
```
NAT Gateway costs money per hour + per GB transferred. Use NAT Instance (EC2) for dev environments to save cost.

### Route Tables
```
Public subnet route table:
  10.0.0.0/16  → local     (all VPC traffic stays internal)
  0.0.0.0/0    → igw-xxx   (everything else goes to internet)

Private subnet route table:
  10.0.0.0/16  → local
  0.0.0.0/0    → nat-xxx   (outbound internet via NAT)
```

## Security Groups vs NACLs

```
Security Group:                      NACL (Network ACL):
─────────────────────────────────    ─────────────────────────────
Stateful (tracks connections)        Stateless (no connection tracking)
Applied at INSTANCE level            Applied at SUBNET level
Allow rules only (no deny)           Allow AND deny rules
Evaluates ALL rules before deciding  Processes rules in number order
Default: deny all in, allow all out  Default: allow all in and out
```

### Security Group example
```
Web server SG:
  Inbound:  TCP 80, 443 from 0.0.0.0/0  (public HTTP/S)
  Inbound:  TCP 22 from 10.0.0.0/16     (SSH from VPC only)
  Outbound: All traffic (default)

DB server SG:
  Inbound:  TCP 5432 from web-server-sg  (only from web servers)
  Outbound: All traffic
```
**Security group chaining:** Reference other SGs as source/destination. The DB SG accepts traffic FROM the web server SG — no IP addresses needed. Scales automatically.

### NACL use case
NACLs are useful for BLOCKING specific IPs (explicit deny):
```
NACL Rule 100: DENY TCP from 1.2.3.4/32 to any port  ← block attacker IP
NACL Rule 200: ALLOW all inbound
```

## VPC Flow Logs
Capture info about IP traffic going to/from network interfaces. Published to CloudWatch Logs or S3.
```
Format: version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes
Usage:  Security auditing, traffic analysis, troubleshooting
```

## VPC Peering — Connect Two VPCs
```
VPC A (10.0.0.0/16) ←→ VPC A-B peering ←→ VPC B (172.16.0.0/16)
```
- No transitive peering: A↔B and B↔C doesn't mean A↔C
- CIDR ranges must not overlap
- Works cross-account and cross-region

## AWS PrivateLink — Service Endpoints
Access AWS services (S3, DynamoDB) without going through the internet:
```
EC2 in private subnet → VPC Endpoint (Gateway type) → S3
                      ↑ traffic stays within AWS network — faster, no NAT Gateway cost
```
Interface endpoints (Powered by PrivateLink): put an ENI in your subnet for services like SSM, Secrets Manager, etc.

## Bastion Host Pattern
```
Developer (internet) → Bastion Host (public subnet, SSH allowed)
                              → Private EC2 (private subnet, SSH from bastion only)
```
The bastion is the only instance with a public IP. Everything else is private.

## Common Patterns

### 3-Tier Architecture
```
Internet → ALB (public subnets, AZ A+B)
               → Web servers (private subnets, AZ A+B)
                    → RDS (private subnets, isolated, AZ A+B)
```
Each tier has its own security group with rules only allowing traffic from the tier above.

### VPN/Direct Connect
```
Corporate network ←→ VPN Gateway (encrypted tunnel over internet) ←→ VPC
Corporate network ←→ Direct Connect (dedicated fiber, 1-10Gbps) ←→ VPC
```

## Common Pitfalls
- **Overlapping CIDR blocks in peered VPCs**: peering fails if CIDRs overlap. Plan IP space early.
- **Missing outbound rules on security groups**: default allows all outbound — explicitly restrict for sensitive instances.
- **Using a single AZ**: design subnets and resources across at least 2 AZs for high availability.
- **Forgetting ephemeral ports in NACLs**: NACLs are stateless. Return traffic uses ephemeral ports (1024-65535) — your NACL must allow outbound 1024-65535.
- **One NAT Gateway for multi-AZ**: if the AZ with your NAT Gateway goes down, all private subnets lose internet access. Use one NAT Gateway per AZ.

## Connections
- `aws-practitioner` — foundational: VPC overview, regions, AZs
- `cloud-fundamentals` — IaaS networking concepts
- `security-fundamentals` — defense in depth, network security layers
- `system-design-fundamentals` — network topology affects system design
""",
        "questions": [
            {"id": "vpc-q1", "type": "mcq", "prompt": "What makes a subnet 'public' in AWS?", "choices": ["It has a public IP assigned to every instance", "It has a route in its route table pointing to an Internet Gateway (0.0.0.0/0 → igw)", "It has less security restrictions", "It's in a specific AWS region"], "answerIndex": 1, "explanation": "A subnet becomes public when its route table has a route for 0.0.0.0/0 pointing to an Internet Gateway. Without this route, instances can't communicate directly with the internet.", "tags": ["vpc", "subnets"]},
            {"id": "vpc-q2", "type": "mcq", "prompt": "What is a NAT Gateway used for?", "choices": ["Allow inbound internet traffic to private subnets", "Allow private subnet instances to initiate outbound internet connections without being directly reachable from the internet", "Connect two VPCs", "Encrypt traffic between AZs"], "answerIndex": 1, "explanation": "NAT Gateway provides outbound-only internet access for private subnet resources. Internet-initiated connections to private instances are not allowed.", "tags": ["nat-gateway", "subnets"]},
            {"id": "vpc-q3", "type": "mcq", "prompt": "Key difference between Security Groups and NACLs?", "choices": ["They are identical", "Security Groups are stateful (track connections), applied per instance. NACLs are stateless, applied per subnet, support deny rules.", "NACLs are applied per instance", "Security Groups support deny rules"], "answerIndex": 1, "explanation": "Stateful SG: return traffic is automatically allowed. Stateless NACL: must explicitly allow return traffic (ephemeral ports). SGs have no deny rules. NACLs process rules in number order.", "tags": ["security-groups", "nacl"]},
            {"id": "vpc-q4", "type": "mcq", "prompt": "What is VPC peering?", "choices": ["Connecting a VPC to the internet", "A private network connection between two VPCs for direct traffic routing", "A VPN tunnel", "AWS PrivateLink"], "answerIndex": 1, "explanation": "VPC peering creates a direct network route between two VPCs (same or different accounts/regions). Traffic uses private IPs. CIDR blocks must not overlap.", "tags": ["vpc-peering"]},
            {"id": "vpc-q5", "type": "mcq", "prompt": "Does VPC peering support transitive routing (A↔B and B↔C means A↔C)?", "choices": ["Yes", "No — transitive routing is not supported. Each pair needs its own peering connection.", "Only in the same region", "Only with Transit Gateway"], "answerIndex": 1, "explanation": "VPC peering is non-transitive. If A peers with B and B peers with C, A cannot reach C. For hub-and-spoke topology, use AWS Transit Gateway.", "tags": ["vpc-peering"]},
            {"id": "vpc-q6", "type": "mcq", "prompt": "What is a VPC Endpoint (Gateway type)?", "choices": ["An EC2 instance acting as a proxy", "A VPC component that allows private access to S3/DynamoDB without internet traffic", "An internet-facing load balancer", "A VPN connection"], "answerIndex": 1, "explanation": "Gateway VPC Endpoints (free) route S3 and DynamoDB traffic within AWS network — no internet, no NAT Gateway, faster and cheaper.", "tags": ["vpc-endpoints"]},
            {"id": "vpc-q7", "type": "mcq", "prompt": "Why should you deploy a NAT Gateway per Availability Zone?", "choices": ["For load balancing", "If the AZ hosting the single NAT Gateway fails, all private subnets in other AZs lose internet access", "NAT Gateways are AZ-specific by design", "To reduce costs"], "answerIndex": 1, "explanation": "A NAT Gateway is AZ-scoped. One per AZ ensures resilience: if AZ-A goes down, private subnets in AZ-B still have internet access via AZ-B's NAT Gateway.", "tags": ["nat-gateway", "high-availability"]},
            {"id": "vpc-q8", "type": "mcq", "prompt": "What is a Bastion Host?", "choices": ["A load balancer", "A hardened EC2 instance in a public subnet used as a secure jump server to SSH into private instances", "An NAT Gateway alternative", "An AWS managed service"], "answerIndex": 1, "explanation": "Bastion host (jump server): only instance with public IP and SSH/RDP access from internet. Used to access private instances. SSH from bastion to private EC2 using the same key.", "tags": ["bastion-host", "security"]},
            {"id": "vpc-q9", "type": "mcq", "prompt": "Security Group source can be:", "choices": ["IP CIDR blocks only", "IP CIDR blocks OR another Security Group ID", "Only public IPs", "DNS names only"], "answerIndex": 1, "explanation": "Referencing another SG as source means 'allow traffic from any instance that has this SG attached'. This is more maintainable than IP ranges — as instances are replaced, the SG reference automatically covers them.", "tags": ["security-groups"]},
            {"id": "vpc-q10", "type": "mcq", "prompt": "What does a NACL rule with action DENY do that a Security Group cannot?", "choices": ["Nothing extra", "Explicitly block specific IPs — Security Groups can only ALLOW traffic (implicit deny for everything else)", "Encrypt traffic", "Log traffic"], "answerIndex": 1, "explanation": "Security Groups have no deny rules — they allow or implicitly deny. NACLs can explicitly deny specific IP ranges, useful for blocking known malicious IPs.", "tags": ["nacl", "security-groups"]},
            {"id": "vpc-q11", "type": "mcq", "prompt": "What is VPC Flow Logs used for?", "choices": ["Encrypting VPC traffic", "Capturing metadata about IP traffic (source, dest, port, packets, bytes) for security analysis and troubleshooting", "Configuring routes", "Load balancing"], "answerIndex": 1, "explanation": "Flow Logs capture network flow metadata (not actual packet data). Published to CloudWatch Logs or S3. Used to analyze traffic patterns, investigate security incidents, troubleshoot connectivity.", "tags": ["flow-logs", "monitoring"]},
            {"id": "vpc-q12", "type": "mcq", "prompt": "A private subnet EC2 instance needs to download packages from the internet. What do you need?", "choices": ["Assign it a public IP", "An Internet Gateway", "A NAT Gateway in a public subnet with a route from the private subnet's route table", "A VPN connection"], "answerIndex": 2, "explanation": "Private subnet → outbound internet: need NAT Gateway in public subnet, and route `0.0.0.0/0 → nat-gateway` in the private subnet's route table.", "tags": ["nat-gateway", "routing"]},
            {"id": "vpc-q13", "type": "mcq", "prompt": "What is AWS Transit Gateway?", "choices": ["A NAT Gateway replacement", "A hub that connects multiple VPCs and on-premises networks with transitive routing support", "A dedicated internet connection", "A VPN service"], "answerIndex": 1, "explanation": "Transit Gateway is a regional router. Attach multiple VPCs (and VPN/Direct Connect) to it. Unlike VPC peering, TGW DOES support transitive routing.", "tags": ["transit-gateway"]},
            {"id": "vpc-q14", "type": "multi", "prompt": "Which are associated with a VPC Subnet (not the VPC itself)?", "choices": ["Route Table association", "NACL association", "Internet Gateway", "Availability Zone placement", "VPC Flow Logs"], "answerIndexes": [0, 1, 3], "explanation": "Subnets have: route table (determines traffic routing), NACL (subnet-level firewall), and must be in an AZ. Internet Gateway and Flow Logs are VPC-level (not subnet-level) by default.", "tags": ["vpc", "subnets"]},
            {"id": "vpc-q15", "type": "mcq", "prompt": "Why is NACL stateless a common trap?", "choices": ["NACLs are actually stateful", "Return traffic uses ephemeral ports (1024-65535). If you allow inbound TCP 443 but forget to allow outbound 1024-65535, responses are blocked.", "NACLs don't track source ports", "NACLs don't support TCP"], "answerIndex": 1, "explanation": "A client connects on port 443 → your server responds from port 443 to the client's ephemeral port (e.g., 54321). Your outbound NACL must allow 1024-65535 for this to work.", "tags": ["nacl", "stateless"]},
            {"id": "vpc-q16", "type": "mcq", "prompt": "What is the 3-tier architecture pattern in AWS VPC?", "choices": ["3 VPCs connected by peering", "Web tier (public ALB) → App tier (private EC2) → Data tier (private RDS), each in different subnets with SGs allowing traffic only from the tier above", "3 availability zones only", "3 regions"], "answerIndex": 1, "explanation": "Classic 3-tier: ALB in public subnets, app servers in private subnets (allowed from ALB SG), RDS in isolated private subnets (allowed from app server SG). Defence in depth.", "tags": ["architecture", "security"]},
            {"id": "vpc-q17", "type": "mcq", "prompt": "What is AWS Direct Connect vs VPN?", "choices": ["They are the same", "Direct Connect: dedicated fiber link (1-10 Gbps, consistent latency, higher cost). VPN: encrypted tunnel over public internet (lower cost, higher latency, jitter).", "VPN uses fiber", "Direct Connect uses the internet"], "answerIndex": 1, "explanation": "Direct Connect: physical fiber from your datacenter to AWS — predictable bandwidth and latency. VPN: encrypted IPsec tunnel over internet — cheaper but variable performance.", "tags": ["direct-connect", "vpn"]},
            {"id": "vpc-q18", "type": "mcq", "prompt": "What is an Elastic Network Interface (ENI)?", "choices": ["A physical network card", "A virtual network interface attachable to EC2 instances — has a private IP, optional public IP, security groups, and MAC address", "A DNS entry", "A load balancer"], "answerIndex": 1, "explanation": "An ENI is a virtual NIC. You can attach multiple ENIs to an EC2 instance (for multiple IPs/SGs). ENIs can be moved between instances, preserving IP and MAC — useful for failover.", "tags": ["eni", "networking"]},
            {"id": "vpc-q19", "type": "mcq", "prompt": "Can two VPCs with overlapping CIDR blocks be peered?", "choices": ["Yes", "No — overlapping CIDRs cause routing ambiguity and peering will fail", "Yes, with a NAT Gateway between them", "Yes, if they are in different regions"], "answerIndex": 1, "explanation": "VPC peering requires non-overlapping CIDR blocks. Plan your IP addressing scheme from the start across all VPCs and on-premises networks to avoid this.", "tags": ["vpc-peering", "cidr"]},
            {"id": "vpc-q20", "type": "multi", "prompt": "Which statements about Security Groups are true?", "choices": ["Stateful — return traffic is automatically allowed", "Applied at the instance/ENI level", "Support both allow and deny rules", "Multiple SGs can be attached to one instance", "Rules are evaluated in number order"], "answerIndexes": [0, 1, 3], "explanation": "SGs are stateful (0 true), instance-level (1 true), support only allow rules (2 false — NACLs do deny), multiple SGs allowed per instance (3 true), all rules evaluated at once — no ordering (4 false).", "tags": ["security-groups"]},
        ],
        "flashcards": [
            {"id": "vpc-fc1", "front": "Public vs Private subnet", "back": "Public: route table has 0.0.0.0/0 → Internet Gateway. Resources can have public IPs. Private: no IGW route. Outbound internet via NAT Gateway only.", "tags": ["subnets"]},
            {"id": "vpc-fc2", "front": "Security Group vs NACL — stateful vs stateless", "back": "SG: stateful (return traffic auto-allowed), instance-level, allow only. NACL: stateless (must allow return traffic explicitly), subnet-level, allow + deny.", "tags": ["security-groups", "nacl"]},
            {"id": "vpc-fc3", "front": "NAT Gateway HA rule", "back": "One NAT Gateway per AZ. If a single NAT Gateway's AZ goes down, all private subnets in other AZs lose internet. One per AZ = fully resilient.", "tags": ["nat-gateway"]},
            {"id": "vpc-fc4", "front": "VPC Peering limitation", "back": "Non-transitive. A↔B and B↔C does NOT mean A↔C. No overlapping CIDRs. Use AWS Transit Gateway for hub-and-spoke with transitive routing.", "tags": ["vpc-peering"]},
            {"id": "vpc-fc5", "front": "SG chaining pattern", "back": "DB SG: `allow from web-sg` (reference by SG ID). When web servers are replaced, new instances automatically match. Scales better than CIDR-based rules.", "tags": ["security-groups"]},
            {"id": "vpc-fc6", "front": "NACL ephemeral port trap", "back": "NACLs are stateless. Allow inbound 443 but ALSO allow outbound 1024-65535 (ephemeral ports). Otherwise responses from your servers are blocked.", "tags": ["nacl"]},
            {"id": "vpc-fc7", "front": "VPC Endpoint (Gateway) benefit", "back": "Access S3/DynamoDB without internet. Traffic stays in AWS network. Free for gateway type. No NAT Gateway needed = cost saving. Add to route table as managed prefix list.", "tags": ["vpc-endpoints"]},
            {"id": "vpc-fc8", "front": "3-tier VPC architecture", "back": "ALB (public subnets) → App EC2 (private, allowed from ALB SG) → RDS (private isolated, allowed from App SG). Each tier has its own SG allowing only the tier above.", "tags": ["architecture"]},
        ],
        "project": {
            "brief": "Design the VPC architecture for a production web application. Requirements: web tier accessible from internet, app tier with business logic (no direct internet access), database tier (highly sensitive, zero internet access), CI/CD pipeline needs to pull from npm/pip during builds, and compliance requires logging all network traffic. Design: CIDR plan for the VPC and subnets, security group rules for each tier, NAT Gateway strategy, flow logs configuration, and how the CI/CD runner accesses the internet. Use 2 AZs for HA.",
            "checklist": [
                {"id": "vpc-p1", "text": "Design VPC CIDR and 6+ subnets (2 public, 2 private app, 2 private DB, 2 AZs)", "weight": 20},
                {"id": "vpc-p2", "text": "Define Security Group rules for ALB, App servers, and RDS", "weight": 20},
                {"id": "vpc-p3", "text": "Configure NAT Gateway strategy for HA (how many, where)", "weight": 20},
                {"id": "vpc-p4", "text": "Configure VPC Flow Logs (destination, what to capture)", "weight": 20},
                {"id": "vpc-p5", "text": "Justify whether to use a VPC Endpoint for S3/ECR access in CI/CD runners", "weight": 20},
            ],
            "hints": [
                "CIDR: VPC 10.0.0.0/16. Public: /24 each. Private app: /22 (more IPs for scaling). Private DB: /24.",
                "ALB SG: allow 80/443 from 0.0.0.0/0. App SG: allow 8080 from ALB SG. RDS SG: allow 5432 from App SG only.",
                "2 NAT Gateways (one per AZ). Private subnets route to their AZ's NAT. ~$64/month each — weigh against HA requirement.",
                "VPC Endpoint for S3/ECR eliminates NAT Gateway data transfer costs and keeps traffic in AWS network. Essential for CI/CD pulling large container images.",
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
    print(f"  WROTE {path.name} ({len(topic.get('questions', []))}q, {len(topic.get('flashcards', []))}fc)")


if __name__ == "__main__":
    overwrite = "--overwrite" in sys.argv
    print(f"Writing AWS batch 1 → {OUT}/")
    for t in TOPICS:
        write_topic(t, overwrite)
    print("Done.")

