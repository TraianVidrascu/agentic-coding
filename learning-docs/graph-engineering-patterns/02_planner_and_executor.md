# Planner and Executor

**A strong model thinks once, cheaper models do the work.**

```
spec generator ──spec.md──► human approves ──► planner (strong, read-only) ──plan──► human approves ──► executors (cheaper, edit + test) ──► reviewer checks against the spec
   (WHAT)                                         (HOW)        ▲                                                │
                                                               └──────────── "blocked: <reason>" ──────────────┘
```

## Spec stage (before planning)

**First pin down *what* to build. Then plan *how*.**

| | Spec | Plan |
|---|---|---|
| answers | **what + why**: behavior, API, edge cases, acceptance tests | **how**: tasks, files, order |
| lives in | the repo (`docs/specs/<feature>.md`), and survives `/clear` | the current run |
| used by | humans, planner, executors, reviewer | executors |
| role | the **source of truth** that everything is checked against | splits up the work |

### Spec generator agent

`.claude/agents/spec-writer.md`:
```markdown
---
name: spec-writer
description: Turns a feature request into a spec file. Use before planning any non-trivial feature.
tools: Read, Bash, Write
model: opus
---
1. Read the request, CLAUDE.md and the related code.
2. Ask the user up to 5 questions about anything unclear (behavior, edge cases, UI). Wait for the answers.
3. Write docs/specs/<feature>.md using the template below. No implementation details. No file lists.
4. Every acceptance criterion must be testable (input → expected output).
```

Spec template:
```markdown
# <Feature>
## Goal            one or two sentences: what + why
## Behavior        what the user can do, step by step
## API / UI        endpoints, params, status codes; UI elements
## Edge cases      the tricky inputs and what happens
## Out of scope    what this does NOT do
## Acceptance      testable checks, e.g. "GET /api/export.csv?from=2026-11-16&to=2026-11-22 → 200, text/csv, 1 row per entry"
```

### How the spec flows through the graph

- **Human:** reviews the spec. This is the cheapest gate, since no code exists yet (Axioms 4, 8).
- **Planner:** gets the spec path and turns each `Acceptance` item into a task `acceptance` check.
- **Executors:** get their task plus the spec's relevant sections, not the whole conversation.
- **Reviewer:** checks the diff **against the spec**: "does each acceptance item pass? anything out of scope?" (`01`).
- **Spec changes:** update the spec first, then re-plan. The spec stays the source of truth.

### A well-defined Jira task *is* a spec

If the ticket already covers the template, don't write a separate spec. The ticket is the source of truth.

Example ticket `TIME-42`:
```
Summary:      Export the current week as CSV
Description:  Users need to send their weekly hours to payroll, which accepts CSV only.
Behavior:     A "Download CSV" button in the week navigation downloads the selected week.
API:          GET /api/export.csv?from=YYYY-MM-DD&to=YYYY-MM-DD → 200 text/csv
              columns: date,start,end,minutes,project,description
Edge cases:   - empty week → header row only
              - entry without project → empty project column
              - from > to → 422
Out of scope: Excel format, custom columns, exporting other weeks than the selected one.
Acceptance:   - [ ] week with 3 entries → 4 lines (header + 3), sorted by date then start
              - [ ] empty week → header only
              - [ ] from > to → 422
              - [ ] button downloads "timesheet-2026-11-16.csv"
```

| Ticket field | Spec section |
|---|---|
| Summary + Description | Goal (what + why) |
| Behavior, API | Behavior, API / UI |
| Edge cases | Edge cases |
| Out of scope | Out of scope |
| Acceptance checklist | Acceptance: each item becomes a test |

**"Well defined" = ready for agents:**
- every acceptance item is **testable** (input → expected output)
- edge cases are listed
- scope limits are stated
- no "TBD" and no "should be nice"

The flow with Jira (read-only MCP, `basics/07_mcp.md`):
1. **spec-writer** fetches the ticket and checks it against the template.
   - Complete: the ticket is used as the spec, with no new file.
   - Gaps: it asks you, or drafts a comment for the ticket, rather than guessing. Fix the ticket, not a side document, so the team sees it too.
2. **Planner** gets the ticket key (`TIME-42`) instead of a spec path.
3. **Reviewer** checks the diff against the ticket's acceptance checklist.

Skip the spec for small changes. A clear one-line request is already the spec.

## Planner agent

- **Strong model, high effort** (e.g. `opus`). Planning mistakes compound through every step after (Axiom 4), so this is where capability pays off most.
- **Read-only tools** (`Read`, `Bash` for `rg`/`git`). It explores and decides, and never edits.
- **Output = a structured plan.** Each task has:

| Field | Why |
|---|---|
| `id`, `goal` | one clear job per task |
| `files` | the scope. Tasks with **no overlapping files** can run in parallel |
| `acceptance` | tests or commands that prove it's done (the anchor) |
| `depends_on` | the order. Independent tasks run in parallel |

- Good plan tasks are **small enough for a cheaper model**: one file or function, a clear acceptance check.

## Executor agent

- **Medium or cheap model** (`sonnet`; `haiku` for mechanical edits). The plan already did the hard thinking.
- **Narrow input:** one task, plus only the files it lists (Axiom 5).
- **Edit tools + tests.** It must run its acceptance check before reporting.
- **Doesn't re-plan.** If the task is wrong or impossible, it reports `blocked` with a reason instead of improvising.
- **Structured result:** `{status: done|blocked, summary, reason?}`.
- Parallel executors: one **worktree** each (`isolation: 'worktree'`).

## Planner/executor tandem

| Variant | How | Use when |
|---|---|---|
| static | plan once, execute everything | well-understood features |
| re-plan on block | a blocked executor sends its reason to the planner, which revises the remaining tasks | some unknowns |
| plan → execute → verify | adds an adversarial reviewer loop (`01`) after the executors | anything shipped |

In Claude Code, by hand:
- **Plan mode** (shift+tab) gives you a reviewable plan before any edit, which is your human gate.
- The `opusplan` model setting uses Opus while planning and Sonnet while executing.

### Variant: orchestrator-workers (dynamic)

The plan isn't fixed up front. A lead agent decides the next workers **at runtime**, based on what earlier workers found.

| Static planner/executor | Orchestrator-workers |
|---|---|
| plan once (+ re-plan on block) | decide after each result |
| tasks known up front | unknown scope ("find and fix all date bugs") |
| easy to review and approve | harder to predict cost. Cap the rounds |

In a workflow, it's a loop: lead agent → `{next_tasks}` → run the workers → feed the results back to the lead → stop when the lead returns no tasks, or the round cap is hit.

## Failure modes

| Failure | Fix |
|---|---|
| vague tasks ("improve the API") | require `files` + `acceptance` for every task |
| executors overlap and conflict | the planner must split by file. Use worktrees |
| an executor silently re-plans | prompt "if the task doesn't fit, return blocked" and check the `status` |
| over-planning (20 tasks for a small change) | cap the tasks. Small changes skip the planner |
| a stale plan after a block | re-plan the **remaining** tasks, not the finished ones |

## Example: CSV export (exercise 2)

Spec first, then two workflows with a human in between (Axiom 8: approve before any code).

**0. Spec:** *"use the spec-writer agent for exercise 2 (CSV export)"*. Answer its questions, then review `docs/specs/csv-export.md`.

**1. Plan** (from the spec; returns the plan for you to review):
```js
export const meta = { name: 'plan-feature', description: 'Plan a feature as small, parallel tasks' }

const PLAN = { type: 'object', properties: { tasks: { type: 'array', items: { type: 'object', properties: {
  id: { type: 'string' }, goal: { type: 'string' }, files: { type: 'array', items: { type: 'string' } },
  acceptance: { type: 'string' }, depends_on: { type: 'array', items: { type: 'string' } } },
  required: ['id', 'goal', 'files', 'acceptance', 'depends_on'] } } }, required: ['tasks'] }

return await agent(`Plan the spec at ${args.spec} for mock_up/. Read CLAUDE.md conventions and the relevant code.
  Max 5 tasks. No two tasks may touch the same file.
  Every Acceptance item in the spec must be covered by some task's runnable acceptance check.`,
  { schema: PLAN, model: 'opus', effort: 'high', agentType: 'Plan' })
```
→ e.g.:
```json
[{ "id": "api",  "goal": "GET /api/export.csv?from=&to= in main.py + repository query",
   "files": ["src/core/main.py", "src/core/repository.py", "tests/test_api.py"],
   "acceptance": "python -m pytest tests/test_api.py -k csv", "depends_on": [] },
 { "id": "ui",   "goal": "Download button in WeekNav calling api.exportCsv",
   "files": ["src/frontend/src/api.js", "src/frontend/src/components/WeekNav.jsx"],
   "acceptance": "cd src/frontend && npm run build", "depends_on": [] },
 { "id": "docs", "goal": "Add endpoint row to API table",
   "files": ["docs/architecture.md"], "acceptance": "grep export.csv docs/architecture.md", "depends_on": ["api"] }]
```

**2. You review and edit the plan, then execute:**
```js
export const meta = { name: 'execute-plan', description: 'Execute approved plan tasks, re-plan on block' }

const RESULT = { type: 'object', properties: { status: { type: 'string', enum: ['done', 'blocked'] },
  summary: { type: 'string' }, reason: { type: 'string' } }, required: ['status', 'summary'] }

const done = new Set(), results = {}
let pending = args.tasks
while (pending.length) {
  const ready = pending.filter(t => t.depends_on.every(d => done.has(d)))
  if (!ready.length) return { status: 'deadlock', pending, results }

  const out = await parallel(ready.map(t => () => agent(
    `Task: ${t.goal}. Only touch: ${t.files.join(', ')} (in mock_up/).
     Done = this passes: ${t.acceptance}. Commit when green.
     If the task is wrong or impossible as written, return status "blocked" with the reason. Don't improvise.`,
    { schema: RESULT, model: 'sonnet', isolation: 'worktree', label: `exec:${t.id}` })))

  ready.forEach((t, i) => { results[t.id] = out[i]; if (out[i]?.status === 'done') done.add(t.id) })
  const blocked = ready.filter((t, i) => out[i]?.status !== 'done')
  pending = pending.filter(t => !done.has(t.id))

  if (blocked.length) {   // re-plan only the remaining work
    const re = await agent(`These tasks were blocked: ${JSON.stringify(blocked.map(t => ({ ...t, why: results[t.id]?.reason })))}.
      Finished: ${[...done].join(', ') || 'none'}. Revise ONLY the remaining tasks: ${JSON.stringify(pending)}.`,
      { schema: { type: 'object', properties: { tasks: { type: 'array', items: { type: 'object' } } }, required: ['tasks'] },
        model: 'opus', label: 'replan' })
    pending = re.tasks
  }
}
return { status: 'done', results }
```

| Piece | Axiom |
|---|---|
| opus plans, sonnet executes | spend capability where errors compound (4) |
| human reviews the plan between the workflows | human gate (8) |
| `acceptance` per task | an anchor at every node (1, 2) |
| files per task, worktrees | minimal context, no collisions (5) |
| `blocked` → re-plan the remaining tasks | stops a wrong plan from compounding (4) |
| dependencies, loop, deadlock check in code | deterministic edges (6) |

Next step: run the adversarial review loop (`01`) on the merged result, with the spec's `Acceptance` section as the reviewer's criteria.

Note: the re-plan loop has no round limit. In real use, cap the number of re-plans (e.g. 2), then stop and escalate to a human (see the stop conditions in `01`).
