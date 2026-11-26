# Coding Agent Basics

## What is a coding agent?

**LLM + tools + harness, running in a loop.**

- **LLM**: decides what to do next. It only outputs text.
- **Tools**: let it act: read/write/edit files, search (grep/glob), run shell commands (bash).
- **Harness**: the program around the LLM (e.g. Claude Code) that runs the tools for it.

## The agent loop

```
user prompt
   ↓
LLM thinks → asks for a tool call  (e.g. "read src/core/main.py")
   ↓
harness runs the tool → sends back the output
   ↓
repeat until the LLM replies with no tool call → done
```

## How does an LLM see a codebase?

- It doesn't see the codebase up front. It starts with nothing but the prompt.
- It explores with tools (`ls`, `grep`, read file) and only knows what it has read.
- What it has read sits in its **context window** (its working memory, which has a size limit).
- Old context gets summarized or dropped, so details can be lost in long sessions.

## How is an LLM guided?

From these inputs, most general first:

1. **System prompt**: set by the harness (rules, tool descriptions).
2. **Project instructions**: `CLAUDE.md` is loaded automatically on every session.
3. **Your prompt**: the task.
4. **Tool results**: test output, errors, file contents. This is how it corrects itself.

## What is a harness?

The program that wraps the LLM and turns it into an agent. It:

- sends the prompt, context and tool definitions to the LLM
- runs the tool calls the LLM asks for
- asks for **permission** before risky actions
- manages context (memory, `CLAUDE.md`, summarizing)
- adds extras: hooks, skills, subagents, slash commands

## Key takeaways

- The LLM keeps no memory between sessions. Anything that must persist goes in `CLAUDE.md` or memory files.
- Good feedback makes a better agent: give it tests and commands it can run to check its own work.
- Be specific: name the files, constraints and how to verify the result.

# Appendix: Tools, and where they come from

## The durable part

Whatever the names are in your version, every tool comes from one of three places:

| Source | What it is |
|---|---|
| **Built-in** | Ships with the harness (Claude Code) |
| **MCP servers** | External services plugged in via the Model Context Protocol (named `mcp__<server>__<tool>`) |
| **Deferred** | Built-in or MCP tools whose definitions load only when needed (via `ToolSearch`), to save context |

And the **capabilities** an agent needs are stable, even as the tool names change:

| Capability | Why an agent needs it |
|---|---|
| read and write files | the actual work |
| search by name and by content | find the code without reading everything |
| run commands | tests, git, builds: the agent's feedback loop |
| reach the web | docs and errors it hasn't seen |
| delegate to subagents | keep the main context clean, work in parallel |
| plan and ask | agree on the approach before editing |
| isolate | worktrees, so parallel work doesn't collide |
| background and scheduled work | long jobs, recurring tasks |
| load more instructions or tools on demand | pay for context only when it's used |

When you design an agent, think in this column, not in tool names: *"this reviewer needs
read + search + run commands, and must not be able to write."*

## An example snapshot

One real session's built-in tools, grouped by capability. **Treat this as an illustration, not
a reference.** Tools get added, renamed, split and deferred between versions.

| Capability | Tools in that session |
|---|---|
| Files | `Read`, `Write`, `Edit`, `NotebookEdit` |
| Search | `Grep`, `Glob` |
| Shell | `Bash`, `PowerShell`, `Monitor` |
| Web | `WebSearch`, `WebFetch` |
| Subagents | `Agent`, `SendMessage`, `Workflow` |
| Planning | `EnterPlanMode`, `ExitPlanMode`, `AskUserQuestion` |
| Isolation | `EnterWorktree`, `ExitWorktree` |
| Background tasks | `TaskCreate`, `TaskList`, `TaskGet`, `TaskOutput`, `TaskUpdate`, `TaskStop` |
| Scheduling | `CronCreate`, `CronList`, `CronDelete`, `ScheduleWakeup`, `PushNotification` |
| Extensions | `Skill`, `ToolSearch` |
| Output | `Artifact`, `ReportFindings` |

Plus MCP tools, which differ per user depending on what's connected (`basics/07_mcp.md`) --
in that session, Claude Docs, Google Calendar, Gmail and Drive.

**To see your own list**, just ask the agent: *"list the tools you have, grouped by purpose"*.
Run `/context` to see what they cost you in tokens.

## Related, but not tools

- **Skills**: instruction packs loaded with the `Skill` tool (e.g. `/code-review`, `/init`).
- **Hooks**: shell commands the harness runs automatically on events. The LLM doesn't call them.
