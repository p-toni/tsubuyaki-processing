# Mutation scale schedule v1 — result

## Calibration

The frozen schedule family was:

```text
explore       = 1.00 * q
round A       = 0.70
refine-local  = 0.55 / q
refine-jump   = 1.20
```

Grid: `2/3, 0.8, 1.0, 1.25, 1.5`.

Across 90 consumed-seed route blocks / 180 local+global target cases, all 180 `q=1.0` cases exactly replayed ordinary search. Candidate counts were invariant.

| q | mean combined improvement | delta vs q=1 |
| ---: | ---: | ---: |
| 0.6667 | 0.076060 | -0.002052 |
| 0.8 | 0.076085 | -0.002028 |
| 1.0 | 0.078113 | 0 |
| **1.25** | **0.078125** | **+0.000012** |
| 1.5 | 0.075987 | -0.002126 |

The preregistered calibration winner was `q=1.25`, but by only `0.000012` mean combined improvement over baseline.

## Fresh holdout

Fresh seeds `193, 197, 199` were opened only after calibration selected `q=1.25`. The holdout compared only `q=1.25` against exact `q=1.0`.

Historical preregistered route-vote result:

| route | strict wins | route supports? | mean paired delta |
| --- | ---: | --- | ---: |
| recurrence | 1/3 | no | -0.000922 |
| orbit | 0/3 | no | -0.004504 |
| family | 0/3 | no | -0.007570 |
| sheet | 2/3 | yes | +0.003679 |
| filament | 2/3 | yes | +0.025176 |

Only 2/5 routes support the schedule under the frozen `>=2/3`, then `>=4/5` gate, so the preregistered general-support criterion fails.

Before opening holdout results, the reducer was extended to retain paired continuous effects rather than discarding magnitude:

```text
mean delta       +0.003172
median delta     -0.001338
strict wins       5/15
non-worse         6/15
mean local delta +0.004695
mean global delta+0.001648
```

The positive mean is not broad-based. Three route means are negative. Filament is strongly influenced by one block (`seed=197`, delta `+0.074771`), while the median block is negative.

## Decision

Reject a **general** mutation-scale stage-schedule change. Keep the current schedule as the research baseline.

There may be representation-dependent behavior in sheet/filament, but do not pursue route-specific tuning yet. Two methodological assumptions used by this search-mechanics arc now require audit before further policy conclusions:

1. the stochastic two-stage route-vote gate;
2. the sparse-image mean-absolute-pixel target-recovery objective.

The schedule experiment itself remains useful as a faithfully executed preregistered negative/generalization result. Its objective-score interpretation is explicitly provisional pending that audit.

## Evidence boundary

This is objective target-recovery evidence only. It does not authorize artistic promotion, representation pruning, production/default changes, portfolio-sufficiency claims, or `SKILL.md` changes.
