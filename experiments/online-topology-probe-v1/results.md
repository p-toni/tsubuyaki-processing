# Online topology probe v1 — result

## Calibration

Pilot size was calibrated only on already-consumed seeds `101, 103, 107, 109, 113, 127` using the preregistered grid `p ∈ {1,2,3,4}`.

The frozen selection rule chose `p=4`:

| p | mean combined improvement | pilot arm-choice accuracy |
| ---: | ---: | ---: |
| 1 | 0.0779 | 68.3% |
| 2 | 0.0852 | 78.3% |
| 3 | 0.0891 | 83.3% |
| 4 | **0.0943** | **88.3%** |

The grid was not extended after observing this monotonic trend.

## Untouched holdout

Fresh seeds were the preregistered `131, 137, 139`. The frozen `p=4` policy was used unchanged for every route and both target regimes.

| route | non-worse vs adaptive | replacement support |
| --- | ---: | --- |
| recurrence | 2/3 | yes |
| orbit | 1/3 | no |
| family | 1/3 | no |
| sheet | 1/3 | no |
| filament | 3/3 | yes |

Primary result:

```text
supporting routes = 2/5
required          = >=4/5

→ general online-simple replacement not supported
```

The result is equally negative under strict wins: only recurrence and filament reach 2/3 strict wins.

## What the diagnostics say

The breadth-vs-fixed part of the problem is largely solved by this mechanism:

```text
pilot arm-choice accuracy       83.3%
mean regret to simple oracle    0.0100
```

But the full topology problem is not:

```text
probe mean combined improvement       0.0730
adaptive mean combined improvement    0.0898
best-of-three mean improvement        0.1180
probe regret to best-of-three         0.0584
```

The split by hidden target regime is especially informative:

```text
local target
  adaptive   0.1456
  probe      0.0630

global target
  probe      0.0831
  adaptive   0.0339
```

So the principal remaining problem is not choosing `breadth` versus `fixed-parent-local`. It is detecting, from observable early search state, **when sequential adaptive depth is worth paying for versus when a simpler topology is better**.

## Decision

Reject this minimal two-arm probe as a general replacement for the current adaptive search.

Do not add more stages to the current staged topology. The next experiment should instead test richer *observable* early-search signals that choose between:

```text
adaptive sequential depth
vs
simple breadth/local search
```

The signal must remain target-regime-blind and must be calibrated on previously consumed seeds before evaluation on another untouched seed set.

No production/default search behavior changes are authorized by this result.

## Evidence boundary

This is objective search-mechanics evidence only. It does not authorize artistic candidate promotion, hard representation pruning, portfolio sufficiency claims, or production `SKILL.md` changes.
