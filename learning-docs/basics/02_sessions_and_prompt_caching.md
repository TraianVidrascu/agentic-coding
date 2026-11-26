# Sessions and Prompt Caching

## What is CLAUDE.md?

**A project instructions file that Claude Code loads into context automatically at session start.**

- It is *not* the system prompt. It is added right after it, as part of the conversation.
- Put in it what the agent can't guess: commands, conventions, "don't do X".
- It gets cached because it's always at the start of the prompt. More on caching below.
- Keep it short. Every line costs tokens on every turn.

## Sub-folder CLAUDE.md

- `CLAUDE.md` files in parent folders (from where you started up to the repo root) load at start.
- `CLAUDE.md` files in **sub-folders** load only when the agent reads files in that folder.
- Use them for rules that apply only to that part of the code (e.g. `mock_up/CLAUDE.md`).

## What is a session?

**One conversation, from launch until `/clear` or exit.**

```
start → load system prompt + CLAUDE.md + memory
  ↓
user prompt → agent loop (LLM ↔ tools) → answer
  ↓
next prompt: the WHOLE conversation is sent again
```

- The LLM is stateless. Every turn re-sends everything so far.
- `/clear` starts a new session. `claude --continue` / `--resume` reopens an old one.
- When the context fills up, it gets **compacted** (summarized) and details can be lost.

## What is prompt caching?

- Every turn starts with the same **prefix** (tools + system prompt + CLAUDE.md + earlier messages).
- The provider caches that processed prefix. The next turn only pays full price for the new part.
- Cache reads cost about **10%** of normal input tokens, and responses come back faster.
- The cache expires after a few minutes of inactivity (5 min by default; 1 h on some setups).
- It matches only the **exact** prefix. If something early changes, everything after it must be processed again.
- Caching saves cost and time. It does **not** change what the model sees.

## What is context pollution?

**The context fills with irrelevant, stale or wrong content, so quality drops.**

- Symptoms: it forgets earlier instructions, mixes up tasks, repeats mistakes, hallucinates.
- Causes: long sessions, huge tool outputs, failed attempts, switching tasks in one session.
- Fixes:
  - `/clear` between unrelated tasks
  - `/compact` to summarize and keep going
  - let **subagents** do noisy exploration; only their summary comes back

## What is memory?

**Notes the agent writes for itself, so it remembers things between sessions.**

- The LLM forgets everything when a session ends. Memory is how facts carry over.
- It's stored in `~/.claude/projects/<project>/memory/`, one fact per file.
- `MEMORY.md` is the index (one line per memory) and loads at every session start.
- The full memory file is read only when it's relevant to the task.
- Save one: just say *"remember that ..."*. Remove one: *"forget that ..."*.

### CLAUDE.md vs memory

| | CLAUDE.md | Memory |
|---|---|---|
| Written by | you | the agent (or you, by asking) |
| Shared via git | yes | no, personal and local |
| Holds | project rules and commands | your preferences, past corrections, ongoing work |

### Memory types and examples

| Type | Stores | Example |
|---|---|---|
| `user` | who you are | "Backend dev, new to React. Explain frontend changes in more detail." |
| `feedback` | how you want it to work | "Don't mock the DB in tests. A mocked test once hid a broken migration." |
| `project` | ongoing work and deadlines | "Timer feature (exercise 5) in progress. Demo on 2026-12-01." |
| `reference` | where to find things | "Bugs are tracked in the Linear project TIME." |

### What a memory file looks like

`memory/no-db-mocks.md`:
```markdown
---
name: no-db-mocks
description: Tests must hit a real SQLite DB, never mocks
metadata:
  type: feedback
---
Use the `client` fixture (fresh tmp DB) instead of mocking the repository.
**Why:** a mocked test once passed while the real query was broken.
**How to apply:** any new test in mock_up/tests/.
```

`memory/MEMORY.md`:
```markdown
- [No DB mocks](no-db-mocks.md): tests use a real tmp SQLite DB
- [User role](user-role.md): backend dev, new to React
```

### What NOT to put in memory

- Things the repo already records: code structure, git history, CLAUDE.md rules.
- One-off details that matter only to the current task.
- Secrets.

## What types of prompts exist?

| Type | Who writes it | Example |
|---|---|---|
| System prompt | Harness | rules, tool descriptions |
| Project instructions | You (in files) | `CLAUDE.md`, memory |
| User prompt | You | "add CSV export" |
| Assistant message | LLM | answer or tool call |
| Tool result | Harness | file contents, test output |
| System reminder | Harness | "file changed on disk", current date |

## Key takeaways

- Short, stable CLAUDE.md = cheap and reliable.
- One task per session. `/clear` often.
- Big searches go to a subagent to keep the main context clean.

# Appendix: Everything in context and where it comes from

Order matters: caching covers an unchanged prefix, so the most stable parts go first.

| # | Part | Source | Changes |
|---|---|---|---|
| 1 | Tool definitions | Harness (built-in + MCP servers) | rarely |
| 2 | System prompt | Harness | rarely |
| 3 | User CLAUDE.md | `~/.claude/CLAUDE.md` (all your projects) | rarely |
| 4 | Project CLAUDE.md | `./CLAUDE.md` + parent folders (commit to git) | per project |
| 5 | Local CLAUDE.md | `./CLAUDE.local.md` (personal, gitignored) | per project |
| 6 | Memory | `~/.claude/projects/<project>/memory/` | over time |
| 7 | Conversation | your prompts, LLM replies, tool calls + results | every turn |
| 8 | On-demand | sub-folder CLAUDE.md, skills, deferred tools | when needed |

Rows 1 to 6 form the stable, cached prefix. Row 7 grows each turn. Compaction rewrites it.
