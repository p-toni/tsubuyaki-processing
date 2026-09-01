# Artistic signal retrospective v1

## Question

Do simple target-free visual/temporal descriptors contain a reproducible signal for the human artistic judgments already collected by the project?

This is a **retrospective measurement audit**, not fresh artistic evidence. It may only authorize a fresh prospective scorer test. It cannot authorize an automatic aesthetic scorer or change production search/delivery.

## Immutable source reviews

Decisive/generalization corpus:

- #104 `spectral-material-control-portfolio-artistic-v1`: 12 blocks
- #107 `delivery-dispersion-artistic-v1`: 12 blocks
- #112 `independent-starts-artistic-v1`: 12 blocks
- #114 `spectral-preserve-restart-artistic-v1`: 12 blocks

These contribute 48 blocks total: 44 decisive and 4 equivalent.

External neutrality diagnostic only:

- #79 `artistic-repertoire-evaluation-v1`: 20 blocks, all judged `equivalent` after the original frozen package was finally reviewed.

#79 is **never used to fit a model** because its six-candidate presentation differs from the three-candidate layouts in the decisive corpus. It is used only to test whether a scorer trained on decisive experiments remains near-neutral on a human-all-equivalent surface.

Reviewer images are immutable workflow artifacts. No blind identity, route, seed, treatment identity, structural score, target score, genome, or policy label is available to the scorer.

## Image extraction

For #104/#107/#112/#114, each block is the common 446×1038 vertical A/B layout. The extractor:

1. converts to grayscale;
2. detects exactly six contiguous dark render strips where >80% of row pixels are `<50`, each strip at least 100 px high;
3. assigns first three strips to A, last three to B;
4. splits each strip into three equal temporal tiles;
5. crops 5% from every tile edge;
6. resizes to 96×96 with nearest-neighbor sampling.

For #79 only, the extractor:

1. detects the central A/B divider as the brightest vertical column inside the central 20% of the image;
2. starts the render body at 4% image height;
3. splits the remaining body into six equal candidate bands per side;
4. splits each side into three equal temporal columns;
5. crops 5% horizontally, 15% from the top, and 10% from the bottom of each tile to exclude row/time labels;
6. resizes to 96×96 with nearest-neighbor sampling.

Foreground is frozen as grayscale `>20`.

## Frozen side descriptors

Each side is represented by exactly nine interpretable descriptors:

1. `ink_mean`: mean foreground fraction across tiles;
2. `ink_sd`: SD of foreground fraction across tiles;
3. `bbox_span_mean`: mean max normalized foreground bbox width/height;
4. `center_offset_mean`: mean normalized foreground-centroid distance from tile center;
5. `temporal_change_mean`: mean normalized pixel MAD between adjacent temporal frames of the same candidate;
6. `temporal_change_sd`: SD of those adjacent-frame MADs;
7. `candidate_dispersion_mean`: mean candidate-pair distance, where pair distance is mean normalized pixel MAD across the three matched times;
8. `candidate_dispersion_min`: minimum candidate-pair distance;
9. `candidate_dispersion_sd`: SD of candidate-pair distances.

The block feature vector is `features(A) - features(B)`. This makes the representation antisymmetric to A/B swapping.

## Frozen model

Human target:

- `A>B` = `+1`
- `B>A` = `-1`
- `equivalent` = `0`

Model: zero-intercept ridge regression with `alpha=1.0`.

For every leave-one-experiment-out fold:

1. fit feature mean/SD on the other three decisive experiments only;
2. standardize training and held-out features with those training statistics;
3. fit `w = (XᵀX + I)⁻¹Xᵀy`;
4. predict held-out continuous score `Xw`.

No hyperparameter search, feature selection, feature weighting, route stratification, treatment labels, or post-hoc threshold tuning is allowed.

## Primary evaluation

Only decisive held-out blocks count for accuracy.

A prediction is correct iff `sign(prediction) == judgment`.

`SIMPLE_ARTISTIC_SIGNAL_PROMISING` requires all of:

1. extraction/model invariants pass and all predictions are finite;
2. pooled leave-one-experiment-out decisive accuracy is **> 0.60**;
3. one-sided exact binomial p-value versus chance `p=0.5` is **<= 0.10**;
4. every decisive-containing held-out experiment has accuracy **>= 0.50**;
5. every decisive-containing held-out experiment has positive mean signed margin `mean(y * prediction) > 0`;
6. after fitting once on all four three-candidate experiments, the external #79 all-equivalent surface has mean absolute prediction **<= 0.25**.

If any gate fails: `SIMPLE_ARTISTIC_SIGNAL_NOT_PROMISING`.

## Boundary

Positive authorizes only a **fresh prospective artistic scorer test** on new review blocks with the exact frozen feature/model pipeline.

Negative closes this exact hand-crafted pixel/temporal descriptor family. Do not tune feature weights, thresholds, ridge alpha, or extraction parameters on these consumed human judgments. A future scorer would need a materially richer representation (for example learned vision/multimodal judgment or explicit morphology semantics) and fresh evidence.
