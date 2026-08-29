# Artistic repertoire evaluation v1

Independent human-evidence layer after repertoire-preserving allocation passed the consumed pilot (#77) and fresh mechanical confirmation (#78).

This experiment does **not** change or re-tune the confirmed allocator. It asks a separate question:

> Under equal search compute, does the confirmed repertoire-preserving parent-selection policy leave a human reviewer with a more useful / interesting portfolio of mathematical forms than ordinary lineage deepening?

## Frozen population

Four review-only master seeds, each checked absent from repository history before branch creation:

`41011, 41017, 41023, 41047`

All five route strata are included for every seed: **20 review blocks**.

These seeds are fresh artistic-review evidence, not another mechanical target-recovery confirmation.

## Frozen generation

For every route x seed block:

- generate the same six hard-valid starts used by the confirmed #77 mechanism;
- run `lineage-depth` and `repertoire-preserving` with the exact #77 `_run_policy` implementation;
- preserve identical basin budgets, mutation event streams, mutation scales, descriptor, and whole-genome mutator;
- do not generate or inspect target-phenotype scores;
- do not use diagnostic score, model judgment, or artistic judgment to select presentation candidates.

### Portfolio endpoint selection

Each policy side presents exactly six matched basin endpoints, one per starting basin.

For a basin, select the child from the latest mutation cycle that is hard-valid. If no generated child in that basin is valid, fall back to the shared hard-valid start. This rule is symmetric and fixed before images are generated.

Each endpoint is shown at raw renderer times `30`, `90`, and `150`. Pixel intensity is not normalized or contrast-stretched.

## Blind presentation

- 20 blocks are shuffled into labels `R01` .. `R20` using a frozen order.
- policy identity is independently randomized to side `A` or `B` per block.
- the review-sheet artifact contains no route, seed, or policy identity.
- the blind key is uploaded as a separate artifact and should remain unopened until all judgments are recorded.

Allowed judgment per block:

- `A>B`
- `B>A`
- `equivalent`
- `unreviewable`

The intended question is portfolio-level: **which side contains the stronger set of forms worth keeping / developing?** This is not a request to identify which policy generated more structural niches.

## Frozen artistic-support gate

After all 20 judgments are recorded and the key is decoded:

`ARTISTIC_SUPPORT` iff all three hold:

1. at least **15 / 20** blocks are reviewable;
2. total candidate-vs-baseline net preference is **> 0**;
3. every leave-one-route-out candidate-vs-baseline net preference is **> 0**.

Scoring after decoding:

- candidate preferred: `+1`
- baseline preferred: `-1`
- equivalent: `0`
- unreviewable: `0` for net preference and excluded from reviewable count

Candidate/baseline win counts, route nets, and an exact one-sided sign-test over decisive blocks are diagnostics only. They cannot override the frozen gate.

## Boundary

A positive result supports the confirmed allocator as artistically useful for this reviewer and this current representation repertoire. It does not authorize route pruning, representation promotion, or a universal aesthetic claim.

A negative result does not invalidate the already-confirmed mechanical target-recovery effect. It means the current mechanical gain has not translated into independent human artistic utility under this presentation contract.
