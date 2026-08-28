# Screened-search pair-matrix triad runtime replay v1

## Purpose

This is the deployment gate for the opt-in triad scheduler.

Earlier experiments established the scheduling rule in isolation and then through real pair/triad queue files. This experiment removes the remaining architectural gap by driving the actual public research entrypoint:

```text
prepare_probe(...)
→ strong route screen keeping the frozen routes alive
→ resume_adaptive_search(...)
→ EvidenceAuthoritySelector
→ actual pair / pair-matrix review queues
→ synthetic calibration decisions
→ resume_adaptive_search(...) again
→ convergence
```

The synthetic oracle is scheduling/convergence evidence only. It is not artistic authority.

## Frozen setup

Seeds: `7, 19, 43`.

Routes: `recurrence`, `family`, `sheet`.

The probe phase uses one deterministic start per route solely to reproduce the exact frozen search starts from the prior scheduler calibrations. This is an experiment-specific override; the screened-search product default remains two probes per route.

Every route receives a strong `keep`, so route narrowing does not alter the three-route frozen search. No extra starts are allocated after the probe phase.

## Compared runtime policies

```text
screened-current-pair-k2
  current evidence-authority runtime behavior
  eager pair queue
  global pending cap 2
  pending group cap 1

screened-matrix-triad-k2
  same resume_adaptive_search entrypoint
  opt-in candidate_pair_matrix_triads=True
  unresolved comparisons collected during traversal
  post-search flush upgrades only dependency-safe fixed siblings
```

## Gate

For every seed:

1. both policies must reproduce the exact frozen eager trajectory signature;
2. the current screened pair path must reproduce the exact task/round/exposure metrics already measured by the file-backed queue experiment;
3. the opt-in screened triad path must reproduce the exact triad task/round/exposure metrics already measured there;
4. triads must reduce review tasks and candidate exposures without increasing reviewer rounds;
5. normal repository CI must remain green.

Expected frozen metrics:

| seed | current tasks | triad tasks | current rounds | triad rounds | current exposures | triad exposures |
|---|---:|---:|---:|---:|---:|---:|
| 7 | 18 | 14 | 10 | 9 | 36 | 32 |
| 19 | 19 | 15 | 11 | 9 | 38 | 33 |
| 43 | 21 | 17 | 11 | 9 | 42 | 37 |

If any exact value drifts, the opt-in scheduler does not advance.

## Results

All deployment gates pass on the actual screened-search entrypoint.

| seed | current tasks | triad tasks | current rounds | triad rounds | current exposures | triad exposures | current relations | triad relations |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 7 | 18 | **14** | 10 | **9** | 36 | **32** | 18 | **22** |
| 19 | 19 | **15** | 11 | **9** | 38 | **33** | 19 | **21** |
| 43 | 21 | **17** | 11 | **9** | 42 | **37** | 21 | **23** |
| **mean** | **19.33** | **15.33** | **10.67** | **9.00** | **38.67** | **34.00** | **19.33** | **22.00** |

Relative to the current screened pair group-K2 path:

```text
review tasks          -20.7%
review rounds         -15.6%
search replays        -14.3%
candidate exposures   -12.1%
pair relations         +13.8%
```

The runtime reproduced the prior file-backed scheduler experiment exactly on every predeclared task, round, and exposure metric. It also reproduced the same frozen full-state trajectory signatures and winners:

```text
seed 7  83aeec... -> FC1-A1
seed 19 acbe0c... -> RC1-R2
seed 43 a2bf05... -> FC1-E1
```

This closes the observed implementation gap across three levels:

```text
abstract scheduler calibration
= file-backed pair/triad queue integration
= actual prepare_probe / resume_adaptive_search runtime
```

`results.json` persists the exact runtime evidence. The temporary workflow was used only to execute the deployment gate and is removed before merge.

## Decision

**Merge the opt-in pair-matrix scheduler. Keep the current pair group-K2 policy as the default.**

The evidence is now strong that the opt-in implementation faithfully realizes the calibrated scheduling policy. It is not yet evidence that a real human reviewer finds three explicit judgments on one A/B/C panel equally reliable or less fatiguing than separate pair panels.

Without new human review, the next useful autonomous evidence is broader scheduler robustness: additional seeds/search trajectories and adversarial dependency cases. That can strengthen a later default decision without consuming artistic ratings.

## Default boundary

This experiment does **not** justify making triads the default. Passing it establishes that the opt-in `resume_adaptive_search(...)` path implements the already-calibrated scheduler faithfully. A later default decision should require broader independent replay coverage and/or real reviewer evidence showing that the compressed panel preserves human judgment quality in practice.
