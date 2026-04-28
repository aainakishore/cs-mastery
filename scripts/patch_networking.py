"""
Patch Networking — Consolidated Patch Script
Consolidated from: patch_networking_1.py, patch_networking_2.py, patch_networking_3.py, patch_ws_extra.py, fix_ftp_guide.py
Run: python3 scripts/patch_networking.py
Each section is clearly delimited — you can copy/edit individual sections.
"""
import json
from pathlib import Path

BASE = Path(__file__).parent.parent / "src/content/topics"


def patch(folder, filename, updates):
    p = BASE / folder / filename
    if not p.exists():
        print(f"  SKIP (not found): {folder}/{filename}")
        return
    d = json.loads(p.read_text())
    before_q = len(d.get("questions", []))
    d.update(updates)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    print(f"  OK {filename}: guide={len(d.get('guide',''))} q={len(d.get('questions',[]))} fc={len(d.get('flashcards',[]))}")


def main():

    # ── patch_networking_1.py ──────────────────────────────────────────────────────────────────
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

    # ── patch_networking_2.py ──────────────────────────────────────────────────────────────────
    """
    patch_networking_2.py — firewalls.json, proxies.json, websockets.json
    Run: python3 scripts/patch_networking_2.py
    """
    import json
    from pathlib import Path

    BASE = Path(__file__).parent.parent / 'src/content/topics/networking'

    # ─────────────────────────────────────────────────────────────────────────────
    # FIREWALLS
    # ─────────────────────────────────────────────────────────────────────────────
    p = BASE / 'firewalls.json'
    d = json.loads(p.read_text())

    FIREWALLS_GUIDE = """# Firewalls

    ## What Is a Firewall? Start From Zero

    Imagine your home has a front door with a doorman. The doorman has a list of rules:
    "Let in family members, let in the pizza delivery person on Friday nights,
    but don't let in strangers wearing masks." A firewall does the same thing for
    network traffic — it decides which packets (network messages) are allowed
    through and which are blocked.

    A **firewall** is a network security system that monitors and controls incoming
    and outgoing network traffic based on predetermined security rules.

    ```
    INTERNET (untrusted)         FIREWALL            PRIVATE NETWORK (trusted)
       │                            │                        │
       │  TCP SYN to port 443  ──►  │  Allow: port 443?      │
       │  ← ── ── ── ── ── ──       │  ALLOW -> forward ──►  │  Your web server
       │                            │                        │
       │  TCP SYN to port 22   ──►  │  Allow: port 22?       │
       │  ← blocked ──              │  DENY -> drop packet   │
       │  (no response)             │                        │
    ```

    Without a firewall: your servers are directly reachable on every port from every IP
    on the internet. Any exposed service (database! admin panel! SSH!) is an attack surface.

    ---

    ## Packet Filtering — The Foundation

    All firewalls fundamentally inspect packet headers and decide ALLOW or DENY.

    ```
    A network packet has headers the firewall can inspect:
      Source IP:       1.2.3.4
      Destination IP:  10.0.0.1
      Source Port:     54321 (ephemeral port from client)
      Destination Port: 443 (HTTPS)
      Protocol:        TCP / UDP / ICMP
      TCP Flags:       SYN, ACK, FIN, RST

    FIREWALL RULE EXAMPLE:
      Source IP   | Dest IP    | Protocol | Dest Port | Action
      0.0.0.0/0   | 10.0.0.1   | TCP      | 443       | ALLOW
      0.0.0.0/0   | 10.0.0.1   | TCP      | 80        | ALLOW
      0.0.0.0/0   | 10.0.0.1   | TCP      | 22        | DENY
      10.0.0.0/8  | 10.0.0.1   | TCP      | 22        | ALLOW (only internal network)
      0.0.0.0/0   | 0.0.0.0/0  | *        | *         | DENY  (default deny all)

    RULE: apply rules in order, first match wins.
    ```

    ---

    ## Stateless vs Stateful Firewalls

    ```
    STATELESS FIREWALL:
      Inspects each packet INDEPENDENTLY.
      No memory of previous packets.
      Rule: "Allow TCP port 443 inbound" -> allows every individual TCP packet
      on that port.

      Problem: TCP handshake has SYN, SYN-ACK, ACK.
      Stateless firewall allows all of them independently.
      But what about the RETURN traffic?
      If rule says "allow inbound port 443" but blocks "outbound ephemeral ports",
      the client response packet is blocked -> connection fails.
      Must manually add rules for both directions.

      USE: Simple switches, routers with basic ACLs. Very fast, low memory.

    STATEFUL FIREWALL:
      Tracks the STATE of network connections.
      Maintains a connection table (state table).

      TCP connection attempt:
        Outbound SYN (port 443) -> firewall records: {src:192.168.1.5,dst:8.8.8.8,
                                                        sport:54321,dport:443,state:SYN_SENT}
        Return SYN-ACK arrives  -> firewall checks table: IS this a response to an
                                   existing outbound connection? YES -> ALLOW automatically
        ACK sent -> state: ESTABLISHED
        FIN -> state: CLOSE_WAIT -> CLOSED -> entry removed from table

      Benefits:
        Only allow RETURN traffic for established connections (no need for inbound rules)
        Can detect port scanning (SYN flood without ACK = suspicious)
        TCP session hijacking detection
        Drops packets that aren't part of a valid connection

      USE: Modern production firewalls, cloud security groups (AWS SGs are stateful).

    COMPARISON:
      Stateless:  fast, no memory, simple rules, must allow both directions explicitly
      Stateful:   connection-aware, automatic return traffic, complex but safer
    ```

    ---

    ## Application Layer Firewall (Layer 7)

    ```
    Traditional firewalls: operate at OSI Layer 3-4 (IP/TCP).
    They see IP addresses and port numbers. They don't see inside the payload.

    Application Layer Firewall (Layer 7 / WAF - Web Application Firewall):
      Inspects the actual application content.

      WHAT IT CAN SEE AND BLOCK:
        HTTP request: "GET /admin' OR '1'='1 HTTP/1.1"  <- SQL injection in URL!
        HTTP body: <script>document.cookie</script>     <- XSS attack in form!
        HTTP headers: Host: internal-service.corp        <- SSRF attempt
        Rate: 10,000 identical requests from same IP     <- DDoS / scraping

      AWS WAF (Web Application Firewall) example rules:
        Block: requests matching SQL injection patterns
        Block: requests matching XSS patterns
        Block: requests from known malicious IPs (threat intel feed)
        Rate limit: > 2000 requests per IP per 5 minutes -> block for 1 hour
        Allow: only specific country codes (geo-restriction)

    LAYER COMPARISON:
      L3/L4 firewall: allows TCP port 443 -> sees encrypted HTTPS, can't inspect payload
      L7 WAF:         TLS terminates at WAF, can inspect decrypted HTTP, block attacks
    ```

    ---

    ## Cloud Security Groups vs NACLs (AWS Context)

    ```
    AWS SECURITY GROUPS (stateful, instance-level):
      Attached to EC2 instances, RDS, Lambda, ECS tasks.
      Rules apply per instance.
      Stateful: outbound response to allowed inbound is automatically allowed.

      Example SG for an app server:
        Inbound rules:
          TCP 443 from 0.0.0.0/0  (HTTPS from internet)
          TCP 22  from 10.0.0.0/8 (SSH from internal only)
        Outbound rules:
          TCP 5432 to sg-database-sg  (PostgreSQL to DB security group)
          TCP 443  to 0.0.0.0/0       (HTTPS outbound for API calls)
          All traffic to 0.0.0.0/0    (or lock down specifically)

    AWS NETWORK ACLs (stateless, subnet-level):
      Applied at subnet boundary (before reaching instances).
      Rules applied to all instances in the subnet.
      Stateless: must explicitly allow both inbound AND return traffic.
      Numbered rules: evaluated in order (100, 200, 300...) first match wins.
      Have DENY rules (security groups only have ALLOW).

      Use NACLs for:
        Blocking specific IPs/ranges at subnet level (DDoS mitigation)
        Compliance (broad-stroke deny rules)
        Subnet-wide policies

      Two-layer defense:
        NACL (subnet level) + Security Group (instance level)
        Attacker must bypass both.
    ```

    ---

    ## Demilitarized Zone (DMZ)

    ```
    A DMZ is a subnet that sits between the public internet and your internal
    private network. It contains services that MUST be publicly accessible
    but should not directly touch internal systems.

      INTERNET
          │
       [Firewall 1]   <- blocks everything except 80, 443
          │
       [DMZ subnet]
       [Web Server]   <- public-facing, handles HTTP requests
       [Load Balancer]
          │
       [Firewall 2]  <- blocks direct internet access to internal network
          │
       [Internal Network]
       [App Servers] [Databases]  <- private, no direct internet access

    If the web server is compromised: attacker is in DMZ, not internal network.
    Firewall 2 prevents lateral movement to databases and app servers.

    Modern cloud equivalent: public subnet (DMZ) + private subnet + NAT Gateway.
    ```

    ---

    ## Common Firewall Attacks and Defenses

    ```
    PORT SCANNING:
      Attacker sends SYN to all 65535 ports to discover open services.
      Defense: stateful firewall drops SYNs without follow-up ACK.
               Rate-limit new connection attempts per IP.
               Use intrusion detection system (IDS).

    SYN FLOOD (DDoS):
      Attacker sends millions of SYN packets, never completes handshake.
      Server's half-open connection table fills up. Legitimate connections rejected.
      Defense: SYN cookies (server generates cookie, doesn't store state until ACK).
               Rate limit SYN packets per source IP.
               AWS Shield / Cloudflare absorb volumetric attacks.

    IP SPOOFING:
      Attacker forges source IP to bypass IP-based allow rules.
      Defense: Ingress/egress filtering. Verify that packets from your network
               actually have your network's source IPs.

    FIREWALL BYPASS VIA ALLOWED PORT:
      Firewall allows port 443 (HTTPS). Attacker tunnels C2 (command and control)
      traffic over HTTPS to bypass firewall.
      Defense: Layer 7 inspection, behavior analysis, SSL inspection.
    ```

    ---

    ## Mind Map

    ```
    FIREWALLS
    |
    +-- PACKET FILTERING
    |   +-- Source/dest IP, port, protocol
    |   +-- First match wins
    |   +-- Default deny all (explicit allow)
    |
    +-- STATELESS vs STATEFUL
    |   +-- Stateless: each packet independent, must allow both directions
    |   +-- Stateful: connection state table, auto-allow return traffic
    |   +-- AWS Security Groups = stateful
    |
    +-- LAYERS
    |   +-- L3/L4: IP + TCP (ports, IPs)
    |   +-- L7 WAF: HTTP payload (SQLi, XSS, rate limiting)
    |
    +-- AWS CONSTRUCTS
    |   +-- Security Groups (stateful, instance-level, allow only)
    |   +-- NACLs (stateless, subnet-level, allow + deny)
    |
    +-- NETWORK ZONES
        +-- DMZ (public-facing services isolated from internal)
        +-- Public subnet + private subnet + NAT
    ```

    ---

    ## References

    ### Videos
    - **Firewalls and Network Security** by PowerCert Animated Videos:
      https://www.youtube.com/watch?v=kDEX1HXybrU
      - 10 minutes. Animated firewall concepts from scratch.
    - **AWS Security Groups vs NACLs** by StephaneMaarek:
      https://www.youtube.com/watch?v=ttc0b2NZTV0
      - AWS-specific comparison with diagrams.

    ### Articles
    - **AWS Security Groups docs**: https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html
    - **OWASP WAF guide**: https://owasp.org/www-community/Web_Application_Firewall
    """

    FIREWALLS_Q = [
        {"id":"fw-q4","type":"mcq","prompt":"What is a stateful firewall?",
         "choices":["A firewall with a database","A firewall that tracks the state of active connections — allows return traffic automatically for established connections, detects port scans",
                    "A cloud firewall only","A firewall with logging"],
         "answerIndex":1,"explanation":"Stateful firewall maintains a connection table. Outbound TCP to port 443: table entry created. Return SYN-ACK: firewall checks table, sees valid return, auto-allows. Stateless must have explicit rules for both directions. AWS Security Groups are stateful.","tags":["firewalls","stateful"]},
        {"id":"fw-q5","type":"mcq","prompt":"What is the difference between AWS Security Groups and Network ACLs?",
         "choices":["They are identical","Security Groups: stateful, instance-level, ALLOW rules only. NACLs: stateless, subnet-level, ALLOW + DENY rules, evaluated in numbered order.",
                    "NACLs are per-instance","Security Groups are stateless"],
         "answerIndex":1,"explanation":"SG: attached to instances, stateful (return traffic auto-allowed), only allow rules, last-match semantics actually all rules evaluate. NACL: applied to entire subnet, stateless (must explicitly allow return), allow AND deny rules, numbered order (first match).","tags":["firewalls","aws","security-groups","nacl"]},
        {"id":"fw-q6","type":"mcq","prompt":"What is a WAF (Web Application Firewall)?",
         "choices":["A wireless access firewall","Layer 7 firewall that inspects HTTP content — blocks SQL injection, XSS, rate abuse, known attack patterns",
                    "A network switch","A VPN endpoint"],
         "answerIndex":1,"explanation":"WAF decrypts HTTPS, inspects HTTP request/response. Rules: block requests matching SQL injection patterns, XSS payloads, known malicious user agents. Rate limit IPs. Geo-block countries. AWS WAF, Cloudflare WAF, ModSecurity are common. Layer 3/4 firewalls cannot see inside encrypted HTTPS.","tags":["firewalls","waf","layer7"]},
        {"id":"fw-q7","type":"mcq","prompt":"What is a DMZ (Demilitarized Zone) in network security?",
         "choices":["A zone with no firewall","A subnet between the internet and internal network — contains public-facing servers (web, load balancer). Separate firewall protects internal network from DMZ.",
                    "A database isolation zone","A VPN tunnel"],
         "answerIndex":1,"explanation":"DMZ: public web servers live here (must face internet). Internal app servers and databases live in private network behind second firewall. If web server is compromised: attacker is in DMZ, not internal network. Two firewalls = two layers of protection.","tags":["firewalls","dmz","network-zones"]},
        {"id":"fw-q8","type":"mcq","prompt":"What is a SYN flood attack and how do firewalls defend against it?",
         "choices":["Flooding with legitimate traffic","Attacker sends millions of SYN packets without completing TCP handshake — fills server's half-open connection table. Defense: SYN cookies, rate limiting SYN packets per source IP.",
                    "DNS amplification attack","ICMP flood"],
         "answerIndex":1,"explanation":"SYN flood: server allocates state for each SYN waiting for ACK. 1M SYNs from spoofed IPs: table exhausted, real users get connection refused. SYN cookies: server encodes state in the SYN-ACK sequence number instead of storing it. No table entry until ACK arrives with valid cookie.","tags":["firewalls","syn-flood","ddos"]},
        {"id":"fw-q9","type":"mcq","prompt":"What is default-deny in firewall rules?",
         "choices":["Block traffic by default during maintenance","Final rule that blocks ALL traffic not explicitly allowed — forces security by explicit permission rather than explicit blocking",
                    "Deny all internal traffic","Cloud provider blocks all by default"],
         "answerIndex":1,"explanation":"Default-deny: last rule = DENY ALL. Every service you need must be explicitly opened. Principle of least privilege at network level. Alternative (default-allow) is dangerous: must explicitly block every bad IP/port, impossible to enumerate all threats. AWS Security Groups: default deny (no inbound allowed unless explicitly added).","tags":["firewalls","default-deny","security"]},
        {"id":"fw-q10","type":"mcq","prompt":"Why are AWS Security Groups preferred over NACLs for most use cases?",
         "choices":["NACLs are deprecated","Security Groups are stateful (return traffic auto-allowed), attached per-instance (granular), and use only ALLOW rules (simpler). NACLs are stateless (must manage return traffic), subnet-wide (less granular), but can DENY.",
                    "Security Groups are faster","NACLs cost more"],
         "answerIndex":1,"explanation":"SG: create inbound rule TCP 5432 from app-sg -> return traffic automatic. NACL: need inbound rule TCP 5432 from app-subnet AND outbound rule TCP 1024-65535 to app-subnet (ephemeral port range). SGs are simpler. Use NACLs for: subnet-level IP blocking (DDoS mitigation) or compliance DENY rules.","tags":["firewalls","aws","security-groups"]},
        {"id":"fw-q11","type":"mcq","prompt":"What OSI layer do traditional packet-filtering firewalls operate at?",
         "choices":["Layer 7 (Application)","Layer 5 (Session)","Layer 3-4 (Network/Transport) — can inspect IP addresses, TCP ports, protocols but not application payload inside encrypted connections",
                    "Layer 1 (Physical)"],
         "answerIndex":2,"explanation":"L3 (IP): filter by source/dest IP. L4 (TCP/UDP): filter by port, TCP flags. Cannot see what's inside TCP payload (especially when encrypted with TLS). WAF (L7): TLS terminated, full visibility into HTTP request. Choose based on what inspection depth is needed.","tags":["firewalls","osi","layers"]},
        {"id":"fw-q12","type":"mcq","prompt":"What is egress filtering in firewall rules?",
         "choices":["Filtering incoming traffic only","Controlling OUTBOUND traffic from your network — prevents compromised servers from phoning home to attacker C2, limits data exfiltration",
                    "Encryption of outbound data","A VPN technology"],
         "answerIndex":1,"explanation":"Most orgs focus on inbound (block attackers). Egress filtering = control what goes OUT. Compromised server tries to connect to attacker's C2 server: egress firewall blocks (only allow known outbound: 443 to known CDNs/APIs). Limits blast radius of compromise.","tags":["firewalls","egress"]},
        {"id":"fw-q13","type":"mcq","prompt":"What is IP whitelisting vs blacklisting in firewall rules?",
         "choices":["They are identical security approaches","Whitelist: allow ONLY specific IPs (default deny all others). Blacklist: deny SPECIFIC IPs (allow everything else). Whitelist is more secure but requires maintenance.",
                    "Blacklisting is always better","Whitelisting only works for IPv4"],
         "answerIndex":1,"explanation":"Whitelist (allowlist): allow IPs 1.2.3.4 and 4.5.6.7, deny all others. Safe default. Hard to maintain (must update when IPs change). Blacklist (denylist): deny known bad IPs. Easier but reactive (must keep up with new threats). Principle: whitelist internal APIs, deny-all external, whitelist specific CDN/partner IPs.","tags":["firewalls","whitelist","blacklist"]},
        {"id":"fw-q14","type":"mcq","prompt":"What is a next-generation firewall (NGFW)?",
         "choices":["A firewall from the future","Combines traditional stateful firewall with deep packet inspection, application awareness, intrusion prevention (IPS), and TLS inspection",
                    "A cloud-only firewall","A firewall with AI"],
         "answerIndex":1,"explanation":"NGFW: all of stateful L3/L4 + application identification (is this Facebook? TikTok? Zoom? regardless of port) + IPS (detect and block attack patterns) + SSL/TLS inspection (decrypt, inspect, re-encrypt) + user identification (block specific users, not just IPs). Palo Alto, Fortinet, Cisco Firepower are NGFW vendors.","tags":["firewalls","ngfw"]},
        {"id":"fw-q15","type":"mcq","prompt":"What port and protocol should almost always be blocked from public internet to databases?",
         "choices":["Port 443 (HTTPS)","Port 80 (HTTP)","Database ports (5432 PostgreSQL, 3306 MySQL, 27017 MongoDB) should NEVER be reachable from public internet — databases belong in private subnets only",
                    "Port 53 (DNS)"],
         "answerIndex":2,"explanation":"Databases in public subnets with open ports: attackers can attempt direct connections. Default postgres password? Compromised instantly. Databases MUST be in private subnets. Only app servers (in same VPC) connect via security group rule. Firewall rule: PostgreSQL port accessible only from app-server security group.","tags":["firewalls","database","security"]},
        {"id":"fw-q16","type":"mcq","prompt":"What is intrusion detection vs intrusion prevention (IDS vs IPS)?",
         "choices":["They are identical","IDS: monitors and ALERTS on suspicious traffic (passive). IPS: monitors and ACTIVELY BLOCKS suspicious traffic (inline). IPS is in the traffic path, IDS is a copy.",
                    "IDS is newer","IPS requires hardware"],
         "answerIndex":1,"explanation":"IDS: receives a copy of traffic (port mirror), analyzes, sends alerts. If it misses something: no impact (it's just monitoring). IPS: sits inline in traffic path, drops suspicious packets. If it false-positives: legitimate traffic blocked. Most NGFWs combine IDS+IPS modes.","tags":["firewalls","ids","ips"]},
        {"id":"fw-q17","type":"mcq","prompt":"What is TLS/SSL inspection by a firewall?",
         "choices":["Blocking all HTTPS traffic","Firewall acts as man-in-the-middle: decrypts TLS, inspects plaintext HTTP, re-encrypts. Requires installing firewall's CA cert as trusted on client machines.",
                    "A VPN protocol","Encrypting firewall logs"],
         "answerIndex":1,"explanation":"Without TLS inspection: WAF/NGFW sees encrypted blob. Can't detect SQLi/XSS in HTTPS. SSL inspection: firewall has certificate authority cert. Decrypts client's HTTPS, inspects, re-encrypts with real server cert (signed by firewall CA). Client must trust firewall CA. Common in corporate networks.","tags":["firewalls","tls","inspection"]},
        {"id":"fw-q18","type":"mcq","prompt":"What is the principle of least privilege applied to firewall rules?",
         "choices":["Grant all access then revoke","Allow only the minimum network access needed for each service to function. App server: needs port 5432 to DB, port 443 outbound for APIs. Nothing else needed = nothing else allowed.",
                    "Use default-allow for convenience","Share security groups across all services"],
         "answerIndex":1,"explanation":"Least privilege at network level: each security group allows only the specific ports and sources it needs. App server SG: inbound 443 from ALB-SG only, outbound 5432 to DB-SG only, outbound 443 to 0.0.0.0/0. Not: all traffic allowed. Limits lateral movement if server is compromised.","tags":["firewalls","least-privilege","security"]},
        {"id":"fw-q19","type":"mcq","prompt":"What is a bastion host (jump server)?",
         "choices":["A high-availability server","A hardened entry point for SSH access to private subnet servers — the only server with SSH port 22 open from internet, all other servers only allow SSH from bastion IP",
                    "A database server","A load balancer"],
         "answerIndex":1,"explanation":"Bastion: port 22 open only from specific IPs (office IP, engineer home IPs). Internal servers: port 22 open only from bastion's security group. To access internal server: SSH to bastion -> SSH from bastion to internal server. Reduces attack surface to one hardened host with MFA/audit logging.","tags":["firewalls","bastion","ssh"]},
        {"id":"fw-q20","type":"mcq","prompt":"How does a Security Group reference work in AWS (source = another SG)?",
         "choices":["Only IP ranges can be sources","A Security Group rule with source = another SG ID allows traffic from any resource with that SG attached, regardless of IP — auto-updates as instances scale",
                    "SG references require static IPs","SG references are deprecated"],
         "answerIndex":1,"explanation":"RDS SG inbound rule: source = app-server-sg. ANY EC2 with app-server-sg attached can connect. New EC2 added to auto-scaling group? It gets app-server-sg automatically, immediately can reach RDS. Better than IP-based: IPs change as instances scale. SG-to-SG references are the correct AWS pattern.","tags":["firewalls","aws","security-groups"]},
    ]

    FIREWALLS_FC = [
        {"id":"fw-fc4","front":"Stateful vs stateless firewall","back":"Stateless: per-packet decision, no memory, must allow both directions. Stateful: tracks connections in state table, return traffic auto-allowed, detects port scans. AWS Security Groups = stateful. NACLs = stateless.","tags":["firewalls","stateful"]},
        {"id":"fw-fc5","front":"AWS Security Group vs NACL","back":"SG: stateful, per-instance, ALLOW rules only, SG-to-SG references. NACL: stateless, per-subnet, ALLOW+DENY, numbered order. Use SG for most. Use NACL for: subnet-level IP blocking, compliance DENY rules, DDoS mitigation.","tags":["firewalls","aws"]},
        {"id":"fw-fc6","front":"WAF vs traditional firewall","back":"L3/L4 firewall: filters by IP, port, protocol. Cannot see inside TLS. WAF (L7): decrypts HTTPS, inspects HTTP payload, blocks SQLi/XSS/bots, rate limits by IP/user. Run both: firewall for network control, WAF for application protection.","tags":["firewalls","waf"]},
        {"id":"fw-fc7","front":"Default-deny principle","back":"Last rule = DENY ALL. Only explicitly opened ports/IPs are allowed. Principle of least privilege at network level. AWS SG default: deny all inbound, allow all outbound. Best practice: also lock down outbound (egress filtering).","tags":["firewalls","default-deny"]},
        {"id":"fw-fc8","front":"Database firewall rule","back":"NEVER open DB ports (5432, 3306, 27017) to internet. RDS SG inbound: allow TCP 5432 from app-server-sg ONLY. DB in private subnet (no public IP). App server connects via private VPC network. Bastion for admin access.","tags":["firewalls","database","aws"]},
    ]

    d['guide'] = FIREWALLS_GUIDE
    existing_ids = {q['id'] for q in d['questions']}
    for q in FIREWALLS_Q:
        if q['id'] not in existing_ids:
            d['questions'].append(q)
    existing_fc_ids = {fc['id'] for fc in d['flashcards']}
    for fc in FIREWALLS_FC:
        if fc['id'] not in existing_fc_ids:
            d['flashcards'].append(fc)
    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"firewalls.json: guide={len(FIREWALLS_GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ─────────────────────────────────────────────────────────────────────────────
    # PROXIES
    # ─────────────────────────────────────────────────────────────────────────────
    p = BASE / 'proxies.json'
    d = json.loads(p.read_text())

    PROXIES_GUIDE = """# Proxies — Forward and Reverse

    ## What Is a Proxy? Zero to Clear

    A proxy is a server that acts as an **intermediary** between a client and another server.
    The client doesn't communicate directly with the destination — it talks to the proxy,
    and the proxy makes the request on the client's behalf.

    **Why use a proxy?**
    ```
    Direct connection:
      Client ──────────────────────────► Server
      Client's IP exposed to server

    Via proxy:
      Client ──► Proxy ──────────────► Server
      Server sees proxy's IP, not client's IP
      Proxy can: inspect, filter, cache, transform, log requests
    ```

    Two completely different types exist, and they're often confused:
    - **Forward Proxy** — on behalf of the CLIENT (client-side)
    - **Reverse Proxy** — on behalf of the SERVER (server-side)

    ---

    ## Forward Proxy — On Behalf of Clients

    ```
    POSITION: Client side (between clients and the internet)

    HOW IT WORKS:
      Client is configured to send all requests to the proxy.
      Proxy makes the actual request to the internet.
      Server sees proxy's IP, not client's IP.

      Employee's PC ──► Forward Proxy ──► Internet (google.com, facebook.com)
      Employee's PC ──► Forward Proxy ──► BLOCKED (social media)

    USE CASES:

    1. CORPORATE INTERNET FILTER:
       All employee traffic routed through proxy.
       Proxy enforces: block adult sites, social media, known malware sites.
       Log all internet activity for compliance.
       Companies: Zscaler, Bluecoat, Squid proxy.

    2. CONTENT CACHING:
       Many employees watch the same YouTube training video.
       Without cache: 100 employees = 100 requests to YouTube = 100x bandwidth.
       Proxy caches the video. 100 employees = 1 request to YouTube.
       Saves bandwidth, speeds up repeated access.

    3. ANONYMISATION:
       VPN and Tor are types of forward proxies.
       Your ISP sees traffic going to proxy, not to the destination site.
       Destination site sees proxy's IP, not yours.
       Bypasses geo-restrictions.

    4. EGRESS CONTROL:
       All outbound traffic from servers goes through proxy.
       Audit log of every external API call.
       Block unexpected destinations (DLP - Data Loss Prevention).
    ```

    ---

    ## Reverse Proxy — On Behalf of Servers

    ```
    POSITION: Server side (between the internet and backend servers)

    HOW IT WORKS:
      Client thinks it's talking to the destination server.
      Actually talking to the reverse proxy.
      Proxy forwards to backend server(s).

      Browser ──► Reverse Proxy ──► App Server 1
      (thinks it's         │──────── App Server 2
       talking to          └──────── App Server 3
       myapp.com)

    THE CLIENT NEVER KNOWS the backend server exists.
    The backend server's IP/port is hidden.

    USE CASES:

    1. LOAD BALANCING:
       Reverse proxy distributes requests across multiple backend servers.
       Algorithms: round-robin, least connections, IP hash.
       nginx: upstream { server backend1; server backend2; server backend3; }

    2. TLS TERMINATION:
       HTTPS from browser -> Reverse proxy (decrypt TLS) -> HTTP to backends
       Backend servers: don't need TLS certificates or TLS overhead.
       Single cert at edge. Central cert management.

    3. CACHING:
       Proxy caches backend responses.
       GET /api/products -> cached for 60s -> 1000 requests = 1 backend call.
       Varnish, nginx cache, Cloudflare Edge are reverse proxy caches.

    4. COMPRESSION:
       Proxy compresses responses before sending to client.
       Backend returns uncompressed JSON, proxy compresses with gzip/brotli.
       50-70% bandwidth savings.

    5. SECURITY / RATE LIMITING:
       Proxy applies rate limits before requests reach backend.
       DDoS: proxy absorbs/blocks attack traffic before it hits app servers.
       IP blocking, WAF rules at proxy level.
       Backend servers never exposed to internet (only proxy's IP is public).

    6. CANARY DEPLOYMENTS:
       5% of traffic -> new version (Canary)
       95% of traffic -> old stable version
       Monitor canary for errors before full rollout.
       All handled at proxy routing level.
    ```

    ---

    ## Nginx — The Most Common Reverse Proxy

    ```nginx
    # nginx as reverse proxy with load balancing

    upstream backend_servers {
        server 10.0.1.10:8080;
        server 10.0.1.11:8080;
        server 10.0.1.12:8080;
        # least_conn;  # least-connections algorithm
    }

    server {
        listen 443 ssl;
        server_name myapp.com;

        ssl_certificate /etc/ssl/myapp.crt;   # TLS termination here
        ssl_certificate_key /etc/ssl/myapp.key;

        # Rate limiting zone
        limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;

        location /api/ {
            limit_req zone=api;                # apply rate limit
            proxy_pass http://backend_servers; # forward to backends
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;   # pass client IP
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location /static/ {
            root /var/www;                # serve static files directly
            expires 1y;                   # cache-control header
            add_header Cache-Control "public, immutable";
        }
    }
    ```

    ---

    ## Forward Proxy vs Reverse Proxy — Side by Side

    ```
    +------------------+----------------------+----------------------+
    | Aspect           | Forward Proxy        | Reverse Proxy        |
    +------------------+----------------------+----------------------+
    | Position         | Client side          | Server side          |
    | Configured by    | Client/network admin | Server/DevOps        |
    | Client awareness | Client is configured | Client unaware       |
    |                  | to use it            | (thinks it's server) |
    | Server awareness | Server unaware       | Server unaware       |
    |                  | (sees proxy IP)      | (sees proxy, not client)|
    | Primary uses     | Content filter,      | Load balancing,      |
    |                  | caching, anonymity,  | TLS termination,     |
    |                  | access control       | caching, WAF         |
    | Examples         | Squid, Zscaler, VPN  | Nginx, HAProxy,      |
    |                  |                      | Cloudflare, AWS ALB  |
    +------------------+----------------------+----------------------+

    MEMORY TRICK:
      Forward proxy: client's FRIEND (helps client reach internet)
      Reverse proxy: server's FRIEND (helps server handle client requests)
    ```

    ---

    ## Service Mesh — Modern Microservices Proxy

    ```
    In microservices, every service-to-service call can benefit from a proxy.
    Service Mesh adds a sidecar proxy to every pod/container.

      Service A ──► Sidecar A ──── [network] ──── Sidecar B ──► Service B

    Sidecar handles:
      mTLS (mutual TLS between services, zero-trust networking)
      Retries (with exponential backoff)
      Circuit breakers (stop calling downstream if it's failing)
      Load balancing (between service instances)
      Observability (metrics, traces for every service call)

    The services themselves don't know about TLS, retries, or load balancing.
    The mesh handles it transparently.

    Examples: Istio, Linkerd, Consul Connect, AWS App Mesh

    TRADE-OFF: added complexity, latency overhead of extra proxy hop.
    Best for: large microservices with 50+ services where cross-cutting
    concerns (mTLS, observability, retries) are painful to implement everywhere.
    ```

    ---

    ## Mind Map

    ```
    PROXIES
    |
    +-- FORWARD PROXY (client-side)
    |   +-- Client configured to route through proxy
    |   +-- Server sees proxy IP not client
    |   +-- Uses: content filter, caching, VPN/anonymity, egress control
    |   +-- Examples: Squid, Zscaler, VPN
    |
    +-- REVERSE PROXY (server-side)
    |   +-- Client unaware (thinks it's talking to backend)
    |   +-- Uses: load balancing, TLS termination, caching, rate limiting
    |   +-- Canary deployments, WAF
    |   +-- Examples: Nginx, HAProxy, Cloudflare, AWS ALB
    |
    +-- SERVICE MESH
        +-- Sidecar proxy per service
        +-- mTLS, retries, circuit breakers, observability
        +-- Istio, Linkerd
    ```

    ---

    ## References

    ### Videos
    - **Proxy vs Reverse Proxy Explained** by ByteByteGo:
      https://www.youtube.com/watch?v=SqqrOspasag
      - Visual animation of both types with real examples.
    - **Nginx Tutorial for Beginners** by TechWorld with Nana:
      https://www.youtube.com/watch?v=iInUBOVeBCc
      - nginx as reverse proxy, load balancer, TLS termination.

    ### Articles
    - **Nginx reverse proxy guide**: https://nginx.org/en/docs/http/ngx_http_proxy_module.html
    - **HAProxy documentation**: https://www.haproxy.com/documentation/
    """

    PROXIES_Q = [
        {"id":"proxy-q4","type":"mcq","prompt":"What does a forward proxy do?",
         "choices":["Routes traffic from servers to clients","Acts on behalf of CLIENTS — client routes requests through proxy, server sees proxy IP not client IP. Used for: content filtering, caching, VPN/anonymity",
                    "Balances load across servers","Terminates TLS"],
         "answerIndex":1,"explanation":"Forward proxy: intercepts client outbound requests. Corporate: all employees route through proxy -> company can filter sites, cache content, log all requests. VPN: your traffic goes to VPN server (forward proxy) -> destination sees VPN IP. Client must be configured to use it.","tags":["proxies","forward-proxy"]},
        {"id":"proxy-q5","type":"mcq","prompt":"What does a reverse proxy do?",
         "choices":["Routes traffic back to clients","Acts on behalf of SERVERS — sits in front of backends, clients think they're talking directly to the destination. Used for: load balancing, TLS termination, caching",
                    "Encrypts client requests","DNS resolution"],
         "answerIndex":1,"explanation":"Reverse proxy: client sends request to myapp.com. Actually hits nginx (reverse proxy). Nginx forwards to one of 3 backend servers. Client never knows about backends. Server team controls proxy, not clients. Backend IP/port completely hidden from internet.","tags":["proxies","reverse-proxy"]},
        {"id":"proxy-q6","type":"mcq","prompt":"What is TLS termination at a reverse proxy?",
         "choices":["Blocking TLS connections","Reverse proxy handles the HTTPS encryption/decryption. Browser speaks HTTPS to proxy. Proxy decrypts, sends plain HTTP to backends. Backends don't need TLS certificates.",
                    "A VPN protocol","TLS compression"],
         "answerIndex":1,"explanation":"TLS termination: HTTPS to proxy -> proxy decrypts -> HTTP to backends. Benefits: single cert management (proxy), no TLS overhead on app servers (CPU-intensive), backends use faster plain HTTP internally. Backend still in private subnet so plain HTTP is safe.","tags":["proxies","tls","reverse-proxy"]},
        {"id":"proxy-q7","type":"mcq","prompt":"What is the X-Forwarded-For header and why is it needed with reverse proxies?",
         "choices":["Security authentication header","Reverse proxy adds original client IP to this header — without it, backend servers see only proxy IP, losing the real client IP for logging/rate limiting",
                    "Cache control header","Load balancer routing header"],
         "answerIndex":1,"explanation":"Backend sees traffic from proxy IP (10.0.0.1) not client. X-Forwarded-For: 203.0.113.45 = original client IP forwarded by proxy. Backend reads this for: audit logs ('user from IP 203.x clicked...'), rate limiting by real IP, geo-IP lookup, abuse detection.","tags":["proxies","x-forwarded-for","headers"]},
        {"id":"proxy-q8","type":"mcq","prompt":"What is the key difference between a forward and reverse proxy?",
         "choices":["Forward is faster","Forward proxy: client-side, client configured to use it, hides client from server. Reverse proxy: server-side, client unaware, hides server from client.",
                    "They are identical","Reverse proxy is newer"],
         "answerIndex":1,"explanation":"Memory trick: Forward = client's friend (helps client reach internet). Reverse = server's friend (helps server handle clients). Forward: client knows about proxy. Reverse: client thinks proxy IS the server. Both sit in the middle, but from different perspectives.","tags":["proxies","comparison"]},
        {"id":"proxy-q9","type":"mcq","prompt":"What is a canary deployment using a reverse proxy?",
         "choices":["Testing with canary bird metaphor","Route a small percentage (e.g., 5%) of traffic to new version, 95% to stable. If new version has high errors: stop rollout. If clean: gradually increase.",
                    "Blue-green deployment","A/B testing for UI"],
         "answerIndex":1,"explanation":"Canary: nginx upstream weight=5 for new version, weight=95 for old. 5 out of 100 requests hit new version. Monitor: error rate, latency, business metrics. If metrics look good: increase to 20%, 50%, 100%. Roll back instantly (update nginx config) if problems. Zero downtime.","tags":["proxies","canary","deployment"]},
        {"id":"proxy-q10","type":"mcq","prompt":"What role does Cloudflare play as a proxy?",
         "choices":["DNS registrar only","Reverse proxy and CDN at scale — traffic to myapp.com hits Cloudflare edge first. Cloudflare: DDoS protection, WAF, TLS, caching, load balancing, performance optimization",
                    "A forward proxy","A VPN service"],
         "answerIndex":1,"explanation":"Cloudflare: when you proxy DNS through Cloudflare, ALL traffic hits Cloudflare edge first. Cloudflare: absorbs DDoS (up to Tbps), applies WAF rules, caches static assets, terminates TLS. Origin server (your server) never exposed to raw internet attacks. Origin IP hidden.","tags":["proxies","cloudflare","cdn"]},
        {"id":"proxy-q11","type":"mcq","prompt":"What is a service mesh sidecar proxy?",
         "choices":["A proxy running alongside the main process in each pod — handles mTLS, retries, circuit breaking, observability without modifying application code",
                    "A proxy for database connections","A hardware load balancer","A database connection pool"],
         "answerIndex":0,"explanation":"Service mesh: inject Envoy/Linkerd proxy as sidecar in every pod. App calls localhost:8080 -> sidecar intercepts, applies mTLS + retries + circuit breaker + traces -> forwards to destination sidecar. App code: zero changes. Cross-cutting concerns handled by mesh.","tags":["proxies","service-mesh","microservices"]},
        {"id":"proxy-q12","type":"mcq","prompt":"What is a transparent proxy?",
         "choices":["A proxy that is invisible to traffic","A proxy that intercepts network traffic WITHOUT requiring client configuration — network routes traffic through proxy automatically (common in ISPs and corporate networks)",
                    "A proxy with no caching","A proxy that doesn't modify requests"],
         "answerIndex":1,"explanation":"Transparent (intercepting) proxy: at network level (NAT rules or BGP), traffic is redirected to proxy. Client: no configuration needed. Proxy: gets traffic it didn't explicitly receive. Used by: ISPs (traffic caching), corporate networks (content filtering without per-machine config), CDNs.","tags":["proxies","transparent"]},
        {"id":"proxy-q13","type":"mcq","prompt":"HAProxy vs Nginx — when to use each as a reverse proxy?",
         "choices":["Always use nginx","HAProxy: Layer 4 (TCP) and Layer 7 load balancing, extreme performance, wire-speed. Nginx: HTTP reverse proxy, serving static files, SSL termination, flexible config. Both excellent for HTTP.",
                    "HAProxy is deprecated","Nginx only for static files"],
         "answerIndex":1,"explanation":"HAProxy: pure load balancer/proxy, extremely fast, Layer 4 (non-HTTP protocols like PostgreSQL, Redis proxying), extensive health checking. Nginx: web server + reverse proxy + cache + static files. For HTTP load balancing: both are excellent. HAProxy often marginally faster for pure proxying.","tags":["proxies","nginx","haproxy"]},
        {"id":"proxy-q14","type":"mcq","prompt":"What does proxy caching do for API responses?",
         "choices":["Caches client-side only","Reverse proxy stores API response for a TTL. Identical requests within TTL served from cache without hitting backend — 1000 identical API calls = 1 backend call.",
                    "Caches database queries","Proxy caching requires Redis"],
         "answerIndex":1,"explanation":"nginx proxy_cache: GET /api/products -> response stored for 60s. Next 999 identical requests: served from nginx cache. Backend receives only 1 request per 60s. Massively reduces backend load for read-heavy public APIs (product listings, leaderboards). Only cache: identical, public, GET requests.","tags":["proxies","caching"]},
        {"id":"proxy-q15","type":"mcq","prompt":"What is connection pooling in a reverse proxy database proxy?",
         "choices":["Storing database backups","Proxy maintains a pool of persistent DB connections. App servers connect to proxy (thousands of connections). Proxy multiplexes onto fewer real DB connections (DB has connection limit).",
                    "Caching query results","Encrypting DB connections"],
         "answerIndex":1,"explanation":"PgBouncer (PostgreSQL proxy): DB handles 100 connections max. 10 app servers * 100 threads = 1000 DB connections needed. PgBouncer: 1000 app connections -> pool of 50 real DB connections (multiplexed). App servers connect to PgBouncer as if it's PostgreSQL. DB stays healthy.","tags":["proxies","connection-pool","database"]},
        {"id":"proxy-q16","type":"mcq","prompt":"What is Envoy proxy and where is it commonly used?",
         "choices":["A VPN client","High-performance proxy/sidecar developed by Lyft — used as the data plane in Istio service mesh, AWS App Mesh. Handles L4/L7 proxying, mTLS, circuit breaking, distributed tracing",
                    "A CDN","A database proxy"],
         "answerIndex":1,"explanation":"Envoy: C++ proxy, ~1ms overhead per call. Istio uses Envoy sidecars: one per pod. Envoy handles: load balancing, TLS termination, connection pooling, retries, circuit breaking, observability (xDS API). Configured by Istio control plane. The de facto sidecar proxy standard.","tags":["proxies","envoy","service-mesh"]},
        {"id":"proxy-q17","type":"mcq","prompt":"What is an API Gateway vs a reverse proxy?",
         "choices":["They are identical","API Gateway: reverse proxy with additional features — authentication, authorization, rate limiting, API key management, request/response transformation, developer portal. Reverse proxy: simpler forwarding.",
                    "API Gateway is client-side","Reverse proxy does authentication"],
         "answerIndex":1,"explanation":"Reverse proxy: forward request to backend. API Gateway (Kong, AWS API Gateway, nginx + plugins): authenticate JWT, check API keys, rate limit by user/plan, transform request (add headers, modify body), route to microservices, provide developer docs. Purpose-built for API management.","tags":["proxies","api-gateway"]},
        {"id":"proxy-q18","type":"mcq","prompt":"What is the security benefit of a reverse proxy for backend servers?",
         "choices":["Backend servers become faster","Backend server IP and port never exposed to internet. Only proxy IP is public. Attacker cannot directly connect to backend. DDoS hits proxy (which can absorb it), not the application server.",
                    "Reverse proxy adds authentication","Removes need for firewall"],
         "answerIndex":1,"explanation":"Backend in private subnet + reverse proxy in public subnet: attacker knows myapp.com IP = proxy IP. Backend IP: unknown, unreachable. Direct attack on DB port: impossible (proxy doesn't forward to DB). DDoS the app: absorbed by proxy/CDN/WAF. Backend handles only valid forwarded traffic.","tags":["proxies","security","backend"]},
        {"id":"proxy-q19","type":"mcq","prompt":"What is CONNECT method in HTTP and how is it related to forward proxies?",
         "choices":["A REST API method","HTTP CONNECT: client asks forward proxy to establish a TCP tunnel to a destination. Used for HTTPS through HTTP proxy — proxy tunnels encrypted traffic without decrypting it.",
                    "A WebSocket handshake","A gRPC method"],
         "answerIndex":1,"explanation":"CONNECT example: client sends 'CONNECT google.com:443 HTTP/1.1' to proxy. Proxy opens TCP to google.com:443, sends '200 Connection established'. Now client speaks directly to Google through the TCP tunnel (encrypted). Proxy can't inspect HTTPS content via CONNECT (just tunneling bytes).","tags":["proxies","http-connect","tunnel"]},
        {"id":"proxy-q20","type":"mcq","prompt":"What is mTLS (mutual TLS) in a service mesh context?",
         "choices":["A faster version of TLS","Both sides authenticate with certificates — service A proves to service B that it is who it claims (not just server proving identity to client). Zero-trust networking between microservices.",
                    "Multiple TLS certificates","Load balancing with TLS"],
         "answerIndex":1,"explanation":"Standard TLS: server proves identity (certificate), client trusts. mTLS: BOTH prove identity. Service A has cert issued by internal CA. Service B has cert. On connection: both verify each other's cert. Sidecar proxy automated cert rotation. Even if internal network is compromised: only verified services can talk to each other.","tags":["proxies","mtls","zero-trust"]},
    ]

    PROXIES_FC = [
        {"id":"proxy-fc4","front":"Forward vs reverse proxy memory trick","back":"Forward proxy: CLIENT's friend. Client configured to use it. Hides client from server. Use: content filter, VPN, anonymous browsing. Reverse proxy: SERVER's friend. Client unaware. Hides server from client. Use: load balancing, TLS, caching, WAF.","tags":["proxies","comparison"]},
        {"id":"proxy-fc5","front":"Reverse proxy capabilities","back":"Load balancing (round-robin/least-conn). TLS termination (cert at proxy, plain HTTP to backends). Response caching. Compression. Rate limiting. WAF/security rules. Canary routing (% traffic to new version). Single entry point hides all backends.","tags":["proxies","reverse-proxy"]},
        {"id":"proxy-fc6","front":"X-Forwarded-For header","back":"Without: backend sees proxy IP for all requests (can't log real users, can't rate-limit by real IP). With X-Forwarded-For: proxy adds client real IP in header. Backend reads header for logging, geolocation, rate limiting. Also: X-Real-IP, Forwarded (RFC 7239 standard).","tags":["proxies","x-forwarded-for"]},
        {"id":"proxy-fc7","front":"Service mesh vs reverse proxy","back":"Reverse proxy: external traffic to backend. Service mesh: service-to-service internal traffic. Sidecar per pod. Auto mTLS, retries, circuit breaking, distributed tracing. Istio/Linkerd. Use for 50+ microservices where cross-cutting concerns need consistency.","tags":["proxies","service-mesh"]},
        {"id":"proxy-fc8","front":"Nginx reverse proxy config pattern","back":"upstream block: list backend servers. location block: proxy_pass to upstream. proxy_set_header X-Real-IP, X-Forwarded-For. limit_req for rate limiting. ssl_certificate for TLS termination. Static files served directly (no proxy). Cache with proxy_cache.","tags":["proxies","nginx"]},
    ]

    d['guide'] = PROXIES_GUIDE
    existing_ids = {q['id'] for q in d['questions']}
    for q in PROXIES_Q:
        if q['id'] not in existing_ids:
            d['questions'].append(q)
    existing_fc_ids = {fc['id'] for fc in d['flashcards']}
    for fc in PROXIES_FC:
        if fc['id'] not in existing_fc_ids:
            d['flashcards'].append(fc)
    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"proxies.json: guide={len(PROXIES_GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ─────────────────────────────────────────────────────────────────────────────
    # WEBSOCKETS
    # ─────────────────────────────────────────────────────────────────────────────
    p = BASE / 'websockets.json'
    d = json.loads(p.read_text())

    WS_GUIDE = """# WebSockets

    ## What Are WebSockets? The Real-Time Problem

    HTTP is request-response: client asks, server answers. But what if the SERVER
    needs to push data to the CLIENT without the client asking? Chat messages, live
    scores, stock prices, collaborative editing, live dashboards.

    Before WebSockets:
    ```
    POLLING (simple but inefficient):
      Client asks every second: "Any new messages?"
      Server: "No." "No." "No." "YES! Here's a message." "No." "No."
      1000 clients * 1 request/sec = 1000 requests/sec of wasted polling.
      Message arrives "1 second late" on average.

    LONG POLLING (better but awkward):
      Client sends request, server holds it open until data is available.
      Data arrives: server responds, client immediately sends new request.
      Better latency, but HTTP overhead per message remains.
      Complex to scale (thousands of long-held connections).
    ```

    **WebSockets solve this with a persistent, bidirectional connection:**
    ```
      Client                HTTP Upgrade Request              Server
        │ ──── GET /chat HTTP/1.1 ────────────────────────► │
        │      Upgrade: websocket                            │
        │      Connection: Upgrade                           │
        │ ◄─── HTTP 101 Switching Protocols ─────────── ─── │
        │                                                    │
        │════════════ WebSocket connection open ════════════│
        │                                                    │
        │ ──── "Hello!" ──────────────────────────────────► │
        │ ◄─── "Hi there!" ─────────────────────────────── │
        │ ◄─── "New message from Alice" ─────────────────── │  (server push!)
        │ ──── "Got it, thanks" ──────────────────────────► │
        │                                                    │
        │  Both sides can send at any time!                  │
        │  One TCP connection, full duplex                   │
    ```

    WebSocket is a PROTOCOL UPGRADE from HTTP. It uses TCP's full-duplex
    capability — both sides can send simultaneously on the same connection.

    ---

    ## WebSocket vs HTTP: When to Use Each

    ```
    HTTP (REST):
      Request-response model. Client always initiates.
      Good for: CRUD operations, loading pages, static data.
      Bad for: server-initiated events, real-time updates.

    WebSocket:
      Persistent bidirectional connection. Either side can send data.
      Good for: chat, live updates, games, collaborative tools.
      Bad for: simple CRUD, stateless APIs (stateful connection = harder to scale).

    SERVER-SENT EVENTS (SSE) — middle ground:
      Server pushes data to client over regular HTTP.
      One-way: server -> client only (NOT bidirectional).
      Client cannot send data on same connection.
      Simpler than WebSockets for server-push-only use cases.
      Built on HTTP/2, supports reconnect automatically.
      Good for: live dashboards, notifications, tickers.
      Bad for: chat, games (need client->server real-time).

    DECISION GUIDE:
      Simple CRUD: REST HTTP
      Server needs to push updates, client doesn't respond in real-time: SSE
      Both sides communicate in real-time: WebSocket
      Real-time gaming / collaborative editing: WebSocket
    ```

    ---

    ## WebSocket Handshake in Detail

    ```
    1. Client sends HTTP Upgrade request:
       GET /chat HTTP/1.1
       Host: server.example.com
       Upgrade: websocket
       Connection: Upgrade
       Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==   <- random base64 key
       Sec-WebSocket-Version: 13

    2. Server agrees to upgrade:
       HTTP/1.1 101 Switching Protocols
       Upgrade: websocket
       Connection: Upgrade
       Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=  <- hashed key

    3. Connection is now a WebSocket:
       HTTP is no longer used. Binary WebSocket frames are exchanged.
       Either side can send frames at any time.

    WHY UPGRADE THROUGH HTTP?
      Firewalls and proxies allow port 80/443 HTTP.
      WebSocket uses same port, starts as HTTP, then upgrades.
      Traverses firewalls that would block a new TCP connection on a random port.
    ```

    ---

    ## WebSocket Frames and Protocol

    ```
    WebSocket messages are sent as FRAMES.

    Frame structure:
      FIN bit:       is this the last frame of the message?
      Opcode:        text (0x1), binary (0x2), ping (0x9), pong (0xA), close (0x8)
      Mask bit:      client->server frames must be masked (XOR with key)
      Payload length: variable length encoding
      Masking key:   4 bytes (client->server only)
      Payload data:  the actual message

    TEXT vs BINARY frames:
      Text (opcode 0x1): UTF-8 encoded string. JSON is common.
        {"type": "message", "user": "Alice", "content": "Hello!"}
      Binary (opcode 0x2): raw bytes. Used for images, audio, game state.

    PING/PONG (heartbeat):
      Server sends ping every 30 seconds.
      Client must respond with pong.
      No pong received: server closes connection (dead client).
      Keep NAT/proxy connections alive (they timeout idle connections).
    ```

    ---

    ## Building Real-Time Features with WebSockets

    ```
    CHAT APPLICATION:
      User connects -> WebSocket opens.
      Server assigns connection to a room (e.g., "room:general").
      User sends message -> server receives, broadcasts to all connections in room.

      // Node.js + ws library
      const wss = new WebSocketServer({ port: 8080 });
      const rooms = new Map();  // room -> Set of connections

      wss.on('connection', (ws) => {
        ws.on('message', (data) => {
          const msg = JSON.parse(data);
          if (msg.type === 'join') {
            rooms.get(msg.room)?.add(ws);
          }
          if (msg.type === 'message') {
            // broadcast to all in room
            rooms.get(msg.room)?.forEach(client => {
              if (client.readyState === WebSocket.OPEN) {
                client.send(JSON.stringify(msg));
              }
            });
          }
        });
        ws.on('close', () => { /* remove from rooms */ });
      });

    LIVE DASHBOARD:
      Server sends metrics every second:
        ws.send(JSON.stringify({cpu: 45, mem: 72, rps: 1234}));
      Client renders in UI immediately.
      No polling. No wasted requests.
    ```

    ---

    ## Scaling WebSockets — The Hard Part

    ```
    WebSockets create STATEFUL server connections.
    One server can handle ~10,000-100,000 concurrent WebSocket connections.
    (vs millions of stateless HTTP requests per server)

    THE PROBLEM WITH MULTIPLE SERVERS:
      Client A connects to Server 1.
      Client B connects to Server 2.
      A sends message -> Server 1 must broadcast to ALL clients.
      But B is on Server 2! Server 1 doesn't know about B.

    SOLUTION: Message broker (Redis Pub/Sub or Kafka):

      Server 1 (has clients A, C)    Server 2 (has clients B, D)
             │                               │
             │  publish "room:general: msg"  │
             └─────────► Redis Pub/Sub ◄─────┘
                         (all servers subscribed
                          to this channel)
             │◄─────────────────────────────►│
      Server 1 receives -> broadcasts to A,C  │  Server 2 receives -> broadcasts to B,D

    Every server subscribes to Redis pub/sub.
    Any server publishes: all servers receive and forward to their local clients.

    STICKY SESSIONS:
      Load balancer uses IP hash or cookie -> same client always routes to same server.
      Simpler but inflexible (can't freely scale servers).

    ALTERNATIVES:
      socket.io: popular Node.js library with fallbacks (long-poll if WS not available),
                 rooms, namespaces, Redis adapter for multi-server.
      Ably, Pusher, AWS IoT Core: managed WebSocket services (no infra to manage).
    ```

    ---

    ## WebSocket Security

    ```
    SECURITY CONSIDERATIONS:

    1. USE WSS (WebSocket Secure = WebSocket over TLS):
       ws://  = unencrypted (like HTTP)
       wss:// = TLS encrypted (like HTTPS)
       Always use wss:// in production.

    2. ORIGIN VALIDATION:
       During upgrade, check Origin header.
       Reject connections from unexpected origins to prevent CSRF-like attacks.
       if (request.headers.origin !== 'https://myapp.com') reject();

    3. AUTHENTICATION:
       HTTP is stateless with each request re-authenticated.
       WebSocket: authenticate ONCE at connection time (JWT in query param or first message).
       Don't use cookies (vulnerable to CSRF in WS context).

    4. MESSAGE VALIDATION:
       Parse and validate every incoming message.
       Client can send arbitrary data. Never trust.

    5. RATE LIMITING:
       Client can send messages very fast. Implement per-connection rate limiting.
       Close connection if client exceeds message rate (potential DoS).

    6. RECONNECTION:
       Network blips close WebSocket connections.
       Client must implement exponential backoff reconnection:
         try reconnect after: 1s, 2s, 4s, 8s, 16s... (don't hammer server)
    ```

    ---

    ## Mind Map

    ```
    WEBSOCKETS
    |
    +-- vs HTTP
    |   +-- HTTP: request-response, client initiates
    |   +-- WS: persistent bidirectional, either side sends
    |   +-- SSE: server-push only (one-way, HTTP-based)
    |
    +-- PROTOCOL
    |   +-- HTTP Upgrade handshake (101 Switching Protocols)
    |   +-- Binary frames (text/binary/ping/pong/close)
    |   +-- Uses port 80/443 (traverses firewalls)
    |
    +-- USE CASES
    |   +-- Chat (broadcast to room)
    |   +-- Live dashboards (server push metrics)
    |   +-- Collaborative editing
    |   +-- Real-time gaming
    |   +-- Financial tickers
    |
    +-- SCALING
    |   +-- Stateful connections (hard to scale)
    |   +-- Redis Pub/Sub for multi-server broadcast
    |   +-- Sticky sessions alternative
    |   +-- Managed: Ably, Pusher, AWS IoT
    |
    +-- SECURITY
        +-- Always WSS (TLS)
        +-- Origin validation
        +-- Auth at connection time
        +-- Rate limit messages per connection
    ```

    ---

    ## References

    ### Videos
    - **WebSockets in 100 Seconds** by Fireship:
      https://www.youtube.com/watch?v=1BfCnjr_Vjg
      - Perfect 100-second mental model plus demo.
    - **Scaling WebSockets** by ByteByteGo:
      https://www.youtube.com/watch?v=M3Tz7qMRyWs
      - Multi-server scaling with Redis pub/sub.

    ### Articles
    - **MDN WebSockets Guide**: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API
    - **socket.io (most popular WebSocket library)**: https://socket.io/docs/v4/

    ### Practice
    - **socket.io chat tutorial**: https://socket.io/get-started/chat
      - Build a real chat app in 30 minutes.
    """

    WS_Q = [
        {"id":"ws-q6","type":"mcq","prompt":"What problem does WebSocket solve that HTTP polling cannot efficiently solve?",
         "choices":["WebSocket is faster for REST APIs","Server-initiated real-time push — HTTP polling wastes bandwidth checking constantly. WebSocket: open once, server pushes immediately when data arrives",
                    "WebSocket replaces TCP","WebSocket uses less memory"],
         "answerIndex":1,"explanation":"Polling: client asks every second = 1000 clients = 1000 requests/sec of wasted work. WebSocket: server pushes within milliseconds when an event occurs. No wasted requests. One persistent connection per client. Latency: near-zero vs avg 500ms for 1-second polling.","tags":["websockets","real-time","polling"]},
        {"id":"ws-q7","type":"mcq","prompt":"What HTTP status code indicates a successful WebSocket upgrade?",
         "choices":["200 OK","301 Moved","101 Switching Protocols — server agrees to upgrade from HTTP to WebSocket",
                    "204 No Content"],
         "answerIndex":2,"explanation":"WebSocket handshake: client sends Upgrade: websocket, Connection: Upgrade headers. Server responds 101 Switching Protocols = connection upgraded. After 101: no more HTTP. The TCP connection is now a WebSocket channel for binary frames.","tags":["websockets","handshake","http"]},
        {"id":"ws-q8","type":"mcq","prompt":"Why does WebSocket use port 80/443 for connections?",
         "choices":["Those are the fastest ports","WebSocket starts as HTTP on port 80/443, then upgrades — traverses corporate firewalls and proxies that block other ports",
                    "Those are the only TCP ports","WebSocket requires HTTP/2"],
         "answerIndex":1,"explanation":"Firewalls typically allow 80 (HTTP) and 443 (HTTPS) outbound. A new WebSocket on a random port would be blocked. By starting as HTTP on 80/443 and upgrading, WebSocket piggybacks on allowed ports. Proxies that understand WebSocket let the upgrade through.","tags":["websockets","ports","firewalls"]},
        {"id":"ws-q9","type":"mcq","prompt":"What is Server-Sent Events (SSE) and how does it differ from WebSocket?",
         "choices":["SSE is the same as WebSocket","SSE: one-way server->client push over HTTP. WebSocket: bidirectional. SSE: uses standard HTTP (no upgrade), automatic reconnect. WebSocket: custom protocol, manual reconnect.",
                    "SSE requires HTTP/3","SSE is deprecated"],
         "answerIndex":1,"explanation":"SSE: simpler than WebSocket for server-push-only. Browser EventSource API. Automatic reconnect on disconnect. Works over HTTP/2. Good for: live score updates, notifications, log streaming. NOT for: chat (can't send user messages back on same connection).","tags":["websockets","sse","comparison"]},
        {"id":"ws-q10","type":"mcq","prompt":"What is the WebSocket ping/pong mechanism used for?",
         "choices":["For authentication","Heartbeat to detect dead connections and keep NAT/proxy connections alive — server pings, client must pong, no pong -> close connection",
                    "For load balancing","Message acknowledgment"],
         "answerIndex":1,"explanation":"NAT gateways and proxies close idle TCP connections (30-60 second timeout). Ping/pong every 30s: 1) keep connection alive through NAT, 2) detect dead clients (mobile app backgrounded = no pong = close). Server initiates ping. Client must respond pong within timeout.","tags":["websockets","ping-pong","heartbeat"]},
        {"id":"ws-q11","type":"mcq","prompt":"How does WebSocket authentication differ from HTTP authentication?",
         "choices":["Same as HTTP bearer token on each message","Authenticate once at connection establishment (JWT in first message or headers) — the connection is then trusted. HTTP re-authenticates every request.",
                    "WebSocket has no authentication","WebSocket uses cookies"],
         "answerIndex":1,"explanation":"WebSocket: authenticate at upgrade time (check token in query param or first message). Once authenticated, connection is trusted for its lifetime. No re-auth per message. Risk: if token invalidated (logout, ban), must close the open WebSocket connection server-side. Track connections by userId.","tags":["websockets","authentication","security"]},
        {"id":"ws-q12","type":"mcq","prompt":"What is the scaling challenge with WebSocket servers?",
         "choices":["WebSocket servers crash more often","WebSocket connections are STATEFUL — a client connected to Server 1 cannot receive a broadcast sent from Server 2 without a shared message bus",
                    "WebSocket uses too much CPU","Databases can't handle WebSocket load"],
         "answerIndex":1,"explanation":"HTTP: stateless, any server handles any request. WebSocket: client A on Server 1, B on Server 2. Broadcast to all users in a room: Server 1 must notify Server 2. Solution: Redis Pub/Sub or Kafka. All servers subscribe, any server publishes = all servers relay to their local clients.","tags":["websockets","scaling","state"]},
        {"id":"ws-q13","type":"mcq","prompt":"What should you use instead of WebSocket for one-way server-to-client streaming of events?",
         "choices":["Long polling is better","Server-Sent Events (SSE) — simpler, uses HTTP, automatic reconnect, built-in event IDs, works with HTTP/2 multiplexing",
                    "WebSocket is required","Short polling"],
         "answerIndex":1,"explanation":"SSE vs WebSocket: If server needs to push but client only reads (live dashboard, notifications, price updates) -> SSE. Simpler: no upgrade, standard HTTP, EventSource API. WebSocket: when client ALSO sends real-time data (chat, game input, collaboration). Don't use WebSocket when SSE suffices.","tags":["websockets","sse","decision"]},
        {"id":"ws-q14","type":"mcq","prompt":"What is socket.io and why is it preferred over raw WebSocket in many applications?",
         "choices":["A lower-level protocol","A library built on WebSocket adding: automatic reconnection, fallback to polling (if WS unavailable), rooms/namespaces, binary support, Redis adapter for multi-server",
                    "A UDP-based protocol","A WebSocket debugger"],
         "answerIndex":1,"explanation":"Raw WebSocket: you build reconnection, rooms, multi-server yourself. socket.io: rooms out-of-box (socket.join('room:123')), io.to('room:123').emit() broadcasts. Auto-reconnect with backoff. If WebSocket blocked: falls back to long-polling. Redis adapter: multi-server fan-out automatic.","tags":["websockets","socket-io","library"]},
        {"id":"ws-q15","type":"mcq","prompt":"What does `wss://` mean compared to `ws://`?",
         "choices":["Weighted WebSocket","WebSocket Secure — WebSocket over TLS/SSL. wss is to ws what https is to http. Always use wss in production to encrypt the connection.",
                    "WebSocket with server-side state","Wide-area WebSocket"],
         "answerIndex":1,"explanation":"ws://: unencrypted WebSocket (like HTTP). Messages visible in plaintext to network sniffers. wss://: TLS encrypted WebSocket (like HTTPS). All WebSocket traffic encrypted. In production: always wss. Most browsers block non-secure WebSocket connections when page is served over HTTPS.","tags":["websockets","wss","security"]},
    ]

    WS_FC = [
        {"id":"ws-fc5","front":"WebSocket vs HTTP vs SSE decision","back":"HTTP: request-response CRUD. SSE: server-push only (live dashboard, notifications, one-way). WebSocket: bidirectional real-time (chat, games, collab editing). Use the simplest that fits: SSE before WebSocket, HTTP before SSE.","tags":["websockets","sse","decision"]},
        {"id":"ws-fc6","front":"WebSocket scaling pattern","back":"Single server: 10K-100K connections (stateful). Multi-server: client on Server1 can't get broadcast from Server2. Fix: Redis Pub/Sub (all servers subscribe). Any server publishes -> all servers relay to their local clients. socket.io Redis adapter automates this.","tags":["websockets","scaling","redis"]},
        {"id":"ws-fc7","front":"WebSocket security checklist","back":"1. Always wss:// (TLS). 2. Validate Origin header at upgrade. 3. Authenticate at connection time (JWT in query/first message). 4. Validate every incoming message. 5. Rate limit messages per connection. 6. Server-side close on auth revocation.","tags":["websockets","security"]},
        {"id":"ws-fc8","front":"WebSocket reconnection pattern","back":"Connections drop (network blip, server restart, idle timeout). Client: catch onclose event, retry with exponential backoff: 1s, 2s, 4s, 8s, 16s (capped at 60s). Add jitter (random offset) to prevent thundering herd on server restart.","tags":["websockets","reconnection","resilience"]},
    ]

    d['guide'] = WS_GUIDE
    existing_ids = {q['id'] for q in d['questions']}
    for q in WS_Q:
        if q['id'] not in existing_ids:
            d['questions'].append(q)
    existing_fc_ids = {fc['id'] for fc in d['flashcards']}
    for fc in WS_FC:
        if fc['id'] not in existing_fc_ids:
            d['flashcards'].append(fc)
    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"websockets.json: guide={len(WS_GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ── patch_networking_3.py ──────────────────────────────────────────────────────────────────
    """
    patch_networking_3.py — rate-limiting.json, load-balancing.json, long-polling.json, ftp.json
    Run: python3 scripts/patch_networking_3.py
    """
    import json
    from pathlib import Path

    BASE = Path(__file__).parent.parent / 'src/content/topics/networking'

    # ─────────────────────────────────────────────────────────────────────────────
    # RATE LIMITING
    # ─────────────────────────────────────────────────────────────────────────────
    p = BASE / 'rate-limiting.json'
    d = json.loads(p.read_text())

    RL_GUIDE = """# Rate Limiting

    ## What Is Rate Limiting and Why Does It Matter?

    Imagine a coffee shop with one barista. If 1000 customers rush in at once,
    the barista can't serve everyone — they'd be overwhelmed and serve nobody well.
    So the shop has a rule: take orders from at most 100 customers per hour.

    **Rate limiting** enforces a maximum rate of requests a client can make to a service.

    ```
    WITHOUT rate limiting:
      One bad actor sends 1,000,000 requests -> server overloaded -> all users suffer
      Scrapers download your entire data catalogue for free
      Brute force attack: try 10 billion passwords until one works
      DDoS: millions of bots overwhelm your API

    WITH rate limiting:
      Each IP/API key limited to 1000 requests/minute
      Bad actor hits limit -> 429 Too Many Requests
      Normal users: unaffected
      Server: protected from volumetric abuse
    ```

    Rate limiting protects for: security (brute force, DDoS), fair use (prevent one user
    hogging resources), cost control (API that charges per request).

    ---

    ## Algorithm 1: Fixed Window Counter

    ```
    Simplest approach. Divide time into fixed windows (e.g., each minute).
    Count requests in the current window. Reject if over limit.

    Time: 14:00:00 - 14:00:59 = window 1
          14:01:00 - 14:01:59 = window 2

    Rule: max 10 requests per minute per IP.

    Window 1:
      14:00:01 IP=1.2.3.4 -> count=1 -> ALLOW
      14:00:10 IP=1.2.3.4 -> count=2 -> ALLOW
      ...
      14:00:55 IP=1.2.3.4 -> count=10 -> ALLOW
      14:00:59 IP=1.2.3.4 -> count=11 -> DENY (429)

    Window 2:
      14:01:00 IP=1.2.3.4 -> count=1 -> ALLOW (new window, counter reset!)

    THE BURST PROBLEM:
      Client sends 10 requests at 14:00:59 (end of window 1)
      Counter resets at 14:01:00
      Client sends 10 more requests at 14:01:00 (start of window 2)
      In 2 seconds: 20 requests! (2x the intended limit)
      Window boundary = burst allowed.

      14:00:59 ──[10 req]── | ──[10 req]── 14:01:00
                          window reset
                          20 requests in 2 seconds!
    ```

    ---

    ## Algorithm 2: Sliding Window Log

    ```
    Track exact timestamp of each request in a log.
    On each request: remove entries older than window, count remaining.

    Rule: 10 requests per minute.
    1.2.3.4 log: [14:00:01, 14:00:05, 14:00:10, ..., 14:00:55]

    Request at 14:01:05:
      Remove entries before 14:00:05 (1 minute ago)
      Count remaining entries: 9
      9 < 10 -> ALLOW. Add 14:01:05 to log.

    More accurate than fixed window (no burst at boundary).
    Con: stores every request timestamp. High memory for high-volume APIs.
    Better: sliding window COUNTER (hybrid approach, approximates sliding window).
    ```

    ---

    ## Algorithm 3: Token Bucket

    ```
    Imagine a bucket that holds tokens.
    Tokens are added to the bucket at a fixed rate (e.g., 10 tokens/sec).
    Each request consumes 1 token.
    If bucket is empty: request denied (429).
    If tokens available: allow request.

    VISUAL:
      ┌──────────────┐
      │ ● ● ● ● ●   │  bucket (max 10 tokens)
      │ ● ● ● ● ●   │
      └──────────────┘
           │
           │ refill rate: +10 tokens/sec (max 10)
           │

      Request comes in -> remove 1 token -> ALLOW
      Bucket empty -> DENY until tokens refill

      token_count = min(max_tokens, current_tokens + elapsed_time * refill_rate)

    BURSTING ALLOWED:
      Bucket is FULL at start -> 10 requests can burst immediately.
      Then limited to refill rate.
      This is intentional: token bucket allows SHORT bursts above steady-state rate.

    USAGE:
      AWS API Gateway uses token bucket.
      Most practical rate limiting starts with token bucket.

    PARAMETERS:
      bucket_size: max burst size
      refill_rate: sustained request rate
      Set bucket_size = 2x refill_rate for typical burst tolerance.
    ```

    ---

    ## Algorithm 4: Leaky Bucket

    ```
    Requests go INTO a bucket (queue).
    Bucket LEAKS at a fixed rate (processes one request per N ms).
    If bucket is full: new requests are dropped.

    VISUAL:
      Requests ──► ┌──────────┐
                   │ queued   │
                   │ requests │ ──► processed at fixed rate (leak)
                   └──────────┘

      If queue full: request DROPPED immediately.

    KEY DIFFERENCE FROM TOKEN BUCKET:
      Token bucket: request processed immediately if token available, bursts OK.
      Leaky bucket: request added to queue, processed at CONSTANT rate. No bursts.
      Leaky = smoothed output. Token = burst-allowed output.

    USE: network traffic shaping where smooth output rate is required.
         Less common in API rate limiting (token bucket preferred).
    ```

    ---

    ## Implementation: Redis-Based Sliding Window

    ```python
    import redis
    import time

    r = redis.Redis()

    def is_rate_limited(user_id: str, limit: int, window_seconds: int) -> bool:
        key = f"rate_limit:{user_id}"
        now = time.time()
        window_start = now - window_seconds

        pipe = r.pipeline()
        # Remove requests outside the window
        pipe.zremrangebyscore(key, 0, window_start)
        # Count requests in current window
        pipe.zcard(key)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Set key expiry
        pipe.expire(key, window_seconds * 2)
        results = pipe.execute()

        count = results[1]
        return count >= limit  # True = rate limited, return 429

    # Usage:
    if is_rate_limited(user_id="user:123", limit=100, window_seconds=60):
        return HTTP_429_TOO_MANY_REQUESTS
    ```

    ---

    ## Rate Limit Response — What to Return

    ```
    HTTP 429 Too Many Requests

    Headers:
      X-RateLimit-Limit:     100    # max requests per window
      X-RateLimit-Remaining:  0     # how many requests left
      X-RateLimit-Reset:  1714320000  # Unix timestamp when limit resets
      Retry-After:           30     # seconds until client can retry

    Body:
      {
        "error": "rate_limit_exceeded",
        "message": "You have exceeded 100 requests per minute",
        "retry_after": 30
      }

    Client responsibility:
      On 429: wait Retry-After seconds before retrying.
      Implement exponential backoff with jitter if many retries needed.
      Cache responses where possible to reduce request rate.
    ```

    ---

    ## Rate Limiting Granularity — What to Limit By

    ```
    BY IP ADDRESS:
      Simplest. But: shared IPs (office, university) unfair. VPNs bypass.
      Good for: anonymous endpoints (login, signup).

    BY USER ID / API KEY:
      More accurate. Authenticated users identified.
      Good for: authenticated APIs.
      Risk: one user signs up many accounts ("account stuffing").

    BY ENDPOINT:
      Different limits per endpoint.
      /api/send-email: 10/hour (expensive, abuse risk)
      /api/products: 10000/minute (cheap, read-only)
      Fine-grained but complex to configure.

    BY TIER/PLAN:
      Free tier: 100 requests/day
      Pro tier:  10,000 requests/day
      Enterprise: unlimited
      Stripe, SendGrid, GitHub all do this.

    BEST PRACTICE: combine multiple:
      IP rate limit: 1000/min (blocks bots, DDoS)
      User rate limit: 100/min (fair use)
      Endpoint rate limit: expensive actions limited more
    ```

    ---

    ## Where to Implement Rate Limiting

    ```
    LAYER OPTIONS:
      1. API Gateway (Kong, AWS API Gateway, nginx):
         Single place, all APIs protected. Easy to configure, no code change.
         Recommended for most cases.

      2. Application code:
         More fine-grained (per-user, per-plan, per-action).
         Redis for distributed rate limit store.
         Can make business logic decisions.

      3. CDN / Edge (Cloudflare, AWS WAF):
         Closest to attacker. Blocks before hitting your infrastructure.
         IP-based limiting. Good for DDoS first line of defense.

      4. Database:
         Token bucket in DB. Simple but DB becomes bottleneck.
         Don't do this for high-volume APIs.

    RECOMMENDED STACK:
      Cloudflare/WAF: block known bad IPs, volumetric DDoS
      API Gateway (nginx/Kong): IP rate limit, API key quota
      Application (Redis): fine-grained user/plan limits
      Three layers = defense in depth
    ```

    ---

    ## Mind Map

    ```
    RATE LIMITING
    |
    +-- ALGORITHMS
    |   +-- Fixed Window (simple, burst at boundary)
    |   +-- Sliding Window Log (accurate, high memory)
    |   +-- Token Bucket (burst allowed, practical)
    |   +-- Leaky Bucket (smooth output, no burst)
    |
    +-- GRANULARITY
    |   +-- By IP (anonymous endpoints)
    |   +-- By user/API key (authenticated)
    |   +-- By endpoint (different limits per action)
    |   +-- By tier/plan (free/pro/enterprise)
    |
    +-- RESPONSE
    |   +-- HTTP 429 Too Many Requests
    |   +-- Retry-After header
    |   +-- X-RateLimit-* headers
    |
    +-- IMPLEMENTATION
        +-- API Gateway (recommended)
        +-- Redis Sorted Set (sliding window)
        +-- CDN/WAF (first line of defense)
    ```

    ---

    ## References

    ### Videos
    - **Rate Limiting System Design** by ByteByteGo:
      https://www.youtube.com/watch?v=FU4WlwfS3G0
      - All 4 algorithms visualised with system design context.
    - **Designing a Rate Limiter** by System Design Interview channel:
      https://www.youtube.com/watch?v=mhUQe4BKZXs
      - Full system design walkthrough.

    ### Articles
    - **Redis rate limiting patterns**: https://redis.io/docs/manual/patterns/rate-limiting/
    - **Stripe rate limiting blog**: https://stripe.com/blog/rate-limiters
    """

    RL_Q = [
        {"id":"rl-q4","type":"mcq","prompt":"What HTTP status code does rate limiting return?",
         "choices":["400 Bad Request","403 Forbidden","429 Too Many Requests — with Retry-After header indicating when to retry",
                    "503 Service Unavailable"],
         "answerIndex":2,"explanation":"HTTP 429 = rate limited. Include: Retry-After: 30 (seconds until ok to retry), X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset. Client must respect Retry-After and back off. Don't use 403 (that's authorization) or 503 (server overloaded).","tags":["rate-limiting","http","429"]},
        {"id":"rl-q5","type":"mcq","prompt":"What is the burst problem with the fixed window rate limiting algorithm?",
         "choices":["Fixed windows cause CPU spikes","Client can double the limit by sending requests at the end of one window and start of the next — both windows' counts reset to 0 at boundary",
                    "Fixed windows are inaccurate for reads","Windows cause clock skew"],
         "answerIndex":1,"explanation":"Limit: 10 req/min. Send 10 at 14:00:59 + 10 at 14:01:00 = 20 requests in 2 seconds. Both windows allow 10 each. The boundary burst is a design flaw. Sliding window and token bucket don't have this flaw.","tags":["rate-limiting","fixed-window","burst"]},
        {"id":"rl-q6","type":"mcq","prompt":"How does a token bucket rate limiter work?",
         "choices":["Requests queued and leaked at fixed rate","Tokens added to bucket at fixed rate. Each request consumes one token. If empty: deny. If available: allow. Bucket size controls max burst.",
                    "Counts requests in a sliding time window","Tracks exact timestamps of requests"],
         "answerIndex":1,"explanation":"Token bucket: bucket holds max N tokens. Replenish R tokens/sec. Request: take 1 token if available. Bucket full when idle -> burst allowed up to N requests immediately. Then limited to R per second. AWS API Gateway, most practical implementations use token bucket.","tags":["rate-limiting","token-bucket"]},
        {"id":"rl-q7","type":"mcq","prompt":"What is the difference between token bucket and leaky bucket?",
         "choices":["They are identical","Token bucket: requests processed immediately if token available, bursts allowed. Leaky bucket: requests queued, processed at constant rate, no bursting.",
                    "Leaky bucket allows more requests","Token bucket is for UDP only"],
         "answerIndex":1,"explanation":"Token bucket: full bucket = burst of N requests immediately (then steady-state R/sec). Output rate varies. Leaky bucket: constant output regardless of input rate. No bursting. Input queue absorbs spikes. Use token for APIs (bursts OK), leaky for network shaping (smooth output needed).","tags":["rate-limiting","token-bucket","leaky-bucket"]},
        {"id":"rl-q8","type":"mcq","prompt":"Where is the best place to implement primary rate limiting?",
         "choices":["Inside each microservice","In the database","At the API Gateway or load balancer level — single choke point, all traffic passes through, no code changes in services",
                    "Only at the CDN"],
         "answerIndex":2,"explanation":"API Gateway (nginx, Kong, AWS API Gateway): single point to configure limits. All services protected automatically. No per-service code. Centralized monitoring. Then add Redis-based application-level limiting for fine-grained per-user/plan limits. CDN as first line for IP-based DDoS.","tags":["rate-limiting","architecture","api-gateway"]},
        {"id":"rl-q9","type":"mcq","prompt":"How should rate limiting track state across multiple API server instances?",
         "choices":["Each server tracks independently (in memory)","Use a shared distributed store like Redis — all API servers read/write the same counter, ensuring limit is enforced globally not per-server",
                    "Use a database for every check","DNS-based rate limiting"],
         "answerIndex":1,"explanation":"In-memory rate limiting: 3 servers, each allows 100 req/min. Client splits requests across servers: 300 req/min! Redis sorted set: all servers share one counter per user. Any request to any server increments the same key. Rate limit is globally enforced.","tags":["rate-limiting","redis","distributed"]},
        {"id":"rl-q10","type":"mcq","prompt":"What is rate limiting by API key/tier vs by IP?",
         "choices":["They are the same","IP: simple, good for anonymous endpoints, but shared IPs cause false positives. API key: authenticated users, per-plan limits (free: 100/day, pro: 10K/day), more accurate and business-aligned.",
                    "IP rate limiting is more secure","API keys bypass rate limits"],
         "answerIndex":1,"explanation":"IP limits: one university IP = 10,000 students. Single IP limit blocks all. API key: each developer/user has own key and quota. Per-plan limits: monetize access (Stripe, SendGrid model). Use both: IP limit for DDoS/brute-force, API key for business quota management.","tags":["rate-limiting","api-key","granularity"]},
        {"id":"rl-q11","type":"mcq","prompt":"What is a sliding window counter (approximate sliding window)?",
         "choices":["A window that slides across time zones","Combines fixed window counters: weight previous window count by how much of it overlaps with current window. Approximates true sliding window with O(1) space per key.",
                    "A Redis data structure","A hardware counter"],
         "answerIndex":1,"explanation":"Sliding window counter: currentWindowCount + previousWindowCount * (fraction of previous window still in scope). If window=60s, 45s into current window: weight previous by (60-45)/60=0.25. Approximate but close enough. Used by Redis rate limit implementations. More memory-efficient than storing every timestamp.","tags":["rate-limiting","sliding-window"]},
        {"id":"rl-q12","type":"mcq","prompt":"What should a well-behaved API client do when it receives a 429 response?",
         "choices":["Retry immediately","Stop sending requests, wait Retry-After seconds, then retry with exponential backoff if 429 persists. Cache responses to reduce future request rate.",
                    "Switch to a different endpoint","Send requests faster to complete before limit"],
         "answerIndex":1,"explanation":"Retry-After: 30 -> wait 30 seconds. If 429 again: wait 60s, 120s (exponential backoff). Add jitter to avoid synchronized retry storms. Implement response caching to reduce hits. A well-behaved client respects rate limits and uses them to schedule requests.","tags":["rate-limiting","client","retry"]},
        {"id":"rl-q13","type":"mcq","prompt":"What is the difference between rate limiting and throttling?",
         "choices":["They are identical","Rate limiting: hard block (429) when limit exceeded. Throttling: slow down responses (add delay) when approaching limit, giving client time to back off gracefully.",
                    "Throttling is for databases only","Rate limiting is for TCP only"],
         "answerIndex":1,"explanation":"Rate limiting: hit limit -> 429, client must wait. Throttling: approaching limit -> responses delayed 500ms, 1s, 2s. Softer degradation. Some systems do both: throttle near limit, hard deny at limit. AWS API Gateway uses both: throttle to steady-state, burst limit for temporary spikes.","tags":["rate-limiting","throttling"]},
        {"id":"rl-q14","type":"mcq","prompt":"How does Redis Sorted Set implement sliding window rate limiting?",
         "choices":["Using Redis KEYS command","ZADD: add request timestamps as scores. ZREMRANGEBYSCORE: remove old timestamps outside window. ZCARD: count remaining. Atomic pipeline for consistency.",
                    "Using Redis Pub/Sub","Redis INCR with TTL"],
         "answerIndex":1,"explanation":"Redis ZADD key score member (score=timestamp, member=unique event ID). ZREMRANGEBYSCORE key -inf (now - window): remove old. ZCARD key: count in window. If count >= limit: 429. EXPIRE key on window_size to clean up. Use PIPELINE for atomicity.","tags":["rate-limiting","redis","sorted-set"]},
        {"id":"rl-q15","type":"mcq","prompt":"Why is rate limiting important for login endpoints specifically?",
         "choices":["Login is slow","Prevents brute-force attacks — without rate limiting, attacker can try millions of password combinations. With limit of 5 attempts/minute, brute-forcing a 8-char password takes centuries.",
                    "Login uses more bandwidth","Login requires more CPU"],
         "answerIndex":1,"explanation":"Without rate limiting on /login: try every password in 'rockyou.txt' (10 billion common passwords). With rate limit 5/min per IP: 10B attempts / 5 per min = 38 centuries. Add account lockout after 10 failed attempts. Add CAPTCHA. Never expose whether email exists (timing attack).","tags":["rate-limiting","brute-force","security"]},
        {"id":"rl-q16","type":"mcq","prompt":"What is a token bucket's `refill_rate` vs `bucket_size` parameter?",
         "choices":["They are the same","Refill rate = sustained request rate (tokens added per second). Bucket size = max burst capacity (max tokens accumulated when idle). Bucket full from idle = burst of bucket_size requests allowed immediately.",
                    "Bucket size limits total requests","Refill rate is the maximum allowed"],
         "answerIndex":1,"explanation":"Refill rate 10/sec, bucket_size 100: user can be idle 10 seconds -> accumulate 100 tokens -> burst 100 requests instantly -> then limited to 10/sec. Browser pre-loading scenario: valid burst. API key with high refill but small bucket: limits burst while allowing high sustained rate.","tags":["rate-limiting","token-bucket","parameters"]},
        {"id":"rl-q17","type":"mcq","prompt":"What is distributed rate limiting and when is it needed?",
         "choices":["Rate limiting across geographic regions only","When multiple server instances or replicas exist, rate limit state must be shared (Redis/Memcached) to enforce global limits regardless of which server a request hits",
                    "Single-server rate limiting","Kubernetes-only rate limiting"],
         "answerIndex":1,"explanation":"3 servers, each with in-memory limit 100/min: user hits all 3 servers = 300/min effective. Distributed rate limiting: all servers share Redis key per user. Request to any server increments same counter. True 100/min limit enforced globally. Required in any horizontally-scaled deployment.","tags":["rate-limiting","distributed","redis"]},
        {"id":"rl-q18","type":"mcq","prompt":"What are the X-RateLimit-* headers and what values should they contain?",
         "choices":["Internal headers not exposed to clients","X-RateLimit-Limit (max per window), X-RateLimit-Remaining (calls left in current window), X-RateLimit-Reset (Unix timestamp when window resets). Clients use these to self-throttle.",
                    "Required by HTTP standard","Performance metrics headers"],
         "answerIndex":1,"explanation":"X-RateLimit-Limit: 100. X-RateLimit-Remaining: 37. X-RateLimit-Reset: 1714320060. Client: if Remaining approaches 0, slow down proactively. Don't wait for 429. Proactive clients are more efficient and avoid disruption. GitHub, Stripe all return these.","tags":["rate-limiting","headers","http"]},
        {"id":"rl-q19","type":"mcq","prompt":"Should you rate limit by user ID or by API key for a commercial API?",
         "choices":["Always by IP","API key is better — it maps directly to a customer's plan/quota, is revocable, traceable, and allows per-customer monetization (free tier: 1000/day, pro: 100K/day)",
                    "User ID and API key are the same","Neither — just use IP"],
         "answerIndex":1,"explanation":"API key: unique per developer/app. Compromised: revoke that key. Exceeded quota: upgrade plan. Usage analytics per customer. Maps to billing. IP-based: rotation possible, shared IPs problematic, no billing tie-in. Commercial APIs (Stripe, Twilio, OpenAI, GitHub): all use API keys.","tags":["rate-limiting","api-key","commercial"]},
        {"id":"rl-q20","type":"mcq","prompt":"What is 'cell-rate' or 'token bucket per cell' pattern?",
         "choices":["A hardware networking term","Different token buckets per action/endpoint — /api/email: 10/hour, /api/search: 1000/min, /api/export: 5/day. Each action has independent bucket matching its cost/risk.",
                    "A Kubernetes limit","Redis cluster partitioning"],
         "answerIndex":1,"explanation":"Per-endpoint limits: search (cheap) gets 1000/min. Email send (expensive, abuse risk) gets 10/hour. Export (heavy server operation) gets 5/day. Matches limit to action cost and abuse potential. Much better than one global limit. AWS API Gateway, Kong, nginx rate limiting all support per-route limits.","tags":["rate-limiting","per-endpoint","granularity"]},
    ]

    RL_FC = [
        {"id":"rl-fc4","front":"4 rate limiting algorithms","back":"Fixed Window: simple, burst at boundary. Sliding Window Log: accurate, high memory. Token Bucket: burst allowed (bucket_size tokens), steady state (refill_rate/sec), practical. Leaky Bucket: constant output rate, no burst, smooth traffic shaping.","tags":["rate-limiting","algorithms"]},
        {"id":"rl-fc5","front":"Token bucket parameters","back":"bucket_size = max burst capacity. refill_rate = sustained rate (tokens/sec). Idle for T seconds -> accumulate min(T*refill_rate, bucket_size) tokens. Full bucket = burst allowed. Then steady-state refill_rate limit. AWS API Gateway default model.","tags":["rate-limiting","token-bucket"]},
        {"id":"rl-fc6","front":"Redis sliding window implementation","back":"ZADD key timestamp event_id. ZREMRANGEBYSCORE key -inf (now-window). ZCARD key -> current count. EXPIRE key. Wrap in PIPELINE for atomicity. All API servers share same Redis key = globally distributed rate limit. O(log N) per request.","tags":["rate-limiting","redis","implementation"]},
        {"id":"rl-fc7","front":"Rate limiting response headers","back":"Status 429. Retry-After: 30 (seconds). X-RateLimit-Limit: 100. X-RateLimit-Remaining: 0. X-RateLimit-Reset: Unix timestamp. Client: wait Retry-After, then exponential backoff with jitter if still 429. Cache responses to reduce rate.","tags":["rate-limiting","http","429"]},
        {"id":"rl-fc8","front":"Defense in depth: three layers","back":"1. CDN/WAF (Cloudflare): IP-based, volumetric DDoS, geo-block. 2. API Gateway (nginx/Kong): API key quotas, IP limits. 3. Application (Redis): per-user plan limits, per-action limits. Each layer handles what it does best.","tags":["rate-limiting","architecture","defense-in-depth"]},
    ]

    d['guide'] = RL_GUIDE
    existing_ids = {q['id'] for q in d['questions']}
    for q in RL_Q:
        if q['id'] not in existing_ids:
            d['questions'].append(q)
    existing_fc_ids = {fc['id'] for fc in d['flashcards']}
    for fc in RL_FC:
        if fc['id'] not in existing_fc_ids:
            d['flashcards'].append(fc)
    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"rate-limiting.json: guide={len(RL_GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ─────────────────────────────────────────────────────────────────────────────
    # LOAD BALANCING
    # ─────────────────────────────────────────────────────────────────────────────
    p = BASE / 'load-balancing.json'
    d = json.loads(p.read_text())

    LB_GUIDE = """# Load Balancing

    ## What Is Load Balancing?

    Imagine a bank with 10 tellers. All customers queue at ONE desk,
    and that desk randomly directs each customer to an available teller.
    No single teller is overwhelmed while others are idle.

    A load balancer does the same for servers: distributes incoming requests
    across multiple backend servers so no single server bears all the load.

    ```
    WITHOUT load balancer:
      All 10,000 req/sec -> Server 1 (overloaded, crashes)
      Server 2, 3, 4... (idle)

    WITH load balancer:
      10,000 req/sec -> Load Balancer
                          ├── 2,500 req/sec -> Server 1
                          ├── 2,500 req/sec -> Server 2
                          ├── 2,500 req/sec -> Server 3
                          └── 2,500 req/sec -> Server 4
    ```

    Benefits:
    - **Horizontal scaling**: add more servers to handle more traffic
    - **High availability**: if one server fails, others continue serving
    - **Zero-downtime deployments**: take servers out of rotation one at a time

    ---

    ## Layer 4 vs Layer 7 Load Balancing

    ```
    LAYER 4 (Transport Layer — TCP/UDP):
      Sees: source IP, dest IP, source port, dest port, protocol (TCP/UDP)
      Cannot see: HTTP headers, URL path, cookies, body
      Routes based on: IP and port only
      How: forwards TCP packets to backend (NAT or TCP proxying)
      Speed: very fast (no application parsing)
      Example: AWS Network Load Balancer (NLB)

    LAYER 7 (Application Layer — HTTP):
      Sees: HTTP method, URL path, headers, cookies, body, host
      Routes based on: URL path, host header, HTTP headers, cookie value
      Can: inspect content, set headers, terminate TLS, rewrite URLs, sticky sessions
      Speed: slightly slower (must parse HTTP), but much more flexible
      Example: AWS Application Load Balancer (ALB), nginx, HAProxy

    COMPARISON:
      Use L4: when you need raw TCP speed, non-HTTP protocols (database, game, streaming)
      Use L7: web applications, microservices, content-based routing (99% of web apps)

    EXAMPLE L7 ROUTING:
      GET /api/v1/users  -> user-service backend pool
      GET /api/v1/orders -> order-service backend pool
      GET /static/*      -> S3 or CDN (skip app servers entirely)
    ```

    ---

    ## Load Balancing Algorithms

    ### Round Robin
    ```
    Requests distributed sequentially: Server1, Server2, Server3, Server1, ...
    Each server gets equal number of requests.

    Simple. Works when all requests take similar time and all servers are equal.
    Problem: one slow request on Server1 while Server2 is idle.

    Weighted Round Robin:
      Server1 (weight=3): 3 out of 6 requests
      Server2 (weight=2): 2 out of 6 requests
      Server3 (weight=1): 1 out of 6 requests
      Use when: servers have different capacities (more powerful server = higher weight).
    ```

    ### Least Connections
    ```
    Send request to server with fewest active connections currently.

    Request 1 -> Server1 (0 conns) -> Server1 now: 1 conn
    Request 2 -> Server2 (0 conns) -> Server2 now: 1 conn
    Request 3 -> Server3 (0 conns) -> Server3 now: 1 conn
    Request 4 -> Server1 or 2 or 3 (all have 1) -> round-robin tiebreak
    Server1 finishes request 1 -> 0 conns -> gets next request

    BETTER THAN ROUND ROBIN FOR:
      Requests with variable processing time (1ms queries vs 10s uploads).
      Round robin: slow request on Server1 while Server2/3 are idle.
      Least connections: Server1 has more active conns = avoid it.

    Weighted Least Connections: multiplied by weight for heterogeneous servers.
    ```

    ### IP Hash
    ```
    hash(client_IP) % server_count -> always same server for same IP

    Client 1.2.3.4 -> always Server2
    Client 5.6.7.8 -> always Server1
    Client 9.10.11.12 -> always Server3

    USE: When the application has server-side session state.
         The user must always hit the same server (sticky sessions).
    Problem: if Server2 dies: all 1.2.3.4 clients lose sessions.
             If IP distribution is uneven: hotspots.
    Better: use stateless apps (sessions in Redis) and avoid IP hash.
    ```

    ### Least Response Time
    ```
    Send to server with lowest combination of active connections + average response time.
    Most accurate but more monitoring overhead.
    HAProxy's "server selection based on response time" mode.
    ```

    ---

    ## Health Checks — Removing Failed Servers

    ```
    Load balancer periodically checks if each backend is healthy.
    Unhealthy server: removed from rotation (no traffic sent).
    Recovered server: added back automatically.

    PASSIVE HEALTH CHECK:
      Load balancer observes requests. If responses are errors (5xx) or timeouts:
      mark server as unhealthy. Stop sending traffic after N consecutive failures.
      Problem: real user requests are affected while detecting failure.

    ACTIVE HEALTH CHECK:
      Load balancer sends health check request every 5-30 seconds.
      GET /health -> 200 OK = healthy, anything else = unhealthy.
      Failures detected before user requests are impacted.
      AWS ALB active health checks: /health every 10s, 3 consecutive failures -> unhealthy.

    HEALTH CHECK ENDPOINT BEST PRACTICES:
      /health -> check: DB connection reachable, cache reachable, required config present.
      /ready  -> is app fully initialised and ready to serve traffic?
      /live   -> is the process alive? (simpler, for liveness probe only)
      Return 200 ONLY when truly ready to serve traffic.
      Return 503 if DB is down: load balancer routes to other healthy instances.
    ```

    ---

    ## AWS Load Balancers

    ```
    AWS APPLICATION LOAD BALANCER (ALB):
      Layer 7 HTTP/HTTPS load balancing.
      Content-based routing (by path, host, header, query string).
      WebSocket support.
      gRPC support.
      WAF integration.
      Terminates TLS (certificates via ACM).
      Target types: EC2, ECS tasks, Lambda, IP addresses.
      Use for: web apps, microservices, REST/HTTP APIs.

    AWS NETWORK LOAD BALANCER (NLB):
      Layer 4 TCP/UDP/TLS load balancing.
      Handles millions of requests per second at ultra-low latency.
      Static IP address (or Elastic IP) — needed for whitelisting.
      Preserves client IP address (ALB replaces it).
      Use for: TCP protocols, gaming, financial systems, IoT, cases needing static IP.

    AWS GATEWAY LOAD BALANCER (GWLB):
      Layer 3 — routes traffic through virtual appliances (firewall, IDS, inspection).
      Used for: security appliance insertion in traffic path.
      Less common; specialized use case.

    ALB ROUTING RULES:
      IF path begins with /api/users THEN forward to user-service target group
      IF host is admin.myapp.com THEN forward to admin target group
      IF path begins with /static THEN return 301 redirect to S3 URL
    ```

    ---

    ## Connection Draining (Deregistration Delay)

    ```
    PROBLEM: You want to remove Server1 from the load balancer.
      Existing in-flight requests to Server1 are still being processed.
      Remove immediately: existing requests fail (502 errors for users).

    SOLUTION: Connection draining / graceful removal
      1. Stop sending NEW requests to Server1.
      2. Wait for existing requests to complete (default: 300 seconds).
      3. After drain period: remove server.
      4. In-flight requests complete successfully. No user impact.

    AWS: "Deregistration delay" — configurable on target group.
    nginx upstream: slow_start parameter for gradual weight increase on adding servers.
    ```

    ---

    ## Global Load Balancing — DNS and Anycast

    ```
    SINGLE REGION: Load balancer routes between servers in same datacenter.
    GLOBAL: Route users to nearest/fastest datacenter worldwide.

    DNS-BASED GLOBAL LB:
      api.myapp.com -> Route 53 latency routing:
        User in Tokyo -> resolves to Asia-Pacific datacenter (20ms latency)
        User in London -> resolves to EU datacenter (30ms latency)
        User in NYC -> resolves to US datacenter (10ms latency)

      Downside: DNS caches (TTL 60s) mean failover takes up to 60 seconds.
      For instant failover: reduce TTL before planned maintenance.

    ANYCAST (used by Cloudflare, CDNs):
      Same IP address announced from multiple locations worldwide.
      BGP routing sends user to nearest datacenter automatically.
      Millisecond failover.
      Cloudflare's 1.1.1.1 DNS, their CDN use Anycast.
    ```

    ---

    ## Mind Map

    ```
    LOAD BALANCING
    |
    +-- LAYERS
    |   +-- L4 (TCP): fast, IP+port routing, NLB
    |   +-- L7 (HTTP): smart, content routing, ALB/nginx
    |
    +-- ALGORITHMS
    |   +-- Round Robin (equal distribution, simple)
    |   +-- Weighted Round Robin (heterogeneous servers)
    |   +-- Least Connections (variable request time)
    |   +-- IP Hash (sticky sessions)
    |   +-- Least Response Time (most accurate)
    |
    +-- HEALTH CHECKS
    |   +-- Active (probe /health regularly, detect before user impact)
    |   +-- Passive (observe errors, detect after user impact)
    |
    +-- AWS LBs
    |   +-- ALB (L7, HTTP, path routing, microservices)
    |   +-- NLB (L4, TCP, ultra-low latency, static IP)
    |
    +-- TOPICS
        +-- Connection draining (graceful removal)
        +-- Global LB (DNS routing, Anycast)
        +-- Sticky sessions (session state challenge)
    ```

    ---

    ## References

    ### Videos
    - **Load Balancing Explained** by ByteByteGo:
      https://www.youtube.com/watch?v=K0Ta65OqQkY
      - Visual walkthrough of all algorithms and layer concepts.
    - **AWS ALB vs NLB vs CLB** by Tech with Lucy:
      https://www.youtube.com/watch?v=jRsoJEQjBho
      - AWS-focused comparison of all three load balancer types.

    ### Articles
    - **AWS ALB documentation**: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/
    - **nginx load balancing guide**: https://nginx.org/en/docs/http/load_balancing.html
    """

    LB_Q = [
        {"id":"lb-q4","type":"mcq","prompt":"What is the difference between Layer 4 and Layer 7 load balancing?",
         "choices":["L4 is newer","L4 routes based on IP+port (fast, cannot inspect content). L7 routes based on HTTP headers, URL path, cookies (flexible, can do content-based routing)",
                    "L7 is faster","L4 works only with TCP"],
         "answerIndex":1,"explanation":"L4 (TCP): sees source/dest IP and port, routes packets. Cannot see URL or headers. Very fast. NLB, HAProxy TCP mode. L7 (HTTP): decodes HTTP, can route /api/* to one backend, /static/* to another. Must parse HTTP = slightly slower. ALB, nginx, Traefik.","tags":["load-balancing","l4","l7"]},
        {"id":"lb-q5","type":"mcq","prompt":"When is Least Connections algorithm better than Round Robin?",
         "choices":["When all servers are identical","When requests have variable processing time — Round Robin distributes by count, Least Connections distributes by actual load (active connections)",
                    "Round Robin is always better","For UDP traffic only"],
         "answerIndex":1,"explanation":"Round Robin: fast requests return quickly, slow ones hold slot. Server A gets 100ms requests, Server B gets 10s uploads. Same request count = B massively overloaded. Least Connections: B has many active conns -> avoid it. Adapts to actual in-flight work.","tags":["load-balancing","least-connections","round-robin"]},
        {"id":"lb-q6","type":"mcq","prompt":"What is connection draining in load balancing?",
         "choices":["Closing idle connections","When removing a server, stop sending new requests but wait for in-flight requests to complete before fully removing — prevents error responses for active users",
                    "Reconnecting failed connections","Limiting connection count"],
         "answerIndex":1,"explanation":"Draining: mark server 'draining' -> no new requests. Existing requests complete (AWS: 300s default). No user sees errors. Rolling deployment: drain server 1, deploy new code, add back, drain server 2... Zero-downtime deployments require connection draining.","tags":["load-balancing","connection-draining","deployment"]},
        {"id":"lb-q7","type":"mcq","prompt":"What is an active health check in load balancing?",
         "choices":["The load balancer monitors server metrics","Load balancer sends periodic requests (GET /health) to each backend — detects failures before real user requests are affected",
                    "Server self-reports health","Only triggered by 5xx errors"],
         "answerIndex":1,"explanation":"Active: LB pings /health every 10s. 3 failures -> unhealthy -> removed from pool. Users never hit the failed server. Passive: LB notices 5xx/timeouts from real user requests THEN marks unhealthy. Users see errors during detection window. Always use active health checks.","tags":["load-balancing","health-checks"]},
        {"id":"lb-q8","type":"mcq","prompt":"What does AWS Application Load Balancer (ALB) support that NLB doesn't?",
         "choices":["Higher throughput than NLB","Content-based routing by URL path, host, headers. WebSocket. gRPC. WAF integration. TLS termination. HTTP/2.",
                    "Static IP addresses","Lower latency"],
         "answerIndex":1,"explanation":"ALB (L7): route '/api/users' to user service, '/api/orders' to order service. WAF rules. Sticky sessions via cookie. WebSocket upgrades. NLB (L4): ultra-low latency, static IP, preserves client IP, handles non-HTTP (TCP gameserver, RTMP, custom protocol). NLB: millions of req/sec with microsecond latency.","tags":["load-balancing","alb","nlb","aws"]},
        {"id":"lb-q9","type":"mcq","prompt":"What is a target group in AWS ALB?",
         "choices":["A group of IAM users","A set of targets (EC2 instances, ECS tasks, Lambda functions) that ALB routes traffic to — each target group has its own health checks and port configuration",
                    "A subnet group","A security group"],
         "answerIndex":1,"explanation":"Target group: collection of backends for a specific service. ALB routing rule: if path /api/users -> forward to user-service-tg. Target group: has health check config, deregistration delay, stickiness settings. Multiple target groups = routing different traffic to different services.","tags":["load-balancing","alb","target-group"]},
        {"id":"lb-q10","type":"mcq","prompt":"What is sticky sessions (session affinity) in load balancing?",
         "choices":["Permanent connection to one server","Load balancer uses a cookie or IP hash to always route the same client to the same server — needed for stateful apps that store session in server memory",
                    "Compressed connections","SSL session resumption"],
         "answerIndex":1,"explanation":"Sticky sessions: user logs in -> Session object in Server1's memory. Next request: must go to Server1 (session data not in Server2). LB sets sticky cookie -> routes client to same server. Problem: Server1 dies -> session lost. Better: stateless apps + Redis session store so any server can handle any request.","tags":["load-balancing","sticky-sessions","state"]},
        {"id":"lb-q11","type":"mcq","prompt":"What is DNS-based global load balancing?",
         "choices":["Load balancing using a DNS server","DNS returns different IPs based on client location or latency — users in Tokyo resolve to Asian DC, users in Europe to EU DC",
                    "Load balancing for DNS queries","Round-robin DNS"],
         "answerIndex":1,"explanation":"AWS Route53: latency-based routing -> returns IP of closest region. Users get low-latency connections to nearest datacenter. Failover routing: if primary health check fails -> Route53 returns secondary region. Caveat: DNS TTL = failover can take TTL seconds (set low TTL: 10-30s for HA).","tags":["load-balancing","dns","global"]},
        {"id":"lb-q12","type":"mcq","prompt":"What is the advantage of Weighted Round Robin?",
         "choices":["It's the fastest algorithm","Route proportionally more traffic to more powerful servers — server with 4x CPU gets 4x the requests",
                    "It prevents session loss","It only works with HTTP/2"],
         "answerIndex":1,"explanation":"Weighted RR: servers have weights (power = 4, 2, 1). Out of 7 requests: 4 to Server1, 2 to Server2, 1 to Server3. Matches traffic to capacity. Use during canary deploys: new version weight=5%, old version weight=95%. Gradually shift weight to new version as confidence grows.","tags":["load-balancing","weighted-round-robin"]},
        {"id":"lb-q13","type":"mcq","prompt":"What is Anycast routing and where is it used?",
         "choices":["Broadcasting to all IPs","Same IP address announced from multiple global locations via BGP — client connects to nearest location automatically. Used by Cloudflare, DNS providers.",
                    "IP multicast","AWS PrivateLink"],
         "answerIndex":1,"explanation":"Anycast: 1.1.1.1 (Cloudflare DNS) announced by 300+ PoPs worldwide. Your request goes to nearest BGP node. Failover: if Tokyo PoP fails, BGP re-routes to Singapore in milliseconds. CDNs, DNS resolvers use Anycast. Different from DNS-based: same IP, routing uses BGP instead of different IPs per region.","tags":["load-balancing","anycast","cdn"]},
        {"id":"lb-q14","type":"mcq","prompt":"What is a health check endpoint best practice?",
         "choices":["Always return 200","Return 200 when truly ready to serve traffic (DB reachable, cache connected, initialised). Return 503 when dependencies are down — prevents LB from routing traffic to broken instance.",
                    "Check CPU only","Health checks slow down the server"],
         "answerIndex":1,"explanation":"Good /health: check DB connection, Redis connection, key config values present. If DB down: return 503. LB marks server unhealthy -> removes from pool. Other servers handle traffic. Bad /health: always returns 200 regardless -> LB routes to broken server -> users get errors.","tags":["load-balancing","health-checks","best-practices"]},
        {"id":"lb-q15","type":"mcq","prompt":"What is SSL/TLS termination at the load balancer?",
         "choices":["Load balancer encrypts all traffic","Load balancer handles HTTPS (decrypts TLS), forwards plain HTTP to backends. Backends don't need certificates or TLS overhead.",
                    "A security vulnerability","Splitting SSL across servers"],
         "answerIndex":1,"explanation":"TLS terminates at ALB: one certificate, managed by ACM. Backends: plain HTTP on private network (VPC). TLS overhead (CPU for key exchange) absorbed by LB. Multiple instances: single cert renewal. Can inspect content (WAF). Backend can still do end-to-end encryption if compliance requires.","tags":["load-balancing","tls","termination"]},
        {"id":"lb-q16","type":"mcq","prompt":"What happens to existing user requests when a backend server fails?",
         "choices":["Users must retry manually","Health check detects failure -> LB stops sending new requests. Requests already in-flight to failed server: connection reset/timeout -> client retries. Idempotent GET requests: client retries automatically. POST: need idempotency key for safe retry.",
                    "Requests queued indefinitely","All requests fail permanently"],
         "answerIndex":1,"explanation":"In-flight to failed server: TCP RST or timeout. Retry at LB level (configure: proxy_next_upstream for nginx on connection failure). Idempotent (GET, PUT, DELETE): retry is safe. Non-idempotent (POST creating records): need idempotency key to prevent duplicate creation on retry.","tags":["load-balancing","failure","retry"]},
        {"id":"lb-q17","type":"mcq","prompt":"What is the X-Forwarded-For header in the context of load balancers?",
         "choices":["Authentication token","Chain of proxy IPs: load balancer adds original client IP before forwarding. Backend reads to get real client IP.",
                    "Load balancer heartbeat","Request routing metadata"],
         "answerIndex":1,"explanation":"Without X-Forwarded-For: backend sees LB's internal IP for all requests. Cannot identify clients, rate-limit by IP, geolocate. LB adds: X-Forwarded-For: 203.0.113.45, 10.0.1.1 (client IP, then LB IP). Backend reads first value = real client. NLB preserves client IP natively (no header needed at TCP level).","tags":["load-balancing","x-forwarded-for","headers"]},
        {"id":"lb-q18","type":"mcq","prompt":"What is the main reason to use NLB (Network Load Balancer) over ALB?",
         "choices":["NLB supports HTTP routing","NLB needs static IP, preserves client IP natively, handles millions req/sec at microsecond latency, supports non-HTTP TCP protocols",
                    "NLB is cheaper","NLB has built-in WAF"],
         "answerIndex":1,"explanation":"NLB over ALB: 1) Need static Elastic IP (partner whitelists your LB IP) 2) Non-HTTP protocol (game TCP, RTMP, custom binary) 3) Ultra-low latency (packet-level forwarding, no HTTP parsing) 4) Need client IP without proxy header (NLB passes through). ALB for HTTP microservices.","tags":["load-balancing","nlb","use-case"]},
        {"id":"lb-q19","type":"mcq","prompt":"What is the 'circuit breaker' pattern at the load balancer level?",
         "choices":["Electrical safety feature","Track error rates per backend. If error rate exceeds threshold: stop sending requests (circuit open). After timeout: try again (half-open). If ok: resume (circuit closed).",
                    "A request timeout mechanism","TCP connection limit"],
         "answerIndex":1,"explanation":"Circuit breaker: if Backend2 returns 50% errors in 10s window: open circuit, stop routing to Backend2. After 30s: send one test request. If success: close circuit (resume). If fail: stay open. Prevents cascading failures and avoids retrying a clearly broken backend. Implemented in: Netflix Hystrix, Resilience4j, Envoy proxy.","tags":["load-balancing","circuit-breaker","resilience"]},
        {"id":"lb-q20","type":"mcq","prompt":"What is a canary deployment using load balancer weights?",
         "choices":["Load balancer testing tool","Route small percentage (5%) of traffic to new version while 95% goes to old stable version — monitor new version metrics before full rollout",
                    "Blue-green deployment","Feature flags in code"],
         "answerIndex":1,"explanation":"Canary: weighted routing (new-version: weight=5, old-version: weight=95). 5% of real production traffic hits new version. Monitor: error rate, latency, business metrics. If good: increase to 20%, 50%, 100% gradually. If bad: instantly route 0% to new version. Zero risk, real traffic validation.","tags":["load-balancing","canary","deployment"]},
    ]

    LB_FC = [
        {"id":"lb-fc4","front":"L4 vs L7 load balancing","back":"L4 (TCP): routes by IP+port, cannot inspect content, very fast, NLB. L7 (HTTP): routes by URL/host/headers, content-based routing, TLS termination, WAF, ALB/nginx. Use L7 for web/APIs. Use L4 for TCP protocols, ultra-low latency, static IP needs.","tags":["load-balancing","l4","l7"]},
        {"id":"lb-fc5","front":"Algorithm selection guide","back":"Round Robin: homogeneous servers, similar request times. Least Connections: variable request duration (uploads, long queries). Weighted RR: heterogeneous server capacity or canary deployments. IP Hash: stateful app needing sticky sessions (prefer stateless + Redis instead).","tags":["load-balancing","algorithms"]},
        {"id":"lb-fc6","front":"AWS ALB vs NLB","back":"ALB: L7 HTTP(S), path/host routing, WAF, WebSocket, gRPC, TLS termination, microservices. NLB: L4 TCP/UDP, millions req/sec, microsecond latency, static IP, preserves client IP, non-HTTP protocols. Default web app: ALB. Need static IP or non-HTTP: NLB.","tags":["load-balancing","alb","nlb"]},
        {"id":"lb-fc7","front":"Health check endpoint best practice","back":"GET /health: check DB connection + Redis + config. Return 200 if all ok, 503 if any dependency down. Return quickly (< 500ms). Don't require auth. LB health check every 10s, 3 failures = unhealthy, routing stops. Routes resume when 2 consecutive health checks pass.","tags":["load-balancing","health-checks"]},
        {"id":"lb-fc8","front":"Connection draining for zero-downtime deploy","back":"Mark server draining -> LB stops NEW requests. Existing in-flight requests complete (AWS default: 300s). Scale down or deploy new version. Add server back. Health check passes -> gets traffic again. Rolling deploy: drain 1 at a time. Never 0 healthy servers.","tags":["load-balancing","connection-draining","deployment"]},
    ]

    d['guide'] = LB_GUIDE
    existing_ids = {q['id'] for q in d['questions']}
    for q in LB_Q:
        if q['id'] not in existing_ids:
            d['questions'].append(q)
    existing_fc_ids = {fc['id'] for fc in d['flashcards']}
    for fc in LB_FC:
        if fc['id'] not in existing_fc_ids:
            d['flashcards'].append(fc)
    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"load-balancing.json: guide={len(LB_GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ─────────────────────────────────────────────────────────────────────────────
    # LONG POLLING + FTP — smaller guides, full questions
    # ─────────────────────────────────────────────────────────────────────────────
    for fname, existing_q_count in [('long-polling.json', 3), ('ftp.json', 3)]:
        p = BASE / fname
        d = json.loads(p.read_text())
        extra_q = []
        extra_fc = []

        if fname == 'long-polling.json':
            prefix = 'lp'
            extra_q = [
                {"id":f"{prefix}-q4","type":"mcq","prompt":"What is the main advantage of long polling over short polling?",
                 "choices":["It uses less CPU on client","Server holds the request until data is available — client gets near-real-time updates without empty responses, reducing wasted API calls",
                            "It is bidirectional","It uses less bandwidth always"],
                 "answerIndex":1,"explanation":"Short poll: client asks every second, server says 'no data' 59 times, 'data!' once per minute. 60 requests for 1 useful response. Long poll: client asks, server waits up to 30s for data. 2 requests for 1 response. Much more efficient.","tags":["long-polling","efficiency"]},
                {"id":f"{prefix}-q5","type":"mcq","prompt":"What is the reconnect flow in long polling after a response?",
                 "choices":["Client disconnects permanently","Server sends response -> client immediately sends new request -> new long-poll cycle begins -> maintains near-continuous connection",
                            "Server keeps connection open","Client waits 60 seconds then reconnects"],
                 "answerIndex":1,"explanation":"Long poll cycle: 1) Client sends GET /updates?lastId=100. 2) Server waits. 3) New data -> server responds with data. 4) Client processes data. 5) Client immediately sends GET /updates?lastId=101. Near-real-time with standard HTTP. Connection is technically new each cycle.","tags":["long-polling","reconnect"]},
                {"id":f"{prefix}-q6","type":"mcq","prompt":"What server resource does long polling use that short polling doesn't?",
                 "choices":["More CPU","Server thread or connection slot held open while waiting — at 10,000 concurrent long-poll clients, 10,000 server threads/connections are occupied (C10K problem)",
                            "More disk I/O","More network bandwidth"],
                 "answerIndex":1,"explanation":"Long poll holds a connection open. At scale: 10K clients = 10K open connections. Traditional thread-per-connection: 10K threads = high memory. Async I/O (Node.js, Nginx, async Java) handles this well — connections are cheap, IO is async. WebSocket is similar but more efficient for high-frequency updates.","tags":["long-polling","scalability","c10k"]},
                {"id":f"{prefix}-q7","type":"mcq","prompt":"When should you use long polling vs WebSocket?",
                 "choices":["Always use WebSocket","Long polling: works on any HTTP infrastructure, simpler to implement, good for low-frequency updates. WebSocket: bidirectional, lower overhead for high-frequency updates, requires WebSocket support.",
                            "Long polling is outdated","WebSocket doesn't work in browsers"],
                 "answerIndex":1,"explanation":"Long polling: pure HTTP, works through all proxies/firewalls, no special server config, good for: notifications (few updates/hour), fallback when WebSocket fails. WebSocket: better for chat/games (many updates/second, bidirectional). socket.io uses long polling as fallback if WebSocket blocked.","tags":["long-polling","websocket","comparison"]},
                {"id":f"{prefix}-q8","type":"mcq","prompt":"What HTTP timeout can break long polling?",
                 "choices":["SSL handshake timeout","Network proxy or load balancer timeout — if request sits open longer than proxy's idle timeout (e.g., 60s), connection is closed. Server must respond within timeout.",
                            "DNS timeout","TCP keepalive timeout"],
                 "answerIndex":1,"explanation":"Nginx default: proxy_read_timeout 60s. If server holds long poll > 60s -> nginx closes connection -> client gets error. Fix: set long poll max wait < proxy timeout, or increase proxy timeout. Client receives empty response on timeout and reconnects. This is expected behavior.","tags":["long-polling","timeout","proxy"]},
                {"id":f"{prefix}-q9","type":"mcq","prompt":"What is the difference between long polling and SSE (Server-Sent Events)?",
                 "choices":["They are identical","Long polling: client makes request, server holds, responds with data, connection closes, client reconnects. SSE: single HTTP connection stays open, server streams multiple events without reconnects.",
                            "SSE requires WebSocket","Long polling is more efficient"],
                 "answerIndex":1,"explanation":"Long poll: request -> wait -> response -> close -> new request. One round-trip overhead per batch of events. SSE: connect once -> server pushes events continuously on same connection. Much more efficient for frequent server-push. SSE has automatic reconnect built into EventSource API.","tags":["long-polling","sse","comparison"]},
                {"id":f"{prefix}-q10","type":"mcq","prompt":"What is a 'timeout response' in long polling?",
                 "choices":["Server errors on timeout","After max wait time (e.g., 30s), server sends empty response. Client immediately reconnects. Prevents proxy timeouts and signals 'no new data yet'.",
                            "Rate limiting response","WebSocket upgrade"],
                 "answerIndex":1,"explanation":"Long poll server logic: if new data arrives within 30s -> respond with data. If 30s passes with no data -> respond with {status: 'no-update'} or HTTP 204. Client reconnects immediately. This is normal behavior, not an error. Prevents the connection from being closed by intermediary proxies.","tags":["long-polling","timeout","implementation"]},
                {"id":f"{prefix}-q11","type":"mcq","prompt":"Which real-world applications use long polling?",
                 "choices":["Streaming video","Facebook Messenger (historically), GitHub issue notifications, many webhooks, legacy chat applications before WebSocket was widespread",
                            "File downloads","Database replication"],
                 "answerIndex":1,"explanation":"Facebook Messenger used Comet/long polling before WebSocket. GitHub activity feed uses it. JIRA real-time updates. Many systems use long polling as: primary real-time mechanism for low-frequency updates, or fallback when WebSocket is blocked by corporate firewalls.","tags":["long-polling","examples","real-world"]},
                {"id":f"{prefix}-q12","type":"mcq","prompt":"What is 'Comet' in web development history?",
                 "choices":["A JavaScript framework","A web programming model from ~2006-2010 enabling server push via long polling and streaming techniques — the predecessor to WebSocket",
                            "A CSS animation library","A database driver"],
                 "answerIndex":1,"explanation":"Comet (2006): Alex Russell coined term for browser-based real-time via long-held HTTP requests. Techniques: long polling, HTTP streaming (forever iframe). Predated WebSocket (standardised 2011). Enabled: Google Finance live updates, early chat apps. superseded by WebSocket and SSE.","tags":["long-polling","history","comet"]},
                {"id":f"{prefix}-q13","type":"mcq","prompt":"How does passing `lastId` or `lastEventId` in long poll requests help?",
                 "choices":["Authentication token","Client tells server which events it already has. Server returns only NEW events since that ID. Prevents sending duplicates on reconnect.",
                            "Rate limiting parameter","Cache key"],
                 "answerIndex":1,"explanation":"GET /updates?since=100: server returns events with id > 100. Client receives [event101, event102]. Next request: GET /updates?since=102. On reconnect after disconnect: client resumes from last seen ID. No duplicate events, no missed events. Critical for reliable long polling.","tags":["long-polling","event-id","reliability"]},
                {"id":f"{prefix}-q14","type":"mcq","prompt":"What is the 'C10K problem' and how does it relate to long polling?",
                 "choices":["10,000 cache keys","The challenge of handling 10,000 concurrent client connections efficiently. Long polling at scale requires async I/O to avoid 10K blocking threads.",
                            "10K database connections","10K API keys"],
                 "answerIndex":1,"explanation":"C10K: 10,000 concurrent connections. Thread-per-connection: 10K threads * 1MB stack = 10GB memory. Solution: async event loop (Node.js, Nginx, async Java/Python). One thread handles thousands of open connections via non-blocking I/O. Long poll, WebSocket, SSE all require C10K-style async server to scale.","tags":["long-polling","c10k","scalability"]},
                {"id":f"{prefix}-q15","type":"mcq","prompt":"What is 'short polling' and when is it acceptable despite inefficiency?",
                 "choices":["Polling with very fast responses","Client sends request every N seconds regardless of whether data exists. Simple to implement, universally works, acceptable for: low-frequency updates where latency doesn't matter (dashboard refreshing every 30s).",
                            "UDP-based polling","Polling with compression"],
                 "answerIndex":1,"explanation":"Short polling: every 30 seconds check for new data. Acceptable when: very low-frequency updates (hourly report), simple dashboards, latency doesn't matter (30s old data is ok), infrastructure doesn't support WebSocket. Not acceptable when: real-time chat, live scores, high-frequency updates.","tags":["long-polling","short-polling","trade-offs"]},
                {"id":f"{prefix}-q16","type":"mcq","prompt":"What is the recommended modern alternative to long polling for server-to-client real-time data?",
                 "choices":["Short polling","GraphQL subscriptions only","Server-Sent Events (SSE) for one-way push or WebSocket for bidirectional — both more efficient than long polling",
                            "REST callbacks"],
                 "answerIndex":2,"explanation":"SSE: persistent HTTP connection, browser EventSource API, automatic reconnect, event IDs for resumption, efficient for server-push. WebSocket: bidirectional real-time. Both supersede long polling. Long polling: still valid as fallback or when SSE/WS not available.","tags":["long-polling","sse","websocket","modern"]},
                {"id":f"{prefix}-q17","type":"mcq","prompt":"What HTTP method is typically used for long polling requests?",
                 "choices":["POST","PUT","GET — long poll is a read operation. Client fetches updates. Server responds when updates are available or timeout occurs.",
                            "OPTIONS"],
                 "answerIndex":2,"explanation":"GET /updates?since=100 HTTP/1.1: standard GET request held open by server. Responses are cacheable by default (but must be prevented with Cache-Control: no-cache to avoid stale data). GET is correct: we're reading data (updates), not creating/modifying anything.","tags":["long-polling","http-method"]},
                {"id":f"{prefix}-q18","type":"mcq","prompt":"How does long polling affect load balancer configuration?",
                 "choices":["No impact","Long-held connections require: increased idle timeout on load balancer, possibly sticky sessions (if server state is per-connection), monitoring of connection count not just RPS",
                            "Long polling breaks load balancers","Requires UDP protocol"],
                 "answerIndex":1,"explanation":"ALB default timeout: 60 seconds for idle connections. Long polling requests held 30s: fine. Held 90s: LB closes at 60s -> error. Fix: ALB idle timeout > long poll max wait. Also: sticky sessions if connection state on server. Monitor: active connection count (not just req/sec) to detect scaling needs.","tags":["long-polling","load-balancing","configuration"]},
                {"id":f"{prefix}-q19","type":"mcq","prompt":"What does the server return when no new data is available after the max wait in long polling?",
                 "choices":["503 Service Unavailable","HTTP 200 with empty body or 204 No Content — signals 'no new data yet', client reconnects immediately",
                            "426 Upgrade Required","408 Request Timeout"],
                 "answerIndex":1,"explanation":"Empty long poll response: 200 {} or 204 No Content. This is NOT an error. Client: receives empty response, immediately sends new long poll request. Cycle continues. 408 (Request Timeout) is also sometimes used but 200/204 with empty body is cleaner. Client must handle both.","tags":["long-polling","empty-response"]},
                {"id":f"{prefix}-q20","type":"mcq","prompt":"What is the bandwidth comparison between short polling every 1s vs long polling for 1 update per minute?",
                 "choices":["They use the same bandwidth","Short polling: 60 empty responses/minute. Long polling: ~2 responses/minute (1 data + 1 timeout reconnect). ~30x less bandwidth with long polling.",
                            "Long polling uses more","Depends on payload size only"],
                 "answerIndex":1,"explanation":"Short poll 1/sec: 60 requests, 60 responses per minute. 59 empty responses, 1 with data. Long poll: 1 request held open for up to 30s. Data arrives at 1/min: 2 responses (data response + reconnect) per minute. 30x fewer request/response cycles means 30x less HTTP overhead.","tags":["long-polling","bandwidth","comparison"]},
            ]
            extra_fc = [
                {"id":f"{prefix}-fc4","front":"Short vs long polling vs SSE vs WebSocket","back":"Short poll: simplest, wastes bandwidth (empty responses). Long poll: near real-time with HTTP, reconnects per update. SSE: persistent connection, server push only, auto-reconnect. WebSocket: bidirectional, best for high-frequency two-way. Order of complexity/efficiency: short -> long -> SSE -> WS.","tags":["long-polling","polling","websocket","sse"]},
                {"id":f"{prefix}-fc5","front":"Long polling reconnect cycle","back":"1. Client: GET /updates?since=lastId. 2. Server: hold open up to 30s. 3a. Data arrives: respond with data, close. Client: immediate new request with new lastId. 3b. Timeout: respond empty (204). Client: immediate new request same lastId.","tags":["long-polling","reconnect"]},
                {"id":f"{prefix}-fc6","front":"Long polling proxy timeout issue","back":"Nginx default proxy_read_timeout: 60s. If long poll max wait > 60s: nginx closes -> client error. Fix: set long poll max wait to 25-45s (< proxy timeout). Or increase proxy timeout. Config: proxy_read_timeout 90s; Always keep long poll timeout below all proxy timeouts in the chain.","tags":["long-polling","nginx","timeout"]},
                {"id":f"{prefix}-fc7","front":"Long polling vs WebSocket decision","back":"Long polling: pure HTTP (traverses all proxies/firewalls), low-frequency updates (notifications, alerts), fallback for WS. WebSocket: high-frequency bidirectional (chat, games), lower overhead per message. socket.io: uses WS with long-poll fallback.","tags":["long-polling","websocket"]},
                {"id":f"{prefix}-fc8","front":"Async server requirement for long polling at scale","back":"Thread-per-connection: 10K long-poll clients = 10K threads = ~10GB memory. Impractical. Async I/O: Node.js event loop, Nginx, async Java (Netty/WebFlux), Python asyncio. One thread handles thousands of open connections. C10K problem solved with async.","tags":["long-polling","c10k","async"]},
            ]
        elif fname == 'ftp.json':
            prefix = 'ftp'
            extra_q = [
                {"id":f"{prefix}-q4","type":"mcq","prompt":"What are the two channels FTP uses and what does each do?",
                 "choices":["Encrypt and decrypt channels","Control channel (port 21): commands and responses. Data channel (port 20 or ephemeral): actual file transfer data. Two separate TCP connections.",
                            "Upload and download channels","Client and server channels"],
                 "answerIndex":1,"explanation":"FTP is unique: two separate TCP connections. Control channel (port 21): authenticate, send commands (LIST, RETR, STOR). Data channel: opened per transfer on port 20 (active) or ephemeral port (passive). This dual-channel design causes NAT/firewall complications.","tags":["ftp","protocol","channels"]},
                {"id":f"{prefix}-q5","type":"mcq","prompt":"What is the difference between FTP active mode and passive mode?",
                 "choices":["Active is encrypted, passive is not","Active: server initiates data connection TO client (breaks NAT). Passive: client initiates data connection to server (NAT-friendly). Always use passive mode.",
                            "Active is faster","Passive requires VPN"],
                 "answerIndex":1,"explanation":"Active FTP: client on port 1234, server connects back to client:1234 for data. NAT gateway blocks inbound connection from server. Passive FTP: server opens random high port, tells client 'connect to me here'. Client initiates. NAT allows outbound connections. Always configure FTP server for passive mode.","tags":["ftp","active","passive","nat"]},
                {"id":f"{prefix}-q6","type":"mcq","prompt":"What security problem does standard FTP have?",
                 "choices":["FTP uses too much bandwidth","FTP transmits credentials and data in PLAINTEXT — passwords, file contents visible to network sniffers. SFTP or FTPS should be used instead.",
                            "FTP is too slow","FTP has no authentication"],
                 "answerIndex":1,"explanation":"FTP: username, password, and all file content sent as plaintext over TCP. Anyone on the network path can read them with Wireshark/tcpdump. Never use FTP over public internet. Replace with: SFTP (SSH File Transfer Protocol, encrypted) or FTPS (FTP + TLS, encrypted).","tags":["ftp","security","plaintext"]},
                {"id":f"{prefix}-q7","type":"mcq","prompt":"What is SFTP and how does it differ from FTP?",
                 "choices":["FTP with SSL (same protocol different transport)","SFTP is a completely different protocol that runs over SSH — fully encrypted, single channel (no firewall issues), uses port 22. Not related to FTP despite the name.",
                            "Secure FTP with added headers","FTP over port 443"],
                 "answerIndex":1,"explanation":"SFTP ≠ FTP + SSL. SFTP is the SSH File Transfer Protocol — a completely new protocol built into SSH. Single TCP connection on port 22. Everything encrypted. Firewall-friendly (one port). FTPS is FTP + TLS (still two channels, still port 21/20). SFTP is generally recommended over FTPS.","tags":["ftp","sftp","ssh","security"]},
                {"id":f"{prefix}-q8","type":"mcq","prompt":"What is FTPS?",
                 "choices":["SFTP with a different name","FTP secured with TLS — either Explicit FTPS (starts as FTP, upgrades with AUTH TLS) or Implicit FTPS (TLS from first connection on port 990). Encrypts FTP traffic.",
                            "FTP over UDP","FTP with compression"],
                 "answerIndex":1,"explanation":"FTPS: standard FTP protocol + TLS encryption. Still uses control and data channels (NAT still an issue). Explicit: connects on 21, client sends AUTH TLS to upgrade. Implicit: port 990, TLS from start. More complex than SFTP due to dual channels and TLS certificate management.","tags":["ftp","ftps","tls","security"]},
                {"id":f"{prefix}-q9","type":"mcq","prompt":"Why is FTP still used despite its security issues?",
                 "choices":["It's the most secure protocol","Legacy system compatibility, some B2B integrations still require it, managed file transfer (MFT) solutions use it. Always use SFTP/FTPS in any new deployment.",
                            "FTP is modern","FTP is faster than alternatives"],
                 "answerIndex":1,"explanation":"FTP persists due to: legacy systems that can't be updated (AS400, mainframes), some payment processors/banks that mandated it decades ago, automated batch file transfers between companies. For any new system: use SFTP. For legacy: at minimum use FTPS to add encryption.","tags":["ftp","legacy","use-cases"]},
                {"id":f"{prefix}-q10","type":"mcq","prompt":"What port does SFTP use?",
                 "choices":["21","990","22 (same as SSH — SFTP is an SSH subsystem)",
                            "8021"],
                 "answerIndex":2,"explanation":"SFTP runs on port 22 (SSH port). SFTP is literally an SSH subsystem — sshd handles SFTP connections. No separate FTP server needed. Client: sftp user@server or use GUI like FileZilla (protocol: SFTP). Single port = simple firewall rule: allow TCP 22.","tags":["ftp","sftp","port"]},
                {"id":f"{prefix}-q11","type":"mcq","prompt":"What FTP command is used to transfer a file from server to client?",
                 "choices":["STOR","GET","RETR (retrieve) — sent on control channel, triggers opening data channel, server sends file bytes",
                            "PUSH"],
                 "answerIndex":2,"explanation":"FTP commands on control channel: USER/PASS (auth), LIST (directory listing), RETR filename (download), STOR filename (upload), DELE filename (delete), MKD dirname (create directory), PWD (print working directory), PASV (enter passive mode). QUIT (disconnect).","tags":["ftp","commands","protocol"]},
                {"id":f"{prefix}-q12","type":"mcq","prompt":"What is anonymous FTP?",
                 "choices":["FTP without encryption","FTP server allowing login with username 'anonymous' and any email as password — used for public file distribution (old software, patches). Never for sensitive data.",
                            "FTP over Tor","FTP with no password at all"],
                 "answerIndex":1,"explanation":"Anonymous FTP: username='anonymous', password=any string (email by convention). Used by: old software mirrors, public patch distribution, RFC archive (ftp.ietf.org historically). No private data should ever be accessible via anonymous FTP. Most modern public distribution uses HTTP/CDN instead.","tags":["ftp","anonymous","public"]},
                {"id":f"{prefix}-q13","type":"mcq","prompt":"What is SCP (Secure Copy) and how does it relate to SFTP?",
                 "choices":["Symmetric Cryptographic Protocol","SCP uses SSH to securely copy files between hosts. Simpler than SFTP (no interactive session, just copy). Both encrypted via SSH. SFTP: interactive (list, navigate, rename). SCP: one-time copy operation.",
                            "A network protocol","FTP over SSH"],
                 "answerIndex":1,"explanation":"SCP: scp file.txt user@server:/path/. Simple non-interactive copy. SFTP: sftp user@server -> interactive: ls, cd, get, put, rm. Use SCP for scripts/automation. Use SFTP for interactive file management. Both use port 22, both SSH-encrypted. SCP is deprecated in OpenSSH; use sftp or rsync instead.","tags":["ftp","sftp","scp","ssh"]},
                {"id":f"{prefix}-q14","type":"mcq","prompt":"What is the FTP PASV command?",
                 "choices":["Pause transfer","Client sends PASV to ask server to enter passive mode — server responds with IP:port for client to connect to for data channel. NAT-friendly.",
                            "Set passive file permissions","Password validation"],
                 "answerIndex":1,"explanation":"PASV flow: client sends PASV. Server: '227 Entering Passive Mode (10,0,1,5,195,80)' = IP 10.0.1.5, port 195*256+80=50000. Client opens TCP connection to 10.0.1.5:50000. Client initiates data connection = works through NAT. EPSV (Extended Passive) = IPv6-compatible version.","tags":["ftp","passive","pasv","nat"]},
                {"id":f"{prefix}-q15","type":"mcq","prompt":"How should you transfer sensitive files between servers today instead of FTP?",
                 "choices":["Anonymous FTP","SFTP (SSH File Transfer Protocol), FTPS (FTP+TLS), or managed file transfer (MFT) solutions like AWS Transfer Family for S3 integration. For ad-hoc: scp or rsync over SSH.",
                            "Email attachment","Standard FTP with strong password"],
                 "answerIndex":1,"explanation":"Never FTP for sensitive data. SFTP: easiest, uses existing SSH infrastructure. FTPS: if FTP is mandated (legacy). Cloud: AWS Transfer Family (managed SFTP/FTPS endpoint directly to S3). rsync over SSH: for large sync operations. Strong password doesn't protect FTP — everything including the password is still in plaintext.","tags":["ftp","security","modern-alternatives"]},
                {"id":f"{prefix}-q16","type":"mcq","prompt":"What is binary vs ASCII transfer mode in FTP?",
                 "choices":["Binary is encrypted, ASCII is not","Binary mode: transfers file byte-for-byte (for images, executables, archives). ASCII mode: translates line endings (LF/CRLF) between OS types. Using wrong mode corrupts files.",
                            "They are the same in modern FTP","ASCII mode uses more bandwidth"],
                 "answerIndex":1,"explanation":"FTP was designed cross-platform. ASCII mode: convert \\n (Unix) to \\r\\n (Windows) on transfer. OK for text files between mixed OS. Binary/Image mode: exact byte copy, no translation. Always use binary for: zip files, images, executables, databases. ASCII for text files (if needed). Modern FTP clients default to binary.","tags":["ftp","binary","ascii","modes"]},
                {"id":f"{prefix}-q17","type":"mcq","prompt":"What is AWS Transfer Family?",
                 "choices":["A file migration service","Managed SFTP/FTPS/FTP server that puts files directly into S3 or EFS — clients use standard SFTP clients, no server to manage",
                            "A network routing service","An IoT protocol"],
                 "answerIndex":1,"explanation":"AWS Transfer Family: managed endpoint for SFTP/FTPS. Partner sends file to your SFTP endpoint -> file lands in S3 bucket automatically. No EC2, no SSH server management. Set up DNS: sftp.company.com -> Transfer Family endpoint. IAM role controls which S3 prefix each SFTP user can access.","tags":["ftp","sftp","aws","s3"]},
                {"id":f"{prefix}-q18","type":"mcq","prompt":"What is rsync and how does it improve on SCP for file transfer?",
                 "choices":["A replacement for FTP","Delta transfer: only sends CHANGED bytes (not entire file). Over SSH: encrypted. Resumable. Preserves permissions, timestamps. Faster than SCP for large or frequently-updated files.",
                            "A real-time sync protocol","Encrypted FTP client"],
                 "answerIndex":1,"explanation":"rsync: rsync -avz --delete /local/ user@server:/remote/. Delta algorithm: compare local and remote checksums at block level, send only changed blocks. 1GB file with 1KB change: transfers ~10KB not 1GB (if already synced). Over SSH (rsync -e ssh): encrypted. For backups and deployments: rsync is far superior to scp.","tags":["ftp","sftp","rsync","delta"]},
                {"id":f"{prefix}-q19","type":"mcq","prompt":"What firewall ports must be open for an FTP server in passive mode?",
                 "choices":["Port 21 only","Port 21 (control channel) AND a range of high ports for data connections (e.g., 50000-51000) — server must be configured to use only this range for passive data channels",
                            "Ports 20 and 21 only","Ports 22 and 21"],
                 "answerIndex":1,"explanation":"Passive FTP: server opens random high port for each data transfer. Firewall must allow inbound to all possible random ports = security nightmare. Solution: configure FTP server with fixed passive port range (pasv_min_port=50000, pasv_max_port=51000). Open only that range in firewall. SFTP: only port 22 needed.","tags":["ftp","passive","firewall","ports"]},
                {"id":f"{prefix}-q20","type":"mcq","prompt":"What is the difference between SFTP and FTPS in terms of channel architecture?",
                 "choices":["SFTP has two channels, FTPS has one","SFTP: single SSH channel (port 22, simple firewall). FTPS: two channels like FTP (control on 21 + data channels), TLS over each. SFTP is simpler to firewall and operationally.",
                            "They are architecturally identical","FTPS is more secure than SFTP"],
                 "answerIndex":1,"explanation":"SFTP: one TCP connection on port 22. Open port 22 in firewall. Done. FTPS: still TCP 21 for control + separate data connections (passive range or active mode). Must configure TLS on both channels. More complex. Firewall: must allow range of data ports. SFTP operationally simpler than FTPS.","tags":["ftp","sftp","ftps","comparison"]},
            ]
            extra_fc = [
                {"id":f"{prefix}-fc3","front":"FTP active vs passive mode","back":"Active: server initiates data connection TO client -> FAILS behind NAT. Passive: client connects TO server data port -> NAT friendly. Always configure servers for passive mode. Configure fixed passive port range, open only that range in firewall.","tags":["ftp","active","passive","nat"]},
                {"id":f"{prefix}-fc4","front":"FTP vs SFTP vs FTPS","back":"FTP: plaintext, dual channel, legacy only. SFTP: SSH subsystem, port 22, encrypted, single channel, recommended. FTPS: FTP + TLS, still dual channel, complex. For new systems: SFTP always. Legacy requirement: FTPS. Never plain FTP over internet.","tags":["ftp","sftp","ftps","security"]},
                {"id":f"{prefix}-fc5","front":"SFTP in practice","back":"sftp user@host (interactive). sftp user@host:/remote/file ./local/ (get). sftp -b batchfile user@host (scripted). Port 22, same as SSH. Uses SSH key auth (no password). AWS Transfer Family: managed SFTP endpoint pointing to S3.","tags":["ftp","sftp","commands"]},
                {"id":f"{prefix}-fc6","front":"AWS Transfer Family","back":"Managed SFTP/FTPS endpoint -> S3 or EFS. No server to manage. DNS: sftp.company.com -> Transfer Family. IAM controls S3 access per user. B2B file transfer without managing EC2+SSH server+SFTP software.","tags":["ftp","aws","s3","transfer-family"]},
                {"id":f"{prefix}-fc7","front":"rsync vs scp","back":"scp: always copies full file, no resume, slower for large files. rsync: delta algorithm (only changed blocks), resumable, preserves permissions/timestamps, --delete to sync deletions. rsync -avz --delete source/ user@host:dest/ Use rsync for backups and deployments.","tags":["ftp","rsync","scp"]},
                {"id":f"{prefix}-fc8","front":"FTP security rule","back":"FTP password = plaintext over network. NEVER use FTP for: sensitive files, credentials, tokens, PII. Replace with SFTP (port 22, SSH-encrypted). Audit any existing FTP usage. Legacy systems: wrap in FTPS at minimum. Modern cloud: S3 pre-signed URLs or AWS Transfer Family.","tags":["ftp","security","plaintext"]},
            ]

        existing_ids = {q['id'] for q in d['questions']}
        for q in extra_q:
            if q['id'] not in existing_ids:
                d['questions'].append(q)
        existing_fc_ids = {fc['id'] for fc in d['flashcards']}
        for fc in extra_fc:
            if fc['id'] not in existing_fc_ids:
                d['flashcards'].append(fc)
        with open(p, 'w') as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        print(f"{fname}: guide={len(d['guide'])} q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ── patch_ws_extra.py ──────────────────────────────────────────────────────────────────
    p = Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics/networking/websockets.json')
    d = json.loads(p.read_text())

    extra = [
        {"id":"ws-q16","type":"mcq","prompt":"What is WebSocket subprotocol negotiation?",
         "choices":["A security handshake","Sec-WebSocket-Protocol header lets client propose protocols (e.g., 'chat', 'mqtt'). Server selects one. Allows typed communication on same WS endpoint.",
                    "Load balancing protocol","Compression negotiation"],
         "answerIndex":1,"explanation":"Client: Sec-WebSocket-Protocol: chat, superchat. Server: Sec-WebSocket-Protocol: chat (picks one). Both sides then speak that sub-protocol. MQTT over WebSocket uses this. socket.io namespaces are the application-level equivalent.","tags":["websockets","subprotocol"]},
        {"id":"ws-q17","type":"mcq","prompt":"What tool is used to test WebSocket connections from the command line?",
         "choices":["curl","wscat (npm install -g wscat) — wscat -c ws://localhost:8080 opens interactive WS session",
                    "telnet only","netcat only"],
         "answerIndex":1,"explanation":"wscat: wscat -c ws://localhost:8080. Interactive: type messages, see server responses in real time. Browser DevTools: Network tab, WS filter, click connection, Messages tab. Postman also supports WebSocket testing.","tags":["websockets","testing"]},
        {"id":"ws-q18","type":"mcq","prompt":"What does the permessage-deflate WebSocket extension do?",
         "choices":["Encrypts WebSocket frames","Compresses each WebSocket frame using DEFLATE — reduces bandwidth 60-80% for JSON/text payloads. Negotiated in handshake headers.",
                    "Limits message size","Splits large messages"],
         "answerIndex":1,"explanation":"permessage-deflate: Sec-WebSocket-Extensions: permessage-deflate in handshake. Both sides compress each message frame. JSON (highly repetitive text) compresses well. Trade-off: CPU overhead. Enable for high-volume chat/analytics. Not needed for binary audio/video streams (already compressed).","tags":["websockets","compression","performance"]},
        {"id":"ws-q19","type":"mcq","prompt":"What happens to open WebSocket connections when a server node is restarted during a rolling deployment?",
         "choices":["Connections migrate automatically","Connections are terminated. Clients receive onclose event and must reconnect. Best practice: graceful shutdown sends WS close frame before process exit.",
                    "Load balancer re-routes transparently","Connections buffered and replayed"],
         "answerIndex":1,"explanation":"Rolling deploy: drain HTTP connections + WebSocket connections. Graceful: send WS close frame (code 1001 Going Away) -> client gets clean close, reconnects to healthy node. Without graceful close: abrupt TCP RST. Client reconnect logic must handle both cases with exponential backoff.","tags":["websockets","deployment","reconnect"]},
        {"id":"ws-q20","type":"mcq","prompt":"Does WebSocket guarantee message ordering?",
         "choices":["No, messages may arrive out of order","Yes — WebSocket runs on TCP which guarantees in-order delivery on a single connection. Messages arrive in the order sent.",
                    "Only with sequence numbers","Only in binary mode"],
         "answerIndex":1,"explanation":"TCP: ordered, reliable delivery. WebSocket on TCP inherits ordering. Messages sent 1,2,3 arrive 1,2,3 on same connection. Cross-connection ordering (reconnects): not guaranteed. After reconnect add application-level sequence numbers to detect any gaps caused by disconnect.","tags":["websockets","ordering","tcp"]},
    ]

    existing_ids = {q['id'] for q in d['questions']}
    for q in extra:
        if q['id'] not in existing_ids:
            d['questions'].append(q)

    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"websockets.json: q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ── fix_ftp_guide.py ──────────────────────────────────────────────────────────────────
    """
    Fix last thin topic: networking/ftp.json — expand guide to proper length.
    Run: python3 scripts/fix_ftp_guide.py
    """
    import json
    from pathlib import Path

    p = Path(__file__).parent.parent / "src/content/topics/networking/ftp.json"
    d = json.loads(p.read_text())

    FTP_GUIDE = "\n".join([
        "# FTP — File Transfer Protocol",
        "",
        "## What Is FTP and Why Does It Still Exist?",
        "",
        "FTP (File Transfer Protocol) is one of the oldest internet protocols still in use, dating from 1971.",
        "It transfers files between computers over a TCP/IP network. You'll encounter it when:",
        "- Deploying websites to shared hosting servers",
        "- Transferring large files to/from legacy enterprise systems",
        "- Working with scientific or government data archives",
        "- Understanding network security (FTP is often cited as an insecure protocol to avoid or harden)",
        "",
        "```",
        "Modern alternatives to plain FTP:",
        "  SFTP (SSH File Transfer Protocol)  ← use this by default — encrypted",
        "  FTPS (FTP over TLS/SSL)            ← encrypted FTP, for legacy FTP servers",
        "  SCP (Secure Copy Protocol)         ← simple file copy over SSH",
        "  HTTPS (S3, presigned URLs)         ← for web-based file transfer",
        "",
        "Plain FTP:  credentials sent in cleartext, never use over the internet",
        "SFTP/FTPS:  encrypted, safe — these are what you'll actually use",
        "```",
        "",
        "---",
        "",
        "## How FTP Works — The Two-Channel Architecture",
        "",
        "FTP is unusual: it uses TWO separate TCP connections, not one.",
        "",
        "```",
        "FTP CLIENT                    FTP SERVER",
        "     │                              │",
        "     │──── Control Channel ────────►│  (port 21)",
        "     │     Commands + responses     │",
        "     │     USER alice               │",
        "     │     PASS mypassword          │",
        "     │     LIST /files              │",
        "     │     RETR document.pdf        │",
        "     │                              │",
        "     │◄─── Data Channel ───────────►│  (port 20 active, random port passive)",
        "          Actual file content            ",
        "          Directory listings             ",
        "",
        "TWO CHANNELS:",
        "  Control channel (port 21): always open during session, sends commands",
        "  Data channel:              opened on-demand for each file transfer or directory listing",
        "  After transfer completes:  data channel closed, control channel stays open",
        "```",
        "",
        "**Why two channels?** Historical design: one channel for commands/responses (low bandwidth),",
        "a separate higher-bandwidth channel for the actual file data.",
        "",
        "---",
        "",
        "## Active vs Passive Mode",
        "",
        "This is the most confusing part of FTP, and the most important for firewall troubleshooting.",
        "",
        "```",
        "ACTIVE MODE (PORT mode):",
        "",
        "  Client opens control channel to server port 21",
        "  Client picks a port (e.g. 55123) and tells server: PORT 55,123",
        "  Server makes outbound connection BACK to client:55123 for data",
        "",
        "  Client: ──control──► Server:21",
        "  Server: ──data──────► Client:55123  ← SERVER connects TO CLIENT",
        "",
        "  Problem: if client is behind a NAT/firewall, server can't reach client.",
        "  Active mode FAILS in most modern network configurations.",
        "",
        "PASSIVE MODE (PASV mode):",
        "",
        "  Client opens control channel to server port 21",
        "  Client sends PASV command",
        "  Server opens a random high port (e.g. 54000) and tells client",
        "  Client makes outbound connection to server:54000 for data",
        "",
        "  Client: ──control──► Server:21",
        "  Client: ──data──────► Server:54000  ← CLIENT connects TO SERVER",
        "",
        "  Client only makes outbound connections → works through NAT/firewalls.",
        "  Passive mode WORKS in modern networks.",
        "",
        "RULE: Always use PASSIVE mode for modern FTP clients.",
        "      Most FTP clients default to passive mode already.",
        "",
        "FIREWALL IMPLICATION for servers running active mode:",
        "  Must allow inbound connections from high ports (1024-65535) = huge security hole",
        "  Passive mode: server only needs inbound on port 21 + a fixed port range",
        "  Configure passive port range: 50000-51000, open only those in firewall",
        "```",
        "",
        "---",
        "",
        "## FTP Commands",
        "",
        "```",
        "AUTHENTICATION:",
        "  USER alice        → send username",
        "  PASS mypassword   → send password (PLAINTEXT! Never use plain FTP over internet)",
        "  QUIT              → close session",
        "",
        "NAVIGATION:",
        "  PWD               → print working directory",
        "  CWD /home/alice   → change directory",
        "  CDUP              → change to parent directory",
        "  MKD newdir        → make directory",
        "",
        "FILE LISTING:",
        "  LIST              → detailed directory listing (like ls -la)",
        "  NLST              → name list only (like ls)",
        "",
        "TRANSFER COMMANDS:",
        "  RETR file.txt     → download: server sends file to client",
        "  STOR file.txt     → upload: client sends file to server",
        "  DELE file.txt     → delete a file",
        "  RNFR old.txt      → rename from (specify old name)",
        "  RNTO new.txt      → rename to (specify new name)",
        "  APPE file.txt     → append to existing file (resume partial upload)",
        "",
        "MODE COMMANDS:",
        "  PASV              → switch to passive mode",
        "  PORT h,h,h,h,p,p  → notify server of client port (active mode)",
        "  TYPE A            → ASCII transfer mode (text files, converts line endings)",
        "  TYPE I            → binary/image transfer mode (all other files)",
        "",
        "IMPORTANT: Always use TYPE I (binary) unless you specifically need ASCII mode.",
        "           ASCII mode corrupts binary files (images, executables, archives).",
        "```",
        "",
        "---",
        "",
        "## ASCII vs Binary Transfer Mode",
        "",
        "```",
        "ASCII mode (TYPE A):",
        "  Converts line endings during transfer:",
        "  Windows CRLF (\\r\\n) ↔ Unix LF (\\n)",
        "  Use ONLY for plain text files when transferring between Windows and Unix",
        "",
        "Binary mode (TYPE I, 'image' mode):",
        "  Transfers exact bytes — no conversion",
        "  Use for: images, executables, zip/tar archives, PDFs, Word documents, everything else",
        "",
        "Common mistake: FTP in ASCII mode corrupts binary files.",
        "  Transfer a .zip file in ASCII mode: FTP modifies bytes that happen to look like",
        "  line endings → corrupted archive → unzip fails.",
        "  Solution: ALWAYS use binary mode (TYPE I) unless you have a specific ASCII reason.",
        "",
        "Most modern FTP clients auto-detect file types. Still good to verify.",
        "```",
        "",
        "---",
        "",
        "## SFTP vs FTPS — The Secure Variants",
        "",
        "```",
        "+─────────────────────────────────────────────────────────────────────+",
        "│ Feature         │ SFTP                      │ FTPS                  │",
        "+─────────────────────────────────────────────────────────────────────+",
        "│ Protocol basis  │ SSH subsystem             │ FTP + TLS/SSL         │",
        "│ Default port    │ 22 (same as SSH)           │ 990 (or 21 explicit) │",
        "│ Channels        │ Single channel            │ Two channels (like FTP│",
        "│ Firewall        │ Easy (one port: 22)       │ Complex (like FTP)    │",
        "│ Compatibility   │ Needs SSH server          │ Needs TLS + FTP       │",
        "│ Setup           │ Simpler (piggybacks SSH)  │ More complex          │",
        "│ Recommendation  │ Prefer this               │ For legacy FTP systems│",
        "+─────────────────────────────────────────────────────────────────────+",
        "",
        "SFTP (SSH File Transfer Protocol):",
        "  Not FTP over SSH — it's a completely different protocol.",
        "  Designed from ground up as a secure file transfer protocol.",
        "  Runs as a subsystem of SSH. If you have SSH access: you have SFTP access.",
        "  Uses one encrypted channel for everything (commands + data).",
        "  Firewall-friendly: single port 22.",
        "",
        "  Connect: sftp alice@server.com",
        "  Or use FileZilla/Cyberduck with SFTP protocol option.",
        "",
        "FTPS (FTP Secure):",
        "  Original FTP protocol with TLS added.",
        "  Two variants: Explicit FTPS (start unencrypted, upgrade with AUTH TLS)",
        "                Implicit FTPS (encrypted from the start, port 990)",
        "  Firewall still needs data channel ports open.",
        "  Used when: legacy FTP infrastructure requires FTP protocol specifically.",
        "",
        "SCP (Secure Copy Protocol):",
        "  Simple file copy over SSH. No directory browsing.",
        "  Command: scp file.txt alice@server:/home/alice/",
        "  Fast, simple, but no resume on failure or directory sync.",
        "```",
        "",
        "---",
        "",
        "## Common FTP Use Cases Today",
        "",
        "```",
        "1. SHARED HOSTING DEPLOYMENT:",
        "   Many budget web hosts use FTP for file uploads.",
        "   Use FTPS or SFTP if offered. Never plain FTP.",
        "   Tools: FileZilla (free GUI client), Cyberduck (macOS/Win GUI)",
        "",
        "2. LEGACY ENTERPRISE SYSTEMS:",
        "   Banks, government systems, EDI (Electronic Data Interchange) still use FTP.",
        "   Usually FTPS internally, sometimes still plain FTP on isolated networks.",
        "   Automated scripts: ftp command-line client, lftp (Linux), WinSCP scripts",
        "",
        "3. SCIENTIFIC DATA ARCHIVES:",
        "   NCBI (genomics), NASA, NOAA — large public datasets via anonymous FTP",
        "   Anonymous FTP: USER anonymous, PASS email@address",
        "   wget or curl can also download from FTP URLs",
        "",
        "4. AUTOMATED FILE EXCHANGE:",
        "   Nightly batch jobs transfer reports between systems",
        "   Python ftplib: connect, login, RETR each file, process, close",
        "```",
        "",
        "---",
        "",
        "## FTP in Python",
        "",
        "```python",
        "from ftplib import FTP, FTP_TLS",
        "",
        "# Plain FTP (LAN/localhost only — unencrypted)",
        "with FTP('ftp.example.com') as ftp:",
        "    ftp.login(user='alice', passwd='password')",
        "    ftp.set_pasv(True)  # always passive mode",
        "    files = ftp.nlst()  # list files",
        "",
        "    # Download a file",
        "    with open('local_file.txt', 'wb') as f:",
        "        ftp.retrbinary('RETR remote_file.txt', f.write)",
        "",
        "    # Upload a file",
        "    with open('local_upload.txt', 'rb') as f:",
        "        ftp.storbinary('STOR remote_upload.txt', f)",
        "",
        "# FTPS (encrypted — use this for real scenarios)",
        "with FTP_TLS('ftp.example.com') as ftps:",
        "    ftps.login(user='alice', passwd='password')",
        "    ftps.prot_p()  # protect data channel with TLS",
        "    ftps.set_pasv(True)",
        "    # same commands as above",
        "",
        "# For SFTP (preferred): use paramiko or fabric",
        "import paramiko",
        "transport = paramiko.Transport(('server.com', 22))",
        "transport.connect(username='alice', password='password')",
        "sftp = paramiko.SFTPClient.from_transport(transport)",
        "sftp.get('/remote/file.txt', 'local_file.txt')  # download",
        "sftp.put('local.txt', '/remote/uploaded.txt')   # upload",
        "```",
        "",
        "---",
        "",
        "## Mind Map",
        "",
        "```",
        "FTP",
        "|",
        "+-- ARCHITECTURE",
        "|   +-- Control channel: port 21 (commands)",
        "|   +-- Data channel: port 20 (active) / random (passive)",
        "|   +-- Two channels open/close per transfer",
        "|",
        "+-- MODES",
        "|   +-- Active: server connects to client (breaks NAT)",
        "|   +-- Passive: client connects to server (use this)",
        "|   +-- ASCII: text, converts line endings (cautious)",
        "|   +-- Binary: exact bytes (always default)",
        "|",
        "+-- SECURE VARIANTS",
        "|   +-- SFTP: SSH-based, single channel, prefer",
        "|   +-- FTPS: FTP + TLS, legacy compatibility",
        "|   +-- SCP: simple SSH file copy",
        "|",
        "+-- COMMANDS",
        "|   +-- Authentication: USER, PASS",
        "|   +-- Navigation: PWD, CWD, MKD",
        "|   +-- Transfer: RETR, STOR, APPE",
        "|   +-- Control: PASV, TYPE I, QUIT",
        "|",
        "+-- SECURITY",
        "    +-- Plain FTP: never over internet (cleartext passwords)",
        "    +-- Firewall: passive mode + fixed port range",
        "    +-- Prefer SFTP (port 22) over FTPS",
        "```",
        "",
        "---",
        "",
        "## How FTP Connects to Other Topics",
        "",
        "- **Linux**: FTP commands run from the bash shell. `ftp`, `lftp`, `sftp` are",
        "  CLI tools. Server configs live in `/etc/vsftpd.conf`.",
        "- **Networking**: FTP demonstrates TCP connection management, port usage,",
        "  NAT traversal challenges. Active vs passive explains firewall concepts clearly.",
        "- **Security**: FTP is the canonical example of an insecure protocol. Teaches",
        "  why encryption (TLS/SSH) exists and why cleartext credentials are dangerous.",
        "- **Docker/CI-CD**: Some CI pipelines still deploy assets via FTP to shared hosts.",
        "  SFTP or FTPS used in Java/Python automation scripts.",
        "",
        "---",
        "",
        "## References",
        "",
        "### Videos",
        "- **FTP Explained** by NetworkChuck: https://www.youtube.com/watch?v=tOj8MSEIbfA",
        "- **SFTP Tutorial** by TechWorld with Nana: https://www.youtube.com/watch?v=b-QF-e9A_bE",
        "",
        "### Articles",
        "- **RFC 959 — FTP specification**: https://tools.ietf.org/html/rfc959",
        "- **FileZilla client** (free GUI): https://filezilla-project.org/",
        "- **Python ftplib docs**: https://docs.python.org/3/library/ftplib.html",
        "- **Paramiko (SFTP in Python)**: https://www.paramiko.org/",
    ])

    d['guide'] = FTP_GUIDE
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    print(f"ftp.json patched: guide={len(FTP_GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

if __name__ == '__main__':
    main()
