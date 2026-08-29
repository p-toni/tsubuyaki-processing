# Search measurement sensitivity v1

## Purpose

Stress-test the `sparse-shape-v1` target-recovery metric qualified in #64 before any fresh-seed search confirmation.

#64 fixed the deterministic sparse-image failure of pixel MAE, but it deliberately left one known weakness unresolved: with a single tolerant-F1 radius of 3px, an exact target translated by 3px scores zero distance. The metric was therefore qualified only for consumed-seed replay research, not adopted as a benchmark.

This experiment asks a narrower instrument question:

> Can a structural target metric preserve sparse-image sanity while remaining sensitive to graded displacement, missing structure, excess structure, and density corruption?

No search-policy hypothesis is tested here.

## Population

Reuse exactly the already-consumed #64 target population:

- representations: `recurrence`, `orbit`, `family`, `sheet`, `filament`;
- seeds: `101,103,107`;
- local + global held-out target per route×seed;
- 30 target cases total.

No fresh search seed is consumed.

## Frozen controls

For every target render, evaluate:

```text
exact
shift1
shift2
shift3
shift6
shift12
fade50
blank
validAlpha
validNeighbor
unrelatedValid
deleteRightThird
denseBBox
duplicateShift6
```

The first seven include the #64 sanity family plus graded translations. The additional structural controls are deterministic rendered-image perturbations:

- `deleteRightThird`: erase the rightmost approximately one-third of foreground support;
- `denseBBox`: replace sparse internal structure with a fully inked foreground bounding box at the target's mean foreground intensity;
- `duplicateShift6`: preserve the target and add a second copy displaced 6px.

These are adversarial instrument controls, not valid artworks and not representation mutations.

## Metric under audit: sparse-shape-v1

Frozen #64 candidate:

```text
foreground support = pixel > 20
shape               = 1 - tolerant F1(radius=3px)
mass                 = relative foreground ink-mass error
distance             = 0.8 * shape + 0.2 * mass
```

It is expected to retain the known `shift3 == 0` plateau.

## Predeclared candidate: sparse-shape-v2

Change only the shape term from one tolerance radius to the mean across four spatial scales:

```text
F1_r                 = tolerant foreground F1 at radius r
multi-scale F1       = mean(F1_0, F1_1, F1_2, F1_3)
shape                = 1 - multi-scale F1
mass                 = relative foreground ink-mass error
distance             = 0.8 * shape + 0.2 * mass
```

All foreground thresholds, ink-mass logic, frame averaging, and weights remain frozen from v1.

Rationale: integrating the tolerance curve keeps coarse 3px robustness while preventing the largest radius from creating a flat zero-distance basin for all smaller displacements.

This definition is frozen before results are opened; no radius or weight tuning follows from this run.

## Preregistered sensitivity contract

Across the 30 target cases, `sparse-shape-v2` qualifies for a later fresh-seed search confirmation only if all of the following hold:

```text
30/30 exact distance == 0
30/30 blank distance >= 0.99
30/30 shift3 distance > 0
>=27/30 shift1 <= shift2 <= shift3
>=27/30 shift3 < shift6 < shift12
>=27/30 fade50 < deleteRightThird
30/30 deleteRightThird < blank
>=27/30 denseBBox > validNeighbor
>=27/30 unrelatedValid > validNeighbor
>=27/30 duplicateShift6 > fade50
```

The `27/30` tolerance is declared up front because route-native line geometry can create local aliasing, periodicity, or boundary clipping; qualification requires broad behavior rather than perfect synthetic monotonicity.

The same diagnostics are computed for `sparse-shape-v1` for comparison, but v1 is not retuned post hoc.

## Interpretation

A pass means only that `sparse-shape-v2` has survived this consumed-seed sensitivity suite and is eligible to serve as the objective in a separately preregistered fresh-seed search experiment.

A failure means the benchmark objective remains unresolved and search-operator optimization stays paused.

No result here authorizes artistic promotion, representation pruning, production/default changes, benchmark adoption, or `SKILL.md` changes.
