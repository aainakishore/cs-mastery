# Frontend Frameworks Expansion Prompt

> **Goal:** Add Angular, TypeScript, and React as new topic clusters under Unit 10 (Frontend Frameworks), each with multiple sub-topics, organised into sub-folders inside `src/content/topics/`.

---

## 1. Scope

Create three new topic clusters as **sub-folders** under `src/content/topics/`:

```
src/content/topics/
├── angular/
├── typescript/
└── react/
```

Each cluster contains multiple sub-topic JSON files (one file per concept).

### Required sub-topics

#### `typescript/` — TypeScript Fundamentals → Advanced
1. `ts-fundamentals.json` — types, type inference, narrowing
2. `ts-interfaces-types.json` — interface vs type, structural typing
3. `ts-generics.json` — generic functions, classes, constraints
4. `ts-utility-types.json` — Partial, Pick, Omit, Record, ReturnType
5. `ts-advanced-types.json` — conditional types, mapped types, infer
6. `ts-decorators.json` — class/method/property decorators, metadata
7. `ts-modules.json` — ES modules, namespaces, ambient declarations
8. `ts-tsconfig.json` — compiler options, strict mode, paths

#### `react/` — React Core → Advanced
1. `react-fundamentals.json` — JSX, components, props, virtual DOM
2. `react-state-effects.json` — useState, useEffect, dependency arrays
3. `react-hooks.json` — useMemo, useCallback, useRef, useReducer, custom hooks
4. `react-context.json` — Context API, Provider patterns, performance pitfalls
5. `react-rendering.json` — reconciliation, keys, memo, re-render causes
6. `react-router.json` — routing, nested routes, loaders, navigation
7. `react-forms.json` — controlled/uncontrolled, validation, libraries
8. `react-performance.json` — code splitting, lazy, Suspense, profiling
9. `react-server-components.json` — RSC, server actions, streaming

#### `angular/` — Angular Core → Advanced
1. `angular-fundamentals.json` — modules, components, templates, lifecycle
2. `angular-data-binding.json` — interpolation, property/event/two-way binding
3. `angular-directives.json` — structural (*ngIf, *ngFor) vs attribute, custom
4. `angular-services-di.json` — services, providedIn, hierarchical injectors
5. `angular-rxjs.json` — Observables, operators, subscription management
6. `angular-routing.json` — RouterModule, guards, lazy loading, resolvers
7. `angular-forms.json` — template-driven vs reactive, validators
8. `angular-signals.json` — signals API, computed, effect, change detection
9. `angular-standalone.json` — standalone components, modern bootstrap

---

## 2. Schema Conformance

Every JSON file MUST match `src/content/schema.ts` exactly:

```ts
interface Topic {
  id: string                 // kebab-case, must match filename without .json
  unit: 10                   // Unit 10 = Frontend Frameworks
  order: number              // global order continuing from existing topics
  title: string
  summary: string            // 1-2 sentences shown on path node
  prereqs: TopicId[]         // referenced topic ids that should be done first
  guide: string              // markdown — see §3 for quality bar
  questions: Question[]      // exactly 20 — see §4
  flashcards: Flashcard[]    // exactly 8 — see §5
  project: ProjectRubric     // see §6
}
```

### Order numbering

| Cluster | Order range |
|---|---|
| TypeScript | 80–87 |
| React | 88–96 |
| Angular | 97–105 |

The Vite glob loader (`./topics/**/*.json`) must continue to discover all JSONs — verify `import.meta.glob` pattern includes nested folders.

---

## 3. Guide Quality Bar (4000–6000 chars target)

Each guide is **markdown** and MUST include:

1. **Title heading** — `# <Title>`
2. **Mental model paragraph** — what is this concept *really*, in one analogy
3. **3–5 visual ASCII diagrams** showing memory/data flow/component tree
4. **3–5 runnable code examples** in fenced \`\`\`tsx / \`\`\`ts / \`\`\`html blocks
5. **Comparison table** when relevant (e.g. interface vs type, signals vs RxJS)
6. **Complexity / cost cheatsheet** — re-render cost, bundle size, etc. where applicable
7. **Common pitfalls section** — bullets, real bugs developers hit
8. **Connections section** — cross-links to related topics

### Tone & depth

- **Visual first** — reader should *see* the concept in their mind after reading
- **Mental effort over typing effort** — explain the *why*, not just the *how*
- **No fluff** — every paragraph must deliver a new mental model or trace
- **Real-world scenarios** — show what this looks like in production code, not toy examples

### Example diagram styles to include

For React rendering:
```
Component tree → Virtual DOM → Diff → Real DOM patches
     <App/>
     /    \\
  <Nav/>  <Page/>
            |
         <List/>
         /    \\
       <Item> <Item>   ← keys decide reuse vs unmount
```

For RxJS pipe:
```
Observable<click>
  ──┬─ .pipe(
    │    debounceTime(300),     ← swallow rapid clicks
    │    map(e => e.target),    ← transform
    │    distinctUntilChanged() ← drop duplicates
    │  )
  ──┴─ .subscribe(handler)
```

For TypeScript narrowing:
```
function process(x: string | number) {
                   ▲
                   │ x is widened union
  if (typeof x === 'string') {
                   ▼
    x.toUpperCase()  // narrowed to string here
  }
}
```

---

## 4. Questions — exactly 20 per topic

### Mix of types

Aim for this rough distribution per topic:
- **12–14 mcq** (single answer)
- **3–4 codeOutput** (read code → predict output)
- **2–3 multi** (multiple correct answers)
- **0–1 fillBlank** for terminology

### Quality rules

1. **No surface-level recall** — questions should require *thinking*, not memorisation
2. **Trace through provided code** — most code questions show a snippet and ask "what prints" or "what type is inferred"
3. **Test understanding of *why*** — not "what does useState do" but "why does this useState in a loop break"
4. **Cover all guide sections** — pitfalls section produces the trickiest questions
5. **Include subtle distractors** — wrong answers should be plausibly tempting
6. **Tags** — every question has 2–3 concept tags drawn from a consistent vocabulary used across the cluster (so remediation can match by tag)
7. **Explanation field** — must explain *why* the right answer is right AND *why* common wrong picks are wrong

### Question id convention

`<topic-prefix>-q<n>` where `<topic-prefix>` is initials, e.g.:
- `tsf-q1` for `ts-fundamentals`
- `rsf-q1` for `react-state-effects`
- `ang-fund-q1` for `angular-fundamentals`

---

## 5. Flashcards — exactly 8 per topic

- **Front**: a precise prompt (3–10 words) — a concept name, a method signature, or a "when do I use X?" question
- **Back**: a 1–2 sentence answer that includes the rule + a trigger ("use when…")
- Tags: 1–2 from same vocabulary as questions
- Cards should be **memorable but tough** — no trivia, every card unlocks a real production decision

### Example styles

| Front | Back |
|---|---|
| `useEffect dependency array` | Empty `[]` = run once on mount. Missing array = run every render. List vars = run when they change. Always declare every value used inside. |
| `interface vs type alias` | Both describe shapes. `interface` is open (declaration merging, classes can implement). `type` is closed but supports unions, mapped types. Default to `interface` for objects, `type` for everything else. |
| `Angular OnPush change detection` | Component re-renders only when input reference changes, an event fires, or an Observable emits. Use it as the default for performance — forces immutable patterns. |

---

## 6. Project Rubric

Each topic ships with one design-style brain exercise (no code execution required — thinking + short notes).

```ts
interface ProjectRubric {
  brief: string                                                  // 150-300 words
  checklist: { id: string; text: string; weight: number }[]      // 4-6 items, weights 1-each (sum doesn't need to be 100)
  hints: string[]                                                // 3-4 progressive hints
}
```

Project ideas should be **architecture / decision exercises**, not LeetCode-style coding:

- "Design the state shape for an e-commerce cart with optimistic updates, server sync, and offline support. Decide what's local state, Context, server state."
- "Sketch the Observable pipeline for a typeahead search component. Handle: debounce, race conditions, abort on unmount, error retry."
- "List every place a TypeScript narrowing failure could leak `any` into your form-handling code, and the type guard for each."

---

## 7. Implementation Plan

### Step 1 — Update schema/loader for nested folders

If `src/content/index.ts` uses `import.meta.glob('./topics/*.json')`, change to:
```ts
import.meta.glob('./topics/**/*.json', { eager: true })
```
This recurses into sub-folders automatically.

### Step 2 — Create folders and seed first topic

```
mkdir -p src/content/topics/{typescript,react,angular}
```

Author the first topic per cluster fully (`ts-fundamentals`, `react-fundamentals`, `angular-fundamentals`) as the quality reference for the rest.

### Step 3 — Generator script

Write `scripts/gen_frontend_topics.py` (or extend `gen_dsa_topics.py`) that:
1. Holds a `TOPICS` list of dicts conforming to schema
2. Validates structural fields (id, unit=10, 20 questions, 8 flashcards, guide ≥ 4000 chars)
3. Preserves hand-crafted topics (skip overwrite if questions ≥ 20 already)
4. Writes to the correct sub-folder based on a `cluster` key

### Step 4 — Validate

Run `scripts/validate_topics.py` after each batch — ensure:
- All files conform to schema
- All `prereqs` reference real topic ids
- No duplicate ids across all 19 + 26 = 45+ topics
- `npm run build` passes
- `npm test` passes (24 existing tests)

### Step 5 — UI sanity check

- Home view shows Unit 10 with the new topics in correct order
- First topic of each cluster is unlockable (no broken prereq)
- Markdown guides render (especially ASCII diagrams in code blocks)
- Quiz round-trips through `lib/scorer.ts` for all question types

---

## 8. Acceptance Criteria

- [ ] 26 new JSON topic files created (8 TS + 9 React + 9 Angular)
- [ ] All files in correct sub-folders
- [ ] Each file: 20 questions, 8 flashcards, guide ≥ 4000 chars
- [ ] All guides include ≥ 3 ASCII visual diagrams
- [ ] All questions force reasoning, not recall
- [ ] All explanations clarify wrong-answer traps
- [ ] `import.meta.glob` updated to recurse sub-folders
- [ ] `scripts/validate_topics.py` reports zero issues
- [ ] `npm run build` clean
- [ ] `npm test` 24/24 passing
- [ ] Home page renders Unit 10 with all 26 topics

---

## 9. Sourcing Guidance

When researching content, prefer sources that prioritise **conceptual depth and visualisation** over API reference dumping:

- **TypeScript** — official handbook deep-dives (narrowing, generics chapters); Matt Pocock's TS course-style explanations
- **React** — react.dev's "thinking in React" + "Escape Hatches" sections; Dan Abramov's blog (overreacted.io) for rendering/closure intuition
- **Angular** — angular.dev's "core concepts" pages; Minko Gechev's articles on change detection internals; RxJS marble diagrams
- **Universal** — anything that uses diagrams, marble notation, mental models, or "what's actually happening under the hood"

Do **NOT** copy verbatim — the writing must be original, condensed, and visualised. Each guide is a *re-explanation*, not a quote.

---

## 10. Done Definition

The user should be able to:
1. Open the app
2. Navigate to Unit 10 → click any frontend topic
3. Read a guide that visually explains the concept and *makes them see it*
4. Take a quiz that forces them to think, not regurgitate
5. Review flashcards that test real production decisions
6. Complete a project rubric that exercises architectural reasoning
7. Pass the topic and feel they've genuinely understood — not just passed

