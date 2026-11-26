# Model Context Protocol (MCP)

## What is MCP?

**An open standard for plugging external systems (GitHub, Jira, DBs, docs) into an agent as tools.**

```
Claude ──tool call──► harness ──MCP──► MCP server ──API──► GitHub / Jira / DB
       ◄──result────          ◄──────             ◄──────
```

- An **MCP server** is a program that exposes **tools** (name + description + input schema), and optionally **resources** (data to read) and **prompts**.
- The LLM sees those tools like built-in ones and decides when to call them. The **server runs the code**, not the LLM.
- Tool names: `mcp__<server>__<tool>`, e.g. `mcp__github__create_pull_request`.

## Transports

| Type | Runs | Example |
|---|---|---|
| `stdio` | a local process on your machine | `npx some-mcp-server` |
| `http` | a remote server, usually signs in with OAuth | `https://mcp.example.com/mcp` |

## Setup

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/   # remote
claude mcp add sqlite -- npx -y mcp-server-sqlite mock_up/data/timesheet.db  # local (stdio)
claude mcp list
```
- Run `/mcp` in a session to check status and sign in (OAuth).
- Scope: `--scope local` (default: you, this repo), `project` (writes `.mcp.json`, shared via git), `user` (all your projects).

## `.mcp.json` example

The project-scoped servers live in `.mcp.json` in the repo root. Commit it so the whole team gets the same servers.

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": { "Authorization": "Bearer ${GITHUB_PAT}" }
    },
    "jira": {
      "type": "sse",
      "url": "https://mcp.atlassian.com/v1/sse"
    },
    "sqlite": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "mcp-server-sqlite", "${DB_PATH:-mock_up/data/timesheet.db}"],
      "env": {}
    }
  }
}
```

| Field | Meaning |
|---|---|
| `mcpServers.<name>` | server name, becomes the `mcp__<name>__` prefix |
| `type` | `http` / `sse` (remote) or `stdio` (local process) |
| `url` + `headers` | remote server address, plus extra headers such as auth |
| `command` + `args` + `env` | how to start a local server |
| `${VAR}` / `${VAR:-default}` | read from your environment, so **no secrets in git** |

The first time a project's `.mcp.json` is used, Claude Code asks you to approve its servers.

## Auth: how to sign in, by server type

| Method | Used by | How |
|---|---|---|
| **OAuth** (browser login) | most remote servers: Atlassian/Jira, Linear, Notion, Sentry | add the server, run `/mcp`, choose it, click **Authenticate**, log in in the browser. The token is stored by Claude Code |
| **Bearer token / API key** | GitHub (PAT), servers without OAuth | set the env var (`export GITHUB_PAT=...`) and reference it in `headers` as `${GITHUB_PAT}` |
| **Env vars** | local `stdio` servers (DB, cloud CLIs) | pass them in `env`: `"env": { "API_KEY": "${MY_API_KEY}" }` |
| **Already logged-in CLI** | servers that wrap a CLI (`gcloud`, `aws`) | log in to the CLI once; the server uses its credentials |
| **claude.ai connectors** | Google Drive, Calendar, Gmail... | connect them in claude.ai settings; they appear automatically |

Examples:
```bash
# GitHub with a PAT (the token stays in your shell, never in the repo)
export GITHUB_PAT=ghp_xxx          # better: load it from a password manager or keychain
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer $GITHUB_PAT"

# Jira via OAuth
claude mcp add --transport sse jira https://mcp.atlassian.com/v1/sse
# then in a session: /mcp → jira → Authenticate → browser login
```

Token tips:
- Least privilege: a fine-grained GitHub PAT limited to this repo, with only the permissions you need (e.g. read contents, write PRs; no admin).
- Read-only tokens where possible. For Jira-read-only, a read-only token beats any hook.
- Put secrets in your shell, keychain or `.env` (gitignored). Never in `.mcp.json`.
- `/mcp` shows each server's status. If one says "needs auth", log in again from there.

## MCP vs skills

They're not competitors. **MCP = what the agent *can* do. Skill = *how* to do it here.**

| | MCP | Skill |
|---|---|---|
| Gives | new capabilities (API access, auth) | instructions and know-how |
| Runs | server code with typed inputs | the LLM following text, often via `Bash` |
| Control | per tool: hooks and permissions match exact tool names | hard: you'd have to parse arbitrary bash commands |
| Credentials | held by the server (scoped token, OAuth) | whatever your shell has |

Why MCP is safer: `mcp__github__merge_pull_request` is easy to block. `Bash("gh pr merge ...")` hides inside any command string.

Best together: **skill** (workflow) + **MCP** (access) + **hook** (guardrail) + **agent** (focused worker).

## Cost

- Every tool definition takes context space. A big server can add thousands of tokens.
- Claude Code can **defer** MCP tools and load them only when needed (`ToolSearch`).
- Connect only the servers you use. Disable the rest in `/mcp`.

## Example: Jira, read-only

Connect Jira, then block every write tool with a hook.

`.claude/settings.json`:
```json
{ "hooks": { "PreToolUse": [{ "matcher": "mcp__jira__.*",
  "hooks": [{ "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/jira-readonly.sh" }] }] } }
```

`.claude/hooks/jira-readonly.sh`:
```bash
#!/bin/bash
tool=$(jq -r '.tool_name')
if echo "$tool" | grep -qiE 'create|update|edit|delete|transition|add|assign'; then
  echo "Jira is read-only in this project ($tool blocked)." >&2
  exit 2
fi
```
- Matching on name patterns also catches write tools added in future server versions.
- Even stronger: give the server an API token that only has read access.

## Example: Git workflow (MCP + hook + skill + agent)

Goal: never write to `main`/`dev`/`prod`/`test`. Work on feature branches, push, open a PR, get it reviewed.

**1. MCP**: connect the GitHub server (see Setup).

**2. Hook**: block writes to protected branches, whether through `Bash` or the GitHub MCP.
```json
"PreToolUse": [{ "matcher": "Bash|mcp__github__.*",
  "hooks": [{ "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/protect-branches.sh" }] }]
```
```bash
#!/bin/bash
input=$(cat)
protected='main|dev|prod|test'
branch=$(git branch --show-current)
cmd=$(echo "$input" | jq -r '.tool_input.command // empty')
target=$(echo "$input" | jq -r '.tool_input.branch // empty')

# git commit/push while on a protected branch, or pushing to one by name
if echo "$cmd" | grep -qE '^git (commit|push)' && echo "$branch" | grep -qxE "$protected"; then
  echo "On protected branch '$branch'. Create a feature branch first." >&2; exit 2; fi
if echo "$cmd" | grep -qE "git push .*\b($protected)\b"; then
  echo "Pushing to a protected branch is not allowed." >&2; exit 2; fi
# MCP writes (create/update files, push) aimed at a protected branch
if echo "$target" | grep -qxE "$protected"; then
  echo "MCP write to protected branch '$target' blocked." >&2; exit 2; fi
# merging is a human decision
echo "$input" | jq -r '.tool_name' | grep -q 'merge_pull_request' && {
  echo "Merging PRs is done by a human." >&2; exit 2; }
exit 0
```

**3. Skill**: `.claude/skills/ship/SKILL.md` covers the how-to.
```markdown
---
name: ship
description: Create a feature branch, commit with project message rules, push and open a PR. Use when work is ready to share.
---
1. If on main/dev/prod/test: `git switch -c <type>/<short-name>` (type: feat|fix|docs|chore).
2. Run `python -m pytest` from mock_up/. Stop if anything fails.
3. Commit message: `<type>: <imperative summary, max 60 chars>`, then a blank line, then *why* in 1–3 lines.
4. `git push -u origin HEAD`.
5. Open the PR with `mcp__github__create_pull_request`: title = commit summary, body = what / why / how tested.
6. Ask the `pr-reviewer` agent to review it.
```

**4. Agent**: `.claude/agents/pr-reviewer.md` is a read-only reviewer that uses the MCP.
```markdown
---
name: pr-reviewer
description: Reviews a GitHub PR for bugs and CLAUDE.md convention violations. Use after a PR is opened.
tools: Read, Grep, Glob, mcp__github__get_pull_request, mcp__github__get_pull_request_files, mcp__github__create_pull_request_review
model: sonnet
---
Fetch the PR and its changed files. Check them for bugs and CLAUDE.md conventions.
Post ONE review with `create_pull_request_review` (event: COMMENT, never APPROVE).
Each comment should say file:line, the problem, and a suggested fix.
```

| Piece | Job |
|---|---|
| MCP | GitHub access with a scoped token |
| Hook | **enforces** branch protection, whatever the LLM decides |
| Skill | the team's way: branch names, commit format, PR body |
| Agent | separate context, read tools only, can comment but not approve or merge |

Also turn on branch protection in GitHub itself. The hook is a local guard; the server-side setting is the real one.

# Appendix: Where MCP servers come from

| Source | Location | Scope |
|---|---|---|
| Local | `~/.claude.json` (per project) | you, this repo (default) |
| Project | `.mcp.json` in repo root | everyone on the repo (git), asks for approval on first use |
| User | `~/.claude.json` | you, all projects |
| Plugins | bundled with an installed plugin | wherever the plugin is enabled |
| claude.ai connectors | added in your claude.ai account (e.g. Google Drive, Calendar) | your account |
| Enterprise | managed `managed-mcp.json` | set by your org |

Only connect servers you trust. A server's tool descriptions and results go straight into the LLM's context.
