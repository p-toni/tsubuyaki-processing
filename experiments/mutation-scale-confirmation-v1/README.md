# Mutation scale confirmation v1

## Question

Does the consumed-seed #70 signal for a **global numeric mutation multiplier of 1.25** replicate on genuinely fresh master seeds under the qualified `sparse-geometry-v1` metric?

This is the one fresh confirmation permitted by the #68 roadmap after the #56–#63 geometry replay. It confirms one fixed mechanism; it does **not** re-open multiplier search.

## Frozen contrast

- baseline: global numeric mutation multiplier `m = 1.0`
- candidate: global numeric mutation multiplier `m = 1.25`
- routes: `recurrence`, `orbit`, `family`, `sheet`, `filament`
- regimes per route/seed: historical `local` and `global` targets
- all search topology, budgets, starts, target construction, route grammar, candidate IDs, tie breaks and RNG behavior remain frozen
- intervention changes only the existing numeric mutation `scale` argument
- alpha jitter remains unchanged, matching #62
- `m=1.0` must exactly replay the ordinary baseline trajectory for every route/seed/regime

The contrast is event-aligned: both arms make the same candidate calls and consume RNG in the same places. Ordinary paired master seeds are therefore an appropriate counterfactual coupling; no event-keyed RNG rewrite is introduced here.

## Metric

Use exactly `sparse-geometry-v1` from #69 via the already-tested installer in `experiments/search-history-geometry-replay-v1/metric.py`.

No metric tuning is allowed from confirmation outcomes.

## Fresh population

Fixed **n = 32 complete master seeds**:

`1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223`

These seeds are deliberately separated from the consumed 101–199 historical population. A separate smoke-only seed `9001` is allowed for infrastructure validation and is excluded from all analysis.

No sequential stopping. No replacement or extension of the 32-seed set after outcomes are visible unless an infrastructure failure makes a declared seed technically unusable; such an event must be recorded and the scientific run treated as incomplete until resolved.

## Why n=32

#70's consumed calibration estimate for `m=1.25 - m=1.0` was:

- mean complete-master-seed effect: `+0.00793328`
- SD of complete-master-seed effects: `0.01790553`

For a directional paired confirmation at one-sided alpha `0.05`, the normal-approximation planning equation

`n ≈ ((z_0.95 + z_0.80) * SD / effect)^2`

gives approximately 32 master seeds. The final inference uses the observed fresh-sample SE and a one-sided 95% Student-t lower bound; the planning approximation does not substitute for the fresh result.

## Primary estimand

For route `r`, seed `s`:

`delta[r,s] = combined_improvement(m=1.25) - combined_improvement(m=1.0)`

where combined improvement is the equal mean of the historical local and global regimes.

For master seed `s`:

`seed_effect[s] = mean_r delta[r,s]`

Primary effect:

`Delta = mean_s seed_effect[s]`

Seeds are stochastic replicates. Routes are fixed strata and are never treated as 160 independent observations.

## Preregistered confirmation rule

The candidate is **CONFIRMED** only if both are true:

1. the one-sided 95% Student-t lower confidence bound for `Delta` is strictly above `0`; and
2. every leave-one-route-out mean effect is strictly above `0`.

Otherwise the result is **NOT CONFIRMED**. There is no route-vote gate and no fallback threshold.

The second condition encodes the actual claim: a useful general portfolio-scale change must not owe its sign to one representation. It does not require every individual route mean to be positive.

## Required diagnostics

Always report:

- mean, median, SD and SE of complete master-seed effects
- one-sided 95% lower t-bound
- route means and medians
- local and global mean deltas
- leave-one-seed-out mean range
- leave-one-route-out mean range
- largest absolute route×seed cell
- strict-positive/nonnegative cell counts, descriptive only
- exact `m=1.0` baseline replay status for every regime

## Decision boundary

If **CONFIRMED**:

- mutation scale `1.25` becomes the evidence-backed default scale candidate for the current search architecture;
- do not infer that the stage schedule `q=1.25` is valid;
- next research should move up to basin-preserving / representation-allocation search rather than continue local scale tuning.

If **NOT CONFIRMED**:

- retain `m=1.0`;
- stop local mutation/topology knob tuning;
- move directly to route-aware basin-preserving / repertoire search.

Either outcome closes the local-knob branch.

## Artistic authority

This is a mechanistic search experiment using hard geometry. It cannot by itself establish artistic quality, promote a representation, or replace independent/human evidence for artistic decisions.
