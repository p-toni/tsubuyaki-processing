# repertoire-allocation-confirmation-v1

Fresh fixed-sample confirmation of the exact repertoire-preserving allocator that passed the consumed-seed pilot in #77.

## Frozen causal claim

Under identical route and basin budgets, preserving discovered `structural-v1` phenotype-niche histories when selecting the next parent improves unseen target recovery relative to ordinary lineage deepening.

This confirmation does **not** reinterpret the pilot mechanism as increasing terminal niche count. #77 showed effectively unchanged occupied-niche count, rendered uniqueness, and valid yield. The intervention remains exactly the parent-selection rule tested there.

## Frozen mechanism

`run.py` is a thin adapter over `experiments/repertoire-allocation-v1/run.py` from merged main. It changes only the admitted seed population and fresh-evidence metadata.

Unchanged from #77:
- six hard-valid independent starts per route/seed;
- six generic mutation events per basin = 36 generated candidates per arm;
- identical route and basin budgets;
- identical event-keyed RNG labels, streams, and mutation scales;
- identical whole-genome route mutator;
- identical eight-target unseen evaluation portfolio;
- identical `structural-v1` descriptors;
- identical `sparse-geometry-v1` outcome metric;
- lineage-depth parent selection;
- repertoire-preserving least-exposed-niche-history parent selection.

Neither policy sees target outcomes during search.

## Fresh population

24 master seeds, individually checked absent from repository history before branch creation:

`31013, 31019, 31033, 31039, 31051, 31063, 31069, 31079, 31081, 31091, 31121, 31123, 31139, 31147, 31151, 31153, 31159, 31177, 31181, 31183, 31189, 31193, 31219, 31223`

All five routes are fixed strata, producing a complete **120 route×seed block** rectangle. Seed `9001` is excluded smoke only.

No early stopping. No seed replacement. No partial outcome inspection.

## Preregistered inference

For each route×seed block:
- `primaryDelta = repertoire mean normalized target gain - lineage-depth mean normalized target gain`
- `robustnessDelta = repertoire lower-half target gain - lineage-depth lower-half target gain`

For each master seed, effects are equal-route means over the five fixed route strata.

With `n=24`, use Student-t, `df=23`, one-sided 95% critical value `1.713871527747048`.

`CONFIRMED` iff **all** are true:
1. every hard invariant passes across the complete 120-block rectangle;
2. primary complete-master-seed one-sided 95% lower bound > 0;
3. every leave-one-route-out primary mean > 0;
4. robustness complete-master-seed one-sided 95% lower bound > 0.

Otherwise `NOT_CONFIRMED`.

Route signs, medians, win counts, mechanism diagnostics, or artistic judgment cannot override the decision.

## Interpretation boundary

Mechanical capability evidence only. A positive result would support integrating repertoire-preserving branching as a search primitive; it would not grant artistic authority, justify route pruning/promotion, add a representation, or by itself change `SKILL.md`.
