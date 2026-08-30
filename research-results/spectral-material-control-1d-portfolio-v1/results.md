# Spectral material-control intrinsic-1D portfolio v1 — result

Decision: **SPECTRAL_MATERIAL_CONTROL_1D_PORTFOLIO_PROMISING**.

Under the same total 12-challenger budget, replacing half of native numeric mutations with the confirmed spectral operator improves mechanical target recovery across the intrinsic-1D route class.

## Fixed-budget intervention

Both policies start from the same two hard-valid bases.

- native-only: 6 native attempts per start = 12 total
- mixed: first 3 native attempts per start are the exact common prefix of native-only, plus 3 spectral attempts per start = 6 native + 6 spectral = 12 total
- native mutation scale remains 1.0
- spectral operator remains K=2 / amplitude 16
- invalid attempts count; there is no replacement sampling
- no adaptive scheduler is involved

## Primary result

- native-only mean added recovery: `0.012513172971714961`
- mixed mean added recovery: `0.026257409944887716`
- mixed-minus-native mean: **`+0.013744236973172752`**
- median delta: `+0.0072416471543849115`
- one-sided 95% lower bound over 24 master-seed means: **`+0.009772121482104055`**
- meaningful wins (`> +0.005`): `53.61%`
- meaningful losses (`< -0.005`): `11.85%`

## Route-level generalization

Every intrinsic-1D route independently clears its preregistered positive confidence-bound gate:

| Route | Mean delta | One-sided 95% lower bound |
| --- | ---: | ---: |
| recurrence | `+0.02473836893602048` | `+0.014384031801430261` |
| orbit | `+0.010707021971198565` | `+0.006456467752303471` |
| filament | `+0.005787320012299216` | `+0.00245903430283145` |

## Target-family robustness

All five target-family means and all five leave-one-family-out means are positive. The largest family contributes only `23.69%` of positive advantage, below the 50% concentration ceiling.

## Validity

- baseline native: `100%`
- mixed native prefix: `100%`
- mixed spectral pooled: `97.45%`
- recurrence spectral: `100%`
- orbit spectral: `93.75%`
- filament spectral: `98.61%`

The mixed spectral half therefore clears the frozen >=95% pooled and >=90% per-route validity gate.

## Interpretation

The confirmed spectral operator is not merely useful when given extra evaluations. It remains useful when it **replaces half of the incumbent native mutation budget**.

This supports experimental runtime integration of a fixed native+spectral operator portfolio for intrinsic-1D routes. It does not establish artistic superiority, candidate-promotion authority, or production-default status.

The 50/50 split, amplitude 16, and consumed seeds are now closed to tuning on this evidence.

## Provenance

- authoritative run: `33308055958`
- summary artifact: `9731121566`
- digest: `sha256:23b0680f500d553e500d6db41dfa1acdf4cd4e9d59d5c8d015bb83f5530f5b1d`
- authoritative experiment head: `076609f386bc51a626f25d232784643f35ee02ad`
