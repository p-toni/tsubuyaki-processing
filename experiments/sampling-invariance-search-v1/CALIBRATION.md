# sampling-invariance search v1 — excluded operator calibration

Status: **engineering/design calibration only; no search holdout is authorized yet**.

The capacity line established that fixed `bandlimited-k2` adds complementary structural coverage. This experiment asks the next, separate question: can that capacity be navigated efficiently by a mutation/search process?

Before defining a search holdout, calibrate the natural mutation geometry of the representation on excluded seeds.

## Representation geometry

For `K=2`, the field is represented by a nonzero 25-vector `c`, but the zero set is unchanged by any nonzero global scale. After unit normalization the phenotype therefore lives on real projective space: `c` and `-c` encode the same geometry.

The primary mutation operator is an isotropic fixed-angle tangent move:

```text
c := c / ||c||
z ~ N(0, I)
u := z - (z·c)c
u := u / ||u||
c' := cos(theta)c + sin(theta)u
```

For `theta < pi/2`, projective coefficient distance is exactly `theta`:

```text
acos(|c·c'|) = theta
```

This removes the irrelevant radial degree of freedom and gives mutation scale an exact geometric meaning.

## Excluded calibration population

Seeds:

```text
94001, 94007, 94009, 94033
```

Per seed:
- 12 independently drawn valid `bandlimited-k2` base fields;
- four mutation angles: `0.04, 0.08, 0.16, 0.32` radians;
- four independent tangent directions per base x angle.

Total: 48 bases and 768 parent→child mutations.

The coefficient prior, field renderer, viewport, validity contract, and binary `sparse-geometry-v1` scorer are reused unchanged from the confirmed capacity experiment. This calibration may not alter them.

## Calibration measurements

For every mutation record:
- requested angle;
- realized projective angle;
- absolute angle error;
- child validity;
- parent/child binary sparse-geometry distance;
- parent and child fingerprints.

Per angle report:
- valid fraction;
- distinct-child fraction;
- mean/median/SD/min/max phenotype distance;
- maximum coefficient-angle error.

## Engineering contract

The initial angle schedule is usable for search design iff:

1. maximum realized projective-angle error <= `1e-12`;
2. median phenotype distance is strictly increasing across `0.04 < 0.08 < 0.16 < 0.32`;
3. child validity fraction is >= `0.95` at every angle;
4. distinct-child phenotype fraction is >= `0.95` at every angle.

If the contract fails, the failure is excluded engineering evidence: revise only the angle schedule or operator implementation, rerun excluded calibration, and freeze the first schedule that satisfies the contract **before** any search holdout is defined.

Passing this calibration is not search evidence and cannot admit a route.
