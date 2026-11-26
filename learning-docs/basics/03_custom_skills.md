# Custom Skills

## What is a skill?

**A saved set of instructions (plus optional files) that the agent loads only when needed.**

- Write a workflow once and reuse it. No more pasting the same long prompt.
- Run it yourself with `/skill-name`, or the agent loads it on its own when your task matches its `description`.

## What does the LLM see?

Skills load in stages, to keep context small:

| Stage | What loads | When |
|---|---|---|
| 1 | `name` + `description` only | every session (a short listing) |
| 2 | the full `SKILL.md` body | when invoked (by you or the agent, via the `Skill` tool) |
| 3 | reference files, scripts | only if the body tells it to read or run them |

To the LLM a skill is **not a tool**. It's instructions that get added to the context. The `Skill` tool is what loads them.

## What can it contain?

```
.claude/skills/add-endpoint/
├── SKILL.md          # required: frontmatter + instructions
├── reference.md      # optional: details, read only when needed
├── templates/        # optional: files to copy or fill in
└── scripts/check.sh  # optional: scripts the agent runs (output costs tokens, the code doesn't)
```

## Frontmatter

```yaml
---
name: add-endpoint                  # required, kebab-case, becomes /add-endpoint
description: Add a new FastAPI endpoint to the timesheet app following project conventions. Use when asked to add or change an API route.   # required: WHAT it does + WHEN to use it
allowed-tools: Read, Edit, Bash(python -m pytest:*)   # optional: tools it may use without asking
argument-hint: <method> <path>      # optional: shown when typing /add-endpoint
disable-model-invocation: true      # optional: only you can run it, the agent won't auto-load it
---
```

The `description` matters most. The agent decides whether to load the skill from this one line.

## When to use one

- A workflow that repeats and is specific to this project. For example:
  - add an endpoint the project's way
  - run the e2e tests and read the results
  - release steps
- Knowledge the LLM can't guess: internal APIs, team conventions, deploy steps.

## When not to

- Generic skills the LLM already has, e.g. "write Python code".
- Rules that apply to *every* task: put those in `CLAUDE.md` instead.
- One-off tasks: just write a prompt.

## Advice

- Short and specific. Give steps, not essays.
- Write the description as *what + when* ("Use when ...").
- Move long details to reference files, so they load only if needed.
- Use scripts for steps that must always be done the same way.
- Test it: run it on a real task, then tweak.

## Example: explaining each part

`.claude/skills/add-endpoint/SKILL.md`:
```markdown
---
name: add-endpoint
description: Add a new FastAPI endpoint to the timesheet app following project conventions. Use when asked to add or change an API route.
argument-hint: <method> <path>
allowed-tools: Read, Edit, Bash(python -m pytest:*)
---

Add the endpoint `$ARGUMENTS` in `mock_up/`:

1. Model: add request/response models to `src/common/models.py` (Python 3.9 types: `Optional[...]`).
2. SQL: add a function to `src/core/repository.py`. No SQL in routes.
3. Route: register it in `create_app()` in `src/core/main.py`.
4. Test: add a test in `tests/test_api.py` using the `client` fixture.
5. Docs: add a row to the API table in `docs/architecture.md`.
6. Verify: run `python -m pytest` and fix any failures before finishing.
```

| Part | Why it's there |
|---|---|
| `name` | becomes `/add-endpoint` |
| `description` | "Use when..." lets the agent auto-load it at the right moment |
| `argument-hint` | reminds you what to type after the command |
| `allowed-tools` | runs pytest without a permission prompt every time |
| `$ARGUMENTS` | replaced with what you typed, e.g. `/add-endpoint GET /api/tags` |
| numbered steps | a clear order, one action each |
| step 6 | the agent checks its own work |

# Appendix: Where skills come from

| Source | Location | Scope |
|---|---|---|
| Project | `.claude/skills/<name>/SKILL.md` | this repo, shared via git |
| Personal | `~/.claude/skills/<name>/SKILL.md` | all your projects, only you |
| Plugins | installed plugin, named `plugin:skill` | wherever the plugin is enabled |
| Built-in | ships with Claude Code (e.g. `/code-review`, `/init`, `/simplify`) | everywhere |

If two skills have the same name, the most specific one wins (project over personal).
