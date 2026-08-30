# sampling-invariance top-one search — fresh confirmation v1

Status: **preregistered before any confirmation seed execution**.

## Why this experiment exists

`sampling-invariance-search-v2` rejected the preregistered fixed second-basin hedge: `hybrid-top2` was worse than `hybrid-top1` in all five target-family means. However, the explicitly measured `hybrid-top1` comparator produced a new hypothesis-generating signal: after shared breadth discovery, eight calibrated projective-geodesic evaluations around the strongest discovered basin beat eight further independent draws by `+0.006988` mean recovery, with positive mean effect in all five v2 families.

That diagnostic **did not override v2's negative decision**. This experiment is the first fresh test of the newly stated top-one mechanism.

No v2 outcome is used to tune the policy. The following are frozen exactly:

```text
4 valid independent starts
+ 8 independent discovery draws
= 12 shared discovery evaluations

breadth baseline:
+ 8 independent prior draws

candidate top-one policy:
+ 8 adaptive projective-geodesic evaluations
  angles = (0.04, 0.08, 0.16, 0.32) x 2
  parent updates only on strict objective improvement

20 total scored evaluations per policy x target
```

The 12/8 split, field `K=2`, coefficient prior, renderer, validity contract, metric, and geodesic angles are unchanged. There is no second-basin arm and no target-specific schedule.

## Fresh target suite

Freeze 15 new deterministic representation-neutral targets before execution:

- 3 disconnected-loop targets;
- 3 nested-loop targets;
- 3 concave-loop targets;
- 3 open-network targets;
- 3 dense-region controls.

Every v3 fingerprint must be distinct internally and disjoint from **both** the v1 and v2 target suites. The existing target validity contract is unchanged.

Dense regions remain negative controls and cannot be excluded post hoc.

## Fresh master-seed population

Excluded smoke seed:

```text
96999
```

Fresh confirmation seeds — first 24 primes strictly greater than 97000, frozen before execution:

```text
97001, 97003, 97007, 97021, 97039, 97073,
97081, 97103, 97117, 97127, 97151, 97157,
97159, 97169, 97171, 97177, 97187, 97213,
97231, 97241, 97259, 97283, 97301, 97303
```

No seed replacement, early stopping, or addition.

## Primary effect

For every seed x target:

```text
top1_vs_breadth = best_top1_recovery - best_breadth_recovery
```

Meaningful advantage remains strictly greater than `0.005` recovery.

The primary independent replicates are **master seeds**, not the 15 correlated target cells inside each seed.

For each master seed, average `top1_vs_breadth` equally over all 15 targets. The confirmation reducer reports the mean and sample SD of those 24 seed means and a one-sided 95% Student-t lower confidence bound using df=23.

## Hard invariants

Fail closed unless:

1. the new 15-target suite passes the unchanged target contract;
2. every new target fingerprint is distinct from all v1 and v2 target fingerprints;
3. every policy shares the exact same four starts and eight discovery draws;
4. every policy receives exactly 20 scored evaluations per target;
5. invalid discovery/breadth draws consume their slots and are never replaced;
6. the top-one anchor is selected only from the shared 12-evaluation discovery pool;
7. exploitation uses exactly eight events at `(0.04, 0.08, 0.16, 0.32) x 2`;
8. a child becomes parent only on strict recovery improvement;
9. frozen field, metric, v2 search primitive, and spectral operator blobs are exact;
10. all 24 master-seed blocks are present before reduction.

## Confirmation gate

Classify **`SPECTRAL_TOP1_SEARCH_CONFIRMED`** only if all hold:

1. complete hard-invariant rectangle;
2. overall mean `top1_vs_breadth > 0`;
3. one-sided 95% lower confidence bound over the 24 master-seed means is `> 0`;
4. every target-family mean `top1_vs_breadth > 0`;
5. every leave-one-target-family-out mean `top1_vs_breadth > 0`;
6. at least `30%` of all cells have `top1_vs_breadth > 0.005`;
7. top-one exploitation valid yield `>= 0.95`;
8. no target family contributes more than `60%` of aggregate positive `top1_vs_breadth` contribution.

Otherwise classify **`SPECTRAL_TOP1_SEARCH_NOT_CONFIRMED`**.

No route vote, target exclusion, family weighting, or diagnostic can override this gate.

## Advancement discipline

If confirmed:

```text
freeze the exact 12/8 top-one policy
→ objective search navigation is considered confirmed for this representation/benchmark layer
→ next evidence layer may be blinded artistic admission / representation usefulness
```

If not confirmed:

```text
persist the negative result
→ do not tune the 12/8 split or angle schedule on these fresh outcomes
→ close the current spectral-search policy line or define a materially new mechanism
```

Still excluded: higher bandwidths, arithmetic aliasing, state-dependent exponentiation, gradient/SVD fitting, crossover, target-specific mutation schedules, or artistic/model judgment inside this test.
