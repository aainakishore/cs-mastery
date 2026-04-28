"""
patch_networking_1.py — kafka.json, rabbitmq.json, rpc.json
Run: python3 scripts/patch_networking_1.py
"""
import json
from pathlib import Path

BASE = Path(__file__).parent.parent / 'src/content/topics/networking'

# ─────────────────────────────────────────────────────────────────────────────
# KAFKA
# ─────────────────────────────────────────────────────────────────────────────
p = BASE / 'kafka.json'
d = json.loads(p.read_text())

KAFKA_GUIDE = """# Apache Kafka

## What Is Kafka? The Problem It Solves

Imagine an e-commerce platform. When a user places an order, ten things need to happen:
send confirmation email, update inventory, notify the warehouse, charge the card,
update loyalty points, trigger analytics, start fraud check, update the user dashboard,
notify the shipping service, and update the recommendation engine.

**Option A — Direct calls (synchronous):**
```
Order Service calls all 10 services one by one.
Problems:
  - Slow: must wait for each to finish (sequential or complex parallel code)
  - Brittle: if Email Service is down, the ENTIRE ORDER FAILS
  - Tight coupling: Order Service must know about all 10 services
  - Scaling: each service must scale with Order Service traffic
```

**Option B — Kafka (event streaming):**
```
Order Service publishes ONE event: OrderPlaced -> Kafka topic
Done. Returns to user instantly.

All 10 services independently subscribe to the topic.
Each reads at its own pace. Email Service is down? It catches up when it recovers.
New 11th service (analytics v2)? Just subscribe — no changes to Order Service.
```

Kafka is a **distributed event streaming platform**. Think of it as a
massively scalable, durable, replayable message log that services can publish
to and consume from independently.

---

## Core Concepts

```
TOPIC:
  A named category/feed of events.
  "orders", "user-signups", "payments", "page-views"
  Events are published TO topics.
  Consumers subscribe to topics.

PARTITION:
  Topics are split into partitions for parallelism.
  Topic "orders" might have 12 partitions.
  Events in one partition are ORDERED (older events first).
  Across partitions: no ordering guarantee.

  Topic: orders
  ┌─────────────────────────────────────┐
  │ Partition 0: [e1] [e5] [e9]  [e13] │ ← events appended, never deleted early
  │ Partition 1: [e2] [e6] [e10] [e14] │
  │ Partition 2: [e3] [e7] [e11] [e15] │
  │ Partition 3: [e4] [e8] [e12] [e16] │
  └─────────────────────────────────────┘

OFFSET:
  A sequential integer ID for each event within a partition.
  Partition 0: offset 0 = first event, offset 1 = second, etc.
  Consumers track their offset: "I've processed up to offset 47 in partition 0".
  This enables: replay (go back to offset 0), pause/resume, exactly-once delivery.

BROKER:
  A Kafka server that stores partitions and serves producers/consumers.
  A Kafka cluster has 3-9+ brokers for HA and throughput.

PRODUCER:
  Client that publishes events to a topic.
  Decides which partition to write to: round-robin, by key hash, or custom.

CONSUMER:
  Client that reads events from a topic.

CONSUMER GROUP:
  Multiple consumers coordinated to read a topic together.
  Each partition is assigned to exactly one consumer in the group.
  Adding consumers = parallel processing (up to one per partition).
```

---

## The Key Insight: Consumer Groups Enable Fan-Out

```
Multiple consumer groups can independently read the SAME topic.
Each group gets ALL messages, independently of other groups.

Topic: orders (4 partitions, 1000 msg/sec)
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
Consumer Group A  Group B   Group C
(Email Service)  (Analytics) (Inventory)
  [C1][C2]         [C1]       [C1][C2][C3]
    Reads all       Reads all    Reads all
    messages        messages     messages
  Offset: 500     Offset: 800  Offset: 300
  (email is fast) (analytics  (inventory
                   is fast)    needs catch-up)

Each group tracks its own offset.
Slow group (Inventory at offset 300) doesn't affect other groups.
If Inventory crashes: it restarts at offset 300 and resumes.
```

This is what makes Kafka fundamentally different from SQS:
- SQS: message consumed = deleted forever, one consumer group
- Kafka: message retained (configurable days/weeks), multiple groups read independently

---

## Kafka vs SQS vs RabbitMQ

```
+------------------+-------------------+------------------+--------------------+
| Feature          | Kafka             | SQS              | RabbitMQ           |
+------------------+-------------------+------------------+--------------------+
| Model            | Event log (stream)| Work queue       | Message broker     |
| Message retention| Days/weeks/forever| Max 14 days      | Until consumed     |
| Replay           | Yes (any offset)  | No               | No                 |
| Consumer groups  | Multiple independent| One group       | Multiple queues   |
| Throughput       | Millions msg/sec  | Unlimited API    | ~50K msg/sec       |
| Ordering         | Per partition     | FIFO only in $.fifo| Per queue       |
| Ops complexity   | High (cluster)    | Zero (managed)   | Medium             |
| Use case         | Event streaming   | Task queues      | Complex routing    |
+------------------+-------------------+------------------+--------------------+

USE KAFKA WHEN:
  Multiple services need to react to the same events (fan-out)
  You need event replay (audit, reprocessing, new service catch-up)
  High-throughput streaming (millions of events/second)
  Event sourcing architecture
  Real-time analytics pipelines (Kafka -> Spark/Flink -> dashboard)

USE SQS WHEN:
  Simple task queue (send email, process payment)
  Don't need replay
  Don't want to manage infrastructure (SQS is fully managed)

USE RABBITMQ WHEN:
  Complex message routing (exchanges with patterns)
  Traditional message broker patterns (request-reply, pub-sub)
  Existing AMQP ecosystem
```

---

## Kafka Retention — Events Stay Around

```
Kafka KEEPS events by default. They are not deleted when consumed.

Retention policy options:
  Time-based:  delete events older than 7 days (default)
  Size-based:  delete oldest events when topic exceeds 50GB
  Compacted:   keep only the LATEST event per key (for state tables)

Example: user-profiles topic with compaction
  Event 1: key=user123  value={name: Alice, email: a@b.com}
  Event 2: key=user456  value={name: Bob, ...}
  Event 3: key=user123  value={name: Alice, email: newemail@b.com}  <- update
  After compaction: only event 3 for user123 (latest) is kept.
  Event 1 is deleted (superseded by event 3).

This is why Kafka can serve as a source of truth for state:
  New service joins -> reads compacted topic -> gets current state of all users.
  Full database snapshot via Kafka!

REPLAY USE CASE:
  Analytics service crashes, restores from backup at offset 0.
  Replays all events from day 1.
  Gets back to current state without any data loss.
```

---

## Kafka Architecture — Cluster and Replication

```
CLUSTER SETUP (3 brokers minimum for HA):

  Broker 1          Broker 2          Broker 3
  ┌──────────┐      ┌──────────┐      ┌──────────┐
  │ P0 Leader│      │ P1 Leader│      │ P2 Leader│
  │ P1 Replica      │ P2 Replica      │ P0 Replica
  │ P2 Replica      │ P0 Replica      │ P1 Replica
  └──────────┘      └──────────┘      └──────────┘

Each partition has ONE leader and N replicas.
All reads/writes go to the leader.
Replicas stay in sync (In-Sync Replicas = ISR).

REPLICATION FACTOR:
  replication.factor=3: partition copied to 3 brokers.
  Broker 1 dies: Broker 2 or 3 has a complete replica. Automatic leader election.
  No data loss. Consumers/producers reconnect to new leader automatically.

ZOOKEEPER (OLD) vs KRaft (NEW):
  Old: Kafka required ZooKeeper for cluster coordination (separate process).
  New (Kafka 3.x+): KRaft mode — Kafka manages its own metadata.
  KRaft simplifies operations significantly. New clusters: use KRaft.
```

---

## Producer Configuration — Delivery Guarantees

```
acks SETTING (how many brokers must acknowledge before "success"):

  acks=0:  Fire and forget. No confirmation. Fastest. May lose messages.
  acks=1:  Leader must confirm. Default. Leader crash before replica sync = message lost.
  acks=all: All in-sync replicas must confirm. Slowest. No data loss.
           Combine with min.insync.replicas=2 for true durability.

IDEMPOTENT PRODUCER:
  enable.idempotence=true
  If network error causes retry, Kafka deduplicates on the broker side.
  Prevents duplicate messages from producer retries.
  Required for exactly-once semantics.

EXACTLY-ONCE SEMANTICS (EOS):
  Combine: idempotent producer + Kafka transactions.
  atomically: produce to topic A AND commit consumer offset together.
  Use for: financial events where duplicates cause business problems.

COMPRESSION:
  lz4 or snappy compression on producer reduces network I/O 3-5x.
  Critical for high-volume topics. Near-zero CPU overhead.
```

---

## Consumer Configuration

```
AUTO OFFSET COMMIT (dangerous default):
  enable.auto.commit=true  <- commits offset every 5 seconds automatically
  Problem: commit happens BEFORE processing completes.
  If consumer crashes after commit but before processing: event is LOST.

  SAFE PATTERN: disable auto-commit, manually commit AFTER processing:
    consumer.poll() -> process records -> consumer.commitSync()

CONSUMER LAG:
  consumer lag = latest_offset - consumer_current_offset
  If lag is growing: consumers are falling behind production rate.
  Alert on lag > threshold (depend on your SLA).
  Fix: add more consumers (up to partition count), or increase throughput.

REBALANCING:
  When consumer joins or leaves a group, Kafka reassigns partitions.
  During rebalance: ALL consumers stop processing ("stop the world").
  Minimize rebalances: tune session.timeout.ms and heartbeat.interval.ms.
  Kafka 3.x: cooperative incremental rebalancing (less disruptive).
```

---

## Real-World Kafka Patterns

```
EVENT SOURCING:
  Every change is an event. Events stored in Kafka forever.
  State = replay of all events from beginning.
  Database becomes a cache/view of the event log.

CQRS + KAFKA:
  Command side: write events to Kafka.
  Query side: service consumes events, builds optimised read model.
  Read and write models independently scalable.

KAFKA STREAMS / KSQLDB:
  Stream processing ON Kafka without external system.
  count orders per minute, join streams, aggregate.
  Example: real-time fraud detection on transaction stream.

CHANGE DATA CAPTURE (CDC):
  Debezium connector reads MySQL/PostgreSQL WAL.
  Every database INSERT/UPDATE/DELETE -> Kafka event.
  Other services react to DB changes without polling.
  "Database as source of truth, Kafka as event bus" pattern.
```

---

## Mind Map

```
KAFKA
|
+-- CORE CONCEPTS
|   +-- Topic (named event channel)
|   +-- Partition (ordered log, parallelism unit)
|   +-- Offset (position in partition, enables replay)
|   +-- Consumer Group (parallel consumption)
|   +-- Broker (server, stores partitions)
|
+-- KEY FEATURE: RETENTION + REPLAY
|   +-- Events stay on disk (days/weeks)
|   +-- Multiple groups read same topic independently
|   +-- New service: replay from offset 0
|
+-- DELIVERY GUARANTEES
|   +-- acks=0 (fire-forget), acks=1 (leader), acks=all (durable)
|   +-- Idempotent producer (dedup retries)
|   +-- Exactly-once (transactions)
|
+-- OPERATIONS
|   +-- Consumer lag monitoring
|   +-- Replication factor (3 recommended)
|   +-- Compaction (keep latest per key)
|
+-- PATTERNS
    +-- Fan-out (multiple consumer groups)
    +-- Event sourcing
    +-- CDC (Debezium)
    +-- CQRS
```

---

## References and Further Learning

### Videos (Watch These!)
- **Apache Kafka in 6 Minutes** by ByteByteGo:
  https://www.youtube.com/watch?v=Ch5VhJzaoaI
  - Fast, visual Kafka concepts overview.
- **Kafka Tutorial for Beginners** by TechWorld with Nana:
  https://www.youtube.com/watch?v=SqVfCyfCJqw
  - 1 hour. Complete Kafka walkthrough with Docker demo.

### Free Books and Articles
- **Kafka official documentation**: https://kafka.apache.org/documentation/
- **Kafka: The Definitive Guide** (free PDF from Confluent): https://www.confluent.io/resources/kafka-the-definitive-guide/

### Practice
- **Confluent Cloud free tier**: https://confluent.io — managed Kafka, free tier
- **Kafka with Docker Compose**: many tutorials showing full local cluster setup
"""

KAFKA_Q = [
    {"id":"kafka-q4","type":"mcq","prompt":"What does a Kafka partition provide?",
     "choices":["Encryption of messages","Ordered, append-only event log enabling parallelism — a topic's messages are split across partitions, each processed by one consumer in a group",
                "Authentication for consumers","Compression of messages"],
     "answerIndex":1,"explanation":"Partitions are the unit of parallelism. Events within a partition are strictly ordered by offset. A topic with 12 partitions can be consumed by up to 12 parallel consumers. More partitions = higher throughput (but more overhead).","tags":["kafka","partitions"]},
    {"id":"kafka-q5","type":"mcq","prompt":"What is a Kafka offset?",
     "choices":["The delay before a message is delivered","A sequential integer ID for each message within a partition — consumers track their current offset to know what they've processed and to enable replay",
                "The number of partitions","Message priority level"],
     "answerIndex":1,"explanation":"Kafka offset = position in a partition log. Consumer group tracks offset per partition: 'I've read up to offset 500 in partition 2'. To replay: reset offset to 0. To skip old data: seek to latest. Offsets enable exactly-once, at-least-once, at-most-once delivery semantics.","tags":["kafka","offset","replay"]},
    {"id":"kafka-q6","type":"mcq","prompt":"How does Kafka differ from SQS in terms of message consumption?",
     "choices":["Kafka is slower","SQS: message consumed = deleted. Kafka: message retained for days/weeks, multiple independent consumer groups ALL read the same messages",
                "They are identical","Kafka deletes faster"],
     "answerIndex":1,"explanation":"SQS message deleted = gone (one consumer group 'wins' it). Kafka: message stays. Consumer Group A (email) and Group B (analytics) BOTH read the same OrderPlaced event independently. Each tracks its own offset. Fan-out built in.","tags":["kafka","sqs","comparison"]},
    {"id":"kafka-q7","type":"mcq","prompt":"What happens when consumer lag grows on a Kafka consumer group?",
     "choices":["Messages are deleted faster","The consumer group is falling behind production rate — add more consumers (up to partition count) or optimize processing speed",
                "Kafka automatically slows producers","Offsets are reset"],
     "answerIndex":1,"explanation":"Consumer lag = latest_offset - consumer_offset. Growing lag = consumers can't keep up. Fix: add consumers (max = partition count), reduce processing time per message, or increase partitions (allows more consumers). Alert on lag > SLA threshold.","tags":["kafka","consumer-lag","operations"]},
    {"id":"kafka-q8","type":"mcq","prompt":"What does Kafka's `acks=all` producer setting guarantee?",
     "choices":["Message delivered to consumer","All in-sync replicas (ISR) have acknowledged the message — no data loss even if the leader broker crashes immediately after",
                "Consumer has processed the message","Message is compressed"],
     "answerIndex":1,"explanation":"acks=all (or acks=-1): message written to leader AND all in-sync replicas before producer considers it sent. Combine with min.insync.replicas=2: even if leader dies, at least one replica has the message. Required for financial/critical data streams.","tags":["kafka","acks","durability"]},
    {"id":"kafka-q9","type":"mcq","prompt":"What is log compaction in Kafka?",
     "choices":["Gzip compression of the log","Kafka retains only the most recent message per key — older messages with the same key are deleted, creating a current-state snapshot from the event log",
                "Deleting all old messages","Merging multiple partitions"],
     "answerIndex":1,"explanation":"Compacted topic: user123 event appears 5 times (profile updates). After compaction: only latest event for user123 exists. Use for: state tables, lookup data, change streams. New consumer reads compacted topic = gets current state of all keys. Like a DB table as a Kafka topic.","tags":["kafka","compaction","state"]},
    {"id":"kafka-q10","type":"mcq","prompt":"Why is `enable.auto.commit=true` dangerous in Kafka consumers?",
     "choices":["It is always safe","Auto-commit fires every 5 seconds regardless of processing state — if consumer commits offset BEFORE finishing processing, a crash causes that message to be skipped permanently",
                "It commits too slowly","It prevents consumer groups"],
     "answerIndex":1,"explanation":"Auto-commit: Kafka commits your offset at intervals. If commit fires, then consumer crashes mid-processing: message was 'committed' but not processed. Restart: starts from AFTER that offset. Message lost. Safe pattern: disable auto-commit, manually commitSync() AFTER successful processing.","tags":["kafka","consumer","offset-commit"]},
    {"id":"kafka-q11","type":"mcq","prompt":"What is Change Data Capture (CDC) with Kafka and Debezium?",
     "choices":["A Kafka security feature","Debezium reads the database WAL (write-ahead log), converts every INSERT/UPDATE/DELETE into a Kafka event — services react to DB changes without polling",
                "A Kafka backup mechanism","Kafka database storage"],
     "answerIndex":1,"explanation":"CDC: Debezium connector tails the DB WAL (PostgreSQL, MySQL). Every change -> Kafka event. Downstream services subscribe and react. Example: orders table update -> Kafka event -> inventory service, analytics, search index all update. No polling, no DB load from consumers.","tags":["kafka","cdc","debezium"]},
    {"id":"kafka-q12","type":"mcq","prompt":"In Kafka, what determines which partition a message goes to?",
     "choices":["Kafka always uses round-robin","If message has a key: hash(key) % partitions (same key always same partition = ordered). If no key: round-robin across partitions",
                "Consumer chooses partition","Partition with most space"],
     "answerIndex":1,"explanation":"Key-based routing: all events for userId=123 always go to partition 3 (hash deterministic). Guarantees ordering per user. No key: distributed round-robin (max throughput, no ordering). Choose key when ordering matters for a specific entity (user, order ID).","tags":["kafka","partitions","routing"]},
    {"id":"kafka-q13","type":"mcq","prompt":"What is the maximum number of consumers that can read a Kafka topic in parallel within one consumer group?",
     "choices":["Unlimited","Equal to the number of partitions — each partition assigned to exactly one consumer; consumers > partitions means idle consumers",
                "Always 1","10 consumers maximum"],
     "answerIndex":1,"explanation":"Partitions = max parallelism. Topic with 12 partitions: 12 consumers in a group each get 1 partition. 13th consumer is idle (no partition). Want more parallel consumers? Add partitions. Design topics with enough partitions for peak consumer count.","tags":["kafka","consumer-groups","parallelism"]},
    {"id":"kafka-q14","type":"mcq","prompt":"What is Event Sourcing with Kafka?",
     "choices":["Using Kafka as a cache","Every state change is stored as an immutable event in Kafka. Current state = replay of all events. Kafka becomes the source of truth.",
                "Kafka used for monitoring","Kafka replacing databases entirely"],
     "answerIndex":1,"explanation":"Event sourcing: UserCreated, EmailUpdated, PhoneVerified events stored in Kafka forever. User profile = reducing all user events. New service: replay from offset 0 to build its view. Audit trail built-in. Enables time-travel debugging. Complex to implement but powerful.","tags":["kafka","event-sourcing","pattern"]},
    {"id":"kafka-q15","type":"mcq","prompt":"What is Kafka's replication factor and why use 3?",
     "choices":["Number of topics","Number of copies of each partition across brokers — factor=3 means partition on 3 brokers, can lose 2 brokers and not lose data",
                "Number of consumer groups","Consumer thread count"],
     "answerIndex":1,"explanation":"Replication factor 3: partition on broker 1 (leader) + broker 2 (replica) + broker 3 (replica). Broker 1 dies: broker 2 elected leader, no data loss. Broker 2 also dies: broker 3 takes over. Only all 3 failing simultaneously causes data loss. Production minimum: factor=3.","tags":["kafka","replication","ha"]},
    {"id":"kafka-q16","type":"mcq","prompt":"What is Kafka Streams?",
     "choices":["Kafka's network protocol","A client library for stream processing directly on Kafka — stateful transformations, aggregations, joins of Kafka topics without external systems",
                "A UI for Kafka","Kafka's consumer group balancer"],
     "answerIndex":1,"explanation":"Kafka Streams: process events inside your application using a DSL. Count events per minute, join OrderPlaced + PaymentCompleted streams. All state stored in Kafka (or RocksDB locally). No separate Spark/Flink cluster needed for moderate complexity. For complex analytics: Flink or Spark Structured Streaming.","tags":["kafka","kafka-streams","stream-processing"]},
    {"id":"kafka-q17","type":"mcq","prompt":"What is CQRS (Command Query Responsibility Segregation) with Kafka?",
     "choices":["A Kafka CLI command","Separate write model (commands -> Kafka events) from read model (consumer builds optimised query view) — each side independently scalable",
                "A Kafka security pattern","A partitioning strategy"],
     "answerIndex":1,"explanation":"CQRS+Kafka: OrderService writes OrderPlaced event. OrderReadService consumes and builds a denormalised orders table optimised for queries. Write side: optimised for append. Read side: optimised for queries. Scale independently. Trade-off: eventual consistency between write and read models.","tags":["kafka","cqrs","pattern"]},
    {"id":"kafka-q18","type":"mcq","prompt":"What does the idempotent producer setting `enable.idempotence=true` do?",
     "choices":["Compresses messages","Makes the producer assign unique sequence numbers — Kafka broker deduplicates retried messages, preventing duplicates from network errors",
                "Enables consumer group coordination","Increases throughput"],
     "answerIndex":1,"explanation":"Without idempotence: network error + retry = duplicate message on broker. With idempotence: producer assigns (PID, sequence). Broker rejects duplicate sequence. You get exactly-once writes from producer perspective. Required for exactly-once end-to-end (combine with transactions for consumer offset commit).","tags":["kafka","idempotence","exactly-once"]},
    {"id":"kafka-q19","type":"mcq","prompt":"What is a Kafka consumer group rebalance and why should you minimize them?",
     "choices":["A rolling upgrade of brokers","When consumers join/leave a group, Kafka reassigns partitions — during rebalance ALL consumers pause processing ('stop the world')",
                "A log compaction operation","A configuration change"],
     "answerIndex":1,"explanation":"Rebalance = all partitions reassigned. During classic rebalance: every consumer in the group stops processing. High-volume topic: seconds of pause = thousands of unprocessed messages. Minimize: tune session.timeout.ms, use static membership (group.instance.id), upgrade to Kafka 3.x cooperative rebalancing.","tags":["kafka","rebalance","operations"]},
    {"id":"kafka-q20","type":"mcq","prompt":"What is the purpose of Kafka Connect?",
     "choices":["A Kafka CLI tool","A framework for streaming data between Kafka and external systems (databases, S3, Elasticsearch) using ready-made connector plugins without writing code",
                "Kafka's load balancer","Consumer group management"],
     "answerIndex":1,"explanation":"Kafka Connect: run connector plugins that import/export data. Source connectors: DB WAL -> Kafka (Debezium), S3 -> Kafka. Sink connectors: Kafka -> Elasticsearch (for search), Kafka -> S3 (for archival), Kafka -> JDBC (write to any DB). No code needed for common integrations.","tags":["kafka","kafka-connect","integration"]},
]

KAFKA_FC = [
    {"id":"kafka-fc4","front":"Kafka vs SQS fundamental difference","back":"SQS: consumed = deleted, one consumer group. Kafka: events retained (days/weeks), multiple independent consumer groups all read same events. Kafka is an event LOG not a queue. Replay is native. Fan-out is native.","tags":["kafka","sqs","comparison"]},
    {"id":"kafka-fc5","front":"Consumer group parallelism rule","back":"Max parallel consumers = number of partitions. 12 partitions = max 12 consumers in one group (each gets 1 partition). 13th consumer = idle. Design: create topics with 3-6x expected peak consumer count. Can add consumers up to partition limit.","tags":["kafka","consumer-groups","parallelism"]},
    {"id":"kafka-fc6","front":"Safe consumer offset commit","back":"enable.auto.commit=false. Process records. Then commitSync(). Auto-commit (default): may commit before processing = events lost on crash. Manual commit after processing = at-least-once (re-process on crash, must be idempotent consumer).","tags":["kafka","consumer","at-least-once"]},
    {"id":"kafka-fc7","front":"Producer acks durability tradeoffs","back":"acks=0: fastest, any loss possible. acks=1: leader ack, leader crash = loss. acks=all: all ISR ack, max durability, slowest. Production critical data: acks=all + min.insync.replicas=2 + enable.idempotence=true.","tags":["kafka","producer","acks"]},
    {"id":"kafka-fc8","front":"Log compaction use case","back":"Compacted topic: retains ONLY latest value per key. Use for: user profiles, product catalog, feature flags (current state matters, history doesn't). New service joining gets current state by reading compacted topic from start. Like materialised view in Kafka.","tags":["kafka","compaction","state"]},
]

d['guide'] = KAFKA_GUIDE
existing_ids = {q['id'] for q in d['questions']}
for q in KAFKA_Q:
    if q['id'] not in existing_ids:
        d['questions'].append(q)
existing_fc_ids = {fc['id'] for fc in d['flashcards']}
for fc in KAFKA_FC:
    if fc['id'] not in existing_fc_ids:
        d['flashcards'].append(fc)
with open(p, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"kafka.json: guide={len(KAFKA_GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

# ─────────────────────────────────────────────────────────────────────────────
# RABBITMQ
# ─────────────────────────────────────────────────────────────────────────────
p = BASE / 'rabbitmq.json'
d = json.loads(p.read_text())

RABBITMQ_GUIDE = """# RabbitMQ

## What Is RabbitMQ? The Problem It Solves

RabbitMQ is a message broker — a middleman that receives messages from publishers
and routes them to consumers. It implements the AMQP protocol (Advanced Message
Queuing Protocol).

**The core value proposition:**
```
WITHOUT RabbitMQ (direct calls):
  Service A ──────────────────────► Service B
  If B is down: A's request fails.
  If B is slow: A waits.
  A must know B's address.

WITH RabbitMQ:
  Service A ──► RabbitMQ ──► Service B
  If B is down: message waits in queue.
  If B is slow: queue buffers messages.
  A doesn't know about B. A only knows the exchange/routing key.
  Add Service C later: just subscribe to the same queue or binding.
```

---

## Core Architecture — Exchange, Binding, Queue

RabbitMQ's routing model is more flexible than Kafka. Messages go through
an Exchange which routes them to Queues based on rules.

```
PRODUCER                EXCHANGE              QUEUE              CONSUMER
   │                       │                    │                    │
   │ publish(exchange,      │                    │                    │
   │   routing_key,         │                    │                    │
   │   message)             │ bindings route     │                    │
   └──────────────────────► │ to queues          │                    │
                            │                    │                    │
                            ├── binding ────────►│ order.email.queue ─► Email Service
                            ├── binding ────────►│ order.inv.queue   ─► Inventory Svc
                            └── binding ────────►│ order.fraud.queue ─► Fraud Service

EXCHANGE: receives messages, applies routing logic, sends to queues
BINDING:  rule linking exchange to a queue (with optional routing key pattern)
QUEUE:    buffer holding messages until a consumer picks them up
```

---

## Exchange Types — The Four Routing Modes

### Direct Exchange
```
Routes to queues where binding_key == routing_key exactly.

Exchange: orders-direct
  Binding: routing_key="order.created" ──► queue: order-processing
  Binding: routing_key="order.shipped" ──► queue: shipping-notifications

Message with routing_key="order.created" -> goes to order-processing queue ONLY.
Message with routing_key="order.shipped" -> goes to shipping-notifications queue ONLY.

USE: When you know exactly which queue a message belongs to.
```

### Fanout Exchange
```
Ignores routing keys. Sends to ALL bound queues.

Exchange: order-events-fanout
  ──► queue: email-service-queue
  ──► queue: analytics-queue
  ──► queue: audit-log-queue

One message -> all three queues receive it simultaneously.

USE: Broadcasting to multiple services (like Kafka's fan-out consumer groups).
```

### Topic Exchange
```
Routes based on routing_key patterns using wildcards.
* matches one word.  # matches zero or more words.

Exchange: app-events-topic
  Binding: "order.*"     ──► queue: order-team-queue
  Binding: "order.#"     ──► queue: order-all-queue (matches any depth)
  Binding: "*.created"   ──► queue: new-items-queue
  Binding: "#.error"     ──► queue: error-handler-queue

routing_key="order.created":   matches "order.*", "order.#", "*.created" -> 3 queues
routing_key="order.item.added": matches "order.#" only (order.* needs exactly 1 word after dot)
routing_key="payment.error":   matches "*.error" and "#.error"

USE: Flexible routing by topic hierarchy. Most versatile exchange.
```

### Headers Exchange
```
Routes based on message headers (key-value pairs), not routing key.
USE: Rarely used. Complex. Prefer Topic exchange.
```

---

## Dead Letter Exchange (DLX) — Handling Failed Messages

```
When should a message be dead-lettered?
  1. Message rejected by consumer (basic.reject or basic.nack)
  2. Message TTL expired (sat in queue too long without being consumed)
  3. Queue length limit exceeded (dropped the oldest messages)

DLX SETUP:
  Normal queue: orders-queue
    x-dead-letter-exchange: "dlx-exchange"
    x-dead-letter-routing-key: "dead.order"

  DLX queue: dead-letter-queue
    bound to dlx-exchange with routing key "dead.order"

FLOW:
  Message fails 3 times in orders-queue
  -> Message moved to dead-letter-queue
  -> Engineer investigates
  -> Fix bug, re-publish fixed message to orders-queue

Without DLX: failed messages stay in queue being retried forever ("poison pill").
With DLX: isolate failures, inspect them, handle them separately.
```

---

## Message Acknowledgments — Reliability

```
Manual ACK (recommended for reliable processing):

  consumer.basicConsume(queue, autoAck=false, callback)
  |
  ▼
  [Process message]
  |
  ├── SUCCESS ──► channel.basicAck(deliveryTag)
  |               Message permanently removed from queue
  |
  └── FAILURE ──► channel.basicNack(deliveryTag, requeue=true)
                  Message put back in queue for retry
               OR channel.basicNack(deliveryTag, requeue=false)
                  Message dead-lettered (goes to DLX queue)

AUTO-ACK:
  Message removed as soon as consumer receives it.
  If consumer crashes after receiving but before processing: MESSAGE LOST.
  Only use in scenarios where message loss is acceptable.

PREFETCH (QoS):
  channel.basicQos(prefetchCount=10)
  Consumer gets max 10 unacked messages at once.
  Without prefetch: one fast consumer gets ALL messages,
  other consumers sit idle.
  With prefetch=1: fair dispatch (each consumer gets one at a time).
```

---

## RabbitMQ vs Kafka — Pick the Right Tool

```
+-------------------+-------------------------+-------------------------+
| Aspect            | RabbitMQ                | Kafka                   |
+-------------------+-------------------------+-------------------------+
| Primary model     | Message broker (routing)| Event log (streaming)   |
| Message retention | Until ACK'd (consumed)  | Days/weeks (configurable|
| Replay            | No                      | Yes                     |
| Routing           | Powerful (4 exchange    | Topic/partition only    |
|                   | types, patterns)        |                         |
| Throughput        | ~50K msgs/sec           | Millions/sec            |
| Protocol          | AMQP, STOMP, MQTT       | Custom (Kafka protocol) |
| Ordering          | Per queue               | Per partition           |
| Use case          | Task queues, RPC,       | Event streaming, CDC,   |
|                   | complex routing         | audit logs, analytics   |
+-------------------+-------------------------+-------------------------+

CHOOSE RABBITMQ WHEN:
  Complex routing logic (different queues for different message types)
  Traditional task queue (work that gets done and deleted)
  Request-response / RPC pattern over messaging
  Existing AMQP ecosystem or protocol requirement
  Simpler ops than Kafka (no ZooKeeper/KRaft, easier cluster management)
  IoT: MQTT protocol support

CHOOSE KAFKA WHEN:
  Multiple consumer groups need same events (fan-out)
  Event replay is required
  High throughput (>100K msg/sec)
  Event sourcing / CQRS architecture
  Stream processing (Kafka Streams, Flink)
```

---

## RabbitMQ Cluster and High Availability

```
CLASSIC QUEUES (not HA):
  Queue exists on one node. If that node fails: queue gone.

QUORUM QUEUES (recommended HA):
  Queue replicated across majority of nodes (quorum).
  3-node cluster: quorum = 2. Can lose 1 node without losing queue.
  Uses Raft consensus. Default for new queues in RabbitMQ 3.10+.

SETUP:
  3-node cluster minimum for HA.
  All nodes share exchange/queue metadata.
  Quorum queues: data replicated across all 3 nodes.

VERSUS KAFKA REPLICATION:
  Kafka: partition leader + ISR replicas. Proven at massive scale.
  RabbitMQ quorum queues: Raft-based, reliable but lower throughput than Kafka.
```

---

## Mind Map

```
RABBITMQ
|
+-- CORE CONCEPTS
|   +-- Exchange (routing logic)
|   +-- Binding (exchange -> queue rule)
|   +-- Queue (message buffer)
|   +-- Consumer (reads from queue)
|
+-- EXCHANGE TYPES
|   +-- Direct (exact routing key match)
|   +-- Fanout (broadcast to all queues)
|   +-- Topic (* and # wildcards)
|   +-- Headers (by message headers, rarely used)
|
+-- RELIABILITY
|   +-- Manual ACK (process then ack)
|   +-- DLX (dead letter exchange for failures)
|   +-- Prefetch/QoS (fair dispatch)
|   +-- Quorum queues (HA replication)
|
+-- VS KAFKA
    +-- RabbitMQ: task queue, complex routing, no replay
    +-- Kafka: event log, fan-out, replay, high throughput
```

---

## References and Further Learning

### Videos
- **RabbitMQ Tutorial** by TechWorld with Nana:
  https://www.youtube.com/watch?v=7rkeORD4jSw
  - 30 minutes. RabbitMQ concepts and hands-on demo.
- **RabbitMQ vs Kafka** by IBM Technology:
  https://www.youtube.com/watch?v=GMmRtSFQ5Z0
  - Clear side-by-side comparison with decision framework.

### Articles
- **RabbitMQ official tutorials** (code in 9 languages): https://www.rabbitmq.com/getstarted.html
- **CloudAMQP RabbitMQ Simulator**: https://tryrabbitmq.com/ — visual exchange/routing simulator

### Practice
- **RabbitMQ with Docker**: docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management
  Access management UI at http://localhost:15672 (guest/guest)
"""

RABBITMQ_Q = [
    {"id":"rmq-q4","type":"mcq","prompt":"What is a RabbitMQ Exchange?",
     "choices":["A queue for storing messages","A routing component that receives messages from publishers and routes them to queues based on exchange type and binding rules",
                "A consumer group","A cluster node"],
     "answerIndex":1,"explanation":"Exchange = smart router. Producer publishes to an exchange with a routing key. Exchange applies routing logic (direct/fanout/topic/headers) and sends to matching queues. Producer never writes directly to a queue — always via an exchange.","tags":["rabbitmq","exchange","routing"]},
    {"id":"rmq-q5","type":"mcq","prompt":"What exchange type broadcasts a message to ALL bound queues regardless of routing key?",
     "choices":["Direct exchange","Topic exchange","Fanout exchange — ignores routing keys entirely, sends to every queue bound to it",
                "Headers exchange"],
     "answerIndex":2,"explanation":"Fanout = broadcast. Like SNS fan-out pattern. message -> fanout exchange -> ALL bound queues receive identical copies simultaneously. Use for: audit logging, broadcasting notifications, events where multiple services all need the same message.","tags":["rabbitmq","fanout","exchange"]},
    {"id":"rmq-q6","type":"mcq","prompt":"What do * and # wildcards mean in a RabbitMQ Topic exchange binding?",
     "choices":["* = zero or more, # = exactly one","* = exactly one word, # = zero or more words (any depth)",
                "Both match any pattern","They are used for authentication"],
     "answerIndex":1,"explanation":"Topic exchange patterns: 'order.*' matches 'order.created', 'order.shipped' (one word after dot). 'order.#' matches 'order.created', 'order.item.added.to.cart' (any depth). '*.error' matches 'payment.error', 'auth.error' (one word before .error).","tags":["rabbitmq","topic","wildcards"]},
    {"id":"rmq-q7","type":"mcq","prompt":"What is a Dead Letter Exchange (DLX) in RabbitMQ?",
     "choices":["An exchange for high-priority messages","An exchange that receives messages that fail processing (rejected, TTL expired, queue full) — isolates problem messages for investigation",
                "A backup exchange","An exchange for deleted queues"],
     "answerIndex":1,"explanation":"DLX: configure on main queue (x-dead-letter-exchange). On failure/rejection/expiry: message routed to DLX instead of retried forever. Inspect dead letters, fix bugs, replay. Without DLX: poison pill messages loop forever clogging the queue.","tags":["rabbitmq","dlx","reliability"]},
    {"id":"rmq-q8","type":"mcq","prompt":"What is manual acknowledgment in RabbitMQ and why is it safer than autoAck?",
     "choices":["Manual ack is slower and not recommended","Consumer sends ack ONLY after successfully processing — if consumer crashes before acking, message requeued. AutoAck removes message as soon as delivered (loss on crash).",
                "They are identical","Manual ack requires encryption"],
     "answerIndex":1,"explanation":"autoAck=true: RabbitMQ deletes message when consumer receives it. Consumer crashes before processing: data lost. autoAck=false: message stays 'unacked' until consumer calls basicAck. Crash without ack: message requeued for another consumer. Use manual ack for reliable processing.","tags":["rabbitmq","ack","reliability"]},
    {"id":"rmq-q9","type":"mcq","prompt":"What is the purpose of `channel.basicQos(prefetchCount=1)` in RabbitMQ?",
     "choices":["Limits message size to 1KB","Tells RabbitMQ to send max 1 unacked message per consumer at a time — fair dispatch, prevents one fast consumer from getting all messages",
                "Creates 1 channel","Enables compression"],
     "answerIndex":1,"explanation":"Without prefetch: consumer 1 gets ALL 1000 queued messages immediately (even if consumer 2 is idle). With prefetch=1: each consumer gets 1 message, processes, acks, gets next. Other consumers also get work. Fair round-robin. Use prefetch=1 for long-running tasks.","tags":["rabbitmq","prefetch","qos"]},
    {"id":"rmq-q10","type":"mcq","prompt":"What is the main difference between RabbitMQ and Kafka for message retention?",
     "choices":["RabbitMQ retains messages longer","Kafka retains messages for days/weeks independently of consumption. RabbitMQ keeps messages only until they are consumed (or expired) — no replay possible.",
                "They are the same","Both delete after 24 hours"],
     "answerIndex":1,"explanation":"Kafka: event log with time-based retention. Replay from day 1 is possible. New service: read from beginning. RabbitMQ: message consumed = gone. Cannot replay. If a new service starts, it only sees messages published after its start. Fundamental architectural difference.","tags":["rabbitmq","kafka","retention"]},
    {"id":"rmq-q11","type":"mcq","prompt":"What are Quorum Queues in RabbitMQ?",
     "choices":["Queues with priority","Replicated queues using Raft consensus — queue data exists on majority of cluster nodes. Recommended for HA over classic mirrored queues (deprecated).",
                "Queues with message quotas","Leader-only queues"],
     "answerIndex":1,"explanation":"Quorum queues (Raft): queue replicated to all (or configurable) nodes. One node dies: other nodes have complete queue data, elect new leader, no message loss. Much more reliable than classic queues (exist on single node). Default recommendation for RabbitMQ 3.10+.","tags":["rabbitmq","quorum-queues","ha"]},
    {"id":"rmq-q12","type":"mcq","prompt":"When is RabbitMQ a better choice than Kafka?",
     "choices":["Always","When you need complex message routing (different queues for types), traditional task queues, request-reply RPC patterns, or IoT/MQTT protocol support",
                "When you need message replay","When you need millions of messages per second"],
     "answerIndex":1,"explanation":"RabbitMQ strengths: 4 exchange types (esp. Topic for complex routing), simple task queues (email sending, PDF generation), RPC over messaging, AMQP/STOMP/MQTT protocols. Kafka wins on throughput and replay. Most CRUD apps with messaging needs: RabbitMQ is simpler.","tags":["rabbitmq","use-cases","vs-kafka"]},
    {"id":"rmq-q13","type":"mcq","prompt":"What does `basicNack(deliveryTag, requeue=false)` do?",
     "choices":["Acknowledges the message","Negatively acknowledges and DISCARDS the message (or sends to DLX if configured) — use when the message is malformed and retrying would always fail",
                "Requeues multiple times","Pauses the consumer"],
     "answerIndex":1,"explanation":"basicNack with requeue=false: 'I cannot process this, don't retry'. Message goes to DLX (if configured) or dropped. Use for: malformed messages (retrying won't fix them), messages exceeding max retry count. basicNack with requeue=true: 'try again later' (careful: instant loop without delay).","tags":["rabbitmq","ack","nack"]},
    {"id":"rmq-q14","type":"mcq","prompt":"What is the AMQP protocol?",
     "choices":["A Kafka protocol","Advanced Message Queuing Protocol — open standard messaging protocol implemented by RabbitMQ. Defines wire format, exchange/queue semantics, acknowledgments.",
                "A REST API standard","A database protocol"],
     "answerIndex":1,"explanation":"AMQP: open wire protocol for messaging. RabbitMQ is the most popular AMQP broker. Any AMQP client library works with RabbitMQ (Java, Python, Node.js, Go, .NET). RabbitMQ also supports STOMP, MQTT (IoT), HTTP. Standard protocol = vendor-neutral tooling.","tags":["rabbitmq","amqp","protocol"]},
    {"id":"rmq-q15","type":"mcq","prompt":"What is the request-reply (RPC) pattern over RabbitMQ?",
     "choices":["Cannot be done with RabbitMQ","Producer sends request with a reply-to queue and correlation ID. Consumer processes and publishes response to reply-to queue. Producer blocks waiting for response on that queue.",
                "Requires direct exchange only","Request-reply needs Kafka"],
     "answerIndex":1,"explanation":"RPC over RabbitMQ: client generates reply_queue + correlation_id. Publishes request with reply_to=reply_queue. Server processes, publishes response to reply_to queue with same correlation_id. Client consumer receives response. Used for: synchronous-feeling RPC across services without HTTP.","tags":["rabbitmq","rpc","request-reply"]},
    {"id":"rmq-q16","type":"mcq","prompt":"What is message TTL in RabbitMQ?",
     "choices":["Transport Transfer Layer","Time To Live — message automatically discarded if not consumed within the specified time. Configurable per-message or per-queue.",
                "Total Throughput Limit","Transaction Termination Log"],
     "answerIndex":1,"explanation":"TTL: per-queue (x-message-ttl=60000 ms) or per-message. Expired message -> dead-lettered (if DLX configured) or dropped. Use: time-sensitive notifications (if not sent in 10 minutes, don't send — outdated), rate limiting, preventing queue backup from slow consumers.","tags":["rabbitmq","ttl","expiry"]},
    {"id":"rmq-q17","type":"mcq","prompt":"What is the 'competing consumers' pattern in RabbitMQ?",
     "choices":["Multiple producers on one queue","Multiple consumers reading from the SAME queue — messages distributed among them (not replicated). Each message goes to exactly one consumer. Scale throughput by adding consumers.",
                "Consumer fighting for connection","Consumers on different nodes"],
     "answerIndex":1,"explanation":"Competing consumers: 10 emails to send, 3 consumers. Consumer 1 gets email 1, Consumer 2 gets email 2, Consumer 3 gets email 3, Consumer 1 finishes, gets email 4... Work distributed across all consumers. Add consumers = scale throughput linearly (up to queue limit).","tags":["rabbitmq","competing-consumers","scaling"]},
    {"id":"rmq-q18","type":"mcq","prompt":"How does RabbitMQ achieve message durability?",
     "choices":["Messages are never persisted","Durable queues (survive broker restart) + persistent messages (delivery_mode=2 written to disk) + publisher confirms. All three needed for guaranteed durability.",
                "Replication handles durability","Messages are cached in RAM only"],
     "answerIndex":1,"explanation":"Full durability: 1) durable=True queue (survives restart). 2) delivery_mode=2 message (written to disk before delivery). 3) Publisher confirms (broker ACKs producer when persisted). Without all three: messages lost on broker restart or crash.","tags":["rabbitmq","durability","persistence"]},
    {"id":"rmq-q19","type":"mcq","prompt":"What is publisher confirms in RabbitMQ?",
     "choices":["Consumer acknowledging the publisher","Broker sends acknowledgment to producer when message is safely stored/routed — producer can retry if no confirm received within timeout",
                "A logging feature","Exchange routing confirmation"],
     "answerIndex":1,"explanation":"Publisher confirms: channel.confirmSelect(). After publishing: wait for broker ACK. If broker crashes before ACK: producer knows to retry. Without confirms: producer assumes message received (fire-and-forget). Required for at-least-once delivery guarantee from producer side.","tags":["rabbitmq","publisher-confirms","reliability"]},
    {"id":"rmq-q20","type":"mcq","prompt":"What priority queues in RabbitMQ allow?",
     "choices":["Messages sorted by timestamp","Messages with higher priority value processed before lower-priority messages in the same queue — configured with x-max-priority",
                "Consumers get priority access","Queue replication priority"],
     "answerIndex":1,"explanation":"Priority queues: x-max-priority=10 (values 0-10). Consumer gets highest-priority unacked message first. Use: urgent orders over regular, P1 alerts over P3, premium users over free users. Note: priority processing has overhead — only use when genuinely needed.","tags":["rabbitmq","priority","advanced"]},
]

RABBITMQ_FC = [
    {"id":"rmq-fc4","front":"RabbitMQ exchange types","back":"Direct: exact routing key match (order.created -> processing queue). Fanout: broadcast to ALL bound queues. Topic: wildcard patterns (* = 1 word, # = any). Headers: by message attributes. Most flexible: Topic. Simplest: Direct or Fanout.","tags":["rabbitmq","exchange"]},
    {"id":"rmq-fc5","front":"Dead Letter Exchange setup","back":"On main queue: x-dead-letter-exchange=dlx, x-dead-letter-routing-key=dead. Create DLX exchange + dead letter queue. Messages failing after retries/rejection/TTL go to DLX. Alert on DLQ depth. Investigate and replay. Isolates poison pills.","tags":["rabbitmq","dlx"]},
    {"id":"rmq-fc6","front":"Manual ACK vs AutoAck","back":"autoAck=false + channel.basicAck(tag) after processing = safe. Message requeued if consumer crashes mid-process. autoAck=true = message deleted on receipt, lost if crash mid-process. Always use manual ACK for reliable task queues.","tags":["rabbitmq","ack","reliability"]},
    {"id":"rmq-fc7","front":"RabbitMQ vs Kafka one-liner","back":"RabbitMQ: task queue, complex routing (4 exchange types), message consumed=gone, ~50K msg/sec. Kafka: event log, replay, fan-out, millions/sec. RabbitMQ for routing complexity. Kafka for event streaming and replay.","tags":["rabbitmq","kafka","comparison"]},
    {"id":"rmq-fc8","front":"Full message durability checklist","back":"1. Durable queue (durable=True). 2. Persistent message (delivery_mode=2). 3. Publisher confirms (channel.confirmSelect()). All 3 required. Missing any one: messages lost on broker restart or crash.","tags":["rabbitmq","durability"]},
]

d['guide'] = RABBITMQ_GUIDE
existing_ids = {q['id'] for q in d['questions']}
for q in RABBITMQ_Q:
    if q['id'] not in existing_ids:
        d['questions'].append(q)
existing_fc_ids = {fc['id'] for fc in d['flashcards']}
for fc in RABBITMQ_FC:
    if fc['id'] not in existing_fc_ids:
        d['flashcards'].append(fc)
with open(p, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"rabbitmq.json: guide={len(RABBITMQ_GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

# ─────────────────────────────────────────────────────────────────────────────
# RPC
# ─────────────────────────────────────────────────────────────────────────────
p = BASE / 'rpc.json'
d = json.loads(p.read_text())

RPC_GUIDE = """# RPC — Remote Procedure Call (gRPC vs REST)

## What Is RPC? The Big Picture

When function A in your code calls function B — that's a local procedure call.
The call is fast (nanoseconds), strongly typed, and the caller and callee share
the same process memory.

**RPC (Remote Procedure Call)** makes calling code in ANOTHER computer (or service)
feel like a local function call. The network complexity is hidden from the developer.

```
LOCAL CALL:                         REMOTE CALL (RPC):
  result = getUserById(123)           result = userService.getUserById(123)
  |                                   |
  | direct function call              | looks the same in code!
  | nanoseconds                       | but actually:
  | same process memory               |   serialize arguments
                                      |   send over network (TCP/HTTP)
                                      |   remote server deserializes
                                      |   remote function executes
                                      |   serialize result
                                      |   send back over network
                                      |   deserialize result
                                      | 1-10ms (network latency)
```

**REST vs RPC mental model:**
- REST: "I want to GET the resource at /users/123"
- RPC: "I want to CALL the function getUserById(123)"

REST is resource-oriented. RPC is action-oriented. gRPC is modern RPC.

---

## REST — The Dominant API Style

REST (Representational State Transfer) uses HTTP methods to operate on resources
identified by URLs.

```
HTTP Method -> CRUD mapping:
  GET    /users/123        -> Read user 123
  POST   /users            -> Create new user (body contains user data)
  PUT    /users/123        -> Replace user 123 entirely
  PATCH  /users/123        -> Partially update user 123
  DELETE /users/123        -> Delete user 123

JSON over HTTP:
  Request:
    GET /users/123
    Accept: application/json
    Authorization: Bearer eyJhbGci...

  Response:
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
      "id": 123,
      "name": "Alice",
      "email": "alice@example.com",
      "createdAt": "2026-01-15T10:30:00Z"
    }

HTTP Status Codes (must know):
  200 OK            -> success
  201 Created       -> resource created (after POST)
  204 No Content    -> success, no body (after DELETE)
  400 Bad Request   -> client sent bad data
  401 Unauthorized  -> not authenticated
  403 Forbidden     -> authenticated but not allowed
  404 Not Found     -> resource doesn't exist
  409 Conflict      -> duplicate (unique constraint violation)
  422 Unprocessable -> validation failed
  429 Too Many Req  -> rate limited
  500 Internal Err  -> server bug
  503 Unavailable   -> server overloaded / downstream down

REST strengths:
  Universal: every language, every client (browser, mobile, server) speaks HTTP
  Human readable: JSON is inspectable, curl-able, logged clearly
  Cacheable: GET responses cached by browsers, CDNs, proxies
  Stateless: each request is self-contained
  Tooling: Swagger/OpenAPI, Postman, every HTTP library ever

REST weaknesses:
  No contract enforcement (anyone can send wrong JSON shape)
  HTTP/1.1: one request per TCP connection by default (HTTP/2 fixes this)
  Over/under-fetching: endpoint returns too much or not enough
  Not ideal for streaming or bidirectional communication
```

---

## gRPC — Modern High-Performance RPC

gRPC was developed by Google and is built on Protocol Buffers + HTTP/2.

```
HOW gRPC WORKS:

1. Define service in .proto file:
   service UserService {
     rpc GetUser (GetUserRequest) returns (User);
     rpc ListUsers (ListUsersRequest) returns (stream User);
     rpc CreateUser (stream CreateUserRequest) returns (CreateUserResponse);
     rpc Chat (stream ChatMessage) returns (stream ChatMessage);
   }

   message GetUserRequest { int64 user_id = 1; }
   message User {
     int64 id = 1;
     string name = 2;
     string email = 3;
   }

2. Run protoc compiler:
   Generates strongly-typed client + server code in YOUR language.
   Java, Python, Go, Node.js, C++, Kotlin, Swift, Rust, etc.

3. Use generated client:
   // Java client (generated stub)
   UserServiceGrpc.UserServiceBlockingStub stub = ...;
   User user = stub.getUser(GetUserRequest.newBuilder().setUserId(123).build());
   System.out.println(user.getName()); // type-safe!

4. Wire format: Protocol Buffers (binary, not JSON)
   JSON "id": 123    -> 3+ bytes: 7 chars + quotes + colon + space
   Proto field 1=123 -> 2 bytes: field tag + varint
   ~5-10x smaller. 5-10x faster to serialize/deserialize.
```

---

## gRPC vs REST Comparison

```
+------------------+---------------------------+---------------------------+
| Feature          | gRPC                      | REST/JSON                 |
+------------------+---------------------------+---------------------------+
| Protocol         | HTTP/2                    | HTTP/1.1 or HTTP/2        |
| Serialization    | Protocol Buffers (binary) | JSON (text)               |
| Contract         | .proto file (strict)      | Optional (OpenAPI/Swagger)|
| Code generation  | Built-in (protoc)         | Optional (openapi-gen)    |
| Streaming        | Bidirectional streams     | HTTP/2 only               |
| Browser support  | Limited (grpc-web needed) | Native                    |
| Human readable   | No (binary wire format)   | Yes (JSON)                |
| Performance      | ~5-10x faster             | Baseline                  |
| Typed            | Strongly typed            | Weakly typed (JSON)       |
| Use case         | Internal microservices    | Public APIs, browser      |
+------------------+---------------------------+---------------------------+

WHEN TO USE gRPC:
  Internal microservice communication (service-to-service)
  Performance-critical paths (thousands of calls per second)
  Bidirectional streaming (chat, live updates, sensor data)
  Polyglot services (generate client in each service's language)
  Mobile clients (smaller payload = less data usage, faster on 4G)

WHEN TO USE REST:
  Public APIs that third parties and browsers must consume
  Debugging/inspectability is important
  Team unfamiliar with Protocol Buffers
  Simple CRUD with no performance pressure
  Webhooks and callbacks
```

---

## Protocol Buffers Deep Dive

```
.proto file defines message structure and service:

syntax = "proto3";
package users;

message User {
  int64 id = 1;           // field number 1
  string name = 2;        // field number 2
  string email = 3;       // field number 3
  bool active = 4;
  repeated string tags = 5;  // repeated = array
  UserStatus status = 6;
}

enum UserStatus {
  ACTIVE = 0;
  INACTIVE = 1;
  SUSPENDED = 2;
}

message GetUserRequest {
  int64 user_id = 1;
}

service UserService {
  rpc GetUser (GetUserRequest) returns (User);
}

WIRE FORMAT (binary, field number + type + value):
  {id: 123, name: "Alice", email: "a@b.com"}
  JSON:   38 bytes: {"id":123,"name":"Alice","email":"a@b.com"}
  Proto:  ~15 bytes: \x08\x7b\x12\x05Alice\x1a\x07a@b.com

BACKWARDS COMPATIBILITY:
  Add new fields with new numbers: v1 clients ignore unknown fields.
  NEVER change existing field numbers (breaks wire format).
  NEVER remove required fields.
  This is Proto's key advantage: schema evolution without breaking clients.
```

---

## gRPC Streaming — Four Patterns

```
1. UNARY RPC (request-response, like REST):
   client.getUser(request) -> single response
   Use: standard queries

2. SERVER STREAMING:
   client.listUsers(request) -> stream of responses
   Server sends multiple response messages as they become available.
   Client reads stream until server closes.
   Use: return large result sets without buffering, live logs

3. CLIENT STREAMING:
   client.uploadFile(stream of chunks) -> single response
   Client sends multiple request messages before getting response.
   Use: file upload, bulk insert

4. BIDIRECTIONAL STREAMING:
   Chat(stream of messages) -> stream of messages
   Both client and server can send independently.
   Use: real-time chat, collaborative editing, game state
```

---

## GraphQL — Third Option for APIs

```
REST problem: over-fetching and under-fetching.
  GET /users/123 -> returns ALL user fields even if you only need name
  GET /users/123/orders -> separate request, N+1 for all users

GraphQL solves this:
  Client specifies EXACTLY what fields it needs in one query.

  query {
    user(id: 123) {
      name
      email
      orders(last: 5) {
        total
        status
      }
    }
  }

  Returns: only name, email, last 5 orders with total and status.
  One request. No over-fetching. No under-fetching. No N+1.

GraphQL vs REST vs gRPC:
  REST: simple CRUD, public APIs, browser-native
  GraphQL: complex queries from frontend, mobile clients with data efficiency
  gRPC: internal microservices, high performance, streaming

Not a silver bullet: GraphQL has N+1 issues on server side (use DataLoader),
complex schema management, no caching by default.
```

---

## Mind Map

```
RPC / gRPC / REST
|
+-- REST
|   +-- HTTP methods (GET/POST/PUT/PATCH/DELETE)
|   +-- Resources identified by URL
|   +-- JSON (human-readable)
|   +-- Universal browser/client support
|   +-- Status codes (200/404/500...)
|
+-- gRPC
|   +-- Protocol Buffers (.proto IDL)
|   +-- Binary wire format (5-10x smaller/faster)
|   +-- HTTP/2 (multiplexing, server push)
|   +-- Code generation (typed stubs)
|   +-- 4 streaming modes
|   +-- Internal microservices
|
+-- GraphQL
|   +-- Client specifies exact fields needed
|   +-- One endpoint (/graphql)
|   +-- Solves over/under-fetching
|   +-- Frontend-driven API
|
+-- WHEN TO USE
    +-- REST: public API, browser, simplicity
    +-- gRPC: internal services, performance, streaming
    +-- GraphQL: complex frontend data requirements
```

---

## References and Further Learning

### Videos
- **gRPC vs REST: Understanding gRPC, OpenAPI and REST** by Google:
  https://www.youtube.com/watch?v=k5BU28dPTgY
  - Official comparison with use case guidance.
- **gRPC Crash Course** by Traversy Media:
  https://www.youtube.com/watch?v=Yw4rkaTc0f8
  - Hands-on gRPC with Node.js demo.

### Articles
- **Protocol Buffers encoding**: https://protobuf.dev/programming-guides/encoding/
  - How binary encoding works under the hood.
- **gRPC official docs**: https://grpc.io/docs/
  - Language-specific quickstarts (Java, Python, Go, Node.js).

### Practice
- Build a gRPC service in Go or Python. Compare payload size with equivalent REST JSON.
- **Buf Schema Registry**: https://buf.build — modern Proto toolchain
"""

RPC_Q = [
    {"id":"rpc-q4","type":"mcq","prompt":"What is the core idea behind gRPC?",
     "choices":["A REST API specification","Define services in .proto files, use Protocol Buffers for binary serialization over HTTP/2 — generates strongly-typed client/server code in any language",
                "A JSON API standard","An HTTP/1.1 optimization"],
     "answerIndex":1,"explanation":"gRPC: 1) Write .proto IDL (interface definition). 2) Run protoc to generate typed stubs for your language. 3) Use generated client — looks like local function calls. Wire: binary Protocol Buffers over HTTP/2. 5-10x faster/smaller than JSON/REST.","tags":["grpc","protocol-buffers"]},
    {"id":"rpc-q5","type":"mcq","prompt":"What serialization format does gRPC use and why is it faster than JSON?",
     "choices":["XML","YAML","Protocol Buffers — binary encoding with field numbers instead of field names. ~5-10x smaller payload, ~10x faster to serialize/deserialize vs JSON text parsing.",
                "MessagePack"],
     "answerIndex":2,"explanation":"JSON: 'name': 'Alice' = 14 chars (field name repeated every time). Proto field 2='Alice' = 7 bytes (field number + length + bytes). No field names on wire. Binary: no string parsing. Numbers as varints not ASCII digits. Also: proto-generated code avoids reflection.","tags":["grpc","protobuf","serialization"]},
    {"id":"rpc-q6","type":"mcq","prompt":"What HTTP version does gRPC require and why?",
     "choices":["HTTP/1.0","HTTP/1.1","HTTP/2 — provides multiplexing (multiple concurrent streams on one TCP connection), header compression, server push, used for all 4 gRPC streaming modes",
                "HTTP/3 (QUIC)"],
     "answerIndex":2,"explanation":"HTTP/2: single TCP connection, multiple streams. gRPC bidirectional streaming needs both sides to send anytime on same connection — impossible with HTTP/1.1's request-response model. HTTP/2 also: header compression (HPACK), binary protocol = less overhead.","tags":["grpc","http2"]},
    {"id":"rpc-q7","type":"mcq","prompt":"What are the four gRPC streaming patterns?",
     "choices":["Push, pull, batch, stream","Unary (1 request 1 response), server streaming (1 req many responses), client streaming (many reqs 1 response), bidirectional (many req many resp simultaneously)",
                "Sync, async, batch, realtime","REST, GraphQL, WebSocket, Poll"],
     "answerIndex":1,"explanation":"Unary: like REST call. Server streaming: client subscribes to server events (live logs). Client streaming: upload file in chunks. Bidirectional: real-time chat, collaborative editing, both sides send independently on same stream.","tags":["grpc","streaming"]},
    {"id":"rpc-q8","type":"mcq","prompt":"Why can't gRPC be called directly from a browser?",
     "choices":["Browsers don't support HTTP/2","Browsers cannot access HTTP/2 trailers needed by gRPC. Workaround: grpc-web (transcoding proxy) or use REST for browser-facing APIs and gRPC for service-to-service.",
                "gRPC requires WebSockets","Browsers only support JSON"],
     "answerIndex":1,"explanation":"gRPC uses HTTP/2 trailers (metadata after response body). Browser fetch API cannot access trailers. Solution: grpc-web protocol (with Envoy proxy) transcodes grpc-web to full gRPC. Or: use REST for public/browser APIs, gRPC for internal microservice communication only.","tags":["grpc","browser","limitations"]},
    {"id":"rpc-q9","type":"mcq","prompt":"What is backward compatibility in Protocol Buffers?",
     "choices":["New proto versions break old clients always","Add new fields with new field numbers — old clients ignore unknown fields (forward compatible). Never change existing field numbers or remove required fields.",
                "Backward compat requires versioning","Proto is not backward compatible"],
     "answerIndex":1,"explanation":"Proto3: add field 10: string phone = 10; Old clients (no field 10) receive message with phone field: they ignore it (proto skips unknown fields). Old client sends message without field 10: new server gets empty/default value. Safe schema evolution. NEVER reuse or change field numbers.","tags":["grpc","protobuf","backward-compat"]},
    {"id":"rpc-q10","type":"mcq","prompt":"What HTTP status code should a REST API return when an authenticated user tries to access a resource they don't have permission for?",
     "choices":["401 Unauthorized","404 Not Found","403 Forbidden — user is authenticated (401 would mean not authenticated) but lacks permission for this specific resource",
                "400 Bad Request"],
     "answerIndex":2,"explanation":"401: not authenticated (no valid token/session). 403: authenticated but not authorized (valid token, but user's role/permissions don't allow this action). Common mistake: returning 401 when 403 is correct. 404 sometimes used intentionally to hide resource existence from unauthorized users.","tags":["rest","http-status","auth"]},
    {"id":"rpc-q11","type":"mcq","prompt":"What problem does GraphQL solve that REST doesn't?",
     "choices":["GraphQL is faster than REST","Over-fetching (getting too many fields) and under-fetching (needing multiple requests for related data) — GraphQL lets client specify exactly what fields it needs in one request",
                "GraphQL supports binary encoding","GraphQL has better authentication"],
     "answerIndex":1,"explanation":"REST GET /users/123: returns ALL 50 fields even if mobile app needs 3. REST N+1: fetch users, then fetch orders for each user separately. GraphQL: one query specifies exactly {user { name orders { total } }} = one request, only requested fields.","tags":["graphql","rest","over-fetching"]},
    {"id":"rpc-q12","type":"mcq","prompt":"What is idempotency in REST API design?",
     "choices":["All REST calls must be fast","An operation that produces the same result whether called once or N times. GET, PUT, DELETE are idempotent. POST is NOT (calling POST /orders twice creates two orders).",
                "Only GET is allowed in REST","Every request must return 200"],
     "answerIndex":1,"explanation":"GET: no state change, idempotent obviously. PUT /users/123 {name: Alice}: sets name to Alice. Call 5 times: still name is Alice. Idempotent. POST /orders: creates new order each time. NOT idempotent. PATCH: depends on implementation. Clients can safely retry idempotent calls.","tags":["rest","idempotency","http-methods"]},
    {"id":"rpc-q13","type":"mcq","prompt":"What is the difference between PUT and PATCH in REST?",
     "choices":["They are identical","PUT: replace the ENTIRE resource (send all fields). PATCH: partial update (send only changed fields). PUT with missing field = field set to default/null.",
                "PATCH is newer and deprecated PUT","PUT creates, PATCH updates"],
     "answerIndex":1,"explanation":"PUT /users/123 {name: Alice}: replaces entire user. If you omit email, email becomes null. PATCH /users/123 {name: Alice}: only changes name, all other fields unchanged. Use PATCH for partial updates. Use PUT when you want to explicitly set the complete resource state.","tags":["rest","put","patch","http-methods"]},
    {"id":"rpc-q14","type":"mcq","prompt":"What header does a REST API use to return rate limit information?",
     "choices":["Authorization","Content-Type","X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset (standard de-facto headers) and 429 status code when limit exceeded",
                "Cache-Control"],
     "answerIndex":2,"explanation":"Rate limit headers: X-RateLimit-Limit (max calls per window), X-RateLimit-Remaining (calls left), X-RateLimit-Reset (Unix timestamp when limit resets). HTTP 429 Too Many Requests body: {error: 'rate_limit_exceeded', retry_after: 60}. Used by GitHub, Twitter, Stripe APIs.","tags":["rest","rate-limiting","headers"]},
    {"id":"rpc-q15","type":"mcq","prompt":"What is a .proto file in gRPC?",
     "choices":["A protocol configuration file","Interface Definition Language (IDL) file specifying messages (data types) and services (RPC methods) — compiled by protoc to generate typed client/server code",
                "A deployment configuration","A gRPC test file"],
     "answerIndex":1,"explanation":".proto = contract. Define: message User {int64 id = 1; string name = 2;}. Define: service UserService {rpc GetUser (GetUserRequest) returns (User);}. Run protoc: generates UserServiceGrpc.java, user_pb2.py, user.pb.go depending on language. All clients use same contract.","tags":["grpc","proto","idl"]},
    {"id":"rpc-q16","type":"mcq","prompt":"What is HATEOAS in REST?",
     "choices":["A REST security model","Hypermedia As The Engine Of Application State — responses include links to related actions. Client discovers API by following links, not hardcoding URLs.",
                "HTTP Authentication standard","A caching strategy"],
     "answerIndex":1,"explanation":"HATEOAS: GET /orders/123 response includes: {id:123, status:pending, _links:{pay:{href:/orders/123/pay},cancel:{href:/orders/123/cancel}}}. Client knows what it can DO with this resource from the response. URL structure can change without breaking clients. Rarely fully implemented but level 3 of Richardson REST maturity model.","tags":["rest","hateoas","design"]},
    {"id":"rpc-q17","type":"mcq","prompt":"What is API versioning in REST and the most common approaches?",
     "choices":["REST APIs don't need versioning","URL path versioning (/api/v1/users), header versioning (Accept: application/vnd.api+json;version=1), or query param (?version=1). URL path versioning is most common because it's visible and cacheable.",
                "REST uses semantic versioning","Proto versioning handles this"],
     "answerIndex":1,"explanation":"URL versioning: /api/v1/users vs /api/v2/users — clear, cacheable, easy to route. Header versioning: cleaner URLs but less visible. Breaking changes require new version. Non-breaking (adding fields): backwards compatible, no new version needed. Proto's field numbers handle versioning implicitly.","tags":["rest","versioning","api-design"]},
    {"id":"rpc-q18","type":"mcq","prompt":"What is the main advantage of gRPC for internal microservices over REST?",
     "choices":["gRPC supports more HTTP methods","Strongly-typed contracts prevent integration bugs, binary Protocol Buffers are 5-10x smaller/faster, HTTP/2 multiplexing reduces connections, code generation eliminates manual client code",
                "gRPC works in browsers","gRPC is easier to debug"],
     "answerIndex":1,"explanation":"Service-to-service: REST json has no contract (wrong field = runtime error). gRPC .proto = compile-time type checking. Binary: at 10K calls/sec, 5x smaller payload = significant bandwidth saving. HTTP/2 multiplexing: one connection for all calls (REST HTTP/1.1: one connection per request or connection pooling needed).","tags":["grpc","microservices","internal"]},
    {"id":"rpc-q19","type":"mcq","prompt":"What is the gRPC status code equivalent to HTTP 404?",
     "choices":["STATUS_NOT_FOUND is returned as gRPC status code 5","gRPC doesn't map to HTTP","gRPC uses HTTP 404","gRPC uses error messages"],
     "answerIndex":0,"explanation":"gRPC has its own status codes: OK(0), CANCELLED(1), NOT_FOUND(5), ALREADY_EXISTS(6), PERMISSION_DENIED(7), UNAUTHENTICATED(16), RESOURCE_EXHAUSTED(8=rate limited), INTERNAL(13), UNAVAILABLE(14). Map to HTTP status for grpc-web proxies. NOT_FOUND is the gRPC equivalent of HTTP 404.","tags":["grpc","status-codes"]},
    {"id":"rpc-q20","type":"mcq","prompt":"What is an OpenAPI (Swagger) specification?",
     "choices":["A gRPC contract format","YAML/JSON file describing a REST API — endpoints, request/response schemas, auth method. Generates documentation, client SDKs, server stubs, test cases automatically.",
                "A database schema format","A security standard"],
     "answerIndex":1,"explanation":"OpenAPI: machine-readable REST API contract. openapi: 3.0. paths: /users/{id}: get: responses: 200: schema: $ref: User. Tools: Swagger UI (interactive docs), openapi-generator (client SDKs in 50+ languages), Postman import. The REST equivalent of gRPC's .proto files.","tags":["rest","openapi","swagger"]},
]

RPC_FC = [
    {"id":"rpc-fc4","front":"gRPC vs REST decision","back":"gRPC: internal microservices, high-perf, polyglot, streaming. REST: public APIs, browser clients, simplicity, human-readable. GraphQL: frontend-driven, exact field selection, complex queries. Most systems: REST for public, gRPC for internal.","tags":["grpc","rest","decision"]},
    {"id":"rpc-fc5","front":"Protocol Buffers wire encoding","back":"Field number + wire type + value. No field names on wire. 5-10x smaller than JSON. Backwards compat: add fields with new numbers, old clients ignore them. NEVER change existing field numbers. Use proto3 for all new projects.","tags":["grpc","protobuf"]},
    {"id":"rpc-fc6","front":"gRPC 4 streaming patterns","back":"Unary: 1 req -> 1 resp (like REST). Server stream: 1 req -> many resp (live logs, search results). Client stream: many req -> 1 resp (file upload). Bidirectional: many req + many resp simultaneously (real-time chat, collaboration).","tags":["grpc","streaming"]},
    {"id":"rpc-fc7","front":"REST HTTP status cheatsheet","back":"2xx: success (200 OK, 201 Created, 204 No Content). 4xx: client error (400 Bad Request, 401 Unauthenticated, 403 Forbidden, 404 Not Found, 409 Conflict, 429 Rate Limited). 5xx: server error (500 Internal, 503 Unavailable).","tags":["rest","http-status"]},
    {"id":"rpc-fc8","front":"REST idempotency by method","back":"Idempotent (safe to retry): GET, PUT, DELETE, HEAD. NOT idempotent: POST (creates new resource each call), PATCH (depends). Retry logic: only retry idempotent methods automatically. POST requires idempotency key if client needs to retry.","tags":["rest","idempotency"]},
]

d['guide'] = RPC_GUIDE
existing_ids = {q['id'] for q in d['questions']}
for q in RPC_Q:
    if q['id'] not in existing_ids:
        d['questions'].append(q)
existing_fc_ids = {fc['id'] for fc in d['flashcards']}
for fc in RPC_FC:
    if fc['id'] not in existing_fc_ids:
        d['flashcards'].append(fc)
with open(p, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"rpc.json: guide={len(RPC_GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

