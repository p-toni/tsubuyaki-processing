# Mutation scale schedule v1 — coarse-to-fine contrast

## Question

Global mutation scaling in #62 selected the current `m=1.0` baseline, but exposed a consistent aggregate tradeoff: larger steps improved independent/global-target recovery while reducing local-target recovery.

Can the same total search topology use radius more effectively by changing **when** large versus small steps occur rather than scaling every stage together?

## Distinct hypothesis

The current adaptive search uses:

```text
explore       1.00
round A       0.70
refine-local  0.55
refine-jump   1.20
```

Define one schedule-contrast parameter `q`:

```text
explore       1.00 * q
round A       0.70          # unchanged
refine-local  0.55 / q
refine-jump   1.20          # unchanged
```

Interpretation:

```text
q > 1  → wider first-stage basin exploration, tighter late local exploitation
q < 1  → tighter first-stage exploration, broader late local exploitation
q = 1  → exact current schedule
```

This is deliberately not another global multiplier. It reallocates mutation radius between the beginning and local-refinement end of the existing trajectory while leaving the intermediate round-A radius and explicit late escape-jump radius unchanged.

The legacy mutator's separate occasional `alpha` jitter remains unchanged because the production `scale` parameter does not govern it.

## Frozen schedule grid

Log-reciprocal pairs around the exact baseline:

```text
q = 2/3, 0.8, 1.0, 1.25, 1.5
```

`2/3 ↔ 1.5` and `0.8 ↔ 1.25` test approximately reciprocal schedule contrasts.

## Invariants

The experiment reuses the ordinary search engine and temporarily wraps only the active route mutator's incoming search scale. It does not change:

- common starts or target construction;
- RNG seed or random-number consumption;
- candidate IDs;
- stage ordering;
- parent-selection logic;
- frontier logic;
- selector;
- candidate budgets;
- representation grammar.

The wrapper recognizes only the four production search scales `1.0`, `0.7`, `0.55`, `1.2`; any unexpected scale fails closed.

Every tested schedule must finish with the same total candidate count as the ordinary baseline.

## Exact baseline replay gate

`q=1.0` must hash-identically replay an ordinary `run_search_from_starts(...)` invocation for every route×seed×target-regime calibration case.

The canonical signature includes candidate identity, lineage, genomes, phenotype fingerprints, stage decisions, provisional champion, frontier, allocations, and selection status.

## Objective benchmark

Reuse the frozen search-leverage mechanics:

- representations: `recurrence`, `orbit`, `family`, `sheet`, `filament`;
- three common valid starts per route;
- local held-out phenotype target + independent global target;
- target-distance selector;
- normalized improvement from the best common start;
- unchanged candidate budget.

This is objective search-mechanics evidence only, not artistic-quality evidence.

## Phase 1 — calibration

Use all already-consumed search-mechanics seeds:

```text
101, 103, 107,
109, 113, 127,
131, 137, 139,
149, 151, 157,
163, 167, 173,
179, 181, 191
```

90 route×seed blocks / 180 target-regime cases.

Select the `q` with highest mean combined local/global normalized improvement across all 90 blocks. Exact ties choose the schedule closest to `q=1`; if still tied, choose the smaller `q`.

Calibration makes no hypothesis claim.

## Phase 2 — untouched holdout

Reserved and still untouched after #62:

```text
193, 197, 199
```

Only the frozen selected schedule will be compared with exact `q=1.0` there. If calibration selects `q=1.0` itself, the holdout will not be consumed because strict selected-vs-baseline wins are impossible by construction.

## Holdout primary gate

A fresh route×seed counts only on a strict selected-schedule combined win over baseline.

```text
>=2/3 strict-win seeds → route supports schedule change
>=4/5 supporting routes → general schedule leverage supported
```

Classification:

```text
4–5 routes → general coarse-to-fine schedule leverage supported
3 routes   → mixed / representation-dependent schedule signal
0–2 routes → general schedule leverage not supported
```

## Boundary

Even a positive result authorizes only a later opt-in implementation/evidence experiment. It does not authorize artistic promotion, hard representation pruning, portfolio sufficiency claims, production/default changes, or `SKILL.md` changes.
