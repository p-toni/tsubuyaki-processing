# Morphology-context artistic judge prospective v1

## Status and motivation

`semantic-judge-prospective-v1-replacement` produced a protocol-valid negative result: the frozen generic pixels-only semantic/artistic judge predicted only 7 / 24 human-decisive choices and failed the preregistered gate. Per that preregistration, this experiment does not tune the failed prompt or reuse the consumed `756xxx` population. It moves to the next research boundary: **explicit morphology/context**.

The hypothesis is not that any morphology metric is intrinsically artistic. The hypothesis is that a multimodal reasoner may judge artistic preference better when visible pixels are accompanied by deterministic, candidate-level evidence about spatial organization and temporal behavior that is difficult to estimate reliably from small review panels alone.

## Question

Can GPT-5.6 Sol, given the same reviewer-facing images **plus a frozen deterministic morphology card for each candidate**, prospectively predict which fresh generated mathematical form the human reviewer prefers?

This is a representation experiment, not prompt fishing. The human task, generation/search process, A/B pair sampling, scoring, and absolute prospective gate remain aligned with the prior semantic-judge experiment. The changed independent variable is the explicit morphology/context representation.

## Fresh population

Authoritative review-only seeds:

- `757003`
- `757019`
- `757037`
- `757053`
- `757071`
- `757089`
- `757107`
- `757127`

Excluded smoke seed: `757999`.

The `757xxx` namespace must be absent from repository code and commit history before branch creation/use. No `755xxx` or `756xxx` reviewer block is reused.

Routes remain the evidence-authorized intrinsic-1D class:

- recurrence
- orbit
- filament

Eight seeds × three routes = **24 authoritative blocks**.

## Frozen generation

Every block uses the same supported mixed intrinsic-1D search as the prior prospective judge:

- exactly one hard-valid route-prior start;
- exactly 20 generated attempts;
- `native-spectral-50-50-v1` = exactly 10 native + 10 spectral attempts;
- current single-incumbent search;
- no sidecar;
- no human/model scorer in generation.

The brief is target-free and fixed to the route. Generation does not use the morphology card.

## Frozen pair sampling

After the complete trajectory exists:

1. exclude the original start;
2. retain hard-valid generated challengers in deterministic generation order;
3. require at least 12 valid generated challengers;
4. select generation-order quantiles `q=0.35` and `q=0.75` using `floor((n-1)*q)`;
5. do not resample identical or near-identical displays.

Each candidate is rendered at raw times `t=30,90,150`.

A/B orientation is randomized from the frozen blind salt and block id. Human reviewer material contains only block id, A/B temporal images, and the frozen question.

## Frozen morphology representation

Morphology is computed **after candidate selection and before model/human judgment**. It is deterministic, label-free, and never used to alter generation or pair sampling.

For descriptor computation, each raw 400×400 grayscale frame is resized to 100×100 with bilinear resampling and binarized at pixel value `>20`. The morphology card contains no route, seed, candidate id, genome, operator, generation index, diagnostic score, or search history.

For each of the three frames, record:

- `occupancy`: lit-pixel fraction;
- `bbox_w`, `bbox_h`: normalized lit bounding-box span;
- `bbox_fill`: lit fraction inside the bounding box;
- `components`: count of 8-connected lit components;
- `largest_component_share`: fraction of lit pixels belonging to the largest component;
- `grid_entropy`: normalized Shannon entropy of lit-pixel mass over a fixed 4×4 spatial grid;
- `anisotropy`: `1 - minor_eigenvalue / major_eigenvalue` of the lit-pixel coordinate covariance, where 0 is isotropic and values near 1 are line-like;
- `edge_fraction`: fraction of lit pixels touching at least one dark/out-of-bounds 4-neighbor;
- `mirror_x_iou`, `mirror_y_iou`: binary-mask IoU against horizontal and vertical reflections;
- `centroid_x`, `centroid_y`: normalized lit centroid coordinates.

Temporal summary across adjacent frame pairs records:

- `mask_iou_mean`: mean binary-mask IoU;
- `occupancy_change_mean`: mean absolute occupancy change;
- `centroid_drift_mean`: mean normalized centroid displacement;
- `bbox_area_change_mean`: mean absolute normalized bounding-box-area change;
- `component_change_mean`: mean absolute component-count change.

All floating values are rounded to six decimals in the model-facing context artifact.

These values are **descriptors, not scores**. No metric direction is declared better or worse.

## Model-facing material

Before human review, GPT-5.6 Sol receives only:

1. the same reviewer-facing A/B image for each block;
2. the corresponding morphology card for A and B;
3. the question:

> Which candidate is the stronger mathematical form worth keeping or developing further?

Allowed response per block:

- `A`
- `B`
- `tie`

Frozen instruction:

> Judge visible artistic quality. Consider composition/material coherence, structural distinctiveness, temporal quality, and originality/non-genericness. The morphology card is descriptive evidence, not a quality score: no metric or direction is automatically preferable. Use it only to make spatial organization and temporal behavior explicit. Prefer `tie` whenever the artistic margin is not meaningful. Do not infer or reward route, search stage, mathematical elegance, code complexity, compression, or hidden metadata.

## Durable prospective custody

The exact 24-prediction object is one JSON object with lexical keys `R01` through `R24`, values only `A`, `B`, or `tie`, and canonical bytes:

```python
json.dumps(predictions, indent=2, sort_keys=True) + "\n"
```

Before human review begins:

1. store those exact bytes as an unreferenced Git blob;
2. compute SHA-256 over the same bytes;
3. commit a public commitment containing SHA-256, Git blob SHA, reviewer artifact id/digest, morphology-context artifact id/digest, generation head, model name, and explicit blinding flags;
4. do not fetch/open the prediction blob again until all 24 human judgments are fixed;
5. do not open the separate identity key until all 24 human judgments are fixed.

After human ratings are fixed, fetch the blob, verify SHA-256, then score. No prediction may be edited or regenerated after commitment.

## Human judgment

The human reviewer sees the reviewer-facing image package only, not morphology cards, model predictions, route/seed identity, or search diagnostics.

Allowed responses:

- `A>B`
- `B>A`
- `equivalent`
- `unreviewable`

## Frozen scoring and gate

Human decisive labels map `A>B → A`, `B>A → B`. A model `tie` on a human-decisive block is incorrect for primary accuracy.

`MORPHOLOGY_CONTEXT_JUDGE_PROSPECTIVE_PROMISING` requires all:

1. at least **18 / 24** human-reviewable blocks;
2. at least **12** human-decisive blocks;
3. primary decisive accuracy **> 0.65**;
4. one-sided exact binomial p-value vs chance `p=0.5` **<= 0.10**;
5. every route with at least three decisive blocks has decisive accuracy **>= 0.50**;
6. model `tie` on no more than **25%** of human-decisive blocks.

The failed pixels-only `756xxx` result is a historical comparator only and is not pooled into this gate.

If any gate fails: `MORPHOLOGY_CONTEXT_JUDGE_PROSPECTIVE_NOT_PROMISING`.

## Boundary

- Positive: authorize one second fresh prospective replication of this exact morphology representation and judgment instruction. Do not integrate it into search yet.
- Negative: do not add more hand-selected descriptors or tune the model prompt on this population. Close model-mediated generic/morphology artistic judging and move to explicit human-preference learning over reproducible morphology/context representations.
- Custody/validity failure: record invalid/inconclusive and replace on a fresh untouched population without reconstructing predictions.
