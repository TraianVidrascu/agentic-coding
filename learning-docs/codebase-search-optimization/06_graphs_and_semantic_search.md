# Graphs and Semantic Search

**Build an index over code and docs, so the agent can query it instead of grepping.**

| Index | Answers | Good for |
|---|---|---|
| **Knowledge graph** | "what connects to X?" (calls, imports, concepts) | architecture questions, big repos, many docs |
| **Vector DB** | "code *about* X" (meaning, not exact words) | concept search when names are unknown |
| **Hybrid** (vector + keyword/BM25) | both, ranked together | the best recall in large mixed repos |
| **grep** (baseline) | exact names | always. Keep it |

Downsides: indexes go **stale**, cost time to build, and add setup. Not worth it for small repos.

## Knowledge graph: graphify

An open-source skill and CLI that turns a folder (code, docs, papers, images) into a queryable knowledge graph.

```bash
pip install graphifyy && graphify install   # package "graphifyy", command "graphify"
/graphify .                                 # in Claude Code: build the graph for this repo
```
- Code is parsed **locally** with tree-sitter: no LLM call. Semantic extraction from docs, PDFs
  and images is optional, and only calls a backend if you configure one.
- Output in `graphify-out/`: `GRAPH_REPORT.md` (highlights, key concepts, suggested questions),
  `graph.html` (interactive view), `graph.json` (the full graph).
- `graphify install` sets up the `/graphify` skill. Keep the graph current with `--watch` or the
  `graphify hook install` post-commit git hook.
- Nothing points the agent at the graph by itself: add a line to CLAUDE.md telling it to read
  `graphify-out/GRAPH_REPORT.md` before architecture questions (see `02_codebase_map.md`).
- Measure the saving on your own repo (`/cost`, `/context`) rather than trusting any headline number.

Details and caveats: `usefull-plugins-and-libraries/01_plugins.md`.

## Vector / hybrid search via MCP

- Index the repo into embeddings, then search with an MCP tool like `search_code("where are weekly totals computed")`.
- Example: **Claude Context** (Zilliz), a hybrid BM25 + vector code search MCP.
- Pattern: the semantic search finds the **area**, then grep or reading confirms the **exact** lines.

## Rule of thumb

```
small repo           → CLAUDE.md map + grep
medium               → + Explore subagents + LSP
large / many docs    → + graph or hybrid index
```
