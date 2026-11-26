# Observability and Evals

**See what your graph did (observability), and measure whether a change made it better (evals).**

Without both, you tune prompts by feel. A graph change can quietly make things worse.

## Observability: what to record per run

| Signal | Why | Where to get it |
|---|---|---|
| each agent's input and output | debug wrong results | workflow journal (`journal.jsonl` in the run's transcript folder), agent transcripts |
| tokens and cost per agent | find the expensive agents | `/cost` in a session; JSON output from `claude -p`; OpenTelemetry |
| duration per agent | find the slow agents | `/workflows` progress view, the journal |
| route / status / loop rounds | how the graph behaves | `log()` lines + returned status objects |
| tool calls | what agents actually did | a `PostToolUse` hook that appends to a log file |
| escalations, blocked tasks | where humans were needed | returned statuses (`05`) |

Simple tool-call log (PostToolUse hook, matcher `.*`):
```bash
#!/bin/bash
jq -c '{t: now, tool: .tool_name, input: .tool_input}' >> "$CLAUDE_PROJECT_DIR/.work/tool-log.jsonl"
```

Org-level metrics: Claude Code can export usage through OpenTelemetry (`CLAUDE_CODE_ENABLE_TELEMETRY=1` + an OTel exporter config).

## Evals: test the graph like code

**An eval set = tasks with known expected outcomes. Run it before and after each change.**

```
eval set (10–30 tasks) ──► graph version A ──► scores
                       └─► graph version B ──► scores  →  keep B only if better
```

Each eval case has:
- **input**: request, ticket or bug
- **starting state**: a git commit
- **a check that decides pass or fail**: tests pass, the issue was found, the route is correct

### Example eval set for mock_up

| Case | Input | Pass if |
|---|---|---|
| router-1 | "how are weeks computed?" | route = question |
| router-2 | "Sunday shows in next week" | route = bug |
| bug-1 | commit with an off-by-one in `week_bounds` | hidden test `test_sunday_week` passes after the run |
| review-1 | diff with SQL inside a route | the reviewer reports it (file + line) |
| review-2 | a clean diff | the reviewer reports **nothing** (catches false positives) |
| feature-1 | TIME-42 CSV ticket | all acceptance tests pass, no changes outside the planned files |

Run headless and score with code:
```bash
for case in evals/*/; do
  git -C mock_up checkout -q "$(cat $case/commit)"
  claude -p "$(cat $case/prompt.md)" --output-format json > "$case/out.json"
  bash "$case/check.sh" && echo "PASS $case" || echo "FAIL $case"
done
```

Track per version: **pass rate**, **cost**, **time**. A prompt that adds 2% pass rate but doubles the cost may not be worth it.

## Tips

- Seed evals from **real failures**: every escaped bug becomes an eval case.
- Include **negative cases** (clean code, easy questions) to catch over-flagging and over-routing.
- Keep the checks automatic. An LLM judge only where code can't decide, and give it a rubric.
- Fix the starting state with a commit, so runs are comparable.
- LLM runs vary. Run each case 2–3 times and compare averages, not single runs.

## Failure modes

| Failure | Fix |
|---|---|
| "it feels better" | an eval set with automated checks |
| eval set too easy, always 100% | add the hard cases and real failures |
| only measuring pass rate | track cost and time too |
| overfitting to the eval set | keep adding new real cases. Hold some back |
