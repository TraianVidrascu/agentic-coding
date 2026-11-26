# The Modern Developer's Job

**Agents write most of the code. The developer decides *what* gets built, sets up *how* agents work, and makes sure the result is *right*.**

```
before:  think → type code → test → ship
now:     define → set up the agents → delegate → verify → decide → ship
```

The job moves from **writing code** to **specifying, setting up the system, and judging**.

## 1. Define the work (the spec is the product)

- Turn vague requests into **testable specs**: behavior, edge cases, out of scope, acceptance criteria.
- A well-defined ticket *is* a spec. If agents can't test it, it isn't ready.
- The biggest wins come before any code: a wrong spec gets faithfully built.

→ `learning-docs/graph-engineering-patterns/02_planner_and_executor.md`

## 2. Build the anchors

- **Tests are your main tool.** They're how agents check their own work, and how you trust it.
- Write or approve the tests **before** the code. Never let the agent that wrote the code also edit the tests to make them pass.
- Add the other checks: type checker, linter, build, CI.

→ `learning-docs/prompting-techinques/09-verification-driven.md`, `graph-engineering-patterns/00_axioms.md`

## 3. Set up the environment for agents

You maintain the agent's working environment the way you used to maintain a build system:

| Piece | Your job |
|---|---|
| `CLAUDE.md` + rules | short, accurate, current conventions |
| skills | the team's repeatable workflows |
| agents | focused reviewers, planners, searchers |
| hooks + permissions | enforce what must never happen |
| MCP | safe, least-privilege access to tools |

→ `learning-docs/basics/`

## 4. Delegate well

- Pick the right shape: one agent, a subagent, a planner/executor pipeline, a fan-out.
- Brief agents like new teammates: the goal, the files, the constraints, how to check.
- Choose the model and effort to match how hard the task is. Don't pay top-model prices for searches.
- Keep the context clean: one task per session, `/clear` often, give big searches to subagents.

→ `learning-docs/prompting-techinques/`, `learning-docs/codebase-search-optimization/`

## 5. Review and judge (the part you can't delegate)

- **Read the diffs.** Green tests don't prove good design.
- Watch for **AI blobs**: duplicated helpers, needless abstraction, dead code. Ask for simplification.
- Check the reasoning on risky changes: data, security, money, migrations.
- You own the merge. "The agent wrote it" is never an excuse.

## 6. Keep the human gates

Agents propose, you approve:
- **the spec**
- **the plan**
- **the merge / deploy**
- **anything you can't undo**: deleting data, sending messages, spending money

Few gates, in the right places. Approving everything without reading is no gate at all.

→ `learning-docs/graph-engineering-patterns/05_guardrails_and_human_in_the_loop.md`

## 7. Improve the system, not just the output

- Is the same review comment coming up again and again? Turn it into a rule, a test or a checklist item.
- Measure: cost, time, pass rate. Keep a small eval set for your pipelines.
- Prune instructions as often as you add them.

→ `learning-docs/graph-engineering-patterns/07_observability_and_evals.md`, `08_learning_loop.md`

## Skills that matter more now

| More important | Less important |
|---|---|
| clear writing (specs, prompts, tickets) | typing speed, memorizing syntax |
| system design and architecture | boilerplate and glue code |
| testing strategy | writing every test by hand |
| reading and reviewing code fast | writing code from scratch |
| security and risk judgment | — |
| understanding the domain and the users | — |
| knowing what the model can and can't do | — |

## Don't delegate

- Understanding the problem and the users.
- Architecture decisions with long-term effects.
- Security, privacy and data-loss judgments.
- The final call on what ships.
- Your own learning: understand the code you merge. You'll debug it at 2 a.m.

## Anti-patterns

| Anti-pattern | Instead |
|---|---|
| "vibe coding": accepting code you didn't read | review every diff that ships |
| prompting without tests | define done as a passing check |
| one giant session for everything | one task per session, subagents for searching |
| rules only in prompts | enforce them with hooks, permissions, CI |
| a 500-line CLAUDE.md | short map + path-scoped rules |
| more agents = better | the simplest graph that works |

## A daily loop

```
morning:  pick tickets → make sure each one is a testable spec
work:     plan (review it) → delegate → agents run tests → review the diffs → simplify → merge
weekly:   look at recurring failures → update rules/skills/tests → prune → check costs
```
