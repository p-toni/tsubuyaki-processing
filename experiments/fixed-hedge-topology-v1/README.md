# Fixed hedge topology v1 — diversification without prediction

## Result

The preregistered untouched holdout does **not** support a general fixed hedge.

```text
selected adaptive share = 0.50
fresh seeds             = 179, 181, 191
supporting routes       = 2/5
required                = >=4/5

→ general fixed-hedge leverage not supported
```

The fixed hedge nevertheless improved the overall holdout mean:

```text
50/50 hedge      0.08460
adaptive         0.07717
relative delta  +9.64%
```

That gain is not representation-general. Family and filament pass (`2/3` strict-win seeds each); recurrence, orbit, and sheet do not. The route-level gate therefore overrides the positive aggregate diagnostic.

The regime split shows what the hedge is buying:

```text
local   hedge 0.08230 vs adaptive 0.09034
global  hedge 0.08691 vs adaptive 0.06399
```

It trades local depth for global coverage, but the trade is too uneven across representations for a general policy change.

See `calibration.json`, `results.json`, and `results.md` for the frozen evidence.

## Question

After #57–#60 failed to generalize route identity, static start geometry, and paid mutation response as predictors of depth-vs-breadth payoff, can a fixed budget hedge capture useful upside from both without predicting a latent regime?

## Policy

Every candidate policy shares the exact current adaptive paid explore prefix:

```text
3 common starts
× 4 explore mutations per basin
= 12 paid explore candidates
```

All prefix candidates remain eligible.

Let `R` be the number of candidate evaluations the full adaptive trajectory would spend after that prefix. For fixed adaptive share `h`:

```text
k = floor(h * R + 0.5)
```

The hedge keeps the first `k` causally generated candidates from the real adaptive continuation and spends the remaining `R-k` evaluations on independent route-native breadth samples from the same isolated breadth RNG stream used in #60.

The final candidate count is exactly equal to adaptive. Invalid breadth samples consume budget. There is no runtime signal, threshold, route map, target-regime label, semantic prior, or artistic judge.

Endpoints are explicit controls:

```text
h = 0.0  → paid explore prefix + all remaining budget to breadth
h = 1.0  → exact adaptive candidate pool
```

## Calibration

Calibration used all seeds already consumed by topology research:

```text
101, 103, 107,
109, 113, 127,
131, 137, 139,
149, 151, 157,
163, 167, 173
```

Across five routes: 75 route×seed blocks / 150 target-regime cases.

Frozen share grid:

```text
0.0, 0.25, 0.5, 0.75, 1.0
```

The preregistered rule selected `h=0.50`:

| adaptive share | mean combined improvement |
| ---: | ---: |
| 0.00 | 0.07046 |
| 0.25 | 0.07271 |
| 0.50 | **0.07834** |
| 0.75 | 0.07696 |
| 1.00 | 0.07830 |

Exact numerical ties would choose the larger adaptive share. Calibration made no hypothesis claim.

## Untouched holdout

Reserved before calibration and executed only after `h=0.50` was frozen:

```text
179, 181, 191
```

Only the selected share was executed on these seeds.

A route required at least `2/3` strict wins over adaptive; general support required at least `4/5` routes.

| route | strict wins | support |
| --- | ---: | --- |
| recurrence | 1/3 | no |
| orbit | 1/3 | no |
| family | 2/3 | yes |
| sheet | 1/3 | no |
| filament | 2/3 | yes |

## Decision

Stop the depth-vs-breadth topology line.

The accumulated sequence has now tested both prediction and fixed diversification:

```text
#57 route identity                → failed to generalize
#59 static common-start geometry  → failed to generalize
#60 paid mutation response        → failed to generalize
#61 fixed depth/breadth hedge     → positive mean, failed generality gate
```

Further thresholds, predictors, or hedge ratios would be post-hoc optimization over the benchmark rather than a distinct hypothesis. The next research program moves to a different search-mechanics axis: mutation-scale scheduling.

## Durable evidence

- `calibration.json` — frozen calibration and selected share;
- `results.json` — frozen untouched-holdout result;
- `results.md` — interpretation and next research direction;
- `policy.py`, `aggregate_calibration.py`, `aggregate_holdout.py` — deterministic protocol.

Temporary calibration and holdout workflows are removed after completed runs.

## Boundary

Objective search-mechanics research only. The positive aggregate mean does not authorize artistic promotion, hard representation pruning, portfolio sufficiency claims, production default changes, or `SKILL.md` changes.
