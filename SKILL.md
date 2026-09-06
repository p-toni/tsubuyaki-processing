---
name: tsubuyaki-processing
description: "Create original tweet-sized #つぶやきProcessing p5.js sketches: discover a compact mathematical system, inspect its animation, and produce a verified post within 280 characters."
---

# Tsubuyaki Processing

Create a small mathematical cause producing a surprising, coherent animation.

## Essential constraints

- Use p5.js global mode unless asked otherwise. Final code must execute.
- The complete post must fit both 280 X-weighted characters and 280 raw Unicode code points. The limit is a ceiling, not a target.
- Work in readable mathematical roles before golfing. Prefer shared latent variables, recurrence and reusable generators over independent decoration.
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
- stop when new candidates cease to offer meaningful improvement. Keeping the incumbent is a valid result.

For resumable searches, branching lineages or experiments requiring reproducibility, use [discovery-state.md](references/discovery-state.md) and `scripts/discovery-state.mjs`. Initialize with the CLI so the grammar is pinned correctly. Once using that state, preserve paired causal changes, exact review evidence and historical stage legality. Ordinary sketch iteration does not require an event ledger.

## Compress and verify

After visual selection, load [compression-promotion.md](references/compression-promotion.md).

Name the defining relationships and choose a meaningful behavioral horizon before compression. It must expose the motion, relative phases or recurrence drift that make this sketch work. Keep that horizon and those relationships fixed through preflight and exact verification.

Try the cheapest plausible compression of the best visual candidate. If its cause and animated identity survive, finish golfing with [code-golf-techniques.md](references/code-golf-techniques.md). If it fails, retain the artistic discovery and try the next visually worthwhile candidate. Stop when none remain; report the limitation instead of weakening the identity to obtain a length pass.

Character count constrains deployment, not artistic ranking. There is no required shortlist size. If the preflight already uses the exact final code and covers all final checks, reuse that verification; changed code needs verification again.

Verify the complete executable post, including its hashtag:

```sh
node scripts/check-length.mjs post.txt
```

`CODE//#つぶやきProcessing` leaves 259 X-weighted characters for code. Execute and render the exact post over the chosen horizon. Confirm both observable survival and preservation of the named causes; see [preservation-contract.md](references/preservation-contract.md).

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

Provide the concept, readable p5.js, executable tweet line, and verification results: raw and weighted length, runtime, temporal horizon and compression survival. Include a few useful variation controls when relevant.

Explain search lineage, anatomical structure or deployment fallback only when used. Distinguish the readable artistic winner from the deployment candidate if they differ. Report anything not actually verified.
