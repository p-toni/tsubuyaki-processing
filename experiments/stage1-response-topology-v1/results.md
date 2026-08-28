# Stage-1 response topology v1 — result

## Outcome

The preregistered general-support gate failed decisively.

```text
selected threshold = 0.025
fresh seeds        = 163, 167, 173
supporting routes  = 0/5
required           = >=4/5

→ general paid stage-1 response topology leverage not supported
```

Route support:

| route | strict wins vs adaptive | support |
| --- | ---: | --- |
| recurrence | 1/3 | no |
| orbit | 0/3 | no |
| family | 1/3 | no |
| sheet | 1/3 | no |
| filament | 1/3 | no |

Only 4/15 route×seed blocks strictly beat adaptive; 8/15 were non-worse.

## Aggregate performance

```text
dynamic selector       0.08459
current adaptive       0.09281
stage1-then-breadth    0.07586
adaptive/breadth oracle 0.11857
```

The oracle headroom is real, but the paid mutation-response signal does not recover it. Regime-level policy-choice accuracy was only `56.7%`, with mean oracle regret `0.03398`.

## Main causal finding

The central hypothesis was that useful progress during the exact paid adaptive explore stage would reveal whether sequential depth should continue.

It did not.

```text
mean paid-prefix gain, local target   0.02537
mean paid-prefix gain, global target  0.02464
```

The two constructed regimes have materially different downstream topology preferences, but nearly identical early mutation-response gain. The observed stage-1 objective improvement therefore does not expose the latent property that determines whether depth or breadth will pay off.

The final regime split reinforces this:

```text
local
  adaptive             0.10861
  dynamic selector     0.06134
  stage1-then-breadth  0.04250

global
  adaptive             0.07701
  dynamic selector     0.10784
  stage1-then-breadth  0.10922
```

Adaptive remains strongly favored for local targets; breadth is strongly favored for global targets. The selector is not learning that distinction from observable paid-prefix progress.

## Interpretation across #57–#60

Three increasingly expensive predictors have now failed to generalize:

```text
route identity
→ static common-start geometry
→ paid stage-1 mutation response
```

This is evidence against adding more classifier-driven topology stages to the current search. The remaining oracle gap should not be treated as justification for another threshold or a richer version of the same signal family.

A more defensible next question is whether a **fixed hedged allocation** can capture some adaptive/local and breadth/global upside without predicting which regime it is in. That would test budget diversification rather than another latent-regime classifier.

## Calibration harness incident

The first calibration workflow failed before producing valid blocks because the harness attempted to identify common starts by a stage label they do not carry. The corrected run identifies the already-predeclared common starts by candidate identity. Seeds, threshold grid, signal, policy, budget, and gates were unchanged. No holdout seed was touched before the correction and calibration freeze.

## Boundary

This is objective search-mechanics evidence only. It does not authorize artistic promotion, hard representation pruning, portfolio sufficiency claims, production defaults, or `SKILL.md` changes.
