# Spectral material-control intrinsic-1D confirmation v1

## Question

Does the calibrated K=2 amplitude-16 ambient spectral deformation provide a reproducible control advantage over native numeric mutation specifically for the incumbent **intrinsic-1D manifold class**?

The class is not defined by the operator-v1 outcome. It is frozen by existing representation metadata:

- recurrence: intrinsic dimension 1
- orbit: intrinsic dimension 1
- filament: intrinsic dimension 1
- family: intrinsic dimension 2
- sheet: intrinsic dimension 2

The prior generic operator experiment motivated testing this existing topology distinction, but this confirmation excludes both 2D routes even though `family` had a positive exploratory effect.

## Frozen intervention

No operator tuning from the consumed generic result:

- K = 2
- spectral amplitude = 16
- same Hamiltonian `J grad(F^2)` warp
- same native mutator at scale 1.0
- two shared hard-valid starts per route
- 12 challenger attempts per arm, six per start
- both arms retain their shared bases
- every challenger attempt counts, valid or invalid
- generation happens before target construction/scoring
- exact same sparse-geometry metric

## Fresh evidence

- routes: recurrence / orbit / filament only
- 15 wholly fresh targets, three in each structural family
- target fingerprints must be disjoint from sampling-invariance v1, search-v2, top1-confirmation, and generic operator-v1
- excluded smoke seed: `120999`
- 24 fresh consumed master seeds:

`121001, 121007, 121013, 121019, 121021, 121039, 121061, 121063, 121067, 121081, 121123, 121139, 121151, 121157, 121169, 121171, 121181, 121189, 121229, 121259, 121267, 121271, 121283, 121291`

## Confirmation gate

`SPECTRAL_MATERIAL_CONTROL_1D_CONFIRMED` iff all hold:

1. complete hard-invariant 24 × 3 × 15 rectangle;
2. mean master-seed spectral-vs-native delta >= `+0.005`;
3. overall one-sided 95% lower bound over master-seed means > 0;
4. all three route means > 0;
5. **each route separately** has a one-sided 95% lower bound over its 24 master-seed means > 0;
6. every leave-one-target-family-out mean > 0;
7. fraction of cells above `+0.005` exceeds fraction below `-0.005`;
8. spectral validity >= 95% pooled and >= 90% in every route;
9. no target family supplies >50% of positive advantage.

Otherwise the decision is `SPECTRAL_MATERIAL_CONTROL_1D_NOT_CONFIRMED`.

## Authority boundary

This remains mechanical evidence only. Even confirmation would establish a route-class search/control primitive, not artistic superiority or production admission. Human artistic authority remains separate.

The consumed seeds must not be reused to tune amplitude, challenger budget, topology class, or thresholds.
