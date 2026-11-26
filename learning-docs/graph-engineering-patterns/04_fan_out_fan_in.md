# Fan-Out / Fan-In (Map-Reduce)

**Split the work into independent items, run one agent per item in parallel, then combine the results.**

```
            ┌─► worker(item 1) ─┐
discover ──►├─► worker(item 2) ─┤──► reduce (code or agent) ──► result
 (items)    └─► worker(item N) ─┘
```

- **Discover:** list the items (files, endpoints, components). Do it in code or with one cheap agent, ideally *before* the fan-out.
- **Map:** the same prompt for every item. Each worker sees only its own item (Axiom 5).
- **Reduce:** merge, deduplicate, rank. Use **plain code** when you can, and an agent only when it needs judgment (Axiom 6).

## When to use

- Many similar, independent items: audit endpoints, migrate components, review files, write tests per module.
- Work too big for one context.

## When not to

- Items depend on each other (use planner/executor with `depends_on`, `02`).
- Few items. 1–2 agents in sequence are simpler.

## Map variants

| Variant | Use when |
|---|---|
| `pipeline(items, stageA, stageB)` | multiple stages per item. No waiting between stages (**default**) |
| `parallel(...)` then reduce | the reduce step needs **all** results at once (dedupe, ranking) |
| `isolation: 'worktree'` per worker | workers **edit** files in parallel |

## Warm-up before the fan-out

Fan-out is where the **warm-up agent** pays off most: N identical workers all start at the same moment.

- Workers launched together **all miss the cache**. Each one pays the full cache-write price for the same starting context (tools, system prompt, CLAUDE.md).
- Fix: run **one tiny agent first with exactly the same options**, then fan out. Workers 2..N read the starting context at about 10% of the price.
- "Same options" means the same `agentType`, `model` **and `schema`**. A schema adds an output tool, which changes the tool definitions and so the starting context.
- Worth it from about 5 workers, or with a big starting context. Below that, skip it.

Details and cost math: `codebase-search-optimization/05_explore_subagents.md` (warm-up agent).

## Example: audit every endpoint

```js
export const meta = { name: 'endpoint-audit', description: 'Audit each API endpoint in parallel, then merge findings',
  phases: [{ title: 'Audit' }, { title: 'Reduce' }] }

const FINDINGS = { type: 'object', properties: { issues: { type: 'array', items: { type: 'object', properties: {
  endpoint: { type: 'string' }, problem: { type: 'string' }, severity: { type: 'string', enum: ['high', 'low'] } },
  required: ['endpoint', 'problem', 'severity'] } } }, required: ['issues'] }

// discover: passed in via args (listed beforehand, e.g. with grep "@app\." src/core/main.py)
const ENDPOINTS = args.endpoints   // ["GET /api/projects", "POST /api/entries", ...]

// the same options for the warm-up and every worker, so they all share one cached starting context
const WORKER = { schema: FINDINGS, phase: 'Audit', effort: 'low' }

// warm-up: one tiny call writes the cache before the fan-out
await agent('Reply with an empty issues list.', { ...WORKER, label: 'warm-up' })

// map: one audit per endpoint, each with a fresh, small context. They read the starting context from cache
const results = await parallel(ENDPOINTS.map(ep => () => agent(
  `Audit ${ep} in mock_up/src/core/main.py: input validation, status codes vs docs/architecture.md,
   SQL only via repository.py, test coverage in tests/test_api.py. Report only real issues.`,
  { ...WORKER, label: `audit:${ep}` })))

// reduce: plain code (no LLM): flatten, dedupe, sort
const all = results.filter(Boolean).flatMap(r => r.issues)
const failed = ENDPOINTS.filter((_, i) => !results[i])
if (failed.length) log(`no result for: ${failed.join(', ')}`)   // no silent gaps
const seen = new Set()
const unique = all.filter(i => { const k = i.endpoint + i.problem; return seen.has(k) ? false : seen.add(k) })
return unique.sort((a, b) => (a.severity === 'high' ? -1 : 1) - (b.severity === 'high' ? -1 : 1))
```

| Piece | Why |
|---|---|
| discovery passed via `args` | the item list is fixed and visible before any agent runs |
| warm-up with the same `WORKER` options | N parallel workers read the starting context from cache instead of each writing it |
| same prompt per item | the results can be compared |
| `effort: 'low'` | many cheap workers rather than one expensive agent |
| reduce in code | deterministic, free (Axiom 6) |
| `log` failed items | no silent gaps: "covered everything" must be true |

Next: send the high-severity issues through the adversarial review (`01`).

## Failure modes

| Failure | Fix |
|---|---|
| workers overlap or conflict | items split by file. Worktrees for edits |
| inconsistent outputs | `schema` on every worker |
| silent gaps (failed workers) | check for `null` results and `log` them |
| a reduce agent drowns in input | reduce in code first (dedupe, filter), then one agent on the short list |
| cost blow-up | cheap model or effort for the map + a warm-up agent before the fan-out |
| warm-up doesn't help | the warm-up and workers used different `agentType`, `model` or `schema`. Share one options object |
