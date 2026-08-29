# Mutation scale v1 — global numeric step amplitude

## Question

Does the current adaptive search use a generally useful mutation amplitude, or can one global multiplier improve objective target recovery across representations without changing search topology?

This begins a new search-mechanics axis after the depth-vs-breadth topology line was closed in #61.

## Intervention

The production trajectory supplies stage-specific numeric mutation scales:

```text
explore   1.00
round A   0.70
refine    0.55 or 1.20
```

For global multiplier `m`, this experiment temporarily wraps the active representation mutator:

```text
mutate(genome, rng, stage_scale)
→ mutate(genome, rng, stage_scale * m)
```

The legacy mutator's separate occasional `alpha` jitter remains unchanged because the existing `scale` argument does not govern it.

The intervention does not change starts, target construction, RNG consumption, candidate IDs, stage ordering, parent-selection logic, frontier logic, selector, nominal candidate budgets, or representation grammar.

## Exact baseline replay gate

`m=1.0` must exactly replay an ordinary `run_search_from_starts(...)` invocation for every route×seed×target-regime calibration case.

The canonical signature includes candidate IDs, route/basin/stage/parent, genomes, phenotype fingerprints, stage decisions, provisional champion, final frontier, allocations, and selection status. Every multiplier must also finish with the same total candidate count as ordinary baseline.

## Objective benchmark

Reuse the frozen search-leverage benchmark mechanics:

- representations: `recurrence`, `orbit`, `family`, `sheet`, `filament`;
- three common valid starts per route;
- one local held-out phenotype target and one independent global target;
- target-distance selector;
- normalized improvement from the best common start;
- unchanged search settings and candidate budget.

This is objective search-mechanics evidence only, not artistic-quality evidence.

## Calibration preregistration

Consumed seeds only:

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

Select the multiplier with highest mean combined local/global normalized improvement across all 90 blocks. Exact ties choose the multiplier closest to `1.0`; if still tied, choose the smaller multiplier.

Fresh holdout seeds were reserved before calibration:

```text
193, 197, 199
```

The preregistered holdout gate requires strict selected-scale wins over exact `m=1.0` on at least 2/3 fresh seeds for a route, with general support requiring at least 4/5 routes.

## Calibration result

Workflow `33222085480` completed all 90 blocks / 180 target-regime cases. Every `m=1.0` wrapped trajectory exactly replayed the ordinary engine.

| multiplier | mean combined recovery | delta vs current |
| ---: | ---: | ---: |
| 0.50 | 0.072688 | -0.005424 |
| 0.75 | 0.075096 | -0.003016 |
| **1.00** | **0.078113** | **0** |
| 1.25 | 0.077420 | -0.000693 |
| 1.50 | 0.074508 | -0.003605 |

The preregistered winner is the exact current baseline, **`m=1.0`**. The strongest alternative, `m=1.25`, is about 0.89% lower on mean combined recovery.

A secondary tradeoff is visible rather than a globally better scale:

```text
          local      global
m=1.00   0.097655   0.058570
m=1.25   0.093397   0.061442
m=1.50   0.085006   0.064009
```

Larger numeric steps improve average global-target recovery while degrading local-target recovery. `m=1.25` strictly beats baseline on 54/90 individual calibration blocks but still loses on aggregate. This is evidence of heterogeneous scale preference, not evidence for a global replacement or post-hoc representation-specific tuning.

## Holdout decision

Fresh seeds `193,197,199` remain untouched.

Because the frozen selected multiplier is `m=1.0` itself, the preregistered selected-vs-baseline holdout comparison would be exact equality by construction, while the gate requires strict wins. Running those fresh seeds would therefore add no information and only consume holdout capacity.

No holdout was run.

## Decision

Retain the current global numeric mutation amplitude as the research baseline. Do not implement a global scale change and do not continue tuning the same multiplier grid on consumed seeds.

The next mutation-mechanics experiment should test a distinct hypothesis—most naturally the **schedule of scales across stages** or **mutation-operator diversity**—rather than another global multiplier.

## Durable evidence

- `calibration.json`
- `results.json`
- `results.md`
- `policy.py`
- `aggregate_calibration.py`

The temporary calibration workflow was removed after its completed run.

## Boundary

This is objective search-mechanics evidence only. It provides no artistic promotion authority, no hard representation-pruning authority, no portfolio-sufficiency claim, no production/default change, and no `SKILL.md` authority.
