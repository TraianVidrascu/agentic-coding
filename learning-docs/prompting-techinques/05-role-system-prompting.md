# Role / System Prompting

**Tell the model who it is and what rules it works under, before giving the task.**

- **System prompt**: set once and applies to the whole conversation (role, rules, format).
- **Role**: "You are a code reviewer for a FastAPI + React app" focuses its knowledge and tone.
- In Claude Code you write system prompts as:
  - **agent bodies** (`.claude/agents/*.md`)
  - **skills**
  - **CLAUDE.md** (project rules)

## What actually helps

| Helps | Helps little |
|---|---|
| specific role + context: "reviewer for *this* app, focused on SQL safety" | generic flattery: "You are a world-class genius engineer" |
| rules with reasons: "no SQL in routes, so all queries are testable in one place" | ALL CAPS, "VERY IMPORTANT!!!" |
| the audience: "explain for a backend dev new to React" | long biographies of the persona |
| the output format | repeating the same rule three times |

## When to use

- Every agent or skill: it's their system prompt.
- When a fixed perspective matters: reviewer, tester, security auditor, teacher.
- To set the tone or level of the explanation.

## Example 1: agent system prompt

`.claude/agents/sql-reviewer.md`:
```markdown
---
name: sql-reviewer
description: Reviews SQL changes in mock_up for safety. Use after editing repository.py or db.py.
tools: Read, Bash
---
You review SQL in a small FastAPI + sqlite3 timesheet app (mock_up/).

Rules to check:
- Only parameterized queries (`?`), never f-strings or string concatenation. This prevents SQL injection.
- All SQL in src/core/repository.py. This keeps queries in one testable place.
- Schema changes in db.py need a manual migration plan, because there are no migrations.

Reply with `file:line | issue | fix`, or "No issues".
```

## Example 2: role for explanation level

```
You're explaining this codebase to a backend developer who knows Python well but has never used React.
Explain how App.jsx's run() wrapper refreshes data after a mutation. Compare it to a Python pattern they'd know.
```

## Bad example: vague persona, no rules

```
You are an amazing, world-class senior engineer with 20 years of experience. Review this code.
```
What's wrong:
- The flattery adds nothing.
- No codebase context, rules or output format.
- You get a generic review that misses project rules.

Fix: Example 1. Specific role + rules + reasons + format.

## Tips

- Role = **who + for what codebase + which focus**.
- Give rules a short *why*. The model applies the reason to cases you didn't list.
- Keep system prompts short: they're sent on every turn (and cached).
- Put the task in the user prompt, and the stable role and rules in the system prompt.
