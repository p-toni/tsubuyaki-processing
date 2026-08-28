# Search leverage v1 — result

Source workflow run: `33210657342`

Execution head: `3f8317af2c9b1e384f5a73bf763483da190dcec8`

Main at execution: `bacde5fe9f4cc3925dfc01fd83c46a6cfbce1fe3` (includes the completed #55 scheduler stress/cache work through the PR merge ref).

All 15 route × seed blocks completed successfully. The preregistered aggregate job also completed successfully. Scientific hypothesis outcomes were not wired to CI pass/fail; the aggregate job checked only completeness and internal consistency.

## Primary result

| route | adaptive > fixed-parent on local target | sequential-promotion support | breadth > adaptive on global target | basin-discovery support |
| --- | ---: | --- | ---: | --- |
| recurrence | 1/3 | no | 0/3 | no |
| orbit | 0/3 | no | 2/3 | yes |
| family | 1/3 | no | 3/3 | yes |
| sheet | 2/3 | yes | 1/3 | no |
| filament | 2/3 | yes | 2/3 | yes |

Predeclared route-majority classification:

```text
local sequential-promotion support     2/5 routes
→ general exploitation leverage not supported

global independent-breadth support     3/5 routes
→ mixed / representation-dependent basin-discovery requirement

combined architecture
→ current staged topology not generally supported
```

The intended general broad-to-deep claim required both local exploitation and global breadth support on at least 4/5 routes. Neither condition passed.

## Secondary evidence

Mean normalized improvement over the strongest common initial start:

```text
local target
  fixed-parent-local      0.1157
  adaptive                0.0816
  independent-breadth     0.0185

global target
  independent-breadth     0.0788
  adaptive                0.0546
  fixed-parent-local      0.0352
```

These descriptive means agree with the primary direction but do not override the preregistered route-majority rule.

Adaptive search did generate real multi-step lineages (`local mean depth 2.27`, `global mean depth 3.47`), so the negative local result is not explained by the adaptive policy failing to chain mutations at all. Chaining happened; it simply did not beat the strong fixed-parent local control consistently across representations.

Valid-yield and exact rendered-phenotype diversity were near saturation for all three policies, so the result is also not primarily an invalid-candidate or duplicate-collapse artifact.

## Interpretation

The experiment rejects the idea that the current staged search should be treated as a representation-agnostic default purely because it combines breadth and depth.

The evidence is instead route-conditional:

- `sheet` and `filament` show repeatable objective benefit from sequential promotion on local targets;
- `orbit` and `family` show repeatable benefit from independent basin discovery on global targets;
- `filament` supports both mechanisms under the frozen rule;
- `recurrence` supports neither general comparison in this benchmark and is a useful warning against extrapolating from earlier route-specific artistic results.

This does **not** establish that a specific route should permanently use a specific policy. It establishes that one universal staged topology is not justified by this benchmark.

## Decision

Do not add more generic exploitation machinery (including trust-region/niche-preserving refinement) on top of the current universal staged topology yet.

The next search-quality experiment should test a **simpler route-conditional policy layer** against the current adaptive topology under held-out objective targets. The key question is whether choosing among simple breadth, fixed-parent local, and chained depth policies by representation captures the useful leverage with less machinery and without an oracle that sees the target.

No production/default search behavior changes are authorized by this experiment alone.

## Evidence boundary

This is objective search-mechanics evidence only. It contains no human or independent-model artistic-quality evidence and cannot authorize artistic candidate promotion, representation pruning, or claims of portfolio sufficiency.

Machine-readable aggregate results are frozen in `results.json`. The complete 15 raw block artifacts are retained in source workflow run `33210657342`; `reproduce.py` deterministically regenerates them from the frozen route/seed design.
