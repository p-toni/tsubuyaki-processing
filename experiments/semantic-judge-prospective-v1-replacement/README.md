# Semantic artistic judge prospective v1 — replacement

## Status and scope

This is a **replacement first prospective test** for the invalidated `semantic-judge-prospective-v1` run in PR #122.

PR #122 preserved a valid pre-human SHA-256 commitment and 24 later human labels, but the exact committed prediction JSON preimage was not durably retained across the conversation boundary. Its semantic gate was therefore not evaluated. This replacement does not tune on those labels and is not the positive-result second replication from the original protocol.

Only one protocol mechanic changes here: **sealed prediction custody**. The judge question, visible judgment instructions, population size, generation/search contract, pair sampling, scoring, and prospective gate remain unchanged.

## Question

Can a semantic/artistic multimodal judgment made **before any fresh human label exists** predict which of two fresh generated mathematical forms the human reviewer will prefer?

A positive result does **not** grant production artistic authority. It only authorizes a second fresh replication of the same semantic-judge protocol and, if that also succeeds, an implementation study using a reproducible multimodal API judge.

## Fresh population

Authoritative review-only seeds:

- `756003`
- `756019`
- `756037`
- `756053`
- `756071`
- `756089`
- `756107`
- `756127`

Excluded smoke seed: `756999`.

The `756xxx` namespace must be checked absent from repository code and commit history before branch creation/use. No `755xxx` reviewer block from the invalidated run is reused.

Routes remain the frozen evidence-authorized intrinsic-1D class:

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

A/B orientation is randomized from a frozen replacement blind salt and block id.

The reviewer artifact contains only:

- block id;
- side A three temporal frames;
- side B three temporal frames;
- the frozen question.

It excludes route, seed, candidate id, generation index, genome, operator history, structural score, and search diagnostics.

A separate identity key contains those fields and remains unopened until both model and human judgments are fixed.

## Model judgment — prospective commitment

Before the reviewer package is shown to the human reviewer, GPT-5.6 Sol receives only the reviewer-facing images and the question:

> Which candidate is the stronger mathematical form worth keeping or developing further?

Allowed model response per block:

- `A`
- `B`
- `tie`

Judge visible artistic quality only. Consider composition/material coherence, structural distinctiveness, temporal quality, and originality/non-genericness. Prefer `tie` whenever the visible margin is not meaningful. Do not infer route, search stage, mathematical elegance, code complexity, compression, or hidden metadata.

### Exact prediction object

The complete prediction object is exactly one JSON object with keys `R01` through `R24` in lexical order and values only `A`, `B`, or `tie`.

Canonical bytes are:

```python
json.dumps(predictions, indent=2, sort_keys=True) + "\n"
```

No metadata is included inside the prediction object.

### Durable sealed custody

Before human review begins:

1. write the exact canonical prediction bytes as a Git blob in this repository using the Git data API, without adding the blob to the experiment branch tree;
2. compute SHA-256 over those exact bytes;
3. commit a public commitment record containing the SHA-256, Git blob SHA, reviewer artifact id/digest, generation head, model name, and explicit pre-human blinding flags;
4. do not fetch/open the prediction blob again until all 24 human judgments are fixed;
5. do not open the identity-key artifact until all 24 human judgments are fixed.

The Git blob SHA is custody infrastructure, not reviewer material. The human reviewer must not fetch that blob before fixing all ratings, exactly as they must not open the identity-key artifact.

After human ratings are fixed, fetch the blob by its committed Git blob SHA, verify its SHA-256 against the commitment, and only then score it. No prediction may be edited or regenerated after commitment.

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
- Custody/validity failure: do not score reconstructed predictions. Record the run as invalid/inconclusive; it is neither positive nor negative semantic evidence.
