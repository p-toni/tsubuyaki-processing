# File-backed triad queue replay v1

## Purpose

Validate the actual runtime integration shape for pair-matrix triads.

Previous experiments used direct in-memory synthetic evidence to isolate scheduling. The pair and triad transports now exist, so this gate runs the real search through real queue files, sealed mappings, decisions, provenance, and decoders.

No production/screened-search behavior changes in this experiment.

## Policies

```text
current-group-k2
  today's EvidenceAuthoritySelector
  pair queue only
  global pending cap = 2
  pending group cap = 1

collector-pair-k2
  collect unresolved comparisons during the replay
  after search, flush at most 2 pair tasks / 1 per group
  triads disabled

matrix-triad-file-k2
  same collect→flush policy
  upgrade only dependency-safe fixed sibling proposals to one pair-matrix triad
  all other tasks remain ordinary v3 pairs
```

## Strong parity gate

`collector-pair-k2` must reproduce **the exact same pair IDs in the exact same review batches, round by round**, as `current-group-k2` on every frozen seed.

This is stronger than final trajectory agreement. If it fails, collect→flush is not a safe implementation base even if the final winner happens to match.

## Triad boundary

A proposal can be upgraded only when:

- both unresolved comparisons share the same incumbent phenotype;
- both challengers are distinct fixed siblings;
- same route and same stage;
- challenger stage is `explore` or `roundA`;
- both challenger parents equal the current incumbent id;
- none of the three pair relations already has authoritative evidence.

`refine` remains pairwise because later candidate generation can depend on an earlier promotion. Frontier/cross-route comparisons remain pairwise.

## Real transport replay

Pair tasks are written with `create_review_bundle(...)` and resolved through the existing v3 pair decoder.

Triad tasks are written with `create_triad_pair_matrix_bundle(...)`; the synthetic oracle fills all three anonymous pair verdicts and the next replay consumes them through `decode_triad_pair_matrix_evidence(...)`.

Synthetic oracle provenance is `independent-model` only to exercise the existing authority path. It is calibration evidence, not an artistic judgment.

## Gate

Advance scheduling plumbing only if all frozen seeds satisfy:

1. exact eager trajectory signature;
2. collector pair-only batches exactly equal current group-K2 batches;
3. pair-matrix triads reduce reviewer tasks/exposure without increasing review rounds versus current group-K2;
4. no triad is created from refine/frontier/cross-route proposals.

If the gate passes, the next PR may add an **opt-in** screened-search scheduler. Default behavior should remain pair group-K2 until the actual runtime path passes equivalent replay tests.
