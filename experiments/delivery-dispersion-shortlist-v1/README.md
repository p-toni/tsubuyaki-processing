# Delivery dispersion shortlist v1

## Question

#104 established that the mixed native+spectral **generated portfolio** has strong blinded artistic value when the portfolio is actually exposed. #105 then showed that distributing a fixed search budget across plural parents reduces search recovery.

Can we keep the efficient incumbent-only search trajectory unchanged and improve the **delivery surface** by selecting a target-blind three-item shortlist that covers more of the generated phenotype space?

## Frozen treatment boundary

Every route/seed runs exactly one incumbent-search trajectory using the already-supported runtime:

- routes: recurrence / orbit / filament;
- `native-spectral-50-50-v1`;
- 20 generated challengers: 10 native + 10 spectral;
- current deterministic temporal selector remains the search driver;
- search allocation, parenting, mutation scales, start generation, and total compute are unchanged;
- only hard-valid generated challengers are eligible for delivery;
- the shared start is excluded from both delivery shortlists.

The two shortlist policies operate on the **same completed archive**.

### Baseline: generation quantiles

Reuse the target-blind presentation rule from #104:

1. retain hard-valid generated challengers in deterministic generation order;
2. require at least 12;
3. choose `floor((n-1)*q)` for `q = 0.20, 0.50, 0.80`.

### Candidate: max-dispersion shortlist

For every eligible challenger, render raw `t=30,90,150` frames and resize each grayscale frame to `100×100` only for shortlist-distance computation.

Candidate-to-candidate phenotype distance is mean absolute pixel difference across the three resized frames, normalized to `[0,1]`.

Enumerate every three-candidate combination. Choose the combination that lexicographically maximizes:

1. minimum of its three pairwise phenotype distances;
2. mean of its three pairwise phenotype distances.

Combinations are enumerated in generation-order index order; exact score ties keep the first combination. No target, diagnostic score, proxy vote, semantic score, novelty label, human judgment, model judge, or prior artistic rating enters shortlist selection.

The max-dispersion shortlist must contain three distinct phenotype hashes. The implementation also verifies that its minimum pairwise distance is never below the quantile shortlist's minimum pairwise distance, since the quantile shortlist is itself one feasible three-candidate combination.

## Fresh population

Excluded smoke seed: `742999`.

Authoritative seeds:

`742003, 742021, 742039, 742057, 742073, 742091, 742109, 742127, 742147, 742163, 742181, 742199, 742217, 742237, 742253, 742271`.

All listed seeds were absent from repository code and commit messages before preregistration.

## Outcome construction

Only after both target-blind shortlists are frozen, score them against the already-frozen 15-target runtime structural benchmark using `sparse-geometry-v1-exact-fast-grayscale` at canonical `t=90`.

For each route × target cell:

- quantile recovery = best recovery among its three quantile candidates;
- dispersion recovery = best recovery among its three max-dispersion candidates;
- full-archive recovery = best recovery among every hard-valid generated challenger, diagnostic only;
- paired effect = dispersion minus quantile recovery.

There are 45 cells per master seed. The seed is the inferential unit.

Also record target-blind shortlist dispersion and full-archive regret. Structural recovery is experimental evidence, not artistic authority.

## Preregistered decision

`DISPERSION_SHORTLIST_PROMISING` iff all are true:

1. mean seed-level dispersion-minus-quantile recovery > 0;
2. one-sided 95% bootstrap lower bound over seed-level effects > 0;
3. every route's mean paired recovery effect > 0.

Hard integrity requirements:

- exact 16-seed population and 720 paired cells;
- exact mixed 10-native / 10-spectral challenger budget for every route/seed;
- at least 12 hard-valid generated challengers per route/seed;
- exactly three distinct selected phenotypes per shortlist;
- max-dispersion minimum pairwise distance >= quantile minimum pairwise distance for every route/seed.

A positive result authorizes one fresh blinded artistic comparison of **dispersion shortlist vs generation-quantile shortlist**. It does not authorize a production default by itself.

A negative result stops this exact raw-pixel max-dispersion delivery policy. Do not tune its distance resolution, shortlist size, or objective on the consumed seeds.
