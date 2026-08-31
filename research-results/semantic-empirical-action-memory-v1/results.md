# Semantic empirical action memory v1 — result

**Decision:** `EMPIRICAL_ACTION_NAVIGATION_NOT_PROMISING`

Authoritative workflow run: `33347529752`  
Authoritative experiment head: `6c5daf49398ecde65b1c0b2dab2d7b67b40a18c0`  
Aggregate artifact: `9742879071`  
Artifact ZIP digest: `sha256:da0b03e2d554f9df85e7a43ab87347dd8093f2ef53b2f136cd1d1f0749fee24d`

The fresh target-free calibration result remains positive, and the semantic experiment shows that nearest-neighbor empirical action memory carries useful control information. But the pure six-start local-MPC architecture does not beat global breadth at equal render budget.

## Aggregate semantic evidence

- complete fresh rectangle: 12 seeds × 8 concepts = 96 cells;
- held-out top-1: breadth `62.5%`, empirical memory `53.125%`, route/action mean `50.0%`;
- empirical memory vs breadth mean held-out F1: `-0.0251332`, one-sided 95% seed lower bound `-0.0369792`;
- empirical memory vs route/action mean: `+0.0183725`, lower bound `+0.0076818`;
- route/action mean vs breadth: `-0.0435057`, lower bound `-0.0546312`.

The selected target-free memory configuration was `k=16`, action weight `4.0`, shrinkage `0.5`.

## Interpretation

The important positive finding survives the semantic test: **local empirical experience ranks interventions better than a global route/action average even on unseen semantic targets**. The failure is architectural. Replacing a globally diverse 60-state archive with a six-start local planning beam loses more search-space coverage than the better action ranking can recover.

No human-recognition package was authorized.

## Next experiment

Do not retune on the consumed arrow/key/mushroom/cloud/number-3/hourglass/bird/cactus outcomes. Test the complementary architecture on a new semantic suite and new seeds:

1. preserve a large, route-balanced target-blind breadth prefix;
2. use exact external semantic reranking only after those renders exist;
3. spend a bounded suffix of the same 60-render budget refining promising breadth states;
4. compare empirical-memory refinement against an otherwise identical route/action-mean refinement control and breadth60;
5. keep human recognition behind a fresh preregistered aggregate gate.

This tests whether empirical action memory is valuable as an **exploitation layer on top of breadth**, rather than as a replacement for breadth.
