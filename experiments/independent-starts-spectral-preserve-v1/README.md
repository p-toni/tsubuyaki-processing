# Independent starts spectral-preserve v1

## Question

#111 showed a strong equal-budget mechanical benefit from replacing R9-R12 with four independent one-shot starts, but #112 rejected that exact treatment artistically. A material confound is that R9-R12 are four of the six refine-stage **spectral** attempts, while prior fresh blinded evidence (#104) gave unanimous artistic support to the mixed native+spectral portfolio.

This experiment tests the strongest integration loophole:

> Can independent starts retain their mechanical basin-discovery value when they replace four **native** refine attempts instead, preserving the complete 10-evaluation spectral budget?

## Frozen arms

Both arms use one shared start, the exact current explore `N,N,S,S` and roundA `N,N,S,S`, the same deterministic selector, the same 20 generated-candidate budget, the same hard-valid archive, and the same target-blind three-item max-dispersion delivery rule.

### `baseline20`

Exact supported runtime:

- 10 native
- 10 spectral
- 0 restart

Refine schedule: `N,N,N,N,N,N,S,S,S,S,S,S`.

### `spectralPreserve20`

- exact same start;
- exact same first 10 generated candidates (explore + roundA + R1-R2);
- R3-R6 native refinements are replaced by four independent one-shot route-prior restarts;
- R7-R12 remain spectral;
- exactly 20 generated candidates;
- 6 native + 10 spectral + 4 restart;
- restarts never become parents and invalidity consumes the evaluation.

The treatment therefore preserves the full spectral evaluation count. Because R9-R12 in the baseline are anchored to the frozen pre-refine incumbent, their rendered phenotypes must also replay exactly in the treatment; this is a hard smoke invariant. R7-R8 may differ because their parent is the evolving champion.

## Fresh population

Excluded smoke: `751999`.

Authoritative seeds:

`751003, 751019, 751037, 751053, 751071, 751089, 751107, 751127, 751149, 751167, 751181, 751199, 751223, 751239, 751257, 751277, 751293, 751311, 751331, 751349`.

Before preregistration, these seeds and the `751` namespace were absent from repository code and commit messages.

## Mechanical authority

Structural targets are constructed only after both target-blind search archives and delivery trios are frozen. They remain experimental instruments, not artistic authority.

Use the same meaningful-effect margin frozen before the restart line:

`0.003255297955511336`.

`SPECTRAL_PRESERVE_RESTART_PROMISING` requires all:

1. complete 20-seed × 3-route × 15-target rectangle;
2. exact supported baseline replay in excluded smoke;
3. exact shared start and first 10 generated candidates;
4. exact baseline R9-R12 spectral phenotype replay inside treatment in smoke;
5. archive mean treatment-minus-baseline > meaningful margin;
6. one-sided seed bootstrap 95% lower bound on archive delta > 0;
7. every route archive mean > 0;
8. delivery mean treatment-minus-baseline > meaningful margin;
9. one-sided seed bootstrap 95% lower bound on delivery delta > 0;
10. every route delivery mean > 0;
11. treatment valid rate no more than 5 percentage points below baseline.

If the gate passes, authorize one fresh blinded artistic review only. Do not promote production mechanically.

If it fails, stop this exact spectral-preserving native-swap treatment. The next preregistered loophole class is **restart cultivation**, not position/ratio tuning on `751xxx`.

## Why this is not a post-hoc rescue of #112

The treatment is derived from independent evidence that predates #112:

- mixed native+spectral portfolios received unanimous fresh blinded artistic support in #104;
- #109's target-blind early novelty diagnostic selected spectral in all 60 route-seed prefixes.

No #112 per-block outcome chooses seeds, routes, target families, mutation scales, or the four native positions being replaced.
