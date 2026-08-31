# Independent starts marginal v1

## Question

The supported discovery runtime now has a stable search regime:

- one hard-valid route-prior start;
- single-incumbent parenting;
- exactly 20 generated challengers;
- fixed 10 native + 10 spectral portfolio;
- complete hard-valid generated archive preserved;
- target-blind max-dispersion three-item delivery.

The repository still leaves one higher-level search question unresolved:

> Is marginal compute better spent searching deeper around the current trajectory or sampling genuinely independent route-prior starts?

This experiment is a **screening experiment**. It does not change the supported 20-attempt runtime. Both candidate arms first reproduce the exact supported 20-attempt trajectory, then receive four additional candidate evaluations.

A positive result only authorizes a fresh equal-20-budget substitution experiment. It does not authorize production promotion.

## Frozen shared baseline

For each route/seed, construct the exact current runtime trajectory with:

- the same hard-valid start;
- the same deterministic selector;
- the same 4 explore + 4 roundA + 12 refine stages;
- exactly 10 native + 10 spectral generated challengers;
- the same mutation scales and spectral material control;
- the same complete hard-valid generated archive.

Excluded smoke must prove this custom replay is phenotype-identical to `search_engine.run_search` before authoritative seeds open.

## Frozen marginal arms

Each arm adds **exactly four candidate evaluations** after the shared 20-attempt baseline.

### `deepLocal24`

Continue local exploitation from the baseline provisional champion with four sequential low-scale mutations:

`native, spectral, native, spectral`

Rules:

- scale = `0.55` for all four;
- the current local champion is the parent of each next attempt;
- a challenger becomes the next parent only on a clear deterministic-selector win;
- invalid attempts still consume one of the four evaluations;
- no retries.

This asks what four more ordinary local mutations buy after the supported trajectory is complete.

### `independentStarts24`

Add four independent one-shot route-prior draws.

Rules:

- each draw calls the route's frozen prior seed generator from an independent deterministic RNG stream;
- each draw is evaluated exactly once;
- invalid draws still consume one of the four evaluations;
- there is no retry-until-valid behavior;
- no restart is used as a parent for another restart;
- no target, novelty statistic, selector, or human judgment chooses which restart to keep.

This makes compute accounting exact: both marginal arms receive four candidate evaluations, not four successful candidates.

## Archive and delivery construction

The shared baseline archive is frozen before either marginal arm is scored.

For each arm:

- full archive = shared baseline hard-valid generated challengers + hard-valid marginal candidates;
- delivery = the already-supported target-blind max-dispersion three-item shortlist over that arm's full archive.

The original start remains excluded from the delivery archive, exactly as in the promoted delivery rule. Independent restart candidates are eligible because they are newly evaluated marginal candidates.

Only after both marginal archives and both delivery trios are frozen are the existing 15 structural runtime targets constructed and scored.

Structural recovery remains experimental evidence only; it has no artistic authority.

## Fresh population

Excluded smoke: `746999`.

Authoritative master seeds:

`746003, 746019, 746037, 746053, 746071, 746089, 746107, 746127, 746149, 746167, 746181, 746199, 746223, 746239, 746257, 746277, 746293, 746311, 746331, 746349`.

Before preregistration, every listed seed and the excluded smoke were absent from repository code, and the `746` namespace was absent from repository commit messages.

Routes remain:

- recurrence;
- orbit;
- filament.

The authoritative rectangle is 20 seeds × 3 routes × 15 targets = 900 paired cells.

## Outcomes

For every seed × route × target cell record:

- baseline-20 full-archive recovery;
- deep-local-24 full-archive recovery;
- independent-starts-24 full-archive recovery;
- local marginal archive gain over baseline;
- restart marginal archive gain over baseline;
- restart-minus-local archive effect;
- baseline max-dispersion delivery recovery;
- deep-local max-dispersion delivery recovery;
- independent-starts max-dispersion delivery recovery;
- restart-minus-local delivery effect;
- restart-minus-baseline delivery effect.

Bootstrap unit: master-seed mean across the 45 route-target cells.

Bootstrap: 50,000 draws, deterministic seed `746555001`.

Delivery non-inferiority margin remains the already-frozen complexity/evidence margin:

`0.003255297955511336`.

## Preregistered decision

### `INDEPENDENT_STARTS_SCREEN_PROMISING`

Requires all of:

1. exact 20-seed / 60 route-seed / 900-cell authoritative rectangle;
2. excluded smoke proves exact baseline runtime replay on all three routes;
3. mean independent-starts-minus-deep-local full-archive recovery > 0;
4. one-sided 95% seed-bootstrap lower bound for that archive effect > 0;
5. every route's mean independent-starts-minus-deep-local archive effect > 0;
6. mean restart marginal archive gain over baseline > mean local marginal archive gain over baseline;
7. mean independent-starts-minus-deep-local delivery recovery > `-0.003255297955511336`;
8. one-sided 95% seed-bootstrap lower bound for independent-starts-minus-deep-local delivery recovery > `-0.003255297955511336`;
9. every route's independent-starts-minus-deep-local delivery mean > `-0.003255297955511336`;
10. one-sided 95% seed-bootstrap lower bound for independent-starts-minus-baseline delivery recovery > `-0.003255297955511336`;
11. every route's independent-starts-minus-baseline delivery mean > `-0.003255297955511336`.

A pass means independent route-prior starts carry enough marginal target-blind search value to justify **one fresh equal-20-budget substitution experiment**. That future experiment must preregister which four existing attempts are replaced; this consumed evidence cannot choose them.

### `INDEPENDENT_STARTS_SCREEN_NOT_PROMISING`

Any other outcome stops this exact marginal screen.

Do not tune on consumed `746xxx` evidence:

- four-vs-four marginal budget;
- local `N,S,N,S` schedule;
- local scale `0.55`;
- sequential local-parent rule;
- one-shot restart definition;
- route-prior restart generator;
- delivery margin or decision gates.
