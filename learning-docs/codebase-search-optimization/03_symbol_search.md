# Symbol Search (LSP)

**Search by code meaning (definitions, references, types), not by text.**

| Grep | Symbol search |
|---|---|
| `grep "create_app"` finds definitions, calls, comments, strings | `find_definition(create_app)` gives exactly 1 location |
| "who calls this?" means grep, then read every hit | `find_references` gives an exact list |
| reads the whole file to see one function | reads just that function's body |
| no errors until tests run | type errors show up right after the edit |

It uses a **language server (LSP)**, the same engine behind go-to-definition in your IDE.

## Option 1: Claude Code LSP plugins (official)

Gives Claude go-to-definition, find-references and live diagnostics after every edit.

```bash
npm i -g pyright typescript typescript-language-server   # 1. install the language servers (binaries)
/plugin install pyright-lsp@claude-plugins-official      # 2. Python plugin
/plugin install typescript-lsp@claude-plugins-official   # 2. JS/TS plugin
```
- The plugin only tells Claude Code how to start the server. The server binary must be on your `PATH`.
- Works in terminal sessions, not cloud sessions.

## Option 2: Serena (MCP)

An open-source MCP server for symbol-level reading **and editing**, backed by LSP or a JetBrains IDE.

```bash
claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server
```
Key tools:
- `find_symbol`: find a class or function by name
- `find_referencing_symbols`: who uses it
- `get_symbols_overview`: a file's outline without its bodies
- `replace_symbol_body`, `insert_after_symbol`: edit a whole function at once

## Option 3: structural search (no server)

- **ast-grep** (`sg`): search by syntax tree. `sg -p 'fetch($$$)' src/frontend` finds every `fetch` *call*, but not comments.
- **ctags**: a quick symbol index file. Old but works everywhere.

## When it's worth it

- Large or typed codebases with many same-named things.
- Refactors: rename or change a signature, then find every caller.
- Small repos (like `mock_up`): grep is enough.
