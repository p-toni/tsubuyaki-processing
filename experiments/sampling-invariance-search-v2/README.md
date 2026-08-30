# sampling-invariance search v2 — breadth + geodesic basin hedge

Status: **preregistered before any consumed v2 seed execution**.

## Why v2 exists

`sampling-invariance-search-v1` established three facts under equal 20-evaluation budgets:

1. projective geodesic mutation is fully valid/distinct under the calibrated angle schedule;
2. adaptive parent updating beats fixed-parent geodesic mutation in every target family;
3. a single greedily improving lineage does not robustly beat independent breadth.

The failed assumption was therefore **budget concentration in one basin**, not local mutation geometry.

This v2 tests a materially different topology: discover basins first, then hedge local exploitation across the two strongest discovered basins.

This is also consistent with earlier project evidence from `hybrid-portfolio-search`: basin discovery was useful, while the historical bottleneck was exploitation drifting away from the useful niche. The spectral field now has a calibrated projective trust-region operator, so the two previously separate mechanisms can be tested together.

No v1 angle, coefficient prior, field representation, renderer, validity rule, or metric is tuned from v1 outcomes.

## Frozen prerequisites

Required persisted results:

```text
SAMPLING_INVARIANCE_CAPACITY_CONFIRMED
CALIBRATION_VALID
SPECTRAL_SEARCH_NOT_PROMISING   # v1 single-lineage pilot
```

Frozen operator:

```text
isotropic-projective-geodesic-v1
angles = 0.04, 0.08, 0.16, 0.32 radians
```

The field remains fixed `K=2` with the Stage-B coefficient prior, viewport, validity contract, and exact-binary equivalent of `sparse-geometry-v1`.

## New target suite

Because v1 target-level outcomes have now been inspected, v2 does **not** reuse the exact 15 v1 target images as primary evidence.

Freeze 15 new deterministic representation-neutral geometries before execution:

- 3 new disconnected-loop targets;
- 3 new nested-loop targets;
- 3 new concave-loop targets;
- 3 new open-network targets;
- 3 new dense-region controls.

The family definitions and target validity contract remain unchanged, but every target fingerprint must differ from all v1 benchmark fingerprints.

The dense family remains a negative-control family; it is not removed despite the representation's confirmed weakness there.

## Shared discovery phase

Every policy receives exactly the same first **12 scored evaluations** per seed x target:

```text
4 shared hard-valid independent starts
+ 8 shared independent prior draws
= 12 discovery evaluations
```

The four starts are generated once per master seed and remain shared across all targets/policies.

The eight additional discovery draws are generated once per master seed and are also shared across all targets/policies. They are **not validity-filtered**: an invalid draw consumes its slot and cannot be selected as a basin anchor.

After the 12 discovery evaluations, valid candidates are ranked for each target by objective recovery (`1 - sparse_geometry_distance`), ties by stable candidate id.

The highest-ranked valid discovery candidate is basin anchor #1; the next highest-ranked valid candidate is anchor #2.

## Final eight-evaluation policies

All policies therefore use exactly **20 scored evaluations per seed x target**.

### A. `breadth-20`

After the shared 12 discovery evaluations, generate eight additional independent prior draws.

Invalid draws consume budget and cannot win.

This is the pure breadth baseline.

### B. `hybrid-top1`

After shared discovery:

- anchor #1 receives eight adaptive geodesic events;
- angle schedule: `(0.04, 0.08, 0.16, 0.32) x 2`;
- a valid child becomes that basin's parent only if it strictly improves target recovery.

No restart or budget transfer.

### C. `hybrid-top2`

After shared discovery:

- anchor #1 receives one full four-angle adaptive cycle;
- anchor #2 receives one full four-angle adaptive cycle;
- each basin updates its own parent only on strict objective improvement;
- budgets cannot transfer between basins.

### Matched H1/H2 events

`hybrid-top1` and `hybrid-top2` share the first four exploitation events exactly: same anchor #1, same angles, same event RNG seeds.

For the second four events they also use the same raw event RNG seeds and angle sequence. The **only intervention** is allocation:

```text
hybrid-top1: second cycle continues anchor #1 lineage
hybrid-top2: second cycle is allocated to anchor #2 lineage
```

Because tangent directions are parent-relative, realized children may differ after the allocation fork; event seeds and requested angles remain matched.

## Objective effects

For every seed x target:

```text
top2_vs_breadth = best_hybrid_top2_recovery - best_breadth_20_recovery
top2_vs_top1    = best_hybrid_top2_recovery - best_hybrid_top1_recovery
top1_vs_breadth = best_hybrid_top1_recovery - best_breadth_20_recovery
```

Meaningful advantage is strictly greater than `0.005` recovery.

Report additionally:

- discovery-best recovery;
- anchor #1 / anchor #2 recovery gap;
- accepted improvements by exploitation basin;
- valid yield and unique rendered phenotype rate;
- how often the final H2 winner originates from basin #2.

Diagnostics cannot override the gate.

## Populations

Excluded smoke seed:

```text
95999
```

Consumed v2 pilot seeds — first 20 primes strictly greater than `96000`, frozen before execution:

```text
96001
96013
96017
96043
96053
96059
96079
96097
96137
96149
96157
96167
96179
96181
96199
96211
96221
96223
96233
96259
```

No replacement, early stopping, or seed addition.

## Hard invariants

Fail closed unless every consumed block satisfies:

1. exact 15-target v2 rectangle;
2. all v2 target fingerprints are distinct and none equal a v1 benchmark fingerprint;
3. exact four shared valid starts and eight shared discovery draws across policies;
4. exactly 20 scored evaluations per policy x target;
5. invalid discovery/breadth candidates consume budget and are never replaced;
6. H1/H2 anchor #1 and anchor #2 rankings come from the identical shared discovery pool;
7. H1/H2 first four exploitation events use identical anchor #1, requested angles, and RNG event seeds;
8. H1/H2 second four events use identical requested angles/RNG seeds and differ only in basin allocation;
9. no exploitation budget transfer;
10. frozen field/operator/metric source blobs are exact;
11. all 20 master-seed blocks are present before reduction.

## Pilot advancement gate

Classify **`SPECTRAL_HEDGE_SEARCH_PROMISING`** only if all hold on the complete 20-seed x 15-target rectangle:

1. all hard invariants pass;
2. mean `top2_vs_breadth > 0`;
3. every leave-one-target-family-out mean `top2_vs_breadth > 0`;
4. mean `top2_vs_top1 > 0`;
5. every leave-one-target-family-out mean `top2_vs_top1 > 0`;
6. at least `30%` of cells have `top2_vs_breadth > 0.005`;
7. H2 exploitation valid yield >= `0.95`;
8. no target family contributes > `60%` of total positive `top2_vs_breadth` contribution.

The H2-vs-H1 gates make the mechanism claim explicit: success requires evidence that preserving a second basin is useful, not merely that any 12/8 hybrid beats breadth.

## Failure / advancement discipline

If not promising:

```text
persist v2 negative result
→ do not tune the 12/8 split, top-2 count, or angle schedule on these seeds
→ reassess whether target-aware basin ranking, fixed allocation, or search itself is the remaining bottleneck
```

If promising:

```text
freeze v2 topology and all scientific primitives
→ power-plan one fresh confirmation with another fresh target suite and fresh master seeds
→ only after confirmed objective search evidence consider blinded artistic admission
```

Still excluded from this experiment:

- higher bandwidths;
- deterministic arithmetic aliasing;
- state-dependent exponentiation;
- gradient/SVD target fitting;
- coefficient crossover;
- target-specific mutation schedules;
- artistic/model judgment.
