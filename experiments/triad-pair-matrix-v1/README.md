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

The candidate format is:

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

Every policy must reproduce the exact frozen eager trajectory on seeds `7, 19, 43`.

## Dependency boundary

Unchanged from `triad-review-v1`:

- candidate A is the current incumbent;
- B and C are already-generated siblings;
- `B.parent == A.id` and `C.parent == A.id`;
- B/C stage is `explore` or `roundA`;
- same route/group;
- `refine` remains forbidden because later phenotype generation may depend on an earlier promotion;
- frontier packing remains out of scope.

## Decision rule

The explicit pair-matrix format advances only if:

1. all frozen trajectories remain exact;
2. it does not regress mean review tasks, rounds, or candidate exposures versus rank-triad-k2;
3. it demonstrates that at least one selected triad can preserve a non-rankable/cyclic pair matrix, or otherwise provides no practical advantage over the simpler rank transport.

If it advances, the next implementation should supersede ranked-triad scheduling with an explicit pair-verdict triad transport. Existing ranked-triad v1 can remain as historical prototype evidence but should not become the automatic runtime scheduler.

Synthetic oracle outcomes in this experiment are scheduling/convergence evidence only, never artistic authority.
