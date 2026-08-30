# Spectral material-control operator v1

## Question

After calibration established that a K=2 bandlimited field can safely deform the five incumbent grammars at amplitude 16, does that deformation provide a **useful search/control direction** relative to the incumbent native numeric mutator under equal challenger exposure?

This is not a standalone-route test and not an artistic preference test.

## Frozen intervention

For every master seed × incumbent route:

1. establish exactly **two hard-valid native starts**;
2. both policies retain those same starts;
3. from each start, generate exactly **six challenger attempts** per policy;
4. native arm: route's existing mutator, one-step from the shared start, `scale=1.0`;
5. spectral arm: unchanged native genome + one independent K=2 field at calibrated amplitude **16**;
6. all attempts count, including hard-invalid challengers;
7. candidate generation finishes before any target score is computed;
8. canonical objective frame is `t=90`; route hard validity remains evaluated on `t=(30,90,150)`.

Therefore each arm has the same two shared bases + 12 challenger attempts. The only intervention is the mutation/control direction.

## Fresh target suite

15 deterministic representation-neutral structural targets, five families × three:

- disconnected-loops
- nested-loops
- concave-loops
- open-networks
- dense-regions

The new target fingerprints must be disjoint from the Stage-B v1, search-v2, and top1-confirmation target suites before any consumed seed can run.

## Seeds

Excluded engineering smoke: `119999`.

Consumed master seeds, frozen before any operator outcome:

`120011, 120017, 120041, 120047, 120049, 120067, 120071, 120079, 120097, 120103, 120121, 120133, 120157, 120163, 120181, 120193, 120199, 120223, 120233, 120247`.

The master seed is the inferential unit. Route/target cells inside a seed are correlated observations, not independent samples.

## Per-cell estimands

For each seed × route × target:

- `baseRecovery`: best of the two shared starts;
- `nativeRecovery`: best of shared starts + valid native challengers;
- `spectralRecovery`: best of shared starts + valid spectral challengers;
- `delta = spectralRecovery - nativeRecovery`;
- `nativeAdded = nativeRecovery - baseRecovery`;
- `spectralAdded = spectralRecovery - baseRecovery`.

Meaningful directional margin: `0.005` recovery.

## Preregistered advancement gate

Decision is `SPECTRAL_MATERIAL_CONTROL_OPERATOR_PROMISING` iff all are true:

1. complete hard-invariant `20 seeds × 5 routes × 15 targets` rectangle;
2. exactly two shared valid starts and exactly 12 challenger attempts per arm/route/seed;
3. mean `delta >= 0.002`;
4. one-sided 95% Student-t lower bound of the 20 master-seed mean deltas is `> 0`;
5. mean delta is `> 0` in **all five routes**;
6. every leave-one-target-family-out mean delta is `> 0`;
7. fraction with `delta > +0.005` is greater than fraction with `delta < -0.005`;
8. spectral challenger hard-valid fraction is `>=0.95` pooled and `>=0.90` in every route;
9. no target family contributes more than `0.50` of total positive delta.

Diagnostics include native validity, route/family effects, base/native/spectral added recovery, meaningful win/loss fractions, and concentration.

## Interpretation

Pass:
- spectral fields have evidence as a generic latent material-control mutation direction;
- freeze amplitude 16 and this operator;
- next layer may test apples-to-apples human value: same incumbent grammar/search context with vs without the spectral control option.

Fail:
- do not tune amplitude, target suite, mutator scale, or challenger count on these 20 consumed seeds;
- generic control claim closes as tested;
- route-specific follow-up requires a newly stated mechanism and fresh seeds, not post-hoc promotion from subgroup diagnostics.
