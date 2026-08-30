# Semantic empirical action memory v1

## Why this experiment exists

`semantic-local-dynamics-v1` trained successfully on 13,824 target-blind transitions but failed fresh target-free calibration: its learned conditional visual-delta predictor was worse than the route/action-family empirical mean on every route, especially `orbit`. No semantic evidence was consumed.

This follow-up tests a simpler hypothesis:

> Reusing actual outcomes from visually and mathematically similar past interventions can provide useful generator control without fitting a global dynamics function.

The method is deliberately nonparametric. Training experience remains target-blind. Semantic targets are never used to build or select the memory.

## Frozen prior experience

The memory reuses the exact 12 immutable training artifacts produced by GitHub Actions run `33336810605`, head `a22ad8d607b8f879949fec3f3c8f537079629ed6`:

`734100011, 734100029, 734100041, 734100067, 734100079, 734100101, 734100113, 734100137, 734100151, 734100173, 734100197, 734100211`.

Each artifact contains 1,152 target-blind transitions. Total memory: 13,824 observed parent/action/outcome triples. If those artifacts expire, the same frozen generator, seeds, and source hashes reproduce them; the experiment does not depend on semantic outcomes from any earlier run.

Each memory row contains:

- rendered 490-D parent visual descriptor;
- route;
- one of the same 8 generic action families from local-dynamics v1;
- exact mathematical action delta;
- actually observed visual delta;
- child-validity observation.

No prompt label, semantic target, target distance, human rating, or concept-specific primitive appears in the memory.

## Retrieval rule

Candidate actions are compared only with prior transitions from the **same route and action family**. Thus the previous route/action-family mean baseline is exactly the non-local limit of the same empirical experience.

Neighbor distance is:

`visual_state_distance + action_weight * standardized_action_delta_distance`

where visual-state distance is the already-frozen perceptual descriptor distance, and action-delta distance is mean absolute standardized difference over active mathematical action dimensions within that route/action stratum.

The raw neighbor visual delta is an inverse-distance-weighted mean of the `k` nearest observed deltas. To control nearest-neighbor variance, the final prediction is shrunk toward the route/action mean:

`mean + α * (neighbor_mean - mean)`.

Frozen target-free candidate grid:

- `k ∈ {4, 8, 16, 32, 64}`
- `action_weight ∈ {0, 0.25, 1, 4}`
- shrinkage `α ∈ {0.25, 0.50, 0.75, 1.00}`

No other retrieval form or parameter is tried in this lineage.

## Training-only configuration selection

Configuration selection uses leave-one-training-seed-out cross-validation over the already-collected target-blind experience. For every held seed, four fixed base indices per route (`0, 6, 12, 18`), both native and spectral parents, and all eight actions are queried; the held seed is absent from neighbor memory.

The selection rule is frozen before fresh calibration. For each configuration, training-only CV measures improvement over the held-out route/action mean on: predicted-top-1 true top-quartile rate, exact action top-2 recall, true regret, and visual-delta MSE. A fixed additive utility combines those four improvements; only non-negative-MSE configurations are preferred. Ties favor stronger action-utility evidence and then smaller configurations.

This cross-validation chooses a configuration; it is not itself the promotion evidence.

## Stage A — fresh target-free calibration

Fresh seeds:

`735200011, 735200029, 735200041, 735200067, 735200079, 735200101`.

Each seed contains 384 held-out transition pairs plus 96 independent generic pseudo-goal retrieval tasks. Semantic targets are forbidden.

Two predictors are compared from the same frozen experience:

- `mean`: unconditional route/action-family average visual delta;
- `memory`: selected nearest-neighbor empirical delta.

Decision `EMPIRICAL_ACTION_MEMORY_CALIBRATED` requires all of:

- complete invariants and exact six-seed rectangle;
- memory visual-delta MSE no worse than the route/action mean overall (MSE is a sanity diagnostic, not the primary navigation objective);
- memory pseudo-goal true action in predicted top-4 >= `0.20` and >= `+0.03` over mean;
- memory predicted top-1 in the actual top quartile >= `0.45` and >= `+0.08` over mean;
- memory mean true regret <= `0.035` and at least 8% lower than mean;
- memory improves top-quartile rate on at least 2/3 routes;
- memory lowers regret on at least 2/3 routes;
- finite neighbor-distance diagnostics.

Exact action recovery is intentionally secondary: with redundant actions, the controller only needs an intervention that lands near the desired visual consequence. True top-quartile rate and regret are therefore the primary calibration signals.

If this gate fails, semantic smoke and consumed jobs are forbidden. Fresh calibration seeds are never retuned.

## Stage B — zero-shot semantic navigation

Only if Stage A passes.

The semantic catalog remains the frozen, never-consumed suite:

`arrow, key, mushroom, cloud, number-3, hourglass, bird, cactus`.

Fresh semantic seeds:

`735300011, 735300029, 735300041, 735300067, 735300079, 735300101, 735300113, 735300137, 735300151, 735300173, 735300197, 735300211`.

Excluded smoke seed: `735399999`.

Each seed/concept has three equal **60-render** arms:

### `breadth60`

60 target-blind independent states: 10 native + 10 spectral states per route. Target information appears only after all renders exist.

### `meanDynamics60`

6 shared valid starts, then 3 rounds × 18 renders. Each round generates 64 generic mathematical actions per current beam state without rendering. Predicted child state is current state plus the unconditional route/action-family mean observed delta. The external target ranks predictions; actual rendered states then rerank the beam exactly.

### `empiricalMemory60`

Identical starts, budgets, proposal generator, external target, and exact replanning loop. The only difference is that predicted child visual state comes from nearest observed target-blind transitions.

This three-arm design distinguishes the value of generic empirical action averages from the additional value of local experience retrieval.

Primary decision `EMPIRICAL_ACTION_MEMORY_SEMANTIC_NAVIGATION_PROMISING` requires:

- exact hard-invariant rectangle and identical frozen memory config;
- mean held-out F1 gain memory vs breadth > `0.05` with positive one-sided seed-level 95% lower bound;
- mean held-out F1 gain memory vs mean > `0.015` with positive lower bound;
- memory held-out top-1 >= `0.75` and >= `+0.15` over breadth;
- >=6/8 concepts positive memory vs breadth;
- >=5/8 concepts positive memory vs mean;
- >=6/8 concepts memory top-1 >= `0.50`;
- every leave-one-concept-out memory-vs-breadth mean positive;
- no concept contributes >40% of total positive memory-vs-breadth gain.

A separately preregistered secondary decision `ROUTE_ACTION_MEAN_SEMANTIC_NAVIGATION_PROMISING` applies if the memory hypothesis fails but the simpler mean controller independently meets the analogous breadth-improvement gate. This prevents a useful simpler mechanism from being discarded merely because nearest-neighbor locality adds no value.

Neither mechanical decision establishes human recognizability.

## Frozen recognition handoff

If either semantic controller passes, the workflow builds a blinded recognition package automatically. The winning arm is selected only by the preregistered mechanical decision above; examples are not chosen visually.

Frozen concept/display-seed assignments:

- arrow → `735300011`
- key → `735300029`
- mushroom → `735300041`
- cloud → `735300067`
- number-3 → `735300079`
- hourglass → `735300101`
- bird → `735300113`
- cactus → `735300137`

Panels are deterministically shuffled with order seed `735390001`. The review artifact contains only anonymous panels and labels; the mapping is uploaded separately as a sealed key. Formal forced-choice recognition requires >=6/8 exact matches. Spontaneous recognizability is recorded separately and is not overwritten by forced guesses.

## Outcome blindness

Before the Stage A aggregate exists, calibration shards may be inspected only for execution status. If Stage A passes, semantic jobs may likewise be inspected only for status until the complete semantic aggregate exists. The sealed recognition key must not be opened before the human mapping is complete.
