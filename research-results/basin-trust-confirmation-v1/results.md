# Basin trust confirmation v1

Decision: **NOT_CONFIRMED**.

This is the preregistered fresh mechanical confirmation of the basin-preserving exploitation mechanism from #72. It is not artistic evidence and does not authorize automatic production/default adoption.

## Population and transport

- 32 fresh complete master seeds
- 5 fixed route strata
- 160 route×seed blocks
- two target regimes: `same-basin` and `identity-jump`
- all hard invariants passed
- GitHub Actions run `33249680729`
- sealed aggregate artifact `9715480072`
- aggregate digest `sha256:06f8fadf2f3a192b3299f54e1622e31d322148eeda5cd7ee5ef67efd3bbbd59c`

## Preregistered decision rule

`CONFIRMED` required all three:

1. same-basin one-sided 95% Student-t lower bound > 0;
2. every leave-one-route-out same-basin mean > 0;
3. interaction one-sided 95% Student-t lower bound > 0.

With `n=32`, `df=31`, one-sided 95% critical value `t=1.695519`.

## Result

### Same-basin primary effect

- mean: **+0.0273643**
- median: +0.00171369
- SD: 0.136836
- SE: 0.0241894
- one-sided 95% lower bound: **-0.0136492**

Gate 1: **FAIL**.

### Leave-one-route-out robustness

All five means remained positive; range:

- minimum: **+0.0179696**
- maximum: +0.0387724

Gate 2: **PASS**.

### Specificity interaction

`same-basin delta - identity-jump delta`:

- mean: **+0.0725717**
- median: +0.0410054
- SD: 0.167861
- one-sided 95% lower bound: **+0.0222591**

Gate 3: **PASS**.

The identity-jump mean itself was **-0.0452073**.

## Route diagnostics

| route | same-basin | identity-jump | interaction |
|---|---:|---:|---:|
| recurrence | +0.0649432 | +0.0900985 | -0.0251554 |
| orbit | +0.0551440 | -0.0331072 | +0.0882513 |
| family | +0.0280830 | -0.0903803 | +0.1184633 |
| sheet | +0.00691946 | -0.1214194 | +0.1283389 |
| filament | -0.0182681 | -0.0712283 | +0.0529601 |

Route values are heterogeneity diagnostics, not route votes and not authority for pruning or route-specific retuning.

## Interpretation

The mechanism retained the expected **specificity signature**: constraining exploitation to the local trust region is materially better when the target remains within the selected basin than when the target requires an identity crossing. That interaction generalized on fresh seeds.

However, the actual within-basin improvement was too noisy to establish a positive population-level effect under the preregistered primary gate. Therefore the mechanism is **not reliable enough to become a default exploitation policy**.

The correct conclusion is not that basin structure is useless. It is that the evidence supports basin identity as useful search state / architecture, while this particular frozen restricted mutator is not confirmed as a generally superior exploitation operator.

## Next action

Do **not** tune local mutation using these fresh outcomes. Close the local mutation/topology/scale line and move to archive/repertoire architecture using completed evidence. Basin lineage and phenotype niches may be represented explicitly, but no allocator may assume the #72 trust-region mutator is beneficial by default.
