# Triad scheduler fresh-seed holdout v1

## Question

Does the merged opt-in pair-matrix scheduler remain semantically equivalent to the current pair group-K2 scheduler outside the three seeds used throughout development and deployment calibration?

This is a **fresh holdout**. The seeds are predeclared as the first nine prime numbers greater than the largest calibration seed (`43`):

```text
47, 53, 59, 61, 67, 71, 73, 79, 83
```

They were chosen before observing any result. No seed is removed or replaced after execution.

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

Every one of the nine seeds must satisfy:

1. exact equality of the full search trajectory signature;
2. exact equality of final winner;
3. triad review tasks <= pair review tasks;
4. triad review rounds <= pair review rounds;
5. triad search replays <= pair search replays;
6. triad candidate exposures <= pair candidate exposures.

A seed with no safe triad opportunity may tie the pair scheduler on reviewer cost. Any cost regression or trajectory divergence fails the holdout.

## Aggregate decision

After all nine seeds complete:

- all per-seed gates must pass;
- mean review tasks and candidate exposures must not regress;
- at least one fresh seed must show a strict reviewer-cost improvement for the experiment to add positive evidence rather than merely compatibility evidence.

Passing strengthens scheduler-semantic confidence. It still does **not** answer whether a human reviewer prefers or judges equally well from one three-candidate panel, so it does not by itself justify changing the default.
