# Online topology probe v1 — calibrate then fresh holdout

## Question

Can a small amount of **online objective evidence** choose between simple breadth and local-search topologies early enough to beat or match the current staged adaptive search under the same total candidate-evaluation budget?

This follows two negative results:

1. `search-leverage-v1`: the universal staged topology was not generally supported as a representation-agnostic mechanism;
2. `route-conditional-policy-v1`: static representation identity did not generalize as a topology selector.

The remaining diagnostic opportunity is large: on the fresh route-policy holdout, best-of-three policy selection reached mean combined normalized improvement `0.1154`, versus `0.0649` for the frozen route map and `0.0769` for adaptive.

This experiment asks whether part of that instance-level gap is recoverable **online**, without a route policy map or knowledge of how the hidden target was generated.

## Policy: probe then commit

The two simple arms are:

```text
independent-breadth
fixed-parent-local
```

For one target and total incremental evaluation budget `B`:

1. evaluate the first `p` breadth candidates;
2. evaluate the first `p` fixed-parent candidates;
3. compare each arm's best objective distance after its pilot against the same common starts;
4. choose the arm with lower best distance;
5. on an exact numerical tie, choose `fixed-parent-local`;
6. spend the remaining `B - 2p` evaluations continuing the chosen arm's deterministic candidate sequence;
7. the final candidate pool contains both pilots plus the chosen continuation.

Thus the policy always consumes exactly `B` incremental candidate evaluations.

The breadth and fixed-parent sequences use the same deterministic RNG streams as the full simple baselines from `search-leverage-v1`. The probe sees only the prefix it paid for before choosing an arm. The later candidates do not influence the arm choice.

## What the selector may observe

The selector may observe the objective values of candidates it actually evaluated during the pilot. This is analogous to any online optimizer observing its search objective.

It does **not** receive:

- target-regime label (`local` vs `global`);
- future candidate outcomes;
- route-specific policy mapping;
- holdout performance.

The benchmark objective is still rendered target distance. This is search-mechanics evidence, not a claim that an artistic objective is equally observable or authoritative in deployment.

## Phase 1 — pilot-size calibration

Pilot size is a hyperparameter and is calibrated only on seeds that have already been used by earlier experiments:

```text
101, 103, 107, 109, 113, 127
```

Candidate pilot sizes are frozen before calibration:

```text
p ∈ {1, 2, 3, 4}
```

For every route × calibration seed, evaluate all four simulated probe sizes under identical targets and total budgets.

For each `p`, define per-block score:

```text
combinedScore(p) = mean(
  local probe normalized improvement,
  global probe normalized improvement
)
```

Calibration selects the `p` with the highest mean combined score across all 30 route × seed blocks. Exact numerical ties choose the smaller `p`.

No hypothesis claim is made from calibration. Its only output is the frozen pilot size for Phase 2.

## Phase 2 — untouched holdout

The holdout seeds are declared **before calibration** and must not be run until the calibration result is frozen:

```text
131, 137, 139
```

The selected pilot size is then used unchanged for all five routes and both target regimes.

## Shared benchmark mechanics

Reuse `search-leverage-v1` exactly for:

```text
routes                     recurrence, orbit, family, sheet, filament
common starts              3
matched frames             30, 90, 150
local target steps         6 accepted mutations
local target scale         0.65
explore_per_basin          4
roundA_per_survivor        3
total_extra_budget         8
objective                  normalized rendered grayscale distance
```

For each route × seed × regime, retain these diagnostics under the same total incremental evaluation budget:

```text
adaptive
full independent-breadth
full fixed-parent-local
probe-then-commit
```

Invalid candidates consume evaluation budget.

## Holdout primary gate

Per route × holdout seed:

```text
probeCombined = mean(local probe improvement, global probe improvement)
adaptiveCombined = mean(local adaptive improvement, global adaptive improvement)
```

A holdout seed is non-worse when:

```text
probeCombined >= adaptiveCombined
```

Exact equality counts as non-worse because probe-then-commit is a simpler topology; any loss greater than numerical epsilon fails the seed.

A route supports replacement on at least `2/3` fresh seeds.

Across routes:

```text
4–5 supporting routes → general online-simple replacement supported
3 supporting routes   → mixed / representation-dependent online leverage
0–2 supporting routes → general online-simple replacement not supported
```

Strict wins are recorded separately.

## Secondary diagnostics

Record, but do not let override the primary gate:

- pilot arm-choice accuracy against the full simple arm that ultimately performs better;
- mean regret to the per-regime full-simple oracle;
- mean regret to best-of-three (`adaptive`, breadth, fixed);
- local/global means;
- arm-choice distribution;
- valid yield and rendered-phenotype uniqueness.

The simple oracle is diagnostic only and sees final outcomes unavailable to the online selector.

## Decision boundary

If the untouched holdout supports probe-then-commit on at least `4/5` routes, a later implementation experiment may introduce it behind an opt-in research flag and test it with real phenotype evidence.

If it fails, the instance-level oracle gap is not recoverable by this minimal pilot mechanism; the next step should investigate richer observable search-state signals, not add more stages to the current adaptive topology.

No result here authorizes artistic candidate promotion, hard representation pruning, portfolio sufficiency claims, or production `SKILL.md` changes.
