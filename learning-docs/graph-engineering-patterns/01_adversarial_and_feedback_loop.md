# Adversarial Review and Feedback Loops

## Adversarial pattern

**Two roles with opposite goals: one builds, one tries to break it.**

```
generator ──output──► adversary ("find what's wrong")
```

- A friendly reviewer *confirms* ("looks good!"). An adversary is told to **refute**.
- It works because checking is cheaper than generating (Axiom 7), and the opposite goals cancel out each side's bias.
- The adversary is still an LLM. Its findings need **evidence**, ideally an anchor such as a failing test (Axiom 1).

## Adversarial reviewer

How to set one up so it doesn't just rubber-stamp:

| Rule | Why |
|---|---|
| **fresh context**: give it the diff and the criteria, not the author's reasoning | the author's reasoning would anchor it |
| **refute by default**: "assume it's broken. If unsure, report it" | turns friendly agreement into real searching |
| **concrete criteria** (spec, conventions, edge cases) | otherwise you get nitpicks about style |
| **evidence required**: `file:line` plus a failing input or test | separates real bugs from "maybe" |
| **structured output**: `{issues: [{file, line, problem, evidence, severity}]}` | the loop can act on it in code |
| **no fix rights**: tools without `Edit`/`Write` | a reviewer that fixes things is a second author |
| optional: N reviewers, keep issues that ≥2 agree on | filters out false positives |
| optional: a different model or angle (security, perf, correctness) | reviewers see different failure modes |

## Feedback loop

**Generate → check → feed the problems back → revise, until it passes or the budget runs out.**

(Also called **evaluator-optimizer**: the same pattern, a different name.)

```
        ┌──────────── feedback (issues + evidence) ────────────┐
        ▼                                                       │
   generator ──► anchor (tests) ──► adversarial reviewer ──► pass? ── yes ──► human gate
                                                               │
                                                     no + rounds left
```

Every loop needs three stop conditions:
1. **Pass**: anchor green and no confirmed issues.
2. **Budget**: max rounds (2–3 is typical). After that, escalate to a human.
3. **No progress**: the same issues two rounds in a row means it's stuck. Stop.

Loop types:

| Loop | Checker | Example |
|---|---|---|
| test loop | test suite | edit until pytest passes |
| review loop | adversarial reviewer | fix until no confirmed issues |
| discovery loop (loop-until-dry) | "anything new?" | keep searching for bugs until 2 rounds find nothing new |

## Failure modes

| Failure | Symptom | Fix |
|---|---|---|
| rubber-stamping | the reviewer approves every round ("LGTM", *looks good to me*) even when bugs exist | refute-by-default prompt, require evidence |
| nitpick inflation | endless style comments | severity field, gate only on high severity |
| reward hacking | the coder edits the tests or weakens checks | the coder can't touch the tests; hooks block it |
| oscillation | fix A breaks B, fix B breaks A | send the **full** issue history, not only the latest |
| infinite loop | never converges | max rounds plus the no-progress stop |

## Example: overlap detection (exercise 3)

The graph:
- **coder:** writes code and tests
- **anchor:** pytest
- **reviewers:** 3 adversarial reviewers, each with its own angle
- **feedback:** confirmed issues go back to the coder
- **limit:** max 3 rounds, then a human

```js
export const meta = {
  name: 'overlap-adversarial',
  description: 'Implement overlap detection with adversarial review loop',
  phases: [{ title: 'Code' }, { title: 'Review' }],
}

const ISSUES = { type: 'object', properties: { issues: { type: 'array', items: { type: 'object',
  properties: { file: { type: 'string' }, line: { type: 'number' }, problem: { type: 'string' },
                evidence: { type: 'string' }, severity: { type: 'string', enum: ['high', 'low'] } },
  required: ['file', 'problem', 'evidence', 'severity'] } } }, required: ['issues'] }
const LENSES = ['correctness: overlap/touching/midnight edge cases', 'conventions: CLAUDE.md rules', 'API: status codes on POST and PUT']
const key = i => `${i.file}:${i.problem}`

let history = []          // every confirmed issue so far, which prevents oscillation
let lastKeys = ''
for (let round = 1; round <= 3; round++) {
  phase('Code')
  await agent(`In mock_up/, implement exercise 3 (reject overlapping entries with 409).
    Write the tests first. Never edit existing tests. Run python -m pytest until it's green.
    ${history.length ? 'Fix these confirmed issues (full history): ' + JSON.stringify(history) : ''}`,
    { label: `code:r${round}` })

  phase('Review')
  const reviews = await parallel(LENSES.map(lens => () => agent(
    `Adversarially review the uncommitted diff in mock_up/ (git diff). Focus: ${lens}.
     Assume it is broken. Report only issues with evidence (a failing input or a test you ran).`,
    { schema: ISSUES, agentType: 'convention-reviewer', label: `review:${lens.split(':')[0]}` })))

  // keep high-severity issues that at least 2 reviewers found (majority = fewer false positives)
  const all = reviews.filter(Boolean).flatMap(r => r.issues).filter(i => i.severity === 'high')
  const counts = {}
  all.forEach(i => { counts[key(i)] = (counts[key(i)] || 0) + 1 })
  const confirmed = all.filter((i, n) => counts[key(i)] >= 2 && all.findIndex(j => key(j) === key(i)) === n)

  if (!confirmed.length) return { status: 'pass', rounds: round }          // stop 1: pass
  const keys = confirmed.map(key).sort().join('|')
  if (keys === lastKeys) return { status: 'stuck', issues: confirmed }     // stop 3: no progress
  lastKeys = keys
  history.push(...confirmed)
  log(`round ${round}: ${confirmed.length} confirmed issue(s), looping`)
}
return { status: 'escalate-to-human', issues: history }                    // stop 2: budget
```

| Piece | Axiom |
|---|---|
| pytest every round | 1, 2: an anchor |
| "never edit existing tests" | 2: no reward hacking |
| 3 lenses, majority of 2 | 7: scale verification |
| reviewers get the diff only | 5: fresh, minimal context |
| loop, gates and stops in code | 6: deterministic edges |
| full issue history sent back | 4: stops errors from compounding or oscillating |
| ends at a human, never auto-merges | 8: human gate |

Note: majority voting needs the reviewers to describe the same issue in similar words. In practice, add a small "dedupe" agent, or match on `file` + `line` instead.
