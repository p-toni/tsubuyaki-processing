# Semantic world-model navigation v1

## Question

Can a target-agnostic learned surrogate of the existing mathematical generator use cheap model inference to navigate a much larger candidate pool toward **unseen external semantic targets**, while keeping the generator itself free of semantic primitives?

This directly follows `SEMANTIC_BREADTH_BUDGET_NOT_SUFFICIENT`: brute breadth improves through ~240 rendered candidates, then held-out semantic top-1 plateaus even while target F1 continues rising.

## Architectural hypothesis

Semantics stay outside the generative mathematics.

The learned component sees only generic mathematical state and generic visual consequences:

`route + genome + optional spectral field -> perceptual state`

It is never trained on concept labels, prompt names, target prototypes, target distances, or human ratings.

At semantic evaluation time only, an external controller compares the surrogate's predicted visual state with a frozen requested target. The core grammar remains unchanged.

## Frozen generator

Routes: `recurrence`, `orbit`, `filament`.

Operators/states: native genomes and the confirmed K=2 amplitude-16 spectral material control. No new semantic route, primitive, landmark, scaffold, or concept-specific mutation is permitted.

## Learned surrogate

A deterministic random-feature ridge regressor predicts a generic perceptual state from mathematical state.

Input contains route identity, all numeric native genome coordinates, material-control presence, and the 25 spectral coefficients. Training statistics standardize the mathematical state.

Output is a target-agnostic subset of the frozen perceptual descriptor: `grid16`, `grid8`, X/Y projections, polar occupancy, orientation, radial profile, symmetry, and topology. No target-relative field is present.

The hidden random feature map and ridge strength are frozen before evidence.

## Stage A — target-free model calibration

Training seeds (fresh, repository-searched):

`733100011, 733100029, 733100041, 733100067, 733100079, 733100101, 733100113, 733100137, 733100151, 733100173, 733100197, 733100211`

Each seed generates 80 independent base genomes per route. Every base contributes native + spectral examples: 480 examples/seed, 5,760 training examples total.

Calibration seeds:

`733200011, 733200029, 733200041, 733200067`

Calibration remains target-free. It tests held-out perceptual-state prediction and action-free retrieval: for arbitrary held-out visual probes, can predicted states identify genuinely nearby mathematical states?

Calibration passes only if all hard invariants hold and:

1. overall surrogate MSE is at least 20% lower than a frozen route/operator-mean predictor;
2. every route has positive MSE improvement over that baseline;
3. across deterministic 64-candidate retrieval tasks, the true nearest candidate appears in the surrogate-predicted top 8 at least 50% of the time;
4. the surrogate-predicted top-1 candidate is truly better than the candidate-set median at least 85% of the time.

If Stage A fails, semantic test seeds are not consumed.

## Stage B — zero-shot unseen-target navigation

Fresh concepts, never used in surrogate training:

`arrow, key, mushroom, cloud, number-3, hourglass, bird, cactus`

Fresh test seeds:

`733300011, 733300029, 733300041, 733300067, 733300079, 733300101, 733300113, 733300137, 733300151, 733300173, 733300197, 733300211`

For each test seed, one prompt-independent mathematical pool is generated and shared by all eight concepts. The pool contains 1,024 independent bases per route, each in native and spectral form: 6,144 unrendered mathematical states.

Two arms get exactly 60 **rendered/evaluated** candidates per concept:

- `breadth60`: fixed balanced target-blind 60-state prefix from the pool, then the frozen exact perceptual reranker.
- `world-model60`: surrogate-predict all 6,144 states cheaply, rank them against the external target using predicted generic perceptual state, render only the predicted best 60, then use the same frozen exact perceptual reranker.

The large pool is target-blind. Target identity affects only surrogate ranking after all mathematical states already exist.

Primary evaluation remains the frozen held-out prototype F1/top-1 metric, not the surrogate's own predicted distance.

## Frozen decision gate

Decision `SEMANTIC_WORLD_MODEL_NAVIGATION_PROMISING` iff:

- complete 12 x 8 paired rectangle and all hard invariants;
- exactly 60 rendered candidates per arm/concept;
- prompt-independent pool replay is exact;
- learned model artifact is identical for all semantic jobs;
- mean paired held-out target-F1 delta > 0.05;
- one-sided 95% lower bound of seed-mean paired F1 delta > 0;
- world-model held-out top-1 >= 0.75 overall;
- top-1 improvement vs breadth60 >= 0.15;
- at least 6/8 concepts have world-model top-1 >= 0.50;
- at least 7/8 concepts have non-negative mean F1 delta;
- every leave-one-concept-out mean F1 delta > 0;
- no concept contributes >40% of positive F1 delta;
- pooled validity >=0.90 and every route validity >=0.85.

A pass authorizes a fresh blinded human-recognition package. It does **not** itself establish human recognizability or open-vocabulary language understanding.

## Scientific boundary

This test is intentionally a Bitter-Lesson-style bet: useful structure must be learned from generic generator experience and then generalize to targets not present during learning. A concept-specific grammar change, target-conditioned training, or tuning on consumed semantic seeds invalidates the experiment.
