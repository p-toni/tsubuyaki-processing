# Spectral material-control intrinsic-1D confirmation v1 — result

Decision: **SPECTRAL_MATERIAL_CONTROL_1D_CONFIRMED**.

The fresh confirmation supports the topology-level claim that the frozen K=2, amplitude-16 ambient spectral deformation is a mechanically useful control/search operator for the incumbent intrinsic-1D manifold class (`recurrence`, `orbit`, `filament`) relative to the existing native numeric mutator under the same 12-challenger budget.

## Primary effect

- spectral mean added recovery: `0.02888702728061083`
- native mean added recovery: `0.010045935601822485`
- spectral-minus-native mean: **`+0.018841091678788342`**
- median: `+0.017022922172621968`
- all 24 aggregate master-seed means are positive
- one-sided 95% lower bound over aggregate master-seed means: **`+0.016084450011693313`**
- meaningful wins (`> +0.005`): `70.46%`
- meaningful losses (`< -0.005`): `11.76%`

## Route-level confirmation

Every intrinsic-1D route has a positive mean and independently positive one-sided 95% lower bound across the 24 fresh master seeds:

| Route | Mean delta | One-sided 95% lower bound |
| --- | ---: | ---: |
| recurrence | `+0.029609571345791754` | `+0.022323143333829263` |
| orbit | `+0.01475587945280802` | `+0.010108993687117242` |
| filament | `+0.012157824237765258` | `+0.007905245323542991` |

The result therefore does not depend on recurrence alone.

## Target-family robustness

All five target-family means are positive:

- disconnected loops: `+0.01912179163316856`
- nested loops: `+0.019659049647909602`
- concave loops: `+0.018394506635495005`
- open networks: `+0.019426968152319618`
- dense regions: `+0.017603142325048934`

Every leave-one-target-family-out mean is positive. The largest family supplies only `20.70%` of positive advantage, far below the 50% concentration ceiling.

## Validity

- pooled spectral hard-validity: `0.9780092592592593`
- recurrence: `1.0`
- orbit: `0.9479166666666666`
- filament: `0.9861111111111112`

This clears the preregistered >=95% pooled / >=90% per-route gate.

## Interpretation

The evidence now supports **spectral control as an intrinsic-1D route-class primitive**, not as a generic operator for every grammar and not as a standalone visual family.

This does not establish artistic superiority or production admission. The practical next question is integration under a fixed total search budget: whether a portfolio containing both native and spectral operators beats native-only search on intrinsic-1D routes.

## Provenance

The original authoritative run `33307586473` produced all 24 fresh consumed seed blocks. Its aggregate job failed only because the workflow passed `../../../blocks` instead of `../../blocks`, yielding zero reducer inputs. No seed outcome was inspected.

The unchanged frozen reducer was then applied to exactly those original 24 artifacts in reduction-only run `33307720773`.

- authoritative summary artifact: `9731004084`
- digest: `sha256:7b3d1fa4ce3b0d9ab0b900f8ba6815346ffa1f0466aac706bf71d20274bcad54`
- consumed head: `c4d111b59544be4ee0b451a46e36a61cdd30894a`
- reduction head: `423b0a5533f71f764d991c0e05c3cd0cc6f49dcb`

The 24 consumed confirmation seeds must not be reused to tune amplitude, topology class, budget split, or thresholds.
