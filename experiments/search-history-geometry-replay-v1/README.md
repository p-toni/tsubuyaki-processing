# Search history geometry replay v1

## Purpose

Reinterpret the complete recent search-mechanics arc after #69 qualified `sparse-geometry-v1` on an out-of-design metric holdout.

Historical scope:

```text
#56 search-leverage-v1
#57 route-conditional-policy-v1
#58 online-topology-probe-v1
#59 start-state-topology-v1
#60 stage1-response-topology-v1
#61 fixed-hedge-topology-v1
#62 mutation-scale-v1
#63 mutation-scale-schedule-v1
```

The original experiments used matched-frame pixel MAE, which #64 falsified for sparse line art. #65/#66 remeasure only #56–#61 with provisional `sparse-shape-v1`; #67 subsequently falsified that overlap-family metric's displacement sensitivity. Therefore #65/#66 are diagnostic archaeology, not the final methodological reinterpretation.

This experiment is the first coherent replay of #56–#63 under the qualified geometric research instrument.

## Metric

Use the exact #69 implementation, without copied or retuned weights:

```text
placement = explicit foreground-centroid displacement
shape     = radius-3 tolerant F1 after centroid alignment
extent    = foreground bbox width/height error
mass      = relative foreground ink-mass error

distance  = mean(placement, shape, extent, mass)
```

The replay installer imports the #69 metric implementation directly and replaces only the historical `phenotype_distance(...)` function resolved by target-distance selectors.

## No fresh search evidence

Every seed used here has already been opened by the historical search arc:

```text
101,103,107,
109,113,127,
131,137,139,
149,151,157,
163,167,173,
179,181,191,
193,197,199
```

No new seed is consumed.

The last three seeds were untouched by #62 but were later consumed by #63. They may therefore be used here only as retrospective diagnostic evidence, never as fresh confirmation.

## Fidelity contract

Only the target-recovery distance changes.

Preserve historical:

- target construction;
- common starts;
- route grammar;
- candidate generation;
- candidate IDs;
- RNG namespaces and draw behavior;
- mutation operators and scales;
- parent-selection/search topology;
- candidate-evaluation budgets;
- local/global regimes;
- hyperparameter grids;
- calibration/holdout partitions;
- historical tie-breaks and policy-selection rules.

Exact baseline-replay gates embedded in #62/#63 remain mandatory.

## Historical selection rules remain reconstruction rules, not inferential gates

Some experiments selected a policy/hyperparameter from consumed calibration data before evaluating a later block. Those original selection mechanisms are replayed exactly so the counterfactual historical policy can be reconstructed under the corrected metric.

Examples:

- #57 route mapping still uses its historical 2/3 calibration mechanism to define the route policy;
- #58–#61 use their original calibration grids/tie-breaks;
- #62 selects the multiplier with highest mean combined calibration improvement, ties nearest 1.0 then smaller;
- #63 selects the stage-schedule contrast with highest mean combined calibration improvement, ties nearest 1.0 then smaller.

Those rules do **not** become the new evidence aggregation framework.

## Effect framework

Interpretation follows `experiments/search-effect-framework-v1/README.md` from the roadmap work.

For each holdout contrast preserve every route×seed paired effect:

```text
delta[r,s] = selected_policy_score - baseline_score
```

For every complete seed:

```text
seed_effect[s] = mean over the five routes
```

The five routes are fixed strata. Seed effects are the stochastic replicate for uncertainty.

Report:

- all route×seed deltas;
- route means/medians/ranges;
- seed means/medians/ranges;
- overall mean and median seed effect;
- sample SD / SE across seed effects where meaningful;
- leave-one-seed-out and leave-one-route-out mean ranges;
- local/global decomposition when defined;
- strict-win/non-worse counts only as diagnostics;
- historical MAE selection/result versus geometry replay selection/result.

Consumed three-seed holdouts remain diagnostic; no replay interval can turn them into fresh confirmation.

## #56–#61 topology chain

Re-run the exact historical simulators with only `phenotype_distance` replaced.

Use the historical calibration/holdout partitions already encoded in those modules. Reconstruct the route/pilot/threshold/hedge selections from geometry-rescored calibration blocks and evaluate the original holdout seeds.

## #62 global mutation scale

Calibration population remains:

```text
101..191 (18 consumed seeds)
```

Run the full frozen multiplier grid:

```text
0.5, 0.75, 1.0, 1.25, 1.5
```

Re-select under geometry using the original calibration rule.

If geometry selects `1.0`, record the historical conclusion as mechanically surviving and do not manufacture a nonzero holdout contrast.

If geometry selects another multiplier, retrospectively evaluate that frozen geometry-selected multiplier versus `1.0` on `193,197,199`. These seeds are already consumed by #63, so this is diagnostic robustness evidence only.

## #63 stage-specific scale schedule

Calibration population remains:

```text
101..191
```

Full frozen contrast grid:

```text
2/3, 0.8, 1.0, 1.25, 1.5
```

Re-select under geometry using the original calibration rule and evaluate the geometry-selected contrast against `1.0` on the historically opened `193,197,199` holdout.

Do not force the historical MAE-selected `1.25` if geometry calibration selects something else; the point of this replay is to ask which historical conclusion survives when the instrument changes.

## Classification contract

For each historical conclusion assign one of:

```text
SURVIVES
REVERSES
UNRESOLVED / HETEROGENEOUS
```

### SURVIVES

The corrected metric leads to the same practical research conclusion and the continuous evidence does not expose a contradictory robust mechanism.

### REVERSES

The corrected metric selects/supports a materially different mechanism and the consumed holdout direction is coherent enough that the historical conclusion is no longer defensible even as a diagnostic.

### UNRESOLVED / HETEROGENEOUS

Calibration choice changes without coherent holdout evidence, route effects conflict, one seed/route dominates, or the evidence is too small/unstable to support either historical conclusion or its opposite.

No numeric significance threshold is invented after replay results.

## Selection of the next fresh experiment

After all eight conclusions are classified, choose **at most one** search contrast for fresh confirmation.

It must satisfy:

1. mechanism is distinct and interpretable;
2. geometry replay signal survives basic leave-one-seed/route influence checks;
3. effect is not explained by one representation or one extreme block;
4. a universal versus route-specific claim can be stated before fresh data;
5. randomness coupling can be made scientifically coherent for the contrast.

If no contrast meets those conditions, stop local search-mechanics tuning and move upward to representation/basin allocation as specified in the roadmap.

## RNG/counterfactual diagnostic

Classify every candidate next contrast as either:

```text
event-aligned
```

(candidate count/order/RNG draw identity preserved, e.g. pure scale transformations)

or

```text
control-flow-changing
```

(topology/survivor/budget/parent paths diverge).

A control-flow-changing contrast should not move directly to fresh confirmation under the stronger "common random numbers" interpretation. It first needs an experiment-local event-keyed randomness harness or an explicit design that treats shared seed only as scenario blocking.

## Boundary

Consumed-seed methodological reinterpretation only. No artistic promotion authority, representation pruning, production/default search change, benchmark adoption, or `SKILL.md` change follows directly from this replay.
