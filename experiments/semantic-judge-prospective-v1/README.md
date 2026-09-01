# Semantic artistic judge prospective v1

## Question

Can a semantic/artistic multimodal judgment made **before any fresh human label exists** predict which of two fresh generated mathematical forms the human reviewer will prefer?

This is the first prospective scorer test after #120 and #121 closed hand-crafted and generic frozen-ImageNet scorer lines.

The scorer under test is not trained, calibrated, or tuned on this population. Model predictions must be fixed and hash-committed before the reviewer-facing package is shown to the human reviewer.

A positive result does **not** grant production artistic authority. It only authorizes a second fresh replication of the same semantic-judge protocol and, if that also succeeds, an implementation study using a reproducible multimodal API judge.

## Fresh population

Authoritative review-only seeds:

- `755003`
- `755019`
- `755037`
- `755053`
- `755071`
- `755089`
- `755107`
- `755127`

Excluded smoke seed: `755999`.

The `755xxx` namespace was checked absent from repository code and commit history before branch creation.

Routes are the frozen evidence-authorized intrinsic-1D class:

- recurrence
- orbit
- filament

Eight seeds × three routes = **24 authoritative blocks**.

## Frozen generation

Every block runs the currently supported mixed intrinsic-1D search:

- exactly one hard-valid route-prior start;
- exact supported 20 generated attempts;
- `native-spectral-50-50-v1` = exactly 10 native + 10 spectral attempts;
- current single-incumbent search;
- no sidecar;
- no human/model scorer in generation.

The brief is target-free and fixed to the route. Search artifacts are temporary; only the two selected reviewer candidates and sealed provenance key are retained.

## Frozen pair sampling

After the complete trajectory exists:

1. exclude the original start;
2. retain hard-valid generated challengers in deterministic generation order;
3. require at least 12 valid generated challengers;
4. choose two candidates at generation-order quantiles `q=0.35` and `q=0.75` using `floor((n-1)*q)`;
5. do **not** resample if the two rendered phenotypes are identical or near-identical.

Identical or weakly distinguishable pairs are legitimate evidence and may be judged `equivalent` / `tie`.

Each candidate is shown at raw renderer times `t=30,90,150`.

## Blinding

A/B orientation is randomized from a frozen blind salt and block id.

The reviewer artifact contains only:

- block id;
- side A three temporal frames;
- side B three temporal frames;
- the frozen question.

It excludes route, seed, candidate id, generation index, genome, operator history, structural score, and search diagnostics.

A separate identity key contains those fields and remains sealed until both model and human judgments are fixed.

## Model judgment — prospective commitment

Before the reviewer package is shown to the human reviewer, GPT-5.6 Sol receives only the reviewer-facing images and the question:

> Which candidate is the stronger mathematical form worth keeping or developing further?

Allowed model response per block:

- `A`
- `B`
- `tie`

Judge visible artistic quality only. Consider composition/material coherence, structural distinctiveness, temporal quality, and originality/non-genericness. Prefer `tie` whenever the visible margin is not meaningful. Do not infer route, search stage, mathematical elegance, code complexity, compression, or hidden metadata.

The complete 24-block model prediction JSON is saved outside the repository and its exact SHA-256 is committed publicly **before human review begins**. No model prediction may be changed after that commitment.

## Human judgment

After the model commitment exists, the human reviewer receives the same 24 reviewer-facing blocks.

Allowed human response:

- `A>B`
- `B>A`
- `equivalent`
- `unreviewable`

No model prediction or identity key is shown before all 24 human judgments are fixed.

## Frozen scoring

Human decisive labels:

- `A>B` → A
- `B>A` → B

For decisive human blocks:

- model predicts the human winner → correct;
- model predicts the other side → incorrect;
- model predicts `tie` → incorrect for the primary accuracy test.

`equivalent` blocks are excluded from decisive accuracy and used only for tie-calibration diagnostics.

`unreviewable` blocks are excluded from all preference calculations.

## Preregistered prospective gate

`SEMANTIC_JUDGE_PROSPECTIVE_PROMISING` requires all:

1. at least **18 / 24** human-reviewable blocks;
2. at least **12** human-decisive blocks;
3. primary decisive accuracy **> 0.65**;
4. one-sided exact binomial p-value vs chance `p=0.5` **<= 0.10**;
5. every route with at least three decisive blocks has decisive accuracy **>= 0.50**;
6. the model uses `tie` on no more than **25%** of human-decisive blocks.

Tie calibration on human-equivalent blocks is diagnostic only because the number of equivalents is not controlled in advance. If at least four equivalents occur, report the fraction predicted `tie` prominently but do not alter the frozen primary gate.

If any gate fails: `SEMANTIC_JUDGE_PROSPECTIVE_NOT_PROMISING`.

## Boundary

- Positive: authorize one second fresh prospective replication of this exact semantic judging protocol. Do not influence search or delivery yet.
- Negative: do not tune the prompt, thresholds, or this population. Close this exact semantic-judge protocol and move to explicit morphology/context rather than prompt fishing.
