# Spectral material-control calibration v1

Decision: **`SPECTRAL_MATERIAL_CONTROL_CALIBRATED`**

Selected amplitude: **16 px-equivalent normalized displacement scale**.

## Authoritative evidence

- head: `41167c0bf7bb06e2602c5c30dd71e453c67d65d5`
- workflow run: `33288153632`
- artifact: `9725169289` / `spectral-material-control-calibration`
- digest: `sha256:0e374f2a20166668c343077ad128ab2dab831d728eb1537ae67aaf01c7a9782c`
- the artifact's `calibration.json` is the canonical detailed row-level record

Earlier slow runs were operationally superseded before their calibration outcomes were read. The authoritative run uses only performance substitutions that passed explicit equivalence gates.

## Equivalence gates

### Vectorized spectral warp

- 45/45 rendered comparisons exact
- 15/15 route-validity decisions exact
- maximum point-coordinate difference: `1.657256204579568e-13`
- maximum RMS relative difference: `1.4984686074651441e-15`

### Fast grayscale sparse-geometry metric

- 66 comparison cases
- complete returned-result comparison against the frozen reference
- maximum absolute difference: **`0.0`**

## Frozen calibration population

- excluded master seeds: `99001, 99007, 99019, 99037`
- routes: recurrence, orbit, family, sheet, filament
- six valid base/field pairs per route × seed
- amplitudes: `4, 8, 12, 16, 24`
- 120 cases per amplitude
- invariant: `J grad(F^2)` control must remain sign/scale invariant and preserve geometry topology

## Result

| amplitude | pooled valid | worst route valid | median displacement | mean displacement |
|---:|---:|---:|---:|---:|
| 4 | 1.0000 | 1.0000 | 0.01633 | 0.02061 |
| 8 | 1.0000 | 1.0000 | 0.04017 | 0.05077 |
| 12 | 1.0000 | 1.0000 | 0.06432 | 0.07914 |
| **16** | **0.9667** | **0.9167** | **0.09007** | **0.10494** |
| 24 | 0.8833 | 0.6667 | 0.13908 | 0.15339 |

The frozen rule selected the largest amplitude satisfying:

1. all analytic/topology invariants;
2. pooled validity `>=0.95`;
3. every-route validity `>=0.90`;
4. median structural displacement in `[0.01, 0.12]`.

At amplitude 16, recurrence, sheet, and filament were 24/24 valid. Family and orbit were each 22/24 valid. The four failures were two `shared family law loses sibling-scale coherence` cases and two `closed recurrence loses its central aperture` cases.

Amplitude 24 is an informative upper-bound failure: 14/120 cases became invalid, with family validity falling to 2/3. The selected 16 therefore sits near the strongest deformation that still preserves the incumbent grammar contracts broadly.

## Interpretation boundary

This calibrates the bandlimited field as a **latent deformation/control substrate inside existing visual grammars**. It does not:

- admit `bandlimited-k2` as a standalone sixth artistic family;
- establish human aesthetic preference;
- establish that spectral control beats native parameter mutation;
- change production routing or pruning.

The next evidence layer is a fresh equal-budget operator test: from matched incumbent starting forms, compare native numeric mutation against amplitude-16 spectral-control mutation. Only if the spectral direction adds robust objective coverage should a new apples-to-apples human review be considered.
