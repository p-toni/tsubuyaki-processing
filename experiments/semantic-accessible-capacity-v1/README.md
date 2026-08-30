# Semantic accessible-capacity audit v1

## Question

After `PERCEPTUAL_SEMANTIC_STEERING_NOT_READY`, is the remaining bottleneck primarily selector/search quality, or does the current intrinsic-1D grammar/runtime distribution simply fail to expose semantically recognizable forms for some concepts?

This is an **accessible capacity** audit, not a theoretical expressivity proof.

## Frozen archive generator

Routes: `recurrence`, `orbit`, `filament` only.

For each fresh archive seed and route:

- draw exactly 256 independent native route genomes from a route-local deterministic RNG;
- every draw counts whether valid or invalid;
- create one spectral twin of every native draw using the confirmed K=2 amplitude-16 material control and a deterministic independent field seed;
- total per route: 512 attempted candidates = 256 native + 256 spectral;
- total per archive seed: 1536 attempts = 768 native + 768 spectral.

No target label, target pixels, prototype descriptor, target metric, semantic selector, or human judgment is visible while the archive is generated. The exact same archive is scored post-hoc against all eight concepts.

Candidate hard-validity remains the existing route checker over t=30/90/150. Semantic scoring is performed at t=90 only after archive generation completes.

## Frozen concepts

Reuse the eight **fresh-concept definitions** from semantic-perceptual-steering-v1, because the question is diagnostic: why did those exact concepts divide into strong and weak identities?

`diamond, spiral, lightning, leaf, umbrella, crown, letter-s, sailboat`

No target geometry or metric may be changed in this audit.

## Post-hoc scoring

Use the held-out prototype recognizer from semantic-perceptual-steering-v1. It is not the selector metric.

For every valid candidate, compute held-out F1 against all eight prototypes once. Each candidate has one held-out top-1 concept.

For each archive seed x concept record:

- `top1Found`: at least one valid archive candidate has this concept as held-out top-1;
- `bestTop1TargetF1`: maximum target F1 among candidates whose held-out top-1 is the concept, or 0 if none;
- `bestAnyTargetF1`: maximum target F1 regardless of the candidate's top-1 label;
- route/operator of the best top-1 candidate when one exists.

This audit deliberately does not use the perceptual selector score as its primary evidence.

## Fresh archive seeds

The prefix `732100` had no repository occurrence before preregistration.

Exactly 12 fresh archive seeds:

`732100011, 732100027, 732100039, 732100057, 732100081, 732100103, 732100119, 732100143, 732100157, 732100181, 732100207, 732100229`

Excluded smoke seed: `732099999`.

These seeds cannot be reused to tune route sampling, archive size, validity rules, target definitions, scoring, or gates.

## Preregistered decision

Decision **`ACCESSIBLE_SEMANTIC_CAPACITY_PRESENT`** requires all:

1. complete 12-seed archive rectangle;
2. exactly 1536 attempted candidates per seed, 768 native + 768 spectral;
3. pooled hard-validity >= 0.90 and every route >= 0.85;
4. `top1Found` in >=80% of the 96 seed x concept cells;
5. every concept has `top1Found` in >=50% of the 12 fresh archives;
6. each previously weak concept (`spiral`, `umbrella`, `crown`, `letter-s`) has `top1Found` in >=50% of archives;
7. mean `bestTop1TargetF1` across all 96 cells >= 0.45;
8. no single concept contributes >35% of total positive `bestTop1TargetF1` mass.

Pass means broad target-blind sampling already exposes semantically classifiable candidates often enough that search/retention is the next bottleneck.

If any gate fails, decision is **`ACCESSIBLE_SEMANTIC_CAPACITY_LIMITED`**. That means the current route distribution does not reliably expose semantic forms even under a 25.6x larger attempt budget than the 60-attempt target-guided steering test; it does **not** prove mathematical impossibility.

## Authority boundary

This audit cannot establish human recognizability. It only determines whether the incumbent grammar/runtime distribution contains candidates that the held-out semantic recognizer can distinguish. Human recognition remains required before any `looks like X` product claim.
