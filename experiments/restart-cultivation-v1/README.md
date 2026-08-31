# Restart cultivation v1

## Question

Fresh mechanical evidence shows that independent route-prior starts discover useful new structural basins, but two artistic boundaries have not justified automatic substitution:

- #112 rejected replacing four late spectral refinements with one-shot starts;
- #114 corrected that confound by preserving all ten spectral evaluations and replacing native refinements instead, but its stricter Stage-A artistic gate did not pass.

The remaining material integration loophole is **maturity**:

> Are one-shot restart basins structurally useful but underdeveloped when they reach the delivery surface?

This experiment tests cultivation directly. It does not tune #113/#114 positions, ratios, seeds, or review gates on consumed evidence.

## Frozen three-arm comparison

Each route/seed runs three exact **20-candidate** arms from the same route-prior start.

### `baseline20`

Exact supported runtime:

- 10 native
- 10 spectral
- no restarts
- full hard-valid archive
- target-blind three-item max-dispersion delivery

### `oneShot20`

Exact #113 spectral-preserving treatment, replayed on fresh seeds:

- same first 10 baseline candidates phenotype-for-phenotype
- native R3-R6 replaced by four independent one-shot route-prior starts
- all six refine-stage spectral attempts retained
- 6 native + 10 spectral + 4 restart
- restarts never become parents

This arm is a fresh replication control.

### `cultivated20`

Same first 10 candidates and same six spectral-tail candidates as `oneShot20`.

The four replacement slots become:

1. independent restart basin 1;
2. one native small-step child of restart basin 1;
3. independent restart basin 2;
4. one native small-step child of restart basin 2.

Frozen cultivation mutation:

- operator: native
- scale: `0.55`, the existing small refine scale
- one child exactly; no retries
- child RNG is isolated from the main trajectory
- both restart parent and child remain in the archive
- no target/proxy/human score chooses which basin is cultivated

Portfolio accounting:

- 8 native total (6 main-trajectory native + 2 cultivation children)
- 10 spectral
- 2 restart
- exactly 20 generated candidates

The first two restart parents must be phenotype-identical between `oneShot20` and `cultivated20`. All six spectral-tail candidates must also be phenotype-identical between those arms. Therefore the only causal difference is **two additional independent basins versus one local maturation step on each of two shared basins**.

## Fresh population

Excluded smoke: `753999`.

Authoritative seeds:

`753003, 753019, 753037, 753053, 753071, 753089, 753107, 753127, 753149, 753167, 753181, 753199, 753223, 753239, 753257, 753277, 753293, 753311, 753331, 753349`

Routes:

- recurrence
- orbit
- filament

Frozen benchmark:

- 15 structural targets
- canonical `t=90`
- `sparse-geometry-v1-exact-fast-grayscale`

Before preregistration, the `753` namespace was absent from repository code and commit messages.

## Hard invariants

Before any result can count:

1. exact route set;
2. exact 20-candidate budget in all three arms;
3. baseline is exactly 10 native + 10 spectral;
4. one-shot is exactly 6 native + 10 spectral + 4 restart;
5. cultivated is exactly 8 native + 10 spectral + 2 restart, with exactly 2 cultivation children;
6. shared start is exact across all arms;
7. first ten generated candidates are exact across all arms;
8. first two restart parents are exact between one-shot and cultivated;
9. all six spectral-tail candidates are exact between one-shot and cultivated;
10. baseline runtime replay is phenotype-exact in excluded smoke;
11. complete 20-seed × 3-route × 15-target rectangle before reduction.

## Frozen decision

Use paired master-seed bootstrap with 50,000 draws.

Meaningful structural margin remains frozen at:

`0.003255297955511336`

`RESTART_CULTIVATION_PROMISING` requires all of:

### One-shot replication

For both archive and delivery:

- oneShot-minus-baseline mean > meaningful margin;
- one-sided 95% bootstrap lower bound > 0;
- every route mean > 0.

### Cultivated treatment

For both archive and delivery:

- cultivated-minus-baseline mean > meaningful margin;
- one-sided 95% bootstrap lower bound > 0;
- every route mean > 0.

### Maturity tradeoff

For both archive and delivery:

- one-sided 95% lower bound of cultivated-minus-oneShot > `-meaningful_margin`;
- every route cultivated-minus-oneShot mean > `-meaningful_margin`.

### Validity

- cultivated valid rate >= baseline valid rate - 0.01;
- restart-parent valid rate >= 0.95;
- cultivation-child valid rate >= 0.95.

If every gate passes, authorize one fresh blinded artistic comparison of `baseline20` versus `cultivated20` under the stricter #114 review contract.

Otherwise:

`RESTART_CULTIVATION_NOT_PROMISING`

and stop automatic restart substitution. Do not tune restart count, cultivation count, mutation scale, positions, seeds, or margins on consumed `753xxx` evidence. The evidence-conservative fallback is a baseline-preserving optional restart sidecar rather than another automatic replacement.

Mechanical structural evidence is not artistic authority.
