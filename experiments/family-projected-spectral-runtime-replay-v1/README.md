# Family projected-spectral runtime replay v1

## Question

Does the mechanically supported family projected-spectral 50/50 portfolio survive integration into the **actual adaptive runtime** under a fixed 20-challenger budget, while preserving every existing default and authority boundary?

This is the deployment/mechanical gate authorized by #133. It grants no artistic authority.

## Runtime intervention under test

A new explicit opt-in portfolio mode:

```text
native-family-projected-spectral-50-50-v1
```

Runtime rules:

- omitted `mutation_portfolio` and `native-only` remain legacy native behavior;
- existing `native-spectral-50-50-v1` remains restricted to the supported intrinsic-1D class;
- the new mode is eligible **only for `family`**;
- `sheet` and every non-family route remain native under the new mode;
- each family local batch preserves a native prefix and spends the remaining half on `projected-spectral`; odd batches conservatively keep the extra attempt native;
- projected spectral uses frozen K=2 / amplitude 16 Hamiltonian control;
- the control state is serialized in the incumbent family genome under `_material_control` with a distinct control type;
- the generic warp is projected around each warped family anchor so that sibling anchor→terminal length equals the native sibling length;
- native mutation of a controlled candidate preserves its selected material field;
- no checker threshold, selector authority, route set, sidecar authority, or artistic authority changes.

## Runtime search shape

The performance replay runs `family` alone with one hard-valid start basin. Both arms use the real `DeterministicTemporalSelector` and adaptive incumbent-challenge loop:

```text
explore: 4
round A: 4
refine: 12
total generated challengers: 20
```

Baseline:

```text
native-only = 20 native
```

Candidate:

```text
family projected mode = 10 native + 10 projected-spectral
```

Both arms reset from the same search seed and must begin from the exact same start phenotype. Search and selector are target-blind. The full hard-valid archives are fixed before structural targets are constructed or scored.

## Excluded smoke

Smoke seed:

```text
764999
```

Before authoritative seeds may open, smoke must prove all:

1. omitted portfolio and explicit `native-only` are trajectory-identical on `family` after normalizing the brief key;
2. two independent family projected-mode runs are trajectory-identical;
3. native and projected arms begin from the same family start phenotype;
4. both family arms generate exactly 20 challengers;
5. projected mode generates exactly 10 native + 10 `projected-spectral` challengers;
6. every projected challenger serializes the exact family projected control type, K=2, amplitude 16, and 25 coefficients;
7. `sheet` under the family projected mode generates only native challengers;
8. existing recurrence under `native-spectral-50-50-v1` still generates exactly 10 native + 10 generic spectral challengers;
9. targeted material-control/runtime equivalence tests pass;
10. the fresh target suite is hard-valid, distinct, and image-fingerprint-disjoint from every prior sampling/material-control target suite through #133.

Smoke is excluded from inference.

## Fresh authoritative population

Exactly 20 master seeds:

```text
764003 764019 764037 764053 764071
764089 764107 764127 764149 764167
764181 764199 764223 764239 764257
764277 764293 764311 764331 764349
```

The exact `764` namespace must be absent from the frozen pre-experiment base before execution. No authoritative seed may run until smoke passes.

Consumed seeds may not be reused to tune the runtime schedule, 50/50 split, K, amplitude, family projection, validity threshold, target suite, metric, or decision gate.

## Fresh target suite

15 new static targets, three each from:

- disconnected loops;
- nested loops;
- concave loops;
- open networks;
- dense regions.

They are a fresh runtime-replay suite, not the #131 or #133 targets. Image-fingerprint disjointness is verified before smoke.

## Outcome

For each master seed × target:

```text
nativeRecovery = best t=90 recovery among all hard-valid native-runtime candidates
mixedRecovery  = best t=90 recovery among all hard-valid family projected-runtime candidates
delta          = mixedRecovery - nativeRecovery
```

There are `20 × 15 = 300` paired cells. Master seed is the inference unit.

## Preregistered decision gate

`FAMILY_PROJECTED_SPECTRAL_RUNTIME_PROMISING` requires **all**:

1. complete hard-invariant 300-cell rectangle;
2. exact 20-vs-20 challenger budgets on every seed;
3. exact 20-native baseline and 10-native/10-projected candidate allocation on every seed;
4. same starting phenotype between arms on every seed;
5. mean mixed-minus-native recovery >= `+0.005`;
6. one-sided 95% master-seed bootstrap lower bound > 0;
7. every target-family mean > 0;
8. every leave-one-target-family-out mean > 0;
9. meaningful wins (`delta > +0.005`) exceed meaningful losses (`delta < -0.005`);
10. projected-spectral hard-valid rate >=95%;
11. projected sibling-scale-law failures = 0;
12. mixed total challenger validity is no more than 5 percentage points below native baseline;
13. no target family contributes >50% of total positive advantage.

### Pass

A pass supports merging the new **opt-in family projected-spectral runtime mode** as mechanically validated. It remains default off, family-only, and artistically unpromoted. Visual review remains paused.

### Fail

A fail means the operator/portfolio effect did not survive actual adaptive runtime integration. Do not tune the consumed `764xxx` population. Archive the result without promoting the runtime mode and return to the broader roadmap.
