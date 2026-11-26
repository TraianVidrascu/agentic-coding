# Verification-Driven Prompting (TDD)

**Give the agent a way to check its own work, and require that it passes.**

- **The most effective technique for coding agents.** An agent that can run a check can iterate until it's right, without you.
- A check = anything with a clear pass/fail: tests, the type checker, a linter, a build, a curl call, a screenshot compared to a mockup.
- Without a check, "done" means the code *looks* right to the model.

## When to use

- Almost always for code changes.
- Especially for bug fixes: reproduce first, then fix.

## Example 1: test-driven (TDD)

```
Add overlap detection (exercise 3) in mock_up/.
1. First write failing tests in tests/test_api.py:
   overlap → 409, touching entries → 201, different days → 201.
2. Run python -m pytest and confirm the new tests fail.
3. Implement until all tests pass. Don't change the tests to make them pass.
```
"Don't change the tests" stops it from cheating by editing the check.

## Example 2: bug fix with reproduction

```
Sunday entries show up in the next week.
1. Write a test that reproduces it (week_bounds for a Sunday date).
2. Confirm it fails.
3. Fix it. Run the full suite. Done = the new test passes and nothing else broke.
```

## Example 3: non-test checks

```
After the change:
- python -m pytest
- cd src/frontend && npm run build   (catches JSX and import errors)
- start the API and curl /api/summary. Expect 200 and JSON with by_day.
```

## Section: interview first

**Let it ask before it builds.** This is cheap, and it prevents a wrong build.
```
I want a running timer (exercise 5). Before planning, ask me up to 5 questions about
anything unclear: behavior, edge cases, UI. Wait for my answers.
```

## Section: spec-driven / plan-then-execute

**Write the spec first, then implement against it, then verify against it.**
```
1. Write docs/specs/timer.md: behavior, API changes, edge cases, acceptance tests.
2. Wait for my review.
3. Implement it, and turn each acceptance test in the spec into a pytest.
```
The spec is a checkable contract, and it survives `/clear` and new sessions.
For the full multi-agent version (spec → plan → execute → verify), see `graph-engineering-patterns/02_planner_and_executor.md`.

## Bad example: no way to check

```
Add overlap detection. Make sure it works.
```
What's wrong: "make sure it works" has no check behind it. The model *believes* it works and says done.

Fix: Example 1. Concrete tests, run them, define done as "all pass".

## Tips

- Define **done** as a command that passes.
- Reproduce bugs with a failing test **before** fixing them.
- Forbid changing the checks to make them pass.
- Automate checks with hooks (run the tests after each edit, `basics/06_hooks.md`).
- No tests yet? Make "write a test" the first step.
