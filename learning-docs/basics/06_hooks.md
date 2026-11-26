# Hooks

## What is a hook?

**A shell command that the harness runs automatically when an event happens.**

- The LLM doesn't decide whether it runs. It **always** runs. That's the difference from prompts and rules.
- Configure hooks in `settings.json` under `"hooks"`:
  - `~/.claude/settings.json`: personal
  - `.claude/settings.json`: project, shared via git
  - `.claude/settings.local.json`: project, just you
- Or run `/hooks` to manage them interactively.

## How does a hook work?

```
event fires → harness runs your command, sending event JSON on stdin
            → your script decides → exit code tells the harness what to do
```

| Exit code | Meaning |
|---|---|
| `0` | OK, continue. For some events stdout is **added to context** |
| `2` | **Block** the action. stderr is sent back to the LLM as the reason |
| other | non-blocking error, shown to you, and the action continues |

Example input on stdin (PreToolUse):
```json
{ "session_id": "...", "cwd": "/path/to/repo", "hook_event_name": "PreToolUse",
  "tool_name": "Bash", "tool_input": { "command": "rm -rf data/" } }
```

## What events are there?

| Event | Fires | Typical use |
|---|---|---|
| `PreToolUse` | before a tool runs | block dangerous commands or files |
| `PostToolUse` | after a tool succeeds | format, lint, run tests |
| `UserPromptSubmit` | when you send a prompt | add context, block secrets in prompts |
| `SessionStart` | session starts or resumes | load git status, TODOs |
| `Stop` / `SubagentStop` | agent or subagent finishes | final checks, notify you |
| `PreCompact` | before context is summarized | save notes or a transcript |
| `Notification` | agent needs your attention | desktop or phone alert |
| `SessionEnd` | session ends | cleanup, logs |

`matcher` filters tool events by tool name: `"Bash"`, `"Edit|Write"`, `"mcp__.*"`.

## Config shape

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/guard.sh" }]
      }
    ]
  }
}
```

## Security: block dangerous actions

Stop the agent touching the real DB or deleting data. `.claude/hooks/guard.sh`:
```bash
#!/bin/bash
cmd=$(jq -r '.tool_input.command')
if echo "$cmd" | grep -qE 'rm -rf|data/timesheet\.db|DROP TABLE'; then
  echo "Blocked: touches real data. Use the test DB (tmp_path) instead." >&2
  exit 2
fi
```
- `exit 2` blocks the command. The stderr message tells the LLM *why*, so it can change course.
- Use `permissions.deny` for simple cases. Use hooks when you need logic.

## Keep context clean

A hook can't clear context, but it can **stop junk from entering** it:
```bash
#!/bin/bash
# PreToolUse, matcher "Read": block huge or generated files
path=$(jq -r '.tool_input.file_path')
if echo "$path" | grep -qE 'node_modules|package-lock\.json|\.db$'; then
  echo "Don't read $path: generated or huge. Search for what you need instead." >&2
  exit 2
fi
```
Other ideas:
- trim long test output before it reaches the LLM
- save a summary in `PreCompact`

## Add context

stdout from `SessionStart` and `UserPromptSubmit` is **added to the context**:
```bash
#!/bin/bash
# SessionStart: show the agent where things stand
echo "Branch: $(git branch --show-current)"
echo "Recent commits:"; git log --oneline -5
echo "Uncommitted:"; git status --short
```
Other ideas:
- add the relevant doc when the prompt mentions "API" (`UserPromptSubmit`)
- add today's open tickets

## Quality: check every edit automatically

```json
"PostToolUse": [{ "matcher": "Edit|Write",
  "hooks": [{ "type": "command", "command": "cd \"$CLAUDE_PROJECT_DIR/mock_up\" && python -m pytest -q 2>&1 | tail -5" }] }]
```
The agent sees failing tests right after the edit that broke them.

## What language can a hook be written in?

**Any.** The command runs in a shell, so bash, Python, Node, a compiled binary... anything installed on the machine.
- It must read JSON from stdin and signal its result with the exit code (or JSON on stdout for advanced control).
- Keep hooks **fast**. They run on every matching event.

## Advice

- Make scripts executable: `chmod +x`.
- Test a hook by piping sample JSON into it: `echo '{"tool_input":{"command":"rm -rf x"}}' | ./guard.sh; echo $?`
- Write clear stderr messages. They're the LLM's only clue why it was blocked.
- Hooks run with **your** permissions. Review any hook before enabling it, especially from plugins.

# Appendix: Where hooks come from

| Source | Location | Scope |
|---|---|---|
| Personal | `~/.claude/settings.json` | all your projects |
| Project | `.claude/settings.json` | everyone on the repo (git) |
| Local | `.claude/settings.local.json` | you, this repo (gitignored) |
| Plugins | installed plugin's hooks config | wherever the plugin is enabled |
| Enterprise | managed policy settings | set by your org, can't be overridden |
