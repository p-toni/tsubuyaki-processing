# Explicit pair-matrix triad review v1

## Trigger

The merged `triad-review-v1` experiment showed that one three-candidate review task can reduce reviewer work while preserving the frozen search trajectory. Its runtime transport, however, represents the decision as one ranked partition such as:

```text
B > A = C
```

That format is safe only when the three underlying pairwise judgments are jointly rankable.

In the synthetic experiment, rankability could be checked **before** packing because the hidden pairwise oracle was available. A real human review has no such pre-review oracle. Automatically asking for one total ranking would therefore impose transitivity on artistic judgments that may legitimately be cyclic or context-sensitive.

## Question

Can the same one-panel compression preserve arbitrary pairwise evidence exactly?

The tested format is:

```text
one blinded A/B/C temporal panel

record independently:
A vs B -> A | B | tie
A vs C -> A | C | tie
B vs C -> B | C | tie
```

This represents all `3^3 = 27` complete three-candidate pairwise outcome matrices, including the 14 matrices that cannot be represented as a total preorder.

## Frozen comparison

Reuses the exact candidate generation, oracle, seeds, routes, and eager trajectory signatures from `triad-review-v1` / `route-balanced-review-v1`.

Policies:

```text
pair-k2
  current two pair-task baseline

rank-triad-k2
  merged v1 experiment: safe sibling triad only when hidden pair outcomes are rankable

matrix-triad-k2
  same dependency-safe sibling boundary
  no rankability precondition
  one task explicitly settles all three pair relations
```

Every policy reproduced the exact frozen eager trajectory on seeds `7, 19, 43`.

## Dependency boundary

Unchanged from `triad-review-v1`:

- candidate A is the current incumbent;
- B and C are already-generated siblings;
- `B.parent == A.id` and `C.parent == A.id`;
- B/C stage is `explore` or `roundA`;
- same route/group;
- `refine` remains forbidden because later phenotype generation may depend on an earlier promotion;
- frontier packing remains out of scope.

## Predeclared decision rule

The explicit pair-matrix format advances only if:

1. all frozen trajectories remain exact;
2. it does not regress mean review tasks, rounds, or candidate exposures versus rank-triad-k2;
3. it demonstrates that at least one selected triad can preserve a non-rankable/cyclic pair matrix, or otherwise provides no practical advantage over the simpler rank transport.

## Results

| seed | pair tasks | rank tasks | matrix tasks | rank rounds | matrix rounds | rank exposures | matrix exposures | matrix triads | non-rankable matrix triads |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 7 | 18 | 15 | **14** | 9 | 9 | 33 | **32** | 4 | 1 |
| 19 | 19 | 16 | **15** | 10 | **9** | 35 | **33** | 3 | 1 |
| 43 | 21 | 17 | 17 | 9 | 9 | 37 | 37 | 3 | 0 |
| **mean** | **19.33** | **16.00** | **15.33** | **9.33** | **9.00** | **35.00** | **34.00** | **3.33** | **0.67** |

Compared with the rank-constrained triad policy:

```text
review tasks        16.00 -> 15.33   (-4.2%)
review rounds        9.33 ->  9.00   (-3.6%)
candidate exposures 35.00 -> 34.00   (-2.9%)
```

Compared with the current pair-K2 baseline:

```text
review tasks        19.33 -> 15.33  (-20.7%)
review rounds       10.67 ->  9.00  (-15.6%)
candidate exposures 38.67 -> 34.00  (-12.1%)
```

The practical distinction is not merely theoretical:

- seed 7 packed a non-rankable recurrence triad that rank-triad had to split into later pair work;
- seed 19 packed a non-rankable sheet triad;
- both preserved the exact frozen search trajectory.

The gate passes.

## Decision

**Use explicit pair-matrix triads as the runtime direction. Do not automatically schedule ranked triads.**

The next implementation should introduce a pair-verdict triad transport that decodes directly to the existing three `PhenotypePreferenceEvidence` records without any transitivity assumption. The merged ranked-triad v1 transport remains historical prototype evidence and can be useful for explicit rank-based review, but it is not the automatic scheduler contract.

After that transport is validated, automatic scheduling still requires a separate replay experiment because the current `EvidenceAuthoritySelector` queues eagerly. The scheduler must preserve current group-K2 ordering and upgrade only dependency-safe sibling proposals into a triad; `refine` and frontier comparisons remain pairwise.

Synthetic oracle outcomes in this experiment are scheduling/convergence evidence only, never artistic authority.
