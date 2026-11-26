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
- Code is parsed **locally** with tree-sitter. Docs and images go to the LLM to extract concepts.
- Output in `graphify-out/`:
  - `GRAPH_REPORT.md`: summary, key nodes, communities
  - `graph.html`: an interactive view
  - the graph data
- `graphify install` adds a CLAUDE.md note ("read GRAPH_REPORT.md first") and a PreToolUse hook that points searches to the graph.
- `--watch` keeps the graph updated as files change.
- The project claims large token savings. Measure it on your own repo.

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
