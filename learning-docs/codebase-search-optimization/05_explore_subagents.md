# Explore Subagents

**Search in a separate, cheap context. Only the answer comes back to the main session.**

```
main (expensive model, clean context)
  └─► Explore agent: greps 30 files, reads 12 ─► returns "validation is in models.py:20-45"
```

Why it helps:
- **Cleaner**: the dead ends and big outputs never enter the main context.
- **Cheaper**: a smaller, faster model can search.
- **Parallel**: start several at once (frontend, backend, tests).

## Built-in: `Explore`

- Read-only, built for fast codebase search. Claude Code uses it on its own for broad searches.
- Ask for it: *"use the Explore agent to find where weekly totals are computed"*.
- Set the depth in the prompt: *"quick"*, *"medium"* or *"very thorough"*.

## Custom: a cheap searcher

`.claude/agents/code-finder.md`:
```markdown
---
name: code-finder
description: Finds where something is implemented. Use for "where is X" questions before editing.
tools: Read, Bash
model: haiku
---
Find the code for the request. Use rg and find; read only the relevant line ranges.
Reply ONLY with a list of `path:line - what is there`, max 10 items. No explanations.
```
- `model: haiku`: search doesn't need a strong model.
- Strict output format: a short answer means a small main context.

## Where do the agent's file reads go?

- Into the **agent's own context** only. The main session gets just the final summary.
- Prompt caching is **per conversation**. The agent's reads are cached for *its own* later turns, never in the main session's cache.

## Reuse an agent, or start a new one?

Continuing an agent (`SendMessage`) keeps everything it read. Each follow-up re-sends its whole context, cheaply (about 10%) while the cache is warm.

| Reuse the same agent | Start a new one |
|---|---|
| a follow-up in the same area ("now who calls it?") | a different topic: the old files are just noise |
| soon, within the cache lifetime (5 min, or 1 h on some setups) | after a break: the cache expired, so everything is processed at full price again |
| its context is still small | its context is huge: even 10% of 100k per turn adds up |
| files unchanged | files changed: it would answer from out-of-date copies |

More than one agent on the same topic is fine for:
- **parallel parts** (backend and frontend)
- **different search angles** (by name or by concept)
- an **unbiased second opinion** (give it the question, not the first agent's answer)

## Caching across agents

Every agent starts with the same **opening**: tools, system prompt, CLAUDE.md, memory. If that opening matches exactly, the first agent writes it to the cache and the others read it at about 10% of the price.

What breaks the shared opening:
- a different **model** (each model has its own cache)
- a different agent type, `tools` list or system prompt
- editing CLAUDE.md or memory mid-run
- connecting or disconnecting an MCP server mid-run
- a gap longer than the cache lifetime

**Simultaneous launches miss the cache.** A cache entry is usable only after the first request writing it has started its reply. If 5 agents launch at the same instant, each pays a full cache write (about 1.25×), which is *more* than no caching.

## Warm-up agent

Run one tiny agent of the **same type and model** first, so it writes the cache. Then launch the real ones together.

```
warm-up (same type + model, trivial task) → cache written
   ↓
explorer 1 … explorer N in parallel → all read the opening from cache
```

In a session:
> *"Run the code-finder agent with the task 'reply OK'. Then run 5 code-finder agents in parallel: …"*

In a workflow:
```js
const SEARCH = { agentType: 'code-finder', model: 'haiku' }   // must match for the cache to be shared

await agent('Reply with OK.', { ...SEARCH, effort: 'low', label: 'warm-up' })   // writes the cache
const found = await parallel(AREAS.map(a => () =>
  agent(`Find where ${a} is implemented.`, { ...SEARCH, label: `find:${a}` })))  // read from cache
```

Rough cost for 5 explorers with a 15k-token opening:

| | Opening cost |
|---|---|
| no cache / simultaneous launch | 75k–94k |
| warm-up first | ~19k write + 5 × 1.5k reads = **~27k** |
| the same with a lean 5k opening | **~9k** |

Worth it with **many agents** (5+) or a **big opening**. With 2–3 agents and a small opening, skip it, because the extra round trip costs more time than it saves.

Limits:
- Claude Code decides where the cache checkpoints go, so you can't force exactly which part is shared.
- An agent run earlier in the same session (same type and model, within the cache lifetime) already warms the cache for free.

The biggest lever is still a smaller opening. See the next section.

## Reduced context start

**Caching makes the opening cheaper. Shrinking it makes it cheaper *and* leaves more room for the actual search.**

What every agent loads before its task:

| Part | Typical size | How to shrink it |
|---|---|---|
| tool definitions (built-in + MCP) | 5k–20k+ | narrow `tools:` allowlist, fewer MCP servers, deferred tools |
| system prompt (agent body) | 0.5k–2k | a few lines: role, method, output format |
| CLAUDE.md (all levels) | 1k–10k | keep it short. Move details to path-scoped rules, sub-folder CLAUDE.md or reference files (these load only on demand) |
| memory index | 0.2k–2k | one line per memory. Delete stale ones |
| skills listing | 0.5k–2k | remove skills you don't use |

Check the real numbers: run `/context` in a session to see how much each part takes up.

### Example: heavy vs lean explorer

Heavy (no `tools` limit, so it inherits every built-in **and** MCP tool):
```markdown
---
name: finder-heavy
description: Finds code.
---
You are an expert software engineer with deep knowledge of Python, React, SQL...
(40 lines of general advice the model already knows)
```

Lean:
```markdown
---
name: code-finder
description: Finds where something is implemented. Use for "where is X" questions before editing.
tools: Read, Bash
model: haiku
---
Find the code for the request. Use rg and find; read only the relevant line ranges.
Reply ONLY with `path:line - what is there`, max 10 items.
```

| | finder-heavy | code-finder |
|---|---|---|
| tools | all built-in + Jira + GitHub + Docs MCP, ~25k | `Read`, `Bash`, ~3k |
| system prompt | ~1.5k | ~0.1k |
| CLAUDE.md + memory | ~4k | ~4k → ~1.5k after trimming CLAUDE.md |
| **opening** | **~30k** | **~5k** |
| × 5 agents, no cache | 150k | 25k |

(Sizes are illustrative. Measure your own with `/context`.)

### Trim CLAUDE.md for everyone

Main sessions and custom agents both load it, so every line is paid for on every start.

```markdown
# CLAUDE.md (before: 200 lines)       # CLAUDE.md (after: 30 lines)
- full API table                       - commands + 5 key conventions
- all frontend conventions             - "API table: docs/architecture.md"
- all testing rules                    - frontend rules → .claude/rules/frontend.md (paths: src/frontend/**)
                                       - test rules     → .claude/rules/testing.md  (paths: tests/**)
```

The details still reach the agent, but only when it touches those files.

### Choose the lightest agent that fits

| Need | Use | Why it's light |
|---|---|---|
| broad read-only search | built-in `Explore` | skips CLAUDE.md, read-only tools |
| project-aware search | custom `code-finder` | narrow tools, short prompt, haiku |
| needs the current conversation | fork | reuses the main cache, but carries the **whole** conversation, so it's heavy per turn |

## Watch out

- The summary can be wrong or incomplete. Check the key line yourself before editing.
- For a known file or symbol, a direct grep is cheaper than starting an agent.
