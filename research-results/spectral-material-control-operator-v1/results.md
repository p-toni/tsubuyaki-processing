# Spectral material-control operator v1 — result

Decision: **SPECTRAL_MATERIAL_CONTROL_OPERATOR_NOT_PROMISING**.

This rejects the preregistered claim that one generic amplitude-16 K=2 spectral deformation is a universally useful operator across all five incumbent grammars under the equal 12-challenger budget.

## Strong positive signal

- spectral mean added recovery: `0.025624796484072596`
- native mean added recovery: `0.012984533457409419`
- spectral-minus-native mean: `+0.012640263026663172`
- median: `+0.011522611637840241`
- all 20 master-seed means are positive
- one-sided 95% lower bound over master-seed means: `+0.010647590348138062`
- meaningful wins (`> +0.005`): `61.4%`
- meaningful losses (`< -0.005`): `19.8%`
- every target-family mean is positive
- every leave-one-target-family-out mean is positive
- largest target-family positive-advantage share: `20.86%`

## Why the formal gate fails

Two preregistered gates fail.

### Route universality

Route mean spectral-minus-native delta:

- recurrence: `+0.029912873011031363`
- family: `+0.01885041634612221`
- orbit: `+0.012054636577517238`
- filament: `+0.011399934718226408`
- sheet: **`-0.009016545519581354`**

The operator therefore does not generalize as a universal five-route control direction.

### Fresh hard validity

Spectral challenger validity:

- recurrence: `1.0000`
- sheet: `1.0000`
- filament: `0.9917`
- orbit: `0.9583`
- family: **`0.8417`**
- pooled: `0.9583`

Fresh family validity falls below the frozen per-route floor. The dominant failure is `shared family law loses sibling-scale coherence` (38 occurrences). Orbit loses its central aperture 10 times; filament loses axial identity twice.

## Interpretation

The negative decision is about **generic universality**, not about leverage. Spectral control provides a large, seed-stable, target-family-stable mechanical advantage, but its effect depends materially on incumbent grammar topology.

The next hypothesis must therefore be route-conditional and tested on fresh seeds. This consumed suite must not be reused to tune amplitude 16, challenger count, or route-specific thresholds.

Canonical workflow run: `33307272117`

Summary artifact: `9730886551`

Summary digest: `sha256:6473c6f195b099c34f43aa257ff5b87cab55359d70829d7de5b68b37e08cc843`
