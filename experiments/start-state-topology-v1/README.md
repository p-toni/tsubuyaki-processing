# Start-state topology selector v1 — basin concentration

## Question

Can a zero-extra-cost observable from the common starts tell us when adaptive sequential depth is worth using versus the simpler `p=4` online probe from `online-topology-probe-v1`?

The previous holdout isolated the remaining problem:

```text
breadth vs fixed-parent selection is nearly solved
adaptive vs simple selection is not
```

On untouched seeds `131,137,139`, the `p=4` probe had `83.3%` simple-arm choice accuracy and only `0.0100` regret to the full simple oracle, but `0.0584` regret to best-of-three. Adaptive dominated the local regime while the simple probe dominated the global regime.

This experiment asks whether the *shape of the objective over the existing common starts* is enough to decide which topology to use.

## Observable signal

For the three common starts, sort their objective distances to the current target:

```text
d1 <= d2 <= d3
```

Define basin concentration:

```text
C = (d2 - d1) / mean(d1, d2, d3)
```

Interpretation:

```text
large C  → one start is clearly ahead → a basin may be worth exploiting deeply
small C  → no start clearly dominates → simpler exploration may be preferable
```

The selector uses no route-specific rule, target-regime label, future candidate outcomes, semantic prior, or artistic judge.

## Candidate policies

The selector chooses between two complete equal-budget policies:

```text
adaptive      current staged run_search_from_starts topology
simple-probe  frozen p=4 breadth-vs-fixed probe from online-topology-probe-v1
```

Decision rule for threshold `τ`:

```text
if C >= τ: adaptive
else:      simple-probe
```

The concentration signal is computed from the common starts already present in every policy, so the selector consumes **zero additional candidate evaluations**.

## Phase 1 — threshold calibration

Calibration uses only seeds already consumed by prior experiments:

```text
101, 103, 107, 109, 113, 127, 131, 137, 139
```

Frozen threshold grid:

```text
0.0, 0.025, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.75, 1.0
```

`τ=0` is the explicit always-adaptive null policy.

For every route × seed, the selector may choose separately for the local and global target because it observes the current objective values but never the hidden regime label.

Per route × seed:

```text
combinedScore(τ) = mean(
  selected local normalized improvement,
  selected global normalized improvement
)
```

Select the threshold with highest mean combined score across all 45 calibration blocks. Exact numerical ties choose the smaller threshold.

Calibration makes no hypothesis claim.

## Phase 2 — untouched holdout

Reserved before calibration:

```text
149, 151, 157
```

The selected global threshold is frozen and used unchanged for all five routes.

## Holdout primary gate

For each route × holdout seed:

```text
selectorCombined = mean(selected local improvement, selected global improvement)
adaptiveCombined = mean(adaptive local improvement, adaptive global improvement)
```

A **strict win** requires:

```text
selectorCombined > adaptiveCombined
```

Exact equality does not count. This prevents an always-adaptive selector from passing trivially.

A route supports dynamic topology selection when the selector strictly beats adaptive on at least `2/3` fresh seeds.

Across routes:

```text
4–5 supporting routes → general start-state topology leverage supported
3 supporting routes   → mixed / representation-dependent signal
0–2 supporting routes → general start-state topology leverage not supported
```

Non-worse counts are secondary only.

## Secondary diagnostics

Record, but do not let override the gate:

- selector accuracy against the adaptive-vs-simple oracle per regime;
- simple-probe selection rate;
- local/global policy choice distribution;
- mean regret to adaptive-vs-simple oracle;
- mean combined improvement versus adaptive and simple-probe;
- route-specific concentration distributions.

## Boundary

This is objective search-mechanics research. Even a positive result would only justify a later opt-in implementation experiment. It cannot authorize artistic candidate promotion, hard representation pruning, portfolio sufficiency claims, production default changes, or `SKILL.md` changes.
