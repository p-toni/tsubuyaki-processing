# Family spectral law-projection v1

## Question

Can the fixed K=2 / amplitude-16 spectral deformation that showed strong mechanical leverage on `family` in #89 be made hard-valid by projecting the warped phenotype back onto the representation's pre-existing sibling-scale law, without giving up the useful structural variation?

This is mechanical operator research only. It does not change runtime behavior and provides no artistic authority.

## Prior evidence and causal failure

#89 used one generic pointwise Hamiltonian warp across all five grammars. The universal hypothesis failed, but `family` had a large spectral-minus-native recovery delta (`+0.0188504`) while spectral validity fell to `84.17%`.

The dominant failure was the existing family checker:

```text
shared family law loses sibling-scale coherence
```

That checker is frozen independently of #89 outcomes: for each review frame it measures the coefficient of variation of anchor-to-tip sibling lengths and fails above `0.32`.

The generic spectral operator nonlinearly warps each anchor and each organ point independently, so different siblings can acquire materially different terminal scale changes.

## Frozen treatment

One route only:

```text
family
```

All arms share the exact same two hard-valid starts per master seed and exactly 12 challenger attempts per arm (6 per start). Invalid challengers consume budget and are not retried.

### Native

Existing family numeric mutation, scale `1.0`.

### Generic spectral diagnostic arm

Exact #89 Hamiltonian pointwise warp:

```text
bandwidth = 2
amplitude = 16
```

### Projected spectral treatment

Use the **same field seed and exact same generic spectral warp** as the diagnostic arm, then project only the repeated-organ terminal scale back onto the native family law:

1. pointwise-warp the complete native family geometry;
2. retain the warped root and warped anchors unchanged;
3. for each sibling organ independently, measure native anchor→tip length `L_native` and generic-warped anchor→tip length `L_warp`;
4. multiply every warped organ offset around its warped anchor by `L_native / L_warp`;
5. rebuild `all` from the unchanged warped root plus the projected organs.

This preserves each sibling's native anchor→tip length exactly while retaining field-driven anchor motion and within-organ deformation. It uses no checker threshold, target, score, human label, retry, adaptive amplitude, or post-hoc choice.

K, amplitude, field support, field seeds, starts, budgets, metric, and target suite are frozen before authoritative execution.

## Fresh evidence

Excluded smoke:

```text
762999
```

Authoritative master seeds:

```text
762003 762019 762037 762053 762071
762089 762107 762127 762149 762167
762181 762199 762223 762239 762257
762277 762293 762311 762331 762349
```

The `762` namespace must be absent from frozen pre-experiment base `7447b1a35894312d6e3c01ad9edf49aa8c7b87c1`.

## Target suite

Fifteen fresh target images across the same five structural families used by the operator program:

- disconnected loops;
- nested loops;
- concave loops;
- open networks;
- dense regions.

The target module must prove exact image-fingerprint disjointness from every prior sampling/material-control target suite through `targets_runtime.py`.

Generation of all three arms is target-independent. Targets are built/scored only after challenger archives are fixed.

## Frozen gates

Historical meaningful recovery bar:

```text
0.005
```

### Generic family support

`genericSupported` requires all:

1. hard-valid spectral challenger rate >=95%;
2. generic spectral-minus-native mean recovery >=`+0.005`;
3. one-sided 95% master-seed bootstrap lower bound >0;
4. every target-family mean generic-minus-native delta >0;
5. meaningful wins (`delta > +0.005`) outnumber meaningful losses (`delta < -0.005`).

This is diagnostic confirmation only; it is not assumed.

### Projected family support

`projectedSupported` requires all:

1. hard-valid projected challenger rate >=95%;
2. projected family-law (`shared family law loses sibling-scale coherence`) failure count <=25% of the generic arm's count when the generic arm has any such failures; otherwise projected count must be zero;
3. projected spectral-minus-native mean recovery >=`+0.005`;
4. one-sided 95% master-seed bootstrap lower bound >0;
5. every target-family mean projected-minus-native delta >0;
6. meaningful wins outnumber meaningful losses;
7. projected mean added recovery from the shared starts >=90% of generic spectral mean added recovery when the generic mean added recovery is positive;
8. no target family contributes >50% of projected positive advantage.

## Decisions

- projected and generic pass → `FAMILY_SPECTRAL_GENERIC_AND_PROJECTED_MECHANICALLY_SUPPORTED`; prefer the simpler generic operator mechanically, because the repair is unnecessary on fresh evidence.
- projected passes and generic fails → `FAMILY_SPECTRAL_PROJECTION_MECHANICALLY_SUPPORTED`; this supports the causal law-preserving repair for one later isolated integration experiment.
- generic passes and projected fails → `FAMILY_SPECTRAL_GENERIC_MECHANICALLY_SUPPORTED`; do not add the projection.
- neither passes → `FAMILY_SPECTRAL_NOT_SUPPORTED`; close this exact family spectral line.

No decision authorizes artistic promotion, default search changes, or `sheet` spectral control. No tuning on consumed `762xxx` evidence.
