# Restart sidecar contract

## Status

Production-safe optional exploration surface after the independent-start line through #112–#118, the eight-attempt budget confirmation in #126/#127, and the intrinsic-2D route-scope confirmation in #128.

The sidecar remains **default off, post-search, and non-promoting**.

## Evidence

The research program established:

1. independent route-prior starts improve mechanical structural archive/delivery coverage;
2. replacing supported baseline attempts with restart draws did not earn artistic authority;
3. preserving baseline search and exposing restarts as a separate sidecar avoids that substitution failure;
4. one-shot basin breadth is more valuable than spending the same restart resource cultivating fewer starts;
5. eight sidecar attempts per eligible route are required to retain the established coverage gain (#126/#127);
6. on fresh `760xxx`, eight-attempt sidecars also produced strong mechanical coverage gains on `family` and `sheet` (#128), with 320/320 hard-valid attempts and positive archive, delivery, and dispersion effects on both routes.

The conclusion is still **not** “put restarts into baseline search.” It is:

> preserve the baseline exactly; expose independent-start breadth as an optional, separately labeled exploration surface.

## Two distinct authority surfaces

Mechanical scope and artistic lineage scope are intentionally separate.

### Exploratory sidecar generation

Evidence-authorized routes:

```text
recurrence
orbit
filament
family
sheet
```

`family` and `sheet` were added by #128 for **exploratory sidecar generation only**.

### Reviewed-start lineage

Evidence-authorized routes remain:

```text
recurrence
orbit
filament
```

#128 supplied no artistic evidence and therefore does not authorize `family` or `sheet` to enter a reviewed-start lineage. Expanding this second set requires separate artistic-scope evidence.

Historical sidecar reports that recorded the original three-route sidecar authority remain valid provenance inputs for the reviewed-start handoff; current reports record the five-route exploratory sidecar authority. In both cases, reviewed-lineage route eligibility remains the narrower three-route set.

## Architectural invariants

The restart sidecar MUST satisfy all of the following:

1. **Default off.** Ordinary `run.py` behavior does not generate sidecar candidates.
2. **Post-search only.** Baseline search completes before the sidecar module is invoked.
3. **Separate RNG namespace.** Sidecar draws use `restart-sidecar-v1` derived seeds and cannot advance baseline RNG streams.
4. **No baseline state mutation.** Sidecar candidates never enter `SearchState`.
5. **No selector mutation.** Sidecar candidates never participate in baseline pairwise decisions.
6. **No parenting.** A sidecar candidate cannot parent any baseline candidate.
7. **No delivery replacement.** Sidecar candidates cannot replace or enlarge the baseline artistic frontier or default delivery.
8. **Hard validity only.** Existing route-specific validity checks are applied. No diagnostic score, structural benchmark, human preference, or model judgment automatically promotes a sidecar candidate.
9. **Invalid consumes budget.** Each independent route-prior draw consumes one sidecar attempt; invalid draws are not retried.
10. **Explicit evidence-authorized route scope.** Eligibility is not inferred from registry membership or `intrinsic_dimension` metadata.
11. **Experimental registration remains local.** `orbit` remains outside the ordinary baseline registry and may be registered only for an explicit opt-in operation; process-global registry/checker state is restored afterward.
12. **Separate artifacts.** Sidecar candidates, report, timelines, and contact sheet live under `<out>/restart_sidecar/`.
13. **Explicit authority label.** Sidecar output is exploratory only and carries no automatic artistic-promotion authority.
14. **Record binding.** The sidecar report stores the SHA-256 digest of the exact `candidates.json` bytes.

## Runtime interface

The evidence-supported default budget is eight attempts per eligible active route:

```bash
python run.py \
  --brief brief.json \
  --seed 260826 \
  --out run-with-sidecar \
  --restart-sidecar 8
```

The feature itself remains opt-in. `8` means eight independent attempts for each active route in the exploratory sidecar authority set.

Baseline files remain ordinary outputs and are not rewritten:

```text
report.json
search_state.json
stage1_representatives.png
stage2_survivors.png
finalists.png
winner_timeline.png
```

The exploration surface remains separate:

```text
restart_sidecar/
├─ report.json
├─ candidates.json
├─ contact_sheet.png        # only when at least one valid candidate exists
└─ timelines/
   └─ <candidate>.png       # valid candidates only
```

## Reviewed-start handoff

A sidecar candidate may become the start of a **new isolated lineage** only after explicit external artistic selection and only when its active route is in the narrower reviewed-start authority set (`recurrence`, `orbit`, `filament`). This is not automatic promotion into the run that discovered it.

The handoff fails closed unless, among other provenance checks:

- authority string is explicit and exact;
- source report is a `restart-sidecar-v1` exploratory report with the baseline-isolation contract intact;
- source report carries an exact known historical/current sidecar authority snapshot;
- exact `candidates.json` SHA-256 matches the source report;
- selected candidates were hard-valid independent sidecar starts and reproduce their phenotype hashes;
- every active route belongs to the **reviewed-start** evidence-authorized set;
- every active route retains at least one explicitly selected start.

`family` and `sheet` therefore may be generated in the exploratory sidecar after #128 but remain rejected by reviewed-start handoff.

## Non-degradation claim

Baseline non-degradation is architectural: baseline search finishes before sidecar generation and its output files are not rewritten by the sidecar. Regression tests require byte-identical baseline artifacts with and without sidecar generation and exact restoration of temporary `orbit` registration.

This guarantee is narrower than artistic superiority. The sidecar may contain useful discoveries, weak discoveries, or no useful discoveries. It is a plural exploration surface, not a hidden winner-selection policy.
