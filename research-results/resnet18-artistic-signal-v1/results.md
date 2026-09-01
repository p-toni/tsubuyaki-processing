# ResNet-18 artistic signal retrospective v1

Decision: **RESNET18_ARTISTIC_SIGNAL_NOT_PROMISING**.

## Question

After the simple hand-crafted descriptor scorer in #120 failed cross-experiment and all-equivalent generalization, does one materially richer representation — frozen ImageNet-1K V1 ResNet-18 embeddings — recover a trustworthy artistic preference signal?

The representation, model, corpus, and gates were frozen before the first output. This was the only generic frozen ImageNet backbone authorized for the consumed labels.

## Provenance

- authoritative workflow run: `33455754134`
- frozen scientific head: `3fe8d167e500a11b59d8f3bc6304de238bcfb907`
- result artifact: `9781395941`
- artifact digest: `sha256:aa77365e2fbdae5b934ee3b1256da49b2dd5caa7d340247ad75ec5a4d6bf6bbf`
- README blob: `da8953b3abbfd835ae1eba5f834e299b96a0799d`
- analyzer blob: `68f48230059e6fcea51f5981c46208c1ee29f7f4`
- inherited frozen #120 extractor blob: `2b57c5748c9aed1c522c9b2003623f62406f94cc`
- official checkpoint SHA-256: `f37072fd47e89c5e827621c5baffa7500819f7896bbacec160b1a16c560e07ec`

Representation:

- torchvision `ResNet18_Weights.IMAGENET1K_V1`
- torch `2.10.0+cpu`
- torchvision `0.25.0+cpu`
- 512-d post-average-pool embedding per temporal tile
- side vector = 512-d population mean + 512-d population SD
- block vector = side A minus side B
- zero-intercept dual ridge, alpha `1.0`, train-fold standardization

## Result

Pooled decisive prediction is again above chance:

- correct: **29 / 44**
- accuracy: **65.91%**
- one-sided exact binomial p: **0.02438**

But leave-one-entire-experiment-out performance still fails the preregistered robustness boundary:

| held-out experiment | decisive n | accuracy | mean signed margin |
|---|---:|---:|---:|
| #104 | 12 | 91.67% | +0.6745 |
| #107 | 12 | 75.00% | +0.2275 |
| #112 | 10 | 50.00% | +0.1041 |
| #114 | 10 | **40.00%** | **-0.0526** |

The important improvement over #120 is calibration on the independent all-equivalent surface:

- #120 hand-crafted scorer mean `|prediction|` on #79: **1.2924**
- ResNet-18 mean `|prediction|` on #79: **0.15994**
- frozen requirement: `<= 0.25`

So the learned visual representation no longer hallucinates a large distinction where the human reviewer saw none.

However, it still predicts the #114 artistic boundary in the wrong direction often enough to fail both the per-experiment accuracy and signed-margin gates.

## Gates

Passed:

- finite/complete extraction and model output
- pooled decisive accuracy > 0.60
- exact binomial p <= 0.10
- #79 all-equivalent neutrality <= 0.25

Failed:

- every held-out experiment accuracy >= 0.50 (#114 = 0.40)
- every held-out experiment mean signed margin > 0 (#114 = -0.0526)

## Post-decision diagnostic

The #120 and ResNet scorers are not identical: across the 44 decisive blocks their prediction signs agree on **32 / 44 = 72.7%**, and continuous predictions have pooled Pearson correlation about **0.473**. Yet both yield the exact same experiment-level accuracy sequence: `91.7% / 75% / 50% / 40%`.

That makes the remaining failure less plausibly attributable to a single crude pixel representation. A richer generic appearance embedding fixes neutrality/calibration but does not resolve the intervention-dependent artistic boundary.

## Interpretation

The project now has evidence for three distinct statements:

1. structural/mechanical metrics can improve while human artistic preference does not;
2. simple target-free image descriptors contain some historical preference signal but are badly miscalibrated out of regime;
3. a frozen ImageNet representation improves neutrality substantially, but still cannot generalize across the strongest policy shift in #114.

Therefore generic frozen vision embeddings are **not artistic authority**.

Per preregistration, close this line. Do not try ResNet-50, ViT, CLIP, alternative layers, alternative pooling, a different ridge alpha, or post-hoc calibration on these consumed labels.

The next scorer hypothesis must be materially different: it needs semantic/artistic judgment or explicit morphology/context, and it must earn fresh prospective human evidence before influencing search or delivery.
