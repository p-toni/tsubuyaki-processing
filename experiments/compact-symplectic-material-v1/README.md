# Compact symplectic material v1

## Decision

Does a deployment-native three-shear material representation improve finished compact filament animations enough to justify adding it as an optional compact representation?

This study follows `complete-workflow-audit-v2`, which found that expanded multi-mode spectral material could be artistically useful but did not survive the <=280-character deployment boundary. This experiment does **not** compress a high-dimensional field. The treatment is compact by construction.

Frozen base: `caddc6d36ebb064ffe45f4c866641b9dbf9c5226`.

## Representation

Both arms share the exact same compact two-scale moving filament base:

```text
u -> modulated traveling phase p(u)
x0 = cx + sx*u
y0 = cy + sy*(primary traveling wave + secondary traveling wave)
```

Control `NATIVE` renders `(x0,y0)` directly.

Treatment `SHEAR3` applies three alternating sinusoidal shears at each frame:

```text
x1 = x0 + A sin(y0/q + t/t1 + phi1)
y1 = y0 + B sin(x1/r + t/t2 + phi2)
x2 = x1 + C sin(y1/s + t/t3 + phi3)
```

Each fixed-time shear is globally invertible by subtraction of the same sine term; its Jacobian determinant is exactly 1. Their composition is therefore invertible and area-preserving. Applied to one continuous open filament, it cannot create a branch or closed-loop topology by identification.

This is intentionally different from the failed audit compression attempts, which approximated a 25-coefficient spectral field with one or two additive Fourier modes after artistic selection.

## Population

Excluded smoke: `769999`.

Authoritative master seeds:

```text
769003 769019 769037 769053 769071 769089
769107 769127 769149 769167 769181 769199
```

The seed determines a fresh compact base and the treatment's shear parameters. The control and treatment within a pair share every base parameter exactly.

## Parameter contract

Base parameters are drawn once per pair from frozen bounded sets/ranges chosen for ordinary compact filament viability:

- axial span `sx`: 132..156
- transverse scale `sy`: 58..82
- primary spatial frequency: 4.5..7.5
- phase modulation amplitude: 0.35..0.95
- phase modulation frequency: 2.0..4.5
- primary amplitude fraction: 0.55..0.82
- secondary amplitude fraction: 0.10..0.24
- secondary spatial frequency: 6.0..10.5
- primary/secondary time denominators: 20..36 / 24..44

Treatment-only shear parameters:

- amplitudes `A,B,C`: 7..14 px
- spatial denominators `q,r,s`: 24..44 px
- time denominators: 38..64 frames
- phases: 0..2pi

All numeric literals are deterministically quantized for the final post. No parameter is tuned after rendering.

## Hard preconditions

For every authoritative pair, before human review:

1. both exact complete posts end `//#つぶやきProcessing`;
2. both fit <=280 raw Unicode code points and <=280 X-weighted characters;
3. both execute over frames `1, 50, 100, 150`;
4. both retain meaningful left-to-right axial coverage and in-frame survival;
5. treatment inverse-roundtrip error for the three shears is <=1e-9 on the frozen numerical probe set;
6. the two arms' base parameter records are byte-identical;
7. all 12 pair artifacts are present.

Mechanical checks are vetoes only. They do not choose the artistic winner.

## Blinded review

The authoritative job creates two separate artifacts:

- reviewer package: 12 A/B rows x four matched frames, plus ratings template;
- sealed key: A/B identity, exact generated posts and parameter provenance.

A cryptographically random per-run salt determines orientation. The key is not inspected until all 12 ratings are committed.

Reviewer question for each pair:

> Which final compact animation would you rather keep as an original #つぶやきProcessing filament, considering material richness, coherence, composition and motion across all four times?

Allowed: `A>B`, `B>A`, `equivalent`, `unreviewable`.

## Advancement gate

`COMPACT_SYMPLECTIC_MATERIAL_ARTISTIC_SUPPORT` requires all:

1. 12/12 mechanical pair preconditions pass;
2. >=10 reviewable pairs;
3. >=8 decisive pairs;
4. SHEAR3 decisive win rate >0.65;
5. one-sided exact binomial p<=0.10 against p=0.5.

If the gate fails, close this exact three-shear representation without nearby parameter tuning on the consumed `769xxx` population.

If it passes, the result authorizes only an optional compact filament material primitive. A later ablation may ask whether nonlinear shear composition adds value beyond other equal-cost compact sinusoidal terms; this experiment does not claim that mechanism-level comparison.
