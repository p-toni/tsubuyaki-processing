# Repertoire allocation confirmation v1

Decision: **CONFIRMED**

Fresh fixed-sample confirmation of the exact repertoire-preserving allocator piloted in #77. No mechanism, target portfolio, metric, route/basin budget, mutation law, or parent-selection rule changed.

## Evidence

- Workflow run: `33260916269`
- Aggregate artifact: `9718246741`
- Artifact digest: `sha256:363adbac4fc2927f9f6678bafd6845cba1a257958618294112e9bc0b2fc36251`
- Frozen population: 24 fresh master seeds x 5 fixed routes = 120 route-seed blocks
- Generated candidates per arm per block: 36
- No early stopping; no seed replacement.

## Preregistered gates

All passed:

1. complete hard-invariant rectangle: **PASS**
2. primary one-sided 95% Student-t lower bound > 0: **PASS**
3. every leave-one-route-out primary mean > 0: **PASS**
4. weakest-target robustness one-sided 95% Student-t lower bound > 0: **PASS**

Student-t: df `23`, one-sided 95% critical `1.713871527747048`.

## Primary target-recovery effect

- mean: `0.002554193852156981`
- median: `6.971485996293617e-05`
- SD: `0.005809630157145923`
- one-sided 95% lower bound: `0.0005217379616171756`
- LORO range: `0.0017450203441143756 .. 0.0031927423151962265`

Route means are diagnostic only:

- recurrence: `0.005131645197320155`
- orbit: `0.001841583472201424`
- family: `0.0`
- sheet: `6.852706935923473e-06`
- filament: `0.005790887884327402`

Largest absolute route-seed cell: `filament` / `31159` = `0.1062383606695798`. It does not override the master-seed inference.

## Weakest-target robustness

- mean: `0.0003744734639681187`
- median: `0.0`
- SD: `0.0008920878472658231`
- one-sided 95% lower bound: `6.238316716596803e-05`

## Interpretation

The confirmed mechanical claim is narrow but useful: under equal route budgets, equal basin budgets, equal whole-genome mutation law, and equal mutation event streams, preserving under-exposed `structural-v1` niche histories when selecting parents improves recovery of unseen structural targets relative to ordinary lineage deepening.

This confirms repertoire-preserving branching as a **mechanical search primitive**. It does not establish artistic preference, grant route authority, justify representation pruning/promotion, or by itself change `SKILL.md`. The next evidentiary layer is independent artistic replication of outputs produced under the frozen allocator.
