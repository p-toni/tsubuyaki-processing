# Compressibility forecast retrospective v1

**A free, mechanical forecast of the readable source predicted every archived
compact outcome outside a narrow band.** In the October studies the agent's
compact posts measured **0.88 ± 0.04** of an idiom-free mechanical minification
of the selected readable source (24 unique posts). Sources forecast at or below
300 X-weighted characters delivered **10/10 on their first attempt**; sources
forecast above 340 delivered **0/5 across 10 attempts**.

This is a retrospective diagnostic on consumed archives, written for the
[learning-progress roadmap review](../../references/learning-progress-review.md).
It changes no recorded grade, selection, or decision, and it is not fresh evidence
of capability. Zone thresholds were chosen after looking at these data and need
prospective validation.

## Question

Under the exact-equivalence compaction used since the discovery pilot (syntax and
algebra only; geometry and style within 1e-7 on every frame), how much of the final
post length is already determined by the readable source before any golf attempt?

## Method

[`forecast-length.mjs`](forecast-length.mjs) (Node built-ins only) removes comments
and whitespace, drops `const`/`let`/`var`, renames declared multi-character
identifiers to unused single letters, and shortens numeric literals. It applies no
golf idioms: no setup folding, aliases, frame counters, loop restructuring, or
algebra. The forecast is the weighted length of that code plus the 21-weight
`//#つぶやきProcessing` suffix.

[`analyze.mjs`](analyze.mjs) pairs every archived compact attempt in
`autonomous-discovery-pilot-v1`, `feedback-value-v1`, and `compact-preflight-v1`
with the readable version it compacts, counts the archived post with the repository
checker, removes logical reuses of identical posts, and writes
[`results.json`](results.json). With `--audit` it also runs the archived
`compact-preflight-v1/audit-source.mjs` on each mechanical post: 720 frames, every
point, readable versus mechanical.

## Results

| Attempt | Unique posts | Actual / forecast |
| --- | ---: | --- |
| First | 15 | 0.893 ± 0.033 (0.826–0.947) |
| Second | 9 | 0.861 ± 0.037 (0.787–0.917) |
| All | 24 | 0.882 ± 0.038 |

| Forecast zone | Unique compacted sources | Delivered | Attempts spent |
| --- | ---: | ---: | ---: |
| green ≤ 300 | 10 | 10 | 10 |
| amber 301–340 | 3 | 2 | 4 |
| red > 340 | 5 | 0 | 10 |

Agent golf removed about 11% beyond mechanical minification on a first attempt and
about 14% on a second. The best ratio in the archive is 0.787. Representation
changes moved forecasts much further: Aperture 432 → 306, Thread 432 → 296, and
Wake 457 → 264.

Observation-led artistic revisions usually raised the forecast. The late arm of
`compact-preflight-v1`, which never saw counts, moved Thread 370 → 432, Relay
284 → 336, and Wake 409 → 457 between v1 and v2. In `feedback-value-v1`, adaptive
revision moved Weave 294 → 346 and Exchange 316 → 385 (v1 → v4); both became the only B-grade
candidates for their briefs and both failed the length boundary. Exchange's two
in-budget batch alternatives (261 and 254) lost its two-body identity and were
graded C. On those briefs, quality and deployability were anti-correlated within
the explored candidates.

The late arm's 1/4 delivery in `compact-preflight-v1` is retrodicted by its frozen
selections: three red sources and one amber.

## Exact-equivalence audit

The mechanical minification is an exact program, not only a length estimate.
Run through the archived `compact-preflight-v1` auditor over frames 1–720, all
18 mechanical posts reproduce every point of their readable source with
geometry and style error exactly 0. The pilot's own horizon was 600 frames;
720 is a superset.

Eight of them already fit within 280. Their sources cover **10 of the 15
logical October deliveries** (8 of 12 unique delivered sources): identical
readable behavior was deliverable with no agent golf. The remaining five
deliveries needed 4–56 characters of agent golf beyond the mechanical form.

| Readable source | Points per frame | Max geometry / style error | Mechanical post | Fits |
| --- | ---: | ---: | ---: | :---: |
| `autonomous-discovery-pilot-v1/B02/v2.js` | 14,000 | 0 / 0 | 234 | yes |
| `autonomous-discovery-pilot-v1/B01/v1.js` | 18,000 | 0 / 0 | 246 | yes |
| `autonomous-discovery-pilot-v1/B03/v2.js` | 1,800 | 0 / 0 | 247 | yes |
| `feedback-value-v1/F06/batch/v4.js` | 2,400 | 0 / 0 | 257 | yes |
| `compact-preflight-v1/P04/early/v4.js` | 40,000 | 0 / 0 | 265 | yes |
| `feedback-value-v1/F03/adaptive/v2.js` | 8,000 | 0 / 0 | 266 | yes |
| `feedback-value-v1/F05/batch/v4.js` | 8,000 | 0 / 0 | 274 | yes |
| `feedback-value-v1/F01/adaptive/v2.js` | 5,000 | 0 / 0 | 275 | yes |
| `feedback-value-v1/F06/adaptive/v3.js` | 1,600 | 0 / 0 | 284 | no |
| `feedback-value-v1/F05/adaptive/v2.js` | 8,000 | 0 / 0 | 287 | no |
| `compact-preflight-v1/P01/early/v3.js` | 30,000 | 0 / 0 | 306 | no |
| `compact-preflight-v1/P02/early/v4.js` | 30,000 | 0 / 0 | 329 | no |
| `compact-preflight-v1/P03/early/v2.js` | 12,000 | 0 / 0 | 336 | no |
| `feedback-value-v1/F02/adaptive/v4.js` | 16,000 | 0 / 0 | 346 | no |
| `feedback-value-v1/F04/adaptive/v4.js` | 9,000 | 0 / 0 | 385 | no |
| `compact-preflight-v1/P01/early/v2.js` | 12,000 | 0 / 0 | 432 | no |
| `compact-preflight-v1/P02/early/v2.js` | 18,000 | 0 / 0 | 432 | no |
| `compact-preflight-v1/P04/early/v2.js` | 10,000 | 0 / 0 | 457 | no |

## Gate power

[`gate-power.mjs`](gate-power.mjs) computes how often the frozen October gates
could pass under assumed true effects, treating briefs as independent pairs.
Extra conjuncts in the real gates only lower these upper bounds.

| Gate | Pass if delivery truly rises 50% → 75% | Pass under a 50%/50% null | Likelihood ratio of a fail |
| --- | ---: | ---: | ---: |
| `feedback-value-v1`: ≥ 4 wins, ≤ 1 loss, 6 briefs | 14% | 3.4% | 0.89 |
| `compact-preflight-v1`: ≥ 2 wins, 0 losses, 4 briefs | 34% | 12.9% | 0.76 |

For comparison, the September human-pair rule (decisive win rate above 0.65 and
one-sided p ≤ 0.10) has 65% power at a true 3:1 preference with 12 decisive
pairs and 88% with 24, with a false-pass rate near 7%.

Briefs also differ in difficulty. The script's seeded simulation draws each
brief's control success from a logistic-normal spread (logit SD 1) and runs
arms independently, as isolated sessions would:

| Design | +25 points for a typical brief | +15 points | No effect |
| --- | ---: | ---: | ---: |
| `feedback-value-v1` rule, 6 briefs × 1 run | 9% | 5% | 1% |
| 24 briefs × 1 run, sign test | 52% | 26% | 5% |
| 12 briefs × 3 runs, paired t-test | 76% | 45% | 11% |
| 24 briefs × 3 runs, paired t-test | 95% | 65% | 11% |

The tests use one-sided α = 0.10.

## Interpretation and limits

Within this regime, compaction is close to a fixed shrink factor; the decisive
length decision is made while authoring the readable representation. That is a
statement about these three studies and this author, not a law. It does not cover
semantic compression that removes or approximates causes, where the
[complete workflow audit](../../research-results/complete-workflow-audit-v2/results.md)
found identity loss rather than length to be binding.

The forecast is a measurement and a gauge, not a creative objective. It does not
reopen the [compression-promotion](../../references/compression-promotion.md) rule
against filtering a creative population by compressibility; whether showing it
while authoring helps or harms is a separate prospective question.

Two thresholds and one ratio fitted on 18 sources can be wrong on fresh briefs,
other authors, or other golf effort. Record forecasts prospectively before relying
on them.

## In-flight protection

`compact-representation-v1` forbids character counts before its readable selection
is frozen. The CLI refuses its sources until that study's `selection.json` exists.
This archive contains no forecast for its candidates.

## Reproduce

From this directory, with Node.js:

```sh
node analyze.mjs
node forecast-length.mjs ../compact-preflight-v1/P04/early/v4.js
```

The exact audit takes several minutes and requires no browser:

```sh
node analyze.mjs --audit
```
