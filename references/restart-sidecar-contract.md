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
13. **Record binding.** The sidecar report stores the SHA-256 digest of the exact `candidates.json` bytes so a later reviewed handoff can detect stale or modified candidate records before any lineage starts.

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

## Reviewed-start handoff

A sidecar candidate may become the start of a **new isolated lineage** only after explicit external artistic selection. This is not automatic promotion into the run that discovered it.

The handoff manifest is intentionally explicit:

```json
{
  "version": 1,
  "authority": "explicit-independent-artistic-selection-v1",
  "sourceCandidates": "run-with-sidecar/restart_sidecar/candidates.json",
  "sourceReport": "run-with-sidecar/restart_sidecar/report.json",
  "selectedCandidateIds": ["SC-R1", "SC-O2", "SC-F3"],
  "selectionNote": "optional reviewer note"
}
```

Then run a new lineage with a fresh search seed:

```bash
python run.py \
  --brief brief.json \
  --seed 260901 \
  --out reviewed-lineage \
  --reviewed-starts handoff.json
```

The handoff fails closed unless all of the following hold:

- authority string is explicit and exact;
- source report is a `restart-sidecar-v1` exploratory report with the baseline-isolation contract intact;
- exact `candidates.json` SHA-256 matches the digest recorded by the sidecar report;
- every selected ID exists and was hard-valid in the source sidecar;
- every source candidate is an independent sidecar start (`parent_id = null`, `basin = id`);
- every selected phenotype reproduces its recorded multi-time phenotype hash;
- every selected candidate remains hard-valid under the active brief;
- every active route retains at least one explicitly selected start.

The new lineage is executed by the existing `run_search_from_starts(...)` path and receives an independent search seed. Source selection provenance is persisted in the candidate's `reviews` record and in `reviewed_start_handoff.json`.

`--restart-sidecar` and `--reviewed-starts` are intentionally separate runtime surfaces and cannot be combined in one command in v1.

## Non-degradation claim

The sidecar does not require a statistical non-degradation claim for the baseline because baseline non-degradation is an architectural property: the baseline run finishes before sidecar generation and its output files are not rewritten by the sidecar.

Regression tests therefore require byte-identical baseline artifacts with and without sidecar generation.

This guarantee is narrower than artistic superiority. The sidecar may contain useful discoveries, weak discoveries, or no valid discoveries. It is a plural exploration surface, not a hidden winner-selection policy.

Likewise, a reviewed-start lineage is not evidence that its selected start is universally superior. It means only that explicit independent artistic authority chose to spend a **new** search budget developing that phenotype. The original baseline and discovery run remain unchanged.
