# Sampling-invariance search v2 — result

## Decision

**SPECTRAL_HEDGE_SEARCH_NOT_PROMISING**

Authoritative workflow: `33284874665`  
Aggregate artifact: `9724099800` (`sampling-invariance-search-v2-summary`)  
Artifact digest: `sha256:95a2f7d7ddd90dbeb98273abb8203d923fcc61230665107c399e0ea61548c7fa`

## Frozen experiment

- 20 consumed master seeds x 15 fresh targets = 300 cells.
- 20 evaluations per policy/target.
- Shared first 12 evaluations: four valid starts + eight independent discovery draws.
- Final eight evaluations: pure breadth vs top-one geodesic exploitation vs top-two 4/4 basin hedge.
- Frozen projective-geodesic angles: `0.04, 0.08, 0.16, 0.32` radians.
- Corrected `v2-dense-3` before any consumed execution after the first target-contract run failed at support 41,411 > 40,000. The authoritative target suite passed the full validity/disjointness gate before smoke and consumed execution.

## Gate result

| Gate | Result |
|---|---|
| Complete hard-invariant rectangle | PASS |
| Mean top2 vs breadth > 0 | PASS |
| Every leave-one-family-out top2 vs breadth > 0 | PASS |
| Mean top2 vs top1 > 0 | **FAIL** |
| Every leave-one-family-out top2 vs top1 > 0 | **FAIL** |
| >=30% cells top2 vs breadth > 0.005 | PASS |
| Top2 valid yield >=0.95 | PASS |
| No family >60% positive contribution | PASS |

## Primary effects

- `top1_vs_breadth`: mean **0.006988**, median 0.006313, SD 0.014190.
- `top2_vs_breadth`: mean **0.003788**, median 0.003400, SD 0.013063.
- `top2_vs_top1`: mean **-0.003200**, median -0.001370, SD 0.009992.
- Meaningful top2-vs-breadth fraction (>0.005): **0.417**.
- Second-basin final-winner fraction: **0.227**.
- Top1 and top2 exploitation valid yield: **1.0**.

## Family pattern

Top1 beats breadth on average in all five target families. Top2 also beats breadth in all five families, but top2 is worse than top1 in all five family means. The largest positive top2-vs-breadth contribution is disconnected loops at 0.288, well below the 0.60 concentration ceiling.

## Interpretation

The preregistered **second-basin hedge mechanism is rejected**. Preserving fixed exploitation budget for basin #2 does not add robustness; it consistently dilutes the stronger top-one allocation.

The diagnostic `hybrid-top1` result is nevertheless a materially new signal: after shared breadth discovery, eight calibrated local geodesic evaluations around the best discovered basin beat eight additional independent breadth draws by about 0.007 recovery on average. This cannot override the v2 gate or be promoted on the consumed v2 sample. It can only motivate a new fresh hypothesis test.

## Next step

Do not tune the 12/8 split, basin count, or angle schedule on these outcomes. Freeze exact `hybrid-top1` as a new hypothesis and test it on a new deterministic target suite and fresh master seeds. No artistic admission follows from v2.
