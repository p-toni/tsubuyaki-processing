# sampling-invariance search v1 — objective search pilot

Status: **preregistered before consumed search-seed execution**.

Confirmed capacity is not sufficient for route admission. This pilot asks whether the fixed `bandlimited-k2` capacity can be navigated efficiently by the calibrated projective mutation under equal candidate-evaluation budgets.

This is an objective target-recovery experiment only. It does not test artistic quality or register a production route.

## Frozen prerequisites

Required evidence:

- `SAMPLING_INVARIANCE_CAPACITY_CONFIRMED` persisted under `research-results/sampling-invariance-capacity-confirmation-v1/`;
- `CALIBRATION_VALID` persisted under `research-results/sampling-invariance-search-calibration-v1/`.

Frozen representation/scoring files:

```text
experiments/sampling-invariance-v1/field.py
  blob 66f59d92ab39379d3a2016d18adbd271827997dd
experiments/sampling-invariance-v1/capacity.py
  blob fa5aa481ddab9babff17abdf1e4342d7ed74d2a2
experiments/sampling-invariance-v1/fast_binary_metric.py
  blob 7e1c875350050312971d9397091e8708752c0bcd
experiments/sampling-invariance-search-v1/spectral_operator.py
  blob c86f3a5b9d2862afba4232956066faeda9f378f0
```

The calibrated angle schedule is frozen exactly:

```text
0.04, 0.08, 0.16, 0.32 radians
```

repeated four times for 16 incremental evaluations.

## Benchmark targets

Reuse all 15 fixed representation-neutral targets from the confirmed capacity study:

- 3 disconnected-loops;
- 3 nested-loops;
- 3 concave-loops;
- 3 open-networks;
- 3 dense-regions.

These targets are now a **benchmark, not a new holdout**. They are reused intentionally to isolate the new variable: search policy. The operator and angle schedule were calibrated without target-recovery outcomes.

Dense-region targets remain in the primary rectangle as negative controls; they are not removed despite the known capacity weakness.

## Candidate budget

Every policy receives exactly **20 scored candidate evaluations per master-seed x target**:

```text
4 shared valid initial starts
+ 16 incremental evaluations
= 20 total
```

Invalid incremental candidates consume their evaluation slot and cannot win. They are never replaced.

The four valid initial starts are generated once per master seed and shared exactly across every target and policy. Attempts required to obtain those four valid starts are initialization diagnostics and are identical across policies.

## Policies

### 1. independent-breadth

The four shared starts plus 16 new independent coefficient draws from the frozen Stage-B prior.

Each incremental draw is evaluated once. If invalid, it consumes the slot and is ineligible.

This is the equal-budget non-search baseline.

### 2. fixed-parent-geodesic

For each target:

1. score the four shared starts;
2. choose the objective-best initial start, ties by stable start id;
3. generate all 16 calibrated geodesic mutations from that same fixed parent;
4. angle sequence is `(0.04, 0.08, 0.16, 0.32) x 4`.

This tests local mutation capacity without lineage adaptation.

### 3. adaptive-geodesic

For each target:

1. begin from the same objective-best initial start used by fixed-parent;
2. for each of the same 16 mutation events, mutate the current parent at the scheduled angle;
3. if the child is valid and strictly improves target distance, it becomes the parent for the next event; otherwise the parent remains unchanged.

The fixed-parent and adaptive policies use the same deterministic mutation-event RNG labels and angle sequence. Because tangent directions are defined at the parent point, the realized child directions diverge only after adaptive search changes parent.

No backtracking, restart, extra evaluation, early stopping, or target fitting is allowed.

## Metric / estimands

Metric: frozen exact-binary equivalent of `sparse-geometry-v1`.

```text
recovery = 1 - sparse_geometry_distance
```

Per master-seed x target:

```text
adaptive_vs_breadth = best_adaptive_recovery - best_breadth_recovery
adaptive_vs_fixed   = best_adaptive_recovery - best_fixed_recovery
adaptive_gain_from_initial = best_adaptive_recovery - best_initial_recovery
```

A meaningful improvement is strictly greater than `0.005` recovery.

Report valid yield and unique rendered phenotype rate for each policy. Invalid candidates count in the denominator.

## Populations

Excluded smoke-only seed:

```text
94999
```

Consumed pilot master seeds — first 20 primes strictly greater than 95000, fixed before execution:

```text
95003
95009
95021
95027
95063
95071
95083
95087
95089
95093
95101
95107
95111
95131
95143
95153
95177
95189
95191
95203
```

No replacement or seed addition.

## Hard invariants

For every consumed master seed:

1. exact 15-target rectangle;
2. exact shared four-start fingerprints across all policies for a target;
3. exact 20-evaluation budget per policy x target;
4. fixed/adaptive initial parent identical;
5. fixed/adaptive mutation angle/event labels identical;
6. no invalid-candidate replacement;
7. target suite fingerprint identical across all seeds;
8. all frozen source blobs exact.

The aggregate fails closed if any invariant fails.

## Pilot advancement gate

`SPECTRAL_SEARCH_PROMISING` iff the complete 20-seed x 15-target rectangle satisfies all:

1. every hard invariant passes;
2. mean `adaptive_vs_breadth` > `0`;
3. every leave-one-target-family-out mean `adaptive_vs_breadth` > `0`;
4. mean `adaptive_vs_fixed` > `0`;
5. at least `30%` of seed-target cells have `adaptive_vs_breadth > 0.005`;
6. adaptive incremental valid yield >= `0.95`;
7. no target family contributes more than `60%` of total positive `adaptive_vs_breadth` contribution.

The 30% threshold is fixed before execution as a practical-effect guard: a positive average driven by a small number of lucky target cells is not sufficient.

## Interpretation / next step

If not promising:

```text
persist the negative pilot
→ do not tune this exact operator on these consumed seeds
→ diagnose whether failure is mutation geometry, parent allocation, or capacity/search mismatch using only preregistered diagnostics
```

If promising:

```text
freeze operator + angle schedule + policy + benchmark + metric
→ power-plan one fresh confirmation, including fresh target geometries as an additional generalization layer
→ only after confirmed objective search evidence consider blinded artistic admission
```

Deterministic arithmetic aliasing, state-dependent exponentiation, additional bandwidths, gradient fitting, SVD target reconstruction, and target-specific coefficient optimization are outside this experiment.
