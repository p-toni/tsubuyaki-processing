# Operator novelty allocation v1

## Question

The current supported production-facing regime is:

- single-incumbent search;
- `native-spectral-50-50-v1`;
- exactly 20 generated challengers per route;
- preserve the complete hard-valid archive;
- deliver three candidates with the artistically supported max-dispersion shortlist.

#108 showed that a stable delivery shortlist is **not** a safe stopping signal: late attempts still contribute too much full-archive capacity. This experiment therefore keeps all 20 attempts and asks a different question:

> Can early target-blind phenotype novelty predict which mutation operator should receive more of the fixed suffix budget?

This is operator allocation, not parent/frontier allocation (#105), not search stopping (#108), and not a change to the promoted delivery rule (#106/#107).

## Frozen arms

For every route/seed, all three arms use the same route, exact same deterministic search seed, same hard-valid start, same selector, same incumbent-only parenting, same mutation scales, same total 20 attempts, and same first eight generated attempts.

The shared first eight attempts are exactly the current runtime prefix:

- explore: `native, native, spectral, spectral`;
- roundA: `native, native, spectral, spectral`.

Thus the prefix contains exactly four native and four spectral attempts.

After that shared prefix, the 12-attempt refine stage differs only in operator counts:

1. **baseline10x10** — current runtime: 6 native then 6 spectral refine attempts, for 10 native + 10 spectral total;
2. **adaptive12x8** — the prefix novelty winner receives 8 refine attempts and the loser 4, for a 12/8 final split;
3. **antiAdaptive8x12** — exact complementary allocation: the prefix novelty winner receives 4 refine attempts and the loser 8.

Within refine, native attempts always precede spectral attempts, matching the current runtime's operator-block ordering. The adaptive intervention therefore changes counts, not the native-before-spectral convention.

## Frozen target-blind novelty signal

The allocation decision is made once, after the exact shared eight-attempt prefix and before any refine candidate exists.

For each of the eight generated prefix attempts:

- invalid attempt: novelty contribution = `0`;
- hard-valid attempt: novelty contribution = its nearest-neighbor phenotype distance to the shared hard-valid start or any other hard-valid generated prefix candidate.

Phenotype distance is the exact already-supported raw representation from #106:

- frames `t=30,90,150`;
- grayscale;
- nearest-neighbor resize to `100×100` for distance only;
- mean absolute pixel difference across the concatenated frames.

For each operator, take the mean novelty contribution over its exact four prefix attempts. The operator with the larger mean is the novelty winner. An exact floating-point tie deterministically chooses `native` as the conservative incumbent operator.

There is:

- no target;
- no structural score;
- no diagnostic score;
- no semantic score;
- no model judge;
- no human label;
- no learned threshold;
- no parameter fit.

## Why the anti-adaptive arm exists

A positive adaptive-vs-10/10 result alone could mean only that some 60/40 mixture is globally better.

The complementary arm asks the causal question directly: if the early novelty signal says operator X deserves more suffix budget, does giving more budget to X outperform giving the same imbalance to the other operator?

If the performance gates pass but one operator wins at least 80% of route-seed prefixes, the result is interpreted as a **global operator bias**, not evidence for trajectory-specific adaptation. That outcome authorizes only a fresh fixed-ratio replication.

## Fresh population

Excluded smoke: `745999`.

Authoritative master seeds:

`745003, 745019, 745037, 745053, 745071, 745089, 745107, 745127, 745149, 745167, 745181, 745199, 745223, 745239, 745257, 745277, 745293, 745311, 745331, 745349`.

The complete `745xxx` namespace was absent from repository code and commit messages before preregistration.

Routes remain:

- recurrence;
- orbit;
- filament.

## Evaluation

All three search archives and all three max-dispersion delivery trios are frozen before structural targets are constructed or scored.

Only afterward reveal the existing frozen 15-target runtime structural benchmark.

For each seed × route × target cell record:

- best recovery from each arm's complete hard-valid generated archive;
- best recovery from each arm's max-dispersion three-item delivery shortlist.

Structural recovery is experimental evidence only; it is not artistic authority.

## Meaningful-effect margin

The complexity bar is inherited unchanged from #108:

`0.003255297955511336`

This is exactly half of #106's independently confirmed `+0.006510595911022672` delivery gain. A more complex runtime allocation policy should improve full-archive structural capacity by at least this amount on average before it is considered worth advancing.

## Preregistered decisions

### `NOVELTY_OPERATOR_ALLOCATION_PROMISING`

Requires all of:

1. exact 20-seed / 60 route-seed / 900-cell authoritative rectangle;
2. smoke proves the custom `baseline10x10` runner is phenotype-identical to the current runtime baseline;
3. adaptive minus baseline mean full-archive recovery > `0.003255297955511336`;
4. one-sided 95% seed-bootstrap lower bound for adaptive minus baseline full-archive recovery > 0;
5. adaptive minus anti-adaptive mean full-archive recovery > 0;
6. one-sided 95% seed-bootstrap lower bound for adaptive minus anti-adaptive full-archive recovery > 0;
7. every route has positive adaptive-minus-baseline full-archive mean;
8. every route has positive adaptive-minus-anti-adaptive full-archive mean;
9. adaptive-minus-baseline mean max-dispersion delivery recovery > 0;
10. one-sided 95% seed-bootstrap lower bound for adaptive-minus-baseline delivery recovery > `-0.003255297955511336`;
11. every route's adaptive-minus-baseline delivery mean > `-0.003255297955511336`;
12. adaptive hard-valid generated rate is no more than 5 percentage points below baseline;
13. both operators win at least 20% of the 60 route-seed prefix decisions.

A pass authorizes a **fresh blinded human artistic comparison** of baseline vs adaptive max-dispersion delivery. It does not immediately replace `10/10` in production.

### `GLOBAL_OPERATOR_BIAS_INDICATED`

If gates 1–12 pass but gate 13 fails, do not promote adaptive allocation. The evidence instead indicates that one operator is globally favored under this regime. Authorize one fresh fixed `12/8` dominant-operator replication against `10/10`.

### `NOVELTY_OPERATOR_ALLOCATION_NOT_PROMISING`

Any other outcome stops this exact policy.

Do not tune the 8-attempt prefix, leave-one-out novelty definition, 12/8 split, tie rule, distance representation, or decision gates on consumed `745xxx` evidence.
