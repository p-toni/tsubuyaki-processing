# Selector frontier allocation v1

## Question

The spectral operator is now mechanically confirmed and human-supported at the generated-portfolio surface, while the current deterministic selector repeatedly collapses delivery to an unchanged incumbent when comparisons tie/defer.

Does preserving a **bounded plural local frontier across search stages** improve fresh search recovery under the same mixed operator and the same total compute, without degrading validity?

## Treatment boundary

Both arms use:
- routes: recurrence / orbit / filament;
- exact same hard-valid start per route/seed;
- `native-spectral-50-50-v1` only;
- 20 generated challengers per route: 4 explore + 4 roundA + 12 refine;
- same mutation scales and same random stream seed;
- same deterministic temporal selector;
- same frozen K=2 / amplitude-16 spectral control;
- no human or semantic target inside search.

Only tie/defer handling and subsequent parenting differ.

### Baseline: incumbent-only

Current `search_engine.run_search_from_starts` behavior. A challenger replaces the incumbent only on a clear selector win; ties/defer preserve the incumbent.

### Candidate: bounded frontier

After explore and roundA, use the existing `clear_loss_frontier` relation to preserve candidates the current champion cannot clearly beat. Keep at most four survivors in deterministic frontier order. The next stage distributes the fixed challenger budget round-robin across those survivors. Refinement uses the same 9 low-scale / 3 wide-scale split as the current runtime but distributes those attempts across the frozen roundA frontier.

No scalar beauty score, structural target, human label, semantic score, novelty score, or post-hoc oracle chooses frontier parents.

## Fresh population

Excluded smoke seed: `731999`.

Authoritative seeds:
`731003, 731019, 731037, 731051, 731069, 731087, 731101, 731123, 731141, 731159, 731177, 731191, 731207, 731219, 731233, 731251`.

The `731` seed namespace was absent from current repository code and commit messages before preregistration.

## Outcome construction

Only after both search trajectories for all three routes exist, score every valid generated archive against the already-frozen runtime structural target suite using the existing sparse-geometry recovery metric.

For each seed, average the 45 paired target cells (3 routes × 15 targets) to obtain one frontier-minus-incumbent recovery effect.

Also record:
- per-route paired recovery effects;
- valid generated challenger rates;
- final bounded-frontier size;
- final non-start frontier count;
- whether the baseline provisional champion remained the shared start.

The structural benchmark is experimental evidence only; it is not artistic authority.

## Preregistered decision

`FRONTIER_ALLOCATION_PROMISING` iff all are true:

1. mean seed-level frontier-minus-incumbent recovery > 0;
2. one-sided 95% bootstrap lower bound over seed-level effects > 0;
3. each route's mean paired recovery effect > 0;
4. frontier valid-challenger rate is no more than 0.05 below baseline;
5. median final non-start frontier count >= 2.

Otherwise: `FRONTIER_ALLOCATION_NOT_PROMISING`.

A positive result authorizes a fresh delivery-level artistic test. It does not authorize tuning on the consumed seeds or replacing the production selector directly.

A negative result ends this exact bounded-frontier parenting policy; do not tune its cap or allocation rule on the consumed outcomes.
