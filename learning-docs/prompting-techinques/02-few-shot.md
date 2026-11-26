# Few-Shot Prompting

**Give the task plus a few input → output examples. The model copies the pattern.**

- 1 example = one-shot. 2–5 examples = few-shot.
- The examples teach the **format, style and edge cases** better than describing them in words.
- The model copies *everything* in the examples, including mistakes and quirks.

## When to use

- Zero-shot gives inconsistent or wrongly formatted results.
- A custom format, tone or labeling scheme that's hard to describe.
- Edge cases you want handled a specific way.

## When not to

- Common tasks zero-shot already handles well. Examples just cost tokens.
- Complex reasoning. Examples show the answer, not how to get there (use chain-of-thought).
- In coding agents, the **codebase is often the example**: "follow the pattern of `create_project` in `main.py`" beats pasting code.

## Example 1: classification with edge cases

```
Classify the timesheet entry description. Reply with the category only.

"Daily standup" → meeting
"Fixed overlap bug in repository.py" → coding
"Reviewed PR #12 for CSV export" → review
"Pair-programmed CSV export with Ana" → coding
"Expense report" → admin

"Sync with Ana about the CSV export" →
```
→ `meeting`

The "pair-programmed" example settles an edge case (working *with* someone is still coding) that would be hard to explain in words.

## Example 2: commit message style

```
Write a commit message in our style.

Change: added tags field to entries
Message: feat(entries): add comma-separated tags field

Change: fixed week starting on Sunday in frontend
Message: fix(frontend): start weeks on Monday in mondayOf

Change: added CSV export endpoint and download button
Message:
```
→ `feat(export): add weekly CSV export with download button`

The type, scope, verb tense and lowercase style come across without any rules being written.

## Example 3: pointing to code as the example (agent style)

```
Add GET /api/projects/{id} in mock_up/.
Follow exactly the pattern of the existing DELETE /api/projects/{id} route in src/core/main.py
and get_entry() in src/core/repository.py: same error handling, same naming.
```
The examples are already in the repo, so there's nothing to paste and they're always up to date.

## Sub-technique: negative examples

**Show what you *don't* want next to what you do want, and say why.**

- Useful when the model keeps making the same mistake.
- Contrast teaches the boundary: "this, not that, because…".

### Example: commit messages

```
Write a commit message in our style.

Good: feat(export): add weekly CSV export with download button
Bad:  Added CSV export feature and also fixed some stuff in the frontend.
Why bad: no type(scope) prefix, past tense, vague ("some stuff"), mixes two changes.

Good: fix(frontend): start weeks on Monday in mondayOf
Bad:  fix: bug fix
Why bad: no scope, says nothing about what was fixed.

Change: added overlap detection that returns 409
Message:
```
→ `feat(entries): reject overlapping entries with 409`

### Example: agent coding rule

```
Add the date filter to the entries endpoint.

Do: put the SQL in repository.py:
    def list_entries(conn, date_from, date_to): ... WHERE date BETWEEN ? AND ?
Don't: query the DB inside the route in main.py:
    @app.get("/api/entries") ... conn.execute("SELECT ...")
Why: CLAUDE.md says all SQL lives in repository.py.
```

### Watch out

- **Negative examples can backfire.** The model may copy the bad pattern, because whatever it sees gets reinforced.
- Always **pair** each bad example with a good one, and **label it clearly** (`Bad:` / `Don't:`).
- Explain *why* it's bad. The reason is what generalizes.
- Have more good examples than bad ones. Use negatives only for real, repeated mistakes.
- Often better: state it positively ("use the imperative: 'add', not 'added'").

## Bad example 1: all examples look the same

```
"Daily standup" → meeting
"Weekly sync" → meeting
"Planning meeting" → meeting

"Fixed login bug" →
```
What's wrong:
- Every example has the same label, so the model learns "always say meeting".
- No edge cases are covered.

Fix: give **diverse** examples that cover each label and the tricky cases (see Example 1).

## Bad example 2: inconsistent examples

```
"Daily standup" → Meeting
"Fixed bug" → category: coding
"Reviewed PR" → {"type": "review"}

"Expense report" →
```
What's wrong:
- Three different formats, so the output format is a coin flip.
- The model copies the noise, not a pattern.

Fix: use **exactly the same format** in every example, the one you want back.

## Tips

- 2–5 examples is usually enough. More costs tokens with little gain.
- Make them diverse: different labels, lengths and edge cases.
- Keep the format identical across all of them.
- Mix up the order. If the last examples all share a label, the model leans toward it.
- Label clearly: use `<example>` tags or `Input:` / `Output:` so examples don't blur into the task.
- In agents: point to existing code as the example instead of pasting it.
