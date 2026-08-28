# Five-route screened scheduler stress v1

## Purpose

This is the final planned scheduler-semantic stress test before freezing reviewer-scheduler research and returning to search-quality work.

The earlier pair-matrix scheduler calibration preserved exact screened-search trajectories on smaller three-route workloads. This experiment materially increases the workload:

- all five registered research representations are active;
- the production-calibrated route probe depth is 2 exemplars per route;
- each route receives three viable independent search starts after screening;
- survivor/refinement work is deeper than the earlier calibration;
- three distinct briefs are crossed with two fresh seeds.

No production/default scheduler behavior changes are justified by this experiment. Pair-matrix triads remain opt-in.

## Frozen scenarios

Routes, in fixed order:

```text
recurrence
orbit
family
sheet
filament
```

Fresh seeds:

```text
89, 97
```

Briefs:

1. `living-form` — balanced living-form brief, bbox target `[0.55, 0.82]`.
2. `open-asymmetry` — open/asymmetric negative-space brief, bbox target `[0.45, 0.74]`.
3. `layered-field` — broader layered/material field brief, bbox target `[0.62, 0.90]`.

No failed seed or brief may be replaced.

## Search workload

```text
route probes                  2 / route
probe budget                 10
all-keep test screen          5 routes
additional starts             1 / route
total start budget           15
explore_per_basin             3
roundA_per_survivor           2
total_extra_budget            6
candidate pending K           2
candidate pending/group       1
```

The all-keep route screen and synthetic pair oracle use an authoritative source class only to exercise the authoritative control-flow path. They are deterministic test fixtures and are never artistic evidence.

## Compared policies

```text
current pair group-K2
vs
opt-in explicit pair-matrix triad group-K2
```

Both use the actual public `prepare_probe(...) → resume_adaptive_search(...)` path and the real blinded queue encoders/decoders.

## Hard per-scenario gate

Every one of the six scenarios must satisfy all of the following:

1. pair and triad modes produce the exact same full-state search trajectory signature;
2. pair and triad modes produce the same final winner/provisional frontier state;
3. triads do not increase review tasks;
4. triads do not increase review rounds;
5. triads do not increase search replays;
6. triads do not increase candidate exposures;
7. all five routes remain active after screening;
8. probe allocation is exactly 2 per route;
9. added start allocation is exactly 1 per route;
10. at least one actual pair-matrix triad is queued;
11. no review batch exceeds K=2;
12. no batch contains two tasks from the same hidden scheduling group.

Aggregate gate additionally requires mean tasks, rounds, replays, and exposures to be no worse with triads and strict task savings in at least four of six scenarios.

## Scaling investigation

The first combined pair+triad five-route run exceeded the 20-minute CI boundary. A frozen two-replay profile isolated the cost before any architecture change:

```text
baseline pair replay mean        29.75 s
baseline triad replay mean       29.81 s
selector render calls/replay      1,020
selector render time/replay      ~12.3 s
archive generation/replay        ~1.7 s
```

The evidence selector was rendering the same stable candidate phenotype repeatedly within one replay. A selector-instance-local frame/fingerprint cache removes only that duplicated work; it does not persist across evidence rounds and cannot change pair IDs, search decisions, RNG, or evidence authority.

Measured after the cache:

```text
selector render calls/replay        318   (-68.8%)
pair replay mean                  23.88 s (-19.7%)
triad replay mean                 25.15 s (-15.6%)
```

All prototype regressions remained green. A complete combined representative scenario still reached the 20-minute boundary because K=2 intentionally requires many complete evidence replays. The final experiment therefore executed pair and triad policies independently and compared their exact artifacts instead of introducing checkpointing, persistent caches, or new search-runtime semantics solely for synthetic CI convergence.

## Result

Source workflow run: `33207325081`, head `febfa6b8a7bca4a22c9896c8f9acb1320040c7ad`.

All twelve policy runs completed successfully. All **6/6 matched scenarios passed every hard gate**, including exact trajectory/final-state preservation, five-route coverage, normal probe/start allocation, K=2/group constraints, and actual triad-path exercise.

Every scenario also showed strict task savings. Aggregate means:

```text
metric                pair mean   triad mean   relative change
review tasks             78.67       60.67         -22.9%
review rounds            41.00       32.00         -22.0%
search replays           42.00       33.00         -21.4%
candidate exposures     157.33      140.00         -11.0%
```

The most demanding frozen block, `living-form / seed 89`, preserved the exact trajectory while reducing tasks `86 → 68`, rounds `43 → 34`, replays `44 → 35`, and exposures `172 → 157`.

Detailed signatures and per-scenario metrics are frozen in `results.json`.

## Decision

**Pass. Freeze scheduler-semantic research for now.** The larger five-route workload did not reveal a scheduler-specific semantic failure, representation starvation, queue pathology, or trajectory divergence. Pair-matrix triads remain opt-in because synthetic replay does **not** establish human artistic-judgment fidelity.

The next research line moves to objective **search leverage / search quality**, not further reviewer scheduling.
