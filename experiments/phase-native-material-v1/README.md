# Phase-native compact material v1

## Decision

Does a compact shared-latent phase/amplitude representation improve finished filament animations enough to justify adding it as an optional compact material primitive?

This follows `complete-workflow-audit-v2` and the closed `compact-symplectic-material-v1`. The audit established a compact-representation bottleneck; the three-shear follow-up was mechanically clean but lost 0/12 vs 12/12 to the native compact filament. This experiment moves to a materially different axis: all added structure lives inside the filament's own smooth phase/amplitude law.

Frozen base: `94138c60179e15a5e0d70bf7494bbcadf7ec6726`.

## Matched representation

Both arms share the exact same compact two-scale moving filament base:

```text
x = cx + sx*u
phase0 = f1*u + m*sin(mf*u) - t/t1
y = cy + sy*(a1*sin(phase0) + a2*sin(f2*u + t/t2))
```

Control `NATIVE` renders that base directly.

Treatment `PHASEPACK` introduces one additional smooth traveling latent:

```text
z = g*u - t/t3
envelope = a1 + e*cos(z)
phase = f1*u + m*sin(mf*u + d*sin(z)) - t/t1
y = cy + sy*(envelope*sin(phase) + a2*sin(f2*u + t/t2))
```

The same `z` co-modulates amplitude and local phase curvature. The intended effect is a coherent moving packet/chirp: extra internal richness without an external coordinate warp.

Because `x = cx + sx*u` is strictly monotone in `u`, both arms remain one continuous open graph over the axial coordinate. The treatment cannot create branches or a closed-loop topology.

This is not a nearby shear variant and not a post-hoc Fourier approximation of expanded spectral material.

## Population

Excluded smoke: `770999`.

Authoritative master seeds:

```text
770003 770019 770037 770053 770071 770089
770107 770127 770149 770167 770181 770199
```

The seed determines a fresh compact base and treatment-only phase-packet parameters. Within each pair every base parameter is identical.

## Parameter contract

Base parameters:

- axial span `sx`: 132..156
- transverse scale `sy`: 58..82
- primary spatial frequency `f1`: 4.5..7.5
- static phase-modulation amplitude `m`: 0.35..0.95
- static modulation frequency `mf`: 2.0..4.5
- primary amplitude `a1`: 0.55..0.82
- secondary amplitude `a2`: 0.10..0.24
- secondary spatial frequency `f2`: 6.0..10.5
- primary/secondary time denominators: 20..36 / 24..44

Treatment-only:

- shared latent spatial frequency `g`: 1.5..3.5
- nested phase depth `d`: 0.5..1.2
- envelope depth `e`: 0.12..0.26, constrained so the primary envelope remains positive
- latent time denominator `t3`: 45..75 frames

All floating literals are deterministically quantized to one decimal place before final-post generation. No parameter is tuned after rendering.

## Hard preconditions

For every authoritative pair, before human review:

1. both exact complete posts end `//#つぶやきProcessing`;
2. both fit <=280 raw Unicode code points and <=280 X-weighted characters;
3. both execute over frames `1, 50, 100, 150`;
4. x remains strictly monotone and both arms retain meaningful axial coverage;
5. >=98% of numerical probe points are in-frame at every frozen frame for both arms;
6. both retain visible transverse extent and nontrivial temporal change;
7. treatment primary envelope remains strictly positive on the frozen probe;
8. the two arms' base parameter records are byte-identical;
9. all 12 pair artifacts are present.

Mechanical checks are vetoes only. They do not choose the artistic winner.

## Blinded review

The authoritative job produces separate reviewer and sealed-key artifacts. A cryptographically random per-run salt determines A/B orientation. The key is not opened until all ratings are committed.

Reviewer question:

> Which final compact animation would you rather keep, prioritizing visual coherence, smoothness, consistency of motion, and material richness across all four times?

Allowed: `A>B`, `B>A`, `equivalent`, `unreviewable`.

## Advancement gate

`PHASE_NATIVE_MATERIAL_ARTISTIC_SUPPORT` requires all:

1. 12/12 mechanical pair preconditions pass;
2. >=10 reviewable pairs;
3. >=8 decisive pairs;
4. PHASEPACK decisive win rate >0.65;
5. one-sided exact binomial p<=0.10 against p=0.5.

If the gate fails, close this exact shared-latent phase/amplitude representation without nearby tuning on consumed `770xxx`.

If it passes, the result authorizes only an optional compact filament material primitive. It does not promote the autonomous research runtime or reopen the recurrent/Sotaku branch.
