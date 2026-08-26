# Paired Route-Aware Search Experiment

Status: frozen protocol before viewing results.

## Question

> Given a viable starting mathematical system, does the v0.8 route-aware search policy discover better brief-adherent challengers more efficiently than the previous generic structural search policy?

This experiment tests the **search policy**, not a new representation grammar.

## Starting points

Use 10 independently sampled viable incumbents for each of four routes:

1. repeated math family / plankton;
2. recurrence / living knot;
3. dense 2D sheet / membrane;
4. intentional 1D filament / ribbon.

Each incumbent is sampled deterministically from the frozen v0.6 mathematical vocabulary with route-specific validity/adherence constraints. The same incumbent is shared by all conditions in that paired trial.

Caveat: these are independent genotype draws from the frozen grammar, not 10 independent LLM generations. The experiment therefore measures search around diverse valid mathematical starts, not model one-shot variance.

## Conditions

### A — incumbent only

No mutation. This is the elite baseline.

### B — generic structural search

Parent is always retained. Generate structural + numeric mutations using the broad v0.7-style grammar without topology-specific mutation priorities beyond hard validity.

### C — v0.8 route-aware search

Parent is always retained. Mutation permissions depend on route:

- repeated family: structural + numeric search, but challengers must remain in the multi-instance family niche;
- recurrence: structural divergent search across recurrence roles, family count, deformation/projection and time coupling;
- dense sheet: emphasize projection/deformation family search while preserving true 2D sheetness and negative space;
- filament: local numeric search first; broad projection/topology mutation is disabled for this experiment.

## Elitism

A/B/C all contain the exact same parent. Search can improve or tie but can never force regression.

## Budgets

Use nested mutation prefixes:

```text
4 / 8 / 16 / 24
```

The first 4 candidates at budget 4 are the first 4 candidates at budget 24, etc. This supports best-of-budget curves without changing search randomness.

## Generation vs selection

Generation may use only:

- hard runtime / finite-coordinate validity;
- frozen brief-invariant gates;
- behavioral diversity for review-set reduction.

Do not optimize an aesthetic scalar during candidate generation.

For each condition/budget, compare the incumbent and challengers at matched times `t=3`, `7.5`, `15`.

Selection asks:

> Which brief-adherent candidate would you keep exploring?

Keep dimensions separate:

- brief adherence;
- aesthetic preference;
- mathematical leverage;
- temporal quality;
- distinctiveness;
- likely tweet viability.

## Primary outcomes

For every route and search budget record:

- probability search beats the incumbent;
- C vs B winner count;
- parent-retention / tie rate;
- best-of-budget improvement curve;
- task-drift rejection rate;
- hard failure rate.

## Interpretations

- C beats B at smaller budgets → route-aware search improves search efficiency.
- C and B converge only at 24 → routing helps mainly by reducing search cost.
- B > C on a route → v0.8 narrowed that route too aggressively.
- both mostly retain parent → representation/start quality dominates local search for that route.
- benefits vary strongly by route → preserve topology-specific search policy.

## Freeze rule

Do not change mutation operators, adherence gates, budgets or starting-genotype distribution after viewing results. Record defects as findings and fix them only in a subsequent experiment.