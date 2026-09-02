# Morphology-context artistic judge prospective v1 — result

## Decision

`MORPHOLOGY_CONTEXT_JUDGE_PROSPECTIVE_NOT_PROMISING`

The run is protocol-valid. Human ratings were committed before either sealed object was opened. The exact canonical prediction JSON then re-hashed to the preregistered SHA-256 commitment `13a137bce8682ba22e65341ad6e76baf2c2d0174c44bb067fa41b59f2f3f4b19`, after which the identity key was opened and route-level scoring performed.

## Primary result

- human-reviewable: **24 / 24**
- human-decisive: **24 / 24**
- correct morphology-context predictions: **12 / 24**
- decisive accuracy: **0.5000**
- one-sided exact binomial p-value vs `p=0.5`: **0.5805901289**
- model ties on decisive blocks: **1 / 24 = 0.0417**

Per route:

- recurrence: **5 / 8 = 0.625**
- orbit: **4 / 8 = 0.500**
- filament: **3 / 8 = 0.375**

## Frozen gate

1. reviewable >= 18 / 24: **PASS**
2. decisive >= 12: **PASS**
3. decisive accuracy > 0.65: **FAIL**
4. one-sided exact binomial p <= 0.10: **FAIL**
5. every route with >=3 decisive has accuracy >= 0.50: **FAIL** (`filament = 0.375`)
6. model tie <=25% of decisive blocks: **PASS**

The conjunction therefore fails.

## Interpretation

Adding explicit deterministic morphology and temporal descriptors did not make the model-mediated artistic judge prospectively reliable enough to become an authority layer. This result does **not** justify descriptor-by-descriptor tuning, prompt revision, model cycling, or replay of the consumed `757xxx` population.

The earlier generic pixels-only prospective replacement scored 7 / 24 on a different fresh population. The current 12 / 24 point estimate is not a causal A/B comparison, so it should not be used to claim that morphology improved the judge.

## Research consequence

Per preregistration, close the generic/morphology model-mediated artistic-judge line. Do not run a second replication.

The next research boundary is **explicit human-preference learning over reproducible morphology/context representations**: use accumulated blinded human pairwise judgments as labels, keep the learner low-capacity and antisymmetric, validate it without re-labeling consumed populations, and require fresh prospective evidence before it can influence search or portfolio preservation.
