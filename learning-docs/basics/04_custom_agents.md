# Custom Agents (Subagents)

## What is a subagent?

**A separate agent that the main agent hands a task to. It works in its own context and returns only a summary.**

```
main agent ──prompt──► subagent (fresh context, own tools/model)
     ▲                      │ reads 40 files, runs tests...
     └──── summary ─────────┘   (none of that noise enters the main context)
```

## How do you define one?

A markdown file: frontmatter for the settings, body for the agent's **system prompt**.

- Project: `.claude/agents/<name>.md` (shared via git)
- Personal: `~/.claude/agents/<name>.md` (all your projects)
- Or run `/agents` to create and manage them interactively.

## Why use them?

- **Clean context**: noisy work (searching, reading logs) stays out of the main session.
- **Parallel work**: several subagents can run independent tasks at the same time.
- **Specialization**: a focused system prompt plus only the tools it needs.
- **Cost/speed**: give it a cheaper, faster model for simple work and the strongest model for hard reasoning.

## Fresh vs inherited context

| Type | Starts with | Use for |
|---|---|---|
| Custom/named agent | only the prompt you give it | focused, well-defined tasks |
| Fork | a copy of the current conversation | side tasks that need everything said so far |

A fresh agent knows **only** what's in its prompt, so brief it like a new teammate: the goal, the files, what's already been ruled out.

## When not to use them

- Small tasks (a few tool calls). Handing off costs tokens and loses detail.
- Work where you need to see every step. You only get the summary back.
- Tightly coupled edits. Two agents changing the same files will conflict.

## Options (frontmatter)

```yaml
---
name: convention-reviewer       # required, how you call it
description: Reviews mock_up changes against CLAUDE.md conventions. Use after editing backend code.   # required: WHAT + WHEN, used to auto-pick it
tools: Read, Grep, Glob, Bash   # optional: allowlist. Leave it out and the agent gets all tools
model: sonnet                   # optional: sonnet | opus | haiku | inherit (default)
---
```

- Restrict `tools` to make an agent safe. For example, a reviewer with no `Edit`/`Write` can't change code.
- Choose `model` by difficulty: `haiku` for search, `sonnet` for most coding, `opus` for hard reasoning.

## Example: explaining each part

`.claude/agents/convention-reviewer.md`:
```markdown
---
name: convention-reviewer
description: Reviews mock_up changes against CLAUDE.md conventions. Use after editing backend code.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You review changes in `mock_up/` for convention violations. You never edit files.

1. Run `git diff` to see what changed.
2. Check each rule:
   - SQL only in `src/core/repository.py`, never in routes
   - Python 3.9 types (`Optional[...]`, not `X | None`)
   - new endpoints have a row in `docs/architecture.md`
   - new endpoints have a test using the `client` fixture
3. Run `python -m pytest`.

Reply with a list: `file:line | rule broken | fix`. If everything is fine, say "No issues".
```

| Part | Why it's there |
|---|---|
| `description` "Use after..." | the main agent knows when to call it |
| `tools` without Edit/Write | read-only by design, so it can't "fix" things behind your back |
| `model: sonnet` | checking rules doesn't need the most expensive model |
| "You never edit files" | backs up the tool restriction in words |
| checklist | concrete rules, not "review the code" |
| output format | a short, structured summary is all the main agent gets back |

Call it by asking: *"use the convention-reviewer agent on my changes"*, or let the main agent pick it based on the description.

# Appendix: Where agents come from

| Source | Location | Examples |
|---|---|---|
| Built-in | ships with Claude Code | `general-purpose`, `Explore` (read-only search), `Plan` (design), `fork` |
| Project | `.claude/agents/*.md` | team agents, shared via git |
| Personal | `~/.claude/agents/*.md` | your own, across all projects |
| Plugins | installed plugins | agents bundled with a plugin |

### Skills vs agents

| | Skill | Agent |
|---|---|---|
| Runs in | the main context | its own separate context |
| Is | instructions added to the conversation | a separate worker that returns a summary |
| Use for | "how to do X here" | "go do X and report back" |
