# Topology structural replay v1

## Purpose

Re-measure the exact six-experiment depth-vs-breadth topology arc after `search-measurement-audit-v1` falsified the original sparse-image pixel-MAE objective.

Historical chain:

```text
#56 search-leverage-v1
→ #57 route-conditional-policy-v1
→ #58 online-topology-probe-v1
→ #59 start-state-topology-v1
→ #60 stage1-response-topology-v1
→ #61 fixed-hedge-topology-v1
```

#61 explicitly closed the topology line using the cumulative negatives from this chain. This replay asks whether those qualitative conclusions survive when only the target-recovery measurement is changed.

## What changes

Replace only the historical `phenotype_distance(candidate, target_frames)` implementation with the `sparse-shape-v1` candidate metric qualified in #64:

```text
foreground support = pixel > 20
shape distance      = 1 - tolerant F1(radius=3px)
ink-mass error      = relative foreground ink-mass difference
distance            = 0.8 * shape + 0.2 * mass
```

## What does not change

For every historical simulator:

- target construction;
- common starts;
- route grammar;
- candidate generation;
- RNG namespaces and consumption;
- candidate IDs;
- mutation scales;
- parent-selection/search topology;
- candidate-evaluation budgets;
- local/global regimes;
- policy grids;
- calibration/holdout seed partitions;
- historical hyperparameter-selection rules and tie-breaks.

The historical simulator code is imported directly. The replay installs the structural metric at runtime rather than copying the policy implementations.

## No fresh evidence consumption

Every seed in this replay has already been consumed by the historical topology arc.

```text
#56 train/root        101,103,107
#57 holdout           109,113,127
#58 holdout           131,137,139
#59 holdout           149,151,157
#60 holdout           163,167,173
#61 holdout           179,181,191
```

Later seeds `193,197,199` and any new seeds are not touched.

This is diagnostic remeasurement, not fresh confirmation.

## Historical calibration rules preserved

### #57 route-conditional

Re-derive the route-only simple mapping from the structurally rescored #56 blocks using the exact historical training mechanism:

```text
simple policies = breadth vs fixed-parent
combined score = mean(local improvement, global improvement)
strict seed winner
>=2/3 training seed wins -> route mapping
```

The `>=2/3` mechanism is preserved here only because it defines the historical policy that must be replayed. It is **not** used as inferential evidence.

The universal simple control is whichever simple policy has more strict wins across the 15 training route×seed blocks. An exact total tie is recorded unresolved rather than broken post hoc.

### #58 online probe

Pilot grid `p={1,2,3,4}`. Select highest mean combined improvement over the original calibration blocks; exact tie chooses smaller `p`.

### #59 start-state selector

Use the original threshold grid and original start-concentration signal. Select highest mean combined improvement; exact tie chooses smaller threshold.

### #60 paid stage-1 response

Use the original threshold grid and exact paid explore-prefix signal. Select highest mean combined improvement; exact tie chooses smaller threshold.

### #61 fixed hedge

Use share grid `{0,.25,.5,.75,1}`. Select highest mean combined improvement; exact tie chooses the **larger adaptive share**, matching the historical rule.

## Replacement for the retired stochastic gate

The historical `2/3 seeds -> route support -> 4/5 routes` rule is **not** reused for confirmatory interpretation.

For each original holdout, preserve every continuous paired block effect:

```text
delta(route,seed) = selected_policy_combined_improvement
                  - adaptive_combined_improvement
```

Report:

- all 15 paired deltas;
- overall mean and median delta;
- equal-route mean delta per route;
- equal-seed mean delta per seed;
- local and global mean deltas where applicable;
- strict-win and non-worse counts only as diagnostics;
- calibration choice under MAE versus sparse-shape;
- sign of the historical aggregate mean effect versus sign of the structural replay effect.

No new significance or adoption threshold is introduced after seeing the data.

## Historical reference values

These are frozen before replay and used only for comparison:

```text
#58 selected pilot p       4
#59 selected threshold     0.5
#60 selected threshold     0.025
#61 selected hedge share   0.5

#57 historical route map
  recurrence fixed-parent-local
  orbit      fixed-parent-local
  family     independent-breadth
  sheet      fixed-parent-local
  filament   fixed-parent-local
```

Historical #61 holdout mean effect of selected hedge versus adaptive:

```text
+0.00744 combined normalized improvement
```

## Interpretation boundary

This replay can answer whether the **mechanical conclusions of the topology arc are robust to correcting the target metric**.

It cannot provide fresh confirmation because all seeds are consumed. A materially promising structural-metric result must be followed by a separately preregistered fresh-seed experiment before changing a default search architecture.

`sparse-shape-v1` itself remains a qualified research metric, not a production benchmark. Its 3px tolerance is known to be coarse and will require a sensitivity audit before any default adoption.

No result here authorizes artistic promotion, representation pruning, portfolio-sufficiency claims, production/default search changes, or `SKILL.md` changes.
