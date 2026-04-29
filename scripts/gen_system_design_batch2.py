#!/usr/bin/env python3
"""
System Design Batch 2 — event-driven-architecture, microservices-patterns
Unit 13, orders 128-129
Run: python3 scripts/gen_system_design_batch2.py [--overwrite]
"""
import json, sys
from pathlib import Path

OUT = Path(__file__).parent.parent / "src/content/topics/system-design"
OUT.mkdir(parents=True, exist_ok=True)

TOPICS = [
  {
    "id": "event-driven-architecture",
    "unit": 13,
    "order": 128,
    "title": "Event-Driven Architecture",
    "summary": "Design systems around events: CQRS, event sourcing, saga patterns, and how to handle distributed transactions without 2PC.",
    "prereqs": ["system-design-fundamentals"],
    "guide": """# Event-Driven Architecture — React to What Happened

## Mental Model
In a traditional request/response system, Service A *calls* Service B and waits. In event-driven architecture, Service A *publishes* that something happened. Service B (and C and D) *subscribe* and react — without A knowing or caring.

```
Traditional (tight coupling):
  OrderService ─────────────────► InventoryService (sync call, waits)
  OrderService ─────────────────► PaymentService (another sync call)
  OrderService ─────────────────► EmailService   (another sync call)
  Total latency = sum of all calls. If Email is down, order fails.

Event-Driven (loose coupling):
  OrderService ──► OrderPlaced event ──► Message Bus
                                              │
                                     ┌────────┼────────┐
                                     ▼        ▼        ▼
                              Inventory  Payment   Email
                              (async)    (async)   (async)
  Total latency = time to publish. If Email is down, order still succeeds.
```

## Core Concepts

### Events vs Commands vs Queries
```
Command: "PlaceOrder" — an intent, directed at one service, may be rejected
Event:   "OrderPlaced" — a fact, broadcast, cannot be rejected (already happened)
Query:   "GetOrder"   — asks for state, no side effects

Rule: Events are FACTS. Name them in past tense: OrderPlaced, PaymentFailed.
```

### Event Sourcing
Instead of storing the current state, store the entire *sequence of events* that produced it:
```
Traditional DB:           Event Store:
  Order table:              events table:
  id: 123                   OrderCreated   {orderId:123, items:[...]}
  status: "shipped"         PaymentCharged {orderId:123, amount:50}
  total: 50                 OrderShipped   {orderId:123, trackingId:"X"}

  ← single row, current state     ← append-only log, full history
```

**Benefits:** full audit trail, time-travel queries, replay events to rebuild state, debug by replaying.
**Tradeoff:** queries require replaying all events (use snapshots to optimise).

### CQRS — Command Query Responsibility Segregation
```
Write side (Commands):          Read side (Queries):
  ┌──────────────┐               ┌──────────────┐
  │ Command Model│               │ Read Model   │
  │ (normalised  │──events──────►│ (denormalised│
  │  domain)     │               │  for queries)│
  └──────────────┘               └──────────────┘
  Complex aggregates             Flat, fast views
  Strong consistency             Eventual consistency (milliseconds behind)
```

Use CQRS when read and write patterns differ radically — e.g., millions of reads of simple data, rare complex writes.

### Saga Pattern — Distributed Transactions
Without a distributed transaction coordinator (2PC), use sagas:
```
Choreography Saga (event-driven):
  OrderService    ──► OrderCreated
  PaymentService  ◄── OrderCreated → charges card → PaymentSucceeded
  InventoryService◄── PaymentSucceeded → reserves items → ItemsReserved
  ShipService     ◄── ItemsReserved → creates shipment → OrderShipped

  If PaymentService fails → publishes PaymentFailed
  OrderService ◄── PaymentFailed → cancels order → OrderCancelled

  Pro: no central coordinator. Con: hard to follow the flow.

Orchestration Saga (command-driven):
  SagaOrchestrator ──► ChargePayment command ──► PaymentService
  SagaOrchestrator ◄── PaymentSucceeded       ◄── PaymentService
  SagaOrchestrator ──► ReserveItems command   ──► InventoryService
  ...

  Pro: clear flow, easy to observe. Con: orchestrator can become a bottleneck.
```

### Outbox Pattern — Reliable Event Publishing
```
The problem: write to DB AND publish event — what if crash between them?

Transaction DB:                Message Bus:
  INSERT order ──────┐
  INSERT outbox ─────┘ (same TX)    ← atomic
                            ↑
                     Outbox Relay reads
                     new rows, publishes
                     to Message Bus ──────► published!
                     marks as sent

Guarantees: at-least-once delivery. Make consumers idempotent.
```

## Common Pitfalls
- **Eventual consistency surprise**: after publishing OrderPlaced, if you immediately query the read model it might not reflect the order yet. Communicate this to users (optimistic UI).
- **Event schema evolution**: once events are published and consumed, you can't just change their structure. Use versioning or additive changes only.
- **Lost events**: use durable message brokers (Kafka, RabbitMQ with persistence). Don't use in-memory queues for critical events.
- **Event storms**: a cascade where one event triggers many events which trigger more. Design with circuit breakers and dead letter queues.
- **Not making consumers idempotent**: at-least-once delivery means duplicates. Always handle duplicate events gracefully.

## ASCII Flow: Order Processing
```
User ──► POST /orders
              │
         OrderService
              │ (1) Write to DB
              │ (2) Write to outbox table (same TX)
              ▼
         Outbox Relay ──► Kafka topic: "order.created"
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
        PaymentWorker    InventoryWorker    Analytics
        processes event  reserves stock    updates dashboards
        publishes:       publishes:
        payment.charged  items.reserved
```

## Connections
- `kafka` — the backbone of most event-driven systems
- `distributed-systems` — CAP theorem applies; choose AP for event systems
- `caching-advanced` — read models in CQRS are often cached
- `observability` — tracing events across services requires distributed tracing
""",
    "questions": [
      {"id":"eda-q1","type":"mcq","prompt":"What distinguishes an Event from a Command?","choices":["Events are synchronous, commands are async","Events are facts (past tense, broadcast). Commands are intents (directed, rejectable).","Events require a response","Commands are stored, events are not"],"answerIndex":1,"explanation":"Events record what happened — they can't be rejected because they already occurred. Commands express intent and can fail/be rejected. Name events in past tense: OrderPlaced, not PlaceOrder.","tags":["events","fundamentals"]},
      {"id":"eda-q2","type":"mcq","prompt":"Event Sourcing stores:","choices":["Current state snapshots","Diffs between states","The full sequence of events that produced current state","SQL transactions"],"answerIndex":2,"explanation":"Event Sourcing keeps an immutable append-only log of all events. Current state is derived by replaying events. Full audit trail, time-travel, and replay are free — at the cost of query complexity.","tags":["event-sourcing"]},
      {"id":"eda-q3","type":"mcq","prompt":"CQRS splits:","choices":["Database and cache","Frontend and backend","Command (write) model and Query (read) model into separate representations","SQL and NoSQL"],"answerIndex":2,"explanation":"CQRS separates the write model (normalised, strong consistency for commands) from the read model (denormalised, optimised for queries). The read model is updated asynchronously via events.","tags":["cqrs"]},
      {"id":"eda-q4","type":"mcq","prompt":"In a Choreography Saga, who coordinates the flow?","choices":["A central orchestrator service","No central coordinator — each service reacts to events and publishes its own","The database","An API gateway"],"answerIndex":1,"explanation":"Choreography = no conductor. Each service listens for events it cares about, acts, and publishes the result. The flow is implicit in event subscriptions. Contrast with Orchestration where a central service directs each step.","tags":["saga","choreography"]},
      {"id":"eda-q5","type":"mcq","prompt":"What problem does the Outbox Pattern solve?","choices":["Slow queries","The dual write problem: ensuring a DB write and event publish are atomic","Schema migrations","Event deduplication"],"answerIndex":1,"explanation":"Writing to the DB and publishing an event are two separate operations. If the process crashes between them, you get inconsistency. The Outbox pattern writes both in one DB transaction, then a relay reads the outbox and publishes events reliably.","tags":["outbox","reliability"]},
      {"id":"eda-q6","type":"mcq","prompt":"Why must event consumers be idempotent?","choices":["For performance","At-least-once delivery means the same event can arrive multiple times — processing it twice must not cause double side effects","Events are always exactly-once","For security"],"answerIndex":1,"explanation":"Most message brokers guarantee at-least-once delivery. Network retries, rebalances, and replays can deliver the same event multiple times. Consumers must detect and ignore duplicates (using event IDs).","tags":["idempotency","reliability"]},
      {"id":"eda-q7","type":"mcq","prompt":"Eventual consistency in event-driven systems means:","choices":["Data is never consistent","After all events are processed, all services will have consistent state — but there may be a short lag","Only the write model is consistent","Transactions are used everywhere"],"answerIndex":1,"explanation":"After publishing an event, read models may lag by milliseconds. Eventually (usually very quickly) all subscribers converge on the same state. Systems must be designed to tolerate and communicate this lag.","tags":["consistency","fundamentals"]},
      {"id":"eda-q8","type":"mcq","prompt":"Event schema evolution rule:","choices":["Delete fields freely","Rename events anytime","Make only additive changes (new optional fields) — never remove or rename fields in existing events","Versioning is not needed"],"answerIndex":2,"explanation":"Consumers depend on event structure. Removing or renaming fields breaks consumers. Safe changes: add optional fields, create new event versions. Use a schema registry (Confluent Schema Registry) for enforcement.","tags":["schema-evolution"]},
      {"id":"eda-q9","type":"multi","prompt":"Which patterns address distributed transactions without 2PC?","choices":["Saga pattern","Outbox pattern","Two-phase commit","Eventual consistency with compensating transactions","Distributed locking"],"answerIndexes":[0,1,3],"explanation":"Sagas coordinate multi-service transactions through event chains. The Outbox pattern ensures reliable publishing. Compensating transactions undo partially completed work on failure. 2PC and distributed locking are generally avoided in microservices.","tags":["distributed-transactions","saga"]},
      {"id":"eda-q10","type":"mcq","prompt":"What is a Dead Letter Queue (DLQ)?","choices":["A queue for deleted messages","A queue where messages go after repeated processing failures — for debugging and manual reprocessing","A high priority queue","A backup database"],"answerIndex":1,"explanation":"When a consumer fails to process a message after N retries, the message goes to the DLQ. This prevents poison messages from blocking the main queue. Engineers inspect and replay DLQ messages after fixing the bug.","tags":["dlq","reliability"]},
      {"id":"eda-q11","type":"mcq","prompt":"In an Orchestration Saga, the orchestrator:","choices":["Only listens to events","Sends commands to each participant and waits for their response before proceeding","Is replaced by events","Stores all state in a shared database"],"answerIndex":1,"explanation":"The orchestrator (a separate service or workflow engine) knows the entire saga flow. It commands each step, waits for success/failure, and decides next steps including compensations. Easier to observe but the orchestrator is a single point of complexity.","tags":["saga","orchestration"]},
      {"id":"eda-q12","type":"mcq","prompt":"Event sourcing 'snapshots' are used to:","choices":["Back up events","Avoid replaying the entire event history on every query by storing periodic state checkpoints","Compress events","Synchronise databases"],"answerIndex":1,"explanation":"Replaying 10 million events to reconstruct state is slow. Snapshots periodically capture current state at event N. Then only events N+1 onwards need replay. Snapshot frequency is a trade-off between storage and query speed.","tags":["event-sourcing","snapshots"]},
      {"id":"eda-q13","type":"mcq","prompt":"What is an 'event storm' in event-driven systems?","choices":["Many users connecting simultaneously","A cascade where one event triggers many events which trigger more, potentially overwhelming the system","A Kafka topic with many partitions","DDoS via events"],"answerIndex":1,"explanation":"Event storms are runaway cascades. Use: circuit breakers, backpressure, DLQs, and rate limiting on event processors. Design event flows to be acyclic (DAG) to prevent infinite loops.","tags":["event-storms","reliability"]},
      {"id":"eda-q14","type":"mcq","prompt":"Why is CQRS read model 'eventually consistent'?","choices":["Because it uses NoSQL","Because it's updated asynchronously from events — there's a lag between write and read model update","Because developers chose weak consistency","It's not — read models are always current"],"answerIndex":1,"explanation":"The read model is updated by consuming events from the write side. Events have propagation delay (usually milliseconds). During this window, reads may return slightly stale data. This is the fundamental tradeoff of CQRS.","tags":["cqrs","consistency"]},
      {"id":"eda-q15","type":"mcq","prompt":"Which is the main benefit of event-driven architecture over synchronous microservices?","choices":["Lower latency","Decoupling — publishers don't know or depend on consumers; consumers can be added/changed without changing publishers","Simpler debugging","Fewer services"],"answerIndex":1,"explanation":"Event-driven decouples producers from consumers. You can add new consumers (email, analytics, audit) without changing the producing service. Services fail independently. This is the core value proposition.","tags":["fundamentals","decoupling"]},
      {"id":"eda-q16","type":"mcq","prompt":"What does 'at-least-once' delivery mean for Kafka consumers?","choices":["Messages are delivered exactly once","Messages may be delivered more than once — consumers MUST be idempotent","Messages may be lost","Messages arrive in strict order"],"answerIndex":1,"explanation":"Kafka's default consumer guarantees at-least-once delivery. On failure, the consumer re-reads from its last committed offset and may reprocess messages it already handled. Always track processed event IDs.","tags":["kafka","delivery-semantics"]},
      {"id":"eda-q17","type":"mcq","prompt":"An event schema registry is used to:","choices":["Store events permanently","Enforce schema contracts between producers and consumers — prevent breaking schema changes","Route events to correct consumers","Monitor event throughput"],"answerIndex":1,"explanation":"A schema registry (e.g., Confluent Schema Registry) stores schema versions and validates that producers only publish schema-compatible events. Consumers can negotiate which schema version to use.","tags":["schema-registry","schema-evolution"]},
      {"id":"eda-q18","type":"mcq","prompt":"Compensating transactions in a Saga are used to:","choices":["Speed up transactions","Undo the effects of already-completed steps when a later step fails","Lock rows during processing","Replace rollbacks"],"answerIndex":1,"explanation":"Since distributed sagas can't roll back like a DB transaction, each step must have a compensating action (e.g., 'RefundPayment' compensates 'ChargePayment'). On failure, the saga triggers compensations in reverse order.","tags":["saga","compensating-transactions"]},
      {"id":"eda-q19","type":"mcq","prompt":"Which pattern should you use when you need a full audit trail and time-travel queries?","choices":["CRUD with updated_at timestamps","Event Sourcing — store all events, derive state by replay","CQRS without event sourcing","Append-only logging"],"answerIndex":1,"explanation":"Event Sourcing naturally produces audit trails (every state change is an event). Time-travel queries replay events up to a point in time. CRUD with timestamps only captures current state and a change history must be built separately.","tags":["event-sourcing","audit"]},
      {"id":"eda-q20","type":"multi","prompt":"Which are true about the Outbox Pattern?","choices":["Event and DB write happen in one atomic transaction","A relay process reads the outbox and publishes events","Guarantees exactly-once delivery","Prevents the dual-write problem","Requires a separate microservice"],"answerIndexes":[0,1,3],"explanation":"Outbox: (1) write to DB + outbox in ONE transaction, (2) relay reads outbox and publishes, solving the dual-write problem. It guarantees at-least-once (not exactly-once). The relay can be a separate process or embedded.","tags":["outbox","reliability"]},
    ],
    "flashcards": [
      {"id":"eda-fc1","front":"Event vs Command","back":"Event = FACT (past tense, broadcast, immutable). Command = INTENT (directed, rejectable). OrderPlaced is an event. PlaceOrder is a command.","tags":["fundamentals"]},
      {"id":"eda-fc2","front":"Event Sourcing in one sentence","back":"Store the stream of events, not the current state. Replay events to rebuild state. Full history, time-travel, audit trail for free.","tags":["event-sourcing"]},
      {"id":"eda-fc3","front":"CQRS read model consistency","back":"Eventually consistent — updated asynchronously from events. May lag milliseconds. Design UIs for optimistic updates. Never block reads on write completion.","tags":["cqrs"]},
      {"id":"eda-fc4","front":"Saga vs 2PC","back":"2PC locks resources across services = deadlock risk, poor scalability. Saga = sequence of local transactions with compensating actions. Use Saga for distributed transactions in microservices.","tags":["saga","distributed-transactions"]},
      {"id":"eda-fc5","front":"Outbox Pattern","back":"Write to DB + outbox table in ONE transaction. Relay reads outbox, publishes events, marks sent. Solves dual-write. Guarantees at-least-once delivery (make consumers idempotent).","tags":["outbox"]},
      {"id":"eda-fc6","front":"Idempotency in event consumers","back":"At-least-once delivery = duplicates happen. Track processed event IDs. Re-receiving same event = no-op. Essential for all event consumers.","tags":["idempotency"]},
      {"id":"eda-fc7","front":"Choreography vs Orchestration Saga","back":"Choreography: decentralised, each service reacts to events, no coordinator. Orchestration: central saga service directs each step. Orchestration is easier to understand and debug.","tags":["saga"]},
      {"id":"eda-fc8","front":"Dead Letter Queue purpose","back":"Messages that fail processing N times go to DLQ. Prevents poison messages blocking the queue. Inspect DLQ, fix bug, replay messages. Essential for production event systems.","tags":["dlq","reliability"]},
    ],
    "project": {
      "brief": "Design an event-driven order processing system for an e-commerce platform. Requirements: order placement must not fail if email or inventory service is down, full audit trail of all order state changes, ability to replay last 30 days of events for debugging. Design: event schema for the order lifecycle (name 5+ events), which saga pattern you'd use and why, how you'd handle payment failure compensation, and where you'd put the Outbox pattern.",
      "checklist": [
        {"id":"eda-p1","text":"Define 5+ order lifecycle events with correct past-tense names and key fields","weight":20},
        {"id":"eda-p2","text":"Choose Choreography or Orchestration saga and justify with your requirements","weight":25},
        {"id":"eda-p3","text":"Design compensation flow for PaymentFailed after InventoryReserved","weight":20},
        {"id":"eda-p4","text":"Place Outbox pattern correctly and explain what atomic transaction it protects","weight":20},
        {"id":"eda-p5","text":"Explain how you'd implement idempotency in the Inventory consumer","weight":15},
      ],
      "hints": [
        "Events: OrderCreated, PaymentCharged, PaymentFailed, InventoryReserved, InventoryReleased, OrderShipped, OrderCancelled.",
        "Compensation order: if OrderShipped fails after InventoryReserved + PaymentCharged → first release inventory, then refund payment (reverse order).",
        "Outbox goes in OrderService: INSERT order + INSERT outbox_event in single DB transaction. Relay publishes to Kafka.",
        "Idempotency: InventoryConsumer stores processed event IDs in a ProcessedEvents table. On receive, check if ID exists before processing.",
      ],
    },
  },
  {
    "id": "microservices-patterns",
    "unit": 13,
    "order": 129,
    "title": "Microservices Patterns",
    "summary": "Circuit breakers, service mesh, API gateway, service discovery, bulkhead, sidecar — the production patterns that make microservices actually work.",
    "prereqs": ["event-driven-architecture"],
    "guide": """# Microservices Patterns — Making Distributed Systems Resilient

## Mental Model
A monolith is like a single floor office — everything walks to the printer. Microservices are a city — each building (service) does one thing, connected by roads (network calls). The patterns here are the traffic lights, emergency routes, and building codes that stop the city from grinding to a halt.

```
Monolith:                           Microservices:
  ┌─────────────────────┐            ┌──────┐  ┌──────┐  ┌──────┐
  │ OrderService        │            │Order │  │Pay   │  │Ship  │
  │ PaymentService      │            │Svc   │  │Svc   │  │Svc   │
  │ ShippingService     │            └──┬───┘  └──┬───┘  └──┬───┘
  │ (all in one process)│               └──────────┼─────────┘
  └─────────────────────┘                      Network calls
  Simple deploys, hard to scale           Complex, resilient when designed right
```

## Pattern 1 — Circuit Breaker
Prevents cascading failures when a downstream service is slow/down.

```
States:
  CLOSED (normal) ──[failures > threshold]──► OPEN (fail fast)
                                                    │
                                    [timeout elapsed]│
                                                    ▼
                                              HALF-OPEN (probe)
                                                    │
                             [probe succeeds]────────┼────[probe fails]
                                    ▼                            ▼
                              CLOSED (reset)               OPEN again

In OPEN state: immediately return error (no wait for timeout).
               Upstream gets fast failure, can use fallback.
```

Libraries: Resilience4j (Java), Polly (.NET), Hystrix (deprecated but conceptually relevant).

```java
// Resilience4j example
CircuitBreaker cb = CircuitBreaker.ofDefaults("paymentService");

Supplier<PaymentResult> decorated = CircuitBreaker
  .decorateSupplier(cb, () -> paymentService.charge(order));

Try.ofSupplier(decorated)
  .recover(CallNotPermittedException.class, e -> PaymentResult.fallback());
```

## Pattern 2 — API Gateway
Single entry point for all clients. Handles: routing, auth, rate limiting, SSL termination, request aggregation.

```
Mobile App ──┐
Web App    ──┤──► API Gateway ──► UserService
Partner    ──┘         │       ──► OrderService
                       │       ──► ProductService
              (auth, rate-limit,
               logging, routing)
```

Benefits: clients don't need to know about internal service topology. Centralised cross-cutting concerns. Can aggregate multiple service responses into one.

## Pattern 3 — Service Discovery
Services scale dynamically — IPs change. Don't hardcode service addresses.

```
Client-side discovery:
  ServiceA ──► Registry ──► [list of OrderService IPs]
  ServiceA picks one (load balance) and calls directly

Server-side discovery:
  ServiceA ──► Load Balancer ──► Registry ──► OrderService IP
  (Load Balancer handles the lookup)

Tools: Consul, Eureka (Netflix), Kubernetes DNS (easiest in K8s)

In K8s: order-service.default.svc.cluster.local resolves to ClusterIP
        → K8s handles discovery automatically via DNS + kube-proxy
```

## Pattern 4 — Bulkhead
Isolate failures. Named after ship bulkheads that prevent flooding from spreading.

```
Without bulkheads:
  Thread pool: [  10 threads  ]
  All 10 blocked by slow InventoryService → OrderService also starves

With bulkheads:
  Thread pool A: [3 threads] → InventoryService calls
  Thread pool B: [3 threads] → PaymentService calls
  Thread pool C: [4 threads] → all other calls

  If Inventory blocks all 3 → Payment still works
```

## Pattern 5 — Sidecar / Service Mesh
Deploy a proxy container alongside each service that handles: mTLS, retries, circuit breaking, telemetry — without any code changes.

```
Pod (K8s):
  ┌──────────────────────────────────┐
  │  App Container  │  Sidecar Proxy │
  │  (your code)    │  (Envoy/Istio) │
  │                 │  - mTLS        │
  │                 │  - metrics     │
  │                 │  - retries     │
  │                 │  - circuit bkr │
  └──────────────────────────────────┘
  All traffic in/out goes through sidecar

Tools: Istio (Envoy-based), Linkerd, AWS App Mesh
```

## Pattern 6 — Strangler Fig (Migration Pattern)
Gradually replace a monolith with microservices without a big-bang rewrite:

```
Phase 1:  Monolith handles everything
          Client ──► Monolith

Phase 2:  New service extracted for one domain
          Client ──► API Gateway/Proxy ──► PaymentService (new)
                                       ──► Monolith (everything else)

Phase 3:  Extract more services one by one
          Eventually: Monolith is strangled, fully replaced

Key: the facade/proxy routes incrementally. No risky cutover.
```

## Pattern 7 — Retry with Exponential Backoff + Jitter
```
Naive retry: immediate → floods recovering service with retries
Exponential backoff: wait 1s → 2s → 4s → 8s between retries
With jitter: wait 1±0.3s → 2±0.6s → 4±1.2s
             (randomises timing, prevents thundering herd)

Max retries: 3-5. After that: fail or use fallback.
```

## Pattern 8 — Saga with Compensating Actions (review)
See Event-Driven Architecture topic — Sagas coordinate multi-step transactions across services.

## Common Pitfalls
- **Synchronous calls everywhere**: service A calls B calls C calls D — one slow service cascades latency. Prefer async where possible.
- **No circuit breaker**: cascading failure takes down the whole system, not just the failed service.
- **Chatty microservices**: services that need to make 10 calls to complete one request. Redesign service boundaries or use API aggregation.
- **Distributed monolith**: microservices that are so tightly coupled they must all be deployed together. Defeats the purpose.
- **Missing distributed tracing**: in microservices, a single request touches 5+ services. Without trace IDs propagated through all calls, debugging is nearly impossible.

## Connections
- `event-driven-architecture` — async communication reduces coupling; use events where possible
- `kubernetes` — service discovery, health checks, rolling deployments all built-in
- `observability` — distributed tracing (Jaeger, Zipkin, AWS X-Ray) essential for microservices
- `caching-advanced` — cache responses at API gateway and service level
- `load-balancing` — L7 load balancing is part of the service mesh / API gateway
""",
    "questions": [
      {"id":"ms-q1","type":"mcq","prompt":"A Circuit Breaker in OPEN state:","choices":["Allows all requests through","Immediately returns an error without calling the downstream service","Slows requests down","Queues requests for later"],"answerIndex":1,"explanation":"OPEN = fail fast. No call is made to the downstream service. The upstream gets an immediate error and can use a fallback. This prevents thread exhaustion and cascading failure.","tags":["circuit-breaker"]},
      {"id":"ms-q2","type":"mcq","prompt":"What transitions a Circuit Breaker from OPEN to HALF-OPEN?","choices":["A health check","A timeout period elapsing — then one probe request is allowed through","Manual admin action only","Success rate improving"],"answerIndex":1,"explanation":"After the configured timeout (e.g., 30s), the circuit moves to HALF-OPEN and allows a single probe request. If it succeeds, circuit CLOSES. If it fails, circuit re-OPENS.","tags":["circuit-breaker"]},
      {"id":"ms-q3","type":"mcq","prompt":"What is the primary purpose of an API Gateway?","choices":["Database connection pooling","Single entry point for clients — handles routing, auth, rate limiting, SSL termination","Service-to-service communication","Data transformation only"],"answerIndex":1,"explanation":"API Gateway centralises cross-cutting concerns: authentication, rate limiting, routing, logging, SSL termination. Clients interact with one endpoint regardless of internal service topology.","tags":["api-gateway"]},
      {"id":"ms-q4","type":"mcq","prompt":"Service Discovery solves:","choices":["Database migrations","Dynamic service instance location — services register their IP/port, clients query the registry instead of hardcoding addresses","Load balancing only","Authentication"],"answerIndex":1,"explanation":"In dynamic environments (K8s, auto-scaled EC2), service IPs change constantly. A service registry (Consul, Eureka, K8s DNS) maps service names to current IPs. Clients query the registry, not hardcoded addresses.","tags":["service-discovery"]},
      {"id":"ms-q5","type":"mcq","prompt":"The Bulkhead pattern prevents:","choices":["Memory leaks","One slow dependency consuming all thread pool resources and starving unrelated services","SQL injection","Network packet loss"],"answerIndex":1,"explanation":"Bulkhead isolates thread pools per dependency. If InventoryService is slow and blocks its 3 threads, PaymentService threads are unaffected. Named after ship compartments that prevent one leak from sinking the ship.","tags":["bulkhead"]},
      {"id":"ms-q6","type":"mcq","prompt":"A sidecar proxy in a service mesh handles:","choices":["Business logic for the app","Network concerns (mTLS, retries, circuit breaking, telemetry) without app code changes","Database connections","UI rendering"],"answerIndex":1,"explanation":"The sidecar (Envoy, Linkerd proxy) intercepts all network traffic to/from the app container. It enforces mTLS, records metrics, applies retry policies — all transparently. The app code just makes plain HTTP/gRPC calls.","tags":["sidecar","service-mesh"]},
      {"id":"ms-q7","type":"mcq","prompt":"The Strangler Fig pattern is used to:","choices":["Immediately rewrite a monolith to microservices","Gradually replace a monolith by extracting services one at a time behind a routing proxy","Kill old services instantly","Strangle memory leaks"],"answerIndex":1,"explanation":"Strangler Fig incrementally replaces monolith functionality. A facade/proxy routes traffic: new domain → new service, everything else → monolith. No big-bang rewrite. Each extracted service is production-tested before the next is extracted.","tags":["strangler-fig","migration"]},
      {"id":"ms-q8","type":"mcq","prompt":"Why add jitter to exponential backoff retries?","choices":["For logging purposes","Prevents the thundering herd — without jitter, all clients retry at the same moment after a failure, overwhelming the recovering service","Required by HTTP specification","Improves latency"],"answerIndex":1,"explanation":"After a service recovers, all waiting clients retry simultaneously (thundering herd). Jitter randomises retry timing so clients spread their retries across time, allowing the service to recover gracefully.","tags":["retries","backoff"]},
      {"id":"ms-q9","type":"mcq","prompt":"A 'distributed monolith' is:","choices":["A well-designed microservices system","Microservices so tightly coupled that all must be deployed together — worst of both worlds","A monolith deployed across multiple data centres","A monolith with good APIs"],"answerIndex":1,"explanation":"If your microservices share a database, have synchronous call chains, or must be deployed in lock-step, you have a distributed monolith. You get the operational complexity of microservices without the independence benefits.","tags":["anti-patterns"]},
      {"id":"ms-q10","type":"mcq","prompt":"Why is distributed tracing essential in microservices?","choices":["Performance only","A single user request touches multiple services — tracing propagates a trace ID through all calls so you can reconstruct the full path for debugging","Just for compliance","Replaces logging"],"answerIndex":1,"explanation":"Without trace IDs (W3C TraceContext, B3 headers), you have isolated logs per service with no connection. Tracing (Jaeger, Zipkin, AWS X-Ray) shows the full call graph, timings, and where errors occurred.","tags":["observability","tracing"]},
      {"id":"ms-q11","type":"mcq","prompt":"Client-side service discovery means:","choices":["The client queries DNS only","The client queries the service registry, gets the list of instances, and performs load balancing itself","An API gateway handles all discovery","K8s handles it automatically"],"answerIndex":1,"explanation":"Client-side: client → registry → list of IPs → client picks one (round-robin/random). More control but client needs registry library. Contrast with server-side: client → load balancer → registry → service (client is simpler).","tags":["service-discovery"]},
      {"id":"ms-q12","type":"multi","prompt":"Which are valid Circuit Breaker fallback strategies?","choices":["Return cached response","Return empty/default response","Queue request for retry when circuit closes","Throw error immediately and let client retry","Use a degraded read-only mode"],"answerIndexes":[0,1,2,4],"explanation":"Good fallbacks: cached data, default response, queueing for later processing, degraded mode. Throwing immediately without fallback is also valid (fail fast) but not user-friendly. The right fallback depends on the use case.","tags":["circuit-breaker","fallback"]},
      {"id":"ms-q13","type":"mcq","prompt":"API Gateway vs Service Mesh — key difference?","choices":["API Gateway is for internal, Service Mesh for external","API Gateway: north-south traffic (external clients to services). Service Mesh: east-west traffic (service to service).","They are the same thing","Service Mesh replaces API Gateway"],"answerIndex":1,"explanation":"API Gateway handles traffic entering your system from outside. Service Mesh manages traffic between internal services. You typically need both: Gateway for external access + Mesh for inter-service communication and mTLS.","tags":["api-gateway","service-mesh"]},
      {"id":"ms-q14","type":"mcq","prompt":"mTLS in a service mesh provides:","choices":["Message compression","Mutual authentication — both the calling and called service cryptographically verify each other's identity","Faster routing","HTTP/2 only"],"answerIndex":1,"explanation":"mTLS (mutual TLS) means both sides present certificates. This prevents rogue services from pretending to be legitimate (man-in-the-middle, service impersonation). The service mesh handles certificates automatically.","tags":["service-mesh","security"]},
      {"id":"ms-q15","type":"mcq","prompt":"When is synchronous HTTP between microservices problematic?","choices":["Always","In deep call chains (A→B→C→D→E) — latency adds up and one slow service cascades through the chain","Only in high traffic","Only with REST, not gRPC"],"answerIndex":1,"explanation":"Each hop in a synchronous chain adds network latency. Worse: if E is slow, it makes D slow, which makes C slow, etc. Cascading latency. Use async messaging for non-critical paths; keep sync for reads that need immediate responses.","tags":["anti-patterns","communication"]},
      {"id":"ms-q16","type":"mcq","prompt":"What is 'chatty' microservices anti-pattern?","choices":["Services that log too much","Services that require many network calls to complete a single user request — poor service boundary design","Services that use too much memory","Very fast services"],"answerIndex":1,"explanation":"If displaying a product page requires 20 microservice calls, your service boundaries are wrong. Redesign: aggregate data in a BFF (Backend for Frontend), use event sourcing to maintain denormalised read models, or co-locate related functionality.","tags":["anti-patterns","service-design"]},
      {"id":"ms-q17","type":"mcq","prompt":"Health checks in microservices are used by:","choices":["Only developers","Load balancers, service meshes, and orchestrators (K8s) to route traffic only to healthy instances","Databases","Clients directly"],"answerIndex":1,"explanation":"K8s liveness probes restart unhealthy pods. Readiness probes remove pods from load balancer until ready. Service mesh uses health to make routing decisions. Implement: /health/live and /health/ready endpoints.","tags":["health-checks","k8s"]},
      {"id":"ms-q18","type":"mcq","prompt":"The Backend for Frontend (BFF) pattern:","choices":["A separate backend for each type of frontend client (mobile, web, partner) — each BFF optimises its API for its specific client's needs","A general-purpose API gateway","A database per frontend","Only for mobile apps"],"answerIndex":0,"explanation":"Mobile needs different data shapes than web (smaller payloads, different fields). BFF creates a dedicated API layer per client type that aggregates services and formats data optimally. Each frontend team owns its BFF.","tags":["bff","api-design"]},
      {"id":"ms-q19","type":"mcq","prompt":"Saga compensating transaction for 'PaymentCharged → InventoryReserveFailed':","choices":["Ignore and retry reservation","Publish RefundPayment to rollback the charge — compensation undoes the completed step","Simply cancel the saga without cleanup","Contact the user"],"answerIndex":1,"explanation":"The compensating transaction for PaymentCharged is RefundPayment. Sagas don't roll back like DB transactions — they undo by executing compensations in reverse order of the original steps.","tags":["saga","compensating-transactions"]},
      {"id":"ms-q20","type":"multi","prompt":"Which concerns does a Service Mesh handle transparently (without app code changes)?","choices":["mTLS between services","Automatic retries","Circuit breaking","Business logic","Distributed tracing (telemetry injection)"],"answerIndexes":[0,1,2,4],"explanation":"Service mesh sidecar handles: mTLS, retries, circuit breaking, and telemetry (metrics/traces). Business logic stays in the app container — the mesh only intercepts and manages network traffic.","tags":["service-mesh"]},
    ],
    "flashcards": [
      {"id":"ms-fc1","front":"Circuit Breaker states","back":"CLOSED (normal) → OPEN (fail fast, after failures threshold) → HALF-OPEN (probe) → CLOSED/OPEN again. In OPEN state: return immediately, no call to downstream.","tags":["circuit-breaker"]},
      {"id":"ms-fc2","front":"API Gateway vs Service Mesh","back":"API Gateway: north-south (external → internal). Service Mesh: east-west (service → service). Use both: Gateway for external access, Mesh for internal mTLS + observability.","tags":["api-gateway","service-mesh"]},
      {"id":"ms-fc3","front":"Bulkhead pattern","back":"Separate thread pools per dependency. If InventoryService blocks its pool (3 threads), PaymentService pool (3 threads) still works. Isolate failure blast radius.","tags":["bulkhead"]},
      {"id":"ms-fc4","front":"Exponential backoff + jitter","back":"Retry wait: 1s → 2s → 4s → 8s (exponential). Add jitter (±30%) to randomise — prevents thundering herd when all clients retry at the same moment after failure.","tags":["retries"]},
      {"id":"ms-fc5","front":"Strangler Fig migration","back":"Extract one domain at a time behind a facade/proxy. Route new domain → new service, rest → monolith. Incrementally replace until monolith is gone. No big-bang rewrite.","tags":["strangler-fig","migration"]},
      {"id":"ms-fc6","front":"Distributed tracing necessity","back":"Single request touches 5+ services. Propagate trace ID (W3C TraceContext) in all headers. Use Jaeger/Zipkin/X-Ray to visualise the full call graph. Without it, debugging microservices is nearly impossible.","tags":["observability","tracing"]},
      {"id":"ms-fc7","front":"Chatty microservices anti-pattern","back":"20 calls per page load = bad service boundaries. Fix: BFF (aggregate at API layer), event-sourced read models (denormalise), or reconsider service decomposition.","tags":["anti-patterns"]},
      {"id":"ms-fc8","front":"Service Mesh sidecar handles","back":"mTLS, retries, circuit breaking, telemetry — all transparently, no app code changes. App just makes plain HTTP/gRPC. Envoy/Istio/Linkerd inject sidecar proxy into every pod.","tags":["service-mesh","sidecar"]},
    ],
    "project": {
      "brief": "Design the resilience layer for a payment microservice that calls three downstream services: FraudCheck (SLA: 200ms, latency spikes common), LedgerService (critical, must not lose data), and NotificationService (best-effort email). For each: choose Circuit Breaker thresholds, retry strategy, bulkhead sizing, and fallback behaviour. Also decide whether to use a service mesh or implement these patterns in code, and justify.",
      "checklist": [
        {"id":"ms-p1","text":"Circuit Breaker config for each service: failure threshold, timeout, fallback action","weight":25},
        {"id":"ms-p2","text":"Retry strategy with backoff + jitter for each service","weight":20},
        {"id":"ms-p3","text":"Bulkhead thread pool sizes and rationale","weight":20},
        {"id":"ms-p4","text":"Service mesh vs in-code decision with justification","weight":20},
        {"id":"ms-p5","text":"How you'd implement distributed tracing across all three calls","weight":15},
      ],
      "hints": [
        "FraudCheck: Circuit breaker threshold=5 failures/10s. Fallback: allow payment with async fraud review flag. Retry 2x with 200ms backoff.",
        "LedgerService: No aggressive retries (risk of double charges). Use idempotency keys. Circuit breaker: open after 2 failures. Fallback: DLQ for async retry.",
        "NotificationService: Best-effort. Retry 3x, exponential backoff. If circuit open, log and continue — email failure must not block payment.",
        "Service mesh (Istio/Linkerd): better for polyglot teams, centralised policy. In-code (Resilience4j): more control, no K8s dependency. For a single Java service, in-code is simpler.",
      ],
    },
  }
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
    print(f"Writing System Design batch 2 → {OUT}/")
    for t in TOPICS:
        write_topic(t, overwrite)
    print("Done.")

