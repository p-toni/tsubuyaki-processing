# Restart sidecar contract

## Status

Production-safe integration boundary after the independent-start research line through PRs #112, #113, #114, and #115.

## Evidence

The research line established four facts for the confirmed intrinsic-1D routes (`recurrence`, `orbit`, `filament`):

1. independent route-prior starts repeatedly improve structural archive and delivery coverage;
2. directly replacing supported runtime attempts with restart draws did not earn artistic authority;
3. preserving the full spectral budget removed the strongest operator-deletion confound, but the stricter artistic Stage-A gate still did not pass;
4. spending two of four restart slots on one-step local cultivation preserved improvement over baseline but lost too much breadth relative to four independent starts.

The evidence-supported conclusion is therefore **not** “put restarts into the baseline search.” It is:

> preserve the baseline exactly; expose independent-start breadth as an optional, separately labeled exploration surface.

## Architectural invariants

The restart sidecar MUST satisfy all of the following:

1. **Default off.** Ordinary `run.py` behavior does not generate sidecar candidates.
2. **Post-search only.** Baseline search completes before the sidecar module is imported or invoked.
3. **Separate RNG namespace.** Sidecar draws use `restart-sidecar-v1` derived seeds and cannot advance baseline RNG streams.
4. **No baseline state mutation.** Sidecar candidates never enter `SearchState`.
5. **No selector mutation.** Sidecar candidates never participate in baseline pairwise decisions.
6. **No parenting.** A sidecar candidate cannot parent any baseline candidate.
7. **No delivery replacement.** Sidecar candidates cannot replace or enlarge the baseline artistic frontier or default delivery.
8. **Hard validity only.** Existing route-specific validity checks are applied. No diagnostic score, structural benchmark, human preference, or model judgment promotes a sidecar candidate into the baseline.
9. **Invalid consumes budget.** Each independent route-prior draw consumes one sidecar attempt; invalid draws are not retried.
10. **Eligible topology scope.** v1 is limited to active representations whose frozen intrinsic dimension is 1.
11. **Separate artifacts.** Sidecar candidates, report, timelines, and contact sheet live under `<out>/restart_sidecar/`.
12. **Explicit authority label.** Sidecar output is exploratory only and carries no automatic artistic-promotion authority.

## Runtime interface

```bash
python run.py \
  --brief brief.json \
  --seed 260826 \
  --out run-with-sidecar \
  --restart-sidecar 4
```

`4` means four independent attempts per eligible active intrinsic-1D route.

The baseline files remain the ordinary outputs:

```text
report.json
search_state.json
stage1_representatives.png
stage2_survivors.png
finalists.png
winner_timeline.png
```

The optional exploration surface is separate:

```text
restart_sidecar/
├─ report.json
├─ candidates.json
├─ contact_sheet.png        # only when at least one valid candidate exists
└─ timelines/
   └─ <candidate>.png       # valid candidates only
```

## Non-degradation claim

The sidecar does not require a statistical non-degradation claim for the baseline because baseline non-degradation is an architectural property: the baseline run finishes before sidecar generation and its output files are not rewritten by the sidecar.

Regression tests therefore require byte-identical baseline artifacts with and without sidecar generation.

This guarantee is narrower than artistic superiority. The sidecar may contain useful discoveries, weak discoveries, or no valid discoveries. It is a plural exploration surface, not a hidden winner-selection policy.
