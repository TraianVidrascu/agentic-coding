# Worktrees

## What is a worktree?

**An extra working folder for the same git repo, checked out on a different branch.**

```
agentic-coding/                    ← main worktree    (branch: feat/timesheet-mockup)
.claude/worktrees/csv-export/      ← extra worktree   (branch: worktree-csv-export)
.claude/worktrees/overlap-check/   ← extra worktree   (branch: worktree-overlap-check)
        all share ONE .git: same history, same commits, same remotes
```

- **Not a full copy.** Only the working files are separate. History and objects are shared, so it's fast and small.
- Each worktree has **its own branch**. Git won't check out the same branch in two worktrees.
- A commit made in one is instantly visible from the others (e.g. `git log worktree-csv-export`).

## Why use them?

- **Parallel agents**: two sessions in one folder edit the same files and break each other's work. One worktree per agent means no collisions.
- **Isolation**: a risky experiment can't break your main checkout. If it fails, delete the worktree.
- **No context switching**: review a PR or fix a bug without stashing your current work.

## What is NOT in a new worktree

Only **tracked** files are checked out. Gitignored files are missing:

| Missing | Fix in the new worktree |
|---|---|
| `.venv/` | `python3 -m venv .venv && pip install -r requirements.txt` |
| `node_modules/` | `npm install` |
| `.env`, secrets | copy them in by hand |
| `data/timesheet.db` | a fresh DB is created on startup |

Ports clash too: two backends can't both use `:8000`. Run the second one with `--port 8001`.

## Where are they stored?

- **Claude Code**: `.claude/worktrees/<name>/` inside the repo. Add `.claude/worktrees/` to `.gitignore`.
- **Plain git**: anywhere you choose, usually next to the repo (`../agentic-coding-csv`).
- `git worktree list` shows all of them, wherever they live.

## Commands

```bash
# Claude Code
claude --worktree csv-export      # new worktree + branch, session starts inside it
                                  # in a session: "work in a worktree" → EnterWorktree / ExitWorktree tools

# plain git
git worktree add -b feat/csv-export ../agentic-coding-csv   # new branch + folder
git worktree list
git worktree remove ../agentic-coding-csv                   # once merged
git worktree prune                                           # clean up stale entries
```

Subagents can get one too: `isolation: "worktree"` gives the agent its own worktree, removed automatically if it made no changes.

## Example: two exercises in parallel

Build exercise 2 (CSV export) and exercise 3 (overlap check, 409) from `mock_up/docs/exercises.md` at the same time.

```bash
# terminal 1
claude --worktree csv-export
> Do exercise 2 in mock_up/docs/exercises.md. Run pytest when done.

# terminal 2
claude --worktree overlap-check
> Do exercise 3 in mock_up/docs/exercises.md. Run pytest when done.
```

Each session first sets up its environment (`cd mock_up && python3 -m venv .venv && pip install -r requirements.txt`), then works on its own branch. When both are done:

```bash
git switch feat/timesheet-mockup
git merge worktree-csv-export          # or open a PR for each branch
git merge worktree-overlap-check       # conflicts only if both touched the same lines
git worktree remove .claude/worktrees/csv-export
git worktree remove .claude/worktrees/overlap-check
```

Tip: give parallel agents tasks that touch **different files**. Both of these change `main.py` and `repository.py`, so expect a small merge conflict.

# Appendix: Ways to get a worktree

| Way | Where | Cleanup |
|---|---|---|
| `claude --worktree <name>` | `.claude/worktrees/<name>` | Claude Code offers to remove it on exit |
| `EnterWorktree` tool (just ask "use a worktree") | `.claude/worktrees/<name>` | `ExitWorktree` |
| Subagent with `isolation: "worktree"` | temporary | auto-removed if unchanged |
| `git worktree add` | anywhere | `git worktree remove` by hand |
