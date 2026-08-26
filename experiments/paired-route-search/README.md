# Paired Route-Aware Search Experiment

This experiment tests the v0.8 production thesis against the previous broad structural search policy while controlling for the starting mathematical system.

Read:

- `protocol.md` — frozen design written before the run;
- `results.md` — completed findings.

Core comparison:

```text
same viable incumbent
├── A: incumbent only
├── B: generic structural + parameter search, with elitism
└── C: v0.8 route-aware search, with elitism
```

Budgets are nested `4 / 8 / 16 / 24` mutations.

The main result is not that generic or route-aware search universally wins. Route-aware policies produce substantially more useful **early** mutations for sheet and filament routes, but fixed route restrictions can become too conservative at deeper budgets.

The current hypothesis after this run is therefore **progressive route-aware search**: use topology to choose the initial mutation prior, preserve the elite, then progressively unlock additional brief-preserving structural degrees of freedom only when the narrower search saturates.