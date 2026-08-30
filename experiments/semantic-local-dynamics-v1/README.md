# Semantic local dynamics v1

## Why this experiment exists

`semantic-world-model-navigation-v1` rejected a global raw-math-state -> visual-state surrogate before any semantic evidence was consumed. The failure was concentrated in nonlinear global generalization, especially `orbit`.

This follow-up tests a narrower Bitter-Lesson-style hypothesis:

> A target-agnostic learner can acquire reusable local knowledge of the mathematical generator by predicting `current visual state + mathematical intervention -> delta visual state`, and that learned local dynamics can spend a fixed render budget more effectively on completely unseen semantic targets.

Semantics remain outside the mathematical generator. No concept-specific primitive, grammar change, prompt label, semantic target, target distance, or human rating is allowed in training or target-free calibration.

## Frozen generator and perceptual state

Routes: `recurrence`, `orbit`, `filament`.

The generator, orbit adapter, K=2 Hamiltonian spectral material control, and perceptual descriptor are inherited unchanged from the confirmed upstream branches. Visual state is the same 490-D descriptor vector used by world-model v1 (`grid16`, `grid8`, projections, polar, orientation, radial, symmetry, topology).

## Generic local interventions

Every parent state receives a deterministic action set generated without any target:

- 6 native grammar mutations: two draws each at scales `0.35`, `0.70`, `1.00`, preserving an existing material field;
- 2 material actions:
  - if the parent is native: add two independently drawn frozen K=2 spectral controls;
  - if the parent already has spectral control: two projective-geodesic coefficient moves at angles `0.04` and `0.12`, recomputing the frozen velocity RMS.

The model sees the parent visual state, route/material indicators, and the exact mathematical action delta. It predicts visual delta and child validity. It never sees semantics.

## Stage A — target-free local-dynamics calibration

Training seeds (fresh):

`734100011, 734100029, 734100041, 734100067, 734100079, 734100101, 734100113, 734100137, 734100151, 734100173, 734100197, 734100211`

Each seed generates 24 base genomes per route, both native and spectral parents, and 8 target-blind actions per parent: `24 * 3 * 2 * 8 = 1152` parent/action pairs per seed, `13,824` total.

Calibration seeds (fresh):

`734200011, 734200029, 734200041, 734200067`

Each calibration seed uses 8 base genomes per route, native+spectral parents, and 8 held-out actions: `384` pairs per seed, `1,536` total.

Calibration is entirely target-free. Two tests are frozen:

1. **Delta prediction.** Compare local-model visual-delta MSE against the stronger of zero-delta and route/action-family mean-delta baselines.
2. **Generic action retrieval.** For each held-out parent, generate a separate deterministic 32-action local proposal set. Treat four actually rendered children in turn as generic pseudo-goals. Rank all 32 actions using predicted child visual states. This tests whether learned dynamics can navigate toward an unseen *generated state*, not a semantic concept.

Decision `LOCAL_DYNAMICS_CALIBRATED` requires all of:

- complete invariant rectangle;
- overall MSE improvement over the stronger baseline >= `0.20`;
- route-level MSE improvement positive for all three routes;
- predicted top-4 contains the true nearest action in >= `0.55` of pseudo-goal retrieval tasks;
- predicted top-1 action is in the true top quartile in >= `0.80` of tasks;
- mean true regret of predicted top-1 <= `0.035` perceptual-distance units;
- child-validity balanced accuracy >= `0.80` when both classes are present (otherwise calibration records the degenerate class and does not fail solely for absence of invalids).

If this gate fails, semantic evaluation is forbidden. Calibration seeds are not retuned.

## Stage B — zero-shot semantic navigation

Only if Stage A passes.

The semantic suite is the already-frozen but **never consumed** v1 suite:

`arrow, key, mushroom, cloud, number-3, hourglass, bird, cactus`.

No semantic outcome was produced in world-model v1 because Stage A failed, so these remain fresh outcome-bearing concepts.

Consumed seeds (fresh):

`734300011, 734300029, 734300041, 734300067, 734300079, 734300101, 734300113, 734300137, 734300151, 734300173, 734300197, 734300211`

Excluded smoke seed: `734399999`.

For each seed and concept, both arms receive exactly **60 rendered candidates**.

### `breadth60`

The control arm receives 60 target-blind balanced independent states: 10 base genomes per route, native + spectral. Target information is used only after all 60 renders exist, using the exact frozen perceptual reranker.

### `localDynamics60`

- render 6 target-blind starts: one native + one spectral per route;
- maintain an exact-rendered beam of 6 states;
- 3 rounds;
- from each beam state generate 64 deterministic local mathematical proposals without rendering;
- use the calibrated local model and external target descriptor to rank proposals;
- render exactly the predicted-best 18 unique proposals per round;
- exact frozen perceptual reranking selects the next beam;
- total = `6 + 3*18 = 60` renders.

The semantic target affects only proposal ranking in the external controller. It never changes generator equations, action generation, training data, or model parameters.

Primary evaluation remains the frozen held-out prototype metric, not the controller's own prediction.

Decision `LOCAL_DYNAMICS_SEMANTIC_NAVIGATION_PROMISING` requires all of:

- complete hard-invariant rectangle and exact 60/60 budgets;
- mean paired held-out target-F1 delta (`localDynamics60 - breadth60`) > `0.05`;
- one-sided seed-level 95% lower bound > `0`;
- localDynamics held-out top-1 >= `0.75` overall;
- top-1 improvement over breadth60 >= `0.15` absolute;
- >=6/8 concepts positive on mean held-out F1 delta;
- >=6/8 concepts reach >= `0.50` localDynamics top-1;
- no concept contributes >40% of total positive F1 gain;
- all selected final candidates valid.

A pass authorizes a new blinded human-recognition gate. It does **not** by itself establish human recognizability or open-vocabulary language understanding.

## Outcome blindness

Consumed semantic jobs may be monitored only for status. Individual concept/seed outputs must not be inspected. The aggregate reducer is the first semantic outcome read.
