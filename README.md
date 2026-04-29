# CS Mastery

A Duolingo-style, offline-first Progressive Web App that teaches computer science, cloud infrastructure, and AI through adaptive quizzes, spaced-repetition flashcards, and design-rubric mini-projects.

Single-user · No backend · No API keys · No network after first load · Works on iPhone + macOS

---

## ✅ What's Been Built (Completed Features)

> 🏆 = Done and shipped · 📝 = Script file exists

### UI & Theme
- 🏆 **Full dark/light theme** — CSS custom properties (`--bg-app`, `--bg-card`, `--text-primary` etc.) across every screen
- 🏆 **Light mode fixes** — quiz choices, code blocks (stay dark), orange banners, amber hints, emerald/red feedback all readable
- 🏆 **Topic emoji icons** — every node shows a relevant emoji (🐧 Linux, ⚛️ React, 🐳 Docker…) instead of a play button
- 🏆 **Donut progress ring** — 4-arc SVG ring on each topic node: guide accessed / flashcards / quiz passed / project complete
- 🏆 **Duolingo-style 3D buttons** (`.btn-primary`, `.btn-success` with bottom shadow)
- 🏆 **Difficulty column backgrounds** removed — all cards use `var(--bg-card)` for clean light/dark theming
- 🏆 **Full-width desktop layout** — home, stats, settings all stretch to fill the display

### Navigation & Layout
- 🏆 **4-column difficulty layout** (desktop): Beginner · Intermediate · Advanced · Expert + Optional row below
- 🏆 **Collapsible unit cards** with Chevron toggle — each section is expandable/collapsible
- 🏆 **First topic of every unit always unlocked** — start any section immediately
- 🏆 **Sequential lock within units** — topic N+1 requires N to be 100% complete (learned)
- 🏆 **Bottom nav with CSS vars** — active tab gets indigo highlight ring, readable in both themes
- 🏆 **Stats full-width** — 2-column desktop layout (unit progress + quiz accuracy side by side), 3-column summary cards

### Mind Map
- 🏆 **Obsidian-style** — `#0d1117` dark background (light: `#eef2ff`) with dot grid
- 🏆 **Rounded rectangle nodes** — not circles; width proportional to title length
- 🏆 **Arrow markers on prerequisite edges** — directional bezier curves
- 🏆 **Unit halo bubbles** — dashed circle shows each unit cluster
- 🏆 **Search + filter chips** — filter by unit, search by title/summary
- 🏆 **Pan + pinch zoom** — mouse wheel, Ctrl+scroll, two-finger pinch on mobile
- 🏆 **Bottom sheet on node click** — shows prereqs, unlocks, open topic button
- 🏆 **Theme-compatible** — toolbar, legend, bottom sheet all use CSS vars

### Quiz & Learning
- 🏆 **Quiz card fully theme-compatible** — MCQ choices, multi-select, fill-blank, order, match — all use CSS vars
- 🏆 **Code output blocks stay dark** in light mode (black bg, cyan text — always readable)
- 🏆 **Correct/wrong feedback** — green/red borders and background on answer choices
- 🏆 **RubricChecklist theme-fixed** — project brief, checklist items, score display all use CSS vars
- 🏆 **Result page theme-fixed** — pass/fail panels use CSS vars

### Content Topics Added
- 🏆 **aws-ecs-fargate** — ECS task defs, Fargate, ECR, Blue/Green, auto-scaling (20q, 8fc)
- 🏆 **aws-rds-advanced** — Multi-AZ, read replicas, Aurora, RDS Proxy, PITR, encryption (20q, 8fc)
- 🏆 **event-driven-architecture** — CQRS, event sourcing, saga, outbox pattern (20q, 8fc)
- 🏆 **microservices-patterns** — circuit breaker, service mesh, API gateway, bulkhead, BFF (20q, 8fc)

---

## ⚡ Quick Start (Local Dev)

```bash
cd cs-mastery

# 1. Install dependencies (--legacy-peer-deps needed for React 19 peer compat)
npm install --legacy-peer-deps

# 2. Start dev server
npm run dev
# → Opens at http://localhost:5173/cs-mastery/
```

> **If you see `sh: vite: command not found`** — run `npm install --legacy-peer-deps` first, then retry.

---

## 🏗️ Build & Preview (PWA)

```bash
npm run build          # TypeScript check + Vite production build → dist/
npm run preview        # Serve the built PWA locally (tests offline mode)
```

The `dist/` folder is a fully static, offline-capable PWA. Deploy to GitHub Pages, Cloudflare Pages, or Netlify with zero config.

---

## 📱 Install on iPhone 13 Pro Max

1. `npm run build && npm run preview` (or deploy `dist/` to a public URL).
2. Open the URL in **Safari** on iPhone.
3. Tap Share → **Add to Home Screen**.
4. Launch from the home-screen icon — runs fullscreen, works completely offline.

---

## 💻 Install on macOS

1. Open the URL in **Chrome** or **Edge**.
2. Address bar → install icon → **Install CS Mastery**.
3. Or use Safari — PWA caching (offline) still works even without install.

---

## 🔄 Cross-Device Sync (No Cloud)

Progress lives in `localStorage` per device. To sync between Mac ↔ iPhone:

1. **Source device:** Settings → Export progress → downloads `cs-mastery-progress-<date>.json`
2. **AirDrop** the file to target device (or iCloud Drive / email)
3. **Target device:** open the app → Settings → Import progress → pick the file
4. Merge strategy keeps the most recent record per key — safe to import multiple times

---

## 🧠 How Learning Works

1. **Start** any available topic — first topic in each unit is unlocked immediately.
2. **Read** the guide (markdown with diagrams, analogies, ASCII art).
3. **Quiz** — 5 random questions drawn from 20. Pass ≥ 80% → +20 XP, next topic unlocks.
4. **Fail** → remediation shows only guide sections for concepts you missed. Retry.
5. **Spaced review** — learned topics reappear after 1 day, then longer intervals (SM-2).
6. **Flashcards** — same SM-2 schedule, tracked per card, surfaced in `/review`.
7. **Project rubric** — design-style brain exercise. Self-tick checklist, hints on demand.

### Unlock Rules
- **First topic of each unit** → always unlocked immediately (start anywhere!)
- **Topics within a unit** → unlock sequentially — complete topic N to access topic N+1
- Each topic has a **4-quadrant progress indicator** on its node icon:
  - 🔵 Q1 (top-right): topic accessed
  - 🔵 Q2 (bottom-right): flashcards completed
  - 🔵 Q3 (bottom-left): quiz passed (≥80%)
  - 🔵 Q4 (top-left): project complete

---

## 📚 Curriculum (120 Topics, 18 Units)

### Layout — 4 Difficulty Columns (desktop) / Single Column (mobile)

| 🌱 Beginner | ⚡ Intermediate | 🔥 Advanced | 💎 Expert |
|---|---|---|---|
| Unit 1: Foundations | Unit 3: TypeScript | Unit 8: DSA in Java | Unit 13: System Design |
| Unit 2: Python | Unit 4: React | Unit 9: Scaling & Data | Unit 14: Java Advanced |
| | Unit 5: Angular | Unit 10: Cloud & DevOps | |
| | Unit 6: Networking | Unit 11: AI Advanced | |
| | Unit 7: AI Primer | Unit 12: Security | |
| | | Unit 18: AWS | |

**📦 Optional** (below Expert): Unit 15: Financial Literacy · Unit 16: Advanced Engineering · Unit 17: Tooling

### All Units

| # | Unit | Topics |
|---|------|--------|
| 1 | **Foundations** | Linux, Git, SQL, Embedded DBs, Complexity, Recursion, Memory, Pointers |
| 2 | **Python** | Fundamentals, OOP, Error Handling, Functional, Type Hints |
| 3 | **TypeScript** | Fundamentals through tsconfig (8 topics) |
| 4 | **React** | Fundamentals through Server Components (9 topics) |
| 5 | **Angular** | Fundamentals through Standalone (9 topics) |
| 6 | **Networking** | Firewalls, FTP, Proxies, RPC, WebSockets, Long Polling, Rate Limiting, QPS, Load Balancing |
| 7 | **AI Primer** | ML Basics, Neural Nets, Transformers, LLMs, Prompting |
| 8 | **DSA in Java** | Arrays → Two Pointers (19 topics) |
| 9 | **Scaling & Data** | Caching, Sharding, Partitioning, Kafka, RabbitMQ |
| 10 | **Cloud & DevOps** | Cloud Fundamentals, Docker, Kubernetes, Serverless, CI/CD, Observability |
| 11 | **AI Advanced** | Agents, RAG, Fine-tuning, Leverage, Image Gen, Prompt Eng, LLMOps |
| 12 | **Security** | Security Fundamentals |
| 13 | **System Design** | System Design, Data Structures Advanced, Distributed Systems, DB Internals, Observability, API Design, Caching Advanced |
| 14 | **Java Advanced** | Multithreading, Concurrency Advanced |
| 15 | **Financial Literacy** | Stock market, Technical/Fundamental Analysis, Options, Mutual Funds, Personal Finance, Macro |
| 16 | **Advanced Engineering** | SQL Advanced, Git Advanced |
| 17 | **Tooling** | PyCharm Power-use |
| 18 | **AWS** | AWS Practitioner, AWS Mastery, SQS, Lambda Deep Dive, VPC Networking, ECS & Fargate, RDS Advanced |

### Folder structure (topics/)
```
topics/
├── foundations/       Unit 1
├── python/            Unit 2
├── typescript/        Unit 3
├── react/             Unit 4
├── angular/           Unit 5
├── networking/        Unit 6
├── ai/                Units 7, 11
├── dsa-java/          Unit 8
├── scaling/           Unit 9
├── cloud-devops/      Unit 10
├── security/          Unit 12
├── system-design/     Unit 13
├── java/              Unit 14   ← Java Advanced (multithreading etc.)
├── finance/           Unit 15
├── advanced/          Unit 16
└── aws/               Unit 18
```

---

## 🎯 Anti-Boredom Study Rotation

Don't grind one section — rotate across tracks daily:

| Track A — Core Engineering | Track B — AI & Data | Track C — Systems Thinking |
|---|---|---|
| DSA: Trees, Graphs, DP | ML Basics → Neural Nets | Linux → Docker → K8s |
| TypeScript → React | Transformers → LLMs | Networking: DNS, HTTP |
| Angular signals | RAG & Agents | System Design |
| SQL → Partitioning | Fine-tuning | CI/CD → AWS |

**Rule:** Never do 2 DSA topics back-to-back. End every session with 10 flashcard reviews from a *different* section than what you just studied.

---

## 🆕 Topics to Add Next (Backlog)

### Scripts convention — 2 topics per script
```
scripts/gen_python_batch1.py      → python-oop, python-error-handling
scripts/gen_python_batch2.py      → python-functional, python-type-hints
scripts/gen_python_batch3.py      → (next: python-decorators, python-concurrency)
scripts/gen_java_advanced_batch1.py → java-multithreading, java-concurrency-advanced
scripts/gen_java_advanced_batch2.py → (next: java-jvm-internals, java-spring-boot)
scripts/gen_aws_batch1.py         → aws-lambda-deep-dive, aws-vpc-networking
scripts/gen_aws_batch2.py         → (next: aws-ecs-fargate, aws-rds-advanced)
scripts/gen_system_design_batch1.py → api-design-patterns, caching-advanced
scripts/gen_system_design_batch2.py → (next: event-driven-architecture, microservices)
```

### Python (Unit 2)
- `python-decorators` — function/class decorators, wraps, stacking
- `python-concurrency` — threading, asyncio, GIL

### Java Advanced (Unit 14)
- `java-jvm-internals` — GC algorithms, heap zones, JVM tuning flags
- `java-spring-boot` — IoC, AOP, Spring Data, actuators

### AWS (Unit 18) — Script-based, 2 topics per file
- 🏆 `gen_aws_batch1.py` → aws-lambda-deep-dive, aws-vpc-networking
- 🏆 `gen_aws_batch2.py` → aws-ecs-fargate, aws-rds-advanced
- 📝 `gen_aws_batch3.py` → (next: aws-iam-advanced, aws-aurora-deep-dive)

### System Design (Unit 13)
- 🏆 `gen_system_design_batch1.py` → api-design-patterns, caching-advanced
- 🏆 `gen_system_design_batch2.py` → event-driven-architecture, microservices-patterns
- 📝 `gen_system_design_batch3.py` → (next: database-sharding-deep-dive, consensus-algorithms)

### Security (Unit 12)
- `web-security` — OWASP Top 10, XSS, CSRF, SQL injection
- `auth-patterns` — JWT, OAuth 2.0, OIDC

### System Design (Unit 13)
- `event-driven-architecture` — CQRS, event sourcing, saga pattern
- `microservices` — service mesh, circuit breaker, service discovery

---

## 🛠️ Tech Stack

| Layer | Library |
|-------|---------|
| UI | React 19 + TypeScript |
| Build | Vite 8 |
| Routing | React Router 7 |
| Styling | Tailwind CSS |
| Animation | Framer Motion 12 |
| Icons | Lucide React |
| Markdown | react-markdown + remark-gfm |
| PWA | vite-plugin-pwa + Workbox |
| Storage | localStorage (small keys) + idb (IndexedDB) |
| Testing | Vitest |

All content is bundled as static JSON under `src/content/topics/`. No runtime LLM calls, ever.

---

## 🗂️ Project Structure

```
cs-mastery/
├── src/
│   ├── routes/          # Home, Topic, Quiz, Result, Project, Review, Flashcards, Settings
│   ├── components/      # PathNode, GuideView, QuizCard, FlashcardDeck, MindMap, etc.
│   ├── content/
│   │   ├── schema.ts    # TypeScript types for Topic, Question, Flashcard
│   │   ├── index.ts     # Glob-imports all topic JSONs
│   │   └── topics/      # 107 JSON files organised by subfolder
│   │       ├── cloud-devops/
│   │       ├── networking/
│   │       ├── scaling/
│   │       ├── ai/
│   │       ├── dsa-java/
│   │       ├── angular/
│   │       ├── react/
│   │       ├── typescript/
│   │       ├── foundations/
│   │       ├── security/
│   │       └── *.json   # top-level foundation topics
│   ├── lib/             # scorer.ts, scheduler.ts, storage.ts, sync.ts, normalize.ts
│   └── state/           # ProgressContext.tsx, HeartsContext.tsx
├── scripts/             # Python content-generation scripts
│   ├── gen_dsa_topics.py
│   ├── patch_networking.py
│   ├── patch_scaling.py
│   ├── patch_cloud_devops.py
│   ├── foundations_batch1.py / batch2a.py / batch2b.py
│   └── validate_topics.py
└── public/              # PWA icons, favicon, 404.html
```

---

## 📝 Available Scripts

| Command | What it does |
|---------|-------------|
| `npm run dev` | Vite dev server with HMR at `localhost:5173/cs-mastery/` |
| `npm run build` | TypeScript check + production PWA build → `dist/` |
| `npm run preview` | Serve the built PWA locally |
| `npm run lint` | ESLint |
| `npm run test` | Vitest (scorer + scheduler smoke tests) |
| `python3 scripts/validate_topics.py` | Check all JSON topics for schema compliance |

---

## 🔄 Reset Progress

**Settings → Reset progress** wipes all `csm:*` keys from `localStorage`. Irreversible unless you exported first.

---

## License

Personal project. No license granted.
