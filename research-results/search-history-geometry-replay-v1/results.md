# #56–#63 geometry replay — final interpretation

Status: **complete**  
Workflow: `33229374600`  
Aggregate artifact: `search-history-geometry-summary` (`9708895248`, SHA-256 `a702ae60ab1572b0f57259023d85af409947e4b2c2feb4aaf6b06e462c65e436`)  
Metric: `sparse-geometry-v1`, qualified by #69's preregistered out-of-design holdout.  
Fresh search seeds consumed: **no**.

## Result

The corrected geometry metric does **not** rescue the topology/classifier line. It does surface one mechanistically simple candidate worth fresh confirmation: a **global mutation multiplier of 1.25** versus the baseline 1.0.

| Historical experiment | Classification | Corrected interpretation |
|---|---|---|
| #56 search leverage | **SURVIVES** | Local adaptive chaining is worse on average than fixed-parent local search (`-0.03410`), while global independent breadth is better than adaptive (`+0.02420`). Effects remain route-dependent; no universal staged topology follows. |
| #57 route-conditional policy | **SURVIVES** | Route-only policy mean is only `+0.00982`, with leave-one-route-out range crossing zero (`-0.01262` to `+0.03582`). Route identity remains too coarse for policy selection. |
| #58 online topology probe | **SURVIVES** | Geometry recalibrates `p=4 → p=3` and the raw mean becomes positive (`+0.03441`), but 2/3 master-seed effects are negative and removing sheet flips the aggregate sign. The tiny probe is not a robust general selector. |
| #59 start-state topology | **SURVIVES** | Geometry recalibrates `τ=0.5 → 0.3`; mean effect is `+0.01720`, but leave-one-seed-out crosses zero and the gain is family-heavy. Static start concentration is still not a reliable general selector. |
| #60 stage-1 response | **SURVIVES** | Geometry selects threshold `0.0`; selected policy becomes mechanically identical to adaptive search on holdout (`0.0` effect everywhere). The proposed stage-1 signal has no surviving mechanism. |
| #61 fixed hedge | **SURVIVES** | Geometry selects share `1.0`; selected policy becomes mechanically identical to adaptive search on holdout (`0.0` effect everywhere). There is no surviving fixed-hedge mechanism. |
| #62 mutation scale | **REVERSES — calibration decision only** | Geometry selects **1.25** instead of 1.0. Across 18 complete calibration seeds, mean seed effect is **+0.00793** (SD `0.01791`); every leave-one-seed-out mean (`+0.00593…+0.01041`) and leave-one-route-out mean (`+0.00386…+0.01120`) stays positive. This is a candidate for fresh confirmation, **not a new default**. |
| #63 mutation schedule | **UNRESOLVED / HETEROGENEOUS** | Geometry still selects `q=1.25`, but the consumed 193/197/199 holdout is small (`+0.00391`) and route-sensitive: removing filament makes the aggregate negative (`-0.00120`). Do not confirm this schedule. |

## Why #62, and only #62, advances

The global-scale intervention is event-aligned: it preserves candidate calls and RNG consumption while changing only mutation amplitude. Its consumed calibration effect is positive in both local (`+0.00719`) and global (`+0.00868`) regimes, and its influence diagnostics retain the same sign after removing any one seed or route. Recurrence is the only route with a negative mean (`-0.00512`), so the fresh claim is deliberately **general mean improvement**, not universal per-route improvement.

The schedule contrast is rejected as a confirmation target because its independent consumed holdout remains route-fragile despite a positive aggregate. The topology contrasts are either heterogeneous, collapse to baseline behavior, or change control flow enough that they would additionally require event-keyed counterfactual RNG before a clean fresh test.

## Fresh confirmation size

For #62, consumed calibration gives `mean = 0.00793328` and `SD = 0.01790553` over complete master-seed effects. A directional paired confirmation sized from this variance needs about **32 complete master seeds** for ~80% power at one-sided α=0.05 if the true effect is the observed calibration effect.

Therefore the next experiment is fixed at **n=32 fresh master seeds**, five routes per seed, comparing only `m=1.25` vs `m=1.0`. No sequential stopping and no re-selection of the multiplier.

Primary estimand remains the equal-route master-seed effect:

`seed_effect[s] = mean_route(score(m=1.25) - score(m=1.0))`

The result will report the mean, median, SD/SE, route effects, local/global decomposition, leave-one-seed-out and leave-one-route-out ranges, and largest cell. The confirmatory interpretation is directional at the master-seed level; no route-vote gate is used.

## Boundary

This replay is consumed-seed methodological reinterpretation only. It does not change production/default search behavior, prune a representation, establish artistic authority, or promote `m=1.25`. Only the planned fresh confirmation can decide whether global mutation scale advances.
