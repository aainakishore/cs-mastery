# CS Mastery

A Duolingo-style, offline-first Progressive Web App that teaches computer science, cloud infrastructure, and AI through adaptive quizzes, spaced-repetition flashcards, and design-rubric mini-projects.

Single-user. No backend. No API keys. No network after first load.

## Quick start

```bash
cd cs-mastery
npm install
npm run dev
```

Open http://localhost:5173.

## Build & preview (PWA)

```bash
npm run build
npm run preview
```

The `dist/` folder is a fully static, offline-capable PWA. Deploy it to any static host (GitHub Pages, Cloudflare Pages, Netlify) or just open `preview`.

## Install on iPhone 13 Pro Max

1. `npm run build && npm run preview` (or deploy `dist/` to a public URL).
2. Open the URL in **Safari** on iPhone.
3. Share sheet → **Add to Home Screen**.
4. Launch from the home screen icon — runs fullscreen, works offline.

## Install on macOS

1. Open the URL in **Chrome** or **Edge**.
2. Address bar → install icon → **Install CS Mastery**.
3. Or just bookmark and use in Safari — PWA features (offline, cache) still work.

## Cross-device sync (no cloud required)

Progress lives in `localStorage` per device. To move progress between your Mac and iPhone:

1. On source device: **Settings → Export progress** → downloads `cs-mastery-progress-<date>.json`.
2. AirDrop (or email / iCloud Drive) the file to the target device.
3. On target device: open the app → **Settings → Import progress** → pick the file.
4. Merge strategy keeps the most recently updated record per key, so it's safe to import repeatedly.

## Reset progress

**Settings → Reset progress** wipes all `csm:*` keys from `localStorage`. Irreversible unless you exported first.

## How the learning loop works

1. **Learn** one or two topics per day from the current unit.
2. **Quiz** (5 random questions out of 20). Pass ≥ 80% to unlock the next topic.
3. **Fail?** Remediation surfaces only the guide sections tagged with the concepts you missed. Retry.
4. **Spaced review.** Each learned topic reappears in "Due today" after 1 day, then a few days, then longer — until it's permanent (SM-2 lite algorithm).
5. **Flashcards** run on the same schedule, per card.
6. **Projects** are design-style brain exercises with a self-ticked rubric checklist. Hints available on demand.

## Curriculum order

1. **Foundations** — Linux, Git, SQL, embedded DBs
2. **AI Primer** — ML basics, transformers, LLMs, prompting
3. **Networking & Protocols** — firewalls, proxies, RPC, WebSockets, polling, rate limiting, QPS, load balancing
4. **Scaling & Data** — caching, sharding, partitioning, Kafka, RabbitMQ, SQS
5. **Cloud & DevOps** — cloud fundamentals, Docker, Kubernetes, S3, Lambda, serverless, CI/CD, logging
6. **AI Advanced** — agents, RAG, fine-tuning, leverage strategies
7. **Tooling** — PyCharm power-use

Foundations first for solid mental models, AI primer early for motivation, then depth.

## Tech

React 19 · TypeScript · Vite 8 · React Router 7 · Tailwind CSS · Framer Motion · Lucide · `vite-plugin-pwa` · Workbox · `idb` · Vitest.

All content is bundled as static JSON under `src/content/topics/`. No runtime LLM calls, ever.

## Project structure

See [PROMPT.md](./PROMPT.md) §13 for the full file layout and build spec.

## Scripts

| Command | What it does |
|---|---|
| `npm run dev` | Vite dev server with HMR |
| `npm run build` | Type-check + production PWA build to `dist/` |
| `npm run preview` | Serve the built PWA locally |
| `npm run lint` | ESLint |
| `npm run test` | Vitest (scorer + scheduler smoke tests) |

---

## 📚 What Topics Should I Add Next?

To avoid getting bored in one section, rotate between these domains. Pick one topic from each column per week:

### Suggested Study Rotation (3-Track System)
| Track A — Core Engineering | Track B — AI & Data | Track C — Systems Thinking |
|---|---|---|
| DSA: Trees, Graphs, DP | ML Basics → Neural Nets | Linux → Docker → Kubernetes |
| TypeScript fundamentals | Transformers → LLMs | Networking: TCP/IP, DNS, HTTP |
| React hooks & rendering | RAG & Agents | System Design: Caching, Sharding |
| SQL → Partitioning | Fine-tuning LLMs | CI/CD → AWS practitioner |
| Angular signals | Prompting Engineering | Rate limiting → Load balancing |

**Why context-switch?**  
- Your brain consolidates memory during *sleep and breaks* — switching topics forces retrieval practice across sessions.
- One deep topic + one breadth topic per day = faster long-term retention than grinding one area.

---

### 🆕 Topics to Add (Prioritized)

#### High Value — Add These First
- **`security-fundamentals`** — OWASP Top 10, JWT, OAuth 2.0, CSRF, XSS, SQL injection defence. Every developer needs this.
- **`system-design-fundamentals`** — URL shortener, feed system, chat at scale. The glue between all you've learned.
- **`data-structures-advanced`** — Segment trees, tries, union-find, heap tricks. Bridge from DSA basics.
- **`typescript-advanced`** — Conditional types, infer, mapped types, template literal types.
- **`react-performance`** — Profiler, memo, useCallback, code splitting, Suspense. Production React.

#### Medium Value — Good Context Switches
- **`sql-advanced`** — CTEs, window functions, query optimization, EXPLAIN plans.
- **`git-advanced`** — Rebase, cherry-pick, bisect, hooks, monorepo strategies.
- **`python-fundamentals`** — For AI/ML work. Decorators, generators, dataclasses, asyncio.
- **`regex`** — Pattern matching used everywhere. Often skipped, always needed.
- **`shell-scripting`** — Bash variables, loops, conditionals, cron jobs. Automate everything.

#### Specialist — Add When Ready
- **`distributed-systems`** — CAP theorem, consensus (Raft/Paxos), vector clocks, eventual consistency.
- **`database-internals`** — B-tree, WAL, MVCC, vacuum, index internals. DeepDive into postgres.
- **`observability`** — OpenTelemetry, Prometheus, Grafana, distributed tracing, SLI/SLO/SLA.
- **`serverless-advanced`** — Cold starts, provisioned concurrency, Lambda Layers, Step Functions.
- **`web-security`** — CSP headers, HTTPS internals, TLS handshake, certificate pinning.
- **`frontend-performance`** — Core Web Vitals, LCP/CLS/FID, bundle analysis, service workers.
- **`java-advanced`** — JVM tuning, GC algorithms, virtual threads (Project Loom), Spring internals.
- **`testing-strategies`** — Unit, integration, e2e (Playwright), TDD, mutation testing.
- **`data-engineering`** — ETL pipelines, Spark basics, dbt, data lake vs warehouse.
- **`algorithms-competitive`** — Dynamic programming patterns, graph algorithms, bit manipulation.

#### Fun / Motivational
- **`ai-image-generation`** — Stable Diffusion, LoRA for images, ControlNet, SDXL.
- **`prompt-engineering-advanced`** — DSPy, structured outputs, JSON mode, function calling strategies.
- **`llm-ops`** — LangSmith, Arize, model versioning, A/B testing prompts, cost optimization.
- **`web3-basics`** — Smart contracts, Solidity basics, Ethereum concepts (to understand the space, not necessarily build).

---

### 🎯 Anti-Boredom Strategy

1. **Never do 2 DSA topics back-to-back** — DSA is mentally intensive. Alternate with Cloud/AI/Frontend.
2. **End each session with a flashcard review** — 10 cards from a *different* section than what you studied.
3. **Watch one YouTube video per week** — from the References sections. Visual learning reinforces text.
4. **Build one small project per unit completed** — The project rubrics give you exercises. Actually build them.
5. **Use the mind map weekly** — Check which topics you haven't learned yet. Pick the most interesting unlocked one.

---

## License

Personal project. No license granted.

git add .
git commit -m "feat: add GitHub Pages CI/CD deployment"  
git remote add origin https://github.com/aainakishore/cs-mastery.git  
git branch -M main
git push -u origin main  
git push -u origin main 2>&1
