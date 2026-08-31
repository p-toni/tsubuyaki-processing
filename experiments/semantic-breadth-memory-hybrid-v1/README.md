# Semantic breadth + empirical-memory hybrid v1

## Question

The prior semantic experiment established two facts on its now-consumed arrow/key/mushroom/cloud/number-3/hourglass/bird/cactus suite:

1. target-free empirical action memory improves semantic navigation over a global route/action-mean controller;
2. replacing global breadth with a six-start local MPC beam still loses to breadth at equal 60-render budget.

This experiment tests the complementary architecture:

> **preserve most global breadth, then use empirical action memory only as a bounded exploitation suffix.**

No prior semantic cell is reused for tuning this architecture.

## Arms and exact logical render budget

Every arm receives exactly **60 logical renders per seed × concept**.

### `breadth60`

- 60 target-blind breadth states;
- generated as 10 interleaved rounds × 3 routes × {native, spectral};
- concept only enters after all 60 states exist, when exact semantic reranking chooses the finalist.

### `meanHybrid60`

- first 48 states are the exact first 8 interleaved breadth rounds: 8 × 3 × 2 = 48;
- concept enters only after those 48 renders exist;
- exact semantic reranking selects the six best valid prefix states as refinement parents;
- each parent receives the same 64 deterministic candidate actions;
- the frozen route/action-mean dynamics controller ranks all unrendered proposals by predicted distance to the target visual descriptor;
- top 12 unique proposals are rendered;
- finalist is exact semantic best over the 48-prefix + 12-refinement archive.

### `memoryHybrid60`

Identical to `meanHybrid60` except the frozen calibrated empirical action-memory controller ranks the same proposal pool.

The mean and memory arms therefore share:

- the same 48 rendered prefix;
- the same six target-selected parents;
- the same candidate action proposal set;
- the same exact 60-render budget;
- the same final semantic reranker.

Only the learned action-ranking mechanism differs.

## Frozen empirical memory

No memory training or configuration selection occurs on this semantic suite.

The workflow downloads the immutable target-free memory artifact from authoritative prior run `33347529752` and requires:

```text
k = 16
actionWeight = 4.0
shrinkage = 0.5
prior target-blind training run = 33336810605
```

The memory contains no semantic targets.

## Fresh semantic suite

Concepts, frozen before any run:

```text
glasses
cup
ladder
house
envelope
snowman
scissors
rocket
```

`targets.py` requires every raster fingerprint to be distinct from all earlier structural and semantic suites through the consumed arrow/key/... suite.

## Seeds

Excluded smoke only:

```text
735499999
```

Fresh semantic seeds:

```text
735400011
735400029
735400041
735400067
735400079
735400101
735400113
735400137
735400151
735400173
735400197
735400211
```

These identifiers were checked absent from repository history before preregistration.

## Primary estimands

Per seed, average across all eight concepts:

```text
memoryHybrid60 held-out target F1 - breadth60
memoryHybrid60 held-out target F1 - meanHybrid60
meanHybrid60 held-out target F1 - breadth60
```

Uncertainty is the one-sided 95% t lower bound across the 12 fresh seed means, matching the previous semantic experiment's aggregation unit.

Top-1 prototype recognition is a secondary discrete diagnostic.

## Preregistered empirical-memory gate

`EMPIRICAL_MEMORY_HYBRID_PROMISING` iff all hold:

1. complete hard-invariant 12 × 8 rectangle;
2. immutable memory configuration is identical across shards;
3. mean `memoryHybrid60 - breadth60` held-out F1 > `+0.010`;
4. one-sided 95% seed lower bound for that effect > `0`;
5. mean `memoryHybrid60 - meanHybrid60` held-out F1 > `+0.005`;
6. one-sided 95% seed lower bound for that effect > `0`;
7. memory held-out top-1 exceeds breadth by at least `0.05` absolute;
8. at least 5/8 concept means are positive memory vs breadth;
9. at least 5/8 concept means are positive memory vs mean;
10. every leave-one-concept-out memory-vs-breadth mean remains > `0`;
11. no concept contributes more than 50% of total positive memory-vs-breadth F1 gain.

These thresholds are intentionally smaller than the failed pure-MPC gate because this experiment allocates only 12/60 renders to the learned exploitation layer. The statistical lower-bound and cross-concept requirements prevent a tiny or single-concept gain from passing.

## Secondary generic-refinement gate

If the empirical-memory gate fails, `MEAN_REFINEMENT_HYBRID_PROMISING` may still pass iff:

1. complete hard-invariant rectangle;
2. mean `meanHybrid60 - breadth60` held-out F1 > `+0.010`;
3. one-sided 95% seed lower bound > `0`;
4. mean top-1 exceeds breadth by at least `0.05` absolute;
5. at least 5/8 concept means are positive;
6. every leave-one-concept-out mean remains > `0`;
7. no concept contributes more than 50% of positive gain.

That outcome would support breadth+local-refinement as an architecture but **not** a memory-specific advantage.

Otherwise the decision is `HYBRID_REFINEMENT_NOT_PROMISING`.

## Human-recognition boundary

No human-recognition package may be produced before the complete aggregate gate.

If one arm passes its mechanical gate, the workflow freezes one anonymous output per concept using preregistered display seeds and emits a sealed randomized key. The human task is forced-choice concept matching only; target silhouettes are not shown and artistic quality is not requested.

Recognition success requires at least **6/8 exact matches**. Mechanical semantic metrics remain search-research evidence; human recognition is a separate evidence layer.

## Blindness / stop rules

- Do not inspect or tune from seed-level semantic outcomes before the aggregate reducer finishes.
- Do not change targets, fresh seeds, 48/12 budget split, parent count, proposal count, memory configuration, or gates after the first non-smoke semantic shard starts.
- If the gate fails, the eight concepts and 12 seeds are consumed; do not retune this hybrid on them.
- A positive result authorizes the human-recognition boundary only; it does not by itself make the policy the creative default.
