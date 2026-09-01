# ResNet-18 artistic signal retrospective v1

## Question

Does a materially richer **frozen, pretrained visual representation** contain a reproducible signal for the project's already-collected blinded human artistic judgments where the hand-crafted pixel/temporal descriptors in #120 failed?

This remains a **retrospective measurement audit**. It consumes no new human judgments and cannot authorize an automatic aesthetic scorer or any production policy. A positive result may only authorize a fresh prospective artistic-scorer test.

## One-candidate rule

This experiment tests exactly one generic frozen vision representation:

- `torchvision.models.ResNet18_Weights.IMAGENET1K_V1`
- torchvision `0.25.0`
- torch `2.10.0`
- official torchvision weight URL `https://download.pytorch.org/models/resnet18-f37072fd.pth`
- torchvision's built-in `check_hash=True` weight verification remains in force; the full downloaded checkpoint SHA-256 is recorded in the result.

No alternative backbone, checkpoint, layer, pooling scheme, embedding normalization, ridge alpha, feature selection, or threshold may be tried after outcome inspection. If this experiment fails, the **generic frozen ImageNet embedding line closes**. A future scorer must use a materially different authority source, such as a semantic multimodal judge or an explicit morphology representation, with fresh evidence.

## Immutable human-review corpus

The same corpus and labels as #120 are reused exactly:

Model/generalization corpus:

- #104 spectral portfolio review — reviewer artifact `9756540975` — 12 blocks
- #107 max-dispersion delivery review — reviewer artifact `9759391278` — 12 blocks
- #112 independent-start restart-tail review — reviewer artifact `9766571236` — 12 blocks
- #114 spectral-preserving restart review — reviewer artifact `9772194591` — 12 blocks

Total: **48 blocks, 44 decisive and 4 equivalent**.

External neutrality diagnostic only:

- #79 repertoire-allocation review — reviewer artifact `9719175928` — 20 blocks, all judged `equivalent`.

#79 is never used for fitting because its six-candidate presentation differs from the three-candidate layouts in the decisive corpus.

## Frozen image extraction

The tile extraction is **not redesigned** for this experiment. The analyzer imports the exact committed extraction functions and immutable rating rectangle from:

`experiments/artistic-signal-retrospective-v1/analyze.py`

For #104/#107/#112/#114, use that module's `_vertical_tiles(...)`.

For #79, use that module's `_horizontal79_tiles(...)`.

This preserves the same reviewer-pixel segmentation already frozen before #120's first result.

## Frozen ResNet representation

For every extracted 96×96 grayscale temporal tile:

1. convert to PIL grayscale then RGB;
2. apply the exact transform returned by `ResNet18_Weights.IMAGENET1K_V1.transforms()`;
3. run frozen `resnet18(weights=IMAGENET1K_V1)` in `eval()` mode;
4. replace `fc` with `Identity` and retain the 512-dimensional post-average-pool embedding.

No fine-tuning occurs.

For every portfolio side:

- compute the per-dimension **mean** embedding across all candidate×time tiles (512 dims);
- compute the population **standard deviation** embedding across all candidate×time tiles (512 dims);
- concatenate mean and SD to form a 1024-dimensional side representation.

The block vector is:

`representation(A) - representation(B)`

This makes the input antisymmetric to A/B swapping.

## Frozen model

Human target:

- `A>B` = `+1`
- `B>A` = `-1`
- `equivalent` = `0`

Model: zero-intercept ridge regression with `alpha = 1.0`.

For each leave-one-experiment-out fold:

1. fit feature mean/SD on the other three experiments only;
2. standardize train and held-out vectors using those training statistics, replacing zero SD by 1;
3. fit ridge in the exact dual form `alpha = 1.0`;
4. predict the held-out experiment once.

No hyperparameter search or calibration is allowed.

## Decision gates

Use **exactly the same gates as #120**.

`RESNET18_ARTISTIC_SIGNAL_PROMISING` requires all:

1. all extraction/model outputs finite and source-image rectangles complete;
2. pooled leave-one-experiment-out decisive accuracy **> 0.60**;
3. one-sided exact binomial p-value against chance `p=0.5` **<= 0.10**;
4. every decisive-containing held-out experiment accuracy **>= 0.50**;
5. every decisive-containing held-out experiment mean signed margin `mean(y * prediction) > 0`;
6. after fitting once on all four three-candidate experiments, #79's all-equivalent surface has mean absolute prediction **<= 0.25**.

If any gate fails: `RESNET18_ARTISTIC_SIGNAL_NOT_PROMISING`.

## Boundary

A positive retrospective result authorizes only a **fresh prospective blinded artistic scorer test** using this exact frozen representation/model pipeline.

A negative result closes generic frozen ImageNet embedding work. Do not try ResNet-50, ViT, CLIP, another layer, another alpha, post-hoc calibration, or alternative pooling on these consumed labels.
