# Basin trust-region confirmation v1

## Purpose

Fresh fixed-sample mechanical confirmation of the exact basin-preserving exploitation mechanism selected by consumed-seed pilot #72.

No route partition, target construction, broad-discovery policy, exploitation budget, parent schedule, mutation scale, metric, or RNG scheme is reselected here.

## Frozen mechanism

Source implementation:

- `experiments/basin-trust-region-v1/policy.py`
- `experiments/basin-trust-region-v1/run.py`

The five route partitions are frozen exactly as preregistered in #72.

Both policies share:

- three common starts;
- four ordinary broad mutations per basin;
- qualified `sparse-geometry-v1` basin selection;
- the same selected representative;
- 20 exploitation candidates;
- first 14 events from current champion at scale `0.55`;
- last six events from original selected representative at scale `1.20`;
- event-keyed RNG using the existing `derived_seed(...)` primitive.

Only exploitation key eligibility differs:

- `generic`: current whole-genome numeric mutator;
- `trust-region`: route-local deformation/detail/phase/time/material subspace only.

Target regimes remain:

- `same-basin`: six accepted local-only mutations at scale `0.65`;
- `identity-jump`: one accepted identity-only mutation at scale `1.20`, then five accepted local-only mutations at scale `0.65`.

## Fresh population

32 master seeds, deliberately separated from all previously consumed 1000-series search evidence:

```text
2003, 2011, 2017, 2027,
2029, 2039, 2053, 2063,
2069, 2081, 2083, 2087,
2089, 2099, 2111, 2113,
2129, 2131, 2137, 2141,
2143, 2153, 2161, 2179,
2203, 2207, 2213, 2221,
2237, 2239, 2243, 2251
```

All five routes remain fixed strata:

```text
recurrence, orbit, family, sheet, filament
```

Smoke seed `9001` is infrastructure-only and excluded from analysis.

No early stopping or seed replacement is allowed.

## Sample-size planning

Consumed pilot #72:

```text
same-basin mean master-seed effect  +0.046880
same-basin master-seed SD            0.104491
interaction mean                     +0.134092
interaction SD                        0.173223
```

Using the same-basin pilot mean/SD, one-sided alpha `0.05` and ~80% planning power gives approximately 31 complete master seeds under a normal approximation. Fix `n=32` before opening any fresh result.

The same-basin effect is the sample-size driver; the pilot interaction is larger relative to its variance.

## Estimands

For route `r`, seed `s`, target regime `g`:

```text
delta[r,s,g]
  = trust-region normalized improvement
  - generic normalized improvement
```

Complete-master-seed effects:

```text
same_seed[s] = mean_r delta[r,s,same-basin]
jump_seed[s] = mean_r delta[r,s,identity-jump]
interaction_seed[s] = same_seed[s] - jump_seed[s]
```

Routes are strata, not stochastic votes.

## Hard execution invariants

Confirmation fails mechanically if any pilot invariant fails:

- exact/disjoint partition coverage;
- both policies share the same discovered representative;
- both policies generate exactly 20 exploitation candidates;
- trust-region champion changes zero frozen sampling/identity keys;
- same-basin target changes zero frozen keys from ancestor;
- identity-jump target changes at least one identity key;
- every expected 5-route × 32-seed block exists exactly once.

## Preregistered confirmation rule

Use Student-t uncertainty across the **32 complete master-seed effects**, never 160 route×seed pseudo-replicates.

With `df=31`, one-sided 95% critical value is frozen as:

```text
t_0.95,31 = 1.695519
```

Call the mechanism `CONFIRMED` only if all three are true:

1. same-basin one-sided 95% lower bound > `0`;
2. every leave-one-route-out same-basin mean > `0`;
3. interaction one-sided 95% lower bound > `0`.

Otherwise call it `NOT_CONFIRMED`.

No route-specific sign, strict-win count, median, identity-jump sign, or artistic judgment overrides this rule.

## Interpretation boundary

A `CONFIRMED` result establishes a mechanical search principle:

> after a basin is found, exploitation benefits from preserving basin-defining dimensions.

It does **not** establish that the hand-authored route partitions are final production abstractions or that target-recovery improvement equals artistic improvement.

If confirmed, the next implementation step is to make basin identity explicit search state and then test preservation/allocation across multiple phenotype-structural niches (repertoire / quality-diversity architecture). Artistic promotion remains independently/human validated.

If not confirmed, do not tune nearby local mutation settings on fresh data. Return to the higher-level archive/repertoire hypothesis using the completed evidence.

## Boundary

Fresh mechanical confirmation only. No automatic production/default change, representation promotion/pruning, artistic authority, or `SKILL.md` change.