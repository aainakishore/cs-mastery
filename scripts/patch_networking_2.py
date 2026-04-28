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

