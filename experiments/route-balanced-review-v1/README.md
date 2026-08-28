# Route-balanced evidence review v1

## Purpose

Calibrate how unresolved candidate comparisons are exposed to an authoritative reviewer after `lazy-evidence-review-v1` established `K=2` as the useful global pending-review cap.

The trigger was operational, not artistic: a blinded live run placed eight consecutive review slots in one recurrence/axial neighborhood before later routes received reviewer attention. That live review was subsequently provenance-corrected to `same-model`, so none of its artistic judgments are used here as ground truth.

This experiment asks only:

```text
with a fixed evidence-authoritative search trajectory,
how should a K=2 review batch be scheduled?
```

## Evidence boundary

All preference outcomes in this experiment come from a deterministic synthetic oracle used only to drive replay to convergence.

They are **not artistic evidence** and cannot justify route pruning or candidate promotion outside the calibration harness.

The search itself uses the real candidate generation, rendering, validity, parent-dependent adaptive search, and phenotype-evidence replay path. Every scheduling policy is required to end with the exact same final trajectory signature as the eager baseline.

Frozen seeds: `7, 19, 43`.

Routes: `recurrence, family, sheet`.

## Policies

```text
global-k2
  current K=2 cap; traversal order decides which two unresolved pairs fill the batch

group-k2
  K=2 plus at most one pending pair per hidden review group
  route-local pairs use route:<route>
  cross-route pairs use cross:<routeA>|<routeB>

deferred-k2
  collect all reachable unresolved pairs, then schedule two least-reviewed groups

deferred-k3
  same deferred scheduler with three reviews per batch

route-first-k2
  deferred K2, but exhaust same-route work before cross-route groups

eager
  no pending-review cap
```

Group metadata is stored only in the sealed mapping. It is not present in reviewer-facing queue metadata or panels.

## Calibration results

Every policy matched the eager final trajectory in all three frozen seeds.

| policy | mean ratings | mean review rounds | first-batch route diversity |
|---|---:|---:|---:|
| global-k2 | 21.33 | 11.33 | 1.0 |
| **group-k2** | **19.33** | **10.67** | **2.0** |
| deferred-k2 | 24.33 | 12.67 | 2.0 |
| deferred-k3 | 24.67 | 8.67 | 3.0 |
| route-first-k2 | 26.00 | 13.33 | 2.0 |
| eager | 57.67 | 5.67 | 3.0 |

Per-seed ratings / review rounds:

| seed | global-k2 | group-k2 | deferred-k2 | deferred-k3 | route-first-k2 | eager |
|---|---|---|---|---|---|---|
| 7 | 19 / 10 | 18 / 10 | 25 / 13 | 27 / 9 | 25 / 13 | 57 / 6 |
| 19 | 23 / 12 | 19 / 11 | 25 / 13 | 25 / 9 | 27 / 14 | 61 / 6 |
| 43 | 22 / 12 | 21 / 11 | 23 / 12 | 22 / 8 | 26 / 13 | 55 / 5 |

The first full deferred run also exposed an implementation bug: deferred scheduling initially inherited a base grouping gate that returned `None` whenever the eager per-group cap was disabled. That made the supposed scheduler identical to global K2. The bug was corrected and a direct regression now verifies that deferred K2 can actually choose distinct hidden groups.

## Decision

Promote **group-k2**, not the more sophisticated deferred schedulers.

Why:

1. It preserves the complete eager trajectory on every frozen seed.
2. It reduces ratings versus global K2 by about **9.4%** (`21.33 → 19.33`).
3. It slightly reduces review rounds (`11.33 → 10.67`).
4. It changes the first batch from one route to two distinct route groups.
5. It requires no second scheduling phase, route priority, or speculative global proposal collection.

The deferred designs solve route coverage more aggressively, but they pay for it with extra speculative ratings. Route-first postpones cross-route work but still over-reviews local lineages. Neither earns its additional complexity.

## Runtime consequence

The screened evidence-authoritative path now defaults to:

```text
candidate_max_pending_reviews = 2
candidate_max_pending_reviews_per_group = 1
```

The global cap still controls total reviewer burden. The per-group cap only prevents one hidden route/group from occupying both pending slots when another reachable group is available later in traversal.

The per-group cap can be disabled programmatically with `None` for historical replay or explicit experiments.

## Scope

Research/prototype only. No production `SKILL.md` change and no representation-family change.

The representation-vocabulary / additional-yuruyurau trigger remains unchanged. This experiment addresses reviewer scheduling, not mathematical representation sufficiency.
