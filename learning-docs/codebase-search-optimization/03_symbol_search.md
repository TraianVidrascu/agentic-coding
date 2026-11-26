# Symbol Search (LSP)

**Search by code meaning (definitions, references, types), not by text.**

| Grep | Symbol search |
|---|---|
| `grep "create_app"` finds definitions, calls, comments, strings | `find_definition(create_app)` gives exactly 1 location |
| "who calls this?" means grep, then read every hit | `find_references` gives an exact list |
| reads the whole file to see one function | reads just that function's body |
| no errors until tests run | type errors show up right after the edit |

It uses a **language server (LSP)**, the same engine behind go-to-definition in your IDE.

## Option 1: Claude Code code-intelligence plugins (official)

Two things at once: **diagnostics** (type errors and missing imports show up right after Claude's
own edit, before you build) and an `LSP` tool for read-only symbol navigation.

Always two installs: the language server **binary**, then the **plugin** that starts it.

```bash
npm install -g typescript-language-server typescript     # 1. the binary, on your PATH
/plugin install typescript-lsp@claude-plugins-official    # 2. the plugin, inside Claude Code
```
- The official marketplace covers most mainstream languages (`pyright-lsp` for Python, plus Go,
  Rust, Java, C/C++, C#, Ruby, PHP, Swift, Kotlin, Lua...). Each plugin's README names the binary
  it needs. Run `/plugin` → **Discover** to browse.
- The plugin **doesn't include** the server: it only says which command to start and which file
  extensions it handles. The binary must be on the `PATH` of the shell you start `claude` from
  (check with `which <binary>`, or `Get-Command <binary>` in PowerShell).
- Works in **terminal sessions**. In cloud sessions Claude Code doesn't start plugin language
  servers, so there are no diagnostics and no navigation there.
- It works when you see `Found N new diagnostic issues` under an edit (Ctrl+O to read them). If
  nothing appears, `/plugin` → **Errors** shows `Executable not found in $PATH` and names the binary.
- No official plugin for your language? Write an `.lsp.json` plugin naming the server command and
  extensions.

## Option 2: Serena (MCP)

An open-source MCP server for symbol-level reading **and editing**, backed by LSP or a JetBrains IDE.

```bash
uv tool install -p 3.13 serena-agent     # install it
serena setup claude-code                 # then let it configure Claude Code for you
```
Or wire it up by hand, per project or globally:
```bash
claude mcp add serena -- serena start-mcp-server --context claude-code --project "$(pwd)"
claude mcp add --scope user serena -- serena start-mcp-server --context claude-code --project-from-cwd
```
Key tools:
- `find_symbol`: find a class or function by name
- `find_referencing_symbols`: who uses it
- `get_symbols_overview`: a file's outline without its bodies
- `replace_symbol_body`, `insert_after_symbol`: edit a whole function at once
- also refactorings (`rename`, `move`, `inline`) and `search_for_pattern`

Check the project's docs before copying these: Serena's launch command has changed more than once.

## Option 3: structural search (no server)

- **ast-grep** (`sg`): search by syntax tree. `sg -p 'fetch($$$)' src/frontend` finds every `fetch` *call*, but not comments.
- **ctags**: a quick symbol index file. Old but works everywhere.

## When it's worth it

- Large or typed codebases with many same-named things.
- Refactors: rename or change a signature, then find every caller.
- Small repos (like `mock_up`): grep is enough.
