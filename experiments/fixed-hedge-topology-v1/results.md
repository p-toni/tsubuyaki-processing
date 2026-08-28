# Fixed hedge topology v1 — result

## Outcome

The fixed 50/50 hedge improves aggregate mean recovery but fails the preregistered generality gate.

```text
selected adaptive share = 0.5
fresh seeds             = 179, 181, 191
supporting routes       = 2/5
required                = >=4/5

→ general fixed-hedge leverage not supported
```

Route support:

| route | strict wins vs adaptive | support |
| --- | ---: | --- |
| recurrence | 1/3 | no |
| orbit | 1/3 | no |
| family | 2/3 | yes |
| sheet | 1/3 | no |
| filament | 2/3 | yes |

Across all 15 route×seed blocks, the hedge strictly wins 7 and is non-worse on 8.

## Aggregate performance

```text
50/50 hedge mean        0.08460
adaptive mean           0.07717
absolute delta         +0.00744
relative delta         +9.64%
```

The aggregate gain comes from improved global recovery:

```text
local
  hedge      0.08230
  adaptive   0.09034

global
  hedge      0.08691
  adaptive   0.06399
```

This is a useful secondary finding: diversification trades some local-depth performance for broader global coverage, and in this particular holdout that trade is positive on average.

But the effect is not representation-general. Recurrence and orbit lose on two of three seeds, sheet supports only one strict win, and only family/filament cross the frozen route gate. The positive mean is therefore not sufficient to authorize a general search policy change.

## Calibration

On the 75 previously consumed route×seed blocks, the frozen share grid produced:

| adaptive share | mean combined improvement |
| ---: | ---: |
| 0.00 | 0.07046 |
| 0.25 | 0.07271 |
| 0.50 | **0.07834** |
| 0.75 | 0.07696 |
| 1.00 | 0.07830 |

The preregistered rule selected `0.50`. Its calibration edge over full adaptive was very small, which is why the untouched route-level gate was decisive.

## Decision across the topology line

Stop the depth-vs-breadth topology line.

The sequence now covers both prediction and diversification:

```text
#57 route identity                → failed to generalize
#59 static common-start geometry  → failed to generalize
#60 paid mutation response        → failed to generalize
#61 fixed depth/breadth hedge     → positive mean, failed generality gate
```

There is clearly instance-level oracle headroom between depth and breadth, but the evidence does not support a general mechanism for exploiting it under the current target benchmark. Continuing to add predictors, thresholds, or hedge ratios would be post-hoc search over the benchmark rather than a new hypothesis.

The next research program should move to a different search-mechanics axis. A strong candidate is **mutation-scale scheduling**: test whether the current fixed stage scales (`1.0`, `0.7`, then refinement `0.55/1.2`) are mechanically well calibrated, using equal-budget schedules and fresh holdouts. This changes how candidate neighborhoods are sampled rather than trying to decide depth versus breadth.

## Boundary

Objective search-mechanics evidence only. The positive aggregate mean does not authorize a production default, artistic promotion, representation pruning, portfolio sufficiency claim, or `SKILL.md` change.
