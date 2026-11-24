---
name: tsubuyaki-processing
description: "Autonomously discover and refine original #つぶやきProcessing p5.js animations, inspect motion, and deliver verified executable sketches aiming for 280 characters."
---

# Tsubuyaki Processing

Autonomously discover a small mathematical cause producing a surprising, coherent animation. Given the brief and a bounded exploration budget, choose a representation, inspect rendered behavior, and use the evidence to revise, change direction, or stop. Resolve routine creative choices without requiring the user to select candidates. If no budget is supplied, choose one proportional to the task.

The capability being developed is discovery across fresh briefs. A finished sketch is evidence of that capability; a single attractive result does not establish reliability. For research priorities and evaluation, see the [research roadmap](references/research-roadmap.md).

## Essential constraints

- Use p5.js global mode unless asked otherwise. Final code must execute.
- Aim for 280 characters including the hashtag. Report both X-weighted length and raw Unicode code points. Enforce both limits only when the brief requires a standard post.
- Explore in readable code. Prefer shared mathematical causes and reusable generators. Recurrence is one possible representation.
- Preserve the defining mathematical relationships and animated identity when compressing. Matching a few frames is insufficient if the cause was removed.
- Create original work; do not reconstruct or lightly mutate a published artist's formula.

## Choose the smallest suitable representation

Load only the references needed for the request:

| Need | Guidance |
| --- | --- |
| Abstract field, sheet, filament or attractor | [Mathematical patterns](references/mathematical-patterns.md) and [style](references/style-guide.md) |
| Form emerging from dynamics, harmonics or residue families | [Math-first generators](references/math-first-generators.md) |
| Named anatomy, attachment hierarchy or local anatomical editing | [Morphology composition](references/morphology-composition.md) |
| Explicit semantic controls | [Control strategies](references/control-strategies.md), [scopes](references/control-scopes.md) and [effects](references/semantic-effects.md) |

For emergent form, think `kernel → latent fields → family operator → deformation → projection`. An animal-like appearance alone does not require a scene graph.

## Build, inspect, and stop when it is good

Build one viable readable sketch. Render representative times and inspect silhouette, material, framing and motion. Repair a broken representation before tuning it.

Record the few constraints that define the brief, such as true 2D sampling for a membrane or axial identity for a filament. A beautiful alternative that violates those constraints is a side discovery.

If the sketch meets the brief and is visually strong, proceed to compression. Search is useful when there is an identifiable shortcoming or a worthwhile alternative to explore; it is not a required ceremony.

When searching:

- retain the incumbent and promote only a valid, brief-adherent challenger that is visually preferable across matched times;
- use [discovery-search.md](references/discovery-search.md) for route-specific starting points, broadening within the brief when local changes stop helping;
- treat stage schedules as working heuristics, not proven universal optima;
- use novelty to select alternatives for inspection, never as an aesthetic score;
- stop when the budget is exhausted or new candidates cease to offer meaningful improvement. Keeping a good incumbent is a valid result; report failure if none meets the brief.

For resumable searches, branching lineages or experiments requiring reproducibility, use [discovery-state.md](references/discovery-state.md) and `scripts/discovery-state.mjs`. Initialize with the CLI so the grammar is pinned correctly. Once using that state, preserve paired causal changes, exact review evidence and historical stage legality. Ordinary sketch iteration does not require an event ledger.

## Compress and verify

After visual selection, load [compression-promotion.md](references/compression-promotion.md).

Name the defining relationships and choose a meaningful behavioral horizon before compression. It must expose the motion, relative phases or recurrence drift that make this sketch work. Keep that horizon and those relationships fixed through preflight and exact verification.

Try a simple compression of the best visual candidate. Keep the shortest version you verified that preserves its cause and animated identity. An over-target sketch can satisfy the brief. If a strict format was requested and the winner misses it, preserve the winner and try the next visually worthwhile candidate within budget. [Code golf techniques](references/code-golf-techniques.md)

Reuse a preflight that already verified the exact final code over the chosen horizon. Verify changed code again.

Verify the complete executable post, including its hashtag:

```sh
node scripts/check-length.mjs post.txt
```

At the 280-character target, `CODE//#つぶやきProcessing` leaves 259 X-weighted characters for code. The checker's pass flag answers the standard-post size question. Execute and render the exact sketch over the chosen horizon and confirm each named cause survives. [Preservation contract](references/preservation-contract.md)

Use diagnostics only for claims they can test:

| Claim | Tool |
| --- | --- |
| Density and framing | `scripts/check-visual.mjs` |
| Repeated-family latent semantics | `scripts/check-family-math.mjs` |
| Rendered control scope | `scripts/check-control-scope.mjs` |
| Declared visible control effect | `scripts/check-control-effect.mjs` |
| Compound morphology survival | `scripts/check-morphology-survival.mjs` |
| Recorded search integrity, when used | `node scripts/discovery-state.mjs validate STATE` |

Diagnostics can reveal failures; they cannot establish artistic quality. Low occupancy can be appropriate for filaments, and chaotic kernel changes need not remain local.

## Deliver

Provide the concept, readable p5.js, the complete executable sketch with its hashtag, both length counts, the runtime, the temporal horizon, and what survived compression. Include useful variation controls when relevant.

Explain consequential observation-led decisions when they help assess the discovery process. Distinguish the readable artistic winner from the deployment candidate if they differ. Report failed attempts and any human intervention when evaluating autonomy; an honest failure is still an unsuccessful discovery. Label model aesthetic judgments as provisional and report anything not actually verified.
