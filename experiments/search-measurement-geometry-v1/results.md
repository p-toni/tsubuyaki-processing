# Search measurement geometry v1 — result

## Executive result

`sparse-geometry-v1` **passes the preregistered out-of-design metric holdout**.

The central failure from #67 is resolved:

```text
30/30 holdout targets:
shift1 < shift2 < shift3 < shift6 < shift12
```

This includes all family and sheet targets, where the overlap-only `sparse-shape-v2` had failed heavily.

The metric is therefore qualified for the next research step: one complete consumed-seed remeasurement of search experiments #56–#63.

It is **not** adopted as an artistic or production benchmark.

## Run

Workflow: `search-measurement-geometry` run `33228969040`.

Design population, already inspected by earlier metric work:

```text
101,103,107
5 routes × 3 seeds × local/global = 30 targets
```

Out-of-design metric holdout:

```text
109,113,127
5 routes × 3 seeds × local/global = 30 targets
```

These holdout seeds were already consumed by historical search experiments, so no fresh search-policy evidence was spent, but they had not been used to design #64/#67/#69 metrics.

## Frozen metric

Per frame:

```text
placement = capped foreground-centroid displacement
shape     = radius-3 tolerant F1 after centroid alignment
extent    = foreground bbox width/height error
mass      = relative foreground ink-mass error

distance  = mean(placement, shape, extent, mass)
```

No weights or normalizations were changed after results opened.

## Holdout contract

| relation | passes | required |
|---|---:|---:|
| exact == 0 | 30/30 | 30 |
| blank == 1 | 30/30 | 30 |
| shift1 < shift2 < shift3 < shift6 < shift12 | **30/30** | 30 |
| shift3 < fade50 | 30/30 | 30 |
| shift12 < deleteRightThird | 30/30 | 27 |
| validAlpha < deleteRightThird | 30/30 | 27 |
| deleteRightThird < blank | 30/30 | 30 |
| validNeighbor < unrelatedValid | 30/30 | 27 |
| validNeighbor < denseBBox | 30/30 | 27 |
| duplicateShift6 > fade50 | 29/30 | 27 |
| duplicateShift6 > shift12 | 30/30 | 27 |

Qualification: **PASS**.

## Translation behavior

Holdout mean distances are exactly monotonic:

```text
shift1   0.00625
shift2   0.01250
shift3   0.01875
shift6   0.03750
shift12  0.07500
```

More importantly, this is not an aggregate illusion: the strict chain holds on every one of the 30 holdout targets.

That is the intended architectural benefit of scoring absolute placement separately from translation-aligned intrinsic geometry.

## Other holdout means

```text
exact              0.000000
validNeighbor      0.010574
shift3             0.018750
shift12            0.075000
validAlpha         0.092429
duplicateShift6    0.142506
fade50             0.154367
unrelatedValid     0.253737
denseBBox          0.397083
deleteRightThird   0.473936
blank               1.000000
```

The design population also passed every tested contract, but it is diagnostic only because those seeds influenced metric development.

## One holdout violation worth preserving

The sole failed non-mandatory relation is:

```text
sheet / seed 113 / local:
duplicateShift6 > fade50   FAIL
```

In that case, a synthetic 50% post-render fade pushes all foreground pixels below the fixed binary support threshold, so the geometry components treat the faded render as blank:

```text
fade50 distance          1.000000
duplicateShift6 distance 0.143795
```

This exposes a real threshold discontinuity. It does **not** change the preregistered qualification result: `duplicate > fade` required 27/30 and passed 29/30, while the route-native `validAlpha` control passed its ordering relation on 30/30 holdout targets.

Research consequence:

- keep this as an explicit caveat;
- do not retune the threshold after seeing it;
- watch alpha/material behavior in historical replay diagnostics;
- if actual valid-candidate rankings show threshold-driven reversals, reopen the instrument before fresh confirmation.

## Decision

Proceed to one coherent **consumed-seed #56–#63 remeasurement** under `sparse-geometry-v1`.

That replay must:

- include #62 global mutation scale and #63 stage schedule, not only #56–#61;
- preserve historical target construction, candidate generation, budgets, RNG behavior and calibration partitions;
- reconstruct historical policy choices under the new metric where required;
- preserve all route×seed continuous paired effects;
- analyze uncertainty over complete master seeds rather than treating route×seed cells as independent;
- classify historical conclusions as `SURVIVES`, `REVERSES`, or `UNRESOLVED/HETEROGENEOUS`;
- consume no fresh search seed.

Only after that remeasurement may one mechanistically interpretable contrast be selected for a fresh confirmatory experiment.

## Boundary

Instrument qualification for research replay only. No artistic promotion authority, representation pruning, production/default search change, benchmark adoption, or `SKILL.md` change follows from this result.
