# Spectral material-control intrinsic-1D portfolio v1

## Question

Under a fixed total challenger budget, does replacing half of native numeric mutations with the confirmed spectral operator improve search/recovery on the incumbent intrinsic-1D route class?

This is the practical integration question after `SPECTRAL_MATERIAL_CONTROL_1D_CONFIRMED`.

## Frozen policies

Every route/master-seed block begins from the same two hard-valid starts and both policies retain those starts.

### Baseline: native-only

- 6 native mutation attempts per start
- 12 total challenger attempts
- existing route mutator at scale 1.0

### Candidate: 50/50 mixed portfolio

- first 3 native attempts per start = **exact common prefix** of baseline native schedule
- 3 independent K=2 spectral attempts per start
- 6 native + 6 spectral = 12 total challenger attempts
- spectral operator unchanged: amplitude 16, Hamiltonian `J grad(F^2)` normalized by frozen RMS rule

All attempts count, including invalid challengers. There is no replacement sampling. Candidate generation is completed before target construction/scoring.

No adaptive scheduler is introduced: adaptation would confound operator value with allocation policy.

## Frozen route class

- recurrence
- orbit
- filament

`family` and `sheet` remain excluded by their pre-existing intrinsic-dimension metadata, not by portfolio outcomes.

## Fresh evidence

- excluded smoke seed: `121999`
- 24 fresh consumed master seeds:

`122011, 122021, 122027, 122029, 122033, 122039, 122041, 122051, 122053, 122069, 122081, 122099, 122117, 122131, 122147, 122149, 122167, 122173, 122201, 122203, 122207, 122209, 122219, 122231`

- 15 fresh structural targets, three per family
- fingerprints must be disjoint from every prior sampling-invariance / spectral search / operator / intrinsic-1D confirmation target suite

## Primary outcome

For each route × target × master seed:

`delta = best(mixed portfolio + shared starts) - best(native-only + shared starts)`

using the unchanged exact sparse-geometry metric.

## PROMISING gate

`SPECTRAL_MATERIAL_CONTROL_1D_PORTFOLIO_PROMISING` iff all hold:

1. complete hard-invariant 24 × 3 × 15 rectangle;
2. mean master-seed delta >= `+0.005`;
3. global one-sided 95% lower bound over master-seed means > 0;
4. every route mean > 0;
5. every route separately has a positive one-sided 95% lower bound over its 24 master-seed means;
6. every leave-one-target-family-out mean > 0;
7. fraction of cells above `+0.005` exceeds fraction below `-0.005`;
8. spectral challenger validity >=95% pooled and >=90% per route;
9. no target family contributes >50% of positive advantage.

Otherwise: `SPECTRAL_MATERIAL_CONTROL_1D_PORTFOLIO_NOT_PROMISING`.

## Authority boundary

This is mechanical fixed-budget integration evidence, not artistic preference evidence. A positive result authorizes testing a mixed operator in the intrinsic-1D search runtime; it does not itself authorize production/artistic promotion.

Consumed seeds cannot be reused to tune the 50/50 split, amplitude, route class, or thresholds.
