# sampling-invariance-v1

Status: **Stage A / excluded synthetic smoke only**.

Tracks #81. This experiment is intentionally independent of PR #80 (`multiplex-capacity-v1`). It does not use #80 seeds, targets, reducers, or outcomes and does not register a production route.

## Question

Can a continuous phenotype have a finite, explicit information space while making the renderer's sampling topology a nuisance variable rather than part of phenotype identity?

The mechanism under test is a real bandlimited scalar field on the normalized 2D torus. Geometry is the field's zero level set. Sample points are observations/constraints on that geometry; they are not latent coordinates carrying generative identity.

This is the controlled opposite of an index-multiplexed / aliasing hypothesis:

```text
index-multiplexed geometry:
  sampling/index topology can carry structure

sampling-invariant field geometry:
  structure lives in a finite continuous field;
  sufficiently informative samples reconstruct it
```

## Frozen Stage-A representation

For integer bandwidth `K`, define the canonical positive half-support

```text
Lambda_K^+ = {(kx, ky): max(|kx|, |ky|) <= K,
                         (ky > 0) or (ky == 0 and kx > 0)}
```

and the real field

```text
F(x, y) = c0
        + sum_k [a_k cos(2 pi k.x) + b_k sin(2 pi k.x)]
```

for `k in Lambda_K^+`.

The coefficient-vector dimension is exactly

```text
D(K) = 1 + 2 |Lambda_K^+| = (2K + 1)^2
```

so the two Stage-A supports are:

```text
K=1 -> D=9
K=2 -> D=25
```

Because multiplying every coefficient by any nonzero scalar leaves `F(x,y)=0` unchanged, the zero-set geometry lives in a projective coefficient space with exactly

```text
geometry DOF = D - 1
```

within this representation family.

This DOF is **not** treated as a fair cross-route complexity currency. Existing handcrafted routes contain fixed program structure that is not represented by genome parameter count. Cross-representation work, if later justified, will compare equal search/evaluation budgets; DOF is used here to characterize the bandlimited family's internal capacity and reconstruction threshold.

## Reconstruction contract

For any observed zero-set point `(x_i, y_i)`,

```text
F(x_i, y_i) = 0
```

is a homogeneous linear constraint on the coefficient vector. Stack observed points into a basis matrix `A`. Reconstruction is the unit right-singular vector associated with the smallest singular value / null direction.

Two quantities are kept separate:

1. **information minimum** — `D-1` generic exact zero-set samples can determine a one-dimensional coefficient nullspace, i.e. the field up to scale;
2. **stable reconstruction density** — in the presence of sample-coordinate perturbation, more than `D-1` constraints may be required for a well-conditioned estimate.

The information minimum is a uniqueness statement, not a claim that minimum sampling is numerically robust.

## Observation schemes

Stage A uses two independent zero-point acquisition schemes:

1. `regular-lines` — evenly spaced horizontal/vertical observation lines with deterministic phase shifts; roots are refined against the analytic field;
2. `irregular-lines` — deterministic pseudorandom horizontal/vertical observation lines and scan phases; roots are refined against the same analytic field.

Both observe the same underlying continuous zero set. They do not alter coefficients.

A separate high-density regular-line extraction is used only as the geometry-reference point cloud for equivalence diagnostics.

## Excluded population

Stage A may use only the explicitly excluded synthetic seeds:

```text
91001
91007
91019
91033
```

They are engineering/validity smoke, not evidence for search capacity or artistic usefulness. They may be inspected while Stage A is being implemented.

No search holdout exists for this experiment yet.

## Stage-A invariants

For both `K in {1,2}`, every excluded seed, and both observation schemes:

### A1. Exact accounting

- coefficient dimension equals `(2K+1)^2`;
- zero-set geometry DOF equals `D-1`;
- field and observations are deterministic and finite.

### A2. Scale invariance

For fixed coefficients `c`, the zero-set point cloud from `c` and from `-3.7c` must have symmetric Chamfer distance <= `1e-10` in normalized domain units when extracted with the same reference sampler.

### A3. Information-minimum reconstruction

From exactly `D-1` exact observed zero-set points:

- constraint-matrix rank must equal `D-1`;
- recovered/source coefficient cosine similarity, sign-invariant, must be >= `0.999999`.

From exactly `D-2` exact points:

- nullspace dimension must be at least 2.

This is the explicit uniqueness / underdetermination boundary.

### A4. Resampling equivalence

From `2(D-1)` exact observations acquired independently by either observation scheme:

- coefficient cosine similarity must be >= `0.999999`;
- reconstructed-vs-source zero-set symmetric Chamfer distance must be <= `1e-6`.

A representation that changes identity merely because the observation scheme changes fails Stage A.

### A5. Stable-density diagnostic

Add deterministic zero-point coordinate noise with standard deviation `1e-4` in normalized domain units and reconstruct at:

```text
1x = D-1 samples
2x = 2(D-1) samples
```

Across the complete frozen Stage-A rectangle:

- median `2x` coefficient cosine similarity must be >= `0.999`;
- minimum `2x` coefficient cosine similarity must be >= `0.99`;
- median `2x` coefficient error (`1-similarity`) must be strictly lower than median `1x` error.

The `1x` noisy result is deliberately diagnostic and is allowed to be poor. If `2x` is also unstable, Stage A fails; do not move into capacity/search work.

## Decision

`STAGE_A_VALID` iff A1-A5 all pass over the complete excluded rectangle.

If Stage A fails, change only the representation/reconstruction design and rerun excluded smoke. There is no holdout to protect yet, but every design change must remain recorded.

If Stage A passes:

1. freeze this field basis and reconstruction semantics;
2. wait for #80 to resolve before choosing comparators;
3. design a separate preregistered capacity experiment with fresh, untouched seeds/targets;
4. compare cross-representation capacity at equal candidate/search budget, not nominal parameter count;
5. keep deterministic arithmetic aliasing and state-dependent exponentiation as separate hypotheses.

Passing Stage A does **not** establish structural superiority, artistic usefulness, or route-admission evidence.
