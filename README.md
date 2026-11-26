# agentic-coding

**A learning repository for agentic coding with [Claude Code](https://claude.com/claude-code).**

The goal is to teach the *craft* around coding agents, not just the commands: how an agent
sees a codebase, how to set up a repository so agents work well in it, how to prompt, and
how to connect several agents into a system that produces correct work.

Written as short, readable notes. Every doc answers "what is it / when do I use it / what
goes wrong", and most end with a concrete Claude Code example.

## Who this is for

Developers who already know how to code and now work *with* agents — and want to move from
"I type prompts into a chat" to "I design and run the system that writes the code".

Start here: **[`learning-docs/modern_dev_job.md`](learning-docs/modern_dev_job.md)** — what the
developer's job becomes when agents write most of the code.

## Structure

```
agentic-coding/
├── learning-docs/                      # the course
│   ├── modern_dev_job.md               # start here: the new job description
│   ├── basics/                         # Claude Code: what it is and how to configure it
│   ├── prompting-techinques/           # how to ask: zero-shot → verification-driven
│   ├── codebase-search-optimization/   # making a repo cheap for an agent to search
│   ├── graph-engineering-patterns/     # connecting many agents into a reliable system
│   └── usefull-plugins-and-libraries/  # tools worth installing
└── mock_up/                            # a small real app to practise on
```

### 1. `basics/` — Claude Code

The mechanics of the harness: what you configure, and what each piece is for.

| Doc | Topic |
|---|---|
| [`01_coding_agent.md`](learning-docs/basics/01_coding_agent.md) | LLM + tools + harness in a loop; how an agent sees a codebase |
| [`02_sessions_and_prompt_caching.md`](learning-docs/basics/02_sessions_and_prompt_caching.md) | `CLAUDE.md`, context windows, sessions, prompt caching |
| [`03_custom_skills.md`](learning-docs/basics/03_custom_skills.md) | Skills: repeatable workflows loaded on demand |
| [`04_custom_agents.md`](learning-docs/basics/04_custom_agents.md) | Subagents: focused reviewers, planners, searchers |
| [`05_rules.md`](learning-docs/basics/05_rules.md) | Rules and instructions that always apply |
| [`06_hooks.md`](learning-docs/basics/06_hooks.md) | Hooks: deterministic code the harness runs around tool calls |
| [`07_mcp.md`](learning-docs/basics/07_mcp.md) | MCP: least-privilege access to external tools and data |
| [`08_worktrees.md`](learning-docs/basics/08_worktrees.md) | Worktrees: parallel agents without file conflicts |
| [`09_workflows.md`](learning-docs/basics/09_workflows.md) | Workflows: scripted multi-agent orchestration |

### 2. `prompting-techinques/` — how to ask

Nine techniques, roughly in order of how much structure they add. The last one is the one
that matters most for code.

[zero-shot](learning-docs/prompting-techinques/01_zero_shot.md) ·
[few-shot](learning-docs/prompting-techinques/02-few-shot.md) ·
[chain-of-thought](learning-docs/prompting-techinques/03-chain-of-thought.md) ·
[structured prompts](learning-docs/prompting-techinques/04-structured-prompts.md) ·
[role / system](learning-docs/prompting-techinques/05-role-system-prompting.md) ·
[prompt chaining](learning-docs/prompting-techinques/06-prompt-chaining.md) ·
[ReAct](learning-docs/prompting-techinques/07-react.md) ·
[self-critique](learning-docs/prompting-techinques/08-self-critique.md) ·
[verification-driven (TDD)](learning-docs/prompting-techinques/09-verification-driven.md)

### 3. `codebase-search-optimization/` — making the repo agent-friendly

An agent starts every session knowing nothing and has to *find* things. Search is where most
tokens and most mistakes come from. These docs cover how it searches
([`01`](learning-docs/codebase-search-optimization/01_llm_grep.md)) and five ways to make that
cheaper: a [codebase map](learning-docs/codebase-search-optimization/02_codebase_map.md),
[symbol search via LSP](learning-docs/codebase-search-optimization/03_symbol_search.md),
[context hooks](learning-docs/codebase-search-optimization/04_context_hooks.md),
[explore subagents](learning-docs/codebase-search-optimization/05_explore_subagents.md), and
[graph / semantic indexes](learning-docs/codebase-search-optimization/06_graphs_and_semantic_search.md).

### 4. `graph-engineering-patterns/` — connecting agents

An **agent graph** is a set of agents (nodes) connected by hand-offs (edges):
planner → coders → reviewer → PR. This section is the heart of the repo.

Read [**`00_axioms.md`**](learning-docs/graph-engineering-patterns/00_axioms.md) first — the
rules that hold for any graph shape, and that every pattern below is built on:

- Without an **anchor** (tests, types, a build, a human) a multi-agent system is just
  well-organized hallucination — agents checking agents only *agree*.
- Errors compound: five 90%-correct steps in a chain are ~59% correct.
- Coding agents produce **AI blobs** by default, and N agents mean N copies of the same helper.
- Each node should see only what it needs.

Then the patterns, each solving one failure mode:

| Pattern | Use it when |
|---|---|
| [Adversarial review & feedback loops](learning-docs/graph-engineering-patterns/01_adversarial_and_feedback_loop.md) | A plausible-but-wrong result would survive a friendly review |
| [Planner & executor](learning-docs/graph-engineering-patterns/02_planner_and_executor.md) | The thinking is hard but the work is mechanical |
| [Context management](learning-docs/graph-engineering-patterns/03_context_management.md) | Hand-offs lose information, or nodes drown in it |
| [Fan-out / fan-in](learning-docs/graph-engineering-patterns/04_fan_out_fan_in.md) | The work splits into independent items |
| [Guardrails & human-in-the-loop](learning-docs/graph-engineering-patterns/05_guardrails_and_human_in_the_loop.md) | Some actions are irreversible |
| [Router](learning-docs/graph-engineering-patterns/06_router.md) | Requests vary a lot in kind and difficulty |
| [Observability & evals](learning-docs/graph-engineering-patterns/07_observability_and_evals.md) | You can't tell whether a change made the system better |
| [Learning loop](learning-docs/graph-engineering-patterns/08_learning_loop.md) | The same mistake keeps recurring across runs |
| [Judge panel (best-of-N)](learning-docs/graph-engineering-patterns/09_judge_panel.md) | The solution space is wide and one attempt isn't enough |

### 5. `mock_up/` — the practice app

A small personal timesheet app (FastAPI + SQLite backend, React/Vite frontend) with its own
`CLAUDE.md`, architecture notes, and a pytest suite — a real codebase to try the ideas on
instead of a toy snippet.

[`mock_up/docs/exercises.md`](mock_up/docs/exercises.md) has graded tasks (add a `tags` field,
reject overlapping entries, support entries crossing midnight, add schema migrations), each
sized for a single agent session. See [`mock_up/README.md`](mock_up/README.md) to run it.

## Suggested path

1. `modern_dev_job.md` — the framing.
2. `basics/01` → `basics/09` — set up your own repo as you read.
3. `prompting-techinques/09` — verification-driven prompting; everything else leans on it.
4. `graph-engineering-patterns/00_axioms.md` — then pick patterns as you hit the problems they solve.
5. `codebase-search-optimization/` — when sessions start feeling slow or expensive.
6. `mock_up/docs/exercises.md` — practise.
