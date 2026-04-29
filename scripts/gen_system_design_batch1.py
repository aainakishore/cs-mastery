#!/usr/bin/env python3
"""
System Design — Batch 1
Topics: api-design-patterns, caching-advanced
Unit 13 (System Design), orders 107-108 (after existing 5 topics end at 106)
Run: python3 scripts/gen_system_design_batch1.py [--overwrite]
"""

import json, sys
from pathlib import Path

OUT = Path(__file__).parent.parent / "src/content/topics/system-design"
OUT.mkdir(parents=True, exist_ok=True)

TOPICS = [
    {
        "id": "api-design-patterns",
        "unit": 13,
        "order": 107,
        "title": "API Design Patterns",
        "summary": "Master REST, GraphQL, gRPC, versioning, pagination, and idempotency for production-grade APIs.",
        "prereqs": ["system-design-fundamentals"],
        "guide": """# API Design Patterns — The Contract Between Services

## Mental Model
An API is a contract. Callers depend on it. Breaking it breaks them. Good API design prioritises:
1. **Clarity** — obvious what each endpoint does and returns
2. **Stability** — changes are backward-compatible
3. **Performance** — right granularity, right format for the use case

## REST — The Standard

### Resource naming
```
# Good — noun, plural, hierarchical
GET    /users                  # list users
GET    /users/{id}             # get one user
POST   /users                  # create user
PUT    /users/{id}             # replace user
PATCH  /users/{id}             # partial update
DELETE /users/{id}             # delete user

GET    /users/{id}/orders      # user's orders
GET    /users/{id}/orders/{oid}# specific order

# Bad — verb in URL, non-standard
POST /getUser
GET  /deleteUser?id=123
```

### HTTP status codes that matter
| Code | Meaning | When to use |
|------|---------|-------------|
| 200 | OK | successful GET, PUT, PATCH |
| 201 | Created | successful POST |
| 204 | No Content | successful DELETE |
| 400 | Bad Request | validation error, malformed JSON |
| 401 | Unauthorized | missing/invalid auth token |
| 403 | Forbidden | valid auth, but no permission |
| 404 | Not Found | resource doesn't exist |
| 409 | Conflict | duplicate create, optimistic lock |
| 422 | Unprocessable | semantic validation failed |
| 429 | Too Many Requests | rate limited |
| 500 | Internal Server Error | unexpected server error |

### Pagination patterns
```
# Offset pagination — simple, SQL-friendly, inconsistent on inserts
GET /posts?page=2&limit=20
Response: { data: [...], total: 500, page: 2, limit: 20 }

# Cursor pagination — consistent for real-time feeds, no offset drift
GET /posts?cursor=eyJpZCI6MTIzfQ&limit=20
Response: { data: [...], nextCursor: "eyJpZCI6MTQzfQ", hasMore: true }

# Keyset pagination — most efficient for DB (uses indexed WHERE clause)
GET /posts?afterId=143&limit=20
```

**Rule:** Use cursor/keyset pagination for feeds and real-time data. Offset is fine for admin dashboards.

## GraphQL — Query What You Need
```graphql
# Client requests exactly what it needs
query {
  user(id: "123") {
    name
    email
    orders(last: 5) {
      id
      total
      status
    }
  }
}
```

```
REST problems GraphQL solves:
  Over-fetching: REST returns whole object even if you need 2 fields
  Under-fetching: need 3 REST calls to assemble one screen
  GraphQL: one request, exactly the shape you need
```

**When NOT to use GraphQL:** Simple CRUD, caching is critical (REST caches at HTTP layer; GraphQL typically uses POST → no HTTP caching), team unfamiliar with schema design.

## gRPC — High-Performance Service-to-Service
```protobuf
// user.proto — contract defined in Protobuf
service UserService {
    rpc GetUser(UserRequest) returns (UserResponse);
    rpc ListUsers(ListRequest) returns (stream UserResponse);  // server streaming
}

message UserRequest { string id = 1; }
message UserResponse { string id = 1; string name = 2; int32 age = 3; }
```
gRPC generates client/server code in any language. Uses HTTP/2 (multiplexing, header compression, bidirectional streaming).

**When to use gRPC:** internal service-to-service (microservices), high throughput, streaming, polyglot environments.

## API Versioning Strategies
```
# URL versioning (most visible, easy to route)
GET /v1/users
GET /v2/users

# Header versioning (clean URLs, harder to test in browser)
GET /users
Accept: application/vnd.myapp.v2+json

# Query param (least preferred)
GET /users?version=2
```

**Semantic versioning rules:**
- Breaking change (removed field, changed type) → new major version `/v2`
- Additive change (new optional field) → backward compatible, no new version needed
- Bug fix in behavior → patch, keep same version

## Idempotency — Safe to Retry
```
Idempotent operations:
  GET    — always safe
  PUT    — same request → same result
  DELETE — deleting already-deleted = 404 or 204 (still safe)

Non-idempotent:
  POST   — creates a new resource each time

Make POST idempotent with Idempotency-Key:
  POST /payments
  Idempotency-Key: client-uuid-12345

Server stores the key + response. On retry with same key → return stored response, don't process again.
```

## Common Pitfalls
- **Exposing DB schema in API**: `userId` in DB becomes `user_id` in API — don't expose internal column names; use a stable API name
- **Returning 200 for errors**: `{ "status": "error" }` with HTTP 200 — clients can't distinguish success from failure at HTTP layer
- **Missing pagination**: returning 10k records in one response — always paginate
- **Inconsistent naming**: mixing `camelCase` and `snake_case` in same API
- **No versioning strategy from day 1**: adding `/v2` after production = pain; plan from the start

## Connections
- `system-design-fundamentals` — APIs are the interface of system components
- `distributed-systems` — API design affects how services communicate
- `rate-limiting` — Rate limit at API gateway; API design must signal limits (429 + Retry-After)
- `networking-rpc` — gRPC is RPC over HTTP/2
""",
        "questions": [
            {"id": "apidp-q1", "type": "mcq", "prompt": "What HTTP method + URL correctly represents 'update a specific user's email'?", "choices": ["POST /users/updateEmail", "PATCH /users/{id}", "PUT /updateUser/{id}", "GET /users/{id}/update"], "answerIndex": 1, "explanation": "PATCH is for partial updates. PUT replaces the whole resource. POST and GET are wrong here. The URL should be a noun (resource), not a verb.", "tags": ["rest", "http-methods"]},
            {"id": "apidp-q2", "type": "mcq", "prompt": "What HTTP status should a successful resource creation return?", "choices": ["200 OK", "201 Created", "202 Accepted", "204 No Content"], "answerIndex": 1, "explanation": "201 Created with a Location header pointing to the new resource is the REST standard for successful POST. 200 is for successful reads/updates.", "tags": ["rest", "status-codes"]},
            {"id": "apidp-q3", "type": "mcq", "prompt": "What is the key difference between cursor pagination and offset pagination?", "choices": ["Cursor is faster on small datasets", "Cursor is stable under concurrent inserts (no drift); offset can skip/duplicate rows if data changes during pagination", "Offset uses a database cursor internally", "No real difference"], "answerIndex": 1, "explanation": "Offset drift: if rows are inserted between page 1 and page 2 requests, page 2 might duplicate the last item of page 1. Cursor-based pagination uses a stable pointer (ID/timestamp) — no drift.", "tags": ["pagination"]},
            {"id": "apidp-q4", "type": "mcq", "prompt": "What problem does GraphQL's single-endpoint design solve vs REST?", "choices": ["Authentication", "Over-fetching (too much data) and under-fetching (need multiple requests for one screen)", "Database performance", "Caching"], "answerIndex": 1, "explanation": "REST: fixed response shapes. GraphQL: client specifies exactly what it needs — no wasted bandwidth, no waterfall requests.", "tags": ["graphql"]},
            {"id": "apidp-q5", "type": "mcq", "prompt": "When is gRPC preferred over REST?", "choices": ["Public APIs consumed by browsers", "High-throughput service-to-service communication, streaming, polyglot microservices", "CRUD web applications", "When simplicity is key"], "answerIndex": 1, "explanation": "gRPC uses HTTP/2 (multiplexing, compression, streaming), binary Protobuf (smaller, faster than JSON), and auto-generated clients. Ideal for internal microservice communication.", "tags": ["grpc"]},
            {"id": "apidp-q6", "type": "mcq", "prompt": "What is an idempotency key used for?", "choices": ["Authentication", "Making POST requests safe to retry without duplicate operations", "Caching responses", "Rate limiting"], "answerIndex": 1, "explanation": "An idempotency key (UUID sent by client) lets the server detect retries of the same request. On retry, return the cached response without re-processing. Critical for payments.", "tags": ["idempotency"]},
            {"id": "apidp-q7", "type": "mcq", "prompt": "What does HTTP 403 mean vs 401?", "choices": ["Both mean authentication failed", "401: not authenticated (missing/invalid token). 403: authenticated but not authorized (no permission for this resource).", "403: server error. 401: client error.", "They are interchangeable"], "answerIndex": 1, "explanation": "401 = 'who are you?' 403 = 'I know who you are, but you can't do this.' Always distinguish them — helps clients know whether to re-authenticate or request permissions.", "tags": ["rest", "status-codes"]},
            {"id": "apidp-q8", "type": "mcq", "prompt": "Which API versioning approach is most common and easiest to test?", "choices": ["Header versioning", "URL path versioning (/v1/)", "Query parameter versioning", "Subdomain versioning"], "answerIndex": 1, "explanation": "URL versioning (/v1/, /v2/) is visible, easy to route in load balancers, and testable in browsers. Widely adopted (GitHub, Twitter, Stripe).", "tags": ["versioning"]},
            {"id": "apidp-q9", "type": "mcq", "prompt": "What is a breaking change in an API?", "choices": ["Adding a new optional field to a response", "Removing a field, changing a field type, or changing endpoint behavior", "Adding a new endpoint", "Fixing a bug in an existing endpoint"], "answerIndex": 1, "explanation": "Breaking changes force clients to update code. Removals, type changes, renamed fields, or changed semantics are breaking. Adding optional fields is non-breaking (additive).", "tags": ["versioning"]},
            {"id": "apidp-q10", "type": "multi", "prompt": "Which HTTP methods are idempotent (safe to retry with same result)?", "choices": ["GET", "POST", "PUT", "DELETE", "PATCH"], "answerIndexes": [0, 2, 3], "explanation": "GET (read-only), PUT (replace to same state), DELETE (already deleted = same final state). POST creates new resources each time. PATCH may or may not be idempotent depending on operation.", "tags": ["http-methods", "idempotency"]},
            {"id": "apidp-q11", "type": "mcq", "prompt": "What is the main weakness of GraphQL compared to REST for public APIs?", "choices": ["GraphQL doesn't support authentication", "HTTP caching doesn't work out of the box (POST requests aren't cached by CDNs)", "GraphQL is slower", "GraphQL can't handle complex queries"], "answerIndex": 1, "explanation": "REST GET responses cache naturally at CDN/proxy level. GraphQL uses POST for queries (to send the query body) — CDNs don't cache POSTs, requiring application-level caching.", "tags": ["graphql", "caching"]},
            {"id": "apidp-q12", "type": "mcq", "prompt": "What should a PATCH vs PUT request body contain?", "choices": ["Same thing — both full resource representation", "PATCH: only the fields to change. PUT: the complete new resource representation.", "PUT: partial update. PATCH: full update.", "No body required for either"], "answerIndex": 1, "explanation": "PUT replaces the entire resource (omitted fields get default/null values). PATCH is a partial update — only include what's changing.", "tags": ["rest", "http-methods"]},
            {"id": "apidp-q13", "type": "mcq", "prompt": "What is gRPC's wire format?", "choices": ["JSON", "XML", "Protocol Buffers (binary)", "MessagePack"], "answerIndex": 2, "explanation": "gRPC uses Protocol Buffers — a binary format 3-10x smaller and faster to serialize/deserialize than JSON. Requires generated code from `.proto` schema files.", "tags": ["grpc"]},
            {"id": "apidp-q14", "type": "mcq", "prompt": "What HTTP response should a rate-limited request return?", "choices": ["403 Forbidden", "400 Bad Request", "429 Too Many Requests with Retry-After header", "503 Service Unavailable"], "answerIndex": 2, "explanation": "429 with `Retry-After: 30` (seconds) or a reset timestamp tells clients exactly when to retry. 503 implies the server is down, not that the client is throttled.", "tags": ["rest", "status-codes", "rate-limiting"]},
            {"id": "apidp-q15", "type": "mcq", "prompt": "Which pagination is most DB-efficient for large tables?", "choices": ["Offset/limit", "Cursor using last ID", "Keyset using WHERE id > lastId ORDER BY id LIMIT n", "Random sampling"], "answerIndex": 2, "explanation": "Keyset pagination uses `WHERE id > :lastId LIMIT n` — a full index scan with a seek. `OFFSET n` requires DB to scan and discard n rows — gets slower as offset grows.", "tags": ["pagination", "database"]},
            {"id": "apidp-q16", "type": "mcq", "prompt": "Should you expose database column names directly in your API?", "choices": ["Yes — simplifies mapping", "No — it couples your API contract to DB internals; use stable API names", "Only for admin endpoints", "Only if using camelCase"], "answerIndex": 1, "explanation": "Database schemas change. Column renamed = breaking API change for clients. Use a stable API name layer (DTO/ViewModel) that maps to DB columns.", "tags": ["api-design", "best-practices"]},
            {"id": "apidp-q17", "type": "multi", "prompt": "Which are benefits of gRPC over REST?", "choices": ["HTTP/2 multiplexing", "Human-readable format", "Bidirectional streaming", "No schema required", "Auto-generated clients in many languages"], "answerIndexes": [0, 2, 4], "explanation": "gRPC: HTTP/2 (multiplexing), streaming support, schema-driven code generation. REST/JSON is more human-readable, requires no schema.", "tags": ["grpc"]},
            {"id": "apidp-q18", "type": "mcq", "prompt": "What is over-fetching?", "choices": ["Sending too many requests", "API returning more data than the client needs", "Using too many HTTP methods", "Requesting data that doesn't exist"], "answerIndex": 1, "explanation": "Over-fetching: a REST endpoint returns the full User object (20 fields) but the UI only needs name and avatar. Wastes bandwidth. GraphQL solves this by letting clients specify fields.", "tags": ["graphql", "api-design"]},
            {"id": "apidp-q19", "type": "mcq", "prompt": "Where should you return a 404 vs 403?", "choices": ["404 for all protected resources (security through obscurity)", "403 when resource exists but user can't access it; 404 when it genuinely doesn't exist", "Both are interchangeable", "Always 403 to avoid leaking information"], "answerIndex": 1, "explanation": "In security-sensitive contexts (e.g., private repos): returning 404 for unauthorized resources prevents leaking their existence. But for clarity, 403 is the semantically correct choice for 'exists but no access'.", "tags": ["rest", "status-codes"]},
            {"id": "apidp-q20", "type": "mcq", "prompt": "What is the 'N+1 query problem' in GraphQL?", "choices": ["GraphQL makes N+1 API calls", "Fetching a list of N items then making 1 DB query per item instead of 1 batch query for all", "Returning N+1 fields", "GraphQL schema with N+1 types"], "answerIndex": 1, "explanation": "Classic: fetch 100 users (1 query), then for each user fetch their orders (100 queries) = 101 queries. Solution: DataLoader — batches all individual item requests into one query.", "tags": ["graphql", "performance"]},
        ],
        "flashcards": [
            {"id": "apidp-fc1", "front": "REST resource naming rule", "back": "Nouns, plural, hierarchical. `/users/{id}/orders`. Never verbs in URL. Use HTTP method for the action (GET=read, POST=create, PUT=replace, PATCH=partial, DELETE=remove).", "tags": ["rest"]},
            {"id": "apidp-fc2", "front": "201 vs 200 vs 204", "back": "200: success with body (GET, PUT, PATCH). 201: resource created (POST) — include Location header. 204: success, no body (DELETE).", "tags": ["status-codes"]},
            {"id": "apidp-fc3", "front": "Cursor vs offset pagination", "back": "Cursor: stable pointer (last ID/timestamp), no drift on concurrent inserts, best for feeds. Offset: simpler, drifts on inserts, O(OFFSET) DB scan. Use cursor for real-time data.", "tags": ["pagination"]},
            {"id": "apidp-fc4", "front": "Idempotency-Key pattern", "back": "Client sends UUID header. Server stores `(key → response)`. On retry with same key: return cached response, no reprocessing. Critical for payments and POST mutations.", "tags": ["idempotency"]},
            {"id": "apidp-fc5", "front": "When to use gRPC vs REST", "back": "gRPC: internal service-to-service, streaming, high throughput, polyglot. REST: public APIs, browser clients, simplicity, CDN caching. GraphQL: flexible client queries, avoid over/under-fetching.", "tags": ["grpc", "graphql"]},
            {"id": "apidp-fc6", "front": "Breaking vs non-breaking API change", "back": "Breaking: remove field, change type, rename field, change behavior. Non-breaking: add optional field, add endpoint, improve performance. Breaking → new major version.", "tags": ["versioning"]},
            {"id": "apidp-fc7", "front": "429 Too Many Requests response", "back": "Always include `Retry-After: <seconds>` or `X-RateLimit-Reset: <timestamp>`. Clients use this to back off intelligently instead of hammering again immediately.", "tags": ["rate-limiting", "status-codes"]},
            {"id": "apidp-fc8", "front": "GraphQL N+1 solution", "back": "DataLoader: batches individual field resolvers into one query per type. Instead of 100 user queries → 1 query with WHERE id IN (...). Essential for any list query with nested data.", "tags": ["graphql", "performance"]},
        ],
        "project": {
            "brief": "Design the API for a social media feed service. Users can post, follow others, and see a personalized feed. Design: (1) REST endpoints for posts, follows, and feed; (2) pagination strategy for the feed (justify choice); (3) GraphQL schema alternative for a mobile client that needs flexible data; (4) one example of an idempotent operation and how you'd implement it; (5) versioning strategy. No implementation code — just API contracts and decisions.",
            "checklist": [
                {"id": "apidp-p1", "text": "Define 5+ REST endpoints with correct HTTP methods and URL patterns", "weight": 20},
                {"id": "apidp-p2", "text": "Choose and justify a pagination strategy for the feed endpoint", "weight": 20},
                {"id": "apidp-p3", "text": "Sketch a GraphQL schema with at least 2 types and a query/mutation", "weight": 20},
                {"id": "apidp-p4", "text": "Identify an idempotency requirement (e.g., follow request) and design the key strategy", "weight": 20},
                {"id": "apidp-p5", "text": "Define a versioning plan for your API from day 1", "weight": 20},
            ],
            "hints": [
                "Feed endpoint: cursor pagination — real-time feed changes during browsing make offset drift a real problem.",
                "Follow: POST /users/{id}/follows/{followeeId} — idempotent with idempotency key to prevent double-follow from retries.",
                "GraphQL: type Post { id, content, author: User, likes: Int } — shows how schema composes types.",
                "Versioning: embed /v1/ from day 1 even if you never need /v2/ — no cost upfront, huge benefit later.",
            ],
        },
    },
    {
        "id": "caching-advanced",
        "unit": 13,
        "order": 108,
        "title": "Caching Advanced",
        "summary": "Master Redis patterns, cache invalidation, stampede prevention, TTL strategies, and distributed cache topologies.",
        "prereqs": ["caching", "system-design-fundamentals"],
        "guide": """# Caching Advanced — The Art of Serving Stale Data Correctly

## Mental Model
A cache is a bet: "this data won't change before it's read again." Win the bet → fast response. Lose → serve stale data or cause a stampede. Advanced caching is about managing these bets with precision.

```
Without cache:       Client → App → DB   (10-100ms)
With cache hit:      Client → App → Cache (0.1-1ms)
With cache miss:     Client → App → Cache miss → DB → Cache fill → Client
```

## Redis Data Structures and When to Use Each
| Structure | Use case |
|-----------|---------|
| `String` | Simple key-value: sessions, counters, feature flags |
| `Hash` | Object fields: `HSET user:123 name Alice age 30` |
| `List` | Queue, stack, chat history, latest N items |
| `Set` | Unique members: tags, user IDs, deduplication |
| `Sorted Set` | Leaderboards, rate-limiting windows, time-series |
| `Stream` | Event log, message queue |
| `HyperLogLog` | Approximate unique count (very memory efficient) |

## Cache Invalidation Strategies

### TTL (Time To Live) — simplest
```
SET key value EX 3600    # expires in 1 hour
```
Good for: data that changes predictably (stock prices, weather). Bad for: data that changes unpredictably (user profile after update).

### Write-through — sync cache and DB
```
Write path:    App → DB (write) AND App → Cache (write)
Read path:     App → Cache (always fresh)
Pros:          No stale data
Cons:          Write latency (two writes), cache pollution (write-only data cached)
```

### Write-behind (Write-back) — async
```
Write path:    App → Cache (write) → async → DB
Read path:     App → Cache
Pros:          Fast writes
Cons:          Data loss risk if cache crashes before DB flush
```

### Cache-aside (Lazy loading) — most common
```python
def get_user(user_id):
    user = cache.get(f"user:{user_id}")
    if user is None:                         # cache miss
        user = db.query(f"SELECT * FROM users WHERE id={user_id}")
        cache.set(f"user:{user_id}", user, ex=3600)
    return user

def update_user(user_id, data):
    db.update(...)
    cache.delete(f"user:{user_id}")          # invalidate: next read goes to DB
```
Most common pattern. Tolerates cache downtime (fall through to DB).

## Cache Stampede (Thundering Herd) Prevention

```
Problem: key expires → 1000 concurrent requests all miss → all hit DB → DB dies
```

### Solution 1: Probabilistic early expiration
```python
# Start refreshing the cache before it expires (small probability while still valid)
remaining_ttl = cache.ttl(key)
if remaining_ttl < 10 or random.random() < 0.01:   # last 10s or 1% chance
    refresh_async()
```

### Solution 2: Mutex / distributed lock
```python
def get_with_lock(key, compute_fn):
    value = cache.get(key)
    if value: return value

    lock_key = f"lock:{key}"
    if cache.set(lock_key, "1", nx=True, ex=5):   # acquire lock (nx = only if not exists)
        try:
            value = compute_fn()
            cache.set(key, value, ex=3600)
        finally:
            cache.delete(lock_key)
        return value
    else:
        time.sleep(0.05)         # another thread is refreshing — wait and retry
        return get_with_lock(key, compute_fn)
```

### Solution 3: Background refresh with stale-while-revalidate
Serve stale value immediately, refresh in background. Client never waits.

## Cache Key Design

### Good key patterns
```
user:{id}                        # simple
user:{id}:profile                # namespaced
rate_limit:{user_id}:{window}    # parameterized
feed:{user_id}:page:{cursor}     # complex
```

### Key rules:
- Include version if schema changes: `user:v2:{id}`
- Use colons as namespace separators
- Include all parameters that change the value
- Keep keys short: consider hashing long params

## Distributed Cache Topologies

### Single node — development
```
App → Redis (single)
```

### Redis Sentinel — high availability
```
App → Sentinel (monitors)
         ├── Redis Primary (reads+writes)
         └── Redis Replicas (reads + failover to primary)
```
Automatic failover. No horizontal scaling.

### Redis Cluster — horizontal scaling
```
App → Redis Cluster
         ├── Shard 1 (slots 0–5460)
         ├── Shard 2 (slots 5461–10922)
         └── Shard 3 (slots 10923–16383)
```
16,384 hash slots. Each key maps to a slot via CRC16. Scales linearly.

### CDN caching — edge nodes
```
User (NYC) → Cloudflare Edge (NYC) → Origin (us-east-1)
                                      ↑ only on cache miss
```

## Cache Eviction Policies
| Policy | Behaviour | When to use |
|--------|-----------|-------------|
| `LRU` (Least Recently Used) | Evict least recently accessed | General purpose |
| `LFU` (Least Frequently Used) | Evict least accessed over time | Popularity-based |
| `TTL` | Evict expired keys | Time-sensitive data |
| `allkeys-lru` | LRU on ALL keys (even no TTL) | When memory is precious |
| `volatile-lru` | LRU only on keys with TTL set | Mix of permanent + temp data |
| `noeviction` | Return error on full cache | When data loss is unacceptable |

## Common Pitfalls
- **Cache stampede on startup**: warming cold cache with a single thundering herd. Fix: warm gradually or use a lock.
- **Cache key collision**: two different data types using the same key format. Use namespaces.
- **Forgetting to invalidate**: user updates profile but old version is served for 1 hour. Plan invalidation from day 1.
- **Caching null/404**: if DB returns null, cache it too (with short TTL) to prevent repeated DB hits for nonexistent keys ("cache penetration").
- **Over-caching**: every DB query cached → changes don't propagate → incorrect data shown.

## Connections
- `caching` — foundational LRU, write-through concepts
- `system-design-fundamentals` — caching is one of the core scaling tools
- `distributed-systems` — distributed cache consistency challenges
- `rate-limiting` — Redis Sorted Sets are the best data structure for sliding window rate limiting
""",
        "questions": [
            {"id": "cach-adv-q1", "type": "mcq", "prompt": "What is cache-aside (lazy loading) pattern?", "choices": ["Cache is pre-populated at startup", "App checks cache first; on miss fetches from DB and populates cache", "All writes go to cache first, then async to DB", "Cache and DB are always in sync"], "answerIndex": 1, "explanation": "Cache-aside: read from cache → miss → read from DB → write to cache → return. The application controls the caching logic. Most common pattern.", "tags": ["cache-patterns"]},
            {"id": "cach-adv-q2", "type": "mcq", "prompt": "What is the cache stampede problem?", "choices": ["Too many cache hits causing memory overflow", "A popular key expires; many concurrent requests all miss and all hit the DB simultaneously", "Cache and DB are out of sync", "Too many evictions"], "answerIndex": 1, "explanation": "When a hot key expires, all waiting requests miss simultaneously and flood the DB. Prevention: mutex, probabilistic refresh, or stale-while-revalidate.", "tags": ["stampede"]},
            {"id": "cach-adv-q3", "type": "mcq", "prompt": "How does a distributed mutex prevent cache stampede?", "choices": ["Blocks all requests until DB responds", "Only one thread acquires the lock and refreshes the cache; others wait and retry, eventually getting the cached value", "Prevents cache expiry", "Queues requests in Redis"], "answerIndex": 1, "explanation": "Redis SET NX (set if not exists) creates a distributed lock. Only the lock winner computes and fills the cache. Others sleep briefly and re-check — serving the just-filled value.", "tags": ["stampede", "redis"]},
            {"id": "cach-adv-q4", "type": "mcq", "prompt": "What Redis data structure is best for a leaderboard?", "choices": ["String", "List", "Hash", "Sorted Set"], "answerIndex": 3, "explanation": "Sorted Sets store members with scores and allow O(log n) rank queries: `ZADD leaderboard 1500 userId`, `ZREVRANK leaderboard userId` for rank.", "tags": ["redis", "data-structures"]},
            {"id": "cach-adv-q5", "type": "mcq", "prompt": "What is the difference between write-through and write-behind caching?", "choices": ["No difference", "Write-through: writes to cache AND DB synchronously (consistent). Write-behind: writes to cache first, DB async (fast writes, risk of data loss)", "Write-through only for reads", "Write-behind always crashes"], "answerIndex": 1, "explanation": "Write-through is consistent but has write latency. Write-behind is fast but risks losing writes if the cache crashes before flushing to DB.", "tags": ["cache-patterns"]},
            {"id": "cach-adv-q6", "type": "mcq", "prompt": "What is cache penetration?", "choices": ["Cache is too full", "Requests for keys that don't exist in DB keep bypassing the cache and hitting the DB", "Cache and DB have different data", "Cache is slow to respond"], "answerIndex": 1, "explanation": "If null/not-found results aren't cached, every request for a nonexistent key hits the DB. Fix: cache null with a short TTL, or use a Bloom filter to check key existence before hitting DB.", "tags": ["cache-pitfalls"]},
            {"id": "cach-adv-q7", "type": "mcq", "prompt": "What is Redis Cluster used for?", "choices": ["High availability with failover", "Horizontal scaling via hash slot distribution across multiple shards", "Authentication", "Backup"], "answerIndex": 1, "explanation": "Redis Cluster distributes keys across 16,384 slots across N shards. Scales read/write throughput horizontally. Each shard has its own master+replica pair for HA.", "tags": ["redis", "distributed-cache"]},
            {"id": "cach-adv-q8", "type": "mcq", "prompt": "What does `SET key value NX EX 5` do in Redis?", "choices": ["Sets key, overwrites existing", "Sets key only if it does NOT exist, with 5-second expiry — atomic distributed lock acquisition", "Sets key only if it exists", "Sets 5 keys"], "answerIndex": 1, "explanation": "NX = Only set if Not eXists. EX = expiry in seconds. Combined: atomic lock acquisition. If key exists (lock held), returns nil. If not, sets the key (acquires lock).", "tags": ["redis", "distributed-lock"]},
            {"id": "cach-adv-q9", "type": "mcq", "prompt": "When should you use LFU eviction over LRU?", "choices": ["Always — LFU is better", "When access frequency matters more than recency — viral content that's accessed many times over weeks shouldn't be evicted just because it's not the most recent", "When TTL is set on all keys", "For session data"], "answerIndex": 1, "explanation": "LRU evicts the least recently accessed. LFU evicts the least frequently accessed overall. LFU is better for skewed access patterns where popular items shouldn't be evicted even if not accessed in the last minute.", "tags": ["eviction"]},
            {"id": "cach-adv-q10", "type": "multi", "prompt": "Which are valid cache invalidation strategies?", "choices": ["TTL-based expiry", "Write-through (sync)", "Write-behind (async)", "Cache-aside invalidation on write", "Never invalidate — always fresh"], "answerIndexes": [0, 1, 2, 3], "explanation": "All of 0-3 are valid strategies with different trade-offs. 'Never invalidate' would serve stale data forever — not a valid strategy.", "tags": ["cache-patterns"]},
            {"id": "cach-adv-q11", "type": "mcq", "prompt": "What is stale-while-revalidate?", "choices": ["Serving an error while the cache refreshes", "Serving the current (possibly stale) cached value immediately, while triggering a background refresh", "Blocking until cache is fresh", "Fetching from two sources simultaneously"], "answerIndex": 1, "explanation": "Stale-while-revalidate: client gets the stale value (no wait), background job refreshes the cache. Next request gets the fresh value. Excellent for web performance (HTTP Cache-Control header supports this).", "tags": ["cache-patterns"]},
            {"id": "cach-adv-q12", "type": "mcq", "prompt": "What Redis structure is best for rate limiting with a sliding window?", "choices": ["String with increment", "Hash", "Sorted Set (ZRANGEBYSCORE to count requests in window)", "List"], "answerIndex": 2, "explanation": "Sorted Set: `ZADD user:requests <timestamp> <uuid>`, then `ZCOUNT user:requests (now-60s) now` to count requests in the last 60 seconds. ZREMRANGEBYSCORE prunes old entries.", "tags": ["redis", "rate-limiting"]},
            {"id": "cach-adv-q13", "type": "mcq", "prompt": "What is the benefit of Redis Sentinel over a single Redis node?", "choices": ["Horizontal scaling", "Automatic failover: if master goes down, Sentinel promotes a replica to master", "Lower latency", "More data structures"], "answerIndex": 1, "explanation": "Sentinel monitors master and replicas. On master failure, it auto-promotes the best replica and updates clients. No horizontal scaling — use Cluster for that.", "tags": ["redis", "distributed-cache"]},
            {"id": "cach-adv-q14", "type": "mcq", "prompt": "What is the `noeviction` policy risk?", "choices": ["Data is evicted randomly", "When memory is full, Redis returns errors for write commands — application must handle ENOMEM", "Replicas stop syncing", "TTLs are ignored"], "answerIndex": 1, "explanation": "`noeviction` means Redis refuses writes when full. Use when you can't afford data loss (e.g., session store), but you MUST handle the error response gracefully.", "tags": ["eviction"]},
            {"id": "cach-adv-q15", "type": "mcq", "prompt": "What is cache warming?", "choices": ["Setting high TTL values", "Pre-populating the cache before traffic hits, to avoid cold-start stampedes", "Increasing cache memory", "Running Redis at higher CPU priority"], "answerIndex": 1, "explanation": "After a deployment or restart, the cache is empty (cold). Cache warming pre-loads frequently accessed data. Prevents thundering herd on startup.", "tags": ["cache-pitfalls"]},
            {"id": "cach-adv-q16", "type": "mcq", "prompt": "When should you include a version in a cache key (e.g., `user:v2:{id}`)?", "choices": ["Always", "When the schema/format of the cached data changes — old keys serve old format, new code expects new format", "For security", "When TTL is over 1 hour"], "answerIndex": 1, "explanation": "If your serialization format changes (new fields added to User), existing cache entries are the old format. Key versioning ensures old entries aren't read by code expecting the new format — clean migration.", "tags": ["cache-keys"]},
            {"id": "cach-adv-q17", "type": "multi", "prompt": "Which Redis data structures support O(1) operations?", "choices": ["String GET/SET", "Hash HGET/HSET", "List LPUSH/LPOP (from ends)", "Set SADD/SISMEMBER", "Sorted Set ZADD (it's O(log n))"], "answerIndexes": [0, 1, 2, 3], "explanation": "String, Hash, List (at ends), Set operations are O(1). Sorted Set ZADD/ZRANK are O(log n) due to the skiplist structure.", "tags": ["redis", "complexity"]},
            {"id": "cach-adv-q18", "type": "mcq", "prompt": "What is probabilistic early expiration for stampede prevention?", "choices": ["Expire all keys early", "With a small probability, refresh the cache before it expires — spreading refresh load over time instead of all-at-once", "Cache multiple values per key", "Random TTL assignment"], "answerIndex": 1, "explanation": "As expiry approaches, each request has an increasing probability of triggering a refresh. This distributes the refresh across many requests instead of one stampede moment.", "tags": ["stampede"]},
            {"id": "cach-adv-q19", "type": "mcq", "prompt": "What is the correct way to handle a null/not-found DB result in cache-aside?", "choices": ["Don't cache null — always hit DB", "Cache null with a short TTL (e.g., 30s) to prevent repeated DB hits for nonexistent keys", "Return 500 error", "Cache null with same TTL as existing data"], "answerIndex": 1, "explanation": "Cache penetration: attacker or buggy code repeatedly requests nonexistent keys, bypassing cache and slamming DB. Caching null with short TTL breaks this pattern.", "tags": ["cache-pitfalls"]},
            {"id": "cach-adv-q20", "type": "mcq", "prompt": "What is Redis Cluster hash slot distribution based on?", "choices": ["Random assignment", "CRC16 of the key modulo 16384 determines which slot and therefore which shard", "Key alphabetical order", "Key length"], "answerIndex": 1, "explanation": "Redis Cluster computes `CRC16(key) % 16384` to assign a slot. Slots are distributed across shards. Keys with the same `{hash tag}` go to the same slot.", "tags": ["redis", "distributed-cache"]},
        ],
        "flashcards": [
            {"id": "cach-adv-fc1", "front": "Cache-aside read flow", "back": "1. Check cache. 2. Hit → return. 3. Miss → query DB. 4. Write to cache with TTL. 5. Return. On update: write to DB, delete cache key (next read refills).", "tags": ["cache-patterns"]},
            {"id": "cach-adv-fc2", "front": "Cache stampede — three solutions", "back": "1. Mutex (SET NX lock, one thread refreshes). 2. Probabilistic early refresh (refresh before expiry with small chance). 3. Stale-while-revalidate (serve stale, refresh async).", "tags": ["stampede"]},
            {"id": "cach-adv-fc3", "front": "Redis Sorted Set for rate limiting", "back": "`ZADD key <timestamp> <uuid>` per request. `ZCOUNT key (now-window) now` for count. `ZREMRANGEBYSCORE key 0 (now-window)` to prune. Atomic with Lua or pipeline.", "tags": ["redis", "rate-limiting"]},
            {"id": "cach-adv-fc4", "front": "SET NX for distributed lock", "back": "`SET lock:resource uuid NX EX 5` — acquires lock (NX = only if not exists, EX = auto-expire). On release: `DELETE lock:resource` only if value == uuid (compare-and-delete).", "tags": ["redis", "distributed-lock"]},
            {"id": "cach-adv-fc5", "front": "Cache penetration fix", "back": "Cache null results with short TTL (30s). Or use Bloom filter: cheap membership check before hitting DB — if not in filter, definitely doesn't exist in DB.", "tags": ["cache-pitfalls"]},
            {"id": "cach-adv-fc6", "front": "Sentinel vs Cluster", "back": "Sentinel: high availability (auto-failover), single shard, same capacity. Cluster: horizontal scaling (shards), auto-failover per shard, more complex client.", "tags": ["distributed-cache"]},
            {"id": "cach-adv-fc7", "front": "Write-through vs write-behind trade-off", "back": "Write-through: consistent (sync both), slower writes. Write-behind: fast writes (async to DB), risk of data loss on crash. Use write-behind only when write performance is critical and some loss is tolerable.", "tags": ["cache-patterns"]},
            {"id": "cach-adv-fc8", "front": "LRU vs LFU eviction", "back": "LRU: evict least recently used — good for recency-biased access. LFU: evict least frequently used over time — good for popularity-biased access (protects viral content from eviction).", "tags": ["eviction"]},
        ],
        "project": {
            "brief": "Design the caching layer for a high-traffic news feed. Requirements: 10M users, feeds personalised per user, articles cached globally, trending articles refreshed every 5 minutes, user preferences change rarely. Design: (1) what to cache and at what granularity, (2) TTL strategy for each type, (3) invalidation strategy when an article is edited, (4) stampede prevention for a breaking news article that goes viral, (5) Redis topology for this scale. No code — architecture decisions and justifications.",
            "checklist": [
                {"id": "cach-adv-p1", "text": "Define cache keys and TTLs for user feeds, article content, and trending list", "weight": 20},
                {"id": "cach-adv-p2", "text": "Design invalidation strategy for article edits (which keys, how triggered)", "weight": 20},
                {"id": "cach-adv-p3", "text": "Stampede prevention strategy for viral article (breaking news scenario)", "weight": 20},
                {"id": "cach-adv-p4", "text": "Choose Redis topology (single, sentinel, cluster) and justify for this scale", "weight": 20},
                {"id": "cach-adv-p5", "text": "Identify 2 potential cache pitfalls in this design and mitigations", "weight": 20},
            ],
            "hints": [
                "User feeds are personalised — cache per user ID with 5-minute TTL. Article content is global — cache per article ID with 1-hour TTL.",
                "When an article is edited: delete `article:{id}` cache. For feeds containing that article: either short TTL (eventual consistency) or event-driven invalidation.",
                "Viral article stampede: mutex (distributed lock) for cache fill, or pre-warm the cache via background job before TTL expires.",
                "At 10M users, Redis Cluster is likely needed for feed caches. Global article cache could be a separate smaller Redis Sentinel setup.",
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
    print(f"Writing System Design batch 1 → {OUT}/")
    for t in TOPICS:
        write_topic(t, overwrite)
    print("Done.")

