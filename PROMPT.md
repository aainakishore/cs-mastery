# CS Mastery — Build Spec

> This is a build brief for an AI coding agent. Use whichever frontier model best fits each sub-task (reasoning-heavy architecture decisions vs. mechanical codegen). Keep every decision consistent with the rules below.

## 1. Product in one paragraph
A single-user, offline-first, Duolingo-style **Progressive Web App** called **CS Mastery** that teaches computer science, cloud infrastructure, and AI via a gamified, adaptive, spaced-repetition curriculum. Runs identically on macOS (Safari/Chrome) and iPhone 13 Pro Max (installed to home screen via "Add to Home Screen"). **No backend. No runtime LLM calls. No API keys.** All guides, quizzes, flashcards, and project rubrics are pre-generated JSON bundled with the app. Progress is local, with JSON export/import for cross-device sync.

## 2. Tech stack (locked)
- **Runtime:** React 19 + TypeScript, Vite 8, React Router 7.
- **Styling:** Tailwind CSS (install and configure; do not use CSS Modules).
- **Animation:** `framer-motion@12` (already installed).
- **Icons:** `lucide-react` (already installed).
- **Markdown rendering:** `react-markdown` + `remark-gfm` (install).
- **PWA:** `vite-plugin-pwa` with Workbox (install). Precache all app shell + content JSON so the app fully works offline after first load.
- **Persistence:** `localStorage` for small keys (progress, xp, streak, hearts, reviewSchedule). `IndexedDB` via `idb` (install) only if a single value would exceed ~1 MB — otherwise `localStorage` is fine.
- **Testing:** Vitest (install) — smoke tests for the scorer and the spaced-repetition scheduler only.
- **No backend. No network calls. No env vars. No API keys. Remove any previously referenced `VITE_ANTHROPIC_API_KEY`.**

## 3. Learner profile (for content tone, not runtime logic)
- Background: Java/Spring Boot basics, new to TS/React.
- Time budget: 2+ hrs/day.
- Goal: commit every topic to long-term memory ("back of my hand").
- Preference: concept-dense explanations, mental effort over typing effort, playful UI.

## 4. Curriculum — fixed order, hybrid motivation-first
Units run in this order. Each unit's topics unlock sequentially; next unit unlocks only when prior unit is ≥80% complete.

**Unit 1 — Foundations**
1. Linux essentials
2. Git fundamentals
3. Relational databases & SQL
4. Embedded databases (SQLite, RocksDB)

**Unit 2 — AI Primer (motivation boost)**
5. ML basics (supervised/unsupervised, train/test)
6. Neural nets & backprop intuition
7. Transformers (attention, tokens)
8. LLMs (how they generate, context windows)
9. Prompting fundamentals

**Unit 3 — Networking & Protocols**
10. Firewalls
11. FTP
12. Proxies (forward / reverse)
13. RPC (gRPC vs REST)
14. WebSockets
15. Long polling vs short polling
16. Rate limiting (token bucket, leaky bucket, fixed/sliding window)
17. QPS & capacity planning
18. Load balancing (L4/L7, algorithms)

**Unit 4 — Scaling & Data**
19. Caching (LRU, write-through/back, CDN)
20. Sharding
21. Partitioning (vs sharding)
22. Kafka
23. RabbitMQ
24. AWS SQS

**Unit 5 — Cloud & DevOps**
25. Cloud fundamentals (IaaS/PaaS/SaaS, regions/AZs)
26. Docker
27. Kubernetes
28. AWS Practitioner fundamentals (EC2, VPC, IAM, RDS, DynamoDB, S3) — but no console walkthroughs, just core concepts and mental models
29. AWS Mastery (Lambda, API Gateway, CloudFormation, CDK) — again, no console, just core concepts and mental models; design-style exercises like "Design a serverless URL shortener with Lambda + API Gateway"
30. Serverless patterns
31. CI/CD pipelines
32. Error logging & observability

**Unit 6 — AI Advanced**
33. Agents (tool use, planning loops)
34. RAG (embeddings, vector DBs, chunking)
35. Fine-tuning (LoRA, SFT, RLHF)
36. Leverage strategies — "max output, min effort"

**Unit 7 — Tooling**
37. PyCharm power-use

Agent must produce **one JSON file per topic** at `src/content/topics/<id>.json` conforming to §6. That file should have lots of clear brief and concise stuff with examples. covering whole topic from beginer to pro level. Final count: 37 topics.

## 5. Per-topic content (all pre-generated, bundled, offline)
Each topic ships with:
- **1 Guide** — 1000–1500 words, markdown, with: 2+ real-world scenarios, 2+ analogies, common pitfalls, a mind-map section, "how this connects to other topics" cross-links.
- **20 Quiz questions** — heterogeneous types (see §7). Quiz draws a random 5 per attempt, biased toward unseen/previously-failed questions.
- **8 Flashcards** — short front/back, for spaced repetition.
- **1 Project rubric** — a design-style brain exercise (e.g. "Design a rate limiter for a public API") with a 5–8 item checklist the learner self-ticks.

## 6. Content JSON schema (TypeScript types live in `src/content/schema.ts`)
```ts
type TopicId = string; // kebab-case, stable
type Unit = 1|2|3|4|5|6|7;

interface Topic {
  id: TopicId;
  unit: Unit;
  order: number;           // global order across all topics
  title: string;
  summary: string;         // 1–2 sentences, shown on path node
  prereqs: TopicId[];
  guide: string;           // markdown
  questions: Question[];   // length 20
  flashcards: Flashcard[]; // length 8
  project: ProjectRubric;
}

type Question =
  | { id: string; type: 'mcq';        prompt: string; choices: string[]; answerIndex: number;       explanation: string; tags: string[] }
  | { id: string; type: 'multi';      prompt: string; choices: string[]; answerIndexes: number[];    explanation: string; tags: string[] }
  | { id: string; type: 'order';      prompt: string; items: string[];   correctOrder: number[];     explanation: string; tags: string[] }
  | { id: string; type: 'match';      prompt: string; left: string[];    right: string[]; pairs: [number, number][]; explanation: string; tags: string[] }
  | { id: string; type: 'fillBlank';  prompt: string; accepted: string[]; /* already lowercased, trimmed, synonyms included */ explanation: string; tags: string[] }
  | { id: string; type: 'codeOutput'; prompt: string; code: string; choices: string[]; answerIndex: number; explanation: string; tags: string[] };

interface Flashcard { id: string; front: string; back: string; tags: string[]; }

interface ProjectRubric {
  brief: string;           // 150–300 words
  checklist: { id: string; text: string; weight: number }[]; // weights sum to 100
  hints: string[];         // pre-written, shown on demand
}
```
Every `Question.tags[]` entry must be a concept tag reused by remediation (§9).

## 7. Deterministic scorer — `src/lib/scorer.ts`
Pure function, no LLM, 100% offline. For each question type:
- `mcq` / `codeOutput` — index equality.
- `multi` — set equality of selected indexes.
- `order` — array equality.
- `match` — set equality of pair tuples.
- `fillBlank` — normalize (lowercase, trim, collapse whitespace, strip punctuation) → membership in `accepted[]`.

Return `{ correct: boolean; partialCredit?: number; failedTags: string[] }`.
Quiz score = `correctCount / 5`. Pass threshold = **0.8**.

## 8. Spaced repetition (SM-2 lite) — `src/lib/scheduler.ts`
Goal: user learns one or two topics today, revises them after a few days, then again, until permanent.

Per topic store `{ ease: number; intervalDays: number; dueAt: ISODate; lapses: number }`.
Default ease 2.5, initial interval 1 day.

After each **review** (triggered from Home's "Due today" list, not the first-pass quiz):
- Score ≥ 0.8 → `interval = round(interval * ease)`, `ease += 0.1` (cap 3.0).
- 0.5 ≤ score < 0.8 → `interval = max(1, round(interval * 0.6))`, `ease -= 0.15`.
- Score < 0.5 → `interval = 1`, `ease = max(1.3, ease - 0.3)`, `lapses += 1`.

Next `dueAt = now + interval days`.

Flashcards use the same algorithm, tracked per-card (not per-topic), surfaced in a dedicated `/review` screen.

## 9. Adaptive loop
1. User opens a topic → reads guide → starts quiz (5 questions sampled from the 20).
2. Scorer runs → if pass (≥ 0.8): +20 XP, celebration, topic marked `learned`, scheduled for review in 1 day, next topic unlocked.
3. If fail: collect `failedTags[]`, render a **remediation panel** — filtered slice of the guide showing only sections whose frontmatter tags intersect `failedTags`. Lose 1 heart. Retry with a fresh 5-question sample biased toward `failedTags`.
4. Hearts: 5 max, regen 1 per 30 min (wall-clock, persisted). At 0 hearts, user can still read guides and do flashcards, but quiz is locked for 30 min.
5. Streak: increments once per calendar day when at least one topic is learned OR at least 10 review cards are completed.
6. every 20 min of active use, show an intrusive but playful "Take a break! Look 20m away!" modal with a 2-min timer and confetti. User can dismiss immediately, but if they stay, they get a streak boost (skip next day's requirement). 

## 10. Project rubric grading
Every project, every quiz, every flashcard run logs a rubric entry. For projects specifically:
- User reads brief, does the brain exercise (no code required; thinking + short notes).
- User ticks checklist items honestly.
- `score = sum(tickedWeights)`. ≥ 80 → pass, XP awarded, topic's project marked complete.
- Hints (pre-written, bundled) revealed one at a time; revealing a hint caps max score at 90, then 80, then 70.

## 11. Cross-device sync (offline-compatible)
- Settings screen has **Export progress** → downloads `cs-mastery-progress-<date>.json` (all localStorage keys under namespace `csm:*`).
- **Import progress** → file picker → validate via Zod-style runtime check → merge strategy: take the record with the **later `updatedAt`** per key.
- AirDrop workflow: export on Mac → AirDrop to iPhone → open file → Safari routes to the PWA's `/import?file=…` handler. Document this in README.
- No cloud, no accounts.

## 12. Screens (React Router 7)
- `/` **Home** — vertical Duolingo-style path of unit → topics; current node pulsing; top bar shows XP, streak flame, hearts; "Due for review: N" card opens `/review`.
- `/topic/:id` — markdown guide via `react-markdown`; sticky "Start quiz" CTA; "Flashcards" and "Project" secondary CTAs.
- `/quiz/:id` — one question at a time, progress bar, instant feedback, remediation on fail.
- `/result/:id` — pass: confetti + "Next topic" / "Start review in 1 day" / "Try project". fail: summary of failed tags + "Retry" / "Back to guide".
- `/project/:id` — brief, checklist, hints-on-demand, submit.
- `/review` — mixed queue of due topics + due flashcards.
- `/flashcards/:id` — single-topic flashcard drill.
- `/settings` — export/import, reset progress, toggle sound/animations, theme.

## 13. File layout
```
src/
  main.tsx
  App.tsx                       # router shell only
  routes/
    Home.tsx
    Topic.tsx
    Quiz.tsx
    Result.tsx
    Project.tsx
    Review.tsx
    Flashcards.tsx
    Settings.tsx
  components/
    PathNode.tsx
    GuideView.tsx
    QuizCard.tsx               # renders any Question type
    FlashcardDeck.tsx
    RubricChecklist.tsx
    HeartsBar.tsx
    XPBar.tsx
    StreakFlame.tsx
    Confetti.tsx
    DueTodayCard.tsx
  content/
    schema.ts
    index.ts                    # imports all topic JSONs, exports typed array
    topics/
      linux-essentials.json
      git-fundamentals.json
      … (37 files total)
  lib/
    scorer.ts
    scheduler.ts                # SM-2 lite
    storage.ts                  # typed localStorage wrapper, namespace 'csm:'
    sync.ts                     # export/import
    normalize.ts                # string normalization for fillBlank
  state/
    ProgressContext.tsx
    HeartsContext.tsx
  styles/
    tailwind.css
  test/
    scorer.test.ts
    scheduler.test.ts
```

## 14. Build & delivery checklist (deliverables in this pass)
1. Remove boilerplate from `src/App.tsx` and `src/App.css`.
2. Install Tailwind; wire `styles/tailwind.css`; delete unused demo CSS.
3. Install `vite-plugin-pwa`, configure manifest (name "CS Mastery", short_name "CSM", theme color, standalone, 192/512 icons under `public/`).
4. Install `react-markdown`, `remark-gfm`, `idb`, `vitest`.
5. Implement `content/schema.ts` and `content/index.ts`.
6. Generate all 37 `content/topics/*.json` files conforming to schema. (Content-generation is a separate long-running task; the coding agent should stub 3 topics fully and leave clearly-marked placeholders for the remaining 34, each with a TODO comment and the topic id/title/order/prereqs pre-filled. A follow-up pass will fill them.)
7. Implement `lib/scorer.ts` + vitest coverage for all 6 question types.
8. Implement `lib/scheduler.ts` + vitest coverage for the 3 branches.
9. Implement `lib/storage.ts` with namespaced keys, `updatedAt` per write, typed getters/setters.
10. Implement `lib/sync.ts` (export download + import merge).
11. Implement all 8 screens with mobile-first Tailwind layouts.
12. Implement hearts regen timer with wall-clock persistence.
13. Implement streak counter with calendar-day logic (respect local timezone).
14. Wire `framer-motion` celebrations on pass and on streak increment.
15. Update `README.md` (see companion file).
16. Run `npm run build` and verify PWA audit passes (installable, works offline after first load).

## 15. Non-goals
- Auth, multi-user, cloud storage, payments.
- Runtime LLM calls or any network fetches beyond the initial asset load.
- Writing code inside the project rubric (brain exercise only).
- Native iOS/Android wrappers (PWA install is sufficient for v1).

## 16. Acceptance criteria
- `npm run dev` boots with no console errors.
- `npm run build && npm run preview` serves an installable PWA that passes Lighthouse "Installable" + "Works offline".
- 3 fully-authored topics work end-to-end: guide renders, quiz grades deterministically, flashcards schedule, project rubric awards XP.
- Export → reset → import restores state exactly.
- No network requests after first load (verify in DevTools offline mode).
