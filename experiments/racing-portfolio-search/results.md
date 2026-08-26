# Uncertainty-aware racing portfolio search — results

## Executive result

The final blinded human comparison is mixed:

```text
recurrence: RACE > H1
family:     H2 > RACE
```

So uncertainty-aware racing is **useful but not universally superior** under the fixed 40-candidate budget.

Its value is delayed commitment:

```text
keep several basin representatives alive
-> remove only clear losses
-> use tie/defer when the selector margin is insufficient
-> concentrate only after evidence becomes decisive
```

Its cost is an **optionality tax**: budget spent preserving an uncertain basin is budget not spent exploiting the eventual leaders. The family route exposes this directly.

This experiment reuses the exact exploration population from the merged hybrid-portfolio experiment, so the primary causal comparison is allocation policy rather than candidate-sample luck.

## Selector semantics

This run does not force a total order.

Allowed decisions:

```text
clear win
clear loss
tie / insufficient margin
```

Budget moves only after a clear-margin decision.

## Recurrence

Shared exploration: 20 candidates across four basins.

```text
survive after exploration: basin 1, basin 3
clear loss: basin 2, basin 4

round A:
basin 1 +4
basin 3 +4

round B after basin 1 clear win:
basin 1 +12
```

Final racing representative: `RR-B-B1-12`.

Primary causal comparator: H1 from the same shared exploration population.

Blinded mapping and human result:

```text
A = H1
B = RACE
human = B
=> RACE > H1
```

This is positive evidence that delayed commitment can beat early winner-take-most concentration on a recurrence landscape.

## Repeated family

Shared exploration: 20 candidates across four basins.

```text
survive after exploration: basin 4, basin 1, basin 3
clear loss: basin 2

round A:
basin 4 +4
basin 1 +4
basin 3 +4

then:
basin 3 = clear loss
basin 4 ~= basin 1 = tie/defer

round B:
basin 4 +4
basin 1 +4
```

Final racing representative: `FR-B-B4-3`.

Primary causal comparator: H2 from the same shared exploration population.

Blinded mapping and human result:

```text
A = RACE
B = H2
human = B
=> H2 > RACE
```

This exposes the optionality tax. H2 already funded the correct top-two pair with ten candidates each. Racing spent four additional candidates on basin 3 before enough evidence existed to discard it, leaving less exploitation budget for basins 4 and 1.

## What is supported

1. **The number of live basins should be an outcome, not a fixed K.**
2. **Tie/defer is operationally useful.**
3. **Route behavior differs materially.**
4. **Adaptive allocation can beat a fixed hybrid on some landscapes.**
5. **Optionality has an opportunity cost.**

## What is not supported

Do not encode RACE as a universally superior production policy.

One paired block cannot establish universal values for number of starts, challengers per racing round, confidence threshold, or exploration/exploitation ratio.

## Relation to the trust-region pilot

Independent human ranking preferred:

```text
recurrence: paired D1 > generic H1 > trust-region
family:     paired B4 > trust-region > generic H2
```

Therefore tight basin locking is not supported.

The more defensible search architecture is:

```text
portfolio of representatives
-> coarse clear-loss elimination
-> explicit tie/defer
-> adaptive evidence allocation
-> local refinement without permanently forbidding structural escape
```

## External filament replication

An external evaluator reported a successful independent v0.14.1 filament run. Its qualitative jump came from structural `phase-relation` coupling after numeric search saturated; the winning property was temporal; and successful filament occupancy remained below 2%. These observations support structural escape routes and keeping occupancy diagnostic-only on filament, but are not causal evidence for racing.

## Production recommendation

**No production policy change from this experiment alone.**

The allocator research has answered the higher-level question well enough to proceed:

> search should preserve uncertainty explicitly rather than force early total rankings, but adaptive preservation must compete against its own opportunity cost.

That principle belongs in the next executable autonomous-search prototype as logged behavior, not as a hard-coded racing schedule.

## Reproducibility

`reproduce.py` imports the merged hybrid experiment's deterministic generator, reconstructs the exact shared 4x5 exploration population, then applies the racing-specific RNG seeds and recorded parent decisions.
