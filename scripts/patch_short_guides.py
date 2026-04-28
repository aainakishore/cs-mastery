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

# ─── NETWORKING ───────────────────────────────────────────────────────────────

patch(BASE / "networking/websockets.json",
      guide="""# WebSockets

WebSockets provide a **persistent, full-duplex TCP-based channel** between client and server over a single connection. Unlike HTTP's request-response cycle, either party can send messages at any time.

## The HTTP vs WebSocket Contrast

```
HTTP (request-response):           WebSocket (persistent):
Client → GET /data → Server        Client ──────────────── Server
Server ← 200 OK ← Server           Client ←──────────────→ Server
                                    (open bidirectional pipe)
```

## WebSocket Handshake (HTTP Upgrade)

```
Client sends HTTP request:
  GET /chat HTTP/1.1
  Host: example.com
  Upgrade: websocket
  Connection: Upgrade
  Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
  Sec-WebSocket-Version: 13

Server responds:
  HTTP/1.1 101 Switching Protocols
  Upgrade: websocket
  Connection: Upgrade
  Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=

After this, TCP connection stays open for WebSocket frames.
```

## Frame Structure

```
Each WebSocket message = one or more frames:
  ┌─────┬─────┬────────────────────────────────────────┐
  │ FIN │ Opcode │ Payload length │ [Masking key] │ Payload │
  └─────┴─────┴────────────────────────────────────────┘

Opcodes: 0x0=continuation, 0x1=text, 0x2=binary, 0x8=close, 0x9=ping, 0xA=pong
Client → Server: frames are masked (required by spec)
Server → Client: frames are unmasked
```

## JavaScript API

```javascript
const ws = new WebSocket('wss://chat.example.com/ws');

ws.onopen    = () => ws.send(JSON.stringify({ type: 'join', room: 'general' }));
ws.onmessage = (event) => console.log('Received:', JSON.parse(event.data));
ws.onerror   = (error) => console.error('WS error:', error);
ws.onclose   = (event) => console.log('Closed:', event.code, event.reason);

// Send types:
ws.send('text string');
ws.send(new Blob([...]) );
ws.send(new ArrayBuffer(8));

// Close gracefully:
ws.close(1000, 'Normal closure');
```

## Server-Side (Node.js Example)

```javascript
const { WebSocketServer } = require('ws');
const wss = new WebSocketServer({ port: 8080 });

wss.on('connection', (ws, req) => {
  console.log('Client connected:', req.socket.remoteAddress);

  ws.on('message', (data) => {
    // Broadcast to all connected clients
    wss.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(data.toString());
      }
    });
  });

  ws.on('close', (code, reason) => console.log(`Closed: ${code} ${reason}`));
  ws.on('error', (err) => console.error('WS error:', err));

  // Keep-alive heartbeat
  const interval = setInterval(() => ws.ping(), 30000);
  ws.on('close', () => clearInterval(interval));
});
```

## When to Use WebSockets

| Use WebSocket | Use HTTP/SSE instead |
|---|---|
| Real-time chat | One-way server push (news feed) |
| Multiplayer games | Simple notifications |
| Collaborative editing | Large file downloads |
| Live trading data | Infrequent updates |
| IoT sensor streams | CRUD APIs |

## Common Pitfalls
- **Not handling reconnection** — WebSockets don't auto-reconnect. Implement exponential backoff on `onclose`.
- **Missing heartbeat/ping-pong** — idle connections dropped by proxies. Send ping frames every 30s.
- **Memory leaks from unclosed connections** — always clean up intervals and listeners on close.
- **Scaling without sticky sessions** — WS connections are stateful; a load balancer needs to route the same client to the same server, or use a message bus (Redis pub/sub) to broadcast across nodes.
- **Sending before open** — check `ws.readyState === WebSocket.OPEN` before sending.

## Connections
- **SSE** — simpler alternative for one-way server push (no client→server messages needed)
- **HTTP/3 QUIC** — faster initial connection but different model
- **Load balancing** — sticky sessions or shared pub/sub required for horizontal scaling
""",
      questions=[
          {"id":"ws-q1","type":"mcq","prompt":"WebSocket vs HTTP: the key architectural difference?","choices":["WebSocket is faster","WebSocket creates a persistent bidirectional TCP connection — either party can send at any time without a new request","WebSocket only works over SSL","WebSocket is for file transfers"],"answerIndex":1,"explanation":"HTTP is request-response (client always initiates). WebSocket upgrades to a persistent connection where both sides push data freely.","tags":["websockets"]},
          {"id":"ws-q2","type":"mcq","prompt":"How does a WebSocket connection start?","choices":["Via TCP handshake directly","Via an HTTP Upgrade request — client asks server to switch from HTTP to WebSocket protocol","Via UDP","Via WebRTC signaling"],"answerIndex":1,"explanation":"WebSocket starts with an HTTP GET with 'Upgrade: websocket' header. Server responds 101 Switching Protocols, then TCP is repurposed for WS frames.","tags":["websockets","handshake"]},
          {"id":"ws-q3","type":"mcq","prompt":"Why do WebSockets require sticky sessions or a message bus for horizontal scaling?","choices":["WS only works on single servers","WS connections are stateful — a client connects to ONE server instance. Messages sent to a different instance won't reach that client unless shared via a bus (Redis pub/sub)","WS uses too much bandwidth","Load balancers can't handle WebSockets"],"answerIndex":1,"explanation":"Each WebSocket connection is stateful — maintained on the specific server. To broadcast to all clients across multiple servers, use Redis pub/sub or a message queue as a shared channel.","tags":["websockets","scaling"]},
          {"id":"ws-q4","type":"mcq","prompt":"What happens if you don't send ping/pong heartbeats on an idle WebSocket?","choices":["Nothing — connections stay open indefinitely","Proxies and firewalls may close idle connections after a timeout (typically 60-300s) — heartbeats keep the connection alive","The server closes it after 10s","ping/pong is optional and rarely needed"],"answerIndex":1,"explanation":"Many proxies, load balancers, and firewalls close seemingly-idle TCP connections. Ping frames (opcode 0x9) and pong responses confirm the connection is alive.","tags":["websockets","heartbeat"]},
          {"id":"ws-q5","type":"mcq","prompt":"When is HTTP Server-Sent Events (SSE) a better choice than WebSocket?","choices":["SSE is always better","When you only need server → client messages (news feed, notifications) — SSE is simpler, works over HTTP/2, auto-reconnects","SSE has higher throughput","SSE supports binary data better"],"answerIndex":1,"explanation":"SSE is one-directional (server→client only) but simpler: uses regular HTTP, auto-reconnects, works through proxies without upgrade. WebSocket adds complexity only justified when the client also sends frequent messages.","tags":["websockets","SSE","comparison"]},
      ],
      flashcards=[
          {"id":"ws-fc1","front":"WebSocket handshake","back":"HTTP GET with Upgrade: websocket header. Server responds 101 Switching Protocols. Same TCP connection then carries WS frames — no new connections per message.","tags":["websockets"]},
          {"id":"ws-fc2","front":"WebSocket scaling challenge","back":"Connections are stateful — tied to one server instance. Horizontal scaling needs: sticky sessions (route same client to same server) OR message bus (Redis pub/sub) to broadcast across instances.","tags":["websockets","scaling"]},
          {"id":"ws-fc3","front":"Heartbeat / ping-pong","back":"Proxies drop idle connections. Send ws.ping() every 30s. Server pongs back automatically. Client detects close if pong not received within timeout. Essential for production WS.","tags":["websockets"]},
          {"id":"ws-fc4","front":"WebSocket vs SSE","back":"WebSocket: bidirectional, binary capable, requires upgrade. SSE: server→client only, plain HTTP/2, auto-reconnect. Choose SSE for one-way push; WebSocket when client also sends data.","tags":["websockets","SSE"]},
      ])

patch(BASE / "networking/ftp.json",
      guide="""# FTP — File Transfer Protocol

FTP (RFC 959) is a **dual-channel TCP protocol** for transferring files. It uses separate **control** and **data** connections on ports 21 and 20 respectively.

## The Dual-Channel Design

```
Active Mode:
  Client port 21  ←──── Control ─────→  Server port 21
  Client port N   ←── Data (server initiates) ← Server port 20
  (Server dials BACK to client — blocked by NAT/firewalls)

Passive Mode (PASV):
  Client port 21  ←──── Control ─────→  Server port 21
  Client          ──── Data ──────────→  Server ephemeral port
  (Client initiates data — works through NAT)

Modern deployments use PASV (passive mode) almost exclusively.
```

## Command flow

```
Client              Server
  │ ── 220 ready ──→  │
  │ ← USER alice  ─── │
  │ ── 331 pwd req ─→ │
  │ ← PASS secret ─── │
  │ ── 230 logged in → │
  │ ← LIST /uploads ── │   (active: server connects back; passive: client opens data conn)
  │ ── 150 opening ─→  │
  │ ─── file listing ─→ │
  │ ── 226 transfer OK ─→ │
  │ ← QUIT ─────────── │
```

## FTP vs SFTP vs FTPS

| Protocol | Port | Security | Transport |
|---|---|---|---|
| FTP | 21/20 | None — credentials and data in plaintext | TCP |
| FTPS | 21/990 | TLS/SSL wrapping FTP | TCP |
| SFTP | 22 | SSH-based — completely different protocol | SSH |

**FTP is insecure** — never use it over public networks. SFTP (via SSH) is the modern replacement.

## Common Pitfalls
- **Active mode blocked by firewalls/NAT** — server tries to connect back to the client, which is typically behind NAT. Always configure PASV mode.
- **Credentials in plaintext** — FTP sends username/password as clear text. Use SFTP or FTPS.
- **Firewall port ranges** — PASV uses random high ports; configure the server's PASV port range AND open those ports on the firewall.
""",
      questions=[
          {"id":"ftp-q1","type":"mcq","prompt":"Why does active mode FTP fail behind NAT/firewalls?","choices":["FTP doesn't support NAT","In active mode the server initiates the data connection back to the client — NAT blocks incoming connections the client didn't initiate","Active mode uses UDP","Port 21 is blocked"],"answerIndex":1,"explanation":"Active mode: server dials the client's ephemeral port for data. NAT translates client addresses — the server can't reach the client. Passive mode: client initiates both connections, solving the NAT problem.","tags":["ftp","active-passive"]},
          {"id":"ftp-q2","type":"mcq","prompt":"Main security difference between FTP and SFTP?","choices":["SFTP is faster","FTP sends credentials and data in plaintext. SFTP runs over SSH — everything is encrypted","SFTP uses TLS","FTP supports authentication; SFTP doesn't"],"answerIndex":1,"explanation":"FTP has no built-in encryption. SFTP is a completely different protocol built on SSH — all data (including passwords) is encrypted. FTPS wraps FTP in TLS but is more complex to configure through firewalls.","tags":["ftp","security"]},
          {"id":"ftp-q3","type":"mcq","prompt":"FTP uses how many TCP connections?","choices":["One","Two — a control channel (port 21) and a separate data channel (port 20 or ephemeral)","Three — control, data, and heartbeat","One per file"],"answerIndex":1,"explanation":"FTP's dual-channel design: control channel (commands/responses on port 21) stays open for the session. Data channel opens and closes for each file transfer or directory listing.","tags":["ftp","architecture"]},
      ],
      flashcards=[
          {"id":"ftp-fc1","front":"FTP active vs passive mode","back":"Active: server initiates data connection back to client (blocked by NAT). Passive (PASV): client initiates both connections — works through NAT/firewalls. Always use PASV in production.","tags":["ftp"]},
          {"id":"ftp-fc2","front":"FTP vs SFTP vs FTPS","back":"FTP: plaintext, dual TCP, legacy. FTPS: FTP + TLS/SSL. SFTP: SSH-based, encrypted, single connection, modern standard. Use SFTP. Never use plain FTP over public networks.","tags":["ftp","security"]},
      ])

patch(BASE / "networking/firewalls.json",
      guide="""# Firewalls

A firewall is a **network security device** (hardware or software) that monitors and controls incoming/outgoing network traffic based on rules. It's the primary boundary between trusted internal networks and untrusted external networks.

## Types of Firewalls

```
Packet Filter (L3/L4):
  Inspects IP headers + TCP/UDP ports only
  Fast, stateless, no session context
  Rule: ALLOW TCP src any dst 10.0.0.1 port 443

Stateful Firewall (L3/L4):
  Tracks TCP connection state (SYN, ESTABLISHED, FIN)
  Allows ESTABLISHED traffic back automatically
  Blocks packets that don't match known sessions

Application Layer (WAF/L7):
  Inspects HTTP payload, headers, body
  Detects SQL injection, XSS, DDoS patterns
  More CPU-intensive

Next-Gen Firewall (NGFW):
  Combines stateful + application + IDS/IPS
  Deep packet inspection, user identity awareness
```

## Firewall Rules — Direction Matters

```
Ingress (inbound) rules:  control what enters the network
Egress  (outbound) rules: control what leaves the network

Typical DMZ rule set:
  ALLOW inbound TCP to :80, :443    (web server)
  ALLOW inbound TCP to :25          (mail server in DMZ)
  DENY  inbound ALL others
  ALLOW outbound ESTABLISHED (return traffic)
  DENY  outbound from DMZ to internal network

Security principle: DENY ALL by default, then ALLOW specific exceptions.
```

## Cloud Security Groups vs Firewalls

```
AWS Security Groups:
  Stateful — return traffic automatically allowed
  Rules are per-resource (EC2 instance)
  No explicit DENY — only ALLOW rules (implicit deny)

AWS NACLs (Network ACLs):
  Stateless — must explicitly allow return traffic
  Applied at subnet level
  Numbered rules, evaluated in order
  Support explicit DENY
```

## Common Pitfalls
- **Too permissive rules** — `ALLOW ALL` is the enemy of security. Restrict to minimum required ports.
- **Forgetting egress rules** — malware and data exfiltration go outbound. Control outbound traffic too.
- **Rule ordering** — packet filter rules are evaluated top-to-bottom; first match wins. Put specific rules before broad ones.
- **Forgetting ephemeral ports** — PASV FTP, response traffic, and load balancers need high port ranges (1024-65535) for return traffic in stateless firewalls.
""",
      questions=[
          {"id":"fw-q1","type":"mcq","prompt":"Stateful vs stateless firewall — key difference?","choices":["Stateful is faster","Stateful tracks TCP session state — it knows which connections are established so return traffic is automatically allowed without explicit rules. Stateless inspects each packet in isolation","Stateless is more secure","They are equivalent"],"answerIndex":1,"explanation":"Stateful firewalls model TCP state machines. An ESTABLISHED connection's return packets are allowed automatically. Stateless firewalls need explicit rules for both request AND response directions.","tags":["firewalls","stateful"]},
          {"id":"fw-q2","type":"mcq","prompt":"AWS Security Groups vs Network ACLs — key difference?","choices":["Security Groups are per-region; NACLs per-VPC","Security Groups are stateful (return traffic automatic), applied per-resource. NACLs are stateless, applied per-subnet, support explicit DENY, numbered rules evaluated in order","Security Groups are cheaper","NACLs are deprecated"],"answerIndex":1,"explanation":"Important AWS detail: Security Groups are instance-level, stateful, no explicit deny. NACLs are subnet-level, stateless (must allow return traffic), support DENY rules.","tags":["firewalls","aws","security-groups"]},
          {"id":"fw-q3","type":"mcq","prompt":"Security principle for firewall default policy?","choices":["ALLOW ALL by default, DENY exceptions","DENY ALL by default, ALLOW specific exceptions — least-privilege principle","Block only known bad IPs","Use AI to decide"],"answerIndex":1,"explanation":"Deny-by-default is the security baseline. Only explicitly listed traffic is allowed. Any unrecognized traffic is blocked. This limits the blast radius of misconfiguration.","tags":["firewalls","security"]},
      ],
      flashcards=[
          {"id":"fw-fc1","front":"Firewall types by layer","back":"L3/L4 packet filter: IP+port rules, fast, stateless. Stateful: tracks TCP connections, auto-allows return traffic. L7/WAF: HTTP-aware, detects injection attacks. NGFW: combines all + IDS/IPS.","tags":["firewalls"]},
          {"id":"fw-fc2","front":"AWS Security Group vs NACL","back":"Security Group: stateful, per-instance, ALLOW only (implicit deny). NACL: stateless, per-subnet, numbered rules, supports explicit DENY. Use both for defence-in-depth.","tags":["firewalls","aws"]},
          {"id":"fw-fc3","front":"Default deny principle","back":"DENY ALL by default, then ALLOW minimum required. Reduces attack surface — misconfiguration adds security rather than removing it.","tags":["firewalls","security"]},
      ])

patch(BASE / "networking/rate-limiting.json",
      guide="""# Rate Limiting

Rate limiting **caps the number of requests** a client can make to an API or service within a time window. It protects against abuse, DDoS, and runaway clients.

## Common Algorithms

```
Token Bucket:
  Tokens fill at a fixed rate (e.g., 10/sec).
  Each request consumes 1 token.
  Burst allowed up to bucket capacity.
  Tokens= min(capacity, lastTokens + rate*(now-lastTime))

Leaky Bucket:
  Queue with fixed outflow rate.
  All variability smoothed to constant output.
  Excess requests dropped or queued.

Fixed Window:
  Counter resets every minute/hour.
  Weakness: burst at window boundary
  (100 reqs in last second of window + 100 in first second = 200 instant)

Sliding Window Log:
  Keep timestamps of requests in a rolling window.
  Exact (no boundary burst) but memory-intensive.

Sliding Window Counter:
  Approximation: current_window_count + prev_window_count * (1 - elapsed/window)
  Low memory, no boundary burst, slightly approximate.
```

## HTTP Response Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 942
X-RateLimit-Reset: 1714521600   (Unix timestamp when counter resets)
Retry-After: 3600               (seconds to wait — on 429 response)

HTTP 429 Too Many Requests
```

## Implementation Layers

```
Where to rate limit:
  1. API Gateway (Kong, NGINX, AWS API GW) — best for cross-service limits
  2. Application-level middleware          — per-route granularity
  3. Load balancer                        — gross traffic control

What to rate-limit by:
  - IP address (easy to bypass via proxies)
  - User ID / API key (more accurate)
  - Endpoint (protect expensive ones more strictly)
  - Global (service-wide quota)
```

## Distributed Rate Limiting

Single server: simple in-memory counter.
Multiple servers: share state via Redis.

```javascript
// Redis sliding window counter
async function isAllowed(userId, limit, windowSec) {
  const key = `ratelimit:${userId}`;
  const now = Date.now();
  const window = now - windowSec * 1000;

  const multi = redis.multi();
  multi.zremrangebyscore(key, 0, window);            // remove old entries
  multi.zcard(key);                                   // count in window
  multi.zadd(key, now, now.toString());              // add current request
  multi.expire(key, windowSec);

  const results = await multi.exec();
  const count = results[1];
  return count < limit;
}
```

## Common Pitfalls
- **Fixed window boundary bursts** — double the intended rate is possible at window boundaries. Use sliding window.
- **Per-IP limiting bypassed by proxies** — use API key / user ID for important limits.
- **Not communicating limits** — always return X-RateLimit-* headers so clients can self-throttle.
- **Cascading failures** — if downstream service rate-limits you, implement exponential backoff + jitter in the caller.
""",
      questions=[
          {"id":"rl-q1","type":"mcq","prompt":"Token bucket vs fixed window — main advantage of token bucket?","choices":["Token bucket is simpler","Token bucket allows controlled bursting up to bucket capacity while maintaining a long-term average rate. Fixed window creates boundary bursts where 2x the limit can flow at window boundaries","Fixed window is less accurate","Token bucket requires more memory"],"answerIndex":1,"explanation":"Fixed window: reset at the minute boundary means 100 reqs at 11:59 + 100 at 12:00 = 200 in 2 seconds. Token bucket allows bursts explicitly (up to bucket size) while enforcing the average rate over time.","tags":["rate-limiting","algorithms"]},
          {"id":"rl-q2","type":"mcq","prompt":"HTTP status code for rate limit exceeded?","choices":["400","401","403","429"],"answerIndex":3,"explanation":"HTTP 429 Too Many Requests. Include Retry-After header with seconds to wait, and X-RateLimit-Reset with when the window resets.","tags":["rate-limiting","HTTP"]},
          {"id":"rl-q3","type":"mcq","prompt":"Why use Redis for rate limiting in a distributed system?","choices":["Redis is faster","Multiple application servers share the rate limit counter — without Redis, each server has its own counter and the limit effectively multiplies by server count","Redis is the only option","In-memory is insufficient"],"answerIndex":1,"explanation":"3 servers each with a 100 req/sec limit = 300 req/sec total. Shared Redis counter enforces the limit globally across all instances.","tags":["rate-limiting","distributed"]},
      ],
      flashcards=[
          {"id":"rl-fc1","front":"Rate limiting algorithms","back":"Token bucket: fill at rate, burst allowed. Leaky bucket: smooth output, no burst. Fixed window: simple but boundary burst. Sliding window: accurate, no burst, more memory.","tags":["rate-limiting"]},
          {"id":"rl-fc2","front":"Rate limit HTTP headers","back":"X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset (when resets). On limit: 429 Too Many Requests + Retry-After header.","tags":["rate-limiting","HTTP"]},
          {"id":"rl-fc3","front":"Distributed rate limiting","back":"Use Redis with ZADD/ZCARD (sliding window) or INCR+EXPIRE (fixed window) for shared counters across multiple app servers.","tags":["rate-limiting","redis"]},
      ])

patch(BASE / "networking/load-balancing.json",
      guide="""# Load Balancing

A load balancer **distributes incoming traffic** across multiple backend servers to maximize availability, prevent any single server from being overwhelmed, and enable horizontal scaling.

## Load Balancing Algorithms

```
Round Robin:
  Requests cycle through servers in order: A, B, C, A, B, C...
  Simple, assumes servers are equivalent.

Weighted Round Robin:
  Servers get traffic proportional to weight: A(weight=2) gets 2x B(weight=1).
  Useful when servers have different capacity.

Least Connections:
  Route to server with fewest active connections.
  Good for long-lived connections (WebSockets, DB).

IP Hash / Sticky Sessions:
  Hash client IP → always route to same server.
  Required for stateful apps without shared session storage.

Least Response Time:
  Route to fastest-responding server.
  Accounts for varying server load and health.

Random:
  Route to a random server.
  Surprisingly effective for stateless services at scale.
```

## Layer 4 vs Layer 7 Load Balancing

```
L4 (Transport Layer — TCP/UDP):
  Routes based on IP + port only
  No content inspection — fast, low overhead
  Can't route based on URL path or HTTP headers
  Example: AWS NLB, HAProxy in TCP mode

L7 (Application Layer — HTTP):
  Inspects HTTP headers, path, host, cookies
  Can route /api/* to API servers, /static/* to CDN
  SSL termination (decrypt once at LB)
  Example: AWS ALB, NGINX, HAProxy in HTTP mode

Typical: L7 LB in front → L4 LBs in back → servers
```

## Health Checks

```
Load balancer continuously tests backend health:
  HTTP: GET /health → expect 200
  TCP:  can it connect to port 80?
  Interval: every 5-30 seconds
  Threshold: 2 consecutive failures → mark unhealthy

Unhealthy server removed from rotation.
No downtime — traffic shifts to remaining healthy servers.
```

## Common Pitfalls
- **Forgetting to remove unhealthy servers** — configure health checks with short intervals.
- **Session affinity vs horizontal scaling tension** — sticky sessions work but prevent seamless server removal. Prefer stateless backends with common session storage (Redis).
- **SSL termination security** — traffic from LB to backend servers may be unencrypted (HTTP). Ensure the internal network is trusted or re-encrypt.
- **Single load balancer = single point of failure** — use LB pairs (primary/standby) or DNS round-robin for HA.
""",
      questions=[
          {"id":"lb-q1","type":"mcq","prompt":"Least Connections algorithm is better than Round Robin for:","choices":["Stateless REST APIs","Long-lived connections (WebSockets, database connections) where each connection has different duration and a server may be saturated even with fewer connection count","Static file serving","Read-heavy workloads"],"answerIndex":1,"explanation":"Round Robin assumes all connections are equivalent. With long-lived WebSocket connections, a server with 10 old connections might be more loaded than one with 50 new short-lived connections. Least-connections tracks active load better.","tags":["load-balancing","algorithms"]},
          {"id":"lb-q2","type":"mcq","prompt":"L7 load balancer advantage over L4?","choices":["L7 is faster","L7 inspects HTTP content — can route based on URL path, host header, cookies; can do SSL termination and content-based routing. L4 only routes by IP+port","L7 requires no configuration","L4 is less secure"],"answerIndex":1,"explanation":"L7 enables: /api → API servers, /static → CDN, subdomain-based routing, A/B traffic splitting, WAF integration. At the cost of more CPU (unpacking HTTP packets).","tags":["load-balancing","L7","L4"]},
          {"id":"lb-q3","type":"mcq","prompt":"Sticky sessions solve what problem and at what cost?","choices":["They improve performance","Sticky sessions ensure the same user always hits the same server — needed for stateful apps storing session in memory. Cost: can't remove a server without losing active sessions, may create hotspots","Not useful in production","They reduce latency"],"answerIndex":1,"explanation":"Sticky sessions (IP hash or cookie-based) work for stateful apps but create coupling. Preferred solution: stateless backends + shared session storage (Redis) — all servers can serve any user.","tags":["load-balancing","sticky-sessions"]},
      ],
      flashcards=[
          {"id":"lb-fc1","front":"Load balancing algorithms","back":"Round Robin: cyclic, equal traffic. Weighted RR: proportional to server capacity. Least Connections: route to least-loaded (best for WS). IP Hash: sticky sessions. Least Response Time: adaptive.","tags":["load-balancing"]},
          {"id":"lb-fc2","front":"L4 vs L7 load balancing","back":"L4: routes by IP+port, no inspection, fast. L7: inspects HTTP headers/path/cookies, enables content routing, SSL termination, WAF. L7 has more overhead but more capability.","tags":["load-balancing"]},
          {"id":"lb-fc3","front":"Health checks","back":"LB polls /health every 5-30s. 2 consecutive failures → server removed from rotation. Zero-downtime removal. Critical for production reliability.","tags":["load-balancing","health-checks"]},
      ])

patch(BASE / "networking/proxies.json",
      guide="""# Proxies — Forward and Reverse

A **proxy** is a server that acts as an intermediary between clients and backend servers. Forward proxies sit in front of clients; reverse proxies sit in front of servers.

## Forward Proxy vs Reverse Proxy

```
Forward Proxy:
  Client → Forward Proxy → Internet (servers)

  Client knows about the proxy.
  Server sees proxy's IP not client's.
  Uses: bypass geo-restrictions, corporate filtering, anonymity, caching.

Reverse Proxy:
  Internet (clients) → Reverse Proxy → Backend Servers

  Client talks to proxy thinking it's the origin.
  Client doesn't know about backend servers.
  Uses: load balancing, SSL termination, caching, DDoS protection, WAF.
```

## What a Reverse Proxy Does

```
Incoming HTTPS request → Reverse Proxy:
  ✓ SSL termination (decrypt; re-encrypt to backend or use HTTP internally)
  ✓ Routing (/api/* to API servers, /* to static web server)
  ✓ Rate limiting and WAF rule enforcement
  ✓ Response caching (cache GET /products until TTL expires)
  ✓ Compression (gzip responses)
  ✓ Add security headers (HSTS, CSP, etc.)
  ✓ A/B testing (route 10% of traffic to a new version)
  ✓ Authentication offloading (JWT validation at proxy)
```

## NGINX as Reverse Proxy (Config Example)

```nginx
server {
  listen 443 ssl;
  server_name api.example.com;

  ssl_certificate /etc/ssl/cert.pem;
  ssl_certificate_key /etc/ssl/key.pem;

  location /api/ {
    proxy_pass http://api-upstream;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Host $host;
  }

  location /static/ {
    root /var/www;
    expires 30d;
  }
}

upstream api-upstream {
  least_conn;
  server 10.0.0.1:8080;
  server 10.0.0.2:8080;
}
```

## Common Proxy Patterns

| Pattern | Tool | Purpose |
|---|---|---|
| Edge proxy / CDN | Cloudflare, CloudFront | Global distribution, DDoS, caching |
| API Gateway | Kong, AWS API GW | Auth, rate limiting, routing |
| Service mesh sidecar | Envoy (Istio) | mTLS, observability, circuit breaking |
| Forward proxy | Squid, corporate proxies | Content filtering, caching |

## Common Pitfalls
- **Losing the client IP** — reverse proxy rewrites the source IP. Use X-Forwarded-For or X-Real-IP headers. Configure the app to trust them.
- **Double SSL** — terminating at proxy but not re-encrypting to backend leaks data on internal network if not trusted. Configure backend SSL or ensure private network.
- **Proxy caching stale data** — aggressive caching can serve outdated responses. Set appropriate Cache-Control and vary headers.
""",
      questions=[
          {"id":"px-q1","type":"mcq","prompt":"Forward proxy vs reverse proxy — where each sits in the architecture?","choices":["Same location","Forward: in front of CLIENTS (client knows about it). Reverse: in front of SERVERS (client is unaware, thinks it's talking to origin)","Both sit in the DMZ","Reverse is for UDP only"],"answerIndex":1,"explanation":"Forward proxy represents the client to the internet (anonymity, filtering). Reverse proxy represents the server to the internet (load balancing, SSL, routing) — fundamental architectural difference.","tags":["proxies","architecture"]},
          {"id":"px-q2","type":"mcq","prompt":"Why does a reverse proxy need to pass X-Forwarded-For header?","choices":["For authentication","The proxy rewrites the source IP of requests. Backend apps see the proxy's IP. X-Forwarded-For carries the original client IP so the app can log it, rate-limit correctly, and geo-locate","Required by HTTP spec","For caching"],"answerIndex":1,"explanation":"Without X-Forwarded-For, all traffic appears to come from the proxy (e.g., 10.0.0.1). Logging, rate limiting, and fraud detection break completely. Apps must be configured to trust the proxy and use X-Forwarded-For.","tags":["proxies","headers"]},
          {"id":"px-q3","type":"mcq","prompt":"SSL termination at the reverse proxy means:","choices":["HTTPS is impossible behind the proxy","SSL is decrypted at the proxy. Traffic from proxy to backend may be plain HTTP (faster, less overhead). Only justified if the internal network is trusted or backend also encrypts","The certificate lives on the backend","Clients connect with HTTP"],"answerIndex":1,"explanation":"Centralized SSL termination: one certificate to renew, all traffic encrypted externally, backends handle HTTP. For stricter security, re-encrypt proxy→backend (mTLS). Common in AWS ALB + ECS architectures.","tags":["proxies","SSL","termination"]},
      ],
      flashcards=[
          {"id":"px-fc1","front":"Forward vs Reverse Proxy","back":"Forward: client-side, client knows about it, server sees proxy IP. Uses: filtering, anonymity, corporate caching. Reverse: server-side, client unaware. Uses: LB, SSL termination, WAF, caching.","tags":["proxies"]},
          {"id":"px-fc2","front":"Reverse proxy capabilities","back":"SSL termination, load balancing, routing, caching, compression, rate limiting, WAF, A/B testing, security headers, auth offloading.","tags":["proxies"]},
          {"id":"px-fc3","front":"X-Forwarded-For","back":"Header carrying original client IP through proxy chain. Apps must trust the proxy and read X-Forwarded-For for rate limiting, logging, geo-location. Without it: all traffic looks like it comes from proxy.","tags":["proxies","headers"]},
      ])

# ─── CLOUD / DEVOPS ──────────────────────────────────────────────────────────

patch(BASE / "cloud-devops/docker.json",
      guide="""# Docker

Docker packages applications and their dependencies into **containers** — isolated, portable, reproducible environments that run consistently across any machine.

## The Container vs VM Distinction

```
VM:                           Container:
  ┌────────────────────┐        ┌──────────────────────┐
  │ App A  │ App B     │        │ App A  │ App B  App C │
  │ OS A   │ OS B      │        │ Lib A  │ Lib B  Lib C │
  │──────────────────  │        │──────────────────────│
  │   Hypervisor       │        │   Container Runtime  │
  │   Host OS          │        │   Host OS (shared)   │
  │   Hardware         │        │   Hardware           │
  └────────────────────┘        └──────────────────────┘
  Full OS per app                Shares host OS kernel
  GBs of overhead                MBs of overhead
  Seconds to start               Milliseconds to start
```

## Dockerfile

```dockerfile
# Multi-stage build — final image doesn't need build tools
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
USER node                          # don't run as root!
CMD ["node", "dist/server.js"]
```

## Essential Commands

```bash
docker build -t myapp:1.0 .         # Build image from Dockerfile
docker run -p 3000:3000 myapp:1.0   # Run container (host:container port mapping)
docker run -d --name api myapp:1.0  # Run detached, named
docker exec -it api /bin/sh         # Shell into running container
docker logs -f api                  # Follow container logs
docker ps                           # List running containers
docker images                       # List local images
docker push registry/myapp:1.0      # Push to registry
docker stop api && docker rm api    # Stop and remove
```

## docker-compose — Multi-Container

```yaml
# docker-compose.yml
version: '3.9'
services:
  api:
    build: ./api
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/myapp
    depends_on: [db]
    restart: unless-stopped

  db:
    image: postgres:16
    volumes: ["pgdata:/var/lib/postgresql/data"]
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass

volumes:
  pgdata:
```

## Layer Caching

```
Dockerfile layers cache from bottom of unchanged layer:
  COPY package.json .   ← if unchanged, next layer uses cache
  RUN npm install       ← expensive, skipped if package.json unchanged
  COPY . .              ← changes frequently, but install already cached

Best practice: copy package.json BEFORE src to cache node_modules.
```

## Common Pitfalls
- **Running as root** — adds `USER node` or `USER nobody` in Dockerfile. Root in container can be root on host with misconfigured kernel.
- **Storing secrets in images** — secrets baked into layers persist forever in history. Use secrets management (Docker secrets, Vault, env vars at runtime).
- **Large images** — use Alpine base images, multi-stage builds, `.dockerignore`. Smaller = faster pulls = smaller attack surface.
- **Not using .dockerignore** — COPY . . copies `node_modules`, `.git`, `.env`. Always exclude these.
""",
      questions=[
          {"id":"dkr-q1","type":"mcq","prompt":"Container vs VM: key performance difference?","choices":["Containers are safer","Containers share the host OS kernel — no guest OS per container. Start in milliseconds, use MBs of overhead vs GBs for VMs","VMs are always faster","VMs share the kernel too"],"answerIndex":1,"explanation":"Docker containers share the host OS kernel via Linux namespaces and cgroups. No full OS booting → near-instant startup, tiny memory footprint. Tradeoff: less isolation than VMs (same kernel).","tags":["docker","containers"]},
          {"id":"dkr-q2","type":"mcq","prompt":"Why use multi-stage Docker builds?","choices":["Required by Docker 20+","Separate build tools (compilers, test runners) from the final runtime image — production image only contains what's needed to run, not build. Dramatically reduces image size and attack surface","Multi-stage is slower","Only for compiled languages"],"answerIndex":1,"explanation":"Build stage: includes compiler, dev dependencies, test tools. Runtime stage: copies only built artifacts. Node app: FROM node AS builder (npm install + build) → FROM node-alpine AS runtime (copy dist). Final image has no npm, no source code, no dev deps.","tags":["docker","multi-stage","best-practices"]},
          {"id":"dkr-q3","type":"mcq","prompt":"Why order Dockerfile instructions with COPY package.json before COPY . .?","choices":["Syntax requirement","Docker caches each layer. package.json rarely changes — npm install (expensive) uses cache on most builds. Source code changes frequently, but the cached node_modules layer is reused","Improves security","Required for docker-compose"],"answerIndex":1,"explanation":"Layer caching: if COPY . . comes first and any source file changes, ALL subsequent layers (including npm install) must re-run. Separating dependency files from source allows npm install to be cached.","tags":["docker","layer-caching"]},
      ],
      flashcards=[
          {"id":"dkr-fc1","front":"Container vs VM","back":"Container: shares host OS kernel, MBs overhead, ms startup, namespace/cgroup isolation. VM: own OS per machine, GBs overhead, s startup, hypervisor isolation. Containers faster but less isolated.","tags":["docker"]},
          {"id":"dkr-fc2","front":"Multi-stage Dockerfile","back":"FROM heavy AS builder (compile). FROM alpine AS runtime. COPY --from=builder /app/dist ./. Final image contains only runtime artifacts — no compilers, dev deps, or source. Smaller and more secure.","tags":["docker","multi-stage"]},
          {"id":"dkr-fc3","front":"Key Docker commands","back":"build -t name:tag . | run -p host:container name | exec -it name /bin/sh | logs -f name | ps | push registry/name:tag","tags":["docker"]},
          {"id":"dkr-fc4","front":"docker-compose","back":"Orchestrates multi-container apps locally. services, ports, volumes, environment, depends_on. Startup order but not readiness — use health checks for depends_on to respect DB ready.","tags":["docker","compose"]},
      ])

print("\nAll short guides patched!")

