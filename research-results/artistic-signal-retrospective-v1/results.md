# Artistic signal retrospective v1

Decision: **SIMPLE_ARTISTIC_SIGNAL_NOT_PROMISING**.

## Question

Can simple target-free visual/temporal descriptors predict the project's already-collected blinded human artistic judgments across experiments?

This was a retrospective measurement audit only. The analyzer and gates were frozen before the first result.

## Corpus

Model/generalization corpus:

- #104 spectral portfolio review — 12 blocks
- #107 max-dispersion delivery review — 12 blocks
- #112 independent-start restart-tail review — 12 blocks
- #114 spectral-preserving restart review — 12 blocks

Total: 48 blocks, 44 decisive and 4 equivalent.

External neutrality diagnostic:

- #79 repertoire-allocation review — 20 blocks, all judged equivalent

#79 was never used for model fitting because its six-candidate presentation differs from the three-candidate layouts in the model corpus.

## Frozen representation/model

Nine side-level descriptors from reviewer pixels only:

- ink mean / SD
- bbox span mean
- center offset mean
- temporal change mean / SD
- candidate dispersion mean / minimum / SD

Block vector = `features(A) - features(B)`.

Model = zero-intercept ridge regression, `alpha=1.0`, standardized using training-fold statistics only. Evaluation = leave one entire artistic experiment out.

Analyzer git blob: `2b57c5748c9aed1c522c9b2003623f62406f94cc`.

## Result

Pooled decisive prediction looked promising in isolation:

- correct: **29 / 44**
- accuracy: **65.91%**
- one-sided exact binomial p vs 0.5: **0.02438**

But the cross-experiment pattern failed the preregistered robustness boundary:

| held-out experiment | decisive n | accuracy | mean signed margin |
|---|---:|---:|---:|
| #104 | 12 | 91.67% | +1.2623 |
| #107 | 12 | 75.00% | +0.2458 |
| #112 | 10 | 50.00% | +0.2034 |
| #114 | 10 | **40.00%** | +0.0455 |

The strongest failure is the independent all-equivalent diagnostic. After fitting on all four three-candidate experiments, the scorer produced:

- #79 mean absolute prediction: **1.2924**
- frozen neutrality requirement: **<= 0.25**

So the scorer was highly confident about differences the human reviewer considered equivalent in every block.

## Gates

Passed:

- finite extraction/model output
- pooled accuracy > 0.60
- exact p <= 0.10
- every held-out experiment mean signed margin > 0

Failed:

- every held-out experiment accuracy >= 0.50 (#114 = 0.40)
- external all-equivalent mean absolute prediction <= 0.25 (#79 = 1.2924)

## Interpretation

The hand-crafted descriptors contain a real historical preference signal, especially around the large #104/#107 portfolio-diversity effects. But they do not generalize as a trustworthy aesthetic scorer. They can become confidently wrong when the artistic distinction changes or disappears.

Therefore:

> simple pixel amount / composition / temporal-change / portfolio-dispersion features are useful diagnostics, not artistic authority.

Do not tune these feature weights, extraction thresholds, ridge alpha, or neutrality threshold on the consumed reviews. A future automatic scorer must use a materially richer representation that predates the next fresh labels, then earn prospective artistic evidence.
