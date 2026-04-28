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

