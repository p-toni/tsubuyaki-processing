# Fixed hedge topology v1 — diversification without prediction

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

Use all seeds already consumed by topology research:

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

Select the single share with highest mean combined normalized improvement over all 75 calibration blocks. Exact numerical ties choose the **larger adaptive share**, conservatively staying closer to the current baseline.

Calibration makes no hypothesis claim.

## Untouched holdout reserved before calibration

```text
179, 181, 191
```

Only the selected share will be executed on these seeds.

## Holdout primary gate

For each route×fresh seed, compare the fixed hedge's combined local/global improvement against current adaptive combined improvement.

A seed counts only on a **strict** hedge win. Equality does not count, so the `h=1` adaptive control cannot pass trivially.

```text
>=2/3 strict-win seeds → route supports fixed hedge
>=4/5 supporting routes → general fixed-hedge leverage supported
```

## Why this is distinct from #58–#60

This experiment does not ask an observable to classify topology. The allocation is fixed before seeing a target instance. It tests whether diversification itself is useful when the adaptive-vs-breadth oracle gap is real but instance-level predictors have failed.

## Boundary

Objective search-mechanics research only. Even a positive result would justify only a later opt-in runtime experiment. It cannot authorize artistic promotion, hard representation pruning, portfolio sufficiency claims, production default changes, or `SKILL.md` changes.
