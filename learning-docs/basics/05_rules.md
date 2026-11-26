# Rules

## What are rules?

**Instruction files split out of CLAUDE.md, each one optionally limited to certain file paths.**

- They live in `.claude/rules/*.md` (project) or `~/.claude/rules/*.md` (personal).
- With no `paths`, a rule loads every session, just like CLAUDE.md.
- With `paths`, it loads only when the agent works on matching files.
- Why: a smaller CLAUDE.md, and context spent only on rules that matter right now.

## How are rules attached?

With `paths` in the frontmatter: glob patterns matched against the files the agent touches.

```yaml
---
paths:
  - "mock_up/src/frontend/**/*.jsx"
  - "mock_up/src/frontend/**/*.js"
---
```

Rules attach to **files**, not to agents. For agent-specific instructions, put them in the agent's own body (see `04_custom_agents.md`).

## Are they enough? Bulletproof?

**No.** A rule is just text in the context, and the model *can* ignore it:

- in long or cluttered sessions (context pollution)
- when it conflicts with the user prompt or another rule
- when it's vague ("write clean code")

When something **must** happen, enforce it in code:

| Need | Use |
|---|---|
| block a command or file | `permissions.deny` in `.claude/settings.json` |
| always run X after an edit | a **hook** (e.g. run the formatter after each `Edit`) |
| catch violations | tests, linters, CI |

Rule of thumb: **rules guide, hooks and tests enforce.**

## Advice

- One topic per file: `frontend.md`, `testing.md`, `api.md`.
- Specific and checkable: "use `mondayOf()` from `dates.js`", not "handle dates well".
- Say why in a few words. The model follows rules better when it knows the reason.
- No duplicates of CLAUDE.md, and no contradictions between rules.

## Example: explaining each part

`.claude/rules/frontend.md`:
```markdown
---
paths:
  - "mock_up/src/frontend/src/**/*.{js,jsx}"
---

# Frontend rules

- Only `src/api.js` calls `fetch`. Components get data via props.
- State lives in `App.jsx`. After a mutation, reload through the `run()` wrapper.
- Dates: use local-time helpers in `dates.js`. Never `toISOString()`, it shifts the day in UTC.
- Weeks start Monday (`mondayOf`).
```

| Part | Why it's there |
|---|---|
| `paths` | loads only when frontend files are touched; backend work doesn't pay for it |
| `{js,jsx}` glob | one pattern covers both file types |
| one bullet per rule | short and easy to check |
| "it shifts the day in UTC" | the reason makes the rule stick |

# Appendix: All ways to instruct the agent, from soft to hard

| Mechanism | Loads | Enforced? |
|---|---|---|
| User prompt | this turn | no, guidance |
| CLAUDE.md | every session | no, guidance |
| Rules (no `paths`) | every session | no, guidance |
| Rules (with `paths`) | when matching files are touched | no, guidance |
| Memory | index every session, files when relevant | no, guidance |
| Skills | when invoked | no, guidance |
| Agent body | inside that agent only | no, guidance |
| Permissions | always, checked by the harness | **yes**, blocks or allows tools |
| Hooks | always, run by the harness on events | **yes**, a script always runs and can block the action |
| Tests / CI | when run | **yes**, fails the build |
