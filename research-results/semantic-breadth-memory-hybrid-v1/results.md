# Semantic breadth + empirical-memory hybrid v1 — result

**Decision:** `HYBRID_REFINEMENT_NOT_PROMISING`

Authoritative workflow run: `33349871777`  
Authoritative experiment head: `509550c3e722e0387bc9ee11a8f1b15c14eb719f`  
Aggregate artifact: `9743350229`  
Artifact ZIP digest: `sha256:74a8d04a40315c63b033d95cbbd41deba4ef9ba61a04b3d271751f8fb3b3fff6`

The complete fresh 12-seed × 8-concept rectangle passed every hard invariant. The experiment preserved 48/60 renders as target-blind global breadth, then spent 12/60 on local refinement. Mean and memory hybrids used the exact same prefix, six parents, 384 proposed actions, total render budget and final exact semantic reranker; only proposal ranking differed.

No seed-level semantic outcome was inspected before the aggregate reducer completed.

## Aggregate evidence

- empirical-memory hybrid vs breadth held-out F1: **+0.0135095**;
- one-sided 95% seed lower bound: **+0.0009165**;
- empirical-memory hybrid vs route/action-mean hybrid: **+0.00523284**;
- lower bound: **-0.00144417**;
- route/action-mean hybrid vs breadth: **+0.00827669**;
- lower bound: **-0.00578801**;
- held-out top-1: breadth **64.58%**, empirical memory **64.58%**, mean refinement **61.46%**;
- empirical memory vs breadth was positive on **6/8** concept means;
- empirical memory vs mean was positive on **5/8** concept means;
- every leave-one-concept-out empirical-memory-vs-breadth mean remained positive;
- no concept contributed more than 50% of positive empirical-memory-vs-breadth gain;
- mean overlap between the 12 proposals selected by memory and mean controllers was **56.86%**.

## Gate outcome

The empirical-memory gate failed only two preregistered requirements:

1. top-1 recognition did not improve over breadth by 0.05 absolute — it did not improve at all;
2. the direct empirical-memory-vs-mean one-sided seed lower bound was not positive.

The secondary generic mean-refinement gate also failed.

Therefore no human-recognition package was authorized or generated.

## Interpretation

This materially improves on the pure local-MPC result without passing the intended causal/semantic bar.

The previous experiment showed that replacing breadth with local planning loses too much coverage. Here, retaining 80% of the budget as global breadth and using empirical memory only for the final 20% **does produce a small, statistically positive continuous shape-matching gain over breadth**.

That supports a narrower statement:

> target-free empirical action memory is plausible as a bounded exploitation layer on top of global breadth.

It does **not** yet support the stronger statement that empirical memory itself caused the improvement. The direct paired comparison against the otherwise identical mean controller has the expected positive point estimate but insufficient precision. Nor did the improvement translate into better prototype top-1 identity.

## Next step and stop rule

Do not tune the 48/12 split, parent count, proposal count, memory configuration, or controllers on these consumed concepts/seeds.

Run **one** fresh higher-power causal replication of this exact architecture:

- fresh concepts and fresh seeds;
- same breadth anchor;
- same 48/12 split;
- same six parents and 64 proposals per parent;
- same frozen memory configuration;
- primary question: empirical memory vs the identical mean-refinement control;
- breadth remains an anchor, not a new optimization target;
- retain the existing recognition advancement bar separately.

If the direct memory-vs-mean effect does not reproduce with a positive lower bound, stop this semantic action-memory line. If it does reproduce but prototype identity still does not improve, record a mechanical continuous-matching gain but do not escalate to human recognition. Only a replicated controller effect plus the preregistered recognition advancement gate may open the human boundary.
