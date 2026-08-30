# Semantic breadth budget v1

## Question

After #96 showed that global breadth + end rerank is materially better than adaptive local search but still insufficient at 60 attempts, measure the constrained-budget response of the **same breadth policy** without changing the objective, grammar, routes, or operators.

This experiment asks for the smallest budget among `120`, `240`, and `480` challenger attempts that is mechanically strong enough to justify a fresh human-recognition review.

It does not itself establish human recognizability or artistic quality.

## Frozen policy

Routes: `recurrence`, `orbit`, `filament`.

Concepts: the same frozen eight prototypes:

`diamond, spiral, lightning, leaf, umbrella, crown, letter-s, sailboat`.

Generation is target-blind. One nested archive is generated once per master seed. The prompt never enters any candidate-generation RNG stream.

Three shared hard-valid starts (one per route) are available at every budget without counting as challenger attempts.

For each route, generate 160 independent challengers as 80 native/spectral pairs:

- each pair contains one independently seeded native genome;
- the second candidate is another independently seeded incumbent genome plus the frozen K=2 amplitude-16 spectral control;
- all attempts count, including invalids.

Nested total budgets:

- `60`: first 20 challengers per route = 10 native + 10 spectral;
- `120`: first 40 per route = 20 + 20;
- `240`: first 80 per route = 40 + 40;
- `480`: first 160 per route = 80 + 80.

At each budget, only after the full target-blind prefix exists, choose the best valid candidate separately for each requested concept with the frozen `PrototypePerceptualSelector` rank key. Held-out prototype F1/top-1 remains evaluation-only.

## Fresh seeds

Excluded smoke: `732499999`.

Consumed master seeds (20):

`732500011, 732500029, 732500041, 732500067, 732500079, 732500101, 732500113, 732500137, 732500151, 732500173, 732500197, 732500211, 732500233, 732500257, 732500271, 732500293, 732500317, 732500341, 732500363, 732500389`.

Master seed is the inference unit. Each seed contains all eight concepts and all four nested budgets.

## Mechanical sufficiency gate

For each candidate budget `B ∈ {120,240,480}`, compare against the nested 60-attempt prefix.

Budget `B` is sufficient only if all are true:

1. complete 20-seed × 8-concept rectangle at all four budgets;
2. exact nested budgets and exact 50/50 native/spectral allocations at every route prefix;
3. target-blind archive replay is deterministic;
4. pooled hard-validity at budget B `>= 0.90` and every route `>= 0.85`;
5. held-out top-1 fraction at B `>= 0.75` overall;
6. every concept has held-out top-1 fraction at B `>= 0.50`;
7. mean selected held-out requested-target F1 at B `>= 0.60`;
8. mean paired requested-target F1 improvement B−60 `>= +0.03`;
9. one-sided 95% Student-t lower bound of the 20 master-seed mean B−60 F1 deltas is `> 0`;
10. held-out top-1 fraction improves over 60 by `>= +0.15`;
11. every leave-one-concept-out mean B−60 F1 delta is `> 0`;
12. no concept contributes more than `0.30` of total positive B−60 F1 delta mass.

Decision is the **smallest** sufficient budget:

- `SEMANTIC_BREADTH_BUDGET_120_SUFFICIENT`, else
- `SEMANTIC_BREADTH_BUDGET_240_SUFFICIENT`, else
- `SEMANTIC_BREADTH_BUDGET_480_SUFFICIENT`, else
- `SEMANTIC_BREADTH_BUDGET_NOT_SUFFICIENT`.

No threshold, seed, concept, objective, grammar, or operator changes after consumed evidence.

## Interpretation

A sufficient budget authorizes generation of a fresh blinded human-recognition package at that smallest passing budget. It does **not** itself authorize the claim `ask for X -> looks like X`.

If 480 is still insufficient despite #95's 1,536-candidate accessible-capacity result, the next layer is not another selector tweak: diagnose which concepts require representation/compositional changes or substantially larger search budgets.
