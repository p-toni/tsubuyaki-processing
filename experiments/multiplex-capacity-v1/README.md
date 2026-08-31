# multiplex-capacity-v1

Status: **preregistered, not executed**.

This experiment is the gate between the Yuruyurau grammar audit and any proposal for a sixth representation.

## Claim under test

A neutral **index-multiplexed latent geometry** primitive provides structural search capacity that is not efficiently reachable by the current five routes under equal budget.

The intervention is mechanistic. It must not port any source formula, reproduce a reference image, or encode named creature semantics.

## Experimental representation

The candidate grammar contains independently ablatable mechanisms:

- `slow`: a low-frequency coordinate from one dense scalar sample index;
- `fast`: high-frequency coordinates from the same index;
- `branch`: a small categorical residue coordinate derived from that index;
- `latent`: a nonlinear radius/energy variable built from slow + fast coordinates;
- `reuse`: the latent variable affects phase, placement/deformation, and motion;
- `cross`: multiplicative coupling between slow, fast, latent, and time terms;
- `singular`: a bounded reciprocal response with an explicit denominator floor.

The implementation is neutral and parameterized in `multiplex_representation.py`; it does not port any public source equation.

## Required ablations

The full grammar is compared with four same-genome-schema ablations:

1. **no-branch** — categorical residue coordinate removed;
2. **regular-grid** — quotient/residue/raw-index multiplexing is replaced with an explicit smooth 2-D lattice;
3. **no-reuse** — the latent radius may place points but separate fields drive phase, motion, and reciprocal response;
4. **no-singular** — bounded reciprocal mechanism removed.

All five multiplex variants use the same genome schema, shared accepted start genomes, and the same mutation law. The current five routes remain unchanged.

## Frozen challenge set

The 12 target generators in `challenges.py` are structurally distinct from the candidate implementation and draw randomness only once at the challenge-parameter level; point evaluation is smooth/deterministic.

- `linked-1..3`: multiple phase-linked submanifolds without explicit organ anchors;
- `woven-1..3`: pseudo-2-D structure from one smooth dense parameter;
- `coupled-1..3`: a radial field controls both geometry and local motion magnitude;
- `detail-1..3`: explicit 2-D sheets with localized high-curvature deformation.

Six challenges are marked `smoothPlausible`, exceeding the preregistered floor of four cases where sheet/family-like smooth structure is a plausible solution.

No challenge equation is shared with `multiplex_representation.py`.

## Population

First pass uses exactly these 20 already-consumed master seeds:

`1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223`.

Seed `9001` is excluded smoke only. No fresh search evidence is spent in v1. No early stopping, seed replacement, or post-hoc target substitution.

## Frozen search topology

Every representation × seed × challenge receives exactly **20 candidate evaluations**:

- 4 independently generated hard-valid starts;
- 4 fixed mutation cycles per start = 16 mutations;
- mutation scales `(1.0, 0.7, 0.55, 1.2)`;
- one-coordinate historical ±18% numeric mutation law;
- a mutation replaces its current lineage parent only when it is hard-valid and does not worsen sparse-geometry-v1 target distance;
- all starts and all generated children remain in the final evaluated pool;
- target scoring cannot remove a retained start, so final distance cannot be worse than initial best distance.

The five multiplex variants share the same accepted start genomes. Their mutation RNG event labels are also shared; different outcomes can change later parent genomes, but not the random event assigned to a lineage/cycle.

Current routes use the identical start count, cycle count, mutation scales, candidate-evaluation budget, target selector rule, and sparse-geometry-v1 measurement. Their native seed/mutation/checker contracts remain unchanged.

The confirmed repertoire allocator is intentionally **not** used here because it is not representation-neutral for an unregistered grammar. This is a capacity test under a simpler common target-search topology.

## Measurement

Primary cell score is absolute normalized target recovery:

`recovery = 1 - final_sparse_geometry_distance`.

For each seed/challenge, the primary effect is:

`full multiplex recovery - max(recovery of each current route)`.

Master-seed effects average all 12 challenge effects before seed-level summaries. Inference/diagnostics are over complete master seeds, not representation × seed pseudo-replicates.

Secondary diagnostics:

- full-minus-each-ablation recovery;
- `structural-v1` niche coverage across hard-valid candidates;
- unique rendered phenotype rate;
- hard-valid yield;
- per-family / per-challenge effects;
- leave-one-challenge-family-out means;
- largest seed × challenge primary cell;
- which current route is the best comparator per seed/challenge.

For the niche gate, hard-valid niche records from full + four ablations are deterministically ordered by seed/challenge/candidate id and rarefied to the **minimum hard-valid record count across the five variants**. Niche density is `distinct structural-v1 niches / rarefaction count`, so all variants are compared at equal hard-valid sample count.

## Pilot advancement gate

`MULTIPLEX_CAPACITY_PROMISING` iff all hard invariants pass and all of the following hold:

1. full multiplex mean recovery advantage over **best current-route result per seed/challenge** is > 0;
2. every leave-one-challenge-family-out mean of that advantage is > 0;
3. full multiplex mean recovery advantage over each ablation is > 0;
4. full multiplex rarefied `structural-v1` niche density is at least **1.25×** that of its strongest ablation;
5. no single challenge family contributes more than **60%** of aggregate positive primary advantage.

Route wins, medians, hard-valid yield, unique phenotype rate, or one striking challenge cannot override these gates.

This is a consumed-seed pilot only. Passing it does not admit a new route.

## If promising

1. freeze the exact multiplex genome, mutator, checker, search topology, targets, and reducer;
2. use complete-master-seed variance to power-plan a fresh fixed-sample confirmation;
3. run fresh confirmation exactly once;
4. only after mechanical confirmation, run a blind artistic portfolio comparison against the five-route repertoire;
5. representation admission still requires evidence that the new route adds a niche not already preserved by current routes, and does not weaken outer route authority.

## If not promising

Do not retune the same mechanism family against these 20 consumed seeds. Classify which assumption failed and either close the line or define a materially new v2 hypothesis with a different consumed holdout.

## Relationship to the current research program

This experiment runs in parallel with the independent artistic replication of the confirmed repertoire allocator. It does not modify #79, reinterpret its blind evidence, or change the confirmed allocator.
