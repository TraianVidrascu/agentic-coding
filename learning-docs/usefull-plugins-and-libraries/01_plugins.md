# Useful Plugins

Two plugins that save tokens in different places: **graphify** targets the tokens spent *searching*, **caveman** targets the tokens spent on *replies and tool output*.

| Plugin | Targets | How |
|---|---|---|
| graphify | input tokens spent on searching | a pre-built knowledge graph instead of grep and reading files |
| caveman | reply and tool-output tokens | terse replies, and a local proxy that shrinks tool output |

Both projects publish their own benchmark numbers, and both have changed them across versions.
None are quoted here: measure on your own work with `/cost` and `/context`, which is the only
number that applies to your repo anyway.

## graphify

**Turns a folder (code, docs, papers, images) into a queryable knowledge graph.**

```bash
pip install graphifyy && graphify install   # package "graphifyy", command "graphify"
/graphify .                                 # in Claude Code: build the graph for this repo
```
Requires Claude Code and Python 3.10+. `graphify install` sets up the `/graphify` **skill**
(in `~/.claude/skills/graphify/`), which is what `/graphify .` then invokes.

- Code is parsed **locally** with tree-sitter: no LLM call, nothing leaves your machine.
- Semantic extraction from docs, PDFs and images is optional, and only calls a backend if you configure one.
- Output in `graphify-out/`:
  - `GRAPH_REPORT.md`: highlights, key concepts, suggested questions
  - `graph.html`: an interactive, clickable view
  - `graph.json`: the full graph, queryable later without re-reading the files
- Keeping it current, two ways:
  - `--watch`: run it in a background terminal. Saving a code file triggers an instant AST-only
    rebuild (no LLM); doc and image changes instead notify you to run `--update`.
  - `graphify hook install`: a post-commit **git** hook that rebuilds after every commit, with
    no background process.
- To make the agent actually use the graph, point it there yourself — a line in `CLAUDE.md`
  such as "read `graphify-out/GRAPH_REPORT.md` before answering architecture questions"
  (see `codebase-search-optimization/02_codebase_map.md`).

Use it for: big repos, lots of docs, "how does X connect to Y?" questions.
Skip it for: small repos like `mock_up`, where grep and a CLAUDE.md map are enough.

More: `codebase-search-optimization/06_graphs_and_semantic_search.md` · [github.com/safishamsi/graphify](https://github.com/safishamsi/graphify)

## caveman

**Makes Claude answer in terse "caveman" style: no filler, no pleasantries, just the content.**

```bash
claude plugin marketplace add JuliusBrussee/caveman && claude plugin install caveman@caveman
```

- Type `/caveman` if it doesn't start on its own. Say `stop caveman` to go back.
- Two parts: a **skill** (the terse-reply rules) and a **local proxy** that shrinks tool output
  before it reaches the context. The skill can be installed alone, without the proxy.
- Originals stay on your disk, and the agent can pull any of them back.
- `/caveman-compress <file>` shrinks memory files like CLAUDE.md and backs up the original.
- Two things that eat into the saving: the rules themselves cost input tokens on every turn, and
  if you pay **per request** rather than per token, shorter answers save you nothing.

Use it for:
- long agent sessions
- subagents whose output only another agent reads (orchestrator hand-offs)
- cost-sensitive pipelines

Skip it for: docs, explanations or anything a human reads carefully, where clarity matters more than tokens.

More: [github.com/JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)

## Caveats

- Third-party plugins run with **your** permissions (hooks included). Read what they install before enabling.
- Both are third-party projects under active development. Install flags, commands and output
  files change, so check the repo's README before relying on any detail here.
- caveman routes tool output through a local proxy. Know what that means for your data before
  enabling it on anything sensitive.
