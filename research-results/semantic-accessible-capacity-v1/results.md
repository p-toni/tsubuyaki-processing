# Semantic accessible capacity v1 — result

Decision: **`ACCESSIBLE_SEMANTIC_CAPACITY_PRESENT`**

Authoritative workflow: `33323375003`  
Aggregate artifact: `9735785539`  
Digest: `sha256:5425876834eaadb67ce5a0b5e3b02a3eaf0641d2f3caae4bb0abe3b936cae25a`

The audit generated one target-blind archive per fresh seed: 1,536 candidates per seed, split equally across recurrence/orbit/filament and native/spectral variants. The same archive was scored only after generation against all eight semantic concepts.

Key result:

- 12 fresh seeds, 18,432 total attempts.
- 18,191 hard-valid candidates; pooled validity `0.9869249131944444`.
- Held-out requested-concept top-1 candidate found in `93/96` seed×concept cells (`0.96875`).
- Mean best held-out top-1 target F1: `0.6474042547710153`.
- Every concept met the preregistered >=50% top-1-found floor.
- Seven concepts were found on all 12 seeds; `letter-s` was found on 9/12 seeds.
- All preregistered gates passed.

Interpretation: the current intrinsic-1D grammar/runtime distribution has substantial **accessible semantic capacity** when explored broadly. This rules against the simple hypothesis that the requested forms are generally absent from the grammar. Combined with the 60-attempt steering result, the current bottleneck is search efficiency/retention under constrained budget. This result does **not** establish human recognizability; that authority remains with blinded human review after a constrained-budget search policy earns promotion.
