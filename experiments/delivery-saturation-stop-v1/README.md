# Delivery saturation stop v1

## Question

The supported search/delivery architecture now has two independently confirmed facts:

1. mixed native+spectral incumbent-only search should preserve its full hard-valid archive;
2. a target-blind max-dispersion three-item shortlist is mechanically better than generation quantiles (#106) and survives blinded artistic review (#107).

Can the already-promoted max-dispersion delivery surface also provide a **target-blind stopping signal** that safely saves search compute?

The specific hypothesis is that a search trajectory has become locally saturated when a full shortlist's worth of new hard-valid challengers arrives without changing the max-dispersion trio.

## Frozen search

Every route/seed runs the existing search unchanged to the full budget so the counterfactual suffix remains observable:

- routes: recurrence / orbit / filament;
- one hard-valid start per route;
- incumbent-only search parenting;
- `native-spectral-50-50-v1`;
- exactly 20 generated challengers: 10 native + 10 spectral;
- current selector, stages, mutation scales, and RNG behavior unchanged.

The experiment does **not** actually stop generation. It derives a hypothetical stop point from prefixes of the completed target-blind trajectory, freezes that point, and only afterward evaluates what the omitted suffix would have contributed.

## Frozen saturation signal

Only hard-valid generated challengers can update the signal.

After every hard-valid addition, once the prefix contains at least 12 hard-valid generated challengers:

1. compute the exact #106 max-dispersion three-item shortlist on the current prefix;
2. compare its ordered candidate-id tuple with the previous hard-valid checkpoint;
3. if the trio is unchanged, increment a stability counter; if it changes, reset the counter to zero;
4. declare saturation when **three consecutive additional hard-valid challengers** leave the trio unchanged.

Three is fixed because it equals the promoted delivery shortlist size: an entire shortlist's worth of new viable material has arrived without displacing any member of the current coverage-optimal trio.

There is no learned distance threshold, structural target, semantic target, aesthetic score, diagnostic score, human label, or model judge in the stopping rule.

If the condition never fires, the hypothetical stop remains the full 20 attempts.

## Fresh population

Excluded smoke: `744999`.

Authoritative master seeds:

`744003, 744019, 744037, 744053, 744071, 744089, 744107, 744127, 744149, 744167, 744181, 744199, 744223, 744239, 744257, 744277, 744293, 744311, 744331, 744349`.

The `744xxx` namespace was absent from repository code and commit messages before preregistration.

## Counterfactual outcomes

For every route/seed, first freeze:

- full 20-attempt trajectory;
- hypothetical stop attempt;
- stopped hard-valid prefix archive;
- max-dispersion trio from the stopped prefix;
- max-dispersion trio from the full archive.

Only after all three route stop points are frozen, reveal the already-frozen 15-target runtime structural benchmark.

For each route × target cell record:

- stopped-delivery recovery: best recovery among the stopped prefix's max-dispersion trio;
- full-delivery recovery: best recovery among the full archive's max-dispersion trio;
- stopped-archive recovery: best recovery among every hard-valid generated challenger available at the stop point;
- full-archive recovery: best recovery among every hard-valid generated challenger after 20 attempts;
- delivery loss = full delivery minus stopped delivery;
- archive loss = full archive minus stopped archive.

Structural recovery remains experimental evidence, not artistic authority.

## Non-inferiority margin

#106's fresh mean max-dispersion-vs-generation-quantile gain was `+0.006510595911022672`.

The frozen non-inferiority margin is exactly half of that confirmed gain:

`0.003255297955511336`.

A compute-saving rule is not considered useful if its uncertainty permits it to spend more than half of the already-confirmed delivery advantage.

## Preregistered decision

`SATURATION_STOP_PROMISING` iff all are true:

1. at least 50% of the 60 route-seed trajectories stop before attempt 20;
2. median attempts saved across all 60 route-seed trajectories is at least 3 (15% of the 20-attempt budget);
3. mean seed-level delivery loss is below the non-inferiority margin;
4. one-sided 95% bootstrap upper bound for seed-level delivery loss is below the margin;
5. mean seed-level full-archive loss is below the margin;
6. one-sided 95% bootstrap upper bound for seed-level full-archive loss is below the margin;
7. every route's mean delivery loss is below the margin;
8. every route's mean full-archive loss is below the margin.

Hard integrity requirements:

- exact 20-seed authoritative population and 900 route-target cells;
- exact 20 generated attempts and 10 native / 10 spectral attempts per route/seed;
- at least 12 hard-valid generated challengers per route/seed;
- stop point derived before targets are constructed/scored;
- stopped and full max-dispersion shortlists each contain three distinct phenotypes.

A positive result authorizes implementation of this exact stopping rule behind an experimental runtime flag plus one fresh equality/non-inferiority replay. It does not immediately replace the 20-attempt production search and does not bypass human artistic authority.

A negative result stops this exact stable-three-shortlist rule. Do not tune minimum prefix length, stability count, distance representation, or non-inferiority margin on the consumed `744xxx` seeds.
