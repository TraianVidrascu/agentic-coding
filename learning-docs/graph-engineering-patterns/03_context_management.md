# Context Management Across Agents

**Design what each agent sees, what it hands on, and what survives.**

Single-agent context (sessions, caching, the starting context) is covered in `basics/02` and `codebase-search-optimization/05`.
This doc is about context **between** agents, where most graphs fail (Axiom 5).

```
         ┌──────────── shared state on disk (spec.md, plan.json, progress.md) ────────────┐
         ▼                    ▲                      ▲                     ▲              │
   spec-writer ──contract──► planner ──contract──► executor ──contract──► reviewer        │
   (fresh)                   (fresh)               (fresh, worktree)      (fresh)          │
         └──────── each one: small input in, structured summary out ────────────────────┘
```

## 1. Hand-off contracts

**Each agent gets a defined input and returns a defined output. Never "the whole conversation".**

| Agent | Receives | Returns |
|---|---|---|
| spec-writer | request + pointer to CLAUDE.md | `docs/specs/<f>.md` (file) |
| planner | spec path | `plan.json`: tasks with files and acceptance checks |
| executor | 1 task + its files + the relevant spec sections | `{status, changed_files, decisions, summary}` |
| reviewer | diff + spec `Acceptance` | `{issues: [{file, line, problem, evidence}]}` |

- Enforce the outputs with a `schema` in workflows, or a strict "Reply ONLY with…" in agent prompts.
- Inputs: **pointers over copies** ("read `docs/specs/csv.md` sections API and Edge cases"), not pasted text.

## 2. Shared state on disk (blackboard)

**Agents coordinate through files, not through prompts.**

- Files are lasting: they survive `/clear`, crashes and new sessions. They can be looked at (`cat progress.md`) and tracked in git.
- Each agent reads only the files it needs, when it needs them.
- **One writer per file** avoids conflicts: the planner owns `plan.json`, each executor owns its own section of `progress.md`, or its own file.

| File | Written by | Read by |
|---|---|---|
| `docs/specs/<f>.md` | spec-writer (+ human) | everyone |
| `.work/<f>/plan.json` | planner | orchestrator, executors |
| `.work/<f>/progress.md` | orchestrator / executors | next session, humans |
| `.work/<f>/decisions.md` | any agent (append only) | later agents, reviewer |

Add `.work/` to `.gitignore` if it's scratch. Commit it if the team should see it.

## 3. Fresh vs forked vs resumed

| Mode | Starts with | Use for | Risk |
|---|---|---|---|
| **fresh** | only its prompt | reviewers, executors, anything that needs an unbiased view | missing context, so brief it well |
| **forked** | a copy of the current conversation | side tasks that need everything said so far | heavy context, biased by it |
| **resumed** (`SendMessage`) | its own past context | follow-ups in the same area, soon | stale files, a growing context |

Default to **fresh**. Reviewers must be fresh (Axiom 7: independence).

## 4. Summarize at the boundaries

**Shrink the output before it goes up to the orchestrator, with a fixed format.**

Bad: the executor returns its whole story ("First I read main.py, then I tried…").
Good:
```json
{ "status": "done",
  "changed_files": ["src/core/main.py", "src/core/repository.py", "tests/test_api.py"],
  "decisions": ["CSV rows sorted by date, start", "empty project → empty column, not '(no project)'"],
  "open_questions": [],
  "summary": "GET /api/export.csv added; 3 tests pass" }
```
- `decisions` matter most. They're what later agents need and what usually gets lost.
- Append the decisions to `decisions.md` so they outlive the run.

## 5. Progress files for long tasks

**Write down state so any agent (or you, after `/clear`) can pick up where it stopped.**

`.work/csv-export/progress.md`:
```markdown
# CSV export (TIME-42): progress
## Done
- api: GET /api/export.csv + tests (commit a1b2c3)
## In progress
- ui: download button (executor in worktree ui-csv)
## Next
- docs: API table row
## Blockers
- none
## Decisions
- rows sorted by date, then start
- filename: timesheet-<monday>.csv
```
Resume prompt: *"Read .work/csv-export/progress.md and continue from Next."*

## 6. Context budget per agent

Keep each agent's working context small:
- **Limit tool output:**
  - "max 10 results"
  - "show only failing tests": `pytest -q 2>&1 | tail -20`
  - hooks that trim output (`codebase-search-optimization/04`)
- **Narrow tools and model** per agent (`codebase-search-optimization/05`, reduced context start).
- **Big exploration → a subagent.** Only its summary enters the orchestrator.
- **Long-running orchestrator?** Keep its own context to the contracts and the state files. Never raw tool output.

## 7. Cache-aware layout

- Same agent type and model for parallel workers means a shared cached start.
- Warm up one agent before fanning out (`codebase-search-optimization/05`).
- Put stable parts first (role, rules, spec) and the changing part last (the task).

## Failure modes

| Failure | Symptom | Fix |
|---|---|---|
| context rot | a long orchestrator forgets early decisions | state on disk + fresh agents |
| lost decisions | a later agent undoes an earlier choice | a `decisions` field + `decisions.md` |
| transcript dumping | the orchestrator's context fills with agent stories | fixed summary contracts |
| under-briefing | a fresh agent redoes the research or guesses | pointers to spec, plan and decisions in every prompt |
| stale shared files | an agent acts on an old plan or progress | one writer per file, and re-read it before acting |
| conflicting writes | two agents edit the same state file | one writer per file, or one file per agent |

## Example: CSV export pipeline, context view

The same pipeline as `02`, showing exactly what moves between agents:

```
request "TIME-42"
  │
  ▼ spec-writer (fresh)         in:  ticket key + CLAUDE.md          out: ticket confirmed as spec (or spec.md)
  ▼ planner (fresh, opus)       in:  spec                             out: .work/csv-export/plan.json
  ▼ executor ×3 (fresh, sonnet) in:  1 task + files + spec sections   out: {status, changed_files, decisions}
  │                                                                    + append to decisions.md, progress.md
  ▼ reviewer ×3 (fresh)         in:  diff + spec Acceptance           out: {issues[]}
  ▼ orchestrator                holds: contracts + state file paths. Never transcripts.
```

Executor prompt (with the hand-off contract):
```
Task "api" from .work/csv-export/plan.json.
Read: the spec sections "API" and "Edge cases" from TIME-42, and .work/csv-export/decisions.md.
Touch only: src/core/main.py, src/core/repository.py, tests/test_api.py (in mock_up/).
Done = python -m pytest tests/test_api.py -k csv passes.
Append any decisions to .work/csv-export/decisions.md.
Reply ONLY with JSON: {status, changed_files, decisions, open_questions, summary}.
```

| Piece | Pattern |
|---|---|
| "Read: spec sections…, decisions.md" | pointers over copies (1), shared state (2) |
| fresh executor in a worktree | fresh by default (3) |
| JSON reply with `decisions` | summarize at the boundaries (4) |
| `progress.md` updated per task | survives `/clear` (5) |
| "Touch only…", one file per contract | budget and conflict control (6) |
