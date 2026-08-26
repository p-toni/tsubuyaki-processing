# Hybrid portfolio search protocol

Frozen before candidate generation.

## Question

Under the same 40-candidate budget, can a hybrid portfolio strategy outperform both pure depth and pure breadth by first discovering several mathematical basins and then exploiting the most promising one(s)?

## Baseline evidence

Merged breadth-vs-depth experiment:

- D1: 1 viable start -> 4 sequential rounds x10 = 40 challengers;
- B4: 4 viable starts -> 10 challengers each = 40;
- B8: 8 viable starts -> 5 challengers each = 40.

Observed:

- recurrence: D1 robustly beat B4/B8;
- repeated family: B4/B8 robustly beat D1, exact B4-vs-B8 unresolved.

## Routes

Use the same two route classes:

1. recurrence / living-knot-like system;
2. repeated mathematical family.

Fresh candidate draws are used for the hybrid conditions. Existing D1/B4/B8 results remain the comparison baseline.

## Fixed candidate budget

Each hybrid condition receives exactly 40 generated challengers per route.

### H1 — winner-take-most

```text
4 independent viable starts
x 5 exploratory challengers each
= 20 exploration candidates

rank the four basins artistically using their best exploration challenger + incumbent evidence

best basin
-> 20 exploitation challengers
```

### H2 — top-two portfolio

```text
4 independent viable starts
x 5 exploratory challengers each
= 20 exploration candidates

rank the four basins artistically

best basin  -> 10 exploitation challengers
second basin -> 10 exploitation challengers
```

The initial four viable starts are shared between H1 and H2. Exploration candidates are also shared so the only difference is exploitation allocation after the basin ranking.

## Basin selection

Basin ranking is frozen before exploitation generation.

Use visual + temporal judgment only. Character count and tweet viability are excluded.

For each basin inspect:

- incumbent;
- its five exploration challengers;
- representative times over the same route-appropriate horizon.

Record:

- basin ordering;
- selected best challenger within each basin;
- reason for selecting the top basin(s).

No scalar aesthetic fitness is used.

## Exploitation

Exploit around the best exploration challenger in the selected basin, not automatically around the original start.

Exploit with the same route-local mutation vocabulary used for ordinary progressive search. Preserve the incumbent/elite; a mutation may fail to improve.

H1 may use two sequential x10 exploitation rounds inside the winning basin if the first round produces a clear promoted elite. This still counts as 20 exploitation candidates.

H2 gives each selected basin exactly ten exploitation challengers; no budget can transfer between them after generation.

## Final comparison

For each route compare:

- merged D1 winner;
- merged B4 winner;
- merged B8 winner;
- H1 winner;
- H2 winner.

Primary question:

> Does either hybrid produce a clearly preferable brief-adherent artistic winner under the same 40-candidate budget?

Secondary questions:

- Did basin selection identify the basin that eventually produced the hybrid winner?
- Did H1 over-concentrate on one basin?
- Did H2 preserve useful optionality?
- Does the answer differ by route?

## Selector handling

Use the current selector only for coarse artistic decisions. Close rankings are treated as unresolved rather than forced into a precise total order.

The earlier same-model blinded retest showed only 2/3 pairwise agreement. Therefore this experiment may support large-margin architecture decisions, but not a continuous aesthetic fitness function.

## What this experiment cannot establish

It does not establish:

- the universal optimal number of starts;
- the universal exploration/exploitation split;
- automatic basin-selection quality across all routes;
- independent human/model agreement;
- mutation probabilities.

Do not turn `4 starts`, `20/20`, or `10/10` into production constants merely because they were used here.