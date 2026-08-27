# Judge calibration v1 — independent human audit

## Why this exists

Recent preference-search experiments increasingly attributed regressions to non-transitivity and temporal aliasing. A blinded human calibration showed a more fundamental confound: the same model that generated most of the pairwise artistic labels is not sufficiently aligned with an independent human judge to serve as ground truth for fine-grained promotion.

This record separates two calibration layers:

1. fine-grained within-route candidate preference (v10);
2. coarse five-representation choice (v11).

No production policy change is justified from this calibration alone.

## v10 — fine-grained candidate audit

Eight blinded A/B temporal pairs were reviewed by Toni. After the initial review, Toni explicitly marked rows 1, 2, and 5 low-confidence because they were hard to visualize. The remaining five are the strong calibration subset.

Strong human choices:

| brief | human preference | interpretation |
|---|---|---|
| petal-current | FC9 | deeper family challenger |
| turbulent-cord | RC8 | deeper recurrence challenger |
| rooted-choir | FN1 | anchor family candidate |
| drawn-thread | LN7 | deeper filament challenger |
| smoke-clasp | OC2 | anchor orbit candidate |

Against the later model preference used in the preceding diagnosis, agreement on the strong subset was only **1/5** (`drawn-thread`).

Interpretation: do not use this same model as promotion ground truth for near-neighbor artistic selection.

## v11 — coarse representation audit

Five larger A–E panels compared one phenotype from each research representation. Toni marked only `tension-stroke` low-confidence; the other four are treated as strong calibration.

The audit compositor did not persist its sealed row→route mapping as a machine artifact. The mapping below is reconstructable from the representation-specific phenotypes, but this procedural gap means v11 is exploratory calibration, not confirmatory evidence. Future audits must persist the sealed mapping mechanically.

| brief | A | B | C | D | E | human | confidence |
|---|---|---|---|---|---|---|---|
| twisted-current | sheet | recurrence | orbit | filament | family | **filament** | strong |
| wounded-halo | orbit | sheet | family | filament | recurrence | **sheet** | strong |
| echo-cluster | family | orbit | sheet | recurrence | filament | **sheet** | strong |
| punctured-membrane | filament | sheet | family | orbit | recurrence | **recurrence** | strong |
| tension-stroke | orbit | filament | sheet | recurrence | family | **orbit** | low |

The prior model/experiment treated the intended representation as recurrence, orbit, family, sheet, and filament respectively. Human winner agreement is therefore **0/4 on the strong subset**.

However, the brief-only semantic top-2 still contains the human choice in 3/4 strong cases:

- twisted-current: recurrence / filament → contains human filament;
- wounded-halo: orbit / sheet → contains human sheet;
- echo-cluster: family / sheet → contains human sheet;
- punctured-membrane: sheet / orbit → **misses human recurrence**.

So the 66/66 model-grounded shortlist result should be downgraded from “validated containment” to “promising semantic eligibility heuristic requiring independent replication.”

## Architecture consequence

Split the system into three evidence domains:

```text
text semantics
→ conservative representation eligibility set

hard mathematical checks
→ validity / invariant enforcement

independent preference evidence
→ artistic promotion
```

Same-model judgments and deterministic proxies may triage/review-order candidates, but should not be sufficient promotion evidence.

Low-confidence human judgments should also fail closed to `defer` rather than being counted as clear wins.

## Prototype follow-up

`preference_evidence.py` and `review_evidence_queue.py` implement a new v3 evidence layer without altering the legacy v2 replay path:

- explicit source class + source id;
- explicit strong/low/defer confidence;
- same-model/proxy evidence is advisory only;
- low-confidence evidence cannot promote;
- conflicting authoritative evidence defers;
- repeated votes from one source do not become independent evidence;
- queue artifacts persist brief, temporal horizon, phenotype fingerprints, sealed mapping, provenance, and confidence.
