# Spectral material control v1

## Why this exists

The first artistic-admission protocol for `bandlimited-k2` (#87) was invalidated before any human ratings were recorded. It compared the raw zero set of the new field representation (visually, contour lines) against complete incumbent route grammars. That answered the wrong question: it confounded **structural substrate** with **material grammar**.

The repository's earlier morphology research already separates these layers:

```text
structure / skeleton / positional field
!=
material / family / surface grammar
```

The confirmed facts are therefore kept narrow:

- `bandlimited-k2` adds structural target capacity;
- its projective coefficient space is objectively searchable;
- its raw zero-set renderer has **not** earned standalone artistic-route admission.

This experiment asks the next causal question at the correct abstraction layer:

> Can the confirmed bandlimited field act as a generic positional/deformation control **inside the existing route grammars**, while preserving their hard structural identity?

No human artistic judgment occurs in v1.

## Coupling: sign/scale-invariant Hamiltonian warp

Let the frozen K=2 field be `F(x,y)` on normalized canvas coordinates. Define

```text
P(x,y) = F(x,y)^2
v(x,y) = ( dP/dy, -dP/dx )
```

`v` is a Hamiltonian / divergence-free vector field. The important properties for this project are:

1. it deforms existing geometry instead of drawing the field's zero set;
2. it is invariant to `F -> -F`;
3. after RMS normalization it is invariant to nonzero global coefficient scaling;
4. it therefore preserves the projective coefficient geometry established by the earlier field work;
5. to first order it avoids turning the intervention into a generic density-collapse/growth operator.

For a route point `(X,Y)` on the 400x400 canvas:

```text
x = X / 400
 y = Y / 400
u = v(x,y) / RMS(v on a frozen 65x65 grid)
(X',Y') = (X,Y) + A * u
```

`A` is a fixed pixel amplitude selected only by the excluded calibration below. The same map is applied recursively to every point-bearing component of a route geometry (`spine`, `sides`, `rows`, `cols`, `organs`, `all`, etc.), so route-specific hard checkers see the warped structure rather than a renderer-only postprocess.

No clipping, edge taper, field thresholding, point deletion, point creation, or route-specific special case is allowed in v1.

## Hard algebraic invariants

Before calibration is interpretable:

- `A=0` must reproduce every source point exactly;
- `F`, `-F`, `7F`, and `-3F` must produce the same warped coordinates to numerical tolerance after normalization;
- point/list topology and point counts must be unchanged;
- all warped coordinates must be finite;
- all five current route checkers must execute against the warped geometry.

Failure => `SPECTRAL_MATERIAL_CONTROL_INVALID`; do not tune around the failure on calibration outcomes.

## Excluded amplitude calibration

Calibration population (engineering/design evidence only):

```text
master seeds: 99001, 99007, 99019, 99037
routes: recurrence, orbit, family, sheet, filament
field draws per route/seed: 6
amplitudes: 4, 8, 12, 16, 24 pixels
frames: t = 30, 90, 150
```

Native route genome and field draw are paired across every amplitude. No target score and no aesthetic/model judgment is used.

For each amplitude record:

- pooled hard-valid fraction;
- minimum route-specific hard-valid fraction;
- sparse-geometry-v1 distance from the unwarped base at `t=90`;
- in-frame fraction / checker diagnostics;
- exact algebraic invariants above.

### Frozen amplitude selection rule

Choose the **largest** amplitude satisfying all:

1. pooled hard-valid fraction >= `0.95`;
2. every route hard-valid fraction >= `0.90`;
3. median `t=90` sparse-geometry distance from base is in `[0.01, 0.12]`;
4. no algebraic invariant failure.

If no amplitude satisfies the rule, decision is:

`SPECTRAL_MATERIAL_CONTROL_NOT_READY`

and this coupling closes as tested. Do not ask for human ratings.

If one or more amplitudes satisfy it, freeze the selected amplitude. Calibration does **not** establish useful capacity or art; it only establishes a comparable, validity-preserving intervention scale.

## Next evidence if calibration passes

The next experiment must use fresh seeds/targets and compare, under equal evaluation budget:

```text
incumbent route
vs
same incumbent route + optional frozen spectral warp
```

The intervention must be nested so the augmented route can still express the unwarped base state. Primary evidence should ask whether the spectral control adds structural/recovery coverage without destroying route identity.

Only after a fresh mechanical augmentation result may a human review be opened. That review must compare **the same incumbent grammar with vs without spectral control**, never raw spectral contour lines against a complete family type.

## Boundaries

- #87 is protocol-invalid, not negative artistic evidence.
- The #87 sealed A/B key remains unopened.
- No standalone sixth route is registered here.
- No production `SKILL.md` change.
- No claim that the Hamiltonian coupling is the final artistic materialization; it is the first representation-neutral coupling that preserves the already-confirmed projective field geometry.