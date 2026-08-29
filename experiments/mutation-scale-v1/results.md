# Mutation scale v1 — result

## Outcome

The preregistered global mutation-scale calibration selected the **existing scale unchanged**:

```text
selected multiplier = 1.00
```

Workflow `33222085480` completed all 90 route×seed blocks / 180 local+global target cases. All 180 `m=1.0` cases exactly replayed the ordinary adaptive engine under the canonical trajectory signature.

| multiplier | mean combined recovery | delta vs current |
| ---: | ---: | ---: |
| 0.50 | 0.072688 | -0.005424 |
| 0.75 | 0.075096 | -0.003016 |
| **1.00** | **0.078113** | **0** |
| 1.25 | 0.077420 | -0.000693 |
| 1.50 | 0.074508 | -0.003605 |

The strongest alternative was `m=1.25`, but its mean remained about **0.89% below** the current scale.

A useful secondary observation is heterogeneity rather than a global directional effect: `m=1.25` strictly beat baseline on 54/90 calibration blocks while still losing on aggregate. Larger steps improved average global-target recovery but reduced local-target recovery:

```text
m=1.00  local 0.097655  global 0.058570
m=1.25  local 0.093397  global 0.061442
m=1.50  local 0.085006  global 0.064009
```

That tradeoff is evidence against replacing the current stage scales with one global multiplier. It is not evidence for post-hoc route-specific multipliers.

## Holdout decision

Fresh seeds `193,197,199` were reserved before calibration and remain **untouched**.

The preregistered holdout would compare the frozen selected multiplier with exact `m=1.0`, requiring strict wins. Because calibration selected `m=1.0` itself, every such comparison would be exact equality by construction. Running the holdout would therefore consume fresh seeds while adding no information.

No holdout was run.

## Decision

Retain the current global numeric mutation amplitude as the research baseline. Do not implement a global scale change and do not tune the multiplier grid further on these benchmark seeds.

The next search-mechanics experiment should test a genuinely distinct mutation hypothesis, such as how scale is scheduled across stages or how mutation operators are diversified, rather than another global multiplier.

## Boundary

This is objective search-mechanics evidence only. It provides no artistic promotion authority, no hard representation-pruning authority, no portfolio-sufficiency claim, no production/default change, and no `SKILL.md` authority.
