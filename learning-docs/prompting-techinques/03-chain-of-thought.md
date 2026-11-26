# Chain-of-Thought (CoT) Prompting

**Ask the model to reason step by step *before* answering.**

- An LLM writes one token at a time. Written-out reasoning gives it "room to think", and each step builds on the previous one.
- It helps with math, logic, multi-step problems, debugging and planning.
- The cost: more output tokens and slower answers.

## Variants

| Variant | How | Example |
|---|---|---|
| Zero-shot CoT | add "think step by step" | "…Think step by step, then answer." |
| Few-shot CoT | examples that **show the reasoning**, not just the answer | Q → reasoning → A |
| Structured CoT | separate the reasoning from the answer with tags | `<thinking>…</thinking><answer>…</answer>` |
| Extended thinking | the model reasons internally before replying (built into reasoning models) | raise the effort or thinking level instead of prompting for it |
| Plan first (agents) | "plan, then implement", e.g. Claude Code **plan mode** | review the plan before any edits |

With extended thinking models, "think step by step" adds less. Ask for **what to think about** instead: the edge cases, the constraints, the options.

## When to use

- Several steps or conditions: date math, overlap rules, cost estimates.
- Debugging: from the symptom, to a hypothesis, to a check.
- Decisions with trade-offs.

## When not to

- Simple lookups or formatting. It adds cost with no gain.
- When you need a fast, short answer and the task is easy.

## Example 1: zero-shot CoT (logic)

```
Do these two timesheet entries overlap?
A: 2026-11-20 09:00–11:30
B: 2026-11-20 11:15–12:00
Think step by step, then answer "yes" or "no" on the last line.
```
→
```
A ends at 11:30. B starts at 11:15.
11:15 is before 11:30, so B starts while A is still running.
yes
```

## Example 2: structured CoT (separate reasoning from answer)

```
Weekly hours: Mon 7.5, Tue 8, Wed 6.25, Thu 8, Fri 4.5. The target is 38h.
How many hours are missing?
Reason inside <thinking> tags. Put only the number inside <answer> tags.
```
→ `<thinking>7.5+8=15.5, +6.25=21.75, +8=29.75, +4.5=34.25. 38−34.25=3.75</thinking><answer>3.75</answer>`

Code reads only `<answer>`, and the reasoning stays available for debugging.

## Example 3: debugging in an agent

```
The weekly summary shows Sunday's hours in the next week.
Before changing any code:
1. List the possible causes (frontend date math, backend week_bounds, timezone).
2. For each one, say which file and line you'd check, and what you'd expect to see.
3. Check them in order, and stop when you find the cause.
Then fix it, and add a test that would have caught it.
```
Hypotheses first, then evidence, then the fix. This keeps it from jumping to the first guess.

## Bad example 1: answer first, reasoning after

```
Do the entries overlap? Answer yes or no, then explain why.
```
What's wrong: the answer is already fixed when the "reasoning" starts, so the explanation just justifies it.

Fix: **reasoning first, answer last**, as in Example 1.

## Bad example 2: CoT where it isn't needed

```
What is the file extension of App.jsx? Think step by step.
```
What's wrong: a trivial lookup. It costs more tokens and time for the same answer.

Fix: just ask. Save CoT for multi-step problems.

## Tips

- Reasoning **before** the answer, always.
- Separate the reasoning from the final answer (tags or "last line") so it's easy to parse.
- Guide the steps for hard tasks: "first list the edge cases, then…".
- In agents, plan before editing: plan mode, or "propose a plan, wait for my OK".
- Check the reasoning, not just the answer. Wrong steps reveal wrong assumptions.
