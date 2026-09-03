# Family projected-spectral portfolio v1 — result

**Decision:** `FAMILY_PROJECTED_SPECTRAL_PORTFOLIO_PROMISING`

This fresh equal-compute experiment tested whether the #131 family-law projected spectral operator remains useful when six of twelve native challenger slots are replaced by six projected-spectral slots while preserving an exact six-candidate native common prefix.

No artistic judgment was collected.

## Evidence

- 20 fresh `763xxx` master seeds × 15 fresh target cells = 300 paired cells.
- Both arms use exactly 12 challenger attempts from the same two hard-valid starts.
- Candidate arm = exact first 3 native challengers per start + 3 projected-spectral challengers per start.
- Projected operator remained K=2 / amplitude 16 with no retries or adaptive tuning.
- Authoritative workflow: `33705826152`, generation head `ed712f4d93b766c749039ddb081c64d66743fc74`.
- Summary artifact: `9875189890`, digest `sha256:61fa7a9d6e108074d07cf3f4a4e17e65e85615d1dca505bdb838c8ec22db17ae`.

## Primary result

- mixed-minus-native recovery mean: **`+0.0149285`**;
- one-sided 95% master-seed bootstrap lower bound: **`+0.0107941`**;
- native-only added recovery mean: `+0.0102336`;
- mixed added recovery mean: `+0.0251621`;
- meaningful wins: **211**;
- meaningful losses: **18**.

Every target-family mean was positive:

- disconnected-loops: `+0.0151952`;
- nested-loops: `+0.0120599`;
- concave-loops: `+0.0159154`;
- open-networks: `+0.0162823`;
- dense-regions: `+0.0151897`.

Every leave-one-family-out mean was also positive. The largest target-family share of positive advantage was only `22.19%`, well below the 50% concentration veto.

## Validity / family-law preservation

- baseline native: `239/240 = 99.58%` valid;
- mixed native prefix: `119/120` valid;
- projected spectral: **`120/120 = 100%` valid**;
- mixed total: `239/240 = 99.58%` valid;
- projected sibling-scale-law failures: **0**.

Thus the projected operator preserves the family law while adding substantial structural coverage under a fixed total evaluation budget.

## Gate resolution

All preregistered conditions passed:

- complete hard-invariant rectangle;
- exact equal budgets/common native prefix;
- mean delta >= `+0.005`;
- positive master-seed bootstrap lower bound;
- positive target-family and leave-one-family-out means;
- meaningful wins exceed losses;
- projected validity >=95%;
- zero sibling-law failures;
- mixed validity within 5pp of baseline;
- positive advantage not concentrated in one target family.

## Consequence

This result authorizes one narrow next layer: implement an **opt-in family-specific projected-spectral runtime portfolio and validate it on fresh replay evidence**.

It does not yet authorize:

- changing the default family runtime;
- applying projected spectral to `sheet`;
- artistic usefulness or reviewed-lineage authority;
- any ratio/K/amplitude retuning on consumed `763xxx` evidence.
