# Selector frontier allocation v1 — result

Decision: `FRONTIER_ALLOCATION_NOT_PROMISING`.

Authoritative run: `33390005283`  
Artifact: `9757507512`  
Digest: `sha256:576298dd19de805fe58d927bacffeb209066f5c805060e75940fd5d97a7df9b9`

## Frozen result

- 16 fresh master seeds.
- 3 routes × 15 frozen structural targets = 720 paired cells.
- Mean seed-level frontier-minus-incumbent recovery: `-0.006188385570172992`.
- One-sided 95% bootstrap lower bound: `-0.009972041446243887`.
- Route mean effects:
  - recurrence: `-0.01430698879341908`
  - orbit: `+0.0012637391632608459`
  - filament: `-0.005521907080360743`
- Baseline valid-challenger rate: `0.9864583333333333`.
- Frontier valid-challenger rate: `0.9791666666666666`.
- Validity delta: `-0.007291666666666696`.
- Median final non-start frontier count: `3.0`.
- Baseline provisional champion remained the shared start in `95.83%` of route/seed runs.

## Gate

Passed:
- validity degradation <= 5 percentage points;
- median final non-start frontier >= 2.

Failed:
- positive mean seed effect;
- positive one-sided 95% lower bound;
- positive effect on every route.

## Interpretation

The experiment separates two ideas that should no longer be conflated:

1. **Archive/delivery plurality is useful.** #104 showed unanimous blinded human preference for the mixed native+spectral portfolio when the portfolio was actually exposed.
2. **Plural search parenting is not useful under this fixed budget.** #105 successfully preserved multiple non-start alternatives, but distributing later search attempts across them reduced structural recovery versus incumbent-only search.

Therefore the exact cap-4, round-robin bounded-frontier parenting policy is stopped. Do not tune its cap or allocation rule on these consumed seeds.

The next architectural direction is delivery-only: keep the efficient incumbent search trajectory, retain its complete hard-valid archive, and test whether a target-blind shortlist policy can expose useful structural variation without altering search allocation.
