"""
patch_scaling_1.py — expands caching.json, sharding.json, partitioning.json
Run: python3 scripts/patch_scaling_1.py
"""
import json
from pathlib import Path

BASE = Path(__file__).parent.parent / 'src/content/topics/scaling'

# ─────────────────────────────────────────────────────────────────────────────
#  CACHING
# ─────────────────────────────────────────────────────────────────────────────
p = BASE / 'caching.json'
d = json.loads(p.read_text())

d['guide'] = """# Caching

## What Is Caching? (Start From Zero)

Imagine you work in a library. Every time someone asks for a book, you walk to the
storeroom in the basement, find the book, carry it back upstairs. That takes 10 minutes.

One day you realise: some books are requested 100 times a day. So you keep a small shelf
at the front desk with the most popular books. Now when someone asks, you hand it over
in 5 seconds — 120x faster.

That small shelf IS a cache. A cache is a temporary, fast-access store for frequently
requested data so you don't have to fetch it from the slow original source every time.

**Why caching matters:**
```
Without cache:           With cache:
  Request -> DB query      Request -> Cache hit -> Response
  100ms per request        1ms per request
  DB: 10,000 queries/sec   DB: 100 queries/sec (99% cache hit rate)
  DB overwhelmed           DB relaxed, app 100x faster
```

---

## The Caching Layers

Data can be cached at multiple levels — each faster and closer to the CPU:

```
LAYER 1: CPU Cache (L1/L2/L3)
  Speed:    1-10 nanoseconds
  Size:     KB to MB
  Managed:  by hardware automatically
  You don't code this — CPU does it for you

LAYER 2: Application In-Process Memory
  Speed:    ~100 nanoseconds (RAM access)
  Size:     limited by JVM heap / process memory
  Example:  Java HashMap, Guava LoadingCache, Caffeine
  Use for:  small, rarely-changing data (config, lookup tables)
            Only works for single-process apps (not horizontally scaled)

LAYER 3: Distributed Cache (Redis, Memcached)
  Speed:    ~1 millisecond (network + memory)
  Size:     GBs to TBs across a cluster
  Example:  Redis, Memcached, AWS ElastiCache
  Use for:  shared cache across multiple app server instances
            Session data, user profiles, rate limiting counters

LAYER 4: Database Query Cache / Read Replicas
  Speed:    10-100ms
  Example:  MySQL query cache, PostgreSQL pg_bouncer, read replicas
  Use for:  expensive aggregation queries, reporting

LAYER 5: CDN (Content Delivery Network)
  Speed:    5-50ms (geographically close edge server)
  Example:  CloudFront, Cloudflare, Fastly
  Use for:  static assets (images, CSS, JS), entire API responses
            User in Tokyo gets content from Tokyo edge, not US server

The further right in the request path you can answer from cache,
the more work you save.
```

---

## Cache Write Strategies — Write-Through vs Write-Back vs Write-Around

When data is written, how does it get into the cache?

```
WRITE-THROUGH:
  Application writes to CACHE first
  Cache immediately writes to DATABASE
  Both updated synchronously

  App -> Cache -> DB (in same operation)

  Pros:
    Cache and DB always consistent
    No data loss on cache crash (already in DB)
  Cons:
    Write latency = DB write latency (cache doesn't speed up writes)
  Use for: financial data, anything where consistency > write speed

WRITE-BACK (Write-Behind):
  Application writes to CACHE only
  Cache flushes to DATABASE asynchronously later (every N seconds or N writes)

  App -> Cache   (fast!)
         |  (later, async)
         v
         DB

  Pros:
    Very fast writes (cache speed, not DB speed)
    Can batch multiple writes into one DB operation
  Cons:
    Risk of data loss if cache crashes before flush
    Cache and DB temporarily inconsistent
  Use for: high-write workloads, analytics counters, session activity

WRITE-AROUND:
  Application writes DIRECTLY to DATABASE, bypassing cache
  Cache is populated on first read (cache miss -> load from DB -> store in cache)

  App -> DB   (writes bypass cache)
  App -> Cache (reads check cache first)

  Pros:
    Cache only stores data that's actually READ (no wasted cache space)
  Cons:
    First read after write always a cache miss (cold start per key)
  Use for: write-once-read-many data, large datasets where most writes never read
```

---

## Cache Eviction Policies — What Gets Removed When Cache Is Full

Cache has limited memory. When it fills up, something must be evicted.

```
LRU (Least Recently Used) — MOST COMMON:
  Evict the item that hasn't been accessed for the longest time.
  Assumption: if it hasn't been used recently, it probably won't be needed soon.

  Access log: A B C D A B  (cache size=3)
  Cache:      [D, A, B]   <- C was evicted (least recently used)

  Redis default. Good for general-purpose caching.

LFU (Least Frequently Used):
  Evict the item with the lowest access count.
  Assumption: popular items should stay, unpopular ones go.

  Use when: some items are permanently popular (top 10 products), others are temporary bursts.
  Problem: long-lived items accumulate high frequency and never evict even if stale.

TTL (Time To Live):
  Items automatically expire after a set time regardless of usage.
  key: user_profile:123  TTL: 300 seconds (5 minutes)
  After 5 minutes, next access = cache miss, fetch fresh from DB.

  Best practice: combine LRU AND TTL.
    LRU: evict when memory full
    TTL: ensure stale data doesn't linger forever

RANDOM:
  Evict a random item. Simple, surprisingly effective for large caches.

FIFO (First In First Out):
  Evict the oldest inserted item regardless of usage. Rarely ideal.
```

---

## Cache Invalidation — The Hard Problem

Phil Karlton famously said: "There are only two hard things in Computer Science:
cache invalidation and naming things."

```
THE PROBLEM:
  You cache user profile for user_id=123.
  User updates their email address.
  DB is updated with new email.
  Cache still has OLD email for 5 more minutes.
  User sees stale data — confusing and buggy!

INVALIDATION STRATEGIES:

1. TTL-based (simplest):
   Accept some staleness. TTL=60s means at most 60s of stale data.
   ✓ Simple to implement
   ✗ User may see stale data for up to TTL duration

2. Explicit invalidation:
   When data changes, DELETE the cache key immediately.
   user.update(email=new_email) -> cache.delete("user_profile:123")
   ✓ Instant consistency
   ✗ You must remember to invalidate everywhere data changes
   ✗ "Cache stampede" if many requests hit DB simultaneously after invalidation

3. Cache-aside (lazy loading):
   App checks cache first. Miss -> fetch from DB -> store in cache.
   When data updates -> delete cache key (not invalidate -> repopulate).
   Next read will repopulate. Simple and common.

4. Write-through automatically invalidates:
   Since every write goes through cache, cache is always current.
   No separate invalidation logic needed.

CACHE STAMPEDE (Thundering Herd):
  Popular key expires at same time.
  1000 concurrent requests all get cache miss simultaneously.
  All 1000 hit the database at once -> DB overwhelmed.

  Solutions:
    - Probabilistic early expiration: randomly refresh before TTL expires
    - Mutex lock: only one request rebuilds cache, others wait
    - Background refresh: async refresh before TTL expires
    - Stale-while-revalidate: serve stale data, refresh in background
```

---

## Redis — The Most Popular Distributed Cache

Redis is an in-memory data structure server. Way more than just a cache.

```
DATA STRUCTURES (not just strings!):
  String:     GET/SET key value  (basic caching)
  List:       LPUSH/RPOP         (queues, timelines)
  Set:        SADD/SMEMBERS      (unique visitors, tags)
  Sorted Set: ZADD/ZRANGE        (leaderboards, rate limiting)
  Hash:       HSET/HGET          (user profiles as field->value)
  Bitmap:     SETBIT/GETBIT      (feature flags, daily active users)
  HyperLogLog: PFADD/PFCOUNT     (approximate unique count)

KEY PATTERNS:
  user:123:profile     -> Hash of user fields
  session:abc123       -> String (serialised session JSON)
  rate_limit:user:123  -> Integer counter + TTL
  leaderboard:weekly   -> Sorted Set (score -> userId)
  cache:product:456    -> String (serialised JSON) + TTL

PERSISTENCE:
  RDB: periodic snapshots to disk (data safe across restarts)
  AOF: append-only log of every write command (more durable)
  Both: for production; just RDB for cache-only use

REDIS CLUSTER:
  Horizontal sharding across multiple Redis nodes.
  16384 hash slots distributed across N masters.
  Each key -> hash slot -> shard node.
  Automatic resharding when nodes added/removed.
```

---

## CDN Caching — The Outermost Layer

```
CDN = Content Delivery Network
  Geographically distributed servers that cache your content at the edge.
  User request goes to nearest edge (50ms) not origin server (200ms).

STATIC ASSETS (always cache):
  Images, CSS, JavaScript, fonts
  Cache-Control: max-age=31536000, immutable (1 year, never revalidate)
  Use content-hashed filenames: main.a3f8c.js (hash changes when content changes)

API RESPONSES (sometimes cache):
  GET /api/products/featured -> same for all users -> cache at CDN edge
  GET /api/users/me -> personalised -> DO NOT cache at CDN (or vary by cookie)

HTTP CACHE HEADERS:
  Cache-Control: max-age=3600           -> cache for 1 hour
  Cache-Control: no-store               -> never cache (sensitive data)
  Cache-Control: no-cache               -> cache but revalidate every time
  Cache-Control: public                 -> CDN and browsers can cache
  Cache-Control: private                -> only browser caches (not CDN)
  ETag: "abc123"                        -> fingerprint of content
  Last-Modified: Mon, 28 Apr 2026 ...   -> when content last changed
  Vary: Accept-Encoding, Accept-Language -> different cache per encoding/language
```

---

## Common Caching Patterns

```
CACHE-ASIDE (Lazy Loading) — most common:
  1. App checks cache
  2. Hit: return value
  3. Miss: fetch from DB, store in cache, return value

  def get_user(user_id):
      cached = redis.get(f"user:{user_id}")
      if cached:
          return json.loads(cached)
      user = db.query("SELECT * FROM users WHERE id = ?", user_id)
      redis.setex(f"user:{user_id}", 300, json.dumps(user))  # TTL 5min
      return user

READ-THROUGH:
  Cache sits in front of DB. Cache itself fetches from DB on miss.
  App only talks to cache, never directly to DB.
  Popular in ORMs and caching libraries (Hibernate second-level cache).

HOT KEY PROBLEM:
  One cache key gets 1,000,000 requests/second (celebrity post, trending product).
  Single Redis node becomes bottleneck.
  Solutions:
    - Local in-process cache as L2 (JVM HashMap in front of Redis)
    - Key replication: store same value in cache:product:123:shard0 through :shard9
      Distribute reads across 10 keys (each handles 100K rps)
```

---

## Mind Map

```
CACHING
|
+-- LAYERS
|   +-- L1/L2/L3 CPU (hardware)
|   +-- In-process (HashMap/Caffeine)
|   +-- Distributed (Redis/Memcached)
|   +-- DB read replicas
|   +-- CDN (edge, global)
|
+-- WRITE STRATEGIES
|   +-- Write-through (consistent, slower writes)
|   +-- Write-back (fast writes, risk of loss)
|   +-- Write-around (cache only on read)
|
+-- EVICTION
|   +-- LRU (recency — most common)
|   +-- LFU (frequency)
|   +-- TTL (time-based expiry)
|   +-- Random
|
+-- INVALIDATION
|   +-- TTL (accept staleness)
|   +-- Explicit delete on write
|   +-- Cache stampede prevention
|
+-- REDIS
|   +-- Strings, Lists, Sets, Sorted Sets, Hashes
|   +-- TTL per key
|   +-- Persistence (RDB/AOF)
|   +-- Cluster (sharding)
|
+-- CDN
    +-- Static assets (long TTL, content-hashed)
    +-- Cache-Control headers
    +-- Personalised responses: do NOT cache at CDN
```

---

## How Caching Connects to Other Topics

- **Sharding**: When a DB is sharded, caching reduces cross-shard queries dramatically.
- **Rate Limiting**: Redis Sorted Sets and counters power token bucket and sliding window rate limiters.
- **Load Balancing**: CDN caching reduces load balancer and origin server load.
- **Databases**: Read replicas are a form of caching. ElastiCache sits in front of RDS.

---

## References and Further Learning

### Videos (Watch These!)
- **Redis Crash Course** by Traversy Media:
  https://www.youtube.com/watch?v=jgpVdJB2sKQ
  - 40 minutes. Redis commands, data structures, Node.js integration.
- **Caching Explained** by ByteByteGo:
  https://www.youtube.com/watch?v=dGAgxozNWFE
  - System design-focused overview of all caching strategies.

### Free Books and Articles
- **Redis official docs**: https://redis.io/docs/manual/data-types/
- **The System Design Primer — Caching**: https://github.com/donnemartin/system-design-primer#cache
  - Comprehensive system design caching section.

### Diagrams
- **Cache write strategies diagram**: search 'write-through vs write-back cache diagram'
- **CDN caching flow**: search 'CloudFront caching diagram'

### Practice
- **Try Redis in browser**: https://try.redis.io/ — interactive Redis tutorial
- **Redis University (free)**: https://university.redis.com/
"""

CACHING_Q = [
    {"id":"cache-q1","type":"mcq","prompt":"What is a cache hit and a cache miss?",
     "choices":["Hit = error, Miss = success","Hit = requested data found in cache (fast). Miss = data not in cache, must fetch from slower source (DB/API)",
                "Hit = write, Miss = read","They are the same thing"],
     "answerIndex":1,"explanation":"Cache hit: data found in cache, served in <1ms. Cache miss: data not in cache, must go to database (10-100ms). Cache hit rate = hits/(hits+misses). 99% hit rate means DB only serves 1% of traffic.","tags":["caching","basics"]},
    {"id":"cache-q2","type":"mcq","prompt":"What is write-through caching?",
     "choices":["Write only to cache, skip DB","Write to DB only","Write to cache AND DB synchronously — both updated together, always consistent",
                "Write to a message queue"],
     "answerIndex":2,"explanation":"Write-through: every write updates cache and DB in the same operation. Cache is always consistent with DB. Trade-off: write latency = DB write latency (cache doesn't speed up writes). Use for critical data where consistency matters.","tags":["caching","write-through"]},
    {"id":"cache-q3","type":"mcq","prompt":"What is write-back (write-behind) caching?",
     "choices":["Write to DB only, then refresh cache","Write to cache only, flush to DB asynchronously later — fast writes, risk of data loss on crash",
                "Skip the cache entirely","Write only on cache miss"],
     "answerIndex":1,"explanation":"Write-back: write to cache (fast), flush to DB later in batches. Risk: if cache crashes before flush, recent writes are lost. Benefit: very fast write path. Use for high-write workloads that can tolerate brief inconsistency.","tags":["caching","write-back"]},
    {"id":"cache-q4","type":"mcq","prompt":"What does LRU (Least Recently Used) eviction mean?",
     "choices":["Evict the largest item","Evict the item most recently added","When cache is full, remove the item that hasn't been accessed for the longest time — based on recency of use",
                "Evict items randomly"],
     "answerIndex":2,"explanation":"LRU keeps recently accessed items and evicts the oldest-accessed. Works on the assumption: if something hasn't been used recently, it probably won't be needed soon. Most popular cache eviction strategy. Redis default.","tags":["caching","lru","eviction"]},
    {"id":"cache-q5","type":"mcq","prompt":"What is a cache stampede (thundering herd)?",
     "choices":["When too many items are cached","When a popular cached key expires and many simultaneous requests all hit the database at once, overwhelming it",
                "When cache runs out of memory","When two caches have conflicting data"],
     "answerIndex":1,"explanation":"If a hot key expires and 10,000 concurrent requests all get a cache miss simultaneously, all 10,000 hit the DB at once. Solutions: mutex lock (one rebuilds, others wait), probabilistic early expiration, or stale-while-revalidate pattern.","tags":["caching","stampede","reliability"]},
    {"id":"cache-q6","type":"mcq","prompt":"What is the Cache-Aside (lazy loading) pattern?",
     "choices":["Cache writes whenever DB writes","Application checks cache first; on miss, fetches from DB, stores in cache, returns result",
                "Cache automatically syncs with DB","Write through multiple cache layers"],
     "answerIndex":1,"explanation":"Cache-aside is the most common pattern. App: 1) Check cache. 2) Hit? Return it. 3) Miss? Query DB, store in cache with TTL, return. Cache only stores data that's actually requested. App code controls caching logic.","tags":["caching","cache-aside","pattern"]},
    {"id":"cache-q7","type":"mcq","prompt":"What Redis data structure is best for a leaderboard (rank users by score)?",
     "choices":["String","List","Hash","Sorted Set (ZADD/ZRANGE with scores)"],
     "answerIndex":3,"explanation":"Redis Sorted Set: ZADD leaderboard 1500 user:123. ZRANGE leaderboard 0 9 WITHSCORES gets top 10. ZRANK leaderboard user:123 gets a user's rank. O(log N) operations. Perfect for any ranked data.","tags":["redis","data-structures","sorted-set"]},
    {"id":"cache-q8","type":"mcq","prompt":"Your app runs 10 instances. You use an in-process HashMap as cache. What problem arises?",
     "choices":["HashMap is too slow","10 instances have 10 separate caches — different instances may have different cached values; cache invalidation must happen on every instance separately",
                "HashMap doesn't support TTL","Memory is shared across instances"],
     "answerIndex":1,"explanation":"In-process caches are local to each server instance. Instance A caches user profile, user updates, Instance B deletes its cache — but Instance A still serves stale data. Solution: use distributed cache (Redis) shared by all instances.","tags":["caching","distributed","in-process"]},
    {"id":"cache-q9","type":"mcq","prompt":"What HTTP header controls how long a browser and CDN cache a response?",
     "choices":["X-Cache-Control","Authorization","Cache-Control: max-age=3600 controls caching duration (3600 seconds = 1 hour)",
                "Content-Type"],
     "answerIndex":2,"explanation":"Cache-Control header: max-age=N (cache for N seconds), no-store (never cache), public (CDN and browsers cache), private (only browser caches, not CDN). Content-hashed filenames + max-age=31536000 is the standard pattern for JS/CSS assets.","tags":["caching","cdn","http-headers"]},
    {"id":"cache-q10","type":"mcq","prompt":"What is the TTL (Time To Live) in caching?",
     "choices":["Total Transaction Log","Time a cached value is considered valid — after TTL expires, access = cache miss, fresh data fetched from source",
                "Total Traffic Limit","Transaction Timeout Limit"],
     "answerIndex":1,"explanation":"TTL automatically expires stale data. redis.setex('user:123', 300, data) — expires after 300 seconds. Short TTL = more cache misses but fresher data. Long TTL = fewer misses but risk of serving stale data. Choose based on data change frequency.","tags":["caching","ttl","expiry"]},
    {"id":"cache-q11","type":"mcq","prompt":"What is the hot key problem in distributed caching?",
     "choices":["A key that is too large","When one cache key receives disproportionate traffic (e.g., a celebrity's post) causing a single shard to become a bottleneck",
                "A key that never expires","Keys with special characters"],
     "answerIndex":1,"explanation":"If product:bestseller gets 1M requests/second but all map to one Redis node, that node is overwhelmed. Solutions: local in-process cache as L2, key replication (store at cache:key:shard0..9, read from random shard), or Consistent Hashing.","tags":["caching","hot-key","redis"]},
    {"id":"cache-q12","type":"mcq","prompt":"What does a CDN cache and why?",
     "choices":["User sessions and passwords","Static assets (images, JS, CSS) and static API responses — served from edge locations near users, reducing latency and origin server load",
                "Database queries","Only HTML pages"],
     "answerIndex":1,"explanation":"CDN caches static assets (long-lived, same for all users) and optionally public API responses. Never cache user-specific data (personalised pages, tokens). Enable caching: Cache-Control: public, max-age=86400. Disable: Cache-Control: private, no-store.","tags":["caching","cdn","static-assets"]},
    {"id":"cache-q13","type":"mcq","prompt":"What is Redis persistence and why does it matter?",
     "choices":["Redis clears data on restart — persistence doesn't exist","RDB (periodic snapshots) and AOF (append-only log) let Redis survive restarts without losing data",
                "Redis automatically syncs with MySQL","Persistence only works in Redis Cluster"],
     "answerIndex":1,"explanation":"Redis is in-memory but supports persistence. RDB: periodic snapshot to disk (faster restore). AOF: log every write command (more durable, slower). For pure cache use RDB only. For data you can't lose (sessions, rate limit counters) use AOF or both.","tags":["redis","persistence"]},
    {"id":"cache-q14","type":"mcq","prompt":"When should you NOT use a cache?",
     "choices":["When traffic is high","For financial data","When data changes on every request, is unique per user, or when stale data causes serious harm (bank balance during transfer, medical records)",
                "When using a relational database"],
     "answerIndex":2,"explanation":"Caching is harmful when: data changes faster than TTL (cache is never fresh), data is unique per request (cache miss every time = wasted overhead), or serving stale data is dangerous (inventory count during checkout, real-time pricing).","tags":["caching","trade-offs","when-not-to-use"]},
    {"id":"cache-q15","type":"mcq","prompt":"What is the difference between Redis and Memcached?",
     "choices":["They are identical","Redis: rich data structures, persistence, replication, Lua scripting, pub/sub. Memcached: simple string key-value only, multi-threaded, pure cache. Choose Redis for almost all new projects.",
                "Memcached is faster for all use cases","Redis is only for caching"],
     "answerIndex":1,"explanation":"Redis has overtaken Memcached in popularity due to richer feature set. Memcached advantage: multi-threaded, slightly better throughput for simple get/set. Redis advantage: data structures, persistence, replication, atomic operations, pub/sub. Use Redis.","tags":["redis","memcached","comparison"]},
    {"id":"cache-q16","type":"mcq","prompt":"What is cache eviction vs cache invalidation?",
     "choices":["They mean the same thing","Eviction: cache removes items due to memory pressure (LRU/LFU). Invalidation: explicitly removing/updating cached item because source data changed.",
                "Eviction is for CDN only","Invalidation only applies to TTL"],
     "answerIndex":1,"explanation":"Eviction = cache is full, remove least valuable item (LRU etc.) to make room. Invalidation = data in DB changed, remove the cached copy so next read gets fresh data. Both can trigger a cache miss but for different reasons.","tags":["caching","eviction","invalidation"]},
    {"id":"cache-q17","type":"mcq","prompt":"What write strategy is recommended for caching user session data?",
     "choices":["Write-around (session in DB only)","Write-back (cache only, flush later)","Write-through or cache-aside with short TTL — session data must be consistent, and loss on crash is unacceptable",
                "No caching for sessions"],
     "answerIndex":1,"explanation":"Session data must survive cache restarts and be consistent across instances. Write-back risks loss. Write-through or cache-aside with Redis persistence (AOF) is standard. Redis with TTL = sessions auto-expire. Most web frameworks use Redis for session storage.","tags":["caching","sessions","write-strategy"]},
    {"id":"cache-q18","type":"mcq","prompt":"What is stale-while-revalidate caching?",
     "choices":["A Redis feature","Serve cached (possibly stale) response immediately while fetching fresh data in background — user gets fast response, cache is refreshed asynchronously",
                "A SQL caching technique","Force clients to always revalidate"],
     "answerIndex":1,"explanation":"Cache-Control: max-age=60, stale-while-revalidate=30. After 60s, serve stale while async-refreshing. User never waits for a cache miss. CDNs and service workers support this. Trades perfect freshness for zero-latency responses.","tags":["caching","stale-while-revalidate","cdn"]},
    {"id":"cache-q19","type":"mcq","prompt":"What is a read-through cache?",
     "choices":["Cache that only caches reads, not writes","Cache layer sits IN FRONT of database and automatically loads data on cache miss — app only ever talks to cache, never to DB directly",
                "Reading data from multiple caches","Cache that reads from disk"],
     "answerIndex":1,"explanation":"Read-through: app talks only to cache. On miss: cache itself fetches from DB and stores result. App code is simpler — no explicit cache logic. Trade-off: cache must know how to fetch from DB (coupling). Used by Hibernate L2 cache, Spring @Cacheable.","tags":["caching","read-through","pattern"]},
    {"id":"cache-q20","type":"mcq","prompt":"What cache eviction policy should you use for a 'top 100 products' cache where 20 new products are added daily but old ones remain popular?",
     "choices":["FIFO — evict the oldest-added items","LFU — keep items by access frequency; new products start at count=0 but quickly accumulate counts if popular, while truly unpopular ones fade",
                "Random eviction","Always full scan, no eviction needed"],
     "answerIndex":1,"explanation":"LFU is better than LRU here. LRU might evict a popular product just because it wasn't accessed in the last minute. LFU tracks total access count — a product with 10,000 accesses stays even if not accessed in the last 10 minutes.","tags":["caching","lfu","eviction"]},
]

CACHING_FC = [
    {"id":"cache-fc1","front":"Write-through vs write-back vs write-around","back":"Write-through: write cache+DB sync (consistent, slow writes). Write-back: write cache only, flush DB async (fast writes, risk of loss). Write-around: write DB only, cache on first read (cache only stores read data).","tags":["caching","write-strategies"]},
    {"id":"cache-fc2","front":"LRU vs LFU vs TTL eviction","back":"LRU: evict least recently accessed (default, good general purpose). LFU: evict least frequently accessed (better for stable popular items). TTL: auto-expire after time (prevent stale data). Combine LRU + TTL in production.","tags":["caching","eviction"]},
    {"id":"cache-fc3","front":"Cache stampede prevention","back":"Hot key expires -> thousands hit DB simultaneously. Fix: mutex lock (one rebuilds), probabilistic early expiry (randomly refresh before TTL), stale-while-revalidate (serve stale, refresh async), or pre-warm cache before expiry.","tags":["caching","stampede"]},
    {"id":"cache-fc4","front":"Redis data structure cheatsheet","back":"String: simple cache. Hash: object fields. List: queue/timeline. Set: unique tags/visitors. Sorted Set: leaderboard/rate limiter. HyperLogLog: approx unique count. Bitmap: feature flags, daily active users.","tags":["redis","data-structures"]},
    {"id":"cache-fc5","front":"When NOT to cache","back":"Data changes on every request (no benefit). Unique per user (every request = miss). Data where staleness causes harm (bank balance, inventory during checkout). Highly sensitive data (cache may leak across users).","tags":["caching","trade-offs"]},
    {"id":"cache-fc6","front":"CDN cache headers rule","back":"Static assets (JS/CSS/images): Cache-Control: public, max-age=31536000 + content-hashed filename. Dynamic personalised: Cache-Control: private, no-store. Public API (same for all): Cache-Control: public, max-age=60, stale-while-revalidate=30.","tags":["caching","cdn","http-headers"]},
    {"id":"cache-fc7","front":"Cache-aside pattern steps","back":"1) Check cache for key. 2) HIT: return cached value. 3) MISS: query DB. 4) Store in cache with TTL. 5) Return value. App controls caching explicitly. Cache only contains data actually requested. Most common caching pattern.","tags":["caching","cache-aside"]},
    {"id":"cache-fc8","front":"Hot key problem and solution","back":"One Redis key gets millions of requests/sec -> single shard is bottleneck. Fix: local in-process L2 cache in front of Redis, OR key replication (cache:key:shard0..9, read from random shard). Reduces per-shard load by 10x.","tags":["redis","hot-key","scaling"]},
]

d['guide'] = d['guide']  # already set above
d['questions'] = CACHING_Q
d['flashcards'] = CACHING_FC
with open(p, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"caching.json: guide={len(d['guide'])} q={len(d['questions'])} fc={len(d['flashcards'])}")

# ─────────────────────────────────────────────────────────────────────────────
#  SHARDING
# ─────────────────────────────────────────────────────────────────────────────
p = BASE / 'sharding.json'
d = json.loads(p.read_text())

SHARDING_GUIDE = """# Database Sharding

## What Is Sharding? (Start From Zero)

Imagine a library with a million books. One librarian handles all requests.
When the library gets popular, one librarian can't keep up — too many visitors.

One solution: hire more librarians and split the books. Librarian A handles
authors A-G, Librarian B handles H-N, Librarian C handles O-Z.
Now three librarians work in parallel, each handling a third of the load.

That is sharding. You split your database into multiple smaller databases
(shards), each responsible for a subset of the data, running on separate
machines. All shards together hold the complete dataset.

```
Without sharding (one DB, vertical scaling):
  DB Server: 128GB RAM, 32 cores, 10TB storage
  Can't scale further — hardware limit reached
  Single point of failure

With sharding (horizontal scaling):
  Shard 1: users 0-33M      (DB server 1)
  Shard 2: users 33M-66M    (DB server 2)
  Shard 3: users 66M-100M   (DB server 3)

  Add more shards when needed. Near-linear scale.
  3x the capacity, 3x the throughput.
```

---

## Sharding vs Replication — Different Problems

```
REPLICATION:
  Same data on multiple servers.
  Purpose: high availability + read scaling.
  Master writes -> replicas receive copies.

  Master: [A B C D E F G]
  Replica 1: [A B C D E F G]  <- exact copy
  Replica 2: [A B C D E F G]  <- exact copy

  Reads distributed across replicas.
  If Master fails: promote a replica (no data loss).

SHARDING:
  Different data on each server.
  Purpose: write scaling + storage scaling beyond one machine.
  Each shard has different rows.

  Shard 1: [A B C]
  Shard 2: [D E F]
  Shard 3: [G H I]

  Writes distributed across shards (parallel write capacity).
  If Shard 1 fails: those records are UNAVAILABLE (or lost without shard replica).

COMBINED (production pattern):
  Each shard also has replication:
  Shard 1 Master + Shard 1 Replica
  Shard 2 Master + Shard 2 Replica
  Shard 3 Master + Shard 3 Replica
  Best of both: horizontal scale + high availability
```

---

## Sharding Strategies

### Range-Based Sharding
```
Divide data by value ranges of the shard key.

user_id < 33M   -> Shard 1
user_id 33M-66M -> Shard 2
user_id > 66M   -> Shard 3

Pros:
  Simple to understand and implement
  Range queries are efficient (all users 1-1000 on one shard)
Cons:
  HOTSPOT RISK: new users always go to the last shard (highest IDs)
  Uneven distribution if data is skewed
  Rebalancing needed when a shard fills up
```

### Hash-Based Sharding
```
Apply hash function to shard key, modulo by shard count.

shard = hash(user_id) % 3

user_id=1:   hash(1) % 3 = 1  -> Shard 2
user_id=5:   hash(5) % 3 = 2  -> Shard 3
user_id=9:   hash(9) % 3 = 0  -> Shard 1

Pros:
  Even distribution (no hotspots for sequential IDs)
  Predictable routing
Cons:
  Range queries are EXPENSIVE (must scan all shards)
  Adding/removing shards requires resharding (almost all data moves)
  % N strategy breaks when N changes
```

### Consistent Hashing
```
Alternative to hash(key) % N that solves the resharding problem.

Virtual hash ring (0 to 2^32):
  Shard 1 owns tokens 0-1B
  Shard 2 owns tokens 1B-2B
  Shard 3 owns tokens 2B-3B
  ...
  (ring wraps around)

hash(user_id) -> position on ring -> find shard responsible for that range

Adding Shard 4:
  Shard 4 takes a portion of Shard 1's range
  Only ~25% of data moves (vs 100% with simple hash % N)

Used by: Cassandra, DynamoDB, Redis Cluster, Riak
```

### Directory-Based Sharding
```
Lookup table maps every record to its shard.

Shard Directory (stored in a highly available cache):
  user_id=1 -> Shard 2
  user_id=5 -> Shard 1
  user_id=9 -> Shard 3

Pros:
  Maximum flexibility: move any record to any shard easily
  No re-hashing needed
Cons:
  Directory is a SINGLE POINT OF FAILURE (must be highly available)
  Directory lookup adds latency to every query
  Directory can become very large
```

---

## The Sharding Key — Most Critical Decision

The shard key determines how data is distributed. A bad shard key creates
hotspots that negate all benefits of sharding.

```
BAD SHARD KEY: created_at (timestamp)
  All new records go to the "latest" shard
  That shard gets ALL writes while others are idle
  Hotspot!

BAD SHARD KEY: status (only 3 values: active/inactive/deleted)
  Only 3 shards possible
  Doesn't scale beyond 3 nodes

GOOD SHARD KEY: user_id
  Evenly distributed across all users
  Most queries filter by user_id

GOOD SHARD KEY: hash(email)
  Uniform distribution
  Single-user queries are fast

MULTI-TENANT: tenant_id
  All data for one tenant on one shard (good for isolation)
  Risk: large tenants create hotspots

RULES FOR CHOOSING SHARD KEY:
  1. High cardinality (many unique values — not just a few)
  2. Uniform distribution (no value dominates)
  3. Your most common query filter (queries without shard key = scatter-gather)
  4. Immutable (changing the key means moving the record)
```

---

## The Downsides of Sharding

```
1. CROSS-SHARD JOINS:
   SELECT users.name, orders.amount
   FROM users JOIN orders ON users.id = orders.user_id
   WHERE users.country = 'US'

   If users on Shard 1-3 and orders on Shard 4-6:
   Must query all shards and join in application code.
   Expensive, complex.

2. CROSS-SHARD TRANSACTIONS:
   Transfer money from user_id=1 (Shard 1) to user_id=100 (Shard 3)
   No native distributed transactions in most DBs.
   Must use 2-phase commit (slow) or sagas (complex).

3. REBALANCING:
   When shard data grows unevenly or you add new shards,
   data must be moved. During rebalancing: traffic must continue,
   data must not be lost. Very complex operation.

4. OPERATIONAL COMPLEXITY:
   3x the DB instances to monitor, backup, patch, failover.
   Schema changes must be applied to every shard.
   Debugging: which shard has the bad data?

5. SCATTER-GATHER QUERIES:
   "How many total users?" -> query ALL shards, sum results
   "Top 10 users by activity?" -> query all shards, merge, sort
   Slow and expensive.
```

---

## When to Shard vs Alternatives

```
DO THESE FIRST (in order):
  1. Optimise queries (missing indexes, N+1, slow queries)
  2. Add read replicas (for read-heavy workloads)
  3. Add caching (Redis in front of DB)
  4. Vertical scaling (bigger DB server: more RAM, faster SSD)
  5. Partition tables (within one DB — simpler than sharding)
  THEN: Shard when nothing else works

SHARD WHEN:
  Single DB server maxes out on writes (not reads — use replicas for that)
  Data size exceeds single server capacity (>5-10TB)
  Write throughput exceeds single master capacity
  Google/Facebook scale: billions of records

DON'T SHARD WHEN:
  You just need more read capacity (use read replicas)
  You need to run complex joins often (sharding makes this hell)
  Your data fits on one server (most apps never need sharding)
  Startup / early stage (premature optimisation)
```

---

## Mind Map

```
SHARDING
|
+-- CONCEPT
|   +-- Split data across multiple DB instances
|   +-- Each shard = subset of data
|   +-- All shards = complete dataset
|
+-- STRATEGIES
|   +-- Range-based  (simple but hotspot risk)
|   +-- Hash-based   (even dist, bad for range queries)
|   +-- Consistent hashing (good for adding shards)
|   +-- Directory-based (most flexible, needs lookup table)
|
+-- SHARD KEY RULES
|   +-- High cardinality
|   +-- Even distribution
|   +-- Matches common query patterns
|   +-- Immutable
|
+-- PROBLEMS
|   +-- Cross-shard joins (do in app layer)
|   +-- Cross-shard transactions (2PC or Sagas)
|   +-- Rebalancing (hard)
|   +-- Scatter-gather queries (slow)
|
+-- ALTERNATIVES FIRST
    +-- Indexes -> replicas -> caching -> vertical scale -> partition -> THEN shard
```

---

## References and Further Learning

### Videos (Watch These!)
- **Database Sharding Explained** by ByteByteGo:
  https://www.youtube.com/watch?v=5faMjKuB9bc
  - Visual walkthrough of sharding strategies.
- **Consistent Hashing Explained** by Tech Dummies Narendra L:
  https://www.youtube.com/watch?v=UF9Iqmg94tk
  - Deep dive into consistent hashing with visual ring diagrams.

### Free Books and Articles
- **System Design Primer — Sharding**: https://github.com/donnemartin/system-design-primer#sharding
- **AWS DynamoDB Sharding**: https://aws.amazon.com/blogs/database/choosing-the-right-dynamodb-partition-key/

### Practice
- **Design a URL shortener with sharding**: classic system design exercise.
  How do you shard the mapping table? What is the shard key?
"""

SHARDING_Q = [
    {"id":"shard-q1","type":"mcq","prompt":"What is the primary purpose of database sharding?",
     "choices":["Improve read performance with copies","Horizontal partitioning — split data across multiple DB instances to scale writes and storage beyond what a single machine can handle",
                "Encrypt database data","Backup and disaster recovery"],
     "answerIndex":1,"explanation":"Sharding splits data rows across machines. Each shard handles a fraction of the writes and stores a fraction of the data. Unlike replication (same data everywhere), sharding divides data to distribute load.","tags":["sharding","scaling","basics"]},
    {"id":"shard-q2","type":"mcq","prompt":"What is the difference between sharding and replication?",
     "choices":["They are the same","Sharding: different data on each server (scale writes/storage). Replication: same data on each server (scale reads + HA). Production DBs often combine both.",
                "Replication scales writes, sharding scales reads","Sharding is for NoSQL only"],
     "answerIndex":1,"explanation":"Replication = copies of all data (reads spread across replicas). Sharding = data partitioned (writes spread across shards). Production: shard the data AND replicate each shard for HA. You need both for a truly scalable, reliable system.","tags":["sharding","replication","comparison"]},
    {"id":"shard-q3","type":"mcq","prompt":"What is the problem with using `status` (active/inactive/deleted) as a shard key?",
     "choices":["Status is a reserved word","Low cardinality — only 3 possible values means only 3 possible shards, and active users create a hotspot on the 'active' shard",
                "Status changes too frequently","Status is not indexed"],
     "answerIndex":1,"explanation":"A good shard key needs HIGH cardinality (many unique values) and EVEN distribution. Status has 3 values — almost all records are 'active', creating a massive hotspot. Never use boolean or low-enum fields as shard keys.","tags":["sharding","shard-key","cardinality"]},
    {"id":"shard-q4","type":"mcq","prompt":"What is consistent hashing and why is it better than hash(key) % N for sharding?",
     "choices":["It gives the same hash every time","It maps keys to positions on a virtual ring — adding/removing a shard only requires moving ~1/N of data instead of rehashing everything",
                "It is faster than modulo hashing","It prevents hash collisions"],
     "answerIndex":1,"explanation":"hash(key) % 3: add a 4th shard and hash(key) % 4 changes mappings for ~75% of data — massive data movement. Consistent hashing: adding a node only affects the adjacent range on the ring, ~25% data movement.","tags":["sharding","consistent-hashing"]},
    {"id":"shard-q5","type":"mcq","prompt":"What is a scatter-gather query in a sharded database?",
     "choices":["A write that goes to multiple shards","A query that must be sent to ALL shards because it cannot be routed to a single shard — results are merged in the application layer",
                "A query that uses wildcards","A distributed join"],
     "answerIndex":1,"explanation":"'Select top 10 users by total spend' — total spend is spread across all shards. Must query all N shards, merge all results, sort globally. Expensive: N network round trips, N query executions. Avoid by designing queries to be shard-local.","tags":["sharding","scatter-gather","queries"]},
    {"id":"shard-q6","type":"mcq","prompt":"What makes a good shard key?",
     "choices":["Low cardinality and common in queries","High cardinality, uniform distribution, matches common query filters, and is immutable (doesn't change over time)",
                "Auto-increment integer","Most recently updated field"],
     "answerIndex":1,"explanation":"Shard key must: have many unique values (high cardinality), distribute evenly (no single value dominates), appear in your most common queries (otherwise scatter-gather every time), and never change (changing key = moving the record = nightmare).","tags":["sharding","shard-key"]},
    {"id":"shard-q7","type":"mcq","prompt":"Why are cross-shard transactions difficult?",
     "choices":["They are not difficult at all","Standard DB transactions (ACID) require all operations on the same DB server. Cross-shard = operations on different servers — requires 2-phase commit (slow) or sagas (complex application logic)",
                "Cross-shard transactions are blocked by firewalls","You must use NoSQL for cross-shard"],
     "answerIndex":1,"explanation":"ACID transactions within one DB are simple. Across shards (different machines), you need distributed coordination: 2-phase commit (slow, coordinator is bottleneck) or Saga pattern (eventual consistency, application manages compensation logic). Both are complex.","tags":["sharding","transactions","distributed"]},
    {"id":"shard-q8","type":"mcq","prompt":"What should you do BEFORE sharding your database?",
     "choices":["Shard immediately at startup","Optimise queries with indexes, add read replicas for read load, add caching (Redis), try vertical scaling — shard only when these are exhausted",
                "Always start with sharding","Sharding has no prerequisites"],
     "answerIndex":1,"explanation":"Sharding is operationally complex. Try in order: 1) Add missing indexes (often 100x speedup), 2) Read replicas (for read-heavy), 3) Redis cache (for hot data), 4) Bigger server. Most applications never need to shard. Premature sharding = operational nightmare.","tags":["sharding","when-to-shard","alternatives"]},
    {"id":"shard-q9","type":"mcq","prompt":"What problem does range-based sharding have?",
     "choices":["Range queries are impossible","Hotspot: sequential IDs cause all new writes to go to the highest shard. Auto-increment user_id means Shard 3 (highest IDs) gets ALL new user writes while Shard 1 sits idle.",
                "Range sharding requires consistent hashing","Range sharding only works for integers"],
     "answerIndex":1,"explanation":"Range sharding on sequential keys (timestamps, auto-increment IDs) creates write hotspots on the latest range. All new data piles into one shard. Fix: use hash-based sharding, or add random suffix to keys, or use UUID v4 as primary key.","tags":["sharding","range-based","hotspot"]},
    {"id":"shard-q10","type":"mcq","prompt":"How does directory-based sharding work?",
     "choices":["Uses a hash function","Uses a lookup table (directory) mapping each record or key range to its shard — maximum flexibility, any record can be on any shard",
                "Shards based on alphabetical order","Uses consistent hashing ring"],
     "answerIndex":1,"explanation":"Directory sharding: lookup service maps user_id=123 -> Shard 2. Want to move user 123 to Shard 5? Just update the directory entry. No rehashing. Most flexible. Downside: directory must be highly available (it's in the critical path for every request).","tags":["sharding","directory-based"]},
    {"id":"shard-q11","type":"mcq","prompt":"A user makes a payment and the sender is on Shard 1, receiver on Shard 3. How do you ensure atomicity?",
     "choices":["Use a foreign key constraint","Both accounts are on the same shard always","Use 2-phase commit (distributed transaction protocol) or Saga pattern (compensating transactions) — no native ACID across shards",
                "Use database replication"],
     "answerIndex":2,"explanation":"Cross-shard atomicity requires: 2PC (coordinator asks both shards to prepare, then commit — slow, coordinator is bottleneck) or Saga (each step has a compensating rollback action — eventual consistency, complex orchestration). Design to avoid cross-shard transactions when possible.","tags":["sharding","transactions","saga"]},
    {"id":"shard-q12","type":"mcq","prompt":"What happens to a sharded system during rebalancing?",
     "choices":["System shuts down completely","Traffic is paused until data moves","Data is migrated between shards while the system continues operating — requires careful coordination to avoid serving from both old and new locations simultaneously",
                "Rebalancing is instant"],
     "answerIndex":2,"explanation":"Rebalancing while live: double-write to both old and new shard during migration, switch reads to new shard, then stop writing to old. Or use consistent hashing which minimises data movement. This is one of the hardest operations in a sharded system.","tags":["sharding","rebalancing","operations"]},
    {"id":"shard-q13","type":"mcq","prompt":"Which database does NOT support automatic sharding natively?",
     "choices":["MongoDB","Cassandra","PostgreSQL (manual sharding or use Citus extension)","DynamoDB"],
     "answerIndex":2,"explanation":"MongoDB, Cassandra, DynamoDB — built-in distributed sharding. PostgreSQL is single-node by default. Sharding options: Citus (extension for horizontal scale), Vitess (middleware by YouTube), or manual application-level sharding. This is why NoSQL DBs are often chosen for massive scale.","tags":["sharding","databases","postgresql"]},
    {"id":"shard-q14","type":"mcq","prompt":"What is a 'virtual shard' or 'virtual partition' in consistent hashing?",
     "choices":["A shard with no data","A shard in read-only mode","Multiple positions on the hash ring assigned to one physical shard — ensures even distribution even with few shards and handles node weight differences",
                "A backup shard"],
     "answerIndex":2,"explanation":"With 3 shards and a simple ring, one shard might get 60% of traffic due to uneven ring positioning. Virtual nodes (vnodes): each physical shard gets 100+ positions on the ring. Distribution becomes statistically even. Also: a powerful node gets more vnodes (handles more traffic).","tags":["sharding","consistent-hashing","vnodes"]},
    {"id":"shard-q15","type":"mcq","prompt":"What is the fan-out problem in sharded writes?",
     "choices":["Fan-out is a network issue","When one user action must write to multiple shards simultaneously (e.g., updating a timeline for 1M followers spread across all shards) — creates write amplification",
                "Fan-out only affects reads","Fan-out is specific to Redis"],
     "answerIndex":1,"explanation":"Twitter-like: user A has 1M followers. A tweets -> write to 1M timelines. Followers are spread across all shards -> write to every shard. Write amplification. Solutions: pull model (user fetches timeline on load), hybrid model (push for regular users, pull for celebrities).","tags":["sharding","fan-out","write-amplification"]},
    {"id":"shard-q16","type":"mcq","prompt":"How does sharding affect schema migrations?",
     "choices":["Schema migration is easier with sharding","Schema changes must be applied to EVERY shard — requires careful rolling migrations, backward compatibility, and coordination across all shard instances",
                "Sharding prevents schema changes","Schema only applies to Shard 1"],
     "answerIndex":1,"explanation":"ALTER TABLE users ADD COLUMN: must run on all 3 shards. If you run it on Shard 1 first, queries must work with both old and new schema while migration is in progress. Requires: backward-compatible migrations, feature flags, blue-green deployments.","tags":["sharding","operations","schema-migration"]},
    {"id":"shard-q17","type":"mcq","prompt":"What is 'resharding' and when is it needed?",
     "choices":["Initial sharding setup","Redistributing existing sharded data across a different number of shards — needed when shards become uneven, full, or when adding new shard nodes",
                "Moving a shard to a different cloud","Deleting duplicate shards"],
     "answerIndex":1,"explanation":"Resharding: if you start with 3 shards and need 6, data must move. With simple hash % 3, all data changes shard (massive movement). With consistent hashing: only the adjacent ranges move (~50% of data for doubling). Resharding while live is the hardest database operation.","tags":["sharding","resharding","operations"]},
    {"id":"shard-q18","type":"mcq","prompt":"How does Vitess (YouTube's MySQL sharding layer) work?",
     "choices":["It replaces MySQL entirely","A middleware layer that sits in front of MySQL instances, handling sharding logic, connection pooling, and query routing — apps talk to Vitess as if it were a single MySQL",
                "Vitess is a NoSQL database","Vitess only works with Google Cloud"],
     "answerIndex":1,"explanation":"Vitess (now CNCF project, used by PlanetScale) wraps MySQL in a sharding layer. App sends SQL to Vitess -> Vitess parses query -> routes to correct shard(s) -> merges results if needed. Transparent horizontal scaling for MySQL without changing app code.","tags":["sharding","vitess","mysql"]},
    {"id":"shard-q19","type":"mcq","prompt":"What is a hotspot in sharding and how do you fix it?",
     "choices":["A shard that runs out of disk","A shard that receives disproportionate traffic due to a popular or sequential shard key — fix by adding random salt, using hash-based sharding, or splitting the hot shard",
                "A shard with corrupted data","Multiple shards using same hardware"],
     "answerIndex":1,"explanation":"Hotspot: shard for users A-G gets 80% of traffic because most users have names starting A-G. Or: timestamp-based shard key means all 'today' writes go to one shard. Fix: hash the key first, add random suffix, or split the hot shard into sub-shards.","tags":["sharding","hotspot"]},
    {"id":"shard-q20","type":"mcq","prompt":"Which of the following queries is NOT affected by sharding (avoids scatter-gather)?",
     "choices":["SELECT COUNT(*) FROM users","SELECT * FROM orders WHERE total > 100 ORDER BY total DESC","SELECT * FROM users WHERE user_id = 12345 (user_id IS the shard key)","SELECT AVG(salary) FROM employees"],
     "answerIndex":2,"explanation":"Query by shard key (user_id = 12345) routes to exactly ONE shard — fast. Queries without the shard key (COUNT(*), AVG, range on non-shard field) must hit ALL shards and aggregate results — scatter-gather. Design your most common queries to filter by shard key.","tags":["sharding","query-routing","shard-key"]},
]

SHARDING_FC = [
    {"id":"shard-fc1","front":"Sharding vs Replication purpose","back":"Sharding: different data on each server. Purpose: scale WRITES and STORAGE beyond one machine. Replication: same data on each server. Purpose: scale READS + high availability. Production: shard data + replicate each shard.","tags":["sharding","replication"]},
    {"id":"shard-fc2","front":"Good shard key checklist","back":"1. High cardinality (many unique values). 2. Even distribution (no value dominates). 3. Appears in most common query WHERE clause. 4. Immutable (changing it moves the record). Bad: status, boolean, timestamp for sequential writes.","tags":["sharding","shard-key"]},
    {"id":"shard-fc3","front":"Consistent hashing vs modulo hashing","back":"hash(key) % N: adding a node reshuffles ~(N-1)/N of data. Consistent hashing ring: adding a node moves only ~1/N data (just adjacent range). Use consistent hashing for any system where nodes add/remove dynamically.","tags":["sharding","consistent-hashing"]},
    {"id":"shard-fc4","front":"Cross-shard transaction options","back":"2-Phase Commit: coordinator asks all shards to prepare, then commit. Slow, coordinator = bottleneck. Saga: each step has compensation (rollback) action. Eventual consistency. Best: design to avoid cross-shard transactions.","tags":["sharding","transactions"]},
    {"id":"shard-fc5","front":"Do these BEFORE sharding","back":"1. Add missing indexes. 2. Read replicas (for read-heavy load). 3. Redis caching. 4. Vertical scale. 5. Table partitioning (within one DB). Only shard when single-master write throughput or single-machine storage is truly exhausted.","tags":["sharding","alternatives"]},
    {"id":"shard-fc6","front":"Scatter-gather pattern","back":"Query without shard key -> must query ALL N shards -> merge results in app. Slow: N round trips. Fix: ensure common queries include shard key in WHERE. Unavoidable aggregates (COUNT, SUM) require scatter-gather.","tags":["sharding","scatter-gather"]},
    {"id":"shard-fc7","front":"Resharding with consistent hashing","back":"Simple hash % N: adding shard reshuffles ~75% of data. Consistent hashing: adding shard moves ~1/N data (only adjacent ring range). Virtual nodes (vnodes): each physical shard = 100 ring positions -> even distribution.","tags":["sharding","resharding","consistent-hashing"]},
    {"id":"shard-fc8","front":"Operational sharding challenges","back":"Schema migrations: apply to every shard (backward-compatible, rolling). Monitoring: N dashboards. Backup: N databases. Debug: which shard has the bad row? Cross-shard queries: in-app aggregation. Rebalancing: hardest live operation.","tags":["sharding","operations"]},
]

d['guide'] = SHARDING_GUIDE
d['questions'] = SHARDING_Q
d['flashcards'] = SHARDING_FC
with open(p, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"sharding.json: guide={len(SHARDING_GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

# ─────────────────────────────────────────────────────────────────────────────
#  PARTITIONING
# ─────────────────────────────────────────────────────────────────────────────
p = BASE / 'partitioning.json'
d = json.loads(p.read_text())

PARTITIONING_GUIDE = """# Database Partitioning

## What Is Partitioning? (Start From Zero)

Imagine an office filing cabinet with 10,000 folders. To find a folder, you search
all 10,000. Now imagine the cabinet has 12 drawers labelled by month (January-December).
Each drawer holds ~833 folders. To find a folder, you open the right drawer and search
833 — 12x faster.

Database partitioning does the same. A table with 1 billion rows is split into
smaller physical pieces (partitions) that the query engine can skip over entirely.

**Key difference from sharding:**
```
PARTITIONING:
  Still ONE database server
  Table appears as one logical table to applications
  DB engine manages which physical partition data goes into
  Transparent: your SQL doesn't change
  Goal: query performance + manageability

SHARDING:
  MULTIPLE database servers
  Each server has its own DB
  Application must route queries to the right shard
  Not transparent: you must shard-aware code
  Goal: scale beyond single machine
```

---

## Types of Partitioning

### Range Partitioning
```
Split rows based on a value range of a column.

CREATE TABLE orders (
    id       BIGINT,
    user_id  BIGINT,
    amount   DECIMAL,
    created  DATE
) PARTITION BY RANGE (created);

CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE orders_2025 PARTITION OF orders
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

Query: SELECT * FROM orders WHERE created > '2025-01-01'
  Database: skips orders_2024 entirely (partition pruning)
  Scans only orders_2025 -> 2x less data scanned

Best for: time-series data, date-based queries
Risk: hotspot on the latest partition (all new writes go there)
```

### List Partitioning
```
Split rows based on discrete values of a column.

PARTITION BY LIST (country);
  Partition USA:    country IN ('US', 'CA', 'MX')
  Partition EU:     country IN ('DE', 'FR', 'UK', 'IT')
  Partition ASIA:   country IN ('JP', 'KR', 'CN', 'IN')

Query: SELECT * FROM users WHERE country = 'DE'
  Only scans EU partition

Best for: data categorised by region, status, category
Use with: column that has known, limited set of values
```

### Hash Partitioning
```
Apply hash function to a column, modulo by partition count.

PARTITION BY HASH (user_id) PARTITIONS 8;

user_id=1   -> hash(1) % 8 = 1 -> Partition 1
user_id=10  -> hash(10) % 8 = 2 -> Partition 2
user_id=100 -> hash(100) % 8 = 4 -> Partition 4

Evenly distributes rows even if user_id is sequential.
Good for: distributing write load evenly within one server
Bad for: range queries (must scan all partitions for range)
```

### Composite Partitioning
```
Combine multiple partitioning strategies.

First divide by year (range), then by country (list):
  Partition 2024_US, Partition 2024_EU
  Partition 2025_US, Partition 2025_EU

Fine-grained pruning: query for US users in 2025
only scans Partition 2025_US — skips all others.
```

---

## Partition Pruning — Why It Is Powerful

```
PARTITION PRUNING = query optimizer eliminates irrelevant partitions.

WITHOUT partitioning:
  SELECT * FROM orders WHERE created > '2025-01-01'
  Scans: 10 billion rows, all years
  Time: 5 minutes

WITH range partitioning by year:
  Query planner: created > '2025-01-01' -> only need orders_2025
  Skips: orders_2024, orders_2023, orders_2022... (9 out of 10 partitions)
  Scans: 1 billion rows (only 2025 partition)
  Time: 30 seconds

REQUIREMENT for pruning to work:
  The partition column MUST appear in the WHERE clause.
  SELECT * FROM orders WHERE user_id = 123 <- no date filter
  -> must scan ALL partitions (no pruning, possibly WORSE than no partitioning)

Check your queries use EXPLAIN ANALYZE in PostgreSQL:
  EXPLAIN ANALYZE SELECT * FROM orders WHERE created > '2025-01-01';
  Look for "Partitions scanned: 1 of 10" in the output.
```

---

## Partitioning vs Indexing — When to Use Which

```
INDEXES:
  Find specific rows by value quickly (O(log N) search)
  Good for: varied queries on different columns
  Bad for: deleting large date ranges, archiving old data

PARTITIONING:
  Remove entire partitions in milliseconds (DROP PARTITION = instant)
  Good for: time-series data with rolling deletion, bulk operations
  Good for: queries always filtered by the partition column

COMBINE BOTH (common pattern):
  Partition by month (range)
  Index by user_id within each partition
  Query: WHERE created BETWEEN '2025-01-01' AND '2025-01-31' AND user_id = 123
    -> pruned to January 2025 partition
    -> index on user_id narrows to exact rows
    -> extremely fast even on huge tables
```

---

## Data Archival — The Killer Use Case for Partitioning

```
PROBLEM:
  orders table has 10 years of data: 10 billion rows.
  Most queries are for the last 30 days.
  9.7 years of old data sits there, slowing every query.

SOLUTION WITH PARTITIONING:
  Partition by month.
  After 12 months: 'detach' old partition from the table (instant).
  Move old partition to cold storage (S3, Glacier).
  Main table: only current year's data — fast again.

  ALTER TABLE orders DETACH PARTITION orders_2020_jan;
  -- Now orders_2020_jan is a standalone table
  -- orders table no longer contains 2020 data
  -- This operation is INSTANT (no data movement)

  Contrast with: DELETE FROM orders WHERE created < '2020-01-01'
  -- Must delete 1 billion rows, one by one
  -- Locks table, fills transaction log, takes hours

PARTITIONING + ARCHIVAL IS O(1) = instant.
DELETE old rows IS O(N) = takes hours.
```

---

## Horizontal vs Vertical Partitioning

```
HORIZONTAL PARTITIONING (most common, what we've discussed):
  Split ROWS into different partitions.
  All partitions have same columns.
  users_1-1000, users_1001-2000, users_2001-3000

VERTICAL PARTITIONING:
  Split COLUMNS into different tables.
  Hot columns (accessed frequently) in one table.
  Cold columns (rarely accessed) in another.

  users_core:  user_id, name, email, login_count  <- read often
  users_detail: user_id, bio, settings, preferences <- read rarely

  SELECT user_id, name FROM users_core  <- 4 columns, small rows, fast
  vs
  SELECT * FROM users  <- 50 columns, huge rows, slow

  Works like projected storage / columnar storage concept.
  Used in: database normalisation, columnar DBs (BigQuery, Redshift)
```

---

## Mind Map

```
DATABASE PARTITIONING
|
+-- TYPES
|   +-- Range (date ranges, number ranges)
|   +-- List  (country, category, region)
|   +-- Hash  (even distribution)
|   +-- Composite (range + list, two levels)
|
+-- PARTITION PRUNING
|   +-- Query skips irrelevant partitions
|   +-- Requires partition column in WHERE clause
|   +-- EXPLAIN ANALYZE shows partitions scanned
|
+-- USE CASES
|   +-- Time-series data (logs, events, orders by date)
|   +-- Rolling archival (DROP PARTITION = instant)
|   +-- Even write distribution (hash partitioning)
|   +-- Regional data separation (list partitioning)
|
+-- vs SHARDING
|   +-- Same server vs multiple servers
|   +-- Transparent to app vs requires shard routing
|   +-- Query performance vs horizontal scale
|
+-- vs INDEXING
    +-- Index: find rows by value (B-tree)
    +-- Partition: skip entire data chunks
    +-- Combine: partition by date + index by user_id
```

---

## References and Further Learning

### Videos (Watch These!)
- **Database Partitioning Explained** by Hussein Nasser:
  https://www.youtube.com/watch?v=QA25cL_vDeo
  - PostgreSQL partitioning demo, partition pruning explained.
- **Partitioning vs Sharding vs Indexing** by ByteByteGo:
  https://www.youtube.com/watch?v=wXvljefXyEo
  - Clear comparison of all three approaches.

### Free Books and Articles
- **PostgreSQL Partitioning Docs**: https://www.postgresql.org/docs/current/ddl-partitioning.html
- **MySQL Partitioning**: https://dev.mysql.com/doc/refman/8.0/en/partitioning.html

### Practice
- Create a large orders table in PostgreSQL, add range partitions by month,
  run EXPLAIN ANALYZE before and after — see partition pruning in action.
"""

PARTITIONING_Q = [
    {"id":"part-q1","type":"mcq","prompt":"What is database partitioning?",
     "choices":["Splitting a database across multiple servers","Splitting a large table into smaller physical pieces within the same database server — still appears as one logical table to applications",
                "Encrypting database columns","Creating read replicas"],
     "answerIndex":1,"explanation":"Partitioning = one DB server, one logical table, split into physical partitions. App SQL doesn't change. DB engine routes queries to relevant partitions. Goal: query performance and manageability, not horizontal scale (that's sharding).","tags":["partitioning","basics"]},
    {"id":"part-q2","type":"mcq","prompt":"What is the key difference between partitioning and sharding?",
     "choices":["Partitioning is for NoSQL, sharding for SQL","Partitioning: same server, transparent to app, improves query performance. Sharding: multiple servers, app must route queries, scales beyond one machine.",
                "Sharding is always better","They are the same concept"],
     "answerIndex":1,"explanation":"Partitioning keeps all data on one machine — simpler, transparent, great for performance. Sharding spreads data across multiple machines — complex, app-aware, needed when one machine's capacity is exhausted. Choose partitioning first.","tags":["partitioning","sharding","comparison"]},
    {"id":"part-q3","type":"mcq","prompt":"What is partition pruning?",
     "choices":["Deleting old partitions","The query optimizer skipping irrelevant partitions entirely — if query filters by date and data is partitioned by date, only the relevant date partition is scanned",
                "Compressing partitions","Merging small partitions"],
     "answerIndex":1,"explanation":"Pruning = skip partitions. ORDER BY date, partitioned by year: query for 2025 data? DB skips 2020-2024 partitions entirely. 10 partitions, query touches 1 = 10x less scanning. Requires partition column to appear in WHERE clause.","tags":["partitioning","partition-pruning","performance"]},
    {"id":"part-q4","type":"mcq","prompt":"You have an orders table with 10 years of data. Most queries are for the last 30 days. What partitioning strategy helps most?",
     "choices":["Hash partitioning on order_id","Range partitioning by month — queries for recent orders only scan 1-2 partitions, old data can be archived by detaching old partitions instantly",
                "List partitioning by status","No partitioning — add more indexes"],
     "answerIndex":1,"explanation":"Range by month: SELECT for last 30 days touches only 1-2 partitions out of 120 (10 years). 60x less data scanned. Old months can be detached (instant) and archived — vs DELETE which takes hours on billions of rows.","tags":["partitioning","range","time-series"]},
    {"id":"part-q5","type":"mcq","prompt":"Why is DROP PARTITION much faster than DELETE WHERE for archiving old data?",
     "choices":["DROP is a newer SQL command","DROP PARTITION detaches the physical file instantly (metadata operation). DELETE removes rows one by one, creates transaction logs, holds locks — takes hours for billions of rows.",
                "DELETE doesn't work on partitioned tables","They are the same speed"],
     "answerIndex":1,"explanation":"DROP/DETACH PARTITION: O(1) — just removes a pointer. No data movement. Instant. DELETE FROM table WHERE date < '2020': O(N) — touches every qualifying row, writes WAL logs, may lock. On 1B rows: hours. Partitioning makes archival instant.","tags":["partitioning","archival","performance"]},
    {"id":"part-q6","type":"mcq","prompt":"What type of partitioning evenly distributes rows even when the partition key is sequential?",
     "choices":["Range partitioning","List partitioning","Hash partitioning — applies hash(key) % N to determine partition, spreading sequential keys across all partitions evenly",
                "Composite partitioning"],
     "answerIndex":2,"explanation":"Range on sequential keys creates hotspots (all new rows in latest partition). Hash partitioning: hash(user_id) % 8 -> uniform distribution regardless of key sequence. Trade-off: range queries must scan all partitions (no pruning for range on hash-partitioned column).","tags":["partitioning","hash","distribution"]},
    {"id":"part-q7","type":"mcq","prompt":"What is list partitioning used for?",
     "choices":["Distributing rows by numeric range","Partitioning rows by discrete known category values — e.g., country IN ('US','CA','MX') -> North America partition",
                "Time-based archival","Even distribution by hash"],
     "answerIndex":1,"explanation":"List partitioning: explicitly map values to partitions. country='DE' -> EU partition. Queries filtering by country skip all non-EU partitions. Best for: region-based data, categorical data with known values. Not good for high-cardinality columns.","tags":["partitioning","list","categorical"]},
    {"id":"part-q8","type":"mcq","prompt":"For partition pruning to work, what must be true about your query?",
     "choices":["Query must use SELECT *","The partition column must appear in the WHERE clause of the query",
                "Query must use ORDER BY","Joins are not allowed"],
     "answerIndex":1,"explanation":"Partition pruning only works if the query filters by the partition key. SELECT * FROM orders WHERE user_id = 123 (partitioned by date): no date filter -> must scan ALL partitions. SELECT WHERE created > '2025-01-01': pruning works, skips older partitions.","tags":["partitioning","partition-pruning","query-design"]},
    {"id":"part-q9","type":"mcq","prompt":"What is vertical partitioning?",
     "choices":["Partitioning rows into multiple tables","Splitting COLUMNS — frequently accessed columns in one table, rarely accessed in another — reduces row size for hot queries",
                "Partitioning across multiple servers","Range-based row partitioning"],
     "answerIndex":1,"explanation":"Vertical partitioning splits columns. users_core (user_id, name, email) + users_detail (user_id, bio, settings). Queries on users_core read smaller rows (faster). Only join with users_detail when needed. Similar to database normalisation / columnar storage concept.","tags":["partitioning","vertical","columns"]},
    {"id":"part-q10","type":"mcq","prompt":"You need country-specific queries AND year-based archival on an orders table. What partitioning approach combines both?",
     "choices":["Two separate tables","Composite partitioning: first by year (range), then by country (list) — query for US orders in 2025 scans only the 2025_US partition",
                "Sharding by country","Multiple databases"],
     "answerIndex":1,"explanation":"Composite (sub-partitioning): first dimension by year range, second by country list. Orders_2025 -> Orders_2025_US, Orders_2025_EU, Orders_2025_ASIA. Query with both filters: only one sub-partition scanned. Without composite: range prune works but must still scan all country slices.","tags":["partitioning","composite","design"]},
    {"id":"part-q11","type":"mcq","prompt":"Should you partition a table with 10,000 rows?",
     "choices":["Yes, always partition for future growth","No — partitioning adds overhead. Only partition tables with millions+ rows where query scans are genuinely slow. Small tables are faster without partitioning.",
                "Only hash partition small tables","Always range partition"],
     "answerIndex":1,"explanation":"Partitioning has overhead: partition metadata, partition checking for every query, more complex EXPLAIN plans. For small tables, a good index is far better. Partition when: full table scan on large table is slow AND queries naturally filter by a good partition column.","tags":["partitioning","when-to-use"]},
    {"id":"part-q12","type":"mcq","prompt":"How does partitioning help with database maintenance (VACUUM in PostgreSQL)?",
     "choices":["Partitioning breaks VACUUM","VACUUM and ANALYZE can run per-partition in parallel instead of on the entire table — reducing lock duration and maintenance windows",
                "Partitioning replaces VACUUM","Partitions never need VACUUM"],
     "answerIndex":1,"explanation":"VACUUM on a 10TB table: hours, holds locks on the whole table. VACUUM on 10 x 1TB partitions: can run concurrently on each partition, much shorter per-partition lock, can be scheduled rolling. Partitioning makes all maintenance operations more manageable.","tags":["partitioning","maintenance","postgresql"]},
    {"id":"part-q13","type":"mcq","prompt":"What is 'partition key' selection rule similar to sharding?",
     "choices":["Any column works equally well","Choose partition key that appears in most WHERE clauses, has enough cardinality for good pruning, and matches your archival/deletion patterns",
                "Always use primary key","Use the largest column"],
     "answerIndex":1,"explanation":"Partition key selection: appears in most query filters (for pruning), sufficient cardinality (date has 365 values/year, status has 3 values = poor), aligns with data lifecycle (partition by month for monthly archival). Bad partition key = full table scans every query.","tags":["partitioning","partition-key"]},
    {"id":"part-q14","type":"mcq","prompt":"What SQL command would you use to instantly remove a month's worth of old time-series data from a partitioned table?",
     "choices":["DELETE FROM orders WHERE month = '2020-01'","DROP TABLE orders_2020_01","ALTER TABLE orders DETACH PARTITION orders_2020_01; DROP TABLE orders_2020_01;",
                "TRUNCATE TABLE orders WHERE partition = '2020-01'"],
     "answerIndex":2,"explanation":"DETACH PARTITION: removes the partition from the parent table (instant, no data moved). Then DROP TABLE the detached partition (instant, deletes the file). Total: 2 metadata operations, takes milliseconds. The rows are gone but no row-by-row deletion needed.","tags":["partitioning","archival","sql"]},
    {"id":"part-q15","type":"mcq","prompt":"How can you verify partition pruning is happening in PostgreSQL?",
     "choices":["Check the pg_partitions table","Run EXPLAIN ANALYZE on the query and look for 'Partitions scanned' — it shows how many partitions the planner chose to scan vs total partitions",
                "Count rows in each partition","Run ANALYZE TABLE"],
     "answerIndex":1,"explanation":"EXPLAIN ANALYZE SELECT ... shows 'Partitions: scanned 1 of 120'. If it shows scanned 120 of 120, pruning is NOT happening (check your WHERE clause includes the partition key with a constant, not a variable or subquery).","tags":["partitioning","postgresql","explain"]},
    {"id":"part-q16","type":"mcq","prompt":"What happens to a global index on a partitioned table when you drop a partition?",
     "choices":["The index self-heals automatically","Global indexes must be rebuilt after dropping a partition — this is one reason LOCAL indexes (one per partition) are preferred for most scenarios",
                "Dropping a partition drops all data","Global indexes are unaffected"],
     "answerIndex":1,"explanation":"PostgreSQL: detaching/dropping a partition marks global indexes as INVALID — must run REINDEX. This is expensive on large tables. Prefer LOCAL indexes (each partition has its own index, only that partition's index affected when partition is dropped).","tags":["partitioning","indexes","postgresql"]},
    {"id":"part-q17","type":"mcq","prompt":"Can you add a partition to a running production database without downtime?",
     "choices":["No — requires full table lock","Yes — adding a new partition is a metadata-only DDL operation in PostgreSQL 12+ that does not lock the table",
                "Only during maintenance windows","Requires application restart"],
     "answerIndex":1,"explanation":"PostgreSQL 12+: CREATE TABLE new_partition PARTITION OF parent FOR VALUES FROM (...) TO (...) acquires a brief metadata lock, not a full table lock. The table remains readable and writable during partition creation. Zero downtime partition management.","tags":["partitioning","operations","zero-downtime"]},
    {"id":"part-q18","type":"mcq","prompt":"What is the 'default partition' in PostgreSQL?",
     "choices":["The first partition created","Catches rows that don't match any defined partition — prevents insert failures when new values appear (e.g., new country code not in any list partition)",
                "The most queried partition","A partition on the primary key"],
     "answerIndex":1,"explanation":"CREATE TABLE orders_default PARTITION OF orders DEFAULT. Any row whose partition key doesn't match an existing partition goes here. Without it: INSERT fails for unmapped values. With it: rows are captured for later investigation/redistribution.","tags":["partitioning","default-partition","postgresql"]},
    {"id":"part-q19","type":"mcq","prompt":"What is the relationship between partitioning and query parallelism?",
     "choices":["Partitioning prevents parallelism","Multiple partitions can be scanned in parallel by different worker threads/processes — a query scanning 10 partitions may use 10 parallel workers, dramatically reducing query time",
                "Parallelism only works without partitioning","Only hash partitions support parallel scans"],
     "answerIndex":1,"explanation":"PostgreSQL parallel query: one worker per partition (or sub-group of partitions). Aggregate on 10 partitions with 10 workers: 10x faster than sequential scan. Enable with max_parallel_workers_per_gather. Sharding extends this further across machines.","tags":["partitioning","parallelism","performance"]},
    {"id":"part-q20","type":"mcq","prompt":"Which scenario is BEST suited for list partitioning?",
     "choices":["Orders table with 10 years of data","User table partitioned by continent — queries almost always filter by continent (Europe, North America, Asia)",
                "Sensor readings arriving every second","Users table with random UUID primary key"],
     "answerIndex":1,"explanation":"List partitioning: partition by discrete known categories. Continent has 7 values — perfect. User queries WHERE continent = 'Europe' -> only Europe partition scanned. Archiving: detach continent partitions easily. Range suits time-series. Hash suits uniform distribution needs.","tags":["partitioning","list","use-cases"]},
]

PARTITIONING_FC = [
    {"id":"part-fc1","front":"Partitioning vs Sharding one-liner","back":"Partitioning: ONE server, split within DB, transparent to app, improves query speed. Sharding: MULTIPLE servers, app routes queries, scales beyond one machine. Do partitioning first before considering sharding.","tags":["partitioning","sharding"]},
    {"id":"part-fc2","front":"Range vs List vs Hash partition strategy","back":"Range: date/time ranges (time-series, archival). List: discrete categories (country, region, status). Hash: even distribution for sequential keys. Composite: range then list for two-dimensional filtering.","tags":["partitioning","strategy"]},
    {"id":"part-fc3","front":"Partition pruning requirement","back":"Partition column MUST appear in WHERE clause for pruning to work. Check with EXPLAIN ANALYZE: look for 'Partitions scanned: 1 of 10'. If all partitions scanned, pruning failed — check query does not use variable or subquery on partition column.","tags":["partitioning","partition-pruning"]},
    {"id":"part-fc4","front":"Archival: DROP PARTITION vs DELETE","back":"DROP/DETACH PARTITION: O(1) metadata operation, instant. DELETE WHERE old_date: O(N) row-by-row, hours on billions of rows, fills WAL logs. Partition for time-series data specifically to enable instant archival.","tags":["partitioning","archival"]},
    {"id":"part-fc5","front":"Composite partitioning benefit","back":"Two dimensions of pruning. Orders partitioned by year (range) then country (list): query WHERE created > '2025' AND country = 'US' -> scans ONLY 2025_US partition. All other years and countries skipped.","tags":["partitioning","composite"]},
    {"id":"part-fc6","front":"Partitioning maintenance benefit","back":"VACUUM/ANALYZE: run per-partition independently, shorter locks. Index rebuilds: per-partition LOCAL indexes. Backup: pg_dump one partition at a time. Schema migrations: migrate one partition at a time for rolling changes.","tags":["partitioning","maintenance"]},
    {"id":"part-fc7","front":"Local vs Global partitioned indexes","back":"LOCAL index: one index per partition. Dropping partition only affects that partition's index. GLOBAL index: one index across all partitions. Dropping partition = marks global index INVALID, REINDEX needed. Prefer LOCAL indexes.","tags":["partitioning","indexes"]},
    {"id":"part-fc8","front":"When to partition","back":"Partition WHEN: table has millions+ rows, full-table scans are slow, queries naturally filter by partition column, you need rolling archival. Do NOT partition: small tables (<100K rows), unclear query patterns, complex joins required.","tags":["partitioning","when-to-use"]},
]

d['guide'] = PARTITIONING_GUIDE
d['questions'] = PARTITIONING_Q
d['flashcards'] = PARTITIONING_FC
with open(p, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"partitioning.json: guide={len(PARTITIONING_GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

