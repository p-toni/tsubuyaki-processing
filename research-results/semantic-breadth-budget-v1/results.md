# Semantic breadth budget v1 — result

Decision: **SEMANTIC_BREADTH_BUDGET_NOT_SUFFICIENT**

The nested target-blind breadth curve improved held-out semantic recovery from 60 to 240 candidates, then plateaued in top-1 recognition despite continuing F1 gains.

- 60: top-1 53.125%, mean held-out target F1 0.57624
- 120: top-1 62.5%, mean F1 0.59576
- 240: top-1 67.5%, mean F1 0.60955
- 480: top-1 66.875%, mean F1 0.62101

No tested budget cleared the preregistered mechanical sufficiency gate. At 480, the weakest concepts remained letter-S 5%, spiral 35%, umbrella 50%, while diamond, lightning, sailboat, and leaf were 90–100%.

Interpretation: brute breadth is materially useful but is no longer the primary lever. Additional candidate count keeps improving proxy similarity without improving semantic identity. The next investment should test a target-agnostic learned model of the mathematical generator that can use cheap model inference to navigate a much larger unrendered candidate pool toward unseen external targets.

No human-recognition or artistic authority is granted by this result.
