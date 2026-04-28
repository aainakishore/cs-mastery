import json
from pathlib import Path

BASE = Path("/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics")

def patch(filepath, guide, questions, flashcards):
    p = Path(filepath)
    t = json.loads(p.read_text())
    t["guide"] = guide
    t["questions"] = questions
    t["flashcards"] = flashcards
    p.write_text(json.dumps(t, indent=2))
    print(f"patched {p.name}: {len(questions)}q {len(flashcards)}fc")

# ─── NETWORKING — remaining ───────────────────────────────────────────────────

patch(BASE / "networking/long-polling.json",
      guide="""# Long Polling and HTTP Push Techniques

When real-time server→client updates are needed, several patterns exist without WebSockets.

## The Polling Problem

```
Short Polling (bad):
  Client: GET /events → Server: 200 (no new events)  ← wasted request
  (repeat every N seconds)
  Cost: many requests, high latency, wasted bandwidth

Long Polling (better):
  Client: GET /events → Server: [HOLDS response until event]
  Server: 200 { event: "message" }  ← returns when event available
  Client: immediately sends new GET /events
```

## Long Polling Mechanics

```
1. Client sends request to /events
2. Server checks for new events:
   - If events available: respond immediately with 200
   - If no events: hold connection open (wait up to 30s)
3. When event occurs OR timeout: respond to client
4. Client processes response and immediately opens new request
5. Server also includes a timeout/empty response so client retries

This creates the impression of "push" — latency = time to event
```

## Server-Sent Events (SSE) — Modern Alternative

```
GET /events HTTP/1.1
Accept: text/event-stream

HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache

data: { "type": "message", "text": "Hello" }

data: { "type": "update", "count": 42 }
                                    ← connection stays open; server can push any time

id: 123                             ← client can resume from this ID if reconnected
event: custom-type                  ← named event types
```

**SSE advantages:**
- Standard HTTP — no special server setup
- Auto-reconnect built into browser EventSource API
- Works over HTTP/2 with multiplexing
- Simpler than WebSocket for one-way push

## JavaScript Examples

```javascript
// Long polling
async function longPoll() {
  try {
    const res = await fetch('/events?lastId=' + lastId, { signal: controller.signal });
    const data = await res.json();
    process(data);
  } catch(e) {
    await sleep(2000);  // backoff on error
  }
  longPoll();  // immediately re-poll
}

// SSE
const source = new EventSource('/events');
source.onmessage = (e) => console.log(JSON.parse(e.data));
source.onerror   = (e) => console.error('SSE error', e);
// Auto-reconnects on disconnect
```

## Comparison Table

| Technique | Latency | Complexity | Direction | Protocol |
|---|---|---|---|---|
| Short Poll | High | Low | Any | HTTP |
| Long Poll | Low-med | Med | Any | HTTP |
| SSE | Low | Low | Server→Client | HTTP |
| WebSocket | Very Low | High | Bidirectional | WS |

## Common Pitfalls
- **Long polling server resource exhaustion** — holding many open connections ties up threads/memory. Use an event-loop server (Node.js, async Python).
- **Not handling SSE reconnection with last event ID** — include `id:` field so client can use `Last-Event-ID` header on reconnect to avoid missed events.
- **SSE over HTTP/1.1 browser limits** — browsers allow max 6 connections per domain over HTTP/1.1. Multiple SSE tabs saturate this. HTTP/2 multiplexes everything on one connection.
""",
      questions=[
          {"id":"lp-q1","type":"mcq","prompt":"How does long polling differ from short polling?","choices":["Long polling uses WebSocket under the hood","Long polling: server holds the request open until data is available (then responds). Short polling: server responds immediately whether or not there's data — resulting in many empty responses","Long polling uses UDP","Long polling requires server push support"],"answerIndex":1,"explanation":"Short polling: constant empty responses waste bandwidth. Long polling: server delays the response until an event occurs or a timeout. Client immediately re-requests — net effect is near-real-time with fewer wasted requests.","tags":["long-polling"]},
          {"id":"lp-q2","type":"mcq","prompt":"SSE vs WebSocket for a stock ticker (server pushes prices, no client messages needed)?","choices":["WebSocket always","SSE — simpler, HTTP-based, built-in auto-reconnect, sufficient for one-way server→client push","They are equivalent","Long polling"],"answerIndex":1,"explanation":"If clients only receive data (no sending), SSE is simpler: plain HTTP, auto-reconnect via EventSource, no protocol upgrade, works over HTTP/2. WebSocket adds complexity that's only justified when clients also send data frequently.","tags":["long-polling","SSE","comparison"]},
          {"id":"lp-q3","type":"mcq","prompt":"Why does SSE have a connection limit problem over HTTP/1.1?","choices":["SSE doesn't support HTTP/1.1","Browsers allow max 6 connections per domain over HTTP/1.1. Each SSE stream uses one connection. Multiple tabs with SSE hit this limit. HTTP/2 multiplexes all streams on a single connection","SSE uses 2 connections per stream","HTTP/1.1 doesn't support streaming"],"answerIndex":1,"explanation":"HTTP/1.1 browser limit: 6 connections/domain. 6 tabs with SSE = all connections used. HTTP/2 solves this — all SSE streams share one multiplexed TCP connection.","tags":["SSE","HTTP/2"]},
      ],
      flashcards=[
          {"id":"lp-fc1","front":"Long polling pattern","back":"Client requests → server HOLDS until event/timeout → responds → client immediately re-requests. Near-real-time with HTTP. Resource-intensive (holding connections). Use event-loop servers (Node.js).","tags":["long-polling"]},
          {"id":"lp-fc2","front":"SSE (Server-Sent Events)","back":"Content-Type: text/event-stream. Server pushes 'data: ...\\n\\n' lines. Auto-reconnects via EventSource. Resumable via id + Last-Event-ID. One-way server→client. Simple, HTTP-native.","tags":["SSE"]},
          {"id":"lp-fc3","front":"Choosing push mechanism","back":"Short poll: simple/rare. Long poll: legacy, broad compat. SSE: server→client push, simple, HTTP/2 friendly. WebSocket: bidirectional, real-time, gaming/chat.","tags":["long-polling","SSE"]},
      ])

patch(BASE / "networking/rpc.json",
      guide="""# RPC — Remote Procedure Call

RPC is a communication paradigm where a program calls a function on a **remote machine** as if it were a local function call. The network communication is abstracted away.

## RPC Concept

```
Without RPC:                        With RPC:
  fetch('/api/users/123')              const user = userService.getUser(123);
  .then(r => r.json())                 // Looks like a local function call
  .then(user => ...)                   // Network call is hidden by stub

gRPC Stub:
  // Generated from .proto — looks local but makes HTTP/2 calls
  const user = await userClient.GetUser({ id: 123 });
```

## gRPC — Modern RPC

gRPC uses **Protocol Buffers** (protobuf) for serialization and **HTTP/2** for transport.

```protobuf
// user.proto
syntax = "proto3";

service UserService {
  rpc GetUser (UserRequest) returns (User);
  rpc ListUsers (ListUsersRequest) returns (stream User); // server streaming
  rpc UpdateUser (stream UserUpdate) returns (UserSummary); // client streaming
  rpc Chat (stream Message) returns (stream Message); // bidirectional
}

message UserRequest { int32 id = 1; }
message User { int32 id = 1; string name = 2; string email = 3; }
```

```javascript
// Client (Node.js)
const { UserServiceClient } = require('./user_grpc_pb');
const client = new UserServiceClient('localhost:50051', grpc.credentials.createInsecure());

// Unary RPC
const request = new UserRequest();
request.setId(123);
client.getUser(request, (err, response) => {
  console.log(response.getName());
});
```

## gRPC vs REST

| Aspect | gRPC | REST/JSON |
|---|---|---|
| Protocol | HTTP/2 | HTTP/1.1 or HTTP/2 |
| Serialization | Protobuf (binary, ~10x smaller) | JSON (text) |
| Interface definition | Strict .proto contract | OpenAPI/Swagger (optional) |
| Streaming | Bidirectional streaming | Limited (SSE for server push) |
| Browser support | Limited (needs gRPC-web proxy) | Excellent |
| Code generation | First-class | Optional |
| Best for | Internal microservices | Public APIs, browsers |

## Service Mesh and gRPC

In microservices, gRPC services communicate via a service mesh (Envoy/Istio):
```
ServiceA ──gRPC──→ Envoy Sidecar ──gRPC──→ Envoy Sidecar ──→ ServiceB
                   (mTLS, tracing, lb)
```

## Common Pitfalls
- **Browser usage** — gRPC uses HTTP/2 trailers which browsers don't support directly. Requires gRPC-web proxy (Envoy) to translate. REST is simpler for browser clients.
- **Versioning** — protobuf field numbers must never change. Add new fields; never reuse or remove field numbers.
- **Error propagation** — gRPC has its own status codes (OK, NOT_FOUND, UNAVAILABLE). Don't confuse with HTTP codes.
""",
      questions=[
          {"id":"rpc-q1","type":"mcq","prompt":"Main performance advantage of gRPC over REST/JSON?","choices":["gRPC uses UDP","Protobuf binary serialization is ~10x smaller than JSON + HTTP/2 multiplexing eliminates head-of-line blocking — significantly faster for internal service communication","gRPC has no overhead","gRPC compresses JSON"],"answerIndex":1,"explanation":"Two advantages: (1) Protobuf binary is far smaller than JSON text (no field names, binary encoding). (2) HTTP/2 allows request multiplexing — multiple concurrent RPC calls on a single connection without blocking.","tags":["gRPC","protobuf","performance"]},
          {"id":"rpc-q2","type":"mcq","prompt":"When should you prefer REST over gRPC?","choices":["Always prefer REST","For public APIs or browser clients — gRPC doesn't work natively in browsers (needs proxy), harder to explore (no curl/postman natively), and JSON is more human-readable for public consumption","gRPC is deprecated","REST has better streaming"],"answerIndex":1,"explanation":"gRPC excels at internal microservice communication. Public APIs (used by browsers without proxy, mobile teams, third parties) benefit from REST's universality and JSON's human readability.","tags":["gRPC","REST","comparison"]},
          {"id":"rpc-q3","type":"mcq","prompt":"In protobuf, what rule is critical for backward compatibility?","choices":["Field names must be unique","Field numbers must never be reused or removed — they identify fields in the binary format. Add new fields with new numbers; never recycle an old number","Always use proto2","Messages can't be nested"],"answerIndex":1,"explanation":"Protobuf serializes by field numbers, not names. If you remove field 3 and later add a new field with number 3, old clients reading new data (or vice versa) will misinterpret the field. Field numbers are permanent.","tags":["gRPC","protobuf","versioning"]},
      ],
      flashcards=[
          {"id":"rpc-fc1","front":"gRPC stack","back":"Interface: .proto file (service + message definitions). Serialization: Protobuf binary (~10x smaller than JSON). Transport: HTTP/2 (multiplexing, header compression). Code generation: client/server stubs in any language.","tags":["gRPC"]},
          {"id":"rpc-fc2","front":"gRPC streaming types","back":"Unary: 1 req → 1 resp. Server streaming: 1 req → stream of responses. Client streaming: stream → 1 resp. Bidirectional: stream → stream. Defined in .proto with stream keyword.","tags":["gRPC","streaming"]},
          {"id":"rpc-fc3","front":"gRPC vs REST choice","back":"gRPC: internal microservices, performance-critical, bidirectional streaming, polyglot teams. REST: public APIs, browser clients, human-readable, less tooling setup.","tags":["gRPC","REST"]},
      ])

patch(BASE / "networking/rabbitmq.json",
      guide="""# RabbitMQ — Message Broker

RabbitMQ is an **AMQP-based message broker** that decouples producers and consumers using queues, exchanges, and routing keys.

## Core Concepts

```
Producer → Exchange → [Routing] → Queue → Consumer

Exchanges route messages TO queues based on routing rules.
Queues store messages until consumers process them.
Bindings link exchanges to queues (with optional routing key filter).

Key AMQP types:
  Direct  exchange: route by exact routing key match
  Topic   exchange: route by routing key pattern (*.order.#)
  Fanout  exchange: broadcast to ALL bound queues (ignore routing key)
  Headers exchange: route by message headers
```

## Direct Exchange Example

```
Producer sends to exchange "orders" with routing key "new":
  channel.publish('orders', 'new', Buffer.from(JSON.stringify(order)));

Queue "order-processor" bound to exchange "orders" with key "new":
  → receives message

Queue "shipping" bound with key "new":
  → also receives the message (multiple consumers)

Queue "refunds" bound with key "refund":
  → does NOT receive "new" messages
```

## Node.js Producer/Consumer

```javascript
const amqplib = require('amqplib');

// Producer
const conn   = await amqplib.connect('amqp://localhost');
const ch     = await conn.createChannel();
await ch.assertExchange('orders', 'direct', { durable: true });
ch.publish('orders', 'new', Buffer.from(JSON.stringify({ id: 123 })), { persistent: true });

// Consumer
const ch     = await conn.createChannel();
await ch.assertQueue('order-processor', { durable: true });
await ch.bindQueue('order-processor', 'orders', 'new');
ch.prefetch(1);     // Only 1 unacked message at a time — fair dispatch

ch.consume('order-processor', async (msg) => {
  const order = JSON.parse(msg.content.toString());
  await processOrder(order);
  ch.ack(msg);           // ACK = remove from queue
  // ch.nack(msg, false, true); // NACK + requeue on failure
});
```

## Acknowledgements and Dead Letter Queues

```
Acknowledgement modes:
  Auto-ack: message removed on delivery (risky — lost if consumer crashes)
  Manual ack: consumer explicitly acks after processing (safe)
  Negative ack (nack): processing failed — requeue or discard

Dead Letter Queue (DLQ):
  Failed messages (nacked/expired/exceeded max retries) → DLQ
  Human review or automated retry logic processes DLQ

Config:
  x-dead-letter-exchange: 'dlx'
  x-message-ttl: 30000   (ms before message expires)
  x-max-retries: 3
```

## Common Pitfalls
- **Auto-ack data loss** — if consumer crashes between delivery and processing, message is gone. Always use manual ack.
- **Unlimited queue growth** — set `x-max-length` or `x-message-ttl` to prevent memory exhaustion from slow consumers.
- **Prefetch=0 (default)** — RabbitMQ floods a single consumer with ALL unprocessed messages. Set prefetch to 1 for fair dispatch.
- **Missing DLQ** — without a DLQ, messages that fail processing are silently dropped after max retries.
""",
      questions=[
          {"id":"rmq-q1","type":"mcq","prompt":"RabbitMQ exchange vs queue — what does each do?","choices":["Same thing","Exchange: receives messages from producers and routes them to queues based on routing rules. Queue: stores messages until consumers process them. Exchange never stores messages","Queue routes, exchange stores","Queues connect to producers directly"],"answerIndex":1,"explanation":"Exchange is the routing layer (decides WHICH queues get the message based on routing key/headers/fanout). Queue is the storage layer (holds messages). Decoupling them allows flexible many-to-many routing.","tags":["rabbitmq","architecture"]},
          {"id":"rmq-q2","type":"mcq","prompt":"Why use manual acknowledgement instead of auto-ack?","choices":["Manual is faster","Auto-ack removes message from queue on delivery. If consumer crashes during processing, the message is lost. Manual ack removes message ONLY after successful processing — ensures at-least-once delivery","Auto-ack is deprecated","Manual prevents duplicates"],"answerIndex":1,"explanation":"At-least-once delivery guarantee: message stays in queue until consumer explicitly acks it. If consumer dies during processing, RabbitMQ requeues to another consumer. Auto-ack = at-most-once (data loss risk).","tags":["rabbitmq","acknowledgement"]},
          {"id":"rmq-q3","type":"mcq","prompt":"What does `channel.prefetch(1)` do?","choices":["Sends 1 test message","Limits unacknowledged messages per consumer to 1 — fair dispatch. Without it, RabbitMQ floods one consumer with all messages, starving others","Requires proto1","Sets message size limit"],"answerIndex":1,"explanation":"Without prefetch, a fast consumer might get 1000 messages while others get 0. prefetch(1): consumer gets one message, processes it, acks, then gets the next. Enables fair work distribution across consumers.","tags":["rabbitmq","prefetch"]},
      ],
      flashcards=[
          {"id":"rmq-fc1","front":"Exchange types","back":"Direct: exact routing key match. Topic: wildcard patterns (*.order.#). Fanout: broadcast to all bound queues. Headers: route by message headers. All defined in channel.assertExchange().","tags":["rabbitmq"]},
          {"id":"rmq-fc2","front":"Acknowledgements","back":"ack(): processing succeeded, remove from queue. nack(msg, multiple, requeue): failed, requeue or discard. auto-ack: dangerous (data loss on crash). Always use manual ack for reliability.","tags":["rabbitmq"]},
          {"id":"rmq-fc3","front":"Dead Letter Queue (DLQ)","back":"Messages that expire (TTL), exceed max retries, or are nacked without requeue go to DLQ. Use for human review, alerting, or delayed retry. Config: x-dead-letter-exchange.","tags":["rabbitmq","DLQ"]},
      ])

patch(BASE / "networking/kafka.json",
      guide="""# Apache Kafka — Event Streaming Platform

Kafka is a **distributed, durable, high-throughput event streaming platform**. Unlike traditional message queues, Kafka retains messages for days/weeks — consumers can replay events from any point.

## Kafka Architecture

```
Producer ──→ Topic (partitioned) ──→ Consumer Groups

Topic: logical stream of events
  Partition 0: [event1, event3, event5...]  ← ordered within partition
  Partition 1: [event2, event4, event6...]
  Partition 2: [...]

Each partition is an append-only log stored on disk.
Retention: events kept for configurable time (7 days default) regardless of read.
```

## Partitions and Consumer Groups

```
Consumer Group "order-service" (3 consumers, 3 partitions):
  Consumer A ← Partition 0  (exclusive assignment)
  Consumer B ← Partition 1
  Consumer C ← Partition 2

New consumer joins (4 consumers, 3 partitions):
  Consumer A ← Partition 0
  Consumer B ← Partition 1
  Consumer D ← Partition 2
  Consumer C ← idle (no partition — more consumers than partitions is wasteful)

Different group "analytics-service" reads the SAME topic independently:
  Doesn't affect order-service offsets/position
  Can read from beginning or latest  ← Kafka's key advantage over RabbitMQ
```

## Producer (Node.js with kafkajs)

```javascript
const { Kafka } = require('kafkajs');
const kafka = new Kafka({ brokers: ['localhost:9092'] });
const producer = kafka.producer();

await producer.connect();
await producer.send({
  topic: 'orders',
  messages: [
    { key: String(order.userId), value: JSON.stringify(order) }
    //       ↑ same key → same partition → ordering per user
  ]
});
```

## Consumer

```javascript
const consumer = kafka.consumer({ groupId: 'order-processor' });
await consumer.connect();
await consumer.subscribe({ topic: 'orders', fromBeginning: false });

await consumer.run({
  eachMessage: async ({ topic, partition, message }) => {
    const order = JSON.parse(message.value.toString());
    await processOrder(order);
    // Offset committed automatically (or manually for at-least-once)
  }
});
```

## Kafka vs RabbitMQ

| Aspect | Kafka | RabbitMQ |
|---|---|---|
| Message retention | Days/weeks (configurable) | Until consumed (or TTL) |
| Replay | Yes — seek to any offset | No |
| Ordering | Per partition | Per queue |
| Throughput | Very high (millions/sec) | Lower |
| Consumer model | Pull-based | Push-based |
| Best for | Event sourcing, analytics, log aggregation | Task queues, RPC patterns |

## Common Pitfalls
- **More consumers than partitions** — extra consumers are idle. Scale partitions first, then consumers (must match or exceed).
- **Unordered messages** — ordering is per-partition only. Use the same key for events that must be ordered (all orders for user X get the same partition).
- **Large messages** — Kafka is optimized for small-to-medium messages. Large blobs should be stored externally (S3) with Kafka carrying the reference.
- **Not monitoring consumer lag** — if consumers fall behind, lag grows. Alert on consumer group lag > threshold.
""",
      questions=[
          {"id":"kfk-q1","type":"mcq","prompt":"How does Kafka handle multiple consumer groups reading the same topic?","choices":["Only one group can read at a time","Each consumer group has its own offset pointer — they read independently. Adding a new consumer group doesn't affect existing groups' positions. All groups see all events","Second group gets remaining messages","Groups share an offset"],"answerIndex":1,"explanation":"Kafka's offset model: each consumer group tracks its own position. A new analytics service can read from the beginning of a topic without affecting the order-processing service. This is the key architectural advantage over traditional queues.","tags":["kafka","consumer-groups"]},
          {"id":"kfk-q2","type":"mcq","prompt":"Why should events for the same user always use the same Kafka partition key?","choices":["For encryption","Kafka only guarantees ordering WITHIN a partition. Assigning the same key (e.g., userId) to all of a user's events ensures they land in the same partition — maintaining order for that user","Keys are for auth","Random distribution is better"],"answerIndex":1,"explanation":"Key-based partitioning: hash(key) % numPartitions determines the partition. Same key = same partition = guaranteed ordering. Different users (different keys) may go to different partitions — parallelism without sacrificing per-user order.","tags":["kafka","partitioning","ordering"]},
          {"id":"kfk-q3","type":"mcq","prompt":"Kafka advantage over RabbitMQ for event replay?","choices":["Kafka is faster","Kafka retains messages for configurable duration (days/weeks) regardless of consumption. A new service can read historical events from the beginning of the topic. RabbitMQ deletes messages after consumption — no replay possible","Replay is a disadvantage","RabbitMQ also supports replay"],"answerIndex":1,"explanation":"Kafka's disk-based log with retention policies enables replay. A new fraud detection service can process all historical orders from week 1. Event sourcing, audit logs, and analytics depend on this. RabbitMQ is a go, RabbitMQ-consume = gone.","tags":["kafka","event-replay"]},
      ],
      flashcards=[
          {"id":"kfk-fc1","front":"Kafka topic partitions","back":"Each partition is an ordered append-only log. Ordering guaranteed within partition only. Same key → same partition (ensures ordering per entity). More partitions = more parallelism.","tags":["kafka"]},
          {"id":"kfk-fc2","front":"Consumer groups","back":"Each group tracks its own offset independently. Multiple groups can read the same topic simultaneously without interfering. More consumers than partitions = idle consumers.","tags":["kafka"]},
          {"id":"kfk-fc3","front":"Kafka vs RabbitMQ choice","back":"Kafka: replay, event sourcing, high throughput, analytics pipelines, multiple independent consumers. RabbitMQ: task queues, complex routing, RPC-style patterns, at-most-once-processed semantics.","tags":["kafka","comparison"]},
      ])

# ─── SCALING ──────────────────────────────────────────────────────────────────

patch(BASE / "scaling/caching.json",
      guide="""# Caching

Caching stores **frequently accessed data** in fast-access storage so future requests are served without re-computing or re-fetching from slow sources.

## Caching Layers

```
L1: CPU cache (nanoseconds) — hardware managed
L2: In-process memory (microseconds) — Map/LRU cache in app
L3: Distributed cache (sub-millisecond) — Redis, Memcached
L4: CDN edge cache (milliseconds, geographically close)
L5: Browser cache — local to user
```

## Cache Policies

```
Eviction policies (when cache is full):
  LRU (Least Recently Used): evict what hasn't been accessed recently
  LFU (Least Frequently Used): evict what's accessed least overall
  TTL (Time To Live): expire after fixed duration regardless of access

Write patterns:
  Write-through: write to cache AND DB simultaneously
    → No stale data, slightly slower writes
  Write-behind (write-back): write to cache only, async to DB
    → Faster writes, risk of data loss on crash
  Cache-aside (lazy loading): app checks cache, misses load from DB + cache
    → Most common pattern
```

## Redis Cache-Aside Pattern

```javascript
async function getUser(userId) {
  const cacheKey = `user:${userId}`;

  // 1. Try cache
  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);  // Cache HIT

  // 2. Cache MISS — fetch from DB
  const user = await db.users.findById(userId);
  if (!user) return null;

  // 3. Store in cache with TTL
  await redis.setex(cacheKey, 300, JSON.stringify(user));  // 5 min TTL
  return user;
}

// Cache invalidation on update:
async function updateUser(userId, data) {
  await db.users.update(userId, data);
  await redis.del(`user:${userId}`);   // ← invalidate
}
```

## Cache Invalidation Problem

"There are only two hard things in CS: cache invalidation and naming things."

```
Strategies:
  TTL-based: expire after N seconds — simple, eventual consistency
  Event-driven: invalidate on write — consistent, needs coordination
  Version-based: cache key includes version (user:123:v3) — safe but cache bloat
  Write-through: always update cache AND DB together
```

## Cache Stampede / Thundering Herd

```
Problem: popular key expires → 1000 concurrent requests miss →
  all 1000 query DB simultaneously → DB overloads

Solutions:
  Mutex locking: first miss locks, fetches, others wait for lock
  Probabilistic early expiry: randomly refresh before TTL expires
  Background refresh: proactively refresh popular keys before they expire
```

## Common Pitfalls
- **Caching mutable data without invalidation** — cache serves stale data forever. Always set TTL or invalidate on write.
- **Caching large objects** — large cached objects waste memory. Consider caching IDs only, or paginated results.
- **Not handling cache misses gracefully** — if Redis is down, app must fall back to DB, not crash.
- **Cache key collisions** — namespace keys: `user:123`, `product:123` not just `123`.
""",
      questions=[
          {"id":"cache-q1","type":"mcq","prompt":"Cache-aside (lazy loading) pattern — how does it work?","choices":["Cache reads DB automatically","App checks cache first. On miss: load from DB, store in cache with TTL, return. On hit: return from cache. Cache only populated for items actually requested","Write-through is always used","Cache is pre-warmed with all data"],"answerIndex":1,"explanation":"Cache-aside is the most common pattern: read cache → miss → read DB → store in cache → return. Benefits: only cache what's used. Tradeoff: cache misses add latency (two operations).","tags":["caching","patterns"]},
          {"id":"cache-q2","type":"mcq","prompt":"Cache stampede problem and a solution?","choices":["Too many cache hits","Popular key expires → all concurrent requesters cache-miss simultaneously → all query DB → DB overloaded. Solution: mutex lock (first miss fetches + populates; others wait) or probabilistic early expiration","Stampede is a feature","Solved by LRU eviction"],"answerIndex":1,"explanation":"Thundering herd: 1000 concurrent requests all get miss at the same moment → 1000 DB queries. Mutex/probabilistic expiry prevents stampede by serializing the cache population.","tags":["caching","stampede"]},
          {"id":"cache-q3","type":"mcq","prompt":"Write-through vs write-behind caching — key tradeoff?","choices":["Same behavior","Write-through: write to cache AND DB synchronously — consistent, slightly slower writes. Write-behind: write cache only, async DB write — faster writes but risk of data loss if cache crashes before DB write completes","Write-through doesn't exist","Write-behind is deprecated"],"answerIndex":1,"explanation":"Write-behind is faster (fire and forget) but introduces a window where cache has data that DB doesn't. Crash during that window = data loss. Write-through is safer at the cost of write latency.","tags":["caching","write-patterns"]},
      ],
      flashcards=[
          {"id":"cache-fc1","front":"Cache-aside pattern","back":"1. Check cache (hit → return). 2. Miss → query DB. 3. Store result in cache with TTL. 4. Return. Invalidate on write: del(key). Most common, handles cold start gracefully.","tags":["caching"]},
          {"id":"cache-fc2","front":"Cache eviction policies","back":"LRU: evict least recently used (good for recency bias). LFU: evict least frequently used (good for hot keys). TTL: expire after time. Redis default: noeviction (fails on full). Set maxmemory-policy.","tags":["caching"]},
          {"id":"cache-fc3","front":"Cache stampede / thundering herd","back":"Popular key expires → N concurrent misses → N DB queries. Fixes: mutex lock (one refetch, others wait), probabilistic early expiry (refresh before expiry), async background refresh for hot keys.","tags":["caching","stampede"]},
          {"id":"cache-fc4","front":"Write patterns","back":"Write-through: update cache + DB together (consistent, slower writes). Write-behind: cache only + async DB (fast, loss risk). Cache-aside: invalidate on write (simple, eventual). Cache should never be source of truth.","tags":["caching"]},
      ])

patch(BASE / "scaling/sharding.json",
      guide="""# Database Sharding

Sharding is a **horizontal partitioning** technique that distributes data across multiple database instances (shards) to scale beyond a single machine's capacity.

## Sharding vs Replication

```
Replication (copies):
  Master  ──→  Replica 1   (same data, different server)
           └──→ Replica 2   (scale reads, HA)
  Each replica has ALL the data. Read scale but write bottleneck.

Sharding (partitions):
  Shard 1: users 0-3M      (different data, different server)
  Shard 2: users 3M-6M
  Shard 3: users 6M-9M+
  Write scale — each shard handles a fraction of total write load.
```

## Sharding Strategies

```
Range-based:
  users 1-1M → Shard 1, 1M-2M → Shard 2
  Pros: range queries easy (all Jan orders on one shard)
  Cons: hotspots if new data concentrates in one range (all new IDs → Shard 2)

Hash-based:
  shard = hash(userId) % numShards
  Pros: even distribution, no hotspots
  Cons: range queries require all shards, resharding is expensive

Directory-based:
  Lookup table: userId → shard (stored separately)
  Pros: flexible, easy resharding
  Cons: lookup table is a bottleneck/single point of failure

Geographic:
  US users → US shard, EU users → EU shard
  Pros: latency, data residency compliance
  Cons: uneven distribution possible
```

## Resharding Problem

```
hash(userId) % 3 shards:  hash(123) % 3 = 0 → Shard A

Add 4th shard:
  hash(userId) % 4 shards: hash(123) % 4 = 3 → Shard D  (different!)
  MOST existing keys must move — expensive data migration

Consistent Hashing (solution):
  Hash ring — keys and nodes on a circle
  Key routes to the nearest node clockwise
  Adding a node: only adjacent keys need moving (~1/N of data)
```

## Cross-Shard Challenges

```
Problem: JOIN across shards
  SELECT u.*, o.* FROM users u JOIN orders o ON u.id = o.userId
  WHERE u.country = 'US'

  users on Shard 1,2 | orders on Shard 3,4 → can't join server-side

Solutions:
  1. Co-locate (same entity on same shard via same shard key)
  2. Denormalize (duplicate user data in orders shard)
  3. Application-level join (fetch from both, join in code)
  4. Cross-shard query engine (Vitess, Citus)
```

## Common Pitfalls
- **Choosing the wrong shard key** — bad key creates hotspots. Key should distribute writes evenly.
- **Cross-shard queries** — avoid joins and transactions across shards. Design schema to keep related data on the same shard.
- **Resharding without consistent hashing** — modular hashing requires migrating most data. Use consistent hashing for production.
""",
      questions=[
          {"id":"sh-q1","type":"mcq","prompt":"Sharding vs replication — fundamental difference?","choices":["Same thing","Replication: copies of all data on multiple servers (read scale, HA). Sharding: each server has a SUBSET of data (write scale). Sharding enables write scaling that replication cannot provide","Replication is slower","Sharding requires more memory"],"answerIndex":1,"explanation":"Replication: all replicas have ALL rows — each write must propagate to all replicas (write bottleneck stays). Sharding: each shard has different rows — writes distribute across shards. Both are typically combined.","tags":["sharding","replication"]},
          {"id":"sh-q2","type":"mcq","prompt":"Why is consistent hashing preferred over modular hashing (key % N) for sharding?","choices":["Consistent hashing is faster","Modular hashing: adding a shard changes hash(key) % N for most keys — mass data migration. Consistent hashing: adding a node only moves ~1/N of keys (adjacent ones) — minimal resharding cost","Same cost","Consistent hashing requires more servers"],"answerIndex":1,"explanation":"hash(key) % 3 vs hash(key) % 4: most keys map to different shards. Consistent hashing places keys and nodes on a ring — adding a node only affects keys between the new node and its neighbor.","tags":["sharding","consistent-hashing"]},
          {"id":"sh-q3","type":"mcq","prompt":"Best solution for cross-shard JOIN queries?","choices":["Global broadcast queries","Co-locate related data on the same shard by choosing a shard key that keeps related entities together (e.g., shard by userId for users + orders — all of user X's data on one shard)","Avoid JOINs entirely","Always denormalize"],"answerIndex":1,"explanation":"Co-location is the architectural solution: if userId is the shard key for both users and orders tables, a specific user's data is co-located. Application only needs to query one shard for user + their orders.","tags":["sharding","cross-shard"]},
      ],
      flashcards=[
          {"id":"sh-fc1","front":"Sharding strategies","back":"Range: easy range queries, hotspot risk. Hash: even distribution, expensive range queries. Directory: flexible lookup table, bottleneck risk. Geographic: latency/compliance, may be uneven.","tags":["sharding"]},
          {"id":"sh-fc2","front":"Consistent hashing","back":"Keys and nodes on a hash ring. Key routes to next node clockwise. Adding a node: only the next clockwise node's keys move (~1/N). Normal modular hash: adding server moves most keys.","tags":["sharding","consistent-hashing"]},
          {"id":"sh-fc3","front":"Cross-shard JOINs — solutions","back":"1. Co-locate (same shard key → related data on same shard). 2. Denormalize (duplicate data). 3. Application join (fetch separately). 4. Cross-shard engine (Vitess, Citus PG).","tags":["sharding"]},
      ])

patch(BASE / "scaling/partitioning.json",
      guide="""# Database Partitioning

Partitioning splits a large table into smaller **physical pieces** while appearing as a single logical table, improving query performance and manageability.

## Partitioning vs Sharding

```
Partitioning:
  Single database server
  Table split into partitions internally
  Transparent to the application (same query to same table)
  Goal: query performance (skip irrelevant partitions)

Sharding:
  Multiple database servers
  Data distributed across different machines
  Application must know which shard to query
  Goal: write scalability and scale beyond single machine
```

## Partition Types

```
Range Partitioning:
  orders_2024_q1 (Jan-Mar 2024)
  orders_2024_q2 (Apr-Jun 2024)
  orders_2024_q3 (Jul-Sep 2024)
  Pruning: WHERE order_date BETWEEN '2024-01-01' AND '2024-03-31'
     → only scans orders_2024_q1 partition

List Partitioning:
  users_us (country = 'US')
  users_eu (country IN ('DE', 'FR', 'GB'))
  users_other (DEFAULT)

Hash Partitioning:
  hash(user_id) % 8 → 8 partitions
  Even distribution, no hotspots, good for bulk data

Composite:
  Range by year → Hash by userId within each year
```

## PostgreSQL Example

```sql
-- Partitioned table declaration
CREATE TABLE orders (
  id         BIGINT NOT NULL,
  user_id    BIGINT,
  amount     DECIMAL,
  created_at TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

-- Partition for each quarter
CREATE TABLE orders_2024_q1
  PARTITION OF orders
  FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_2024_q2
  PARTITION OF orders
  FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- Index on each partition (auto-inherited)
CREATE INDEX ON orders_2024_q1 (user_id);

-- Query uses same table name — planner auto-prunes
SELECT * FROM orders WHERE created_at > '2024-06-01' AND created_at < '2024-07-01';
-- Scans only orders_2024_q2 ← partition pruning
```

## Partition Pruning

The optimizer skips irrelevant partitions when the WHERE clause includes the partition key. This is the primary performance benefit — query scans 1/N of the data instead of the whole table.

## Common Pitfalls
- **Partition key not in WHERE** — without the partition key in WHERE, ALL partitions are scanned (worse than no partitioning due to overhead).
- **Too many partitions** — each partition has overhead. Planning cost grows. Keep a reasonable number (100s, not 10,000s).
- **Not automating new partitions** — for time-based partitioning, create future partitions ahead of time (pg_partman handles this automatically).
""",
      questions=[
          {"id":"part-q1","type":"mcq","prompt":"How does partition pruning improve query performance?","choices":["Partitions are stored in faster storage","Query planner skips partitions that cannot contain matching rows based on the WHERE clause. Scanning 1 of 12 monthly partitions instead of the full table = near 12x speedup","Indexing is replaced","Partitions use less memory"],"answerIndex":1,"explanation":"Partition pruning = compile-time optimization. SELECT ... WHERE created_at BETWEEN Jan-Mar → planner reads only the Q1 partition. Critical: WHERE must include the partition key for pruning to activate.","tags":["partitioning","partition-pruning"]},
          {"id":"part-q2","type":"mcq","prompt":"Main difference between partitioning and sharding?","choices":["Partitioning is newer","Partitioning: within a single DB server, transparent to app (pruning benefit). Sharding: across multiple DB servers, app must route queries, enables horizontal write scaling","Both distribute across servers","Sharding is partitioning plus replication"],"answerIndex":1,"explanation":"Partitioning is a single-server optimization technique. Sharding distributes across machines for capacity. They combine: 3 shards each with range-partitioned tables.","tags":["partitioning","sharding"]},
          {"id":"part-q3","type":"mcq","prompt":"For a time-series `events` table queried mostly by date range, best partition strategy?","choices":["Hash partitioning","Range partitioning by date (e.g., monthly) — queries with date range WHERE clauses prune to 1-2 partitions. Old data can be archived by dropping old partitions (DROP PARTITION = instantaneous, vs DELETE which is slow)","List partitioning","No partitioning needed"],"answerIndex":1,"explanation":"Time-series + range queries = range partitioning by date. Bonus: DROP TABLE orders_2022_q1 is instant O(1) archival. Deleting rows from a huge table requires writing a DELETE that scans indexes.","tags":["partitioning","time-series"]},
      ],
      flashcards=[
          {"id":"part-fc1","front":"Partition types","back":"Range: ordered ranges (dates, IDs). List: discrete values (country, category). Hash: hash(key) % N = even distribution. Composite: range + hash layered.","tags":["partitioning"]},
          {"id":"part-fc2","front":"Partition pruning","back":"Planner skips irrelevant partitions. Requires partition key in WHERE clause. Scanning 1/12 partition for monthly queries = ~12x speedup. Key: WHERE must use partition column.","tags":["partitioning","pruning"]},
          {"id":"part-fc3","front":"Partitioning vs sharding","back":"Partitioning: single server, transparent to app, pruning benefit. Sharding: multi-server, app routes, write scaling. Combined: shards each with partitioned tables.","tags":["partitioning","sharding"]},
      ])

print("\nBatch 2 done!")

