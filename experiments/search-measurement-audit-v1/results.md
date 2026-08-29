# Search measurement audit v1 — result

## Executive result

Both methodological concerns were real.

1. The historical stochastic route-vote gate is not suitable for confirmatory search-quality inference.
2. The matched-frame mean absolute pixel distance is falsified as a structural target-recovery objective for this sparse line-art domain.

The candidate `sparse-shape-v1` passed the preregistered basic sanity suite and therefore qualifies for a **consumed-seed replay experiment only**. It is not adopted as the benchmark yet.

## A. Historical route-vote gate

Historical rule:

```text
strict majority of seeds -> route supports
>=4/5 supporting routes -> general support
```

Exact general-gate probabilities:

| seeds / route | p(seed win)=0.50 | 0.55 | 0.60 | 0.65 | 0.70 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 0.1875 | 0.2947 | 0.4246 | 0.5661 | 0.7042 |
| 9 | 0.1875 | 0.3749 | 0.5979 | 0.7940 | 0.9203 |
| 21 | 0.1875 | 0.4855 | 0.7887 | 0.9491 | 0.9934 |

The important nuance is that additional seeds **do improve power**. For example, at a true per-seed win probability of 0.60, the general gate rises from 42.5% power at 3 seeds to 78.9% at 21 seeds.

But the null general-pass probability remains **18.75%** for every odd seed count because a symmetric majority vote maps each route back to a 50/50 binary outcome under the null, after which the `>=4/5` route vote dominates the type-I behavior.

### Decision

Retire this two-stage vote from confirmatory **stochastic search-quality** inference.

This does not invalidate deterministic scheduler gates. Exact trajectory preservation, queue bounds, replay identity, and similar invariants remain proof-like pass/fail properties rather than noisy effect estimates.

Future stochastic experiments should preserve paired continuous effects through aggregation instead of converting seed outcomes to route wins and route outcomes to a second win count.

## B. Current pixel-MAE target objective

Audit population:

- five representations;
- consumed seeds `101,103,107`;
- local + global target per route×seed;
- 30 generated targets total.

Hard falsification contract:

```text
if blank is closer than the exact target shifted only 3px on any target,
MAE is not a valid structural target-recovery objective
```

Result: **30/30 failures**.

| variant | mean current MAE to target |
| --- | ---: |
| exact | 0.000000 |
| valid alpha-only variant | 0.001919 |
| valid route-native neighbor | 0.003096 |
| blank | 0.004944 |
| exact target shifted 3px | 0.007866 |
| unrelated valid same-route candidate | 0.008546 |

A blank canvas therefore scores about **37% closer** to the target than an exact three-pixel translation on average.

This is not an edge case:

```text
blank beats shift3          30/30
blank beats valid neighbor   7/30
blank beats unrelated valid 30/30
```

Every representation failed the shift-vs-blank contract on all six of its tested targets.

### Decision

The current matched-frame grayscale MAE is falsified as the structural target-recovery objective used by the recent search-policy arc.

It may still be a literal pixel-alignment distance, but that is not the construct these experiments intended to measure. Search-policy conclusions whose evidence depends on this objective are now provisional and need replay under a validated structural metric before they can support architecture decisions.

## C. Candidate `sparse-shape-v1`

Candidate:

```text
foreground support = pixel > 20
shape distance      = 1 - tolerant F1, radius 3px
ink-mass error      = relative foreground mass difference
metric              = 0.8 * shape + 0.2 * mass
```

Preregistered qualification required all 30 targets to satisfy:

```text
exact == 0
shift3 < blank
fade50 < blank
valid-alpha < blank
blank >= 0.99
shift3 <= 0.25
```

Result: **30/30 targets passed every contract**.

Mean distances:

| variant | sparse-shape-v1 |
| --- | ---: |
| exact | 0.000000 |
| exact shift 3px | 0.000000 |
| valid route-native neighbor | 0.004048 |
| valid alpha-only variant | 0.075618 |
| 50% ink fade | 0.099861 |
| unrelated valid same-route candidate | 0.397980 |
| blank | 1.000000 |

### Important limitation

The candidate is deliberately tolerant, and the 3px dilation makes the exact 3px translation score **zero**. That is acceptable for the preregistered sanity test but is too coarse to treat as final validation of metric sensitivity.

Therefore `sparse-shape-v1` is **qualified for replay research, not adopted**.

Before any production/default benchmark replacement, it should face a sensitivity suite covering at least graded translations, partial structure deletion, density/rib changes, topology changes, and meaningful route-native phenotype differences.

## Research consequence

The recent topology/scale negatives cannot be treated as strong evidence that those policy directions lack leverage, because their quality instrument was measuring a construct with a deterministic sparse-image failure mode.

This does not mean those policies were actually good. It means the correct state is **unresolved**.

Next:

1. replay the prior search-policy comparisons under `sparse-shape-v1` using only already-consumed seeds;
2. preserve continuous paired effects, equal-weighting routes rather than using the retired two-stage vote;
3. compare whether the qualitative conclusions from the old MAE arc survive;
4. only then design a fresh-seed confirmatory experiment if a meaningful signal remains.

No additional fresh seeds are needed for that replay.

## Evidence boundary

This is research-instrument validation only. It does not authorize artistic promotion, representation pruning, a production/default change, or automatic benchmark replacement.
