# Start-state topology selector v1 — result

## Calibration

Calibration used only previously consumed seeds `101,103,107,109,113,127,131,137,139` across all five routes.

The frozen grid selected:

```text
τ = 0.5
```

Historical mean combined improvement rose from `0.0783` for the always-adaptive null (`τ=0`) to `0.0989` at `τ=0.5`. The selected threshold chose the simple probe in `91.1%` of calibration regime cases.

## Untouched holdout

Fresh seeds were the preregistered `149,151,157`. The frozen `τ=0.5` and `p=4` simple probe were used unchanged.

The primary gate counted only strict wins over adaptive.

| route | strict wins | support |
| --- | ---: | --- |
| recurrence | 1/3 | no |
| orbit | 2/3 | yes |
| family | 0/3 | no |
| sheet | 2/3 | yes |
| filament | 1/3 | no |

```text
supporting routes = 2/5
required          = >=4/5

→ general start-state topology leverage not supported
```

## Diagnostics

Mean combined normalized improvement:

```text
adaptive-vs-simple oracle   0.0931
always simple probe         0.0732
start-state selector        0.0692
adaptive                    0.0639
```

The selector was correct against the per-regime adaptive-vs-simple oracle only `36.7%` of the time and incurred `0.0239` mean oracle regret.

It chose:

```text
simple-probe  29/30 regime cases
adaptive       1/30 regime cases
```

That single adaptive switch was itself wrong. So the selector did not improve on simply using the frozen simple probe; it reduced mean performance from `0.0732` to `0.0692`.

The concentration statistic does separate the constructed target regimes on average:

```text
mean local concentration   0.1672
mean global concentration  0.0806
```

but that separation does not transfer into reliable policy choice. In particular, `family` has the highest route-average concentration (`0.2715`) yet gets `0/3` strict selector wins.

## Decision

Reject static common-start basin concentration as a general adaptive-vs-simple topology selector.

The next test should use **observed mutation response / early search progress**, not static start geometry. A useful signal needs to answer a causal question such as:

```text
when we spend a small shared prefix probing local mutations,
does improvement compound enough to justify sequential depth,
or should the remaining budget go to simpler basin discovery/search?
```

The prefix must count against the same total evaluation budget and its candidates should remain eligible, so the experiment measures a real online policy rather than a free diagnostic oracle.

No production/default search behavior change is authorized by this result.

## Evidence boundary

Objective search-mechanics evidence only. No artistic candidate promotion, hard representation pruning, portfolio sufficiency claim, or production `SKILL.md` change follows from this experiment.
