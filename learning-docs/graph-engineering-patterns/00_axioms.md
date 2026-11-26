# Axioms of Agent Graphs

An **agent graph** is a set of agents (nodes) connected by hand-offs (edges): planner → coders → reviewer → PR.
These axioms hold for any graph shape. The patterns in this folder are built on them.

## Axiom 1: Without an anchor, a multi-agent system is just well-organized hallucination

- An **anchor** is something outside the LLM that says right or wrong: tests, a type checker, a build, real data, a human review.
- Agents checking agents without an anchor only **agree** with each other. They don't verify anything.
- **So:** every graph needs at least one anchor. A node without one can be wrong in a convincing way.

## Axiom 2: Automated tests are the cheapest, most scalable anchor

- Unit, regression and end-to-end tests: deterministic, fast, and runnable by any agent at any node.
- A human anchor is the strongest but the slowest. Use it at a few key points (plan approval, merge).
- **So:**
  - write the tests *before* or *with* the code (`prompting-techinques/09`)
  - never let the agent that wrote the code also change the tests to make them pass

## Axiom 3: Coding agents produce "AI blobs" by default

- An **AI blob** is code that works but is bloated: duplicated helpers, needless abstractions, defensive checks everywhere, dead code, comments that repeat the code.
- Why: each agent optimizes for "pass now" in its own narrow context. It doesn't see the codebase as a whole, and it adds instead of reusing.
- In a graph it gets **worse**: N agents mean N private styles and N copies of the same helper.
- **So:**
  - add a simplify/cleanup node (e.g. `/simplify`) and a reviewer with explicit criteria
  - give coders the conventions and the existing helpers ("reuse `time_utils.py`")
  - prefer small diffs

## Axiom 4: Errors compound along a chain

- If each step is 90% right, 5 steps in a row are about 59% right (0.9⁵).
- A wrong plan at node 1 gets *faithfully implemented* by every node after it.
- **So:**
  - keep chains short
  - put anchors early: check the plan before the code exists
  - verify after the riskiest node, not only at the end

## Axiom 5: Each node should see only what it needs

- Context is finite, and every extra token dilutes attention (context pollution).
- Hand-offs lose detail. A node knows only what's in its input.
- **So:**
  - pass small, **structured** hand-offs (JSON schemas), not whole transcripts
  - give each node a narrow job, the right tools and the right model

## Axiom 6: Make the edges deterministic, let the nodes be creative

- Agents (nodes) are non-deterministic. The **control flow** between them doesn't have to be.
- Branching, loops, gates ("stop if review failed") and retries belong in **code** (workflows, hooks), not in prompts.
- **So:** decide in code whatever can be decided in code. Use the LLM only where judgment is needed.

## Axiom 7: Checking is cheaper than generating, so scale verification

- Many independent checkers > one smarter generator.
- Independent means: fresh context, a different angle, and not shown the author's reasoning.
- **So:** fan out the verifiers (majority vote, different viewpoints), and keep only what survives.

## Axiom 8: Irreversible actions need a human gate

- Merge, deploy, delete data, send messages, spend money: an agent can't undo these.
- **So:**
  - enforce gates with permissions and hooks, not prompts
  - agents propose, humans approve
