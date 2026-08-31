# Delivery dispersion artistic review v1

## Question

#106 established on fresh mechanical evidence that, from the same completed mixed native+spectral archive, a target-blind max-dispersion three-item shortlist improves best-of-three structural recovery over the generation-order quantile shortlist used in #104.

Does that delivery-only improvement survive an independent blinded human artistic-usefulness test?

## Frozen treatment boundary

Each route/seed runs exactly one current incumbent-only mixed search trajectory:

- routes: recurrence / orbit / filament;
- `native-spectral-50-50-v1`;
- one hard-valid start;
- exactly 20 generated challengers: 10 native + 10 spectral;
- current deterministic temporal selector drives search unchanged;
- no plural-parent allocation;
- only hard-valid generated challengers enter delivery selection;
- the start is excluded from both delivery shortlists.

Both A/B sides are selected from the **same completed archive**.

### Generation-quantile side

Hard-valid generated challengers remain in deterministic generation order. Require at least 12, then choose `floor((n-1)*q)` at `q = 0.20, 0.50, 0.80`.

### Max-dispersion side

Use the exact #106 frozen rule:

- raw candidate frames at `t=30,90,150`;
- grayscale nearest-neighbor resize to `100×100` only for selection distance;
- candidate distance = mean absolute pixel difference across all three frames, normalized to `[0,1]`;
- enumerate every 3-candidate combination;
- lexicographically maximize `(minimum pairwise distance, mean pairwise distance)`;
- exact ties keep the first generation-order combination.

No structural target, diagnostic score, proxy vote, semantic score, novelty label, human judgment, model judge, or prior artistic rating enters either shortlist.

## Fresh population

Excluded smoke: `743999`.

Authoritative review seeds:

`743003, 743021, 743043, 743063`.

These values were absent from repository code and commit messages before preregistration.

## Reviewer surface

For every route × seed block:

- one side is generation-quantile and the other is max-dispersion;
- A/B assignment is deterministic from a sealed salt and block id;
- each side shows three selected candidates;
- each candidate is shown at raw temporal frames `t=30,90,150`;
- route, seed, policy identity, candidate ids, genomes, operator history, structural scores, and the A/B key are hidden.

The reviewer answers only:

> Which side contains the stronger portfolio of mathematical forms worth keeping or developing further?

Allowed judgments: `A>B`, `B>A`, `equivalent`, `unreviewable`.

## Integrity gates

The reviewer package cannot open unless:

1. exact mixed 10-native / 10-spectral budget holds in every block;
2. every archive has at least 12 hard-valid generated challengers;
3. each shortlist contains three distinct rendered phenotypes;
4. max-dispersion minimum pairwise distance is never below the generation-quantile shortlist;
5. the two displayed three-item portfolios are not pixel-identical in every block;
6. reviewer artifact and policy identity key are uploaded separately.

## Preregistered artistic decision

After all 12 judgments are fixed and only then the key is opened.

`ARTISTIC_SUPPORT` for max-dispersion delivery requires all of:

1. at least 9/12 blocks reviewable;
2. total max-dispersion-vs-quantile net preference > 0 (`win=+1`, `loss=-1`, equivalent/unreviewable=0`);
3. every leave-one-route-out net preference > 0.

A pass authorizes max-dispersion as the default **three-item delivery shortlist** for this supported mixed-search surface. It does not change search parenting, mutation allocation, artistic authority, or the preservation contract.

A failure stops this exact raw-pixel max-dispersion delivery promotion. Do not tune the distance resolution, shortlist size, frames, or objective on these consumed human judgments.
