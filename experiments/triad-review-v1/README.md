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

## Metrics

The primary unit is a reviewer task / panel interaction.

For each policy record:

- total review tasks;
- review rounds / search replays;
- candidate exposures (`2` per pair, `3` per triad);
- pair relations explicitly elicited;
- number of triad vs pair tasks;
- exact final trajectory signature.

A triad policy is interesting only if it preserves the eager trajectory and materially reduces review tasks or rounds without an unreasonable increase in candidate exposure.

## Scope

Experiment only. No runtime queue schema, search policy, production `SKILL.md`, or representation-family change is made in v1.
