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

# Appendix: All tools and where they come from

Example: the tools in a Claude Code session. Any tool comes from one of three places.

| Source | What it is |
|---|---|
| **Built-in** | Ships with the harness (Claude Code) |
| **MCP servers** | External services plugged in via the Model Context Protocol (named `mcp__<server>__<tool>`) |
| **Deferred** | Built-in or MCP tools whose definitions load only when needed (via `ToolSearch`), to save context |

## Built-in

| Group | Tools | Purpose |
|---|---|---|
| Files | `Read`, `Write`, `Edit`, `NotebookEdit` | read and change files |
| Shell | `Bash`, `Monitor`, `TaskStop` | run commands, watch or stop background jobs |
| Web | `WebSearch`, `web-fetch` agent | search the web, fetch pages |
| Agents | `Agent`, `SendMessage`, `ListAgents`, `Workflow` | start subagents and talk to them |
| Planning | `EnterPlanMode`, `ExitPlanMode`, `AskUserQuestion` | plan first, ask the user |
| Isolation | `EnterWorktree`, `ExitWorktree` | work in a separate git worktree |
| Scheduling | `CronCreate`, `CronList`, `CronDelete`, `ScheduleWakeup`, `RemoteTrigger` | recurring or delayed tasks |
| Extensions | `Skill`, `ToolSearch` | load skills, load deferred tools |
| Output | `Artifact`, `ArtifactComments`, `ArtifactData`, `PushNotification` | publish pages, notify the user |
| Meta | `SendFeedback`, `ReportFindings`, `EndConversation` | feedback, code review results |

## MCP (connected services, vary per user)

| Server | Example tools |
|---|---|
| Claude Docs | `batch`, `update`, `create`, `read`, `query`, `export` |
| Google Calendar | `list_events`, `create_event`, `suggest_time` |
| Google Drive / Gmail | `authenticate` (until connected) |

## Related, but not tools

- **Skills**: instruction packs loaded with the `Skill` tool (e.g. `/code-review`, `/init`).
- **Hooks**: shell commands the harness runs automatically on events. The LLM doesn't call them.
