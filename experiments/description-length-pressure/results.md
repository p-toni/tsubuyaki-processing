# Description-Length Pressure — Results

## Executive result

Across four math-first routes and 48 shared expanded candidates:

| condition | deployable phenotype-surviving winners |
|---|---:|
| A — description length only after expanded winner | 3 / 4 |
| B — compression preflight on expanded top-3 | **4 / 4** |
| C — hard compact-cause filter before visual selection | **4 / 4** |

B and C selected the same final candidate on every route.

C therefore provided **no final deployment gain over B** in this experiment, while removing **17 / 48 (35.4%)** expanded candidates before visual/temporal review.

The strongest current interpretation is:

> **description-length pressure should enter after open-ended expanded discovery but before committing to a single final winner.**

That is, use a compression-survival preflight on a small visual shortlist rather than either waiting until after the winner is fixed or filtering the creative population early.

## Frozen protocol

See `protocol.md`.

All A/B/C conditions saw the same expanded candidate pools. Code length did not affect generation.

Routes:

- repeated family;
- dense 2D sheet;
- intentional 1D filament;
- recurrence / living knot.

Each route contained 12 readable expanded candidates rendered at three representative times.

## Expanded visual selection

Expanded ranking was performed without considering code length.

Top candidates:

| route | expanded #1 | expanded #2 | expanded #3 |
|---|---|---|---|
| family | F12 | F2 | F5 |
| sheet | S4 | S6 | S12 |
| filament | L9 | L10 | L7 |
| recurrence | R12 | R6 | R4 |

The recurrence pool provided the key conflict: R12 was the strongest expanded phenotype but depended on a substantially richer compact cause than R6.

## Final selections

| route | A late-only | B shortlist preflight | C early pressure |
|---|---|---|---|
| family | F12 | F12 | F12 |
| sheet | S4 | S4 | S4 |
| filament | L9 | L9 | L9 |
| recurrence | **R12** | **R6** | **R6** |

Thus B/C sacrifice one expanded-rank position only on recurrence.

## Exact compact attempts

The final selected candidates were represented by actual syntactically valid one-line p5.js attempts. Complete post X-weight assumes the standard 21-weight hashtag suffix.

| candidate | code chars | total X-weight | runtime | phenotype survival |
|---|---:|---:|---|---|
| F12 | 246 | 267 | pass | pass — moderate |
| S4 | 212 | 233 | pass | pass — strong |
| L9 | 235 | 256 | pass | pass — strong |
| R6 | 257 | 278 | pass | pass |
| R12 | 229 | 250 | pass | **fail** |

All exact attempts parsed successfully. A five-frame execution under a minimal p5-compatible runtime produced finite point coordinates for every candidate.

R12 is important because **length itself passes**. Its failure is not “cannot get under 280”; it is **description-length survival**: the relationships removed to make it compact are the relationships that made the expanded phenotype the winner.

In other words:

```text
fits <=280 != defining phenotype survived
```

## Recurrence case

Expanded R12 contained residue-family structure + cross-wave deformation + an additional projection harmonic. The compact deployment attempt fit easily after those relationships were removed, but collapsed into a thin recurrent glyph.

R6 was the expanded #2 candidate. Its defining compact cause was simpler; an exact 257-character code retained enough recurrent-state modulation and transformed projection to remain a coherent living-knot phenotype.

Therefore:

```text
A: expanded #1 R12 -> compact -> FAIL survival
B: shortlist {R12,R6,R4} -> preflight -> choose R6 -> PASS
```

This is direct evidence for a pre-commit compression gate.

## Early-pressure cost

Condition C retained only candidates whose compact-cause estimate was already within the practical code budget before visual selection.

| route | retained | removed |
|---|---:|---:|
| family | 11 / 12 | 1 |
| sheet | 8 / 12 | 4 |
| filament | 10 / 12 | 2 |
| recurrence | **2 / 12** | **10** |
| total | **31 / 48** | **17 / 48** |

Despite that pruning, C selected exactly the same final winners as B.

So within this experiment B **weakly dominates** C:

- same deployable outcomes;
- same final visual winners;
- no need to suppress 35% of the expanded search space before aesthetic inspection.

The recurrence effect is especially strong: early pressure would remove R12, R4, and most other structural experiments before they could teach us what visual regimes exist. Even though R12 ultimately cannot deploy as the final tweet, discovering it still informs the aesthetic/search landscape.

## Why not claim “early pressure destroys diversity” yet

Candidate retention clearly decreases under C.

A simple raster-descriptor pairwise-distance diagnostic did **not** monotonically decrease, because tiny retained sets can contain two extreme survivors and therefore show a misleadingly large mean pairwise distance. In recurrence C keeps only 2 candidates, making this statistic particularly unstable.

Therefore the defensible finding is:

> early pressure substantially reduces **exploration opportunity / population support**, with no final benefit in this run.

Do not promote the descriptor-distance statistic into a diversity fitness measure.

## Current causal interpretation

### H1 — late-only pressure is too late

**Supported, but route-dependent.**

A worked on family, sheet, and filament. It failed on recurrence.

The failure mode is high-leverage expanded structure whose compact representation loses the relationships responsible for the visual win.

### H2 — shortlist preflight is the best tradeoff

**Supported by this experiment.**

B fixed the recurrence deployment failure while leaving successful routes unchanged.

It applies medium pressure only after the system has already discovered visually strong regimes.

### H3 — early pressure harms discovery

**Partially supported.**

We directly observed substantial pruning (35.4% overall; 83.3% on recurrence) with no deployment advantage over B.

We did **not** establish that early pressure always lowers the final visual quality, because B and C happened to converge on the same winners in all four routes.

## Recommended production model

Replace the conceptual single-winner transition:

```text
expanded search
-> visual winner
-> golf
```

with:

```text
expanded search
-> visual/temporal shortlist
-> compression-survival preflight
-> tweet-viable finalist
-> full golf
-> exact survival verification
```

The preflight should be a **falsification gate**, not an optimization score.

Ask:

1. Which mathematical relationships make this candidate worth keeping?
2. Can those relationships plausibly be expressed in the deployment budget?
3. If compressed, does the defining phenotype still exist across time?

Do not rank candidates by “shorter is better.”

## What should remain unchanged

- Keep readable/expanded mathematical discovery free from hard character pressure.
- Do not put character count into aesthetic fitness.
- Keep 280 as a ceiling, not a target.
- Keep route-aware progressive search and elitism.
- Continue exact post-length and runtime verification after golf.

## Next research question

The timing result is now good enough to justify a production-policy update, but one parameter remains unestablished:

> **How large should the visual shortlist be before compression preflight?**

This experiment used top-3 by design. It does not establish that 3 is optimal.

A future nested shortlist experiment can compare top-2 / top-3 / top-5 without regenerating candidate populations.

## Limitations

- one evaluator for expanded and compact visual preference;
- 12 candidates per route;
- four hand-authored route vocabularies;
- compact-cause proxy is route-specific and deliberately coarse;
- actual final golf attempts were hand-authored for selected candidates rather than generated by a universal compressor;
- only representative frames, not continuous animation playback;
- no morphology-first route;
- early-pressure condition filtered a shared population rather than changing the generator itself, so real early optimization pressure could have stronger effects than measured here.

These limitations argue against a universal numeric threshold, but not against the observed ordering of operations.