# Triad scheduler fresh-seed holdout v1

## Question

Does the merged opt-in pair-matrix scheduler remain semantically equivalent to the current pair group-K2 scheduler outside the three seeds used throughout development and deployment calibration?

This is a **fresh holdout**. The seeds are predeclared as the first nine prime numbers greater than the largest calibration seed (`43`):

```text
47, 53, 59, 61, 67, 71, 73, 79, 83
```

They were chosen before observing any result. No seed was removed or replaced after execution.

## Runtime under test

This reuses the actual merged screened runtime from `screened-triad-runtime-replay-v1`:

```text
prepare_probe
→ strong route screen preserving recurrence/family/sheet
→ resume_adaptive_search
→ actual pair or pair-matrix queue
→ synthetic authoritative calibration evidence
→ replay until convergence
```

The synthetic oracle is scheduling/convergence evidence only, never artistic authority.

The experiment-specific one-probe-per-route setup is retained so the holdout changes **only the random search seed**, not the architecture or workload shape. Product route-screen default remains two probes per route.

## Policies

```text
currentPairK2
  merged default pair scheduler
  global pending K=2
  per-group K=1

matrixTriadK2
  merged opt-in pair-matrix scheduler
  identical task/group caps
  fixed explore/roundA sibling packing only
```

## Predeclared per-seed gates

Every one of the nine seeds had to satisfy:

1. exact equality of the full search trajectory signature;
2. exact equality of final winner;
3. triad review tasks <= pair review tasks;
4. triad review rounds <= pair review rounds;
5. triad search replays <= pair search replays;
6. triad candidate exposures <= pair candidate exposures.

A seed with no safe triad opportunity could tie the pair scheduler on reviewer cost. Any cost regression or trajectory divergence failed the holdout.

## Result

**All 9 / 9 fresh seeds passed every gate.** All nine also showed strict task savings.

| metric | pair mean | triad mean | relative change |
|---|---:|---:|---:|
| review tasks | 21.11 | 16.44 | **-22.1%** |
| review rounds | 11.78 | 9.44 | **-19.8%** |
| search replays | 12.78 | 10.44 | **-18.3%** |
| candidate exposures | 42.22 | 36.67 | **-13.2%** |
| pair relations elicited | 21.11 | 24.00 | **+13.7%** |

No seed showed a full-trajectory divergence, winner divergence, or reviewer-cost regression.

The result therefore extends the exact scheduler-semantic evidence from the original three frozen seeds to **12 total screened-search trajectories**.

`results.json` persists the per-seed trajectory signatures, winners, costs, and aggregate statistics recovered from the original workflow artifacts.

## Decision

The fresh holdout passes and materially strengthens confidence that pair-matrix packing preserves search semantics while reducing reviewer work.

It still does **not** answer whether a human reviewer judges equally well from one three-candidate panel. Pair-matrix scheduling therefore remains opt-in pending artistic-judgment evidence.

The temporary holdout Actions workflow was merged before cleanup and is removed by the subsequent five-route stress PR so the completed experiment does not continue retriggering.
