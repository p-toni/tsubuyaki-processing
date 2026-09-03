# Family projected-spectral runtime replay v1 — result

**Decision:** `FAMILY_PROJECTED_SPECTRAL_RUNTIME_PROMISING`

The #131/#133 family-law projected spectral operator survives integration into the actual adaptive runtime at exact equal compute.

No artistic judgment was collected.

## Frozen evidence

- 20 fresh `764xxx` master seeds × 15 fresh targets = 300 paired cells.
- Both arms start from the exact same hard-valid family phenotype.
- Both arms use the real `DeterministicTemporalSelector` and adaptive search loop.
- Baseline: 20 native challengers.
- Candidate: 10 native + 10 family projected-spectral challengers.
- K=2 / amplitude 16; no retries, target-aware generation, adaptive amplitude, or checker tuning.
- Full hard-valid archives were fixed before target construction/scoring.
- Authoritative workflow: `33706767366`, generation head `7556408dea5f86963e1dcb2efc304f6780724764`.
- Summary artifact: `9875519068`, digest `sha256:ac498f5e7b5e70e50549ca35ad07debce613828a74e9231997b44c372fa5c57a`.

## Runtime result

- mixed-minus-native recovery mean: **`+0.0240066`**;
- one-sided 95% master-seed bootstrap lower bound: **`+0.0187733`**;
- meaningful wins: **251**;
- meaningful losses: **14**.

Every target-family mean was positive:

- disconnected-loops: `+0.0234536`;
- nested-loops: `+0.0232458`;
- concave-loops: `+0.0196102`;
- open-networks: `+0.0242134`;
- dense-regions: `+0.0295098`.

Every leave-one-target-family-out mean was also positive. The largest share of total positive advantage from one target family was `24.33%`, below the frozen 50% concentration veto.

## Validity and defining-law preservation

- native runtime: **400/400 = 100%** valid;
- mixed runtime: **400/400 = 100%** valid;
- projected-spectral challengers: **200/200 = 100%** valid;
- projected sibling-scale-law failures: **0**.

The excluded smoke independently proved:

- omitted portfolio and explicit `native-only` are exact runtime replays on family;
- projected runtime is deterministic;
- family candidate allocation is exactly 10 native + 10 projected-spectral;
- `sheet` remains native-only under the family mode;
- existing intrinsic-1D spectral mode remains 10 native + 10 generic spectral;
- the runtime family projection matches the frozen #131 operator;
- fresh runtime targets are fingerprint-disjoint from all prior sampling/material-control target suites through #133.

The complete prototype regression suite also passed with the new implementation.

## Gate resolution

All preregistered gates passed:

- complete 300-cell hard-invariant rectangle;
- exact 20-vs-20 budgets and projected allocation;
- shared starts exact;
- mean delta >= `+0.005`;
- positive master-seed bootstrap lower bound;
- positive target-family and leave-one-family-out effects;
- meaningful wins exceed losses;
- projected validity >=95%;
- zero sibling-scale-law failures;
- mixed validity within 5pp of baseline;
- positive advantage not concentrated in one target family.

## Authority consequence

The new runtime mode

```text
native-family-projected-spectral-50-50-v1
```

is mechanically validated for **opt-in `family` use**.

This result does not authorize:

- changing the default away from `native-only`;
- applying projected spectral to `sheet`;
- changing the existing intrinsic-1D spectral mode;
- artistic usefulness or reviewed-lineage promotion.

Visual review remains paused.
