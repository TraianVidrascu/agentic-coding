# How an LLM Searches a Codebase

## How does it search?

**Agentic search**: the LLM explores with shell tools, step by step, like a developer would.

```
glob/find "**/*repository*"  →  grep -n "def list_entries"  →  read lines 40-80  →  answer
```

- Tools: find files by name, search text by regex, read files.
- Claude Code has dedicated `Glob` (files by pattern) and `Grep` (content, built on ripgrep)
  tools, and can also run `rg`/`find` through `Bash`. Which route it takes varies by version
  and by what you ask for, so **don't assume** one: check your own session's tool list
  (`basics/01_coding_agent.md`) before writing anything that depends on it, such as a hook matcher.
- **Exact names** (`create_app`, `EntryIn`, `/api/entries`): grep is precise and always up to date. It beats a vector DB.
- **Concepts** ("where is validation?"): grep only works if the LLM guesses the right words. Semantic search helps here (see `05`).

## How does it know where to look?

At the start it only knows:
- `CLAUDE.md` (all levels), memory, and the working directory path.
- Anything else it has to **discover**: list folders, grep, read.

A better starting map means fewer search steps (see `02`).

## Is it expensive?

Yes. Every `ls`, every grep result and every file read becomes tokens in context.

| Cost driver | Example |
|---|---|
| reading whole files to find 1 function | 600-line file for 10 relevant lines |
| broad greps | `grep -r "date"` gives hundreds of matches |
| dead ends | reading the wrong module first |
| generated files | `package-lock.json`, `node_modules/`, `dist/` |

Polluted context also makes the *answers* worse, not just costlier.

## Techniques (one file each)

| # | File | Idea | Best for |
|---|---|---|---|
| 02 | `02_codebase_map.md` | tell it where things are up front | every project, cheapest win |
| 03 | `03_symbol_search.md` | jump to symbols via LSP, not text | large typed codebases |
| 04 | `04_context_hooks.md` | block junk, inject relevant context | big repos, generated files |
| 05 | `05_explore_subagents.md` | search in a separate, cheap context | "find where X happens" |
| 06 | `06_graphs_and_semantic_search.md` | graph or vector index over code and docs | big repos, lots of docs, concept questions |

Start with 02 and 05. Add the others when the repo gets large.
