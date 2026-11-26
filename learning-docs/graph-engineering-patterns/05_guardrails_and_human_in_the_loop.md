# Guardrails and Human-in-the-Loop

**Layers of safety: block what must never happen, ask before what's risky, let humans approve what's irreversible.**

Prompts *ask*, guardrails *enforce*. A graph of N agents gets N chances to ignore a prompt (Axiom 8).

## Layers (defense in depth)

| Layer | Enforces | Example |
|---|---|---|
| 1. **Permissions** | allow / ask / deny per tool or command | deny `rm -rf`, ask before `git push` |
| 2. **Hooks** | custom logic on every tool call | block writes to `main`, block reading `.env` |
| 3. **Isolation** | limits how far damage can spread | worktrees per agent, the Bash sandbox, a test DB |
| 4. **Scoped credentials** | the agent *can't* do more | read-only Jira token, a PAT limited to one repo |
| 5. **Server-side rules** | the final backstop | GitHub branch protection, required CI |
| 6. **Human gates** | judgment on irreversible steps | approve the spec, the plan, the merge |

Each layer catches what the one above misses. Layers 1–5 are deterministic. Layer 6 is judgment.

## Layer 1: permissions for mock_up

`.claude/settings.json`:
```json
{
  "permissions": {
    "allow": ["Bash(python -m pytest:*)", "Bash(npm run build:*)", "Bash(git diff:*)", "Bash(git status:*)"],
    "ask":   ["Bash(git push:*)", "Bash(npm install:*)"],
    "deny":  ["Bash(rm -rf:*)", "Read(./.env)", "Read(./mock_up/data/**)", "Bash(sqlite3:*)"]
  }
}
```
- **allow** the safe commands agents run constantly, so there are no prompts mid-pipeline.
- **ask** for the outward-facing ones.
- **deny** the never-ever ones.

## Human gates: where to put them

Gate where a mistake is **costly to undo** and **cheap to review**:

| Gate | Cost to review | Cost if wrong |
|---|---|---|
| spec / ticket approval | 2 min | the whole feature built wrong |
| plan approval | 2 min | all executors waste work |
| merge / deploy | 10 min | production incident |
| ~~every single edit~~ | constant interruptions | low (tests catch it) |

Too many gates and people approve without reading (human rubber-stamping). Use few gates, at high-value points.

## Escalation: when an agent should stop and ask

Define it in code, not as a hope:
- **Budget hit:** max rounds in a loop (`01`), max re-plans (`02`).
- **No progress:** the same failure twice.
- **Blocked:** the executor returned `status: "blocked"`.
- **Outside scope:** it needs files outside its task, or a schema change (CLAUDE.md: no migrations).
- **Low confidence:** reviewers disagree (no majority).

How to escalate:
- return a clear status (`escalate-to-human`, with the reasons)
- the agent asks you directly
- or a push notification for long runs

## Example: guarded CSV pipeline

```
spec-writer ─► [HUMAN: approve ticket/spec] ─► planner ─► [HUMAN: approve plan]
   ─► executors (worktrees, allow-list, branch hook) ─► review loop (max 3) ─┬─► [HUMAN: merge PR]
                                                                             └─► escalate if stuck
```

| Risk | Guardrail | Layer |
|---|---|---|
| deletes data | `deny rm -rf`, `deny data/**` | permissions |
| pushes to main | protect-branches hook + GitHub protection | hooks + server |
| executors clobber each other | one worktree each | isolation |
| writes to Jira | read-only token + hook | credentials + hooks |
| merges broken code | required CI + human merge | server + human |
| loops forever | max rounds → escalate | escalation |

## Failure modes

| Failure | Fix |
|---|---|
| a rule exists only in the prompt | move it to permissions or a hook |
| approval fatigue | fewer, better-placed gates. Allow-list the safe commands |
| over-broad tokens | least privilege per server |
| a silent stop | escalation returns a status + reasons + a notification |
