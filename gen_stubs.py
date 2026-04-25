import json, os, sys

stubs = [
  ("relational-databases", 1, 3, "Relational Databases and SQL", "Master SQL, ACID properties, indexes, joins, and query optimization.", ["git-fundamentals"]),
  ("embedded-databases", 1, 4, "Embedded Databases", "SQLite and RocksDB: when to embed a database directly in your app.", ["relational-databases"]),
  ("neural-nets", 2, 6, "Neural Nets and Backprop", "Understand neurons, layers, activation functions, and backpropagation.", ["ml-basics"]),
  ("transformers", 2, 7, "Transformers", "Attention mechanisms, self-attention, and the architecture behind all modern LLMs.", ["neural-nets"]),
  ("llms", 2, 8, "LLMs", "How large language models generate text, tokenization, context windows, and limits.", ["transformers"]),
  ("prompting-fundamentals", 2, 9, "Prompting Fundamentals", "Prompt engineering techniques: zero-shot, few-shot, chain-of-thought, and structured outputs.", ["llms"]),
  ("firewalls", 3, 10, "Firewalls", "Stateful vs stateless firewalls, rules, DMZ, and network security fundamentals.", ["prompting-fundamentals"]),
  ("ftp", 3, 11, "FTP", "File Transfer Protocol: active vs passive mode, security issues, and SFTP/FTPS alternatives.", ["firewalls"]),
  ("proxies", 3, 12, "Proxies", "Forward and reverse proxies, use cases, and how nginx acts as a reverse proxy.", ["ftp"]),
  ("rpc", 3, 13, "RPC and gRPC", "Remote Procedure Calls, Protocol Buffers, and when gRPC beats REST.", ["proxies"]),
  ("websockets", 3, 14, "WebSockets", "Full-duplex communication, handshake, use cases vs HTTP, and real-time app patterns.", ["rpc"]),
  ("long-polling", 3, 15, "Long and Short Polling", "Long polling vs short polling vs SSE vs WebSockets: choosing the right real-time strategy.", ["websockets"]),
  ("rate-limiting", 3, 16, "Rate Limiting", "Token bucket, leaky bucket, fixed/sliding window algorithms and when to use each.", ["long-polling"]),
  ("qps-capacity", 3, 17, "QPS and Capacity Planning", "Queries per second, throughput vs latency, back-of-napkin capacity math for system design.", ["rate-limiting"]),
  ("load-balancing", 3, 18, "Load Balancing", "L4 vs L7, round-robin, least-connections, consistent hashing, health checks.", ["qps-capacity"]),
  ("caching", 4, 19, "Caching", "LRU, write-through/back, CDN, cache invalidation: the hardest problem in CS.", ["load-balancing"]),
  ("sharding", 4, 20, "Sharding", "Horizontal partitioning of databases: hash sharding, range sharding, and hotspot avoidance.", ["caching"]),
  ("partitioning", 4, 21, "Partitioning", "Partitioning vs sharding: table partitioning, time-based partitioning, and query performance.", ["sharding"]),
  ("kafka", 4, 22, "Kafka", "Distributed event streaming: topics, partitions, consumer groups, offset, and at-least-once delivery.", ["partitioning"]),
  ("rabbitmq", 4, 23, "RabbitMQ", "AMQP message broker: exchanges, queues, bindings, routing keys, and message acknowledgement.", ["kafka"]),
  ("aws-sqs", 4, 24, "AWS SQS", "AWS Simple Queue Service: standard vs FIFO queues, visibility timeout, DLQ, and Lambda triggers.", ["rabbitmq"]),
  ("cloud-fundamentals", 5, 25, "Cloud Fundamentals", "IaaS/PaaS/SaaS, regions, availability zones, shared responsibility model.", ["aws-sqs"]),
  ("docker", 5, 26, "Docker", "Containers, images, Dockerfile, layers, networking, volumes, and docker-compose.", ["cloud-fundamentals"]),
  ("kubernetes", 5, 27, "Kubernetes", "Pods, deployments, services, ingress, HPA, namespaces, and kubectl essentials.", ["docker"]),
  ("aws-practitioner", 5, 28, "AWS Practitioner", "Core AWS concepts: EC2, VPC, IAM, RDS, DynamoDB, S3. Mental models, no console walkthroughs.", ["kubernetes"]),
  ("aws-mastery", 5, 29, "AWS Mastery", "Lambda, API Gateway, CloudFormation, CDK. Serverless architecture design exercises.", ["aws-practitioner"]),
  ("serverless-patterns", 5, 30, "Serverless Patterns", "Event-driven architecture, fan-out, saga pattern, cold starts, and cost vs speed tradeoffs.", ["aws-mastery"]),
  ("cicd-pipelines", 5, 31, "CI/CD Pipelines", "Continuous integration and delivery: pipeline stages, testing gates, blue/green and canary deployments.", ["serverless-patterns"]),
  ("error-logging", 5, 32, "Error Logging and Observability", "Structured logging, distributed tracing, metrics, alerts, and the three pillars of observability.", ["cicd-pipelines"]),
  ("agents", 6, 33, "AI Agents", "Tool-use, planning loops, ReAct pattern, multi-agent systems, and agentic failure modes.", ["error-logging"]),
  ("rag", 6, 34, "RAG", "Retrieval-Augmented Generation: embeddings, vector databases, chunking strategies, and relevance.", ["agents"]),
  ("fine-tuning", 6, 35, "Fine-Tuning", "LoRA, SFT, RLHF: when and how to fine-tune vs prompt-engineer, cost tradeoffs.", ["rag"]),
  ("leverage-strategies", 6, 36, "Leverage Strategies", "Max output, minimum energy: AI tools, automation, and mental models to 10x your output.", ["fine-tuning"]),
  ("pycharm", 7, 37, "PyCharm Power-Use", "Debugger, inspections, refactoring, virtual envs, remote interpreters, and productivity shortcuts.", ["leverage-strategies"]),
]

out_dir = os.path.dirname(os.path.abspath(__file__))

for (sid, unit, order, title, summary, prereqs) in stubs:
    fname = os.path.join(out_dir, sid + ".json")
    if not os.path.exists(fname):
        data = {
            "id": sid,
            "unit": unit,
            "order": order,
            "title": title,
            "summary": summary,
            "prereqs": prereqs,
            "guide": "<!-- TODO: author full guide for {} -->".format(title),
            "questions": [],
            "flashcards": [],
            "project": {
                "brief": "TODO: author project brief for {}".format(title),
                "checklist": [],
                "hints": []
            }
        }
        with open(fname, "w") as f:
            json.dump(data, f, indent=2)
        print("Created " + sid + ".json")
    else:
        print("Skipped " + sid + ".json (exists)")

