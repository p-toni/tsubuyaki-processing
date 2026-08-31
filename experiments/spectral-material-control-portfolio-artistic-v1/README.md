# Spectral material-control portfolio artistic review v1

## Question

Under the already-confirmed equal-compute intrinsic-1D runtime, does `native-spectral-50-50-v1` expose a **stronger generated portfolio of mathematical forms** than `native-only` when the human reviewer sees the variation surface directly rather than the deterministic proxy's single champion?

This is the direct follow-up to `spectral-material-control-artistic-v1`.

That prior review was mechanically valid but non-discriminating: after ratings were frozen, all 12 native and mixed provisional champions were revealed to be the exact shared starting phenotype. The deterministic temporal proxy erased the treatment difference before human review.

## Frozen comparison

Routes:
- recurrence
- orbit
- filament

Fresh review-only seeds:
- `127003`
- `127021`
- `127043`
- `127063`

Excluded smoke seed:
- `127999`

Each route × seed block runs the current runtime twice from the exact same hard-valid start:

- native arm: `native-only`, exactly 20 native challengers;
- mixed arm: `native-spectral-50-50-v1`, exactly 10 native + 10 spectral challengers.

The search trajectory itself remains unchanged. Only the **presentation surface** changes.

## Target-blind portfolio sampling

After each complete 20-attempt trajectory exists:

1. discard the shared start;
2. keep only generated hard-valid challengers, in deterministic generation order;
3. require at least 15 hard-valid challengers;
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
