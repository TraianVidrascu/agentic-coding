# Zero-Shot Prompting

**You give the task and its instructions only, with no examples. The model relies on what it already knows.**

- "Shot" means example. Zero-shot = 0 examples. Few-shot = a few examples (see `02`).
- It's the default for modern LLMs and works for most common tasks.
- Quality depends on being **specific**: the task, context, constraints, output format.

## When to use

- Common tasks the model already knows: summarize, explain, fix a bug, write a test.
- The output format is easy to describe in words.

## When it's not enough

- A custom format or style that's hard to describe. Show it instead (few-shot).
- Results come back inconsistent across runs.
- Tricky reasoning. Ask it to think step by step (chain-of-thought).

## Weak vs strong zero-shot

| Weak | Strong |
|---|---|
| "add validation" | "In `src/common/models.py`, make `EntryIn` reject descriptions over 200 chars. Return 422. Add a test in `tests/test_api.py`." |

Same technique, but the strong prompt names the **file**, the **rule**, the **expected result** and **how to check** it.

## Example 1: code task

```
In mock_up/, add GET /api/projects/{id} that returns one project, or 404 if it doesn't exist.
Follow the conventions in CLAUDE.md. Add a test and run python -m pytest.
```
No example of an endpoint is given. The model knows FastAPI, and CLAUDE.md gives the project rules.

## Example 2: classification

```
Classify this timesheet entry description into one category:
meeting, coding, review, admin, other.
Reply with the category only.

Description: "Sync with Ana about the CSV export"
```
→ `meeting`

The labels and the output format are stated, so no examples are needed.

## Example 3: structured output

```
Extract the date, start time, end time and project from the text below.
Reply as JSON: {"date": "YYYY-MM-DD", "start": "HH:MM", "end": "HH:MM", "project": string|null}.
If a field is missing, use null.

Text: "Worked on Timesheet app on Nov 20, 2026 from 9:30 to 12:15"
```
→ `{"date": "2026-11-20", "start": "09:30", "end": "12:15", "project": "Timesheet app"}`

The format is described precisely, including what to do when a value is missing.

## Bad example 1: vague task

```
Make the summary better.
```
What's wrong:
- "Better" how: faster? prettier? more data?
- Which summary: the backend `/api/summary` or `Summary.jsx`?
- When is it done?

The model guesses and may rewrite things you wanted kept.

Fixed:
```
In mock_up/src/frontend/src/components/Summary.jsx, add the total hours per day
(Mon–Sun) under the per-project totals. Use the existing /api/summary data, with no backend changes.
```

## Bad example 2: unclear output format

```
Tell me if this entry is valid: date 2026-11-20, start 14:00, end 13:30.
```
What's wrong:
- No rules are given. Valid by what standard?
- No format, so you get a paragraph back that code can't parse.
- Run it again and you get a different wording.

Fixed:
```
Check this timesheet entry against these rules: date is YYYY-MM-DD, times are HH:MM 24h,
end must be after start, and entries can't cross midnight.
Reply as JSON: {"valid": true|false, "errors": [string]}.

Entry: date 2026-11-20, start 14:00, end 13:30
```
→ `{"valid": false, "errors": ["end (13:30) must be after start (14:00)"]}`

## Tips

- State the output format explicitly: "Reply with X only", JSON, a table.
- Give the context the model can't know: file paths, conventions, constraints.
- Say what *not* to do when it matters: "don't change other files".
- Inconsistent results? Add 1–3 examples, which turns it into few-shot.
