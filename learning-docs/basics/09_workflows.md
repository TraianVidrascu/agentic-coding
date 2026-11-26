# Workflows

## What is a workflow?

**A JavaScript script that orchestrates many subagents. The control flow is code: loops, fan-out, conditions.**

- Real, runnable JavaScript (**not** TypeScript, not pseudo code), run by Claude Code's `Workflow` tool.
- Each `agent(...)` call starts a subagent. The script decides what runs, in what order, and what data goes where.
- It runs in the **background**. Watch progress with `/workflows`.

## Why use one?

| Without (main agent orchestrates) | With a workflow |
|---|---|
| the LLM decides the next step, and it may skip one | the steps are code, so they always run in order |
| everything piles into one context | each agent gets a fresh context with only its input |
| results are free text | `schema` forces typed JSON output |
| hard to run 10 things in parallel | `parallel()` / `pipeline()` |
| a crash means starting over | **resume** reuses finished agents from cache |

The orchestration is deterministic. Each agent's *output* still isn't, so add verify steps.

## When not to

- Small or single-step tasks. A workflow can start dozens of agents and burns tokens fast.
- It runs only when you **explicitly ask** ("use a workflow"), or with `ultracode` on.

## Building blocks

| Function | Does |
|---|---|
| `export const meta = {...}` | required first line: `name`, `description`, `phases` (a plain literal, no variables) |
| `agent(prompt, opts)` | runs one subagent. Returns text, or a typed object with `schema` |
| `pipeline(items, s1, s2...)` | each item flows through the stages on its own, with no waiting (**default choice**) |
| `parallel([...thunks])` | runs everything at once and waits for **all** (use only when you need all results together) |
| `phase(title)` / `log(msg)` | progress groups and messages in `/workflows` |
| `args` | input passed to the workflow |

`agent` options:
- `schema`: typed output
- `model`, `effort`: per-agent model and effort
- `isolation: 'worktree'`: own git worktree, for agents that edit files in parallel
- `agentType`: use a custom agent from `.claude/agents/`
- `phase`, `label`: progress display

Limits:
- No filesystem or Node APIs.
- No `Date.now()` or `Math.random()` (they would break resume).
- Failed agents return `null`, so `.filter(Boolean)`.

## Example: Jira → plan → code → review → PR

```js
export const meta = {
  name: 'jira-to-pr',
  description: 'Turn a Jira ticket into a reviewed PR',
  phases: [{ title: 'Fetch' }, { title: 'Plan' }, { title: 'Code' }, { title: 'Review' }, { title: 'PR' }],
}

const TICKET = { type: 'object', properties: { key: { type: 'string' }, summary: { type: 'string' },
  acceptance: { type: 'array', items: { type: 'string' } } }, required: ['key', 'summary', 'acceptance'] }
const PLAN = { type: 'object', properties: { tasks: { type: 'array', items: { type: 'object',
  properties: { id: { type: 'string' }, files: { type: 'array', items: { type: 'string' } }, goal: { type: 'string' } },
  required: ['id', 'files', 'goal'] } } }, required: ['tasks'] }
const REVIEW = { type: 'object', properties: { ok: { type: 'boolean' }, issues: { type: 'array', items: { type: 'string' } } },
  required: ['ok', 'issues'] }

// 1. Fetch: read-only Jira MCP
phase('Fetch')
const ticket = await agent(`Use the Jira MCP to read ticket ${args.ticket}. Return key, summary, acceptance criteria.`,
  { schema: TICKET, effort: 'low' })

// 2. Plan: split into tasks that touch DIFFERENT files, so coders don't conflict
phase('Plan')
const plan = await agent(`Plan the implementation of ${JSON.stringify(ticket)} in mock_up/.
  Split into independent tasks with no file overlap. Include a test per task.`, { schema: PLAN })

// 3+4. Code each task in its own worktree, then review it (pipeline: no waiting between tasks)
const results = await pipeline(plan.tasks,
  t => agent(`Implement: ${t.goal}. Files: ${t.files.join(', ')}. Run python -m pytest. Commit on a feature branch.`,
         { phase: 'Code', model: 'sonnet', isolation: 'worktree', label: `code:${t.id}` }),
  (out, t) => agent(`Review task ${t.id}'s changes: ${out}. Check acceptance: ${ticket.acceptance.join('; ')}.`,
         { phase: 'Review', agentType: 'convention-reviewer', schema: REVIEW, label: `review:${t.id}` }),
)

// a plain code check, no LLM: stop if anything failed review
const failed = results.filter(r => !r || !r.ok)
if (failed.length) { log(`${failed.length} task(s) failed review`); return { ticket: ticket.key, failed } }

// 5. PR: open it, then a separate agent reviews it on GitHub
phase('PR')
const pr = await agent(`Merge the task branches into feat/${ticket.key}, push, and open a PR via GitHub MCP.
  Title: "${ticket.key}: ${ticket.summary}". Return the PR URL.`)
await agent(`Review PR ${pr} and post comments (never approve).`, { agentType: 'pr-reviewer' })
return { ticket: ticket.key, pr }
```

| Piece | Why |
|---|---|
| `schema` on fetch/plan/review | the next step gets clean data, no text parsing |
| `effort: 'low'` on fetch | a simple job, so it's cheaper |
| plan with "no file overlap" | parallel coders won't clash |
| `model: 'sonnet'` + `isolation: 'worktree'` | cheaper model for coding, each coder on its own branch |
| `pipeline` | task A gets reviewed while task B is still being coded |
| `agentType` | reuses your agents from `04_custom_agents.md` and `07_mcp.md` |
| the `if (failed.length)` gate | a **deterministic** stop: no PR when the review fails |
| hooks from `07_mcp.md` | still apply: no pushes to main, no merges |

Run it: *"use a workflow: run jira-to-pr with ticket TIME-42"*.

# Appendix: Where workflows come from

| Source | Location | Run with |
|---|---|---|
| Inline | written by Claude for one task | "use a workflow to ..." |
| Saved (project) | `.claude/workflows/*.js` | "run the jira-to-pr workflow" |
| Built-in | ships with Claude Code | by name |
| Skill / slash command | a skill whose steps say to run a workflow | `/that-skill` |

Each run saves its script to a file. Edit it and re-run with `scriptPath`, or resume a stopped run with `resumeFromRunId`.
