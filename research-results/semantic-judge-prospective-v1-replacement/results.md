# Semantic artistic judge prospective v1 — replacement result

Decision: **SEMANTIC_JUDGE_PROSPECTIVE_NOT_PROMISING**.

## Validity and custody

- Authoritative generation head: `50366ad66f369149ee6030cec0b4eba16eb66ba7`.
- Reviewer artifact: `9819976860`, digest `sha256:7860355a6e2b1d81d6b81e895a7fd804db4ec5cd57588fbfe3eae8f566024ac2`.
- Prediction commitment was committed before human review at `a14ecbaa00e504179da6c88a034fa0a6d6f1d358`.
- Committed prediction SHA-256: `745154276e44c621e52421e73141992731d963a6869b10d8f5137142d8e6561d`.
- Sealed prediction Git blob: `c5d838df235f24796700a79e33fcf15ed21c1bc9`.
- Human ratings were fixed and committed at `9aca7e5255b954c98f0aac13f32fd56080e2e06d` before the prediction blob or identity key was opened.
- After human ratings were fixed, the prediction blob was fetched and its exact bytes re-hashed. The SHA-256 matched the public commitment exactly.
- The separately sealed identity-key artifact `9819977422` was opened only after all 24 human ratings were fixed.

The replacement prospective test is therefore protocol-valid.

## Frozen gate result

Human review:

- reviewable: **24 / 24**;
- decisive: **24 / 24**;
- human `B>A`: **20 / 24**;
- human `A>B`: **4 / 24**;
- equivalent: **0**;
- unreviewable: **0**.

Model predictions:

- `A`: **15 / 24**;
- `B`: **7 / 24**;
- `tie`: **2 / 24**.

Primary decisive accuracy:

- correct: **7 / 24**;
- accuracy: **0.2917**;
- one-sided exact binomial p-value vs `p=0.5`: **0.988672**.

Per-route decisive accuracy:

- recurrence: **4 / 8 = 0.500**;
- orbit: **1 / 8 = 0.125**;
- filament: **2 / 8 = 0.250**.

Tie rate on human-decisive blocks:

- **2 / 24 = 0.0833**.

Preregistered gates:

1. at least 18/24 reviewable: **PASS** (`24/24`);
2. at least 12 decisive: **PASS** (`24/24`);
3. decisive accuracy > 0.65: **FAIL** (`0.2917`);
4. one-sided exact binomial p <= 0.10: **FAIL** (`0.988672`);
5. every route with >=3 decisive blocks accuracy >=0.50: **FAIL** (orbit `0.125`, filament `0.250`);
6. tie on <=25% of decisive blocks: **PASS** (`0.0833`).

Therefore the frozen decision is **SEMANTIC_JUDGE_PROSPECTIVE_NOT_PROMISING**.

## Diagnostic observations

The human labels happened to be strongly side-skewed: side B won `20/24` blocks. Because A/B orientation was frozen independently from candidate identity, this is noteworthy but does not alter the preregistered result. The preference was not simply a later-generation preference: the human winner came from q=0.75 in `14/24` blocks and q=0.35 in `10/24` blocks.

The model did not exhibit the same side pattern: it predicted A 15 times, B 7 times, and tie twice. Thus the failure is not explained by the model mechanically following the lower/B panel.

## Interpretation

This is a clean negative result for the exact generic semantic/artistic multimodal prompt tested here. The model, using reviewer pixels and the frozen high-level artistic rubric alone, did not predict the human reviewer's pairwise choices above chance and failed badly on orbit and filament.

Do not tune this prompt, thresholds, tie policy, model outputs, or the consumed `756xxx` population. Do not run the preregistered positive-result second replication.

## Research boundary

Per preregistration, close this exact semantic-judge protocol and move to **explicit morphology/context** rather than prompt fishing.

The next research question should test whether exposing reproducible, candidate-level morphological and temporal evidence — instead of asking a generic visual-semantic judge to infer it from pixels — produces a judgment representation that tracks human artistic choices well enough to justify future autonomous search integration.
