# Semantic memory-hybrid causal replication v1

## Question

`semantic-breadth-memory-hybrid-v1` produced a small but robust empirical-memory-hybrid advantage over breadth (`+0.01351` held-out F1; one-sided seed lower bound `+0.00092`) while the direct empirical-memory-vs-mean refinement contrast was positive but underpowered (`+0.00523`; lower bound `-0.00144`). Prototype top-1 did not improve.

This experiment asks one final causal question:

> **With the architecture frozen exactly, does empirical action memory reliably outperform an otherwise identical route/action-mean refinement controller on fresh semantic states?**

No architecture tuning is allowed. If the direct controller effect does not replicate, this semantic action-memory research line stops.

## Frozen architecture

The search architecture is unchanged from `semantic-breadth-memory-hybrid-v1`:

- `breadth60`: 60 target-blind breadth renders;
- `meanHybrid60`: exact first 48 breadth renders + 12 refinements;
- `memoryHybrid60`: the same 48 prefix + 12 refinements;
- six exact semantic prefix parents;
- 64 deterministic proposals per parent;
- mean and memory controllers rank the exact same 384 proposals;
- exact semantic reranking chooses the final state from each 60-render archive;
- same calibrated memory: `k=16`, action weight `4.0`, shrinkage `0.5`;
- same frozen target-blind memory artifact lineage from run `33347529752` / training run `33336810605`.

Only the semantic target suite, seed population and experiment stream identifier are fresh.

## Fresh semantic suite

Frozen concepts:

```text
star
tree
fish
chair
anchor
guitar
butterfly
bicycle
```

`targets.py` requires every target raster fingerprint to be distinct from all earlier structural and semantic suites through `semantic-breadth-memory-hybrid-v1`.

## Seeds and power

Excluded smoke only:

```text
735599999
```

Twenty fresh semantic seeds, checked absent from repository history before branch creation:

```text
735500011
735500029
735500041
735500067
735500079
735500101
735500113
735500137
735500151
735500173
735500197
735500211
735500229
735500251
735500271
735500293
735500307
735500331
735500353
735500379
```

The sample size increase is the only intentional design change. The prior direct effect (`mean=0.00523`, seed SD `0.01288`) implied that ~17 independent seed means would be needed for a one-sided 95% lower bound above zero if the effect reproduced exactly. Twenty seeds provide a modest preregistered margin without changing the search mechanism.

## Primary causal estimand

For each seed, average across all eight concepts:

```text
memoryHybrid60 held-out target F1 - meanHybrid60 held-out target F1
```

Primary uncertainty: one-sided 95% t lower bound across the 20 fresh seed means.

Breadth remains a frozen anchor and is not used to select or tune the controller.

## Causal replication gate

`EMPIRICAL_MEMORY_REFINEMENT_REPLICATED` iff all hold:

1. complete hard-invariant 20 × 8 rectangle;
2. immutable memory configuration identical across shards;
3. mean `memoryHybrid60 - meanHybrid60` held-out F1 > `+0.005`;
4. one-sided 95% seed lower bound for memory-vs-mean > `0`;
5. at least 5/8 concept means are positive memory-vs-mean;
6. every leave-one-concept-out memory-vs-mean mean remains > `0`;
7. no concept contributes more than 50% of total positive memory-vs-mean F1 gain;
8. mean `memoryHybrid60 - breadth60` held-out F1 > `+0.010`;
9. one-sided 95% seed lower bound for memory-vs-breadth > `0`.

The `+0.005` and `+0.010` effect bars are carried forward unchanged from the prior preregistration. They are not re-estimated from the consumed result.

If any causal gate fails, decision is:

```text
EMPIRICAL_MEMORY_REFINEMENT_NOT_REPLICATED
```

and this semantic action-memory line stops. Do not retune nearby architecture or thresholds on these outcomes.

## Separate recognition-advancement gate

A replicated continuous controller effect does **not** automatically authorize human recognition.

Human recognition is authorized only if the causal replication gate passes **and**:

1. memory held-out top-1 exceeds breadth held-out top-1 by at least `0.05` absolute;
2. at least 5/8 concept means remain positive memory-vs-breadth;
3. every leave-one-concept-out memory-vs-breadth mean remains > `0`;
4. no concept contributes more than 50% of positive memory-vs-breadth gain.

The top-1 bar is deliberately unchanged from the failed prior gate. We do not relax the human boundary because continuous F1 improved.

If causal replication passes but recognition advancement fails, decision is:

```text
EMPIRICAL_MEMORY_REFINEMENT_REPLICATED_NO_RECOGNITION
```

This supports a mechanical continuous-matching claim only.

If both gates pass:

```text
EMPIRICAL_MEMORY_REFINEMENT_REPLICATED_RECOGNITION_AUTHORIZED
```

and the workflow may generate the blinded human-recognition package.

## Human boundary

If authorized, freeze one anonymous output per concept using preregistered display seeds. Target silhouettes are not shown. The reviewer matches A-H to the eight concept labels exactly once each and records spontaneous recognizability before forced choice.

Recognition success requires at least **6/8 exact matches**, unchanged from the prior semantic protocols.

## Blindness and stop rules

- Do not inspect any fresh seed-level outcome before the complete aggregate reducer finishes.
- Once the first fresh semantic shard opens, do not change targets, seeds, architecture, budgets, controller configuration, metrics or gates.
- All 20 seeds and eight concepts are consumed after execution regardless of outcome.
- No post-hoc split tuning, parent-count tuning, proposal-count tuning or target selection is allowed.
- If the causal gate fails, stop this semantic action-memory line.
- If causal replication passes but recognition advancement fails, record the mechanical gain and stop before human recognition.
