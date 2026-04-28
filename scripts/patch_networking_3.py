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

