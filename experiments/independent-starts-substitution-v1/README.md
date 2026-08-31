# Independent starts substitution v1

## Question

#110 established, on a fresh marginal screen, that four independent one-shot route-prior starts add substantially more structural archive and max-dispersion delivery value than four additional local mutations after the supported 20-attempt trajectory.

That result does **not** establish an equal-compute production change. This experiment asks the required causal follow-up:

> At the existing fixed budget of 20 generated candidates, does spending the final four evaluations on independent starts outperform the current final four refinement attempts?

## Frozen arms

Both arms use:

- routes: recurrence / orbit / filament;
- identical deterministic search seed per route/seed;
- exact same hard-valid initial start;
- same deterministic temporal selector;
- same first 16 generated candidates, phenotype-for-phenotype;
- same complete hard-valid archive semantics;
- same target-blind max-dispersion three-item delivery;
- exactly 20 generated candidate evaluations total.

### `baseline20`

Exact current supported runtime:

- explore: 4 attempts (`N,N,S,S`);
- roundA: 4 attempts (`N,N,S,S`);
- refine: 12 attempts (`6 native, 6 spectral`) with the current low/wide scale and parenting rules.

Final generated portfolio: `10 native + 10 spectral`.

### `restartTail20`

Preserve the exact first 16 baseline attempts:

- all 4 explore;
- all 4 roundA;
- refine attempts R1–R8 unchanged.

Then replace baseline refine attempts R9–R12 with four independent one-shot route-prior starts.

Each restart:

- uses its own deterministic RNG stream;
- calls the frozen route-prior seed generator exactly once;
- is evaluated exactly once;
- consumes budget if invalid;
- is not retried;
- is not used as a parent for another restart;
- is eligible for archive/delivery only if hard-valid.

Treatment generated portfolio: `10 native + 6 spectral + 4 independent restarts`.

## Why the final four

The replacement location is fixed for architectural, not outcome-mining, reasons:

1. it maximizes the exact common prefix (16/20 generated candidates);
2. it preserves all exploration, roundA, and the first eight refinement decisions unchanged;
3. it asks a clean production question: **continue the current trajectory for its last four evaluations, or spend those final four evaluations entering four fresh route-prior basins?**

No `746xxx` per-seed outcome is used to choose the cut point.

This is also conservative relative to prior evidence: the current final four are spectral refinements, and #109 found spectral material control carries positive mechanical value. The treatment must beat the actual supported tail, not a weakened local control.

## Fresh population

Excluded smoke: `747999`.

Authoritative seeds:

`747003, 747019, 747037, 747053, 747071, 747089, 747107, 747127, 747149, 747167, 747181, 747199, 747223, 747239, 747257, 747277, 747293, 747311, 747331, 747349`.

Before preregistration, every listed seed and the excluded smoke were absent from repository code, and the `747` namespace was absent from repository commit messages.

Authoritative rectangle: 20 seeds × 3 routes × 15 frozen structural targets = 900 paired cells.

## Evaluation

For each arm, freeze the complete hard-valid generated archive and the max-dispersion three-item delivery shortlist before constructing/scoring structural targets.

For every seed × route × target cell record:

- baseline archive recovery;
- restart-tail archive recovery;
- treatment-minus-baseline archive effect;
- baseline delivery recovery;
- restart-tail delivery recovery;
- treatment-minus-baseline delivery effect.

Structural recovery is experimental evidence only, not artistic authority.

Bootstrap unit: master-seed mean across 45 route-target cells.

Bootstrap: 50,000 draws, deterministic seed `747555001`.

Meaningful-effect bar remains:

`0.003255297955511336`.

## Preregistered mechanical decision

### `INDEPENDENT_STARTS_SUBSTITUTION_PROMISING`

Requires all of:

1. exact 20-seed / 60 route-seed / 900-cell rectangle;
2. excluded smoke proves exact current-runtime baseline replay on all three routes;
3. smoke proves the first 16 treatment candidates are phenotype-identical to baseline;
4. treatment-minus-baseline mean full-archive recovery > `0.003255297955511336`;
5. one-sided 95% seed-bootstrap lower bound for archive effect > 0;
6. every route's archive mean effect > 0;
7. treatment-minus-baseline mean max-dispersion delivery recovery > `0.003255297955511336`;
8. one-sided 95% seed-bootstrap lower bound for delivery effect > 0;
9. every route's delivery mean effect > 0;
10. treatment hard-valid generated rate is no more than 5 percentage points below baseline.

A pass does **not** immediately change production. It authorizes a fresh blinded human artistic comparison of baseline-vs-treatment max-dispersion delivery portfolios.

### `INDEPENDENT_STARTS_SUBSTITUTION_NOT_PROMISING`

Any failure stops this exact equal-budget tail-replacement policy.

Do not tune on consumed `747xxx` evidence:

- the 16/4 split;
- replacement positions R9–R12;
- one-shot restart definition;
- route-prior generator;
- meaningful-effect bar;
- archive/delivery decision gates.
