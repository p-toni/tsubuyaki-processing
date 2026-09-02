# Restart sidecar budget v1

## Question

The baseline-preserving restart sidecar is intentionally exploratory-only and currently defaults to four independent route-prior attempts per evidence-authorized route when enabled. Prior equal-budget work repeatedly showed that independent starts broaden structural coverage, while automatic substitution into the baseline search failed the artistic boundary.

With visual review paused, the useful mechanically answerable question is:

> How much isolated sidecar budget is needed before structural coverage shows clear diminishing returns?

This experiment does **not** make an artistic-quality claim and cannot promote sidecar candidates into baseline search or delivery.

## Frozen arms

For every master-seed × route cell:

- run the exact supported baseline search first: 20 generated attempts, 10 native + 10 spectral;
- then generate eight isolated production-sidecar route-prior attempts using the existing `restart-sidecar-v1` RNG namespace;
- evaluate nested prefixes `k = 1, 2, 4, 8` attempts per route.

Because sidecar index RNG is isolated, the smaller arms must be phenotype-exact prefixes of the `k=8` arm.

## Fresh population

Excluded smoke: `759999`.

Authoritative master seeds:

`759003, 759019, 759037, 759053, 759071, 759089, 759107, 759127, 759149, 759167, 759181, 759199, 759223, 759239, 759257, 759277, 759293, 759311, 759331, 759349`

Routes:

- recurrence
- orbit
- filament

The `759xxx` namespace must be absent from repository history before preregistration.

## Mechanical surfaces

All surfaces are descriptive coverage instruments only.

### 1. Hard validity

Measure sidecar hard-valid yield at all nested budgets. Invalid attempts consume budget; no retries.

### 2. Full-union structural recovery

For each budget, union the baseline hard-valid generated archive with the valid sidecar prefix. After every archive is frozen, score maximum recovery against the existing 15-target sparse-geometry benchmark at canonical `t=90`.

### 3. Max-dispersion delivery coverage

From each baseline/union archive, choose the target-blind three-item raw-pixel max-dispersion shortlist using the already artistically supported delivery rule. Score structural recovery of that shortlist against the same targets only after selection is frozen.

### 4. Dispersion

Record the max-dispersion shortlist minimum and mean pairwise raw-pixel temporal distance across `t=30,90,150`.

### 5. Distinct phenotype yield

Record distinct temporal phenotype hashes added by each sidecar prefix.

## Hard invariants

Before evidence counts:

1. baseline runs before sidecar generation;
2. baseline budget is exactly 20 = 10 native + 10 spectral for every route/seed;
3. sidecar budgets are exactly `1,2,4,8` per route;
4. sidecar prefixes are phenotype-exact nested prefixes of `k=8`;
5. sidecar candidates cannot enter baseline state, parent baseline search, or replace baseline delivery;
6. sidecar uses the production `restart-sidecar-v1` RNG namespace and evidence-authorized route class;
7. target construction/scoring occurs only after all target-blind archives and dispersion shortlists are frozen;
8. invalid sidecar draws consume budget and are not retried.

## Frozen decision

The primary decision is a **compute/coverage efficiency** decision, not an artistic one.

First require the maximum budget (`k=8`) to demonstrate a real mechanical sidecar effect:

- sidecar validity >= 95%;
- mean full-union structural-recovery gain over baseline > 0 with one-sided 95% master-seed bootstrap lower bound > 0;
- mean dispersion-shortlist structural-recovery gain over baseline > 0 with one-sided 95% lower bound > 0;
- mean minimum-pairwise-dispersion gain over baseline > 0;
- full-union and delivery recovery gains are non-negative on every route.

If that prerequisite fails: `SIDECAR_BUDGET_EFFECT_NOT_DEMONSTRATED`; keep the existing optional default unchanged and close budget optimization.

If it passes, define a budget `k` as **coverage-sufficient** when, relative to `k=8`, it captures at least 90% of the pooled gain on all three primary coverage surfaces:

1. full-union structural recovery;
2. dispersion-shortlist structural recovery;
3. minimum pairwise dispersion.

It must also have non-negative full-union and delivery recovery gain on every route.

Decision:

- choose the smallest coverage-sufficient `k` among `1,2,4,8`;
- if `k=4`, record `SIDECAR_DEFAULT_FOUR_MECHANICALLY_EFFICIENT` and keep the implementation default;
- if `k=1` or `k=2`, record `SIDECAR_SMALLER_BUDGET_SUFFICIENT` and authorize changing the optional sidecar default downward to that budget;
- if only `k=8` is sufficient, record `SIDECAR_EIGHT_REQUIRED_FOR_COVERAGE` and authorize changing the optional sidecar default upward to eight;
- if ratios are undefined because `k=8` gains are effectively zero, fall back to `SIDECAR_BUDGET_EFFECT_NOT_DEMONSTRATED`.

No result changes the baseline search policy or grants automatic artistic authority to sidecar candidates.
