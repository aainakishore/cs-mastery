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

