# Useful Plugins

Two plugins that save tokens in different places: **graphify** cuts *search* tokens, **caveman** cuts *output* tokens.

| Plugin | Saves | How |
|---|---|---|
| graphify | input tokens spent on searching | a pre-built knowledge graph instead of grep and reading files |
| caveman | output tokens | short, filler-free replies |

## graphify

**Turns a folder (code, docs, papers, images) into a queryable knowledge graph.**

```bash
pip install graphifyy && graphify install   # package "graphifyy", command "graphify"
/graphify .                                 # in Claude Code: build the graph for this repo
```

- Code is parsed **locally** with tree-sitter. Docs and images are sent to the LLM to extract concepts.
- Output in `graphify-out/`:
  - `GRAPH_REPORT.md`: summary, key nodes, communities
  - `graph.html`: an interactive view
  - the graph data
- `graphify install` adds:
  - a CLAUDE.md note: "read GRAPH_REPORT.md before architecture questions"
  - a PreToolUse hook that points searches to the graph
- `--watch` rebuilds the graph as files change.

Use it for: big repos, lots of docs, "how does X connect to Y?" questions.
Skip it for: small repos like `mock_up`, where grep and a CLAUDE.md map are enough.

More: `codebase-search-optimization/06_graphs_and_semantic_search.md` · [github.com/safishamsi/graphify](https://github.com/safishamsi/graphify)

## caveman

**Makes Claude answer in terse "caveman" style: no filler, no pleasantries, just the content.**

```bash
claude plugin marketplace add JuliusBrussee/caveman
claude plugin install caveman@caveman
```

- Turn it on: `/caveman`, or say "talk like caveman" / "less tokens please".
- It cuts **output** tokens only. Input (files, context) stays the same.
- Companion **caveman-compress** shortens memory files like CLAUDE.md, which saves input tokens on every turn.
- The default install adds hooks and a status-line badge (tokens saved). `--minimal` skips them.
- Claimed savings: ~65–75% of output tokens (project and reviews). Real-world reports say ~30–50%.

Use it for:
- long agent sessions
- subagents whose output only another agent reads (orchestrator hand-offs)
- cost-sensitive pipelines

Skip it for: docs, explanations or anything a human reads carefully, where clarity matters more than tokens.

More: [github.com/JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)

## Caveats

- Third-party plugins run with **your** permissions (hooks included). Read what they install before enabling.
- The savings numbers are the projects' own claims. Measure on your own work (`/cost`, `/context`).
