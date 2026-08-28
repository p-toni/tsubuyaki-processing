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

## Results

All gates pass.

The pair-only collector reproduced the **exact current group-K2 pair IDs in the exact same batches on every replay of every seed**. Moving task creation from compare-time to post-search flush is therefore behavior-neutral under the current scheduler policy on the frozen trajectories.

| seed | current tasks | triad tasks | current rounds | triad rounds | current exposures | triad exposures | triad panels |
|---|---:|---:|---:|---:|---:|---:|---:|
| 7 | 18 | **14** | 10 | **9** | 36 | **32** | 4 |
| 19 | 19 | **15** | 11 | **9** | 38 | **33** | 3 |
| 43 | 21 | **17** | 11 | **9** | 42 | **37** | 3 |
| **mean** | **19.33** | **15.33** | **10.67** | **9.00** | **38.67** | **34.00** | **3.33** |

Relative to today's file-backed pair group-K2 path:

```text
review tasks         -20.7%
review rounds        -15.6%
candidate exposures  -12.1%
search replays       -14.3%
```

The triad path elicits more explicit pair relations despite fewer candidate exposures: mean pair relations increase from `19.33` to `22.00`, because one fixed sibling panel can settle the challenger-challenger relation that may become reachable after a promotion.

Every final trajectory signature and winner remains identical to the frozen eager baseline.

The observed file-backed metrics exactly reproduce the prior in-memory `triad-pair-matrix-v1` calibration. This removes a substantial implementation-risk gap between the abstract scheduler and the actual review transports.

`test_scheduler_safety.py` separately guards the dependency boundary: `explore` / `roundA` fixed siblings may pack; `refine`, cross-route, wrong-parent, mixed-stage, duplicate sibling, and already-evidenced relations may not.

## Decision

**Advance to an opt-in screened-search pair-matrix triad scheduler.**

The runtime implementation should preserve today's pair group-K2 path as the default while introducing an explicit opt-in mode that:

1. collects unresolved comparisons without changing comparison traversal;
2. flushes at most the existing task/group caps after the search replay;
3. upgrades only the proven fixed-sibling boundary to pair-matrix triads;
4. reads pair and triad decisions back as ordinary `PhenotypePreferenceEvidence`;
5. leaves `refine`, frontier, cross-route, hard validity, promotion authority, and all representation behavior unchanged.

Before changing the default, the actual `screened_search.resume_adaptive_search(...)` opt-in path should pass an equivalent frozen replay calibration.

`results.json` persists the full integration summary. The temporary calibration workflow has been removed; the final experiment branch contains only durable experiment artifacts and is validated by the repository's normal CI.
