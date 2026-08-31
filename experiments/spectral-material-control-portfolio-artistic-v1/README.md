# Spectral material-control portfolio artistic review v1

## Question

Under the already-confirmed equal-compute intrinsic-1D runtime, does `native-spectral-50-50-v1` expose a **stronger generated portfolio of mathematical forms** than `native-only` when the human reviewer sees the variation surface directly rather than the deterministic proxy's single champion?

This is the direct follow-up to `spectral-material-control-artistic-v1`.

That prior review was mechanically valid but non-discriminating: after ratings were frozen, all 12 native and mixed provisional champions were revealed to be the exact shared starting phenotype. The deterministic temporal proxy erased the treatment difference before human review.

## Pre-review feasibility correction

The first #104 workflow attempt (`33387966417`) failed closed **before any reviewer-facing artifact or identity key was uploaded**. One mixed trajectory produced 14 hard-valid challengers, below the originally frozen presentation-feasibility floor of 15. No portfolio image, A/B identity, or artistic judgment from that population was inspected.

That first population is therefore treated as feasibility-only and is not reused for artistic evidence.

The corrected protocol freezes:

- a new four-seed review population;
- a new excluded smoke seed;
- a minimum of **12** hard-valid generated challengers before three portfolio samples may be shown.

The value 12 is not fitted to the observed count of 14. It is a conservative presentation floor: it requires four times as many viable generated candidates as the three displayed samples while allowing route-level hard-validity variation. The sampling rule, equal budgets, routes, operator, renderer, temporal frames, human question, reducer, and artistic-support gate are otherwise unchanged.

## Frozen comparison

Routes:
- recurrence
- orbit
- filament

Fresh review-only seeds:
- `128003`
- `128021`
- `128041`
- `128053`

Excluded smoke seed:
- `128999`

Each route × seed block runs the current runtime twice from the exact same hard-valid start:

- native arm: `native-only`, exactly 20 native challengers;
- mixed arm: `native-spectral-50-50-v1`, exactly 10 native + 10 spectral challengers.

The search trajectory itself remains unchanged. Only the **presentation surface** changes.

## Target-blind portfolio sampling

After each complete 20-attempt trajectory exists:

1. discard the shared start;
2. keep only generated hard-valid challengers, in deterministic generation order;
3. require at least **12** hard-valid challengers;
4. select exactly three candidates at frozen valid-sequence quantiles `0.20 / 0.50 / 0.80` using `floor((n-1)*q)`;
5. show each selected candidate at raw `t=30,90,150`.

No target, structural metric, semantic score, proxy vote, model judge, human judgment, novelty score, or post-hoc oracle selects the displayed candidates.

The presentation-integrity gate fails closed if native and mixed selected portfolios are display-identical.

## Blind review

There are 12 anonymous A/B blocks.

Each side contains three generated candidates × three temporal frames.

Allowed judgment:
- `A>B`
- `B>A`
- `equivalent`
- `unreviewable`

Question:

> Which side contains the stronger portfolio of mathematical forms worth keeping or developing further?

A/B identity, route, seed, candidate ids, genomes, and operator history remain in a separately uploaded sealed key until all judgments are fixed.

## Preregistered support gate

`ARTISTIC_SUPPORT` iff:

1. at least 9/12 blocks are reviewable;
2. total mixed-vs-native net preference > 0;
3. every leave-one-route-out net preference > 0.

The existing frozen reducer from `spectral-material-control-artistic-v1` is reused unchanged.

## Boundary

Positive evidence supports artistic usefulness of the confirmed mixed operator portfolio for this reviewer and route class. It does not automatically make mixed search a production default or validate the deterministic temporal proxy.

Negative evidence leaves the spectral operator mechanically confirmed but artistically unsupported at this target-blind portfolio surface. Do not tune the operator or sampling rule on consumed review outcomes.
