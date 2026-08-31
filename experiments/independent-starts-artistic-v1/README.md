# Independent starts artistic v1

## Question

#111 established that, at exactly equal 20-candidate compute, replacing baseline refine attempts R9–R12 with four independent one-shot route-prior starts materially improves both full-archive structural recovery and the promoted target-blind max-dispersion delivery surface.

This experiment asks the final authority question before production promotion:

> Does that equal-budget restart-tail treatment also produce a stronger **human-valued portfolio of mathematical forms** than the current runtime?

Structural recovery is not artistic authority. This review is therefore fresh, blinded, and uses no structural target in presentation or selection.

## Frozen arms

For each fresh route/seed block, construct both arms with the already-tested #111 implementations.

### `baseline20`

Exact current runtime:

- one shared hard-valid route-prior start;
- 4 explore + 4 roundA + 12 refine attempts;
- exactly 20 generated candidates;
- 10 native + 10 spectral;
- single-incumbent parenting;
- complete hard-valid generated archive preserved.

### `restartTail20`

Equal-budget treatment:

- exact same shared start;
- exact same first 16 generated candidates phenotype-for-phenotype;
- baseline R9–R12 replaced by four independent one-shot route-prior starts;
- exactly 20 generated candidates;
- 10 native + 6 spectral + 4 restart;
- each restart is evaluated once, with no retry and no parenting between restarts;
- complete hard-valid generated archive preserved.

Both arms use the exact same promoted target-blind **three-item max-dispersion delivery shortlist**.

No structural score, semantic target, model judge, human label, proxy champion, or post-hoc oracle chooses the three displayed candidates.

## Fresh population

Excluded smoke: `748999`.

Review seeds:

- `748003`
- `748021`
- `748043`
- `748063`

Routes:

- recurrence
- orbit
- filament

This yields 12 authoritative A/B blocks.

Before preregistration, all five seeds were absent from repository code and the `748` namespace was absent from repository commit messages.

## Presentation contract

Each A/B side shows exactly three max-dispersion archive candidates. Each candidate is rendered at:

- `t=30`
- `t=90`
- `t=150`

A/B assignment is deterministic from a frozen blind salt and block ID. The reviewer artifact contains no route, seed, arm identity, candidate IDs, genomes, structural scores, or A/B key.

The key is uploaded as a separate artifact and must remain unopened until all 12 judgments are fixed.

Fail closed before review if any block violates:

1. exact equal 20-candidate budgets;
2. exact shared start and first-16 phenotype prefix;
3. at least 12 hard-valid generated candidates in each arm;
4. exactly three distinct displayed phenotypes per side;
5. A and B displayed portfolios are not phenotype-identical.

## Human question

For each block answer one of:

- `A>B`
- `B>A`
- `equivalent`
- `unreviewable`

using only:

> **Which side contains the stronger portfolio of mathematical forms worth keeping or developing further?**

## Preregistered artistic gate

Define each reviewable block's treatment preference after unblinding:

- `+1` if `restartTail20` is preferred;
- `-1` if `baseline20` is preferred;
- `0` if equivalent.

`INDEPENDENT_STARTS_ARTISTIC_SUPPORT` requires all of:

1. at least 9/12 blocks reviewable;
2. total restart-tail-minus-baseline net preference > 0;
3. every leave-one-route-out net preference > 0.

Otherwise: `INDEPENDENT_STARTS_ARTISTIC_SUPPORT_NOT_DEMONSTRATED`.

A pass authorizes promotion of the equal-budget R9–R12 restart-tail policy into the supported runtime. A failure preserves the current runtime and stops this exact artistic promotion attempt; do not tune the review population or substitution positions on consumed evidence.
