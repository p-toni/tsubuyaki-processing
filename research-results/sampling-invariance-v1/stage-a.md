# Sampling invariance v1 — Stage A

Decision: **STAGE_A_VALID**

Stage A validates only the representation/reconstruction contract for a finite real trigonometric field whose phenotype is the zero level set. It uses excluded synthetic seeds only. It does not test structural superiority, search leverage, artistic quality, or production-route admission.

## Evidence

- Workflow run: `33279811590`
- Aggregate artifact: `9722644408`
- Artifact digest: `sha256:e85aee634699fe67ba3c260f8b3f6d74020a1a7062b81e13874a17b61e59403f`
- Population: 4 excluded synthetic seeds x 2 bandwidths x 2 observation schemes = 16 cases
- Excluded seeds: `91001, 91007, 91019, 91033`
- Bandwidths: `K=1,2`
- Observation schemes: `regular-lines`, `irregular-lines`
- Coordinate-noise diagnostic: sigma `1e-4` in normalized domain units

## Frozen representation accounting

For bandwidth `K`:

```text
D(K) = (2K + 1)^2
geometry DOF = D - 1
```

because global nonzero coefficient scaling leaves the zero set unchanged.

Therefore:

- `K=1`: coefficient dimension `9`, zero-set geometry DOF `8`
- `K=2`: coefficient dimension `25`, zero-set geometry DOF `24`

This DOF is an exact within-family quantity, not a claimed fair complexity currency against handcrafted routes.

## Stage-A invariants

All passed:

1. complete frozen rectangle: **PASS**
2. exact coefficient/projective-DOF accounting: **PASS**
3. coefficient-scale invariance of the zero set: **PASS**
4. information-minimum reconstruction at exactly `D-1` exact zero points: **PASS**
5. explicit underdetermination at `D-2` points: **PASS**
6. exact reconstruction from independent regular/irregular observation schemes at `2(D-1)`: **PASS**
7. stable-density noise contract at `2(D-1)`: **PASS**

Across every exact `D-1` case:

```text
constraint rank = D - 1
nullity = 1
sign-invariant coefficient cosine similarity ~= 1
```

Across every `D-2` case:

```text
nullity = 2
```

## Uniqueness versus stability

The useful result is not merely exact reconstructibility. Minimum sampling can be numerically fragile under tiny coordinate perturbations.

Frozen aggregate diagnostic:

- median noisy `1x` coefficient error: `0.013749330327771314`
- median noisy `2x` coefficient error: `1.1049111107164222e-06`
- median noisy `2x` similarity: `0.9999988950888893`
- minimum noisy `2x` similarity: `0.9999875205118398`

Some minimum-sample cases collapse badly under sigma `1e-4` coordinate noise (for example one excluded `K=1` irregular case falls to similarity ~`0.047`). The same frozen cases remain near-perfect at 2x sampling.

So Stage A supports two distinct quantities:

```text
information minimum       = D - 1 generic exact samples
stable reconstruction     = an empirical density above that minimum
```

The first is a uniqueness boundary; it should not be confused with a robust operating point.

## Freeze boundary

Stage A is now frozen:

- real trigonometric basis and half-support convention;
- zero-level-set phenotype semantics;
- projective coefficient accounting;
- homogeneous SVD reconstruction;
- regular/irregular zero-point observation semantics;
- uniqueness-vs-stability distinction.

No Stage-A mechanism tuning should occur after capacity targets or holdout seeds are exposed.

## Next evidentiary layer

The next experiment should test **static structural capacity**, not search-operator quality:

```text
fixed independent viable candidate archives
→ representation-neutral static structural targets
→ sparse-geometry-v1 recovery
```

Cross-representation comparison must use equal viable candidate exposure, with generation attempts/valid yield retained as diagnostics. It must not match representations by nominal genome parameter count or give the bandlimited representation an analytic inverse solver against the target.

Only if independent-exposure capacity is promising should a later experiment design a search operator for spectral coefficients.
