# Hooks for Search Context

**Block junk from entering context, and inject the right context automatically.** (Hook basics: `basics/06_hooks.md`.)

## Trim: block junk reads

Searches now run through `Bash`, so match on it as well as `Read`.

`.claude/hooks/no-junk.sh` (PreToolUse, matcher `Read|Bash`):
```bash
#!/bin/bash
input=$(cat)
target=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.command // empty')
if echo "$target" | grep -qE 'node_modules|package-lock\.json|dist/|\.pytest_cache|__pycache__|data/.*\.db'; then
  echo "Generated or huge path. Search src/ instead, or use the map in CLAUDE.md." >&2
  exit 2
fi
```
Cheaper alternatives for simple cases:
- `.gitignore`d paths are already skipped by `rg`.
- `permissions.deny` with `Read(...)` rules in `settings.json`.

## Inject: add context by location

`UserPromptSubmit` stdout is added to context. Add the local notes for the area the prompt mentions.

`.claude/hooks/area-context.sh`:
```bash
#!/bin/bash
prompt=$(jq -r '.prompt')
echo "$prompt" | grep -qiE 'frontend|react|component|jsx' && cat mock_up/src/frontend/NOTES.md
echo "$prompt" | grep -qiE 'api|endpoint|route|sql'        && cat mock_up/docs/architecture.md
exit 0
```
Other injection points:
- `SessionStart`: git status and recent commits, so it knows what changed lately.
- `PostToolUse` on `Edit`: lint or type errors for the edited file.

## Trade-off

- Too much injection is pollution again. Inject **short** notes only, and only when matched.
- Path-scoped **rules** (`basics/05_rules.md`) often do the same job with no script.
