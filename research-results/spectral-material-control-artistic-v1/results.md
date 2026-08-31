# Spectral material-control blinded artistic review v1

Decision: **ARTISTIC_SUPPORT_NOT_DEMONSTRATED**

The preregistered human gate fails on the frozen 12-block same-grammar native-only vs native+spectral review.

## Human judgments

- reviewable blocks: **12 / 12**
- `equivalent`: **12**
- `A>B`: 0
- `B>A`: 0
- `unreviewable`: 0
- total mixed-vs-native net preference: **0**
- recurrence net: **0**
- orbit net: **0**
- filament net: **0**
- every leave-one-route-out net: **0**

Formal gates:
1. >=9/12 reviewable: **PASS**
2. total mixed-vs-native net preference > 0: **FAIL**
3. every leave-one-route-out net preference > 0: **FAIL**

## Critical diagnostic

After the judgments were fixed and the A/B key was unsealed, every one of the 12 blocks had:

```text
native champion phenotype
= mixed champion phenotype
= shared starting phenotype
```

The reviewer-facing A/B frame regions were also verified pixel-for-pixel identical for all 12 blocks at `t=30,90,150`.

So this result should **not** be interpreted as evidence that spectral material control itself is artistically neutral. The intervention generated a different candidate archive, but the current deterministic temporal proxy selected the unchanged starting candidate in both arms for every review block.

This localizes the failure to the delivery/authority layer:

```text
mechanically useful archive variation
→ deterministic proxy promotion
→ unchanged start
→ human sees no treatment difference
```

The earlier runtime replay remains valid as archive-level mechanical evidence: mixed search improves best available structural recovery under equal budget. What this review falsifies is the stronger claim that the current single-proxy-champion delivery path exposes that improvement to a human reviewer.

## Research consequence

Do not tune the spectral operator from these human ties.

The next artistic test must evaluate the same confirmed native-only vs mixed search at the **portfolio surface** that the mechanical result actually supports, without allowing the deterministic proxy selector to collapse both archives to the shared start before review.

Use fresh review seeds and a frozen target-blind portfolio sampling rule. Human review remains the artistic authority.
