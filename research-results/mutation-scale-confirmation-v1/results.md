# Mutation scale confirmation v1 — result

## Decision

**NOT_CONFIRMED.** Keep the current global numeric mutation scale (`m=1.0`) as the research baseline and close the local mutation-scale / topology knob line.

The preregistered candidate was `m=1.25`, selected only from the consumed-seed geometry replay in #70. The confirmation used 32 fixed fresh master seeds × five route strata, with local and global target regimes and the qualified `sparse-geometry-v1` metric.

## Primary result

```text
complete master seeds            32
route strata                      5
route×seed cells                160
mean master-seed effect    +0.006047
median master-seed effect  +0.007231
master-seed SD              0.021846
master-seed SE              0.003862
one-sided 95% t lower bound -0.000501
```

Preregistered confirmation required both:

1. one-sided 95% Student-t lower bound > 0;
2. every leave-one-route-out mean > 0.

The second condition passed, but the first did not.

```text
leave-one-route-out mean range  +0.004694 .. +0.007589
one-sided 95% lower bound       -0.000501

=> NOT_CONFIRMED
```

## Route diagnostics

Mean paired effect by route:

```text
recurrence  +0.003035
orbit       -0.000121
family      +0.011459
sheet       +0.007414
filament    +0.008446
```

Local/global decomposition:

```text
local mean delta   +0.003116
global mean delta  +0.008978
```

`98/160` route×seed cells were strictly positive. The largest absolute cell was recurrence / seed 1151 (`+0.168199` combined), so individual cells remain much noisier than the master-seed aggregate.

## Interpretation

The consumed-seed signal from #70 did replicate directionally: the fresh mean is positive, all leave-one-route-out means remain positive, and global recovery again benefits more than local recovery. But the fixed-sample uncertainty still crosses zero. That is enough to reject a default change and, per preregistration, stop spending evidence on nearby scale/schedule/topology knobs.

This result should **not** be reframed as evidence that `1.25` is harmful. It is evidence that its general effect is too small/noisy to justify more local optimization effort relative to the next architectural lever.

## Next research phase

Move upward to the architecture already motivated by the hybrid portfolio evidence:

```text
broad basin discovery
-> preserve several distinct mathematical basins
-> route-aware trust-region exploitation inside a selected basin
-> basin / representation allocation
-> repertoire / quality-diversity search
```

The first new causal question is whether exploitation improves when basin-defining dimensions are frozen and only local deformation/detail/time/material dimensions are allowed to move.

## Provenance

- PR: #71
- workflow run: `33247221481`
- workflow conclusion: success
- aggregate artifact: `mutation-scale-confirmation-summary`
- artifact id: `9713556945`
- artifact digest: `sha256:17adab4b307fe8549a7e4273bef17fcda6c4362bae2ce2ccab2556f460f9e2b6`
- smoke seed `9001` was infrastructure-only and excluded from analysis.

## Boundary

Mechanistic search evidence only. No artistic authority, representation promotion/pruning, production default, or `SKILL.md` change follows from this result.