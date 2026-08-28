# Mutation scale v1 — global numeric step amplitude

## Question

Does the current adaptive search use a generally useful mutation amplitude, or can one global multiplier improve objective target recovery across representations without changing search topology?

This begins a new search-mechanics axis after the depth-vs-breadth topology line was closed in #61.

## Intervention

The production trajectory already supplies stage-specific numeric mutation scales:

```text
explore   1.00
round A   0.70
refine    0.55 or 1.20
```

For global multiplier `m`, the experiment temporarily wraps the active representation mutator:

```text
mutate(genome, rng, stage_scale)
→ mutate(genome, rng, stage_scale * m)
```

The wrapper is installed only for one experiment run and restored immediately afterward.

This changes only the scale-sensitive numeric step amplitude. The legacy mutator's separate occasional `alpha` jitter is intentionally unchanged because the existing `scale` argument does not govern it.

The intervention does **not** change:

- common starts;
- target construction;
- RNG seed or random-number consumption;
- candidate IDs;
- stage ordering;
- parent-selection logic;
- frontier logic;
- selector;
- nominal candidate budgets;
- representation grammar.

## Exact baseline replay gate

`m=1.0` is not merely a conceptual control. For every calibration route×seed×target-regime case, the wrapped run must exactly replay an ordinary `run_search_from_starts(...)` invocation.

The experiment hashes a canonical record containing candidate IDs, route/basin/stage/parent, genomes, phenotype fingerprints, stage decisions, provisional champion, final frontier, allocations, and selection status. Any `m=1.0` signature mismatch fails the block.

Every tested multiplier must also finish with the same total candidate count as the ordinary baseline. A budget/topology-count drift fails the block rather than being scored as a scale effect.

## Objective benchmark

Reuse the frozen search-leverage benchmark mechanics:

- five representations: `recurrence`, `orbit`, `family`, `sheet`, `filament`;
- three common valid starts per route;
- one local held-out phenotype target and one independent global target;
- target-distance selector;
- normalized improvement from the best common start;
- same search settings and candidate budget as the existing search-leverage benchmark.

This is objective search-mechanics evidence only, not artistic-quality evidence.

## Phase 1 — calibration

All seeds already consumed by prior search-topology research:

```text
101, 103, 107,
109, 113, 127,
131, 137, 139,
149, 151, 157,
163, 167, 173,
179, 181, 191
```

Across five routes: 90 route×seed blocks / 180 target-regime cases.

Frozen multiplier grid:

```text
0.50, 0.75, 1.00, 1.25, 1.50
```

Per route×seed:

```text
combinedScore(m) = mean(local normalized improvement, global normalized improvement)
```

Select the single multiplier with highest mean combined score across all 90 calibration blocks.

Exact numerical ties choose the multiplier closest to `1.0`; if two non-baseline multipliers are equally distant, choose the smaller multiplier. Calibration makes no hypothesis claim.

## Phase 2 — untouched holdout

Reserved before calibration:

```text
193, 197, 199
```

Only the frozen selected multiplier will be run against `m=1.0` on these seeds.

## Holdout primary gate

For each route×fresh seed, compare selected-scale combined improvement against the exact `m=1.0` baseline.

A seed counts only on a **strict** selected-scale win:

```text
selectedCombined > baselineCombined
```

Equality does not count.

```text
>=2/3 strict-win seeds → route supports global scale change
>=4/5 supporting routes → general mutation-scale leverage supported
```

Classification:

```text
4–5 routes → general global mutation-scale leverage supported
3 routes   → mixed / representation-dependent scale signal
0–2 routes → general global mutation-scale leverage not supported
```

## Secondary diagnostics

Record but do not allow them to override the primary gate:

- local/global mean recovery;
- valid yield;
- unique rendered phenotype rate;
- lineage depth of the objective winner;
- route-specific multiplier means;
- strict/non-worse blocks versus baseline;
- invalid candidate counts;
- calibration and holdout effect sizes.

## Boundary

Even a positive result authorizes only a later opt-in implementation/evidence experiment. It does not authorize artistic promotion, hard representation pruning, portfolio sufficiency claims, a production/default change, or `SKILL.md` changes.
