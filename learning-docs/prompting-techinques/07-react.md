# ReAct (Reason + Act)

**Think → act (call a tool) → observe the result → think again, until done.**

```
Thought:     "Weekly totals are wrong on Sundays. Check how the week is computed."
Action:      grep -n "def week_bounds" src/common/time_utils.py
Observation: time_utils.py:12  def week_bounds(d): ...
Thought:     "Read it and check the Sunday case."
Action:      read time_utils.py lines 12-19
...
```

- It combines **chain-of-thought** (reasoning) with **tools** (real information).
- Reasoning alone hallucinates facts. Acting alone flails without a plan. Together they ground each step in real results.
- This **is** the agent loop (`basics/01_coding_agent.md`). Claude Code does ReAct natively, so you don't prompt the format by hand.

## What you control as a user

You can't change the loop, but you can shape it:

| Lever | Prompt |
|---|---|
| reason before the first action | "Before searching, say where you expect this code to be and why." |
| better observations | "Run the failing test and read the full traceback before changing code." |
| stop conditions | "Stop and ask me if the fix needs changes outside mock_up/src/core." |
| a budget | "Use at most 5 searches. Then tell me what you found." |

## Example 1: guided debugging

```
GET /api/summary returns 500 for weeks with an entry that has no project.
Work in a loop: form a hypothesis, check it with a tool (grep, read, run a test), and update.
Write a failing test first that reproduces the 500. Stop when it passes and nothing else broke.
```

## Example 2: exploration with a budget

```
Find where entries are filtered by date range. Use at most 3 searches.
Reply with path:line and one sentence. Don't read whole files.
```
The limits keep the loop short and the context clean.

## Bad example: no observation step

```
Fix the summary bug. Don't run anything, just edit the code.
```
What's wrong:
- No tests and no reading the traceback, so it's guessing.
- It reasons without grounding, which is plain CoT and prone to confident wrong fixes.

Fix: let it observe. "Run the failing test first."

## Tips

- Give it **observable** signals: tests, commands, logs. They're what makes ReAct work.
- Ask for a hypothesis before big actions, so it isn't searching at random.
- Set stop conditions and budgets for open-ended exploration.
- Long ReAct loops fill the context. Hand big explorations to subagents.
