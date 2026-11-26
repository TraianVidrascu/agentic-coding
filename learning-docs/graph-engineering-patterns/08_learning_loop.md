# Learning Loop (Retrospective)

**After runs, an agent looks at what went wrong *repeatedly* and proposes updates to the instructions, so the next run avoids it.**

```
runs ──► logs (review issues, blocks, escalations, decisions)
              │
              ▼
      retrospective agent ──► proposed diff to CLAUDE.md / rules / skills / agent prompts
              │
              ▼
      [HUMAN: approve] ──► eval set (07) ──► keep if no regression
```

- Agents don't learn between sessions. The **files** are the memory (`basics/02`).
- Without this loop, the same reviewer comment shows up every week.

## What to learn from

| Signal | Example | Becomes |
|---|---|---|
| a recurring review issue | "SQL in route" flagged 3× this month | a rule in `.claude/rules/backend.md` |
| a recurring block | executors blocked on "where is week logic?" | a map line in CLAUDE.md |
| a repeated human correction | "use `mondayOf`, not `getDay()` math" | a rule + a negative example |
| a wasted search | 5 agents grepped for the same helper | a codebase-map entry |
| an escaped bug | a bug found after merge | an eval case (`07`) + a reviewer checklist item |

## Rules for safe learning

- **Evidence threshold:** only patterns seen **≥3 times**. One-offs don't belong in CLAUDE.md.
- **Smallest scope:** a path-scoped rule > CLAUDE.md. An agent prompt > a global rule.
- **Prune as well as add:** remove rules that never fire, or that duplicate others. CLAUDE.md must stay short.
- **Human approves every change.** Agents editing their own instructions without review is drift.
- **Check with evals:** a new rule must not break other cases.

## Example: retrospective agent

`.claude/agents/retro.md`:
```markdown
---
name: retro
description: Reviews recent pipeline logs and proposes instruction updates. Use weekly or after a failed run.
tools: Read, Bash
model: opus
---
Read .work/*/decisions.md, .work/*/progress.md, and the review issues in .work/reviews.jsonl.
1. Group the issues by root cause. Keep only causes seen 3 or more times.
2. For each one, propose the SMALLEST fix: a rule (with paths), a codebase-map line, a checklist item or an eval case.
3. Also list rules in CLAUDE.md and .claude/rules/ that look unused or duplicated.
Reply with: cause | count | evidence (run ids) | proposed diff. Do not edit files.
```
Then: review the proposals → apply the good ones → run the evals → commit.

## Failure modes

| Failure | Fix |
|---|---|
| CLAUDE.md bloat | evidence threshold + pruning + path-scoped rules |
| learning from noise | ≥3 occurrences, with evidence links |
| conflicting rules over time | the retro also checks for contradictions |
| silent drift | the human approves + the eval set gates each change |
