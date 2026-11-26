# Judge Panel (Best-of-N)

**Generate N different solutions, score them with independent judges against a rubric, then pick the winner and borrow the best ideas from the rest.**

```
          ┌─► generator A (angle: simplest) ─┐
problem ──├─► generator B (angle: robust)  ──├─► judges ×3 (rubric) ──► synthesize: winner + best ideas
          └─► generator C (angle: UX-first) ─┘
```

- One attempt, refined over and over, gets stuck near its first idea. N **different** attempts cover more options.
- Different **angles** matter more than N identical runs.
- Judges score against a **rubric** and don't see who wrote what.

## When to use

- Many valid solutions, and choosing well matters: designs, APIs, architecture, UX.
- Open problems where the first idea is often not the best.

## When not to

- There's one right answer you can check: use tests (`01`, Axiom 2).
- Small decisions. N generators + judges cost N+ times more.

## Example: design the running timer (exercise 5)

```js
export const meta = { name: 'timer-design', description: 'Generate 3 timer designs, judge, synthesize',
  phases: [{ title: 'Generate' }, { title: 'Judge' }, { title: 'Synthesize' }] }

const ANGLES = [
  'simplest: fewest changes, reuse entries table (end_time NULL = running)',
  'robust: handles browser close, two tabs, midnight crossing',
  'UX-first: one-click start/stop, live elapsed time, resume last project',
]
const SCORE = { type: 'object', properties: {
  scores: { type: 'array', items: { type: 'object', properties: {
    design: { type: 'string' }, fit: { type: 'number' }, risk: { type: 'number' }, effort: { type: 'number' }, ux: { type: 'number' } },
    required: ['design', 'fit', 'risk', 'effort', 'ux'] } } }, required: ['scores'] }

phase('Generate')
const designs = (await parallel(ANGLES.map((a, i) => () => agent(
  `Design a running timer for mock_up (exercise 5). Angle: ${a}.
   Give: data model change, API, UI, edge cases, test plan. Max 40 lines. No code.`,
  { label: `design:${i}` })))).map((d, i) => ({ id: String.fromCharCode(65 + i), d })).filter(x => x.d)

phase('Judge')
const RUBRIC = `Score each 1-5: fit (CLAUDE.md conventions, no migrations needed), risk (5 = low),
  effort (5 = small), ux. Judge the content only.`
const votes = await parallel([1, 2, 3].map(j => () => agent(
  `${RUBRIC}\n${designs.map(x => `<design id="${x.id}">${x.d}</design>`).join('\n')}`,
  { schema: SCORE, label: `judge:${j}` })))

// tally in code
const total = {}
votes.filter(Boolean).flatMap(v => v.scores).forEach(s => {
  total[s.design] = (total[s.design] || 0) + s.fit + s.risk + s.effort + s.ux })
const ranked = Object.entries(total).sort((a, b) => b[1] - a[1])
log(`scores: ${JSON.stringify(ranked)}`)

phase('Synthesize')
return await agent(`Winner is design ${ranked[0][0]}. Write the final design using it as the base,
  and graft in only the clearly better ideas from the others. Note which ideas you took and why.
  ${designs.map(x => `<design id="${x.id}">${x.d}</design>`).join('\n')}`)
```

| Piece | Why |
|---|---|
| a different angle per generator | real variety, not 3 copies |
| ids A/B/C, not angle names | judges aren't biased by the label |
| a rubric with numbers | comparable scores, tallied in code |
| 3 judges | one judge's quirks average out (Axiom 7) |
| synthesis grafts ideas | better than winner-takes-all |

Then: the final design → `spec-writer` → planner (`02`). A human approves the spec.

## Failure modes

| Failure | Fix |
|---|---|
| all designs alike | stronger, opposed angles |
| judges prefer longer answers | length limit for generators. Rubric says "content only" |
| judges agree with the first design shown | shuffle the order per judge |
| synthesis becomes a messy mix | winner as the base, only clear improvements grafted |
| cost | use it only for decisions with many valid options. Cheaper models for the judges |
