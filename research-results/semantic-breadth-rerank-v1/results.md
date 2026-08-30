# Semantic breadth-rerank v1 — result

Decision: **`SEMANTIC_BREADTH_RERANK_NOT_PROMISING`**

Authoritative workflow: `33327932950`  
Aggregate artifact: `9736956876`  
Digest: `sha256:8380b65b0156025762086ecd7b2588ffa59a4f4ede7dd15e17fc12a2257dc43a`

At an identical 60-challenger budget, target-blind global breadth followed by one perceptual rerank materially outperformed the current target-aware adaptive local search:

- mean held-out target-F1 delta: `+0.046634706431492104`;
- one-sided 95% lower bound over 16 master-seed means: `+0.030232850784000533`;
- held-out top-1 fraction: adaptive `0.359375` -> breadth `0.515625` (`+0.15625`);
- pooled breadth validity: `0.9864583333333333`.

The preregistered absolute recognition gates still failed:

- overall breadth top-1 was below `0.60`;
- crown: `0.125`;
- letter-S: `0.0`;
- spiral: `0.25`;
- umbrella: `0.375`.

Interpretation: early adaptive exploitation is a genuine constrained-budget failure mode, but fixing it is not sufficient at 60 attempts. The next preregistered layer is a fresh nested breadth budget-response test rather than further selector tuning. This result does not establish human recognizability.
