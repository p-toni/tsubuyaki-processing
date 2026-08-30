# Semantic breadth-rerank v1

## Question

After `ACCESSIBLE_SEMANTIC_CAPACITY_PRESENT`, distinguish a constrained-budget **search-policy** bottleneck from a pure budget bottleneck.

At the same 60-challenger budget for one requested concept, does global breadth followed by one discriminative perceptual rerank outperform the current target-aware adaptive local search?

This is a mechanical experiment. It does not establish human recognizability or artistic quality.

## Frozen arms

Concepts are the already-frozen eight prototypes from semantic-perceptual-steering-v1:

`diamond, spiral, lightning, leaf, umbrella, crown, letter-s, sailboat`.

Routes: `recurrence, orbit, filament` only.

Both arms use the frozen `PrototypePerceptualSelector` / held-out prototype recognizer and the confirmed native+spectral operator family.

### A — adaptive-local baseline

Exactly the current perceptual semantic search policy from #94:

- one shared hard-valid start per route;
- 20 challenger attempts per route;
- exactly 10 native + 10 spectral challengers per route;
- target-aware pairwise selection during the trajectory;
- 60 total challenger attempts;
- final route champions reranked with the same perceptual selector.

### B — breadth-rerank candidate

- no target-aware survival decisions during generation;
- 20 independent fresh challenger genomes per route;
- exactly 10 native + 10 spectral challengers per route;
- native challenger = independently seeded incumbent route genome;
- spectral challenger = independently seeded incumbent route genome plus frozen K=2 amplitude-16 material control;
- all attempts count, including invalids;
- generation is target-blind (prompt is not used in breadth RNG streams);
- after all 60 attempts exist, choose the best valid candidate once with the frozen `PrototypePerceptualSelector` rank key.

Thus the intervention is **local adaptive exploitation vs global breadth + end rerank**, not more compute.

## Fresh inference seeds

Smoke only: `732299999` (excluded).

Consumed master seeds (16):

`732300011, 732300029, 732300041, 732300067, 732300079, 732300101, 732300113, 732300137, 732300151, 732300173, 732300197, 732300211, 732300233, 732300257, 732300271, 732300293`.

Inference unit is master seed. Each seed contains all eight concepts.

## Held-out outcomes

For each seed×concept:

- adaptive held-out requested-target F1;
- breadth held-out requested-target F1;
- delta F1 = breadth - adaptive;
- adaptive held-out top-1 identity;
- breadth held-out top-1 identity;
- route/operator validity diagnostics.

The held-out recognizer is not used for candidate selection.

## Preregistered advancement gate

Advance only if all are true:

1. complete `16 × 8 = 128` paired rectangle;
2. exactly 60 challenger attempts per arm per seed×concept, exactly 30 native + 30 spectral;
3. mean paired held-out target-F1 delta `>= +0.03`;
4. one-sided 95% Student-t lower bound of the 16 master-seed mean F1 deltas is `> 0`;
5. breadth held-out top-1 fraction exceeds adaptive by `>= +0.10`;
6. breadth held-out top-1 fraction is `>= 0.60` overall;
7. every concept has breadth held-out top-1 fraction `>= 0.40`;
8. every leave-one-concept-out mean F1 delta is `> 0`;
9. breadth pooled validity `>= 0.90` and each route validity `>= 0.85`;
10. no concept contributes more than `0.30` of total positive F1 delta mass.

Pass: **`SEMANTIC_BREADTH_RERANK_PROMISING`**.

Fail: **`SEMANTIC_BREADTH_RERANK_NOT_PROMISING`**.

No threshold, budget, seed, concept, or operator retuning on consumed evidence.

## Interpretation

- Pass: early adaptive steering is the dominant constrained-budget failure mode. The next step is runtime integration of breadth/rerank or a diversity-preserving approximation, then fresh human recognition.
- Fail: 60 attempts remain insufficient even with global breadth. The next step is a fresh preregistered budget-response experiment (e.g. 60/120/240) rather than another selector tweak.
