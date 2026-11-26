# Router

**A cheap classifier looks at each request and sends it to the right agent, pipeline or model.**

```
             ┌─► question  → haiku answers directly
request ──► router (haiku, low effort) ─┼─► bug       → debug chain (reproduce → fix → test)
             ├─► feature   → spec → plan → execute pipeline (02)
             └─► unclear   → ask the user
```

- Most requests don't need the most expensive path. Routing saves cost and time.
- The router is **small**: a fixed set of labels, a structured output, a cheap model.
- Branching on its label is **code** (Axiom 6).

## When to use

- Mixed incoming work: questions, bugs, features, chores.
- A big cost gap between paths (one haiku answer vs a 10-agent pipeline).

## When not to

- All requests take the same path.
- Too few requests to justify the extra step.

## Built-in routing you already have

- **Agent descriptions:** Claude Code picks a subagent by its `description` ("Use when…"). That's a router.
- **Skill descriptions:** the same, for skills.
- **`opusplan`:** routes by *phase* (planning → Opus, execution → Sonnet).

## Example: request router

```js
export const meta = { name: 'route-request', description: 'Classify a request and run the matching path' }

const ROUTE = { type: 'object', properties: {
  route: { type: 'string', enum: ['question', 'bug', 'feature', 'unclear'] },
  reason: { type: 'string' } }, required: ['route', 'reason'] }

const r = await agent(`Classify this request for the mock_up timesheet app:
  question = asks how something works, no code change
  bug      = existing behavior is wrong
  feature  = new behavior
  unclear  = can't tell, or mixes several
  Request: """${args.request}"""`,
  { schema: ROUTE, model: 'haiku', effort: 'low', label: 'router' })
log(`route: ${r.route} (${r.reason})`)

if (r.route === 'question')
  return await agent(`Answer briefly with file:line references: ${args.request}`, { model: 'haiku' })
if (r.route === 'bug')
  return await agent(`Bug: ${args.request}. Write a failing test that reproduces it, fix it, run python -m pytest.`,
    { model: 'sonnet' })
if (r.route === 'feature')
  return { next: 'run spec-writer, then plan-feature (02)', request: args.request }   // human gate before the big pipeline
return { next: 'ask the user', reason: r.reason }
```

| Piece | Why |
|---|---|
| a fixed `enum` of labels | no free-text routing to parse |
| a short definition per label | consistent classification |
| `unclear` route | a safe fallback instead of a forced guess |
| haiku + low effort | the router must cost much less than the paths it saves |
| a feature stops at a gate | the expensive path needs a human OK (`05`) |

## Option: a "System One" model as the router (Jev)

A router doesn't need to *write* anything. It only picks a label. **System One models** are built for exactly that: fast, structured decisions with no free text.

- **Jev** (TypeSafe, named after William Stanley Jevons): *"unstructured state in, typed probabilistic decisions out"*.
- Its output is one of a **predefined set of choices** (up to 255), with a **calibrated probability** per answer. It can't return a label outside the set.
- Vendor claims: 70–500 ms vs seconds for an LLM, about $0.04 per million input tokens, output free. These are not independently verified.

| | LLM router (haiku) | System One router (Jev) |
|---|---|---|
| output | text forced into JSON by `schema` | a typed choice, by construction |
| confidence | none (or a self-reported guess) | a calibrated probability per label |
| speed / cost | ~1–3 s, cheap | ~0.1–0.5 s, cheaper (vendor numbers) |
| can explain itself | yes (a `reason` field) | no, it doesn't generate text |
| availability | now, inside Claude Code workflows | early access waitlist. Called from your own code, not from Claude Code |

**Best use: confidence-gated routing.** The fast router decides when it's sure. Anything unsure goes up to an LLM or a human.

```
request ──► Jev(route ∈ {question, bug, feature, unclear})
              ├─ p ≥ 0.85 ──► run that path
              └─ p < 0.85 ──► LLM router with reason (haiku) ──► still unclear? ask the user
```

Pseudo-code. The real API is in TypeSafe's docs; the blog post had no code samples:
```python
decision = jev.decide(state=request_text, choices=["question", "bug", "feature", "unclear"])
if decision.probability >= 0.85:
    run_path(decision.choice)
else:
    run_path(llm_router(request_text))   # slower, but gives a reason
```

When it fits:
- **High volume**, latency-sensitive routing (many requests per minute).
- Routing **inside code** (an API backend, CI bots), not interactive Claude Code sessions.
- You want a **confidence threshold**, and LLMs don't give calibrated ones.

When it doesn't:
- You need the router to explain itself or ask follow-up questions.
- Low volume: a haiku call is already cheap enough.

Source: [Introducing System One models and Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) (a vendor announcement. All numbers are their claims).

## Failure modes

| Failure | Fix |
|---|---|
| misroutes (bug labeled question) | clearer label definitions + few-shot examples (`prompting-techinques/02`) |
| a costly path for easy work | check the route distribution in your logs (`07`) |
| the router is too smart (and expensive) | keep it a classifier. No tools, no exploring |
| mixed requests | route to `unclear`, or split the request first |
