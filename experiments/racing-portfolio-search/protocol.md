# Uncertainty-aware racing portfolio search

Frozen before candidate generation.

## Question

Can search outperform fixed H1/H2 allocation by keeping several mathematical basins alive while selector confidence is low, and concentrating compute only after a clear margin appears?

This follows evidence from the breadth/depth and hybrid-portfolio experiments plus independent human calibration.

## Core selector rule

Do **not** force a total order between close candidates or basins.

Every comparison may return one of:

```text
clear win
clear loss
indistinguishable / defer
```

Search-budget reallocation is allowed only on a clear-margin decision. A tie preserves optionality.

## Shared exploration

Reuse the exact 4-start x5 exploration populations from the hybrid-portfolio experiment:

```text
4 basins x 5 challengers = 20 exploration candidates
```

This makes the primary comparison against H1/H2 causal at the allocation stage: the exploration population is identical.

Routes:

1. recurrence;
2. repeated family.

Character count and deployment viability remain excluded from artistic search.

## Racing allocation

Remaining budget: 20 generated challengers.

Experimental schedule:

```text
exploration 20
-> remove only clear-loss basins
-> 4 challengers per surviving basin (round A)
-> compare basin representatives using clear-win/loss/tie
-> remove only newly clear-loss basins
-> spend remaining budget across survivors (round B)
```

The exact number of surviving basins is an outcome, not a fixed policy target.

For this test, if three basins survive the first cut, round A costs 12 and leaves 8. If two survive after round A, each gets four more challengers.

## Mutation behavior

Use the same route-local generic mutation generator as H1/H2 for the primary racing test. Do not introduce a new trust-region grammar in the same causal arm.

Always retain the basin representative / incumbent. Drift candidates may be archived without replacing it.

## Primary comparison

Because exploration is shared, compare:

```text
RACE vs H1 vs H2
```

under the same total 40-candidate budget.

Historical/paired pure D1/B4 results are contextual references, not the primary causal comparison.

## Measurements

Record:

- basin survivors after each racing decision;
- whether a decision was clear win/loss or tie;
- generated and viable counts;
- final representative per surviving basin;
- whether the RACE winner came from a basin H1/H2 would have discarded or underfunded;
- visual/temporal final comparison.

No scalar aesthetic score.

## Human calibration

If the final comparison is close, present a blinded panel with an explicit `tie / too close` option. Do not require a total ranking.

## What would support racing

Strong evidence:

- RACE produces a clearly preferable winner to both H1 and H2 from the same exploration population; or
- RACE preserves a later winning basin that fixed H1/H2 allocation would have starved.

Partial evidence:

- RACE matches the best hybrid with less premature concentration and better niche preservation.

Failure:

- RACE spends budget diffusely and finishes below H1/H2 without preserving a useful alternate basin.

## External replication notes

An independent v0.14.1 filament run reported that its qualitative improvement came from a later structural `phase-relation` coupling after numeric search saturated. Treat this as observational support for delayed structural opportunity, not as causal evidence for this protocol.

The same report found occupancy <2% for a successful filament. `check-visual` is diagnostic-only; occupancy must not become an accept/reject or fitness signal for filament in any autonomous implementation without a route-specific metric.
