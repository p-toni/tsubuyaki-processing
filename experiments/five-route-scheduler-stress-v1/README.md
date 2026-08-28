# Five-route screened scheduler stress v1

## Purpose

This is the final planned scheduler-semantic stress test before freezing reviewer-scheduler research and returning to search-quality work.

The merged pair-matrix scheduler has already preserved exact screened-search trajectories on 12 three-route runs. This experiment changes the workload shape materially:

- all five registered research representations are active;
- the production-calibrated route probe depth is restored to 2 exemplars per route;
- each route receives three viable independent search starts after screening;
- survivor/refinement work is deeper than the earlier three-route calibration;
- three distinct briefs are crossed with two fresh seeds.

No production/default behavior changes in this PR.

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

This yields six predeclared scenarios. No failed seed or brief may be replaced.

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

The all-keep route screen and synthetic pair oracle use an authoritative source class **only to exercise the authoritative control-flow path**. They are deterministic test fixtures and are never artistic evidence.

## Compared policies

```text
current pair group-K2
vs
opt-in explicit pair-matrix triad group-K2
```

Both use the actual public `prepare_probe(...) → resume_adaptive_search(...)` path and the real blinded queue encoders/decoders.

The two policies are executed in separate CI jobs for each frozen scenario, then compared by an aggregate job. This is execution sharding only: the policy code, seeds, briefs, candidate budgets, queue caps, trajectory signatures, and comparison gates are unchanged.

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

Any one violation fails the experiment.

## Aggregate gate

If all six hard gates pass:

- mean tasks, rounds, replays, and exposures must be no worse with triads;
- at least four of six scenarios must show strict task savings;
- there must be no observed scheduler-specific representation starvation or queue pathology.

## Scaling investigation

The first combined pair+triad five-route run exceeded the 20-minute CI boundary. A frozen two-replay profile isolated the cost before any architecture change:

```text
baseline pair replay mean        29.75 s
baseline triad replay mean       29.81 s
selector render calls/replay      1,020
selector render time/replay      ~12.3 s
archive generation/replay        ~1.7 s
```

The selector was rendering the same immutable candidate phenotype repeatedly within one replay. A selector-instance-local frame cache removes only that duplicated work; it does not persist across evidence rounds and cannot change pair IDs, search decisions, RNG, or evidence authority.

Measured after the cache:

```text
selector render calls/replay        318   (-68.8%)
pair replay mean                  23.88 s (-19.7%)
triad replay mean                 25.15 s (-15.6%)
```

All prototype regressions remained green. A complete combined representative scenario still hit the 20-minute boundary because K=2 intentionally requires many full evidence replays. Therefore the experiment is sharded by policy instead of introducing checkpointing, persistent caches, or other search-runtime semantics solely for synthetic CI convergence.

## Decision boundary

Passing this experiment freezes scheduler-semantic research for now. Pair-matrix triads remain opt-in because synthetic replay cannot establish human artistic-judgment fidelity. The next research PR should study **search leverage / search quality**, not reviewer scheduling.

Failing a semantic gate reopens scheduler work only around the concrete failure. Hitting a combined-job wall-time boundary alone is not a semantic failure and is handled by independent policy jobs plus exact artifact aggregation.
