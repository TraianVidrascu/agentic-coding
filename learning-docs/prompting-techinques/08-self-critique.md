# Self-Critique / Reflection

**Generate → critique against explicit criteria → revise.**

```
draft → critique ("does it meet criteria A, B, C?") → fixed version
```

- Models are better at **checking** than at getting it right on the first try.
- The critique needs **concrete criteria**. "Is it good?" gets "yes, looks good!"
- It's stronger when someone *else* critiques: a fresh agent or a different role isn't anchored on the draft.

## When to use

- Code that has to meet clear rules: conventions, acceptance criteria, security.
- Writing that has to hit a format or a length.
- Before finishing any agent task: "review your diff before saying done".

## When not to

- Without criteria. It turns into polishing for its own sake.
- Trivial outputs.

## Example 1: self-review before done

```
Implement exercise 3 (reject overlapping entries with 409).
Before you finish, review your own diff against this checklist and fix any misses:
- SQL only in repository.py
- 409 also on PUT, not just POST
- touching entries (11:00–12:00 and 12:00–13:00) are NOT overlaps
- test for overlap, touching, and different days
- API table in docs/architecture.md updated
```

## Example 2: separate critic (stronger)

```
Turn 1: Write the overlap check.
Turn 2: Use the convention-reviewer agent on the diff.
        (It has a fresh context, so it isn't anchored on the reasoning behind the code.)
Turn 3: Fix what it found.
```

## Section: self-consistency

**Run the same prompt several times and trust the majority answer.**
- Useful for yes/no checks and classifications where one run might be a fluke.
- Example: 3 independent agents each ask "is this a real bug?" Keep the bug only if 2 or more say yes.
- This is the "adversarial verify" pattern in workflows (`basics/09_workflows.md`).
- Costs N× the tokens. Use it for decisions that matter.

## Bad example: critique without criteria

```
Write the overlap check. Then review it and make it better.
```
What's wrong: "better" has no target. You get cosmetic renames, or "looks good!".

Fix: Example 1. A checklist of concrete, checkable items.

## Tips

- Write criteria you can check: "touching entries are not overlaps", not "handle edge cases".
- Prefer a **separate critic** (new agent or role) for important work.
- Combine with verification: the critique says *what* to check, tests prove it (`09`).
- One or two rounds is usually enough. After that it just churns.
