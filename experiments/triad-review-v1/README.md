# Dependency-safe triad review v1

## Purpose

Test whether one blinded three-candidate review can replace multiple pairwise review tasks **without changing the evidence-authoritative search result**.

The target is reviewer interactions, not a new artistic judge.

Current screened search exposes at most two unresolved pair tasks per replay. `route-balanced-review-v1` reduced starvation, but each task still asks about only one pair. In `explore` and `roundA`, the search often generates several fixed sibling challengers from one parent before any artistic promotion occurs. That creates a narrow opportunity to review three already-existing phenotypes together.

## Dependency boundary

Triad packing is allowed only when:

```text
A is the current unresolved incumbent
B and C are already-generated challengers
B.parent == A.id
C.parent == A.id
B/C stage ∈ {explore, roundA}
all three phenotypes are fixed before review
```

It is **forbidden in `refine`**.

Why:

```text
refine step 1 evidence
→ may replace the champion
→ refine step 2 may then mutate a different parent
→ its phenotype is not fixed before step 1 is resolved
```

Pre-reviewing that hypothetical second phenotype would break the seeded search trajectory.

Frontier comparisons are also left pairwise in v1. The first experiment intentionally tests the smallest dependency-safe surface.

## No hidden transitivity assumption

A triad decision is modeled as an explicit ordered partition, for example:

```text
B > A = C
```

That directly supplies all three pair relations inside the shown set:

```text
B > A
B > C
A = C
```

There are exactly **13** weak orders / ordered partitions for three labeled candidates.

The calibration oracle is still pairwise and may be non-transitive. A proposed triad is packed only if its three frozen pair outcomes correspond exactly to one of those 13 weak orders. Cycles or inconsistent tie structures fall back to ordinary pair tasks. The experiment therefore never repairs or assumes away non-transitivity.

The exhaustive algebra check confirms:

```text
13 / 27 complete A/B/C pairwise outcome matrices are total preorders
14 / 27 are non-rankable and must remain pairwise
```

## Frozen comparison target

To isolate the review format, this experiment reuses the exact synthetic pairwise oracle and eager trajectory signatures from `route-balanced-review-v1`:

```text
oracle: synthetic-route-scheduler-oracle-v1
seeds: 7, 19, 43
routes: recurrence, family, sheet
explore_per_basin: 4
roundA_per_survivor: 1
total_extra_budget: 3
```

Synthetic outcomes exist only to drive deterministic replay. They are **not artistic evidence**.

Every tested policy must reproduce the previously frozen eager trajectory signature exactly.

## Policies

```text
pair-k2
  two reviewer tasks per replay
  at most one task per hidden route/cross-route group
  one task elicits one pair relation

triad-k2
  same two-task / one-per-group scheduler
  dependency-safe, rankable sibling comparisons may become one triad task
  one triad task explicitly elicits three pair relations
  all other comparisons fall back to pair tasks
```

## Frozen promotion gate

This gate was committed before reading the calibration results.

Triad review advances to a runtime queue/prototype only if all of the following hold across the frozen seeds:

1. exact eager trajectory agreement on every seed;
2. lower mean review-task count than `pair-k2`;
3. mean candidate exposures do not increase;
4. mean review rounds do not increase.

## Result

All three frozen seeds preserve the exact eager final trajectory.

| seed | pair tasks | triad tasks | pair rounds | triad rounds | pair exposures | triad exposures | triad panels used |
|---|---:|---:|---:|---:|---:|---:|---:|
| 7 | 18 | 15 | 10 | 9 | 36 | 33 | 3 |
| 19 | 19 | 16 | 11 | 10 | 38 | 35 | 3 |
| 43 | 21 | 17 | 11 | 9 | 42 | 37 | 3 |
| **mean** | **19.33** | **16.00** | **10.67** | **9.33** | **38.67** | **35.00** | **3.0** |

Relative to pair-K2, dependency-safe triads reduce:

```text
review tasks        17.2%
review rounds       12.5%
candidate exposures  9.5%
```

The triad policy explicitly elicited more useful pair relations (`21, 22, 23`) than the pair baseline (`18, 19, 21`) while showing fewer total candidate instances to the reviewer. This happens because one three-candidate panel can safely settle the two incumbent/challenger relations plus the sibling relation that may become reachable after a promotion.

The frozen Pareto gate therefore **passes**.

## Decision

Advance to a separate runtime prototype for a blinded triad review queue and decoder.

Do not alter refine behavior, frontier semantics, evidence authority, or production `SKILL.md` as part of this experiment PR. The runtime implementation must preserve the existing pairwise evidence interface by decoding an explicit triad ranking into three ordinary phenotype-pair evidence records.

## Scope

Experiment only. No runtime queue schema, search policy, production `SKILL.md`, or representation-family change is made in v1.
