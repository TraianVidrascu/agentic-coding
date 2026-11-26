# Prompt Chaining

**Split a big task into steps. Each step is its own prompt, and its output feeds the next.**

```
prompt 1: extract → output 1 → prompt 2: plan → output 2 → prompt 3: implement → output 3 → prompt 4: review
```

- Each step does one job, so it's more accurate than one giant prompt.
- You can **check, fix or retry** any single step.
- Different steps can use different models or roles (cheap for extraction, strong for planning).
- In Claude Code, automated chains are **workflows** (`basics/09_workflows.md`). By hand, it's one prompt per turn or a skill with numbered steps.

## When to use

- Tasks with clear stages: research → plan → code → review.
- When one prompt does too much and quality drops.
- When you want to inspect the output in between.

## When not to

- Simple tasks. Every step adds latency and tokens.

## Example 1: feature from a ticket (manual chain)

```
Turn 1: Read exercise 3 in mock_up/docs/exercises.md. List the acceptance criteria as bullets. Don't code yet.
Turn 2: Using those criteria, propose a plan: which files change and what tests to add. Don't code yet.
Turn 3: Implement the plan. Run python -m pytest.
Turn 4: Review your diff against the criteria from turn 1. List any gaps.
```
You check after turns 1 and 2, before any code exists.

## Example 2: chain with structured hand-off

```
Step 1 (haiku): Extract every endpoint from src/core/main.py as JSON:
  [{"method": "...", "path": "...", "status_codes": [...]}]

Step 2 (sonnet): Given this JSON <endpoints>…</endpoints>, compare it with the API table
  in docs/architecture.md. List endpoints missing from the docs, or documented wrong.

Step 3: Update docs/architecture.md to fix only the listed differences.
```
Structured output (JSON or tags) between steps means clean hand-offs and no re-parsing of prose.

## Bad example: one giant prompt

```
Read the exercises, pick the overlap one, figure out the criteria, plan it, implement it,
write tests, review it, update the docs and give me a summary.
```
What's wrong:
- Too many jobs at once, so steps get skipped or done shallowly.
- No checkpoint to catch a wrong plan before the code is written.

Fix: Example 1. One job per step, with checkpoints.

## Tips

- One clear job per step.
- Pass **structured** output between steps (JSON or tags).
- Put a human or automated check after the riskiest step (usually the plan).
- Automate it once it's stable: as a skill (numbered steps) or a workflow (code).
