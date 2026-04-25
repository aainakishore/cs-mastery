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

## License

Personal project. No license granted.
