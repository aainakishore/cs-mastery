"""
Patch Scaling — Consolidated Patch Script
Consolidated from: patch_scaling_1.py, patch_scaling_2.py, patch_scaling_3.py, patch_sqs.py
Run: python3 scripts/patch_scaling.py
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

    # ── patch_scaling_1.py ──────────────────────────────────────────────────────────────────
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

    # ── patch_scaling_2.py ──────────────────────────────────────────────────────────────────
    """
    patch_scaling_2.py — expands qps-capacity.json, embedded-databases.json, relational-databases.json
    Run: python3 scripts/patch_scaling_2.py
    """
    import json
    from pathlib import Path

    BASE = Path(__file__).parent.parent / 'src/content/topics/scaling'

    # ─────────────────────────────────────────────────────────────────────────────
    #  QPS & CAPACITY PLANNING
    # ─────────────────────────────────────────────────────────────────────────────
    p = BASE / 'qps-capacity.json'
    d = json.loads(p.read_text())

    QPS_GUIDE = """# QPS, Capacity Planning & Back-of-Envelope Estimation

    ## What and Why

    Back-of-envelope estimation is a core system design interview skill and a daily
    engineering habit. Before building anything at scale, you estimate: how many
    servers? How much storage? Will the database handle the load?

    **QPS = Queries Per Second** (or Requests Per Second, RPS — used interchangeably).
    It measures throughput: how many operations your system handles each second.

    ```
    Average user on a social media app:
      - Checks feed 20 times/day
      - Likes 5 posts/day
      - Posts 1 update/day
      - Comments 3 times/day

    If platform has 1 million DAILY ACTIVE USERS (DAU):
      Feed checks:    20M / 86400s = 231 QPS
      Likes:           5M / 86400s =  58 QPS
      Posts:           1M / 86400s =  12 QPS
      Comments:        3M / 86400s =  35 QPS
      TOTAL:                       = 336 QPS average

    Always account for PEAK traffic (not average):
      Peak = 2-10x average depending on usage pattern
      Social media peak (evenings): ~3x average = ~1000 QPS peak
    ```

    ---

    ## The Numbers Every Engineer Should Know

    ```
    LATENCY CHEATSHEET:
      L1 cache reference:              1 ns
      L2 cache reference:              4 ns
      Mutex lock/unlock:              25 ns
      Main memory (RAM) access:      100 ns
      SSD random read:            100 µs  (100,000 ns)
      Database query (indexed):      1 ms  (1,000,000 ns)
      Round trip in same datacenter:  1 ms
      Database query (full scan):   10-100 ms
      AWS cross-region request:     100 ms
      HDD seek + read:               10 ms
      Packet: Europe to US:         150 ms
      Packet: US to Australia:      200 ms

    THROUGHPUT RULES OF THUMB:
      1 Gbps network:        125 MB/s
      SSD sequential read:   500 MB/s
      SSD random IOPS:      100,000 IOPS
      HDD sequential:        100 MB/s
      HDD random IOPS:          100 IOPS

    DATABASE CAPACITY:
      PostgreSQL single master:   10,000-50,000 simple queries/sec
      Redis single instance:      100,000+ GET/SET per second
      MySQL with good indexing:   20,000-40,000 queries/sec

    STORAGE ESTIMATES:
      1 KB = 1,000 bytes
      1 MB = 1,000 KB = 1,000,000 bytes
      1 GB = 1,000 MB
      1 TB = 1,000 GB
      1 PB = 1,000 TB (used by YouTube, Netflix)

      Tweet: ~280 chars = ~280 bytes
      Photo: ~200KB average (compressed)
      Video 1080p 1 minute: ~100MB
      Web page HTML: ~50KB average
    ```

    ---

    ## QPS Calculation — Step by Step

    ```
    STEP 1: Establish DAU (Daily Active Users)
      Twitter-like app: 300M DAU (this is Twitter's real number circa 2022)

    STEP 2: Estimate actions per user per day
      Read tweets: 50 times/day
      Write tweets: 3 times/day
      Send DMs: 5 times/day

    STEP 3: Calculate daily operations
      Read requests: 300M * 50 = 15 billion/day
      Write requests: 300M * 3  = 900 million/day

    STEP 4: Convert to per-second
      86,400 seconds in a day (round to 100,000 for easy math)
      Average read QPS:  15B / 86,400  = 173,611  ≈ 175,000 QPS
      Average write QPS: 900M / 86,400 =  10,416  ≈  10,000 QPS

    STEP 5: Apply peak multiplier
      Peak read QPS:  175,000 * 3 = 525,000 QPS
      Peak write QPS:  10,000 * 3 =  30,000 QPS

    STEP 6: Decide architecture
      525,000 read QPS: need caching (Redis) + read replicas
      30,000 write QPS:  single PostgreSQL master can handle ~20,000
                         -> need sharding or NoSQL for writes!
    ```

    ---

    ## Storage Estimation — Step by Step

    ```
    EXAMPLE: Photo sharing app for 1 billion users

    Daily uploads:
      10% of users upload 1 photo/day: 100M photos/day
      Average photo size: 200KB

    Daily storage needed:
      100M * 200KB = 20 TB / day

    Yearly storage:
      20 TB * 365 = 7.3 PB / year

    5-year projection:
      7.3 * 5 = 36.5 PB total storage

    Compression + deduplication: ~50% saving
    Actual storage needed: ~18 PB over 5 years

    Infrastructure:
      Object storage (S3): $0.023/GB/month
      18 PB = 18,000 TB = 18,000,000 GB
      Monthly cost: 18,000,000 * $0.023 = $414,000/month
      This is why Instagram/Facebook serve compressed thumbnails
      and multiple quality levels (thumbnail, medium, full).
    ```

    ---

    ## Bandwidth Estimation

    ```
    EXAMPLE: Video streaming service (YouTube-like)

    Users: 1 billion DAU
    Average watch time: 30 minutes/day
    Average bitrate: 5 Mbps (1080p)

    Daily bandwidth:
      1B users * 30 min * 5 Mbps
      = 1B * 1800s * 5 Mb/s
      = 9,000 billion Mb
      = 9,000 TB/day = 9 PB/day

    Peak concurrency:
      If 10% of DAU are concurrent at peak: 100M concurrent viewers
      100M * 5 Mbps = 500,000 Gbps = 500 Tbps of egress bandwidth

    This is why CDNs are mandatory at this scale.
    Serving from a single datacenter: impossible.
    CloudFront, Fastly, Akamai distribute content globally.
    ```

    ---

    ## Single-Server Capacity Limits

    ```
    SIZING A WEB SERVER (typical stateless app server):
      Modern 8-core server, well-tuned:
        Simple REST API:   1,000 - 5,000 RPS
        With DB queries:     200 - 1,000 RPS
        CPU-bound tasks:     100 - 500 RPS

      To handle 50,000 RPS of REST API: need ~10-50 web servers
      Use load balancer to distribute across them.

    SIZING A DATABASE:
      PostgreSQL (well-indexed, good hardware):
        Simple reads:   10,000 - 50,000 QPS
        Complex joins:      100 - 1,000 QPS
        Writes:           1,000 - 10,000 TPS (transactions/sec)

      If you need > 10,000 writes/sec: consider read replicas + sharding or NoSQL.

    REDIS (single instance, 16 cores):
      100,000 - 1,000,000 simple GET/SET per second
      Rich operations (ZADD, etc.): 50,000 - 200,000 per second

    RULE OF THUMB MULTIPLIERS:
      Add read replicas:    scales reads 3-5x
      Add caching (Redis):  reduces DB load 90-99%
      Add sharding:         scales writes N* (one shard per N)
      Add CDN:              removes 70-95% of static asset traffic from origin
    ```

    ---

    ## The Capacity Planning Conversation

    When asked "design Twitter" in an interview:

    ```
    STEP 1: CLARIFY SCALE
      "How many DAU?"
      "Read-heavy or write-heavy?"
      "Any viral/spike patterns to consider?"

    STEP 2: ESTIMATE QPS  (show your math)
      "300M DAU * 50 reads/day / 86,400 = ~175,000 read QPS"
      "300M DAU * 3 writes/day / 86,400 = ~10,000 write QPS"
      "Peak: 3x average = 525,000 read QPS, 30,000 write QPS"

    STEP 3: ESTIMATE STORAGE
      "1 tweet = 280 chars = ~1KB with metadata"
      "300M users * 3 tweets/day = 900M tweets/day"
      "900M * 1KB = 900GB/day -> ~300TB/year"

    STEP 4: DERIVE ARCHITECTURE
      "525,000 read QPS -> need Redis caching + multiple read replicas"
      "30,000 write QPS -> single PostgreSQL master handles 20K max"
      "  -> need sharding for writes OR switch to Cassandra"
      "300TB/year -> S3 for media (not posgres)"
      "Global users -> CDN for media delivery"
    ```

    ---

    ## Mind Map

    ```
    QPS & CAPACITY PLANNING
    |
    +-- KEY FORMULAE
    |   +-- QPS = (DAU * actions/day) / 86,400
    |   +-- Peak QPS = avg QPS * 2-10x
    |   +-- Daily storage = users * uploads/day * file_size
    |
    +-- LATENCY CHEATSHEET
    |   +-- RAM: 100ns, SSD: 100µs, DB: 1ms, Network: 1-200ms
    |
    +-- SINGLE SERVER LIMITS
    |   +-- Web server: 1-5K RPS (1K with DB)
    |   +-- PostgreSQL: 10-50K simple reads, 1-10K writes
    |   +-- Redis: 100K-1M GET/SET
    |
    +-- SCALING MULTIPLIERS
    |   +-- Read replica: 3-5x reads
    |   +-- Redis cache: 90-99% DB load reduction
    |   +-- Sharding: N* write capacity
    |   +-- CDN: 70-95% static traffic off origin
    |
    +-- INTERVIEW FRAMEWORK
        +-- Clarify -> Estimate QPS -> Estimate storage ->
        +-- Derive architecture from numbers
    ```

    ---

    ## References and Further Learning

    ### Videos (Watch These!)
    - **Back-of-Envelope Estimation** by ByteByteGo:
      https://www.youtube.com/watch?v=UC5xf8FqFeo
      - System Design interview walkthrough of estimation techniques.
    - **Capacity Planning for Software Engineers** by InfoQ:
      https://www.youtube.com/watch?v=ykdjTv8CLVI
      - Real-world capacity planning at scale.

    ### Free Books and Articles
    - **System Design Primer - Numbers Every Engineer Should Know**:
      https://github.com/donnemartin/system-design-primer#latency-numbers-every-programmer-should-know
    - **Latency Numbers Every Programmer Should Know (interactive)**:
      https://colin-scott.github.io/personal_website/research/interactive_latency.html

    ### Practice
    - **Pramp system design practice**: https://www.pramp.com/
    - Work through: "Design Twitter" with full QPS and storage estimation.
    """

    QPS_Q = [
        {"id":"qps-q1","type":"mcq","prompt":"An app has 10M DAU, each user reads 30 times/day. What is the average read QPS?",
         "choices":["300M","3,472 QPS","30,000 QPS","86,400 QPS"],
         "answerIndex":1,"explanation":"QPS = (DAU * actions/day) / seconds_in_day = (10M * 30) / 86,400 = 300M / 86,400 ≈ 3,472 QPS. Always divide by 86,400 (seconds in a day) to convert daily operations to per-second rate.","tags":["qps","capacity","calculation"]},
        {"id":"qps-q2","type":"mcq","prompt":"You calculated average QPS = 10,000. Roughly what peak QPS should you design for?",
         "choices":["10,000 (same)","20,000-100,000 — peak can be 2-10x average depending on traffic patterns",
                    "1,000 (10% of average)","100,000,000"],
         "answerIndex":1,"explanation":"Peak traffic is typically 2-10x average. Social media peaks in evenings (~3x). Flash sales can spike 10x. News events: unpredictable. Design infrastructure for peak, not average, to avoid outages. For 10K avg: design for at least 30K peak.","tags":["qps","peak-traffic","capacity"]},
        {"id":"qps-q3","type":"mcq","prompt":"Approximately how fast is RAM access compared to SSD random read?",
         "choices":["Same speed","RAM (100ns) is ~1000x faster than SSD random read (100µs)",
                    "SSD is faster than RAM","5x faster"],
         "answerIndex":1,"explanation":"RAM: ~100 nanoseconds. SSD random read: ~100 microseconds. 1µs = 1000ns, so SSD is ~1000x slower than RAM. This is why caching (Redis in RAM) is so valuable — serving cached data vs hitting SSD/disk is a 1000x latency difference.","tags":["capacity","latency","numbers"]},
        {"id":"qps-q4","type":"mcq","prompt":"A photo sharing app has 100M DAU. 10% upload 1 photo/day at 200KB each. How much daily storage is needed?",
         "choices":["1 TB","2 TB","200 GB","20 TB"],
         "answerIndex":1,"explanation":"10% of 100M = 10M uploads/day. 10M * 200KB = 2,000,000,000 KB = 2,000,000 MB = 2,000 GB = 2 TB/day. After 1 year: 730 TB ≈ 1 PB. Need object storage (S3) at this scale.","tags":["capacity","storage","estimation"]},
        {"id":"qps-q5","type":"mcq","prompt":"A single PostgreSQL master handles approximately how many write transactions per second?",
         "choices":["10-100 TPS","100-500 TPS","1,000-10,000 TPS for simple writes on good hardware",
                    "1,000,000 TPS"],
         "answerIndex":2,"explanation":"PostgreSQL simple writes (INSERT/UPDATE with index): 1,000-10,000 TPS on a well-tuned server with SSD. Complex transactions (joins, cascades) much lower. Beyond 10K TPS single-master: need read replicas (for reads), write sharding, or a NoSQL database.","tags":["capacity","postgresql","database"]},
        {"id":"qps-q6","type":"mcq","prompt":"What is the approximate maximum QPS for a Redis instance on a 16-core server?",
         "choices":["1,000 QPS","10,000 QPS","100,000-1,000,000 QPS for simple GET/SET",
                    "5 million QPS for all operations"],
         "answerIndex":2,"explanation":"Redis single instance: 100K-1M simple GET/SET operations per second. This is why Redis is used as a cache in front of databases — it handles orders of magnitude more traffic than a relational DB. Complex operations (ZADD, LRANGE) lower but still 50K-200K.","tags":["capacity","redis","throughput"]},
        {"id":"qps-q7","type":"mcq","prompt":"You need 500,000 read QPS. PostgreSQL read replicas handle ~30,000 QPS each. How many replicas minimum?",
         "choices":["5 replicas","17 replicas (500,000 / 30,000 = 16.7, round up)",
                    "500 replicas","1 replica is enough"],
         "answerIndex":1,"explanation":"500,000 / 30,000 = 16.7 -> 17 replicas needed just reading from SQL. In practice, add Redis caching first! 99% cache hit rate -> DB only handles 1% = 5,000 QPS -> 1 master handles that. Cache before scaling replicas.","tags":["capacity","replicas","scaling"]},
        {"id":"qps-q8","type":"mcq","prompt":"How many bytes in a Gigabyte (in decimal/SI units used by storage providers)?",
         "choices":["1024 * 1024 * 1024 = 1,073,741,824","1,000 * 1,000 * 1,000 = 1,000,000,000",
                    "1,024,000,000","500,000,000"],
         "answerIndex":1,"explanation":"Storage uses decimal: 1 GB = 10^9 bytes = 1,000,000,000 bytes. OS uses binary: 1 GiB = 2^30 = 1,073,741,824. For back-of-envelope: use 1 billion to keep math simple. The difference (~7%) doesn't matter for rough estimates.","tags":["capacity","storage","units"]},
        {"id":"qps-q9","type":"mcq","prompt":"What does the '99th percentile latency' (p99) mean?",
         "choices":["Average response time","99% of requests complete within this time — 1% take longer. Better metric than average because it captures outliers that small % of users experience",
                    "Maximum response time","Median response time"],
         "answerIndex":1,"explanation":"p99 = 99th percentile. If p99 = 500ms: 99% of requests finish in < 500ms, 1% take 500ms+. Average can look good (10ms) while p99 is terrible (5 seconds). Always monitor p99 and p999 for user-facing services.","tags":["capacity","latency","percentiles"]},
        {"id":"qps-q10","type":"mcq","prompt":"A new service will handle 1,000 requests/second at peak. Assuming each request takes 100ms of CPU time, how many CPU cores are minimally needed?",
         "choices":["1 core","100 cores (1000 req/s * 100ms = 100 concurrent requests needing CPU)",
                    "10 cores","1000 cores"],
         "answerIndex":1,"explanation":"Concurrency = RPS * average_duration = 1000 * 0.1s = 100 concurrent in-flight requests. Each needs approximately 1 CPU core's worth of work simultaneously. Add 50% safety margin: 150 cores -> 10 x 16-core servers. This is Little's Law: N = λ * W.","tags":["capacity","cpu","littles-law"]},
        {"id":"qps-q11","type":"mcq","prompt":"What is the latency difference between a network request in the same datacenter vs cross-continent?",
         "choices":["They are the same","Same datacenter: ~1ms. Cross-continent (US to Europe): ~100-150ms. 100x difference.",
                    "Same datacenter is 10x slower","5ms vs 6ms"],
         "answerIndex":1,"explanation":"Speed of light limits cross-continental latency. US to Europe: ~70ms one-way, ~140ms round trip. Same datacenter: 0.5-1ms. This is why multi-region deployment and CDNs matter — serving from nearby reduces perceived latency by 100x.","tags":["capacity","latency","network"]},
        {"id":"qps-q12","type":"mcq","prompt":"You need to store 5 years of logs at 10GB/day. What is the total storage needed?",
         "choices":["500 GB","18,250 GB = 18.25 TB (10GB * 365 * 5)",
                    "5 TB","100 TB"],
         "answerIndex":1,"explanation":"10 GB/day * 365 days/year * 5 years = 18,250 GB = 18.25 TB. For logs, consider: compression (10:1 ratio common for text logs = 1.8 TB actual), tiered storage (hot first 30 days on SSD, cold rest on S3 Glacier at 10x cheaper).","tags":["capacity","storage","logs"]},
        {"id":"qps-q13","type":"mcq","prompt":"What is Little's Law and how does it apply to server capacity?",
         "choices":["A networking protocol","N = λ × W: concurrent users = arrival rate × average time in system. If 1000 requests/second each take 200ms, need 1000 * 0.2 = 200 concurrent request slots",
                    "A caching algorithm","The law that memory doubles every 2 years"],
         "answerIndex":1,"explanation":"Little's Law: N (items in system) = λ (arrival rate) * W (time in system). 1000 req/s * 200ms = 200 concurrent connections needed. Exceed 200 -> queuing builds up -> latency spirals. Size connection pools, thread pools, and server counts from this.","tags":["capacity","littles-law","concurrency"]},
        {"id":"qps-q14","type":"mcq","prompt":"How much does Redis caching typically reduce database load?",
         "choices":["10-20%","50%","90-99% if cache hit rate is high — 99% cache hit means only 1% of requests hit the database",
                    "Caching doesn't reduce DB load"],
         "answerIndex":2,"explanation":"With 99% cache hit rate: 10,000 QPS to your app -> only 100 QPS reach the database. That's a 100x reduction. Even 95% hit rate: 10,000 -> 500 to DB. Caching is the single highest-leverage scaling technique before horizontal scaling.","tags":["capacity","caching","redis"]},
        {"id":"qps-q15","type":"mcq","prompt":"What is the formula to convert daily operations to QPS?",
         "choices":["daily_ops / 1000","daily_ops / 3600","daily_ops / 86,400 (seconds in a day)",
                    "daily_ops * 24"],
         "answerIndex":2,"explanation":"86,400 = 60 seconds * 60 minutes * 24 hours = seconds in a day. For rough math: round to 100,000. 1M operations/day = 1M/86400 = 11.6 QPS ≈ 12 QPS. 1B operations/day = 11,574 QPS ≈ 12,000 QPS.","tags":["qps","formula","calculation"]},
        {"id":"qps-q16","type":"mcq","prompt":"A web server handles 2,000 RPS with 50ms average response time. What is the minimum number of concurrent connections the server must support?",
         "choices":["2,000","100 (2000 * 0.05)","50,000","40 connections"],
         "answerIndex":1,"explanation":"Little's Law: N = λ * W = 2000 req/s * 0.05s = 100 concurrent connections. Configure thread pool or connection pool to at least 100. Add safety margin (150-200). Most web servers default to 200-1000 threads — check this matches your Little's Law estimate.","tags":["capacity","concurrency","littles-law"]},
        {"id":"qps-q17","type":"mcq","prompt":"What is the SSD vs HDD IOPS difference for random reads?",
         "choices":["Same performance","SSD: ~100,000 IOPS. HDD: ~100 IOPS. SSDs are ~1000x faster for random I/O.",
                    "HDD is faster due to larger cache","500x difference"],
         "answerIndex":1,"explanation":"HDD mechanical arm must physically seek to read location: ~10ms per seek, ~100 IOPS. SSD has no moving parts: ~0.1ms = 100,000 IOPS. For database random reads (index lookups), SSD is 1000x faster. Always use SSD for production databases.","tags":["capacity","ssd","hdd","iops"]},
        {"id":"qps-q18","type":"mcq","prompt":"You're designing a system for 50M DAU. What order should you address scaling bottlenecks?",
         "choices":["Start with sharding immediately","Optimise queries -> add caching -> add read replicas -> vertical scaling -> shard. Caching and indexes resolve 90% of issues before horizontal scale is needed.",
                    "Add more servers randomly","Use NoSQL for everything"],
         "answerIndex":1,"explanation":"Scaling order: 1) Fix missing indexes (10-100x speedup for free). 2) Add Redis cache (90-99% load reduction). 3) Read replicas (3-5x read capacity). 4) Vertical scale (bigger machine). 5) Partition. 6) Shard. Most apps stop at step 2 or 3.","tags":["capacity","scaling","order"]},
        {"id":"qps-q19","type":"mcq","prompt":"An app will store user-generated text posts. Estimated 100M posts/day at 500 bytes each. Storage after 10 years?",
         "choices":["500 GB","183 TB (100M * 500B = 50GB/day * 365 * 10 = 182,500 GB)",
                    "50 TB","5 PB"],
         "answerIndex":1,"explanation":"100M posts * 500 bytes = 50GB/day. Per year: 50GB * 365 = 18.25 TB. 10 years: 182.5 TB. This fits comfortably in a few PostgreSQL instances with sharding, or in DynamoDB. Not as extreme as media storage — text is very compact.","tags":["capacity","storage","estimation"]},
        {"id":"qps-q20","type":"mcq","prompt":"What is the approximate network bandwidth of a 1 Gbps connection?",
         "choices":["1 GB/s","125 MB/s (1 Gbps / 8 bits per byte = 125 MB/s)",
                    "1000 MB/s","10 MB/s"],
         "answerIndex":1,"explanation":"1 Gbps = 1 billion bits per second / 8 bits per byte = 125 MB/s. A 10 Gbps server interface: 1,250 MB/s = 1.25 GB/s. Data centre servers often have 25-100 Gbps. Useful for bandwidth calculations: how long to transfer 1TB? 1TB / 125 MB/s = 8,000 seconds ≈ 2.2 hours.","tags":["capacity","bandwidth","network"]},
    ]

    QPS_FC = [
        {"id":"qps-fc1","front":"QPS formula","back":"Average QPS = (DAU × actions_per_day) / 86,400. Peak QPS = average × 2-10x (use 3x for social apps). Bandwidth = QPS × average_payload_size. Daily storage = uploads/day × file_size.","tags":["qps","formula"]},
        {"id":"qps-fc2","front":"Latency cheatsheet (number to remember)","back":"L1 cache: 1ns. RAM: 100ns. SSD random: 100µs (1000x RAM). DB indexed query: 1ms. Same DC round trip: 1ms. DB full scan: 10-100ms. US-EU: 150ms. Remember: each level is ~10-1000x the previous.","tags":["latency","numbers"]},
        {"id":"qps-fc3","front":"Single server capacity limits","back":"Web server: 1-5K RPS (200-1K with DB queries). PostgreSQL master: 1-10K writes/sec, 10-50K simple reads. Redis: 100K-1M GET/SET. For higher: add replicas (reads) or shard (writes). Cache first.","tags":["capacity","server-limits"]},
        {"id":"qps-fc4","front":"Little's Law","back":"N = λ × W. Concurrent connections = arrival_rate × avg_response_time. 1000 req/s × 200ms = 200 concurrent. Size thread pools, DB connections, and server count from this formula. Add safety margin (1.5-2x).","tags":["capacity","littles-law"]},
        {"id":"qps-fc5","front":"Storage units cheatsheet","back":"KB=1000B, MB=1000KB, GB=1000MB, TB=1000GB, PB=1000TB. Tweet=280B, Photo=200KB, Video 1min 1080p=100MB, 1B rows×1KB=1TB. For estimates use powers of 10 and round aggressively.","tags":["capacity","storage","units"]},
        {"id":"qps-fc6","front":"Scaling impact per technique","back":"Better indexes: 10-100x query speedup (free). Redis cache: 90-99% DB load reduction. Read replica: 3-5x read capacity. Vertical scale: 2-4x (diminishing returns). CDN: removes 70-95% of static traffic. Sharding: N* writes.","tags":["capacity","scaling-multipliers"]},
        {"id":"qps-fc7","front":"Bandwidth calculation","back":"1 Gbps = 125 MB/s. 10 Gbps = 1.25 GB/s. Video streaming: 5 Mbps per viewer × 100M concurrent = 500 Tbps. This is why CDNs exist. Transfer time: size / bandwidth. 1TB over 1Gbps = 8,000s ≈ 2.2 hours.","tags":["capacity","bandwidth"]},
        {"id":"qps-fc8","front":"Capacity planning interview framework","back":"1. Clarify (DAU? read-heavy? spike patterns?). 2. Estimate QPS (show formula). 3. Estimate storage (daily × years). 4. Derive architecture (exceeds single DB? needs cache? needs CDN?). 5. Identify bottleneck and address it.","tags":["capacity","interview"]},
    ]

    d['guide'] = QPS_GUIDE
    d['questions'] = QPS_Q
    d['flashcards'] = QPS_FC
    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"qps-capacity.json: guide={len(QPS_GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ─────────────────────────────────────────────────────────────────────────────
    #  EMBEDDED DATABASES
    # ─────────────────────────────────────────────────────────────────────────────
    p = BASE / 'embedded-databases.json'
    d = json.loads(p.read_text())

    EMBEDDED_GUIDE = """# Embedded Databases (SQLite & RocksDB)

    ## What Is an Embedded Database?

    A traditional database like PostgreSQL is a separate server process. Your app connects
    to it over a network socket, sends SQL, gets results. Two processes, network overhead,
    authentication, connection pooling.

    An **embedded database** runs INSIDE your application process. No server to start.
    No network connection. No authentication. Just a library you link against.
    Your app reads and writes through function calls — microseconds, not milliseconds.

    ```
    Traditional (Client-Server):         Embedded:
      App Process                           App Process
        |                                     +-- SQLite library
        | TCP socket                          |     +-- Reads/writes file
        v                                     |         directly
      Postgres Process                        v
        + data files on disk              data.db file on disk

      Overhead: network + IPC               Overhead: function call only
      Latency: 1-5ms                        Latency: <1µs (microseconds!)
      Setup: install + config server        Setup: include one .c file
    ```

    SQLite is the world's most deployed database — more instances than all other
    databases combined. Every Android phone, iPhone, macOS machine, Windows PC,
    web browser, and millions of embedded devices run SQLite.

    ---

    ## SQLite — The Reliable Workhorse

    SQLite is a full SQL database engine in a single C source file (about 200KB).

    ```
    WHAT SQLITE IS:
      Full SQL support (SELECT, INSERT, UPDATE, DELETE, JOIN, triggers, views)
      ACID transactions
      Single file database (or :memory: for in-memory)
      Zero configuration
      Cross-platform (same .db file works on Mac, Windows, Linux, iOS, Android)
      Thread-safe modes: serialised, multi-thread, single-thread

    WHAT SQLITE IS NOT:
      NOT designed for multiple concurrent writers (serialised writes)
      NOT for client-server deployments over a network
      NOT for large write-heavy multi-user systems

    SQLITE SWEET SPOTS:
      Mobile apps (iOS CoreData uses SQLite, Android Room uses SQLite)
      Desktop apps (Firefox profile, Chrome history, Slack's local cache)
      Embedded systems (IoT devices, routers)
      Testing (use :memory: for blazing fast test suites)
      Small to medium web apps (SQLite handles surprisingly high load for reads)
      Config/state files that need querying (replacing CSV/JSON with SQL power)
    ```

    ---

    ## SQLite in Practice

    ```python
    # Python SQLite (built into stdlib, no pip install needed)
    import sqlite3

    # Open database (creates file if not exists)
    conn = sqlite3.connect('myapp.db')

    # Or in-memory (for tests — much faster, no file I/O)
    conn = sqlite3.connect(':memory:')

    # Create table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL,
            email   TEXT UNIQUE NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert with parameterised query (prevents SQL injection)
    conn.execute(
        'INSERT INTO users (name, email) VALUES (?, ?)',
        ('Alice', 'alice@example.com')
    )
    conn.commit()  # Writes are only durable after commit

    # Query
    cursor = conn.execute('SELECT * FROM users WHERE email = ?', ('alice@example.com',))
    row = cursor.fetchone()
    print(row)  # (1, 'Alice', 'alice@example.com', '2026-04-28...')

    # Context manager (auto-commit or auto-rollback)
    with conn:
        conn.execute('UPDATE users SET name = ? WHERE id = ?', ('Bob', 1))
        # Auto-commits on exit, auto-rollbacks on exception
    ```

    ---

    ## SQLite WAL Mode — The Performance Unlock

    ```
    DEFAULT JOURNAL MODE (DELETE):
      Write: acquire EXCLUSIVE lock on entire database file
      All readers BLOCKED during write
      Write-heavy workloads: readers starve

    WAL (Write-Ahead Log) MODE:
      Writers write to a separate WAL file
      Readers read from the main database file concurrently
      Readers never block writers, writers never block readers
      Multiple concurrent READERS + 1 concurrent WRITER

    Enable:
      PRAGMA journal_mode=WAL;  -- run once after opening connection

    Performance impact:
      Read throughput: 5-10x improvement for read-heavy workloads
      Write throughput: similar or slightly better
      Recovery: slightly more complex (WAL file must be checkpointed)

    Always enable WAL mode for any SQLite app with concurrent access.
    ```

    ---

    ## SQLite Limitations and When NOT to Use It

    ```
    WRITE CONCURRENCY:
      SQLite serialises writes — only ONE write at a time, even across threads.
      If your app has high concurrent writes (>100/sec from multiple threads):
      contention, lock timeouts, performance degrades.

    FILE LOCKING:
      SQLite uses OS file locks. Network filesystems (NFS, CIFS) often have
      buggy locking — corruption risk. Never put SQLite on NFS.

    MULTI-PROCESS WRITES:
      Multiple processes writing the same SQLite file = serialised through file lock.
      Works but slow for high-concurrency. Better: one process owns the DB.

    DATABASE SIZE:
      SQLite handles up to 281 TB theoretically. Practical: works well up to
      a few GB. Beyond 100GB: consider PostgreSQL.

    NO CLIENT-SERVER:
      Can't do: my app on Server A talks to SQLite on Server B.
      SQLite requires the app to run on the same machine as the file.
      If you need network access: use PostgreSQL.
    ```

    ---

    ## RocksDB — The High-Performance Key-Value Store

    RocksDB was developed at Facebook as a high-performance embedded key-value store.
    It is an evolution of Google's LevelDB, optimised for SSDs and large datasets.

    ```
    KEY DIFFERENCE FROM SQLITE:
      SQLite: SQL queries, joins, tables, relational model
      RocksDB: pure key-value store (get/put/delete by key)
               No SQL, no joins, no tables
               Just: store bytes by key, retrieve bytes by key

    WHAT ROCKSDB EXCELS AT:
      Millions of writes per second (100-500K writes/sec on good SSD)
      Billions of key-value pairs (tested at Facebook with PBs of data)
      SSD-optimised (LSM tree structure minimises write amplification on SSD)
      Embedded (runs in same process as app, no network)

    WHO USES ROCKSDB:
      Facebook (MyRocks = MySQL + RocksDB storage engine)
      Apache Kafka (log segment indexing)
      CockroachDB (storage layer)
      TiKV (Rust key-value store, used by TiDB)
      LinkedIn, Uber, Airbnb
    ```

    ---

    ## LSM Tree — How RocksDB Stores Data

    ```
    LSM = Log-Structured Merge Tree

    WRITE PATH:
      1. New writes go to in-memory MemTable (fast RAM writes)
      2. When MemTable full, flushed to disk as immutable SSTable (Sorted String Table)
      3. SSTables are periodically compacted (merged and re-sorted)

      App writes ----> MemTable (RAM)
                          |  (when full)
                          v
                      L0 SSTables (disk, may overlap)
                          |  (compaction)
                          v
                      L1 SSTables (disk, non-overlapping, sorted)
                          |  (compaction)
                          v
                      L2, L3... SSTables (larger, less frequent)

    WHY LSM BEATS B-TREE FOR SSD WRITES:
      B-tree (used by PostgreSQL, MySQL): random WRITE to specific page on disk
        → SSDs handle random writes poorly (slow, wears flash cells)
      LSM: always append to sequential log + background compaction
        → Sequential writes only → SSD-friendly → very fast writes

    READ PATH:
      1. Check MemTable
      2. Check L0 SSTables (bloom filter helps)
      3. Check L1, L2... by key range
      * Bloom filter: probabilistic structure, quickly checks "key probably not here"
    ```

    ---

    ## SQLite vs RocksDB vs PostgreSQL — Choosing

    ```
    +------------------+-----------+-----------+---------------+
    | Factor           | SQLite    | RocksDB   | PostgreSQL    |
    +------------------+-----------+-----------+---------------+
    | SQL queries      | Full SQL  | None      | Full SQL      |
    | Write speed      | 100K/s    | 500K/s    | 10-50K TPS    |
    | Concurrency      | Low       | High      | High          |
    | Network access   | No        | No        | Yes           |
    | Setup complexity | Minimal   | Medium    | High          |
    | Use case         | Apps,     | Storage   | Production    |
    |                  | testing,  | engines,  | backends,     |
    |                  | mobile    | databases | services      |
    +------------------+-----------+-----------+---------------+

    CHOOSE SQLITE WHEN:
      Mobile app local storage
      Desktop app state
      Test databases (speed + isolation)
      Single-user apps
      Config / history / local cache

    CHOOSE ROCKSDB WHEN:
      Building a database or storage system
      Need extreme write throughput
      Key-value access pattern (no complex queries)
      Large datasets on SSD

    CHOOSE POSTGRESQL WHEN:
      Multi-user application
      Network access from multiple services
      Complex queries / joins
      Production web backend
    ```

    ---

    ## Mind Map

    ```
    EMBEDDED DATABASES
    |
    +-- SQLITE
    |   +-- Full SQL in single file
    |   +-- Zero config, self-contained
    |   +-- ACID transactions
    |   +-- WAL mode (concurrent reads + 1 writer)
    |   +-- Use: mobile, desktop, testing, single-user
    |   +-- Limit: no concurrent writers, no network
    |
    +-- ROCKSDB
    |   +-- Key-value only (no SQL)
    |   +-- LSM tree (write-optimised for SSD)
    |   +-- 100-500K writes/sec
    |   +-- Used as storage engine in other databases
    |   +-- Use: building databases, extreme write throughput
    |
    +-- WHEN TO USE
        +-- SQLite: app = one machine, needs SQL, low concurrency
        +-- RocksDB: building a DB layer, need raw write speed
        +-- PostgreSQL: multi-machine, multi-user, production
    ```

    ---

    ## References and Further Learning

    ### Videos (Watch These!)
    - **SQLite Is Not a Toy Database** by Ben Johnson (SQLite consultant):
      https://www.youtube.com/watch?v=LHMrNvm88XQe
      - SQLite performance, WAL mode, real production use cases.
    - **RocksDB Internals** by Facebook Engineering:
      https://www.youtube.com/watch?v=jGCv4r8CJEI
      - LSM tree, compaction, Facebook's use of RocksDB at scale.

    ### Free Books and Articles
    - **SQLite documentation**: https://sqlite.org/docs.html
    - **Also SQLite** (SQLite for production article): https://fly.io/blog/all-in-on-sqlite-litestream/
    - **RocksDB Wiki**: https://github.com/facebook/rocksdb/wiki

    ### Practice
    - **SQLite Browser** (GUI tool): https://sqlitebrowser.org/
      - Visual tool to create and browse SQLite databases.
    - Use SQLite for your test database in any project — faster and simpler than Docker + Postgres.
    """

    EMBEDDED_Q = [
        {"id":"embd-q1","type":"mcq","prompt":"What is an embedded database?",
         "choices":["A database installed in a container","A database that runs as a library INSIDE the application process — no separate server, no network connection, direct file access",
                    "A database optimised for small data","A read-only database"],
         "answerIndex":1,"explanation":"Embedded database = library linked into app. SQLite, RocksDB, LevelDB. Operates on local files directly. No TCP socket, no auth, no server setup. Latency: microseconds (vs milliseconds for network DB). Perfect for local storage.","tags":["embedded-database","basics"]},
        {"id":"embd-q2","type":"mcq","prompt":"SQLite is the world's most deployed database. Where does it run?",
         "choices":["Only on Linux servers","In every Android phone, iPhone, macOS machine, browser (Firefox/Chrome history), Windows apps — more instances than all other DBs combined",
                    "Only in Docker containers","Only in enterprise software"],
         "answerIndex":1,"explanation":"SQLite runs everywhere: iOS CoreData layer uses SQLite, Android Room uses SQLite, Chrome stores history in SQLite, Firefox profile is SQLite, every macOS/Windows app that stores settings often uses it. It is ubiquitous precisely because it requires zero infrastructure.","tags":["sqlite","deployment"]},
        {"id":"embd-q3","type":"mcq","prompt":"What is WAL mode in SQLite and why should you enable it?",
         "choices":["Write Append Log — makes all writes faster","Write-Ahead Log — allows concurrent readers while one writer writes, instead of blocking all readers during writes. 5-10x read throughput improvement.",
                    "A backup mechanism","A compression format"],
         "answerIndex":1,"explanation":"Default SQLite: write acquires EXCLUSIVE lock, all readers block. WAL: writer appends to WAL file, readers read main DB file concurrently. No contention. Enable: PRAGMA journal_mode=WAL. Always enable for apps with any concurrent reads and writes.","tags":["sqlite","wal","concurrency"]},
        {"id":"embd-q4","type":"mcq","prompt":"What is RocksDB and who developed it?",
         "choices":["A SQL database by Oracle","A high-performance embedded key-value store developed at Facebook, based on Google's LevelDB — optimised for SSD write throughput",
                    "An open-source alternative to SQLite","A distributed NoSQL database"],
         "answerIndex":1,"explanation":"RocksDB was created at Facebook (2012) to solve write-heavy workloads that LevelDB couldn't handle. Key features: LSM tree, SSD-optimised, 100-500K writes/sec, used as storage engine in MyRocks (MySQL), TiKV, CockroachDB.","tags":["rocksdb","key-value"]},
        {"id":"embd-q5","type":"mcq","prompt":"What data model does RocksDB use?",
         "choices":["Relational tables","Document store","Pure key-value: get(key)->bytes, put(key, bytes), delete(key). No SQL, no joins, no tables.",
                    "Graph database"],
         "answerIndex":2,"explanation":"RocksDB is a key-value store. Keys and values are raw bytes. No schema, no SQL, no queries — just: store bytes by key, retrieve bytes by key. You are responsible for serialising your data (Protocol Buffers, JSON, custom binary). No query language.","tags":["rocksdb","key-value","data-model"]},
        {"id":"embd-q6","type":"mcq","prompt":"What is an LSM (Log-Structured Merge) tree?",
         "choices":["A balanced binary search tree on disk","A write-optimised data structure used by RocksDB/Cassandra: writes go to in-memory MemTable, flushed to disk as sequential SSTables, periodically compacted",
                    "A tree used for database indexes","A network routing algorithm"],
         "answerIndex":1,"explanation":"LSM: writes always go to MemTable (RAM), flushed as sequential SSTable files on disk. Sequential writes are SSD-friendly (no random I/O). Background compaction merges SSTables. Result: extremely fast writes, slower reads than B-trees (must check multiple levels).","tags":["rocksdb","lsm-tree","storage"]},
        {"id":"embd-q7","type":"mcq","prompt":"When should you NOT use SQLite?",
         "choices":["For mobile apps","When you need multiple concurrent writers, network access from multiple services, or when the app runs on a different machine than the data",
                    "For test databases","For small single-user apps"],
         "answerIndex":1,"explanation":"SQLite limitations: one writer at a time (serialised), no network access (must be on same machine as file), no NFS (file locking bugs cause corruption). For: multi-user web backend, microservices sharing a DB, high-concurrent writes -> use PostgreSQL.","tags":["sqlite","limitations","when-not-to-use"]},
        {"id":"embd-q8","type":"mcq","prompt":"What advantage does SQLite `:memory:` provide for testing?",
         "choices":["Same performance as file-based","In-memory SQLite creates a fresh database per test with no file I/O — tests run 10-100x faster, completely isolated, no cleanup needed",
                    "Persistent across test runs","Allows multiple concurrent writers"],
         "answerIndex":1,"explanation":"sqlite3.connect(':memory:') creates a database in RAM. No file created. Destroyed when connection closes. Each test gets a fresh database. No inter-test contamination. Much faster than file I/O. Ideal for unit tests that need a real database without Docker.","tags":["sqlite","testing","in-memory"]},
        {"id":"embd-q9","type":"mcq","prompt":"Why is LSM tree better than B-tree for SSD write performance?",
         "choices":["LSM trees use less memory","B-tree writes: random I/O to specific disk pages (slow on SSD, wears flash cells). LSM: always sequential append + background compaction = SSD-friendly, 10-100x higher write throughput.",
                    "B-trees don't work on SSDs","LSM uses better compression"],
         "answerIndex":1,"explanation":"B-tree: update in-place -> random writes scattered across disk -> SSD write amplification (must erase entire block to update one byte). LSM: always appends sequentially -> minimal write amplification -> SSDs love sequential writes. RocksDB does 500K writes/sec vs PostgreSQL's 10K.","tags":["rocksdb","lsm-tree","ssd"]},
        {"id":"embd-q10","type":"mcq","prompt":"SQLite is ACID compliant. What does this mean?",
         "choices":["It uses the same engine as MySQL","Atomicity (transaction fully completes or rolls back), Consistency (constraints maintained), Isolation (transactions don't interfere), Durability (committed data survives crash)",
                    "It only supports read transactions","ACID is a marketing term with no technical meaning"],
         "answerIndex":1,"explanation":"SQLite is fully ACID. A transaction that writes 5 rows: if app crashes before COMMIT, changes are rolled back when you reopen the DB. Durability: after COMMIT, data is safely on disk. Isolation: SQLite serialises writes ensuring no dirty reads.","tags":["sqlite","acid","transactions"]},
        {"id":"embd-q11","type":"mcq","prompt":"What is a Bloom filter in RocksDB used for?",
         "choices":["Encrypting data","Compressing SSTables","A probabilistic data structure that quickly answers 'this key is definitely NOT in this SSTable' — avoids unnecessary disk reads during key lookup",
                    "Sorting keys in MemTable"],
         "answerIndex":2,"explanation":"RocksDB read path must check multiple SSTable levels. Without Bloom filter: open every SSTable and binary search. With Bloom filter: 'is key in this SSTable?' -> if Bloom says NO, skip the file entirely (no disk read). False positive rate ~1% by default. Huge read performance improvement.","tags":["rocksdb","bloom-filter","performance"]},
        {"id":"embd-q12","type":"mcq","prompt":"Can you use SQLite on a network file system (NFS)?",
         "choices":["Yes, it works perfectly","No — NFS file locking is often buggy, which can cause SQLite database corruption. Always run SQLite on local storage only.",
                    "Only in read-only mode","Only with WAL disabled"],
         "answerIndex":1,"explanation":"SQLite uses OS-level file locks for concurrency control. NFS (and CIFS/SMB) often implement file locking incorrectly or unreliably. Result: two processes think they have exclusive access simultaneously -> database corruption. SQLite docs explicitly warn: do not use on NFS.","tags":["sqlite","nfs","limitations"]},
        {"id":"embd-q13","type":"mcq","prompt":"Which production databases use RocksDB as their storage engine?",
         "choices":["PostgreSQL, MySQL","MyRocks (Facebook's MySQL), TiKV (used by TiDB), CockroachDB storage layer",
                    "Redis, Memcached","MongoDB, Cassandra"],
         "answerIndex":1,"explanation":"RocksDB is used as the storage engine by: MyRocks (Facebook's MySQL variant with 10x better write throughput), TiKV (Rust key-value store under TiDB), CockroachDB (replaces RocksDB with Pebble recently), StreamNative Kafka. It's a building block for other databases.","tags":["rocksdb","production","databases"]},
        {"id":"embd-q14","type":"mcq","prompt":"What is SQLite's maximum database file size?",
         "choices":["100MB","2GB","281 TB theoretically (practical limit: works well up to few GB, usable up to ~100GB)",
                    "1TB hard limit"],
         "answerIndex":2,"explanation":"SQLite's theoretical max is 281 TB. Practically: works great up to a few GB, usable up to ~100GB with some performance considerations. Beyond 100GB: PostgreSQL is better. The 2GB limit is an old myth from early SQLite versions.","tags":["sqlite","limits","file-size"]},
        {"id":"embd-q15","type":"mcq","prompt":"What parameterised query syntax prevents SQL injection in Python SQLite?",
         "choices":["String concatenation: f'WHERE id = {user_id}'","Parameterised: cursor.execute('WHERE id = ?', (user_id,)) — driver escapes the value safely",
                    "PRAGMA safe_mode = ON","There is no SQL injection risk in SQLite"],
         "answerIndex":1,"explanation":"SQLite (and all SQL databases): never format user input into SQL strings. Use parameterised queries: execute('SELECT * FROM users WHERE id = ?', (user_id,)). The ? placeholder is safely escaped by the driver. Prevents SQL injection regardless of what the user input contains.","tags":["sqlite","security","sql-injection"]},
        {"id":"embd-q16","type":"mcq","prompt":"What does SQLite's AUTOINCREMENT keyword do and when should you avoid it?",
         "choices":["Creates a random UUID","Guarantees monotonically increasing integers that are never reused — slightly slower than INTEGER PRIMARY KEY alone (which reuses deleted IDs)",
                    "Required for all primary keys","Creates a sequence object like PostgreSQL"],
         "answerIndex":1,"explanation":"INTEGER PRIMARY KEY: SQLite auto-increments and may REUSE deleted IDs. AUTOINCREMENT: never reuses IDs but requires checking a separate table (slower, bigger DB). Use AUTOINCREMENT only if you genuinely cannot reuse IDs. For most apps, INTEGER PRIMARY KEY is fine.","tags":["sqlite","primary-key","autoincrement"]},
        {"id":"embd-q17","type":"mcq","prompt":"What is RocksDB compaction and why is it necessary?",
         "choices":["Compression of keys","Background process that merges SSTables (removing deleted keys, merging sorted files) — prevents read amplification from too many overlapping SSTables accumulating",
                    "Network data compression","Archiving old data"],
         "answerIndex":1,"explanation":"Without compaction: many small SSTables accumulate at L0. Reading a key requires checking all of them. With compaction: SSTables merged, deleted/overwritten keys removed, sorted. Fewer files, faster reads, less storage. Trade-off: compaction uses CPU and I/O — tune for your workload.","tags":["rocksdb","compaction","lsm-tree"]},
        {"id":"embd-q18","type":"mcq","prompt":"Which use case is ideal for SQLite in a web application?",
         "choices":["High-traffic API with 10,000 concurrent users","Read-heavy single-server personal application, developer tool, or application with SQLite as local cache with Litestream for replication",
                    "Distributed microservices","Multi-region global app"],
         "answerIndex":1,"explanation":"Modern SQLite use: personal web apps or small SaaS on a single server with WAL mode and Litestream (streaming replication to S3). Many successful small web apps run entirely on SQLite. The constraint is: single machine. Fly.io and others offer SQLite-first hosting.","tags":["sqlite","web","use-case"]},
        {"id":"embd-q19","type":"mcq","prompt":"What is LevelDB and how does it relate to RocksDB?",
         "choices":["LevelDB is newer than RocksDB","LevelDB is Google's embedded key-value store (2011). RocksDB (Facebook, 2012) is a fork of LevelDB optimised for production SSD workloads at scale.",
                    "They are identical","LevelDB uses B-tree, RocksDB uses LSM"],
         "answerIndex":1,"explanation":"LevelDB: Google's LSM-based embedded KV store, used in Chrome (IndexedDB). RocksDB: Facebook's fork with additions: column families, compaction strategies optimised for large SSDs, better read/write performance at scale. RocksDB has largely superseded LevelDB for production use.","tags":["rocksdb","leveldb","history"]},
        {"id":"embd-q20","type":"mcq","prompt":"What does it mean for SQLite to be 'serverless'?",
         "choices":["It runs on AWS Lambda","There is no separate database server process to install, configure, or maintain — the database engine is a library linked directly into your application",
                    "It uses serverless pricing","It runs in a browser"],
         "answerIndex":1,"explanation":"SQLite 'serverless' = no server process. Contrast: PostgreSQL requires installing and running a postgres daemon. SQLite: include sqlite3.h, link the library, call sqlite3_open(). Zero admin: no config files, no users, no port, no service to start. 'Serverless' in the literal sense, before AWS Lambda popularised the term.","tags":["sqlite","serverless","architecture"]},
    ]

    EMBEDDED_FC = [
        {"id":"embd-fc1","front":"SQLite sweet spots","back":"Mobile apps (Android/iOS), desktop apps (settings/history), test databases (:memory: = instant), single-user/single-process web apps, config/state that needs SQL queries, IoT devices. Not for: multi-user, network access, high concurrent writes.","tags":["sqlite","use-cases"]},
        {"id":"embd-fc2","front":"SQLite WAL mode — always enable","back":"PRAGMA journal_mode=WAL. Default mode: write blocks all readers. WAL mode: readers and writers coexist (multiple concurrent readers + 1 writer). 5-10x read throughput improvement. Run once when first opening DB.","tags":["sqlite","wal"]},
        {"id":"embd-fc3","front":"RocksDB LSM write path","back":"Write -> MemTable (RAM). MemTable full -> flush as SSTable (immutable, sorted, sequential disk write). Background compaction merges SSTables (removes deletes, sorts). Result: always sequential disk writes = SSD-optimised, 500K+ writes/sec.","tags":["rocksdb","lsm-tree"]},
        {"id":"embd-fc4","front":"SQLite vs RocksDB vs PostgreSQL","back":"SQLite: full SQL, single-file, zero-config, low concurrency, local only. RocksDB: key-value only, extreme write throughput, builds other DBs. PostgreSQL: full SQL, client-server, network, high concurrency. Choose by use case not preference.","tags":["sqlite","rocksdb","postgresql"]},
        {"id":"embd-fc5","front":"SQLite parameterised queries rule","back":"NEVER: f'SELECT * FROM users WHERE id = {user_id}'. ALWAYS: execute('SELECT * FROM users WHERE id = ?', (user_id,)). Parameterised = safe from SQL injection for any input. ALL SQLite queries touching user data must be parameterised.","tags":["sqlite","security","sql-injection"]},
        {"id":"embd-fc6","front":"RocksDB Bloom filter purpose","back":"Probabilistic structure per SSTable: 'is this key in this file?' If answer NO -> skip the file (no disk read). ~1% false positive rate. Without Bloom filter: read a key -> check every SSTable level on disk. With: skip most files. Huge read speed improvement.","tags":["rocksdb","bloom-filter"]},
        {"id":"embd-fc7","front":"SQLite :memory: in tests","back":"conn = sqlite3.connect(':memory:'). Creates fresh in-memory DB per test. No file I/O = 10-100x faster. Destroyed when connection closes = no cleanup. Each test fully isolated. Use for any unit test that needs a real relational DB without Docker overhead.","tags":["sqlite","testing"]},
        {"id":"embd-fc8","front":"SQLite NFS danger","back":"NEVER put SQLite database file on NFS, CIFS, or any network filesystem. NFS file locking is unreliable -> two processes get simultaneous exclusive lock -> database corruption. Always use local disk (ext4, APFS, NTFS). Real bug, not theoretical risk.","tags":["sqlite","nfs","corruption"]},
    ]

    d['guide'] = EMBEDDED_GUIDE
    d['questions'] = EMBEDDED_Q
    d['flashcards'] = EMBEDDED_FC
    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"embedded-databases.json: guide={len(EMBEDDED_GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ─────────────────────────────────────────────────────────────────────────────
    #  RELATIONAL DATABASES
    # ─────────────────────────────────────────────────────────────────────────────
    p = BASE / 'relational-databases.json'
    d = json.loads(p.read_text())

    RELATIONAL_GUIDE = """# Relational Databases & SQL

    ## What Is a Relational Database?

    A relational database organises data into **tables** (rows and columns), enforces
    relationships between tables, and uses SQL (Structured Query Language) to query it.

    **Why relational?** Because most real-world data IS relational:
    - A user HAS MANY orders
    - An order HAS MANY line items
    - A line item BELONGS TO a product

    The "relational" part means these connections are formal, enforced, and queryable.

    ```
    users table:            orders table:         products table:
    +----+-------+          +----+---------+      +----+---------+-------+
    | id | name  |          | id | user_id |      | id | name    | price |
    +----+-------+          +----+---------+      +----+---------+-------+
    |  1 | Alice |          |  1 |       1 |      |  1 | Laptop  |  999  |
    |  2 | Bob   |          |  2 |       1 |      |  2 | Mouse   |   29  |
    +----+-------+          |  3 |       2 |      +----+---------+-------+
                            +----+---------+

    JOIN: "Show me Alice's orders with product names"
    SELECT users.name, products.name, products.price
    FROM users
    JOIN orders ON users.id = orders.user_id
    JOIN order_items ON orders.id = order_items.order_id
    JOIN products ON order_items.product_id = products.id
    WHERE users.name = 'Alice';
    ```

    ---

    ## ACID Properties — The Foundation of Reliability

    Every relational database guarantees ACID properties. These are why banks, payment
    systems, and any system where data integrity matters use relational databases.

    ```
    ATOMICITY:
      A transaction is ALL or NOTHING.
      Transfer $100 from Alice to Bob:
        UPDATE accounts SET balance = balance - 100 WHERE user_id = 1  (Alice)
        UPDATE accounts SET balance = balance + 100 WHERE user_id = 2  (Bob)
      If the second UPDATE fails (crash, error), the FIRST is also undone.
      You can never debit Alice without crediting Bob. Partial transactions don't exist.

    CONSISTENCY:
      The database always moves from one VALID state to another VALID state.
      Constraints (NOT NULL, UNIQUE, FOREIGN KEY, CHECK) are enforced.
      No transaction can leave the database in an invalid state.
      Constraint: balance >= 0. Withdrawing $200 from balance of $100 -> rejected.

    ISOLATION:
      Concurrent transactions don't interfere with each other.
      Transaction 1 and Transaction 2 running simultaneously see a consistent view.
      Isolation levels (READ COMMITTED, REPEATABLE READ, SERIALIZABLE) control this.
      Default in PostgreSQL: READ COMMITTED (reads see other committed transactions).

    DURABILITY:
      Once committed, data SURVIVES crashes.
      After COMMIT, even if the server loses power 1ms later, your data is safe.
      Achieved via: Write-Ahead Log (WAL) — changes written to log before the actual data file.
      On restart: replay WAL to recover any committed but not yet written data.
    ```

    ---

    ## SQL Fundamentals — The Language

    ```sql
    -- DDL (Data Definition Language) — structure
    CREATE TABLE users (
        id         SERIAL PRIMARY KEY,          -- auto-increment integer
        email      TEXT NOT NULL UNIQUE,        -- NOT NULL + unique constraint
        name       TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        age        INT CHECK (age >= 0 AND age <= 150)  -- check constraint
    );

    CREATE INDEX idx_users_email ON users(email);  -- speeds up WHERE email = ...

    -- DML (Data Manipulation Language) — data
    INSERT INTO users (email, name) VALUES ('alice@example.com', 'Alice');

    UPDATE users SET name = 'Alice Smith' WHERE id = 1;

    DELETE FROM users WHERE id = 1;

    -- DQL (Data Query Language) — reads
    SELECT id, name FROM users WHERE age > 18 ORDER BY name LIMIT 10;

    -- Aggregation
    SELECT country, COUNT(*) AS user_count, AVG(age) AS avg_age
    FROM users
    GROUP BY country
    HAVING COUNT(*) > 1000  -- HAVING filters AFTER GROUP BY (vs WHERE which filters before)
    ORDER BY user_count DESC;

    -- JOIN types
    SELECT u.name, o.total
    FROM users u
    INNER JOIN orders o ON u.id = o.user_id;       -- only matching rows

    SELECT u.name, o.total
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id;        -- all users, NULL for no orders

    SELECT u.name, o.total
    FROM users u
    RIGHT JOIN orders o ON u.id = o.user_id;       -- all orders, NULL for no user

    -- Subquery
    SELECT name FROM users
    WHERE id IN (SELECT user_id FROM orders WHERE total > 1000);

    -- CTE (Common Table Expression — cleaner than subquery)
    WITH high_value_users AS (
        SELECT user_id FROM orders GROUP BY user_id HAVING SUM(total) > 10000
    )
    SELECT u.name FROM users u
    JOIN high_value_users h ON u.id = h.user_id;
    ```

    ---

    ## Indexes — Making Queries Fast

    ```
    Without index: SELECT * FROM users WHERE email = 'alice@example.com'
      Full table scan: reads every row, checks every email
      O(N) — slow on large tables

    With index on email: same query
      Index lookup: B-tree traversal to find the row
      O(log N) — fast regardless of table size

    INDEX TYPES:
      B-tree (default): balanced tree, good for =, <, >, BETWEEN, ORDER BY, LIKE 'prefix%'
      Hash:         exact equality only (=), faster than B-tree for pure lookup
      GIN:          for arrays, JSONB, full-text search (PostgreSQL)
      GiST:         for geometric data, range types
      Partial index: only index rows matching a condition (smaller, faster)
                     CREATE INDEX ON users(email) WHERE active = true;

    COMPOUND INDEX:
      CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);
      Good for: WHERE user_id = ? AND created_at > ?
      Index order matters: (user_id, created_at) cannot be used for WHERE created_at > ? alone
      Use the leftmost column(s) prefix rule.

    WHEN TO ADD AN INDEX:
      Slow query appears in EXPLAIN ANALYZE showing 'Seq Scan' on large table
      Column appears in WHERE, JOIN ON, ORDER BY, GROUP BY
      Column has high cardinality (many unique values)

    WHEN NOT TO ADD AN INDEX:
      Write-heavy tables (every write must update all indexes)
      Small tables (full scan faster than index for < 1000 rows)
      Low cardinality (boolean column: index not selective enough)
    ```

    ---

    ## Transactions and Isolation Levels

    ```
    Transaction:
    BEGIN;
      INSERT INTO orders (user_id, total) VALUES (1, 99.99);
      UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 42;
    COMMIT;  -- both succeed atomically
    -- or ROLLBACK; to undo both

    ISOLATION LEVELS (from weakest to strongest):

    READ UNCOMMITTED: can see other transactions' UNCOMMITTED changes (dirty read)
      Problem: dirty read (read data that gets rolled back = never existed)
      Almost never used

    READ COMMITTED (PostgreSQL default):
      Only sees COMMITTED data from other transactions
      Problem: non-repeatable read (read same row twice, different result if other txn committed between reads)

    REPEATABLE READ:
      Reads within same transaction see a snapshot of data as of transaction start
      Problem: phantom read (new rows inserted by other txn appear in range queries)

    SERIALIZABLE:
      Transactions appear to execute one after another (no concurrency anomalies)
      Most expensive: serialisation failures possible, must retry
      Use for: complex transactions that must be correct (financial operations)

    PostgreSQL default: READ COMMITTED
      Good enough for: most web application queries
      Use REPEATABLE READ or SERIALIZABLE for: multi-step financial transactions
    ```

    ---

    ## N+1 Query Problem — The Silent Performance Killer

    ```
    THE PROBLEM:
      Fetch 100 users + their orders:

      WRONG (N+1):
        users = db.query("SELECT * FROM users LIMIT 100")  -- 1 query
        for user in users:
            orders = db.query("SELECT * FROM orders WHERE user_id = ?", user.id)  -- 100 queries
        TOTAL: 101 queries! (1 + N where N=100)

      RIGHT (1 query with JOIN):
        db.query('SELECT u.*, o.* FROM users u LEFT JOIN orders o ON u.id = o.user_id LIMIT 100')  -- 1 query, same data

      OR (2 queries with IN clause):
        users = db.query("SELECT * FROM users LIMIT 100")  -- 1 query
        user_ids = [u.id for u in users]
        orders = db.query("SELECT * FROM orders WHERE user_id = ANY(?)", user_ids)  -- 1 query

      N+1 is the #1 ORM performance issue. ORMs like Hibernate, SQLAlchemy
      can generate N+1 if you don't use eager loading:
        Java Hibernate: @OneToMany fetch = EAGER or JOIN FETCH
        Python SQLAlchemy: joinedload() or selectinload()
    ```

    ---

    ## EXPLAIN ANALYZE — Reading Query Plans

    ```sql
    EXPLAIN ANALYZE
    SELECT * FROM orders WHERE user_id = 123 AND created_at > '2025-01-01';

    -- Example output:
    -- Bitmap Heap Scan on orders  (cost=93.45..5432.12 rows=1234 width=64)
    --   Recheck Cond: ((user_id = 123) AND (created_at > '2025-01-01'))
    --   -> Bitmap Index Scan on idx_orders_user_date  (cost=0.00..93.14 rows=1234)

    KEY THINGS TO LOOK FOR:
      Seq Scan: full table scan — usually bad on large tables, means missing index
      Index Scan: good — using an index
      Index Only Scan: best — only reads index, not actual table rows
      Nested Loop: joining two small tables, usually fine
      Hash Join: joining larger tables, generally good
      Merge Join: sorted data join, can be very efficient

    cost=START..TOTAL: planner's estimated cost (arbitrary units)
    rows=N: estimated row count
    actual time=X..Y ms: actual execution time (from ANALYZE)
    actual rows=N: actual rows returned
    ```

    ---

    ## Normalisation and Denormalisation

    ```
    NORMALISATION (reduce redundancy):
      Split data into related tables, no duplicated data.
      1NF: atomic values (no arrays in columns)
      2NF: non-key attributes depend on whole key
      3NF: no transitive dependencies

      Orders: order_id, user_id, product_id, quantity
      NOT: order_id, customer_name, customer_email, product_name, product_price
      (name/email/price duplicated in every order row)

      Benefits: no anomalies (update user email in ONE place, not every order row)
      Costs: more JOINs required for queries

    DENORMALISATION (intentional redundancy for performance):
      Store computed or related data together to avoid expensive JOINs.
      orders table: also store user_email, product_name (duplicated intentionally)
      Fast reads (no JOIN), fast for reporting.
      Trade-off: must keep denormalised copies in sync on write.

    WHEN TO DENORMALISE:
      Read-heavy reporting tables (data warehouse)
      Caching computed results that are expensive to recalculate
      NoSQL databases denormalise by default (document store puts everything together)
    ```

    ---

    ## PostgreSQL vs MySQL — Key Differences

    ```
    +------------------+------------------------+------------------------+
    | Feature          | PostgreSQL             | MySQL (InnoDB)         |
    +------------------+------------------------+------------------------+
    | ACID             | Full ACID              | Full ACID (InnoDB)     |
    | JSON support     | JSONB (indexed, fast)  | JSON (limited indexing)|
    | Full-text search | Built-in, powerful     | Basic                  |
    | Replication      | Streaming replication  | Binary log replication |
    | Extensions       | PostGIS, pg_vector, etc| Fewer                  |
    | Concurrency      | MVCC (excellent)       | MVCC (good)            |
    | Default auth     | Trust (local) / md5   | Password required      |
    | License          | PostgreSQL License     | GPL / Commercial       |
    | Cloud managed    | RDS, Aurora, Supabase  | RDS, Aurora            |
    +------------------+------------------------+------------------------+

    For new projects: PostgreSQL is generally recommended.
    MySQL is fine if your team knows it or you're using pre-existing MySQL infrastructure.
    ```

    ---

    ## Mind Map

    ```
    RELATIONAL DATABASES
    |
    +-- ACID
    |   +-- Atomicity (all or nothing)
    |   +-- Consistency (constraints enforced)
    |   +-- Isolation (concurrent transaction safety)
    |   +-- Durability (committed data survives crash)
    |
    +-- SQL
    |   +-- DDL (CREATE TABLE, INDEX, ALTER)
    |   +-- DML (INSERT, UPDATE, DELETE)
    |   +-- DQL (SELECT, JOIN, GROUP BY, HAVING)
    |   +-- Transactions (BEGIN/COMMIT/ROLLBACK)
    |
    +-- INDEXES
    |   +-- B-tree (default — =, <, >, BETWEEN)
    |   +-- Hash (equality only)
    |   +-- Compound (leftmost prefix rule)
    |   +-- Partial (WHERE condition)
    |   +-- EXPLAIN ANALYZE to verify
    |
    +-- PERFORMANCE
    |   +-- N+1 query (use JOIN or selectinload)
    |   +-- Missing indexes (Seq Scan in EXPLAIN)
    |   +-- Normalise for integrity, denormalise for speed
    |
    +-- ISOLATION LEVELS
        +-- Read Committed (default, most cases)
        +-- Repeatable Read
        +-- Serializable (financial, critical operations)
    ```

    ---

    ## References and Further Learning

    ### Videos (Watch These!)
    - **SQL Tutorial - Full Database Course for Beginners** by freeCodeCamp:
      https://www.youtube.com/watch?v=HXV3zeQKqGY
      - 4 hours. Complete beginner SQL course with PostgreSQL.
    - **Database Indexing Explained** by hussein nasser:
      https://www.youtube.com/watch?v=-qNSXK7s7_w
      - B-tree, hash, composite indexes with real query plan examples.

    ### Free Books and Articles
    - **PostgreSQL official tutorial**: https://www.postgresql.org/docs/current/tutorial.html
    - **Use The Index, Luke** (free book on SQL indexing): https://use-the-index-luke.com/
      - The best resource for understanding SQL indexes deeply.

    ### Practice
    - **SQLZoo** (interactive SQL): https://sqlzoo.net/
    - **pgexercises** (PostgreSQL exercises): https://pgexercises.com/
    - **Explain.dalibo.com** (visualise PostgreSQL EXPLAIN plans): https://explain.dalibo.com/
    """

    RELATIONAL_Q = [
        {"id":"rdb-q1","type":"mcq","prompt":"What does ACID stand for in database transactions?",
         "choices":["Automated, Concurrent, Integrated, Distributed","Atomicity, Consistency, Isolation, Durability — the four properties that guarantee reliable transaction processing",
                    "Asynchronous, Cached, Indexed, Distributed","Atomic, Consistent, Indexed, Durable"],
         "answerIndex":1,"explanation":"A=Atomicity (all or nothing). C=Consistency (constraints maintained). I=Isolation (concurrent transactions don't interfere). D=Durability (committed data survives crashes). These four guarantee data integrity even with failures and concurrency.","tags":["acid","transactions","basics"]},
        {"id":"rdb-q2","type":"mcq","prompt":"What does Atomicity in ACID guarantee?",
         "choices":["Each operation runs in a separate thread","A transaction is either FULLY completed or FULLY rolled back — no partial execution. If the power goes out mid-transaction, all changes are undone.",
                    "Transactions run faster","Data is compressed atomically"],
         "answerIndex":1,"explanation":"Atomicity: debit Alice AND credit Bob happen together or neither happens. You can't have Alice's balance reduced without Bob's being increased. Even a crash mid-transaction is safe — PostgreSQL WAL replay undoes incomplete transactions on recovery.","tags":["acid","atomicity"]},
        {"id":"rdb-q3","type":"mcq","prompt":"What is a foreign key constraint?",
         "choices":["An encryption key","A constraint that ensures a value in one table references a valid value in another table — prevents orphaned records",
                    "An index on a primary key","A unique identifier generated by the database"],
         "answerIndex":1,"explanation":"FOREIGN KEY (user_id) REFERENCES users(id): ensures every order.user_id points to a real user in the users table. Trying to insert an order with user_id=999 (no such user) -> constraint violation. Deleting a user with orders -> violation (unless CASCADE is set).","tags":["relational","foreign-key","constraints"]},
        {"id":"rdb-q4","type":"mcq","prompt":"What is an N+1 query problem?",
         "choices":["Using more than N indexes","Fetching 1 collection then making N additional queries — one per item — instead of a single JOIN query. 100 users = 101 queries instead of 1.",
                    "Joining more than N tables","Having N+1 columns in a table"],
         "answerIndex":1,"explanation":"N+1: SELECT users (1 query) -> for each user: SELECT orders WHERE user_id = ? (N queries) = N+1 total. Fix: JOIN in one query, or use ORM eager loading (Hibernate JOIN FETCH, SQLAlchemy joinedload). N+1 causes the most ORM performance issues.","tags":["sql","n+1","performance"]},
        {"id":"rdb-q5","type":"mcq","prompt":"What does EXPLAIN ANALYZE 'Seq Scan' mean?",
         "choices":["A fast sequential read","A full table scan — reading every row in the table. Usually means a missing index on a large table.",
                    "A sequential index scan","Scan of sequence objects"],
         "answerIndex":1,"explanation":"Seq Scan = full table scan. On a table of 1M rows, Seq Scan reads all 1M rows even if only 1 matches. If you see Seq Scan on a large table with low selectivity, add an index on the WHERE clause column. Index Scan or Index Only Scan is what you want.","tags":["sql","explain","indexes"]},
        {"id":"rdb-q6","type":"mcq","prompt":"What is the difference between WHERE and HAVING in SQL?",
         "choices":["They are identical","WHERE filters BEFORE grouping (individual rows). HAVING filters AFTER grouping (aggregated results). WHERE cannot reference aggregate functions (COUNT, SUM, etc.).",
                    "HAVING is older syntax for WHERE","WHERE is for joins, HAVING for subqueries"],
         "answerIndex":1,"explanation":"WHERE: SELECT ... FROM orders WHERE total > 100 — filters individual order rows before GROUP BY. HAVING: SELECT user_id, COUNT(*) FROM orders GROUP BY user_id HAVING COUNT(*) > 5 — filters groups after aggregation. You cannot use SUM/COUNT in WHERE clause.","tags":["sql","where","having"]},
        {"id":"rdb-q7","type":"mcq","prompt":"What is the 'leftmost prefix rule' for compound indexes?",
         "choices":["Use the first column often","A compound index (a, b, c) can be used for queries filtering on (a), (a,b), or (a,b,c) — but NOT for queries that skip the leftmost column (b alone, c alone, or b,c without a)",
                    "Always sort by leftmost column","Leftmost column must be the primary key"],
         "answerIndex":1,"explanation":"Index (user_id, created_at): WHERE user_id = 5 AND created_at > '2025' -> uses full index. WHERE user_id = 5 -> uses index (partial). WHERE created_at > '2025' -> CANNOT use this index (skips user_id). Create a separate index (created_at) if you need that query.","tags":["sql","indexes","compound-index"]},
        {"id":"rdb-q8","type":"mcq","prompt":"What is database normalisation?",
         "choices":["Encrypting sensitive columns","Organising a database into separate related tables to reduce data duplication — each fact stored in one place, reducing update anomalies",
                    "Creating indexes on all columns","Scaling the database horizontally"],
         "answerIndex":1,"explanation":"Normalisation: don't repeat yourself in the database. User's email in orders.customer_email AND users.email = problem (update in one place, other becomes stale). Solution: store email only in users, use foreign key from orders. Single source of truth.","tags":["relational","normalisation","design"]},
        {"id":"rdb-q9","type":"mcq","prompt":"What SQL isolation level should you use for a multi-step financial transaction (debit + credit)?",
         "choices":["READ UNCOMMITTED (fastest)","READ COMMITTED (default)","REPEATABLE READ or SERIALIZABLE to prevent concurrent transactions from interfering with the complete debit+credit sequence",
                    "Isolation level doesn't matter for this"],
         "answerIndex":2,"explanation":"READ COMMITTED: another transaction's committed change can be visible WITHIN your transaction. For debit+credit: if another transaction modifies the same account between your two updates, READ COMMITTED may produce incorrect results. SERIALIZABLE: transactions appear sequential, correct by definition.","tags":["sql","isolation","transactions","financial"]},
        {"id":"rdb-q10","type":"mcq","prompt":"What does a LEFT JOIN return vs INNER JOIN?",
         "choices":["They return the same rows","LEFT JOIN: all rows from left table + matching rows from right (NULL if no match). INNER JOIN: only rows with matches in BOTH tables. LEFT JOIN includes users with no orders.",
                    "LEFT JOIN is faster","INNER JOIN returns more rows"],
         "answerIndex":1,"explanation":"INNER JOIN users u JOIN orders o: only users who HAVE at least one order. LEFT JOIN users u LEFT JOIN orders o: ALL users (orders columns = NULL for users with no orders). Use LEFT JOIN for 'show me all X, and their Y if they have any'.","tags":["sql","join","left-join"]},
        {"id":"rdb-q11","type":"mcq","prompt":"What is a CTE (Common Table Expression) and why use it?",
         "choices":["A type of join","WITH clause creates a named temporary result set used within the same query — improves readability over nested subqueries, can make complex queries understandable",
                    "A database constraint","A replication technique"],
         "answerIndex":1,"explanation":"WITH high_value AS (SELECT user_id FROM orders WHERE total > 1000) SELECT u.name FROM users u JOIN high_value h ON u.id = h.user_id. Same as subquery but readable. Recursive CTEs (WITH RECURSIVE) enable tree/graph queries.","tags":["sql","cte","readability"]},
        {"id":"rdb-q12","type":"mcq","prompt":"What is denormalisation and when is it appropriate?",
         "choices":["Removing all indexes for performance","Intentionally adding redundant data (duplicating from other tables) to avoid JOINs — trading write overhead for faster reads",
                    "Converting to NoSQL","Changing column data types"],
         "answerIndex":1,"explanation":"Denormalise: store product_name in order_items even though products table exists. Reads are faster (no JOIN), reporting is simpler. Trade-off: when product name changes, must update both places. Use for: read-heavy reporting, analytics tables, caching computed values.","tags":["sql","denormalisation","performance"]},
        {"id":"rdb-q13","type":"mcq","prompt":"What is the PostgreSQL SERIAL type?",
         "choices":["A serialised column","Auto-incrementing INTEGER — equivalent to INTEGER with a sequence that generates unique IDs automatically. Modern PostgreSQL prefers: id BIGINT GENERATED ALWAYS AS IDENTITY",
                    "A unique index type","A replication identifier"],
         "answerIndex":1,"explanation":"SERIAL = creates a sequence, sets default to nextval(sequence). Each insert auto-gets next ID. Modern syntax: id BIGINT GENERATED ALWAYS AS IDENTITY (SQL standard). BIGSERIAL for 64-bit. Use BIGSERIAL for tables that might exceed 2 billion rows.","tags":["postgresql","serial","primary-key"]},
        {"id":"rdb-q14","type":"mcq","prompt":"What is a partial index in PostgreSQL?",
         "choices":["An index on a subset of columns","An index with a WHERE condition — only rows matching the condition are indexed. Smaller, faster than full index.",
                    "An incomplete index build","An index on NULL values only"],
         "answerIndex":1,"explanation":"CREATE INDEX idx_active_users ON users(email) WHERE active = true. Only active users in index. If 90% of users are inactive, full index has 10x more entries than partial index. Smaller index = fits in memory = faster. Use when: most queries filter by a stable condition (email lookup only for active users).","tags":["postgresql","partial-index","performance"]},
        {"id":"rdb-q15","type":"mcq","prompt":"What does VACUUM do in PostgreSQL?",
         "choices":["Deletes old backups","Reclaims storage from dead rows (rows updated/deleted but not yet physically removed by MVCC) and updates statistics for the query planner",
                    "Compresses the database","Reorganises indexes"],
         "answerIndex":1,"explanation":"PostgreSQL MVCC: UPDATE creates a new row version, marks old version as dead (not immediately deleted). VACUUM: physically removes dead rows, reclaims disk space, updates planner statistics. AUTOVACUUM runs automatically — but heavily updated tables may need manual tuning.","tags":["postgresql","vacuum","mvcc"]},
        {"id":"rdb-q16","type":"mcq","prompt":"What is the PostgreSQL JSONB type and when should you use it?",
         "choices":["JSON stored as text with no indexing","Binary JSON that supports indexing (GIN index), efficient storage, and query operators — good for semi-structured data that varies per row",
                    "JSON only for legacy compatibility","JSONB is deprecated"],
         "answerIndex":1,"explanation":"JSONB: binary JSON stored efficiently. CREATE INDEX ON products USING GIN(attributes). Query: WHERE attributes @> '{\"color\": \"red\"}'. Use for: product attributes that vary by category, user preferences, metadata. Not a replacement for proper relational tables — use when schema genuinely varies per row.","tags":["postgresql","jsonb","semi-structured"]},
        {"id":"rdb-q17","type":"mcq","prompt":"What is MVCC (Multi-Version Concurrency Control)?",
         "choices":["Multiple database versions","Readers never block writers, writers never block readers — each transaction sees a snapshot of the database at the time it started",
                    "Multi-core CPU optimisation","A replication protocol"],
         "answerIndex":1,"explanation":"MVCC: instead of locking rows for reads, every transaction sees a 'snapshot' of the database. Writer creates new version, old version stays for ongoing readers. Result: Readers never block writers (no shared locks). High concurrency. PostgreSQL, MySQL InnoDB both use MVCC.","tags":["postgresql","mvcc","concurrency"]},
        {"id":"rdb-q18","type":"mcq","prompt":"What is the EXPLAIN ANALYZE 'Index Only Scan'?",
         "choices":["Same as Index Scan","The most efficient scan — query answered entirely from the index without touching the table. Requires that all needed columns are in the index.",
                    "Full table scan using index","Deprecated feature"],
         "answerIndex":1,"explanation":"Index Only Scan: all required data is in the index itself. No table heap access. Fastest possible read. Example: SELECT user_id FROM orders WHERE user_id = 123 with index on user_id. The index contains the user_id value — no need to look up the actual row.","tags":["postgresql","explain","index-only-scan"]},
        {"id":"rdb-q19","type":"mcq","prompt":"When should you NOT add a database index?",
         "choices":["Never — always add indexes","Small tables (<1000 rows), columns with very low cardinality (boolean), heavily write-dominated tables where index maintenance overhead exceeds read benefit",
                    "Tables with more than 10 columns","Never add indexes to foreign key columns"],
         "answerIndex":1,"explanation":"Index overhead: every INSERT/UPDATE/DELETE must also update all indexes on that table. For write-heavy tables with millions of inserts/sec, too many indexes can SLOW DOWN writes more than they help reads. For small tables, full scan is faster than index. Balance read gain vs write cost.","tags":["sql","indexes","when-not-to-index"]},
        {"id":"rdb-q20","type":"mcq","prompt":"What does RETURNING do in PostgreSQL INSERT/UPDATE?",
         "choices":["Returns the number of rows affected","Returns specified column values of the inserted/updated rows — avoids a second SELECT to get the generated ID",
                    "Returns an error code","Returns the query plan"],
         "answerIndex":1,"explanation":"INSERT INTO users (name) VALUES ('Alice') RETURNING id, created_at. Returns the auto-generated id and timestamp immediately without a second round-trip query. Very useful with ORM frameworks. Standard PostgreSQL extension (MySQL equivalent: LAST_INSERT_ID()).","tags":["postgresql","returning","dml"]},
    ]

    RELATIONAL_FC = [
        {"id":"rdb-fc1","front":"ACID mnemonic","back":"A=Atomicity (all or nothing). C=Consistency (constraints enforced). I=Isolation (concurrent transactions safe). D=Durability (committed data survives crash). WAL (Write-Ahead Log) is the mechanism that provides C and D. MVCC provides I.","tags":["acid","transactions"]},
        {"id":"rdb-fc2","front":"N+1 fix strategies","back":"1. JOIN in one query. 2. ORM eager loading (Hibernate: JOIN FETCH, SQLAlchemy: joinedload). 3. Batch load with IN clause. N+1 is the #1 ORM performance killer. Use EXPLAIN ANALYZE to spot it: N identical queries with different ID values.","tags":["sql","n+1","orm"]},
        {"id":"rdb-fc3","front":"Compound index leftmost prefix rule","back":"Index (a, b, c) works for: WHERE a=?, WHERE a=? AND b=?, WHERE a=? AND b=? AND c=?. Does NOT work for: WHERE b=?, WHERE c=?, WHERE b=? AND c=? (skips leftmost). Order columns by most-selective and most-common-in-queries.","tags":["sql","indexes","compound-index"]},
        {"id":"rdb-fc4","front":"EXPLAIN ANALYZE scan types","back":"Seq Scan = full table scan (bad on large tables, add index). Index Scan = uses index, accesses table. Index Only Scan = uses index only (best). Bitmap Heap Scan = multiple index matches, batches heap access.","tags":["sql","explain","performance"]},
        {"id":"rdb-fc5","front":"JOIN types cheat sheet","back":"INNER JOIN: only matching rows in both tables. LEFT JOIN: all left rows + matching right (NULL if none). RIGHT JOIN: all right + matching left. FULL OUTER JOIN: all rows from both, NULLs where no match. Most common: INNER and LEFT.","tags":["sql","joins"]},
        {"id":"rdb-fc6","front":"Isolation levels — practical choice","back":"READ COMMITTED (default): good for most web queries. REPEATABLE READ: safe for multi-step read then write in same transaction. SERIALIZABLE: use for financial transactions where intermediate state must be consistent. Always start with default, upgrade if anomaly occurs.","tags":["sql","isolation","transactions"]},
        {"id":"rdb-fc7","front":"Normalise vs denormalise decision","back":"Normalise: data integrity, single source of truth, complex queries with JOINs. Denormalise: read performance, reporting, analytics. Rule: normalise first. Denormalise specific hot read paths when profiling shows JOINs are the bottleneck.","tags":["sql","normalisation","performance"]},
        {"id":"rdb-fc8","front":"PostgreSQL distinctive features","back":"JSONB + GIN index (fast JSON queries). VACUUM/AUTOVACUUM (MVCC cleanup). RETURNING (get inserted rows without second query). Partial indexes (WHERE condition in index). PostGIS extension (geospatial). pg_vector (embeddings/AI). Extensions ecosystem.","tags":["postgresql","features"]},
    ]

    d['guide'] = RELATIONAL_GUIDE
    d['questions'] = RELATIONAL_Q
    d['flashcards'] = RELATIONAL_FC
    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"relational-databases.json: guide={len(RELATIONAL_GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ── patch_scaling_3.py ──────────────────────────────────────────────────────────────────
    """
    patch_scaling_3.py — expands error-logging.json
    Run: python3 scripts/patch_scaling_3.py
    """
    import json
    from pathlib import Path

    BASE = Path(__file__).parent.parent / 'src/content/topics/scaling'

    p = BASE / 'error-logging.json'
    d = json.loads(p.read_text())

    GUIDE = """# Error Logging & Observability

    ## What Is Observability? (Start From Zero)

    Your application is running in production. Users are complaining it's slow.
    Something is wrong. But what? Without observability, you are flying blind:
    you guess, restart services, hope for the best.

    Observability means your system can tell you WHAT is happening, WHERE,
    and WHY — by examining its outputs without modifying its code.

    The three pillars of observability are **Logs, Metrics, and Traces**.
    Think of them as three different ways to answer "what is my system doing?".

    ```
    LOGS:     "What happened?" — discrete events with context
      ERROR 2026-04-28T14:23:11Z userId=123 action=checkout error="card declined"

    METRICS:  "How is it doing?" — numerical measurements over time
      api_latency_p99 = 342ms at 14:23:00
      http_5xx_rate = 0.02% at 14:23:00

    TRACES:   "How did it flow?" — path of one request through all services
      Request abc123:
        API Gateway: 5ms
        auth-service: 12ms
        order-service: 180ms
          -> database: 45ms
          -> payment-service: 120ms  <-- this is slow!
        Total: 197ms
    ```

    ---

    ## Logs — Structured vs Unstructured

    ```
    UNSTRUCTURED LOGS (avoid in new code):
      2026-04-28 14:23 ERROR: User 123 checkout failed: card declined

      Problems:
        Hard to search: grep 'card declined' works but 'all errors for user 123' is painful
        No consistent schema: different services log differently
        Machine parsing required: regex-based alerting is fragile

    STRUCTURED LOGS (JSON format — best practice):
      {
        "timestamp": "2026-04-28T14:23:11Z",
        "level": "ERROR",
        "service": "order-service",
        "userId": 123,
        "action": "checkout",
        "orderId": "ord-456",
        "error": "card_declined",
        "cardLast4": "4242",
        "duration_ms": 342,
        "traceId": "abc-123-xyz"
      }

      Benefits:
        Query: WHERE userId = 123 AND level = 'ERROR'
        Alert: error_rate > 1% by service
        Correlate: all events with traceId = 'abc-123-xyz'
        Dashboards built automatically from field names
    ```

    ---

    ## Log Levels — Use Them Correctly

    ```
    FATAL / CRITICAL:
      Application cannot continue. Must page someone NOW.
      "Database connection pool exhausted, cannot serve any requests"
      Use sparingly — should trigger immediate alert and human response.

    ERROR:
      Operation failed. Requires investigation. User affected.
      "Payment processing failed for orderId=456"
      "Cannot connect to email service after 3 retries"
      Alert on high ERROR rate in production.

    WARN:
      Unexpected but recoverable. May indicate a problem building up.
      "Response time 4.2s exceeds threshold of 3s"
      "Retry attempt 2/3 for service call"
      "Cache miss rate 85% (unusually high)"
      Watch warn logs — elevated warn = future error.

    INFO:
      Normal operation events. Key business events.
      "Order ord-456 created for userId=123 amount=$99.99"
      "User userId=789 logged in from IP 1.2.3.4"
      Production: INFO and above. Don't log INFO for every function call.

    DEBUG:
      Detailed technical flow. Only in development.
      "Entering getUserById with id=123"
      "Cache lookup for key user:123 -> MISS"
      NEVER in production (too much volume, hurts performance, may log sensitive data).

    TRACE:
      Even more detailed than DEBUG. Very rarely used. Never in production.
    ```

    ---

    ## Structured Logging in Java and Python

    ```java
    // Java - SLF4J + Logback with structured logging
    import org.slf4j.Logger;
    import org.slf4j.LoggerFactory;
    import net.logstash.logback.argument.StructuredArguments;

    Logger log = LoggerFactory.getLogger(OrderService.class);

    // Good: structured key-value context
    log.info("Order created",
        StructuredArguments.kv("orderId", order.getId()),
        StructuredArguments.kv("userId", userId),
        StructuredArguments.kv("amount", order.getTotal())
    );

    // Good: include exception
    try {
        processPayment(order);
    } catch (PaymentException e) {
        log.error("Payment failed",
            StructuredArguments.kv("orderId", order.getId()),
            StructuredArguments.kv("userId", userId),
            e  // exception at the end -> stack trace in log
        );
    }
    ```

    ```python
    # Python - structlog (best library for structured logging)
    import structlog

    log = structlog.get_logger()

    # Bind context once, reuse in all log statements
    log = log.bind(service="order-service", userId=user_id)

    log.info("order_created", order_id=order_id, amount=99.99)
    log.error("payment_failed", order_id=order_id, error=str(e), exc_info=True)
    ```

    ---

    ## Metrics — The Four Golden Signals

    Google SRE book defines the Four Golden Signals that should be monitored for
    any production service:

    ```
    1. LATENCY:
       How long does it take to serve a request?
       Measure: p50 (median), p95, p99, p999
       Alert: p99 > 500ms for user-facing API
       WHY p99 not average: average hides slow outliers.
         avg=50ms but p99=5000ms: 1% of users wait 5 seconds

    2. TRAFFIC:
       How much demand is the system handling?
       Measure: requests/second, messages/second, queries/second
       Alert: traffic drops to near zero (service down), sudden spike (DDoS or viral event)

    3. ERRORS:
       What fraction of requests are failing?
       Measure: HTTP 5xx rate, exception rate, timeout rate
       Alert: error rate > 0.1% for critical path, > 1% for less critical

    4. SATURATION:
       How full is the service's capacity?
       Measure: CPU %, memory %, DB connection pool %, queue depth
       Alert: CPU > 80%, memory > 85%, connection pool > 90%
       WHY: services degrade before they fail; saturation predicts failure
    ```

    ---

    ## Metrics Tools — Prometheus + Grafana

    ```
    PROMETHEUS:
      Pull-based metrics collection (Prometheus scrapes your service)
      Your service exposes /metrics endpoint with Prometheus format
      Prometheus stores time-series metrics
      PromQL query language for aggregation and alerts

      # Python Prometheus metrics
      from prometheus_client import Counter, Histogram, start_http_server

      request_count = Counter('http_requests_total', 'Total HTTP requests',
                               ['method', 'endpoint', 'status'])
      request_latency = Histogram('http_request_duration_seconds',
                                   'HTTP request latency')

      @app.route('/orders')
      def get_orders():
          with request_latency.time():  # measures duration
              result = process()
              request_count.labels(method='GET', endpoint='/orders', status='200').inc()
              return result

      # Prometheus scrapes http://your-service:8080/metrics
      # Automatically collects: request_count, request_latency histograms

    GRAFANA:
      Visualisation dashboard connected to Prometheus (or CloudWatch, Loki, etc.)
      Create dashboards showing: latency over time, error rate, traffic, CPU
      Set up Alertmanager to send alerts to PagerDuty/Slack when thresholds crossed

    CloudWatch (AWS):
      Managed alternative — no Prometheus/Grafana to run
      Lambda, EC2, RDS all push metrics to CloudWatch automatically
      CloudWatch Alarms -> SNS -> PagerDuty
    ```

    ---

    ## Distributed Tracing — Finding the Slow Part

    ```
    PROBLEM WITHOUT TRACING:
      Microservices: request flows through 8 services. Total response = 2 seconds.
      Which service is slow? You have logs in 8 places but can't correlate them.

    WITH DISTRIBUTED TRACING (OpenTelemetry standard):
      Each request gets a unique trace_id at entry point (API gateway).
      trace_id is passed in headers to every downstream service.
      Each service records: start_time, end_time, parent_span_id.
      Tracing backend (Jaeger, Zipkin, AWS X-Ray) reconstructs the timeline.

      Visualisation (flame graph):
      |======= API Gateway 5ms ==========|
        |=== Auth Service 12ms ===|
        |============ Order Service 200ms =============|
          |= Cache lookup 1ms =|
          |=================== DB query 45ms ====================|
          |========================= Payment Service 130ms ========|
                                    ^---- this is the bottleneck!

      Without this: you'd be guessing which service is slow.
      With this: obvious in 5 seconds that Payment Service is 65% of total latency.
    ```

    ---

    ## Log Aggregation — Centralised Logging

    ```
    PROBLEM: Logs on 50 servers.
      To find a user's error: SSH into all 50, grep each file. Painful.

    SOLUTION: Centralised log aggregation
      All services ship logs to a central system.
      Query all logs in one place.

    ELK STACK (Elasticsearch + Logstash + Kibana):
      Services -> Logstash/Filebeat -> Elasticsearch (storage + search) -> Kibana (UI)
      Search: 'all ERROR logs for userId=123 in last hour across all services'
      Full-text search on petabytes of logs.

    LOKI + GRAFANA (modern, cheaper alternative):
      Like Prometheus but for logs. Stores compressed log streams. Cheaper than ES.
      Grafana UI for both metrics (Prometheus) and logs (Loki) in one dashboard.

    AWS CLOUDWATCH LOGS:
      Managed alternative. Lambda, EC2, ECS auto-ship logs to CloudWatch.
      CloudWatch Insights: query language for ad-hoc log analysis.
      Expensive at scale but zero ops.

    DATADOG, NEW RELIC, SPLUNK:
      SaaS observability platforms (paid). Logs + metrics + traces in one UI.
      Expensive but powerful and no infrastructure to manage.
    ```

    ---

    ## Alerting Strategy — Alert on Symptoms Not Causes

    ```
    BAD ALERTING:
      Alert when: CPU > 80%
      Alert when: memory > 85%
      Alert when: disk > 90%

      Problem: These are CAUSES. You get paged about resource usage but
      the user may not be affected yet.

    GOOD ALERTING (symptom-based = user impact):
      Alert when: HTTP 5xx rate > 1% (users getting errors)
      Alert when: p99 latency > 1s (users experiencing slowness)
      Alert when: order checkout success rate < 99.5% (users can't buy)
      Alert when: DLQ depth > 0 (messages failing to process)

    ALERT FATIGUE (the real danger):
      Too many alerts = engineers start ignoring them.
      Goal: every alert requires human action.
      If an alert fires regularly but 'everything is fine': delete or adjust it.

      Priority levels:
        P1/Critical: wake someone up NOW (5xx rate, data loss risk)
        P2/High: fix within the hour (elevated warnings, degraded performance)
        P3/Medium: fix in business hours (non-critical degradation)
        P4/Low: investigate next sprint (slow trends, non-impactful anomalies)
    ```

    ---

    ## The Correlation ID Pattern

    ```
    A correlation ID (trace ID) is a unique identifier assigned to each request
    at the entry point and passed through every service call.

    Flow:
      Browser -> API Gateway
        Generates: X-Request-ID: abc-123-xyz
        Logs: "Request abc-123-xyz received: GET /checkout"

      API Gateway -> Order Service
        Passes header: X-Request-ID: abc-123-xyz
        Order Service logs: "traceId=abc-123-xyz order processing started"

      Order Service -> Payment Service
        Passes header: X-Request-ID: abc-123-xyz
        Payment Service logs: "traceId=abc-123-xyz payment initiated"

      Error occurs:
        Payment Service logs: "traceId=abc-123-xyz ERROR payment declined"

      Finding all logs for one request:
        grep 'abc-123-xyz' across all services (or query 'traceId: abc-123-xyz' in Kibana)
        See every step that request took, in order.
        Without correlation ID: impossible to trace across services.
    ```

    ---

    ## SLI, SLO, and SLA — Measuring Reliability

    ```
    SLI (Service Level Indicator):
      Measurable metric of service behaviour.
      "99.5% of requests complete in < 300ms over the last 30 days"
      "99.9% of requests return HTTP 2xx"

    SLO (Service Level Objective):
      Internal goal for an SLI.
      "We aim for 99.9% availability and p99 < 500ms"
      Set by engineering. Not binding but drives work prioritization.

    SLA (Service Level Agreement):
      Contractual commitment to customers (with consequences).
      "We guarantee 99.9% uptime per quarter or customer gets credit"
      SLA < SLO (you want internal safety margin above your commitment)

    ERROR BUDGET:
      99.9% SLO = 0.1% allowed downtime = 8.7 hours per year
      Error budget: how much unreliability you can afford.
      If error budget exhausted: freeze new feature work, fix stability.
      If error budget healthy: can take more risks, deploy more often.
    ```

    ---

    ## Mind Map

    ```
    ERROR LOGGING & OBSERVABILITY
    |
    +-- THREE PILLARS
    |   +-- Logs (what happened - events)
    |   +-- Metrics (how it's doing - numbers over time)
    |   +-- Traces (how request flowed - timeline)
    |
    +-- LOGS
    |   +-- Structured (JSON) > unstructured text
    |   +-- Levels: FATAL > ERROR > WARN > INFO > DEBUG > TRACE
    |   +-- Correlation ID per request
    |   +-- Centralised (ELK, Loki, CloudWatch)
    |
    +-- METRICS (4 Golden Signals)
    |   +-- Latency (p99, p999 — not average)
    |   +-- Traffic (requests/sec)
    |   +-- Errors (5xx rate, exception rate)
    |   +-- Saturation (CPU, memory, queue depth)
    |
    +-- TRACES
    |   +-- OpenTelemetry standard
    |   +-- trace_id passed in headers
    |   +-- Jaeger/Zipkin/X-Ray visualise flame graphs
    |
    +-- ALERTING
    |   +-- Alert on SYMPTOMS (user impact) not causes (CPU)
    |   +-- Avoid alert fatigue
    |   +-- SLI -> SLO -> SLA hierarchy
    |   +-- Error budget for release velocity decisions
    ```

    ---

    ## How Observability Connects to Other Topics

    - **CI/CD**: Pipeline deploys should include smoke tests that verify metrics
      don't spike after deployment. Automated rollback if error rate > threshold.
    - **Kubernetes**: kubectl logs, kubectl exec for debugging. Sidecar containers
      for log shipping (Fluentd sidecar pattern).
    - **AWS**: CloudWatch handles logs + metrics for Lambda, EC2, RDS automatically.
      AWS X-Ray for distributed tracing.
    - **Load Balancing**: ALB access logs and latency metrics are key observability data.

    ---

    ## References and Further Learning

    ### Videos (Watch These!)
    - **Observability vs Monitoring** by IBM Technology:
      https://www.youtube.com/watch?v=UJA4PGKny2k
      - Clear explanation of logs, metrics, traces with real examples.
    - **Prometheus + Grafana Tutorial** by TechWorld with Nana:
      https://www.youtube.com/watch?v=QoDqxm7ybLc
      - Full hands-on Prometheus/Grafana setup.

    ### Free Books and Articles
    - **Google SRE Book (free)**: https://sre.google/sre-book/table-of-contents/
      - Chapters: Monitoring Distributed Systems, Alerting on SLOs.
    - **OpenTelemetry docs**: https://opentelemetry.io/docs/
      - The standard for distributed tracing. Language-specific quickstarts.

    ### Diagrams
    - **ELK Stack architecture diagram**: search 'ELK Stack architecture diagram'
    - **Distributed tracing flame graph**: search 'Jaeger distributed tracing example'

    ### Practice
    - **Prometheus + Grafana with Docker Compose**: many tutorials on GitHub.
      Set up locally and instrument a Python Flask or Spring Boot app.
    """

    NEW_Q = [
        {"id":"obs-q1","type":"mcq","prompt":"What are the three pillars of observability?",
         "choices":["CPU, Memory, Disk","Logs, Metrics, Traces — three complementary ways to understand system behaviour",
                    "Debug, Info, Error","Frontend, Backend, Database"],
         "answerIndex":1,"explanation":"Logs: discrete events ('what happened'). Metrics: numerical measurements over time ('how is it doing'). Traces: request journey across services ('how did it flow'). Each answers different questions. Need all three for full observability.","tags":["observability","three-pillars"]},
        {"id":"obs-q2","type":"mcq","prompt":"What is structured logging and why is it better than plain text logs?",
         "choices":["Logs with bullet points","JSON-formatted logs with consistent field names — machine-queryable, filterable by field (WHERE userId=123), dashboardable, alertable without regex",
                    "Logs sorted by timestamp","Gzip-compressed logs"],
         "answerIndex":1,"explanation":"Unstructured: '2026 ERROR user 123 failed checkout' — grep only. Structured JSON: {level:ERROR, userId:123, action:checkout} — query by field, build dashboards, alert on error count by service. Elasticsearch, Splunk, CloudWatch Insights all work on structured logs.","tags":["logging","structured-logging"]},
        {"id":"obs-q3","type":"mcq","prompt":"What are the Four Golden Signals from Google's SRE book?",
         "choices":["CPU, RAM, Disk, Network","Latency, Traffic, Errors, Saturation — these four cover all user-facing aspects of service health",
                    "Debug, Info, Warn, Error","Availability, Durability, Scalability, Security"],
         "answerIndex":1,"explanation":"Golden Signals: Latency (how slow?), Traffic (how busy?), Errors (how many failures?), Saturation (how full?). Monitor these four and you can detect virtually any user-impacting issue before users call. Alert on these, not raw system metrics.","tags":["observability","golden-signals"]},
        {"id":"obs-q4","type":"mcq","prompt":"Why should you alert on p99 latency rather than average latency?",
         "choices":["p99 is simpler to calculate","Average can look good (50ms) while p99 is terrible (5000ms) — average hides the 1% of users experiencing severe slowness",
                    "p99 is cheaper to store","Average is inaccurate"],
         "answerIndex":1,"explanation":"Avg 50ms, p99 5000ms: 99% of requests are fast but 1% of users wait 5 seconds. At 1000 req/sec that's 10 users/sec having a bad experience. Average hides tail latency. Always monitor p95, p99, p999 for user-facing services.","tags":["observability","latency","percentiles"]},
        {"id":"obs-q5","type":"mcq","prompt":"What is a correlation ID (trace ID) and why is it important?",
         "choices":["A database primary key","A unique identifier assigned to each request and passed through all services — allows finding all log entries related to one request across a distributed system",
                    "An encryption key","A user session token"],
         "answerIndex":1,"explanation":"Without correlation ID: user reports 'my checkout failed at 14:23'. You search 8 service logs separately, can't link them. With X-Request-ID passed in all service calls: grep 'abc-123' across all services = see complete request journey instantly.","tags":["observability","correlation-id","distributed"]},
        {"id":"obs-q6","type":"mcq","prompt":"What log level should be used for 'unexpected but recoverable' events that might indicate a growing problem?",
         "choices":["DEBUG","INFO","WARN — unusual situations that don't fail the operation but signal something to watch (slow response, retry attempt, unusually high cache miss rate)",
                    "ERROR"],
         "answerIndex":2,"explanation":"WARN = yellow flag. Not broken, but concerning. 'Retry 2/3 for payment service' is WARN — worked on 3rd try. If WARN rate increases: ERROR will follow. Monitor WARN trends to catch problems before they become ERROR storms.","tags":["logging","log-levels"]},
        {"id":"obs-q7","type":"mcq","prompt":"What is distributed tracing?",
         "choices":["Logging to multiple destinations","Tracking a single request as it flows through multiple microservices — each service records timing data allowing a flame graph of the entire request path",
                    "A load balancing technique","Tracing network packets"],
         "answerIndex":1,"explanation":"Distributed trace: trace_id in HTTP headers, each service records span (start, end, parent span). Jaeger/Zipkin/X-Ray reconstructs: 'request abc took: API Gateway 5ms + Auth 12ms + DB 45ms + Payment 130ms = 192ms total. Payment is 68% of latency.'","tags":["observability","tracing","distributed"]},
        {"id":"obs-q8","type":"mcq","prompt":"What is the OpenTelemetry standard?",
         "choices":["A monitoring algorithm","A vendor-neutral API and SDK for instrumenting code to generate traces, metrics, and logs — works with any backend (Jaeger, Zipkin, Datadog, X-Ray)",
                    "A log format","An alerting protocol"],
         "answerIndex":1,"explanation":"OpenTelemetry (OTel): instrument once, use any backend. Without OTel: instrument for Datadog, then switch to X-Ray = rewrite all instrumentation. With OTel: write OTel code once, configure different exporters. Becoming the industry standard for distributed tracing.","tags":["observability","opentelemetry","tracing"]},
        {"id":"obs-q9","type":"mcq","prompt":"What is alert fatigue and how do you prevent it?",
         "choices":["Alerts that are too quiet","When too many alerts fire (many false-positives or low-priority) causing engineers to start ignoring all alerts — even critical ones get missed",
                    "Alerts with no notification channel","Alerts that are too slow"],
         "answerIndex":1,"explanation":"Alert fatigue: team gets 100 alerts/day, starts silencing/ignoring them. Then a real P1 gets missed. Fix: every alert must require human action. If alert fires and 'nothing is actually wrong', delete or adjust it. Few, meaningful, actionable alerts > many noisy ones.","tags":["observability","alerting","sre"]},
        {"id":"obs-q10","type":"mcq","prompt":"What is the difference between an SLI, SLO, and SLA?",
         "choices":["They are the same","SLI = measurable metric (99.5% of requests < 300ms). SLO = internal target (99.9% availability). SLA = contractual commitment with penalty (99.9% or get refund).",
                    "SLO is for internal teams only","SLA is set by engineering"],
         "answerIndex":1,"explanation":"SLI: what you measure. SLO: what you aim for internally (no penalty if missed, just incentive). SLA: what you promise customers with consequences. Always set SLO stricter than SLA — if SLA is 99.9%, set SLO at 99.95% internally. SLA breach = bad. SLO breach = early warning.","tags":["observability","sli","slo","sla"]},
        {"id":"obs-q11","type":"mcq","prompt":"What is an error budget in SRE?",
         "choices":["Budget for fixing bugs","The amount of downtime/errors allowed within an SLO period — 99.9% SLO = 0.1% budget = 8.7 hours/year. If exhausted: freeze releases until budget recovers.",
                    "Cost of error monitoring tools","Number of errors per sprint"],
         "answerIndex":1,"explanation":"Error budget = 100% - SLO. 99.9% = 0.1% error budget = 8.7 hours/year allowed downtime. Budget empowers: 'Do we have budget to take this risk?' Exhausted budget -> halt new features, focus on reliability. Healthy budget -> deploy more aggressively.","tags":["observability","error-budget","sre"]},
        {"id":"obs-q12","type":"mcq","prompt":"What is the ELK stack?",
         "choices":["A storage technology","Elasticsearch (search/store logs) + Logstash (collect/parse/ship logs) + Kibana (visualise and query logs) — popular open-source centralised logging platform",
                    "A container orchestration stack","A database replication protocol"],
         "answerIndex":1,"explanation":"ELK: Logstash/Filebeat ships logs from all servers -> Elasticsearch stores and indexes -> Kibana UI to query and dashboard. Search '10,000 servers in 5ms' type speed. Modern: often replace Logstash with Fluentd (lighter). Cloud alternative: AWS OpenSearch + Managed Grafana.","tags":["observability","elk","logging"]},
        {"id":"obs-q13","type":"mcq","prompt":"Why should you NOT use DEBUG log level in production?",
         "choices":["DEBUG is reserved for databases","DEBUG logs are extremely verbose — for every user request this might generate 50+ log lines. Fills disk, costs money, hurts performance, may log sensitive data (passwords, tokens, PII)",
                    "DEBUG is not valid in Java","DEBUG requires a special license"],
         "answerIndex":1,"explanation":"DEBUG: 'entering function X', 'cache lookup for key user:123 MISS', 'marshaling response body {...}'. Hundreds of lines per request. 1000 req/sec = 100K+ log lines/sec. Disk full in hours. Log aggregation bill explodes. Sensitive data logged. Production: INFO and above.","tags":["logging","log-levels","performance"]},
        {"id":"obs-q14","type":"mcq","prompt":"What is Prometheus and how does it collect metrics?",
         "choices":["Prometheus pushes metrics to your service","Prometheus PULLS (scrapes) metrics from /metrics endpoints on your services at regular intervals — services passively expose metrics, Prometheus collects them",
                    "Prometheus stores logs","Prometheus is a tracing tool"],
         "answerIndex":1,"explanation":"Prometheus: pull-based. Your service exposes http://service/metrics (Prometheus text format). Prometheus scrapes every 15 seconds. Stores time series. PromQL for queries and alerts. Alternative: push-based like StatsD/CloudWatch where services send metrics to a collector.","tags":["observability","prometheus","metrics"]},
        {"id":"obs-q15","type":"mcq","prompt":"Should you alert when CPU > 80%?",
         "choices":["Yes, always alert on CPU","Cautiously — CPU is a cause not a symptom. Better: alert on user-impacting symptoms (high latency, error rate). CPU alert useful as a leading indicator but alone can cause alert fatigue without user impact.",
                    "Never alert on CPU","Alert only when CPU > 100%"],
         "answerIndex":1,"explanation":"CPU > 80% with latency = 20ms and error rate = 0%: users are unaffected. Paging someone for CPU that causes no user impact = alert fatigue. Better: alert on p99 > 1s or error rate > 1%. Add CPU as a supporting diagnostic metric, not the primary alert condition.","tags":["observability","alerting","cpu"]},
        {"id":"obs-q16","type":"mcq","prompt":"What is the difference between Loki and Elasticsearch for log storage?",
         "choices":["They are identical","Elasticsearch: full-text indexes every word in every log (powerful search, very expensive storage). Loki: stores compressed log streams with label-based indexing (cheap, query by labels + time range but slower full-text search)",
                    "Loki is older","Elasticsearch doesn't store logs"],
         "answerIndex":1,"explanation":"ES: indexes every token -> fast any-field search but expensive (3-5x raw log storage). Loki (Grafana): labels (app=order-service, level=ERROR) + compressed chunks = 10x cheaper. Query: show ERROR logs for order-service. Not: full-text 'find any log containing NullPointerException' (slower in Loki).","tags":["observability","loki","elasticsearch"]},
        {"id":"obs-q17","type":"mcq","prompt":"What is a health check endpoint and why is it important for observability?",
         "choices":["An endpoint that returns server CPU usage","An HTTP endpoint (usually /health or /ready) that returns 200 if service is healthy — used by load balancers, Kubernetes liveness/readiness probes, and monitoring systems",
                    "An endpoint for logging","A metrics endpoint"],
         "answerIndex":1,"explanation":"Health endpoint: load balancer pings /health every 5s. If unhealthy: stops sending traffic. Kubernetes: /ready returns 200 only when DB connection established. /health returns 200 if process is alive. Without health endpoint: load balancer sends traffic to crashed instances.","tags":["observability","health-check","reliability"]},
        {"id":"obs-q18","type":"mcq","prompt":"What is a Dead Letter Queue (DLQ) metric you should alert on?",
         "choices":["DLQ message count > 0 means messages are failing to process — should alert immediately as messages may be lost or indicate a consumer bug",
                    "DLQ depth < 100 is normal","DLQs should not be monitored","DLQ metrics are only for SQS"],
         "answerIndex":0,"explanation":"DLQ > 0 = messages failing after all retries. This means: data that should have been processed wasn't. Business impact: emails not sent, payments not processed, inventory not updated. Alert immediately on DLQ depth > 0. Investigate cause (consumer bug, bad data format, downstream outage).","tags":["observability","dlq","alerting"]},
        {"id":"obs-q19","type":"mcq","prompt":"What is the 'Fluentd sidecar' pattern in Kubernetes?",
         "choices":["A Kubernetes controller","A sidecar container running Fluentd alongside the app container in the same Pod — reads app log files and ships them to centralised log storage (ES, Loki, CloudWatch)",
                    "A debug tool","A metrics exporter"],
         "answerIndex":1,"explanation":"App container writes logs to /var/log/app.log. Fluentd sidecar reads same mounted volume, parses, ships to Elasticsearch. App doesn't need logging SDK. Platform team manages the sidecar. Alternative: DaemonSet Fluentd (one per node, reads all pod logs from node).","tags":["observability","kubernetes","fluentd","sidecar"]},
        {"id":"obs-q20","type":"mcq","prompt":"What information should every ERROR log entry contain?",
         "choices":["Just the error message","Timestamp, log level, service name, request/correlation ID, user context (userId if available), operation that failed, error message, and exception stack trace",
                    "Only the stack trace","Error code only"],
         "answerIndex":1,"explanation":"Good ERROR log: {timestamp, level:ERROR, service:order-svc, traceId:abc, userId:123, action:checkout, orderId:456, error:card_declined, exception:...stack trace...}. Bad ERROR log: 'Something went wrong'. Without context, you cannot reproduce or investigate the failure.","tags":["logging","error-logging","best-practices"]},
    ]

    NEW_FC = [
        {"id":"obs-fc1","front":"Three pillars of observability","back":"Logs: discrete events with context (what happened). Metrics: numerical measurements over time (how it's doing). Traces: request journey across services (how it flowed). Need all three for complete observability. Each answers different questions.","tags":["observability","three-pillars"]},
        {"id":"obs-fc2","front":"Four Golden Signals","back":"Latency (p99, not average). Traffic (requests/sec). Errors (5xx rate, exception rate). Saturation (CPU%, memory%, queue depth, DB connections%). Alert on these — they directly measure user experience.","tags":["observability","golden-signals"]},
        {"id":"obs-fc3","front":"Log level guide","back":"FATAL: system cannot continue, page now. ERROR: operation failed, user affected, investigate. WARN: recoverable anomaly, watch trend. INFO: normal business events. DEBUG: dev only, never production. TRACE: extreme detail, never production.","tags":["logging","log-levels"]},
        {"id":"obs-fc4","front":"SLI vs SLO vs SLA","back":"SLI = what you measure (99.5% requests < 300ms). SLO = internal target (99.9% availability). SLA = customer contract with penalty (99.9% or refund). Set SLO > SLA for safety margin. Error budget = 100% - SLO.","tags":["observability","sli","slo","sla"]},
        {"id":"obs-fc5","front":"Correlation ID pattern","back":"Assign UUID to each request at entry point. Pass in X-Request-ID header to every downstream service. Log it in every service. To debug: grep for ID across all services = complete request journey in seconds. Without it: impossible to trace microservice calls.","tags":["observability","correlation-id"]},
        {"id":"obs-fc6","front":"Alert on symptoms not causes","back":"Bad: CPU > 80% (cause). Good: p99 latency > 1s, HTTP 5xx > 1%, checkout success < 99.5% (symptoms = user impact). Causes are useful diagnostics, not primary alerts. Symptom-based alerting: only page when users are actually affected.","tags":["observability","alerting"]},
        {"id":"obs-fc7","front":"Prometheus vs managed alternatives","back":"Prometheus + Grafana: self-hosted, free, full control, needs maintenance. CloudWatch: AWS managed, zero ops, works with Lambda/EC2/RDS auto, more expensive at scale. Datadog/New Relic: SaaS, all-in-one (logs+metrics+traces), most expensive, least ops.","tags":["observability","prometheus","cloudwatch"]},
        {"id":"obs-fc8","front":"Distributed tracing flow","back":"1. Entry point generates trace_id. 2. Pass in headers to all downstream calls (X-B3-TraceId, traceparent). 3. Each service creates spans (start, end, parent). 4. Jaeger/Zipkin reconstructs flame graph. OpenTelemetry = vendor-neutral SDK standard.","tags":["observability","tracing","opentelemetry"]},
    ]

    d['guide'] = GUIDE
    d['questions'] = NEW_Q
    d['flashcards'] = NEW_FC
    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"error-logging.json: guide={len(GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ── patch_sqs.py ──────────────────────────────────────────────────────────────────
    p = Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics/cloud-devops/aws-sqs.json')
    d = json.loads(p.read_text())

    GUIDE = "\n".join([
        "# AWS SQS — Simple Queue Service",
        "",
        "## What Is a Message Queue? (Start From Zero)",
        "",
        "Imagine a busy coffee shop. Customers walk in and place orders. If the barista had to",
        "serve each customer instantly with no waiting — one slow customer blocks everyone else.",
        "Instead: customers place orders at the register (a queue), the order ticket goes on a",
        "board, and baristas pick up tickets when they are ready. The register does not wait",
        "for the coffee to be made before taking the next order.",
        "",
        "A **message queue** does the same for software services.",
        "",
        "**Without a queue (tight coupling):**",
        "```",
        "User clicks 'Place Order'",
        "    |",
        "    v",
        "Order Service calls Payment Service directly",
        "    |",
        "    | (waits synchronously)",
        "    v",
        "Payment Service calls Email Service directly",
        "    |",
        "    | (waits synchronously)",
        "    v",
        "Response returned to user",
        "",
        "Problem: if Email Service is slow or down, the user waits. If Payment Service is",
        "overwhelmed (Black Friday spike), Order Service fails too.",
        "```",
        "",
        "**With SQS (loose coupling):**",
        "```",
        "User clicks 'Place Order'",
        "    |",
        "    v",
        "Order Service puts message in SQS queue",
        "    |",
        "    v (immediate response to user: 'Order received!')",
        "User gets response",
        "",
        "Meanwhile, asynchronously:",
        "SQS queue -> Payment Service picks up message, processes it",
        "SQS queue -> Email Service picks up message, sends confirmation",
        "",
        "If Email Service crashes: message stays in queue, retried when it recovers.",
        "Spike of 10,000 orders: queue absorbs all of them, workers process at their pace.",
        "```",
        "",
        "---",
        "",
        "## SQS Core Concepts",
        "",
        "```",
        "PRODUCER:  Service that sends messages to the queue",
        "           (your Order Service)",
        "",
        "MESSAGE:   JSON payload, up to 256KB",
        "           {orderId: 'abc123', userId: 'u456', amount: 49.99}",
        "",
        "QUEUE:     Durable buffer storing messages until consumed",
        "           Messages can wait from seconds to 14 days",
        "",
        "CONSUMER:  Service that reads (polls) messages from the queue",
        "           (your Payment Service, Email Service)",
        "",
        "VISIBILITY TIMEOUT:",
        "   When consumer picks up a message, it becomes INVISIBLE to other consumers.",
        "   If consumer processes successfully: deletes the message (gone forever).",
        "   If consumer crashes (no delete): timeout expires, message reappears for retry.",
        "",
        "Message lifecycle:",
        "  SENT -> [Queue] -> RECEIVED (invisible for 30s default) -> DELETED",
        "                                         |",
        "                              (crash, no delete)",
        "                                         v",
        "                              Reappears after visibility timeout",
        "                              Retried by another consumer",
        "```",
        "",
        "---",
        "",
        "## Standard Queue vs FIFO Queue",
        "",
        "```",
        "+------------------+----------------------------+----------------------------+",
        "| Feature          | Standard Queue             | FIFO Queue                 |",
        "+------------------+----------------------------+----------------------------+",
        "| Ordering         | Best-effort ordering       | Strict FIFO (guaranteed)   |",
        "| Delivery         | At-least-once (duplicates) | Exactly-once processing    |",
        "| Throughput       | Unlimited (~infinite)      | Up to 3000 msg/sec         |",
        "| Use case         | Most tasks (email, logs)   | Financial txns, ordering   |",
        "| Naming           | any-name                   | must end in .fifo          |",
        "+------------------+----------------------------+----------------------------+",
        "",
        "Standard: A message MIGHT be delivered twice (at-least-once).",
        "  Your consumer MUST be idempotent (safe to process twice).",
        "",
        "FIFO: Message delivered exactly once in the order sent.",
        "  Use for: bank transfers, inventory updates, anything where order matters.",
        "",
        "When to use which:",
        "  Standard: sending emails (duplicate = extra email, annoying but ok)",
        "  FIFO:     charging a credit card (duplicate = double charge, unacceptable)",
        "```",
        "",
        "---",
        "",
        "## Key SQS Settings",
        "",
        "```",
        "VISIBILITY TIMEOUT (default: 30 seconds):",
        "  Time a message is invisible after being received.",
        "  Set to > your max processing time.",
        "  If processing takes 2 min but timeout is 30s: message reappears, processed twice!",
        "  Rule: set visibility timeout = 6x your average processing time.",
        "",
        "MESSAGE RETENTION PERIOD (default: 4 days, max: 14 days):",
        "  How long unprocessed messages stay in the queue.",
        "  After this period, messages are automatically deleted.",
        "",
        "MESSAGE SIZE (max: 256KB):",
        "  For larger payloads: store data in S3, send only the S3 key in SQS.",
        "  SQS Extended Client Library (Java/Python) handles this pattern.",
        "",
        "DELIVERY DELAY (default: 0, max: 15 minutes):",
        "  Messages become invisible for N seconds after sent.",
        "  Use: delay an action (send invoice email 5 min after order).",
        "",
        "LONG POLLING vs SHORT POLLING:",
        "  Short polling: consumer calls ReceiveMessage, AWS checks a subset of servers.",
        "                 May return empty even if messages exist. More API calls = higher cost.",
        "  Long polling:  consumer waits up to 20 seconds for a message to arrive.",
        "                 Fewer empty responses. Lower cost. Use long polling (WaitTimeSeconds=20).",
        "```",
        "",
        "---",
        "",
        "## Dead Letter Queue (DLQ)",
        "",
        "```",
        "WHAT IS A DLQ?",
        "  A separate SQS queue for messages that fail processing repeatedly.",
        "  Instead of retrying forever, after N failures the message goes to the DLQ.",
        "",
        "WHY USE IT?",
        "  Without DLQ: a poison pill message (one your code cannot process) retries",
        "  forever, blocking other messages and generating noise in logs.",
        "  With DLQ: poison pill is isolated, other messages are unaffected.",
        "",
        "SETUP:",
        "  Create a separate SQS queue: my-queue-dlq",
        "  Set on main queue: Redrive Policy:",
        "    maxReceiveCount: 3   (fail 3 times -> move to DLQ)",
        "    deadLetterTargetArn: arn:...:my-queue-dlq",
        "",
        "WORKFLOW:",
        "  Message arrives -> Consumer processes -> FAILS",
        "  Message reappears (visibility timeout expires)",
        "  Consumer tries again -> FAILS (receive count = 2)",
        "  Consumer tries again -> FAILS (receive count = 3 = maxReceiveCount)",
        "  Message moves to DLQ -> alert fires -> engineer investigates",
        "",
        "WHAT TO DO WITH DLQ MESSAGES?",
        "  - Investigate root cause (bad data? bug in consumer?)",
        "  - Fix the bug",
        "  - Replay messages back to main queue",
        "  - AWS Console: DLQ Redrive feature does this automatically",
        "```",
        "",
        "---",
        "",
        "## Lambda + SQS — The Most Common Pattern",
        "",
        "```",
        "Lambda can consume SQS messages as an event source mapping.",
        "Lambda polls the queue automatically — you don't write polling code.",
        "",
        "Architecture:",
        "  Producer -> SQS Queue -> Lambda (auto-scales with queue depth)",
        "",
        "Event source mapping behaviour:",
        "  Lambda polls the queue in batches (default: 10 messages per invocation)",
        "  If Lambda succeeds: SQS deletes all messages in the batch",
        "  If Lambda fails: ALL messages in batch reappear (retry)",
        "",
        "BATCH SIZE:",
        "  Small batch (1): easy partial failure handling, more Lambda invocations",
        "  Large batch (10): fewer invocations (cheaper), harder partial failure",
        "",
        "PARTIAL BATCH FAILURE:",
        "  Lambda processes messages 1-10. Message 7 fails. Others succeed.",
        "  Without partial failure handling: all 10 retry (messages 1-6, 8-10 re-processed!)",
        "  With batchItemFailures response: return only failed message IDs to retry:",
        "",
        "  def handler(event, context):",
        "      failures = []",
        "      for record in event['Records']:",
        "          try:",
        "              process(record)",
        "          except Exception as e:",
        "              failures.append({'itemIdentifier': record['messageId']})",
        "      return {'batchItemFailures': failures}",
        "",
        "Concurrency:",
        "  Lambda scales one concurrent execution per active message group (FIFO)",
        "  or up to 1000 concurrency for standard queues.",
        "  Set Lambda reserved concurrency to cap downstream DB load.",
        "```",
        "",
        "---",
        "",
        "## SQS vs SNS vs EventBridge",
        "",
        "```",
        "+------------------+----------------------+------------------------+",
        "| Feature          | SQS                  | SNS                    |",
        "+------------------+----------------------+------------------------+",
        "| Model            | Queue (pull-based)   | Topic (push-based)     |",
        "| Consumers        | One consumer group   | Multiple subscribers   |",
        "| Persistence      | Messages wait        | Fire and forget        |",
        "| Retry            | Built-in (visibility)| No retry by default    |",
        "| Use case         | Work queue           | Fan-out notifications  |",
        "+------------------+----------------------+------------------------+",
        "",
        "COMMON PATTERN: SNS + SQS fan-out:",
        "  OrderPlaced event -> SNS topic",
        "  SNS fans out to:",
        "    SQS queue 1 -> Email Lambda (send confirmation)",
        "    SQS queue 2 -> Inventory Lambda (reserve stock)",
        "    SQS queue 3 -> Analytics Lambda (record sale)",
        "  Each service gets its own queue, processes independently.",
        "  One service slow/down doesn't affect others.",
        "",
        "EventBridge vs SQS:",
        "  SQS: work queue, exact delivery, backpressure, retry, DLQ",
        "  EventBridge: event routing with rules, multiple targets, schema registry",
        "  Use SQS for work distribution, EventBridge for event-driven reactions",
        "```",
        "",
        "---",
        "",
        "## Mind Map",
        "",
        "```",
        "AWS SQS",
        "|",
        "+-- CORE CONCEPTS",
        "|   +-- Producer sends messages",
        "|   +-- Queue buffers messages",
        "|   +-- Consumer polls and deletes",
        "|   +-- Visibility timeout = processing lease",
        "|",
        "+-- QUEUE TYPES",
        "|   +-- Standard: high throughput, at-least-once, best-effort order",
        "|   +-- FIFO: strictly ordered, exactly-once, lower throughput",
        "|",
        "+-- KEY SETTINGS",
        "|   +-- Visibility timeout (>6x processing time)",
        "|   +-- Message retention (4 days default, 14 max)",
        "|   +-- Long polling (WaitTimeSeconds=20)",
        "|   +-- Delivery delay",
        "|",
        "+-- DLQ",
        "|   +-- maxReceiveCount retries then -> DLQ",
        "|   +-- Isolates poison pill messages",
        "|   +-- DLQ Redrive to replay fixed messages",
        "|",
        "+-- LAMBDA INTEGRATION",
        "|   +-- Event source mapping (auto-poll + scale)",
        "|   +-- Batch size (1-10000)",
        "|   +-- Partial batch failure response",
        "|",
        "+-- PATTERNS",
        "    +-- Work queue (producer -> SQS -> Lambda workers)",
        "    +-- Fan-out (SNS -> multiple SQS -> multiple Lambdas)",
        "    +-- Backpressure buffer (absorb traffic spikes)",
        "```",
        "",
        "---",
        "",
        "## How SQS Connects to Other Topics",
        "",
        "- **Lambda**: Lambda's event source mapping consumes SQS automatically.",
        "  Lambda + SQS is the most common async processing pattern in serverless.",
        "- **SNS**: SNS fan-out -> SQS queues = multiple independent consumers of same event.",
        "- **Serverless Patterns**: SQS absorbs traffic spikes, Lambda workers scale to drain queue.",
        "- **Kafka vs SQS**: Kafka retains messages for days and supports replay.",
        "  SQS is simpler (managed, no cluster), Kafka is more powerful for streaming.",
        "",
        "---",
        "",
        "## Common Beginner Mistakes",
        "",
        "1. **Visibility timeout too short** — message reappears while still being processed -> double processing.",
        "2. **No DLQ** — poison pill messages retry forever, filling logs and blocking workers.",
        "3. **Not using long polling** — short polling wastes API calls and costs more.",
        "4. **FIFO when not needed** — FIFO has lower throughput limits. Use Standard unless order/deduplication is required.",
        "5. **Large messages in SQS** — 256KB limit. Store large payloads in S3, send S3 key in SQS.",
        "6. **Not handling partial batch failure** — one bad message in batch causes all messages to retry.",
        "7. **Assuming Standard queue deduplicates** — it does NOT. Your consumer must be idempotent.",
        "",
        "---",
        "",
        "## References and Further Learning",
        "",
        "### Videos (Watch These!)",
        "- **Amazon SQS Tutorial** by TechWorld with Nana:",
        "  https://www.youtube.com/watch?v=CyYZ3adwboc",
        "  - 45 minutes. SQS concepts, demo, Lambda integration.",
        "- **SQS vs SNS vs EventBridge** by Be A Better Dev:",
        "  https://www.youtube.com/watch?v=RoKAEzdcr7k",
        "  - Clear comparison of the three AWS messaging services.",
        "",
        "### Free Books and Articles",
        "- **AWS SQS Developer Guide**: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/",
        "- **Lambda + SQS event source mapping**: https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html",
        "",
        "### Diagrams",
        "- **SNS + SQS fan-out diagram**: search 'AWS SNS SQS fan-out diagram' on Google Images",
        "",
        "### Practice",
        "- **AWS Free Tier**: SQS is free for first million requests/month. Build and test locally.",
        "- **LocalStack**: https://localstack.cloud/ — run AWS services locally including SQS.",
    ])

    NEW_Q = [
        {"id":"aws-sqs-q1-real","type":"mcq","prompt":"What problem does SQS solve in a microservices architecture?",
         "choices":["Stores application code","Provides a managed message queue that decouples producers from consumers — producers send at their pace, consumers process at their pace, no direct dependency",
                    "Hosts Lambda functions","Manages IAM policies"],
         "answerIndex":1,"explanation":"SQS decouples services. Producer (Order Service) sends to queue and returns immediately. Consumer (Payment Service) processes when ready. If consumer is slow or down, messages wait in queue rather than failing the producer.","tags":["sqs","decoupling"]},
        {"id":"aws-sqs-q2-real","type":"mcq","prompt":"What is the SQS visibility timeout?",
         "choices":["How long messages are retained in the queue","The time a received message is hidden from other consumers while being processed — prevents duplicate processing",
                    "The delay before a message is delivered","Maximum message size"],
         "answerIndex":1,"explanation":"When consumer A receives a message, it becomes invisible for the visibility timeout period. If A processes and deletes it before timeout: gone. If A crashes: timeout expires, message reappears for consumer B to retry.","tags":["sqs","visibility-timeout"]},
        {"id":"aws-sqs-q3-real","type":"mcq","prompt":"Standard SQS queue guarantees 'at-least-once delivery'. What does this mean for your consumer?",
         "choices":["Messages are never delivered twice","Your consumer must be idempotent — the same message may be delivered more than once and processing it twice must produce the same result",
                    "Messages are guaranteed to arrive in order","You must acknowledge each message twice"],
         "answerIndex":1,"explanation":"Standard SQS can deliver duplicates. A consumer processing 'charge user $10' twice would double-charge. Idempotent design: check if this requestId was already processed. If yes, skip. FIFO queues offer exactly-once delivery.","tags":["sqs","at-least-once","idempotency"]},
        {"id":"aws-sqs-q4-real","type":"mcq","prompt":"When should you use a FIFO queue instead of a Standard queue?",
         "choices":["When you need maximum throughput","When message order and exactly-once delivery are required — financial transactions, ordered inventory updates",
                    "For large messages","FIFO is always better"],
         "answerIndex":1,"explanation":"FIFO queues guarantee ordering and exactly-once delivery but cap at 3000 msg/sec. Standard handles virtually unlimited throughput but may deliver out of order and duplicate. Choose FIFO only when order/dedup are business requirements.","tags":["sqs","fifo","standard"]},
        {"id":"aws-sqs-q5-real","type":"mcq","prompt":"What is a Dead Letter Queue (DLQ)?",
         "choices":["A queue for low-priority messages","A queue that receives messages which have failed processing maxReceiveCount times — isolates poison pill messages and prevents infinite retry loops",
                    "A backup queue","Queue for deleted messages"],
         "answerIndex":1,"explanation":"DLQ catches messages that repeatedly fail. After maxReceiveCount retries, the message moves to DLQ instead of retrying forever. Engineers investigate, fix the bug, and replay messages from DLQ.","tags":["sqs","dlq"]},
        {"id":"aws-sqs-q6-real","type":"mcq","prompt":"Your SQS consumer takes 45 seconds to process a message. What visibility timeout should you set?",
         "choices":["30 seconds (default)","10 seconds","At least 270 seconds (6x processing time is the recommended minimum)",
                    "180 seconds exactly"],
         "answerIndex":2,"explanation":"If visibility timeout < processing time, the message reappears before processing is done — another consumer picks it up = duplicate processing. Recommended: set to 6x average processing time. For 45s processing: 270s minimum.","tags":["sqs","visibility-timeout","configuration"]},
        {"id":"aws-sqs-q7-real","type":"mcq","prompt":"What is long polling in SQS?",
         "choices":["Waiting 24 hours for a message","Consumer waits up to 20 seconds for a message to arrive (WaitTimeSeconds=20) — reduces empty responses, fewer API calls, lower cost vs short polling",
                    "Sending very long messages","Polling from multiple regions"],
         "answerIndex":1,"explanation":"Short polling returns immediately even if empty — many wasted API calls. Long polling waits up to 20 seconds before returning empty. Dramatically reduces costs for queues with low/intermittent traffic. Always use long polling.","tags":["sqs","long-polling"]},
        {"id":"aws-sqs-q8-real","type":"mcq","prompt":"What happens to messages that exceed the SQS message retention period?",
         "choices":["They are moved to S3","They are moved to DLQ","They are permanently deleted from the queue automatically",
                    "They are archived"],
         "answerIndex":2,"explanation":"Default retention: 4 days. Maximum: 14 days. After retention period expires, messages are deleted regardless of whether they were consumed. Monitor queue depth to ensure consumers process faster than retention expires.","tags":["sqs","retention"]},
        {"id":"aws-sqs-q9-real","type":"mcq","prompt":"In the SNS + SQS fan-out pattern, what is the benefit of having one SQS queue per consumer?",
         "choices":["Reduces costs","Each consumer processes at its own pace independently — a slow Email service doesn't delay the Inventory service, and failures are isolated per service",
                    "Increases message throughput","Required by AWS"],
         "answerIndex":1,"explanation":"SNS publishes to multiple SQS queues. Each queue serves one consumer service. Service A slow? Its queue backs up but doesn't affect Service B. Service B crashes? Its messages wait in queue until it recovers. Complete isolation.","tags":["sqs","sns","fan-out"]},
        {"id":"aws-sqs-q10-real","type":"mcq","prompt":"What is the maximum message size in SQS?",
         "choices":["64KB","1MB","256KB","10MB"],
         "answerIndex":2,"explanation":"SQS messages are limited to 256KB. For larger payloads (images, documents): store in S3, send only the S3 object key in the SQS message. The SQS Extended Client Library (Java/Python) handles this S3 offload pattern automatically.","tags":["sqs","limits"]},
        {"id":"aws-sqs-q11-real","type":"mcq","prompt":"When Lambda is configured with SQS as an event source, what happens if Lambda fails to process a message batch?",
         "choices":["Messages are deleted","Messages are immediately moved to DLQ","All messages in the batch return to the queue (visibility timeout expires) and become available for retry",
                    "Lambda retries automatically without returning messages to queue"],
         "answerIndex":2,"explanation":"If Lambda throws an exception (or times out) while processing a batch, it does NOT delete the messages. After visibility timeout, all batch messages reappear. With partial batch failure response, only failed messages retry.","tags":["sqs","lambda","batch"]},
        {"id":"aws-sqs-q12-real","type":"mcq","prompt":"What is the purpose of the SQS message deduplication ID in FIFO queues?",
         "choices":["Authentication token","A unique ID for the message — within a 5-minute deduplication window, SQS ignores messages with the same ID, preventing duplicates",
                    "Message ordering key","Consumer ID"],
         "answerIndex":1,"explanation":"FIFO queues use MessageDeduplicationId to prevent duplicates. If you send two messages with the same dedup ID within 5 minutes, only the first is delivered. Use a hash of the message content or a UUID generated once and stored.","tags":["sqs","fifo","deduplication"]},
        {"id":"aws-sqs-q13-real","type":"mcq","prompt":"What is SQS message group ID used for in FIFO queues?",
         "choices":["Authentication","Messages with the same group ID are processed in FIFO order with one consumer at a time — enables parallelism across groups while maintaining per-group ordering",
                    "Message deduplication","Consumer targeting"],
         "answerIndex":1,"explanation":"MessageGroupId controls ordering scope. Group ID 'customer-123' ensures that customer's messages are ordered. Group ID 'customer-456' is handled independently in parallel. Without group IDs, all messages share one sequence (single consumer).","tags":["sqs","fifo","message-groups"]},
        {"id":"aws-sqs-q14-real","type":"mcq","prompt":"How does SQS help handle a traffic spike (e.g., Black Friday)?",
         "choices":["SQS rejects excess messages","SQS automatically scales the consumer service","SQS acts as a buffer — absorbs millions of messages instantly without dropping any, consumers drain the queue at their own rate rather than being overwhelmed",
                    "SQS charges extra for spikes"],
         "answerIndex":2,"explanation":"SQS queue depth grows during a spike. Consumers process at their capacity. No messages lost, no consumer crashes from being overwhelmed. Lambda event source mapping also auto-scales consumers to drain the queue faster.","tags":["sqs","backpressure","scaling"]},
        {"id":"aws-sqs-q15-real","type":"mcq","prompt":"What is the delivery delay feature in SQS?",
         "choices":["How long it takes to deliver across regions","A configured delay (0-15 minutes) before a newly sent message becomes visible to consumers — useful for deferred processing",
                    "Message retention period","DLQ retry delay"],
         "answerIndex":1,"explanation":"Delivery delay makes messages invisible for a specified time after they are sent. Use case: send order confirmation email 5 minutes after order placed, not immediately. Or: delay a retry after a known processing window.","tags":["sqs","delivery-delay"]},
        {"id":"aws-sqs-q16-real","type":"mcq","prompt":"What is the difference between SQS and Kafka for message queuing?",
         "choices":["They are identical","SQS: fully managed, messages deleted after consumption, simpler ops. Kafka: self-managed cluster, messages retained for replay, supports multiple consumer groups reading same data independently",
                    "Kafka is always better","SQS handles more messages"],
         "answerIndex":1,"explanation":"SQS: AWS manages everything, messages consumed and gone, great for work queues. Kafka: you run the cluster, messages persist for days/weeks enabling replay and multiple independent consumers reading the same stream. Choose Kafka for event streaming, SQS for task queues.","tags":["sqs","kafka","comparison"]},
        {"id":"aws-sqs-q17-real","type":"mcq","prompt":"What is partial batch failure response in Lambda + SQS?",
         "choices":["Lambda rejecting the entire batch","Lambda returns a batchItemFailures list with only failed message IDs — SQS retries only those messages, successfully processed messages are deleted",
                    "Lambda deleting all messages in batch","Lambda sending failed messages to SNS"],
         "answerIndex":1,"explanation":"Without partial failure: one bad message in a batch of 10 causes all 10 to retry — 9 messages re-processed unnecessarily. With batchItemFailures response: return only the failed messageId(s). SQS retries only those while deleting successful ones.","tags":["sqs","lambda","partial-failure"]},
        {"id":"aws-sqs-q18-real","type":"mcq","prompt":"How does Lambda auto-scaling work with an SQS event source mapping?",
         "choices":["Lambda doesn't auto-scale with SQS","Lambda scales one instance per message","Lambda poller scales Lambda concurrency based on queue depth — more messages in queue = more concurrent Lambda executions (up to account concurrency limit)",
                    "You must manually configure auto-scaling"],
         "answerIndex":2,"explanation":"SQS event source mapping automatically scales Lambda. As queue depth grows, Lambda concurrency scales up to drain messages faster. As queue empties, concurrency scales back down. Scales to zero when queue is empty.","tags":["sqs","lambda","scaling"]},
        {"id":"aws-sqs-q19-real","type":"mcq","prompt":"What is the recommended way to monitor SQS queue health in production?",
         "choices":["Check AWS Console manually","Configure CloudWatch alarm on ApproximateNumberOfMessagesNotVisible and ApproximateAgeOfOldestMessage — alert if queue backs up or messages age too long",
                    "Log every message","Use AWS X-Ray only"],
         "answerIndex":1,"explanation":"Key SQS CloudWatch metrics: ApproximateNumberOfMessages (depth), ApproximateAgeOfOldestMessage (how stale is oldest unprocessed message). Stale messages = consumer is stuck or dead. Set alarms on both for production queues.","tags":["sqs","monitoring","cloudwatch"]},
        {"id":"aws-sqs-q20-real","type":"mcq","prompt":"Why should you set Lambda reserved concurrency when using SQS as event source?",
         "choices":["To make Lambda run faster","Lambda can scale to account limits consuming SQS — without reserved concurrency, a spike could create thousands of Lambda executions that overwhelm downstream databases or APIs",
                    "Required by SQS FIFO","To reduce costs only"],
         "answerIndex":1,"explanation":"Unconstrained Lambda + SQS = Lambda scales to 1000+ concurrent executions during a spike. Your RDS database has 100 connection limit. Result: connection pool exhaustion, database crash. Set reserved concurrency = your downstream capacity.","tags":["sqs","lambda","concurrency","backpressure"]},
    ]

    NEW_FC = [
        {"id":"aws-sqs-fc1-real","front":"SQS visibility timeout rule","back":"Set to 6x your average processing time. Message in flight = invisible for this period. Too short = duplicate processing (message reappears while still being processed). Change during processing with ChangeMessageVisibility API.","tags":["sqs","visibility-timeout"]},
        {"id":"aws-sqs-fc2-real","front":"Standard vs FIFO queue choice","back":"Standard: unlimited throughput, at-least-once (may duplicate), best-effort ordering. FIFO: 3000/sec limit, exactly-once, strict order. Use Standard unless order or dedup is a business requirement (financial transactions = FIFO).","tags":["sqs","fifo","standard"]},
        {"id":"aws-sqs-fc3-real","front":"DLQ configuration","back":"Set maxReceiveCount = 3-5 on main queue. Create separate SQS as DLQ. After maxReceiveCount failures, message moves to DLQ. Alert on DLQ depth. Fix bug. Use DLQ Redrive to replay messages back to main queue.","tags":["sqs","dlq"]},
        {"id":"aws-sqs-fc4-real","front":"SNS + SQS fan-out pattern","back":"SNS topic receives event, fans out to N SQS queues. Each queue serves one independent consumer. Benefits: each service scales independently, failures are isolated, slow consumer doesn't block others. Default pattern for event-driven microservices.","tags":["sqs","sns","fan-out"]},
        {"id":"aws-sqs-fc5-real","front":"Lambda partial batch failure","back":"Return {batchItemFailures: [{itemIdentifier: failedMessageId}]}. SQS retries ONLY failed messages and deletes successful ones. Without this: entire batch retries when one message fails = 9 re-processed unnecessarily.","tags":["sqs","lambda","batch"]},
        {"id":"aws-sqs-fc6-real","front":"SQS long polling — always use it","back":"WaitTimeSeconds=20 in ReceiveMessage call. Waits up to 20s for a message. Compared to short polling: 99% fewer empty receives, lower cost, same latency. Turn on in queue settings (ReceiveMessageWaitTimeSeconds=20).","tags":["sqs","long-polling"]},
        {"id":"aws-sqs-fc7-real","front":"SQS max message size workaround","back":"SQS limit = 256KB. For large payloads: store in S3, put S3 object key in SQS message. Consumer reads key, fetches from S3. SQS Extended Client Library (Java/Python) automates this pattern transparently.","tags":["sqs","limits","s3"]},
        {"id":"aws-sqs-fc8-real","front":"SQS backpressure pattern","back":"Traffic spike: producer sends 100K messages faster than consumers can process. SQS absorbs all (no messages lost). Consumers drain at their pace. Lambda scales up to drain faster. Cap Lambda concurrency = protect downstream DB from connection storm.","tags":["sqs","backpressure","scaling"]},
    ]

    d['guide'] = GUIDE
    d['questions'] = NEW_Q
    d['flashcards'] = NEW_FC

    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"aws-sqs.json done: guide={len(GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

if __name__ == '__main__':
    main()
