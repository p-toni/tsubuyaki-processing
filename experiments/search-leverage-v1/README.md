# Search leverage v1 — objective target recovery

## Question

Does the current staged adaptive search create **mechanical search leverage**, or is it mostly machinery around candidate generation?

This experiment deliberately avoids aesthetic judging. It turns search into an objective phenotype-recovery task with a hidden rendered target and compares equal candidate-evaluation budgets.

The result is evidence about **search topology**, not artistic quality.

## Why this experiment

Earlier artistic experiments established a coarse route-dependent pattern:

```text
recurrence: local depth can beat broader basin coverage
family:     independent breadth can find a better basin than depth
```

The hybrid experiment then found a more specific bottleneck:

```text
basin discovery is useful
but generic exploitation can mutate away from the niche that made the basin useful
```

Those results were artistically informative but selector-limited. Here we ask the underlying causal question with an objective target, so same-model aesthetic calibration is irrelevant.

## Routes and seeds

All five registered research representations are tested independently:

```text
recurrence
orbit
family
sheet
filament
```

Frozen seeds:

```text
101, 103, 107
```

Each route × seed block uses the same three valid initial starts for every policy.

## Objective

For candidate `c` and target `T`, distance is the mean absolute grayscale pixel difference across the matched temporal frames `t = [30, 90, 150]`, normalized to `[0,1]`.

```text
d(c,T) = mean_t mean_pixels |frame(c,t) - frame(T,t)| / 255
```

No diagnostic score, language model, semantic prior, or aesthetic selector enters the objective.

Invalid candidates cannot win.

## Two target regimes

### 1. Local / basin target

Start from common initial start #1 and apply six accepted route-native mutations sequentially on an isolated RNG stream at scale `0.65`.

The final valid descendant is the target.

This asks:

> Can sequential promotion compound local progress toward a reachable phenotype better than spending the same compute on one-step mutations from a fixed parent?

### 2. Independent / global target

Generate the first valid route-native seed from a separate deterministic RNG stream not used by the common starts or any search policy.

This asks:

> When the target lies in an independently sampled basin, how much does local adaptive exploitation cost relative to fresh basin discovery?

## Common adaptive workload

The current search engine runs one route at a time from the three common starts with a strict target-distance selector:

```text
starts                    3
explore_per_basin         4
roundA_per_survivor       3
total_extra_budget        8
```

Because the objective is strict, the staged search normally narrows to one basin before round A. The experiment measures the actual number of generated/evaluated non-start candidates, rather than assuming a fixed count.

## Equal-compute policies

Each baseline receives exactly the same number of **additional candidate evaluations** as the adaptive run actually generated.

### A. `adaptive`

Current `run_search_from_starts(...)` topology:

```text
several starts
→ per-basin exploration
→ promotion
→ route frontier
→ round A around survivor
→ promotion
→ refinement around promoted elite
```

### B. `independent-breadth`

Keep the common starts, then spend the entire incremental evaluation budget on independent route-native seeds from an isolated RNG stream.

Invalid samples still consume evaluation budget.

### C. `fixed-parent-local`

Choose the common initial start closest to the target once, then spend the entire incremental budget on one-step mutations of that **unchanged parent**.

Mutation scales cycle through the same broad/local scales present in current search:

```text
1.0, 0.7, 0.55, 1.2
```

No child becomes a parent. This is a strong no-promotion control for sequential depth.

## Primary metrics

Per route × seed × target regime × policy:

- best valid target distance after the full budget;
- normalized improvement over the best common initial start;
- whether the policy wins/ties the block;
- valid-candidate yield;
- number of exact unique rendered phenotype fingerprints;
- generated candidate count;
- for adaptive, winner distance and lineage depth.

Absolute target distance is interpreted only within a route/target block. Cross-route aggregation uses normalized improvement and win counts.

## Predeclared decision rules

The experiment has 15 independent route × seed blocks. The primary inference is **route-majority**, not a pooled 15-block average, so a representation with unusually easy or hard geometry cannot dominate the conclusion.

For each route, a directional result is supported when the same strict comparison wins in at least **2 of the 3 frozen seeds**. Exact ties do not count as wins.

### Local exploitation leverage

For each route, ask whether:

```text
adaptive best distance < fixed-parent-local best distance
```

Classify the route as supporting sequential-promotion leverage when adaptive wins at least 2/3 seeds.

Interpretation across routes:

```text
4–5 supporting routes → general exploitation leverage supported
3 supporting routes   → mixed / representation-dependent leverage
0–2 supporting routes → general exploitation leverage not supported
```

### Independent-basin discovery leverage

For each route, ask whether:

```text
independent-breadth best distance < adaptive best distance
```

Classify the route as supporting breadth leverage when independent breadth wins at least 2/3 seeds.

Interpretation across routes:

```text
4–5 supporting routes → basin discovery is a general first-order requirement
3 supporting routes   → mixed / representation-dependent discovery requirement
0–2 supporting routes → general breadth advantage not supported
```

### Combined architecture decision

The strongest evidence for the intended broad-to-deep architecture is predeclared as:

```text
local exploitation leverage supported on >=4/5 routes
AND
independent-basin breadth leverage supported on >=4/5 routes
```

If only the local condition passes, prioritize selective depth but do not assume current basin discovery is sufficient.

If only the global condition passes, prioritize basin discovery and question the value of chained exploitation.

If neither passes, the current staged topology lacks objective support under this benchmark and should be simplified or redesigned before adding more search machinery.

Mean normalized improvement, valid yield, unique-phenotype rate, winner lineage depth, and 15-block raw win counts are **secondary descriptive evidence**. They may explain a result but cannot override the route-majority decision rule.

## Predeclared interpretations

### Local target

If adaptive consistently beats fixed-parent-local at equal evaluations under the rule above, sequential promotion has objective exploitation leverage.

If fixed-parent-local matches or beats adaptive, promotion/path dependence is not buying enough local leverage and should be questioned before adding more exploitation machinery.

### Independent target

If independent breadth consistently beats adaptive under the rule above, basin discovery remains a first-order search requirement. That would reinforce the earlier family/breadth result without relying on aesthetic judgment.

If adaptive also performs strongly on independent targets, the current broad-to-deep topology may be more robust across basin structure than prior artistic evidence suggested.

### Combined

The desired evidence is not `adaptive wins everything`.

A healthy result may be:

```text
local target:       adaptive > fixed-parent
independent target: breadth  > adaptive
```

That would causally support the architecture:

```text
breadth for basin discovery
→ selective depth for basin exploitation
```

and focus the next experiment on **niche-preserving / trust-region exploitation** rather than more scheduler work.

## Boundary

This experiment changes no production code and cannot justify an artistic-quality claim. It is a search-mechanics benchmark only.
