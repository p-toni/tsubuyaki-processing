# Live image judge v1

## Purpose

Exercise the screened autonomous-discovery loop with real image-input judgment rather than deterministic/synthetic preference evidence, and audit whether that judgment has the provenance required for artistic authority.

The experiment was staged so visual decisions were made before route or candidate identity was revealed.

## Frozen setup

```text
brief: prototypes/autonomous-discovery/brief.json
seed: 260828
routes: all five currently registered screened representations
route probes: 2 per route
matched times: production TIMES
candidate pending-review cap: 2
reviewer: GPT-5.6 Sol in the same conversation driving this research
```

## Blinded route screen

The reviewer saw only the anonymous route panel and artistic brief. Before the sealed route mapping was opened, the visual judgments were:

```text
A keep
B drop
C keep
D defer
E drop
```

After sealing the decisions, the mapping was revealed as:

```text
A = sheet
B = orbit
C = family
D = recurrence
E = filament
```

The judgments themselves remain useful as **same-model advisory observations**.

## Provenance correction

The initial experiment record incorrectly classified the conversational reviewer as `independent-model`.

That is inconsistent with `experiments/judge-calibration-v1`, which found that the same model producing/reasoning about the search is not sufficiently aligned with independent human preference to act as artistic ground truth. The correct source class is:

```text
same-model
```

Therefore:

- the route `drop` judgments cannot authorize hard pruning;
- the route `keep` judgments may be used only as advisory ordering/focus signals;
- the candidate-level judgments cannot authorize artistic promotion;
- the adaptive replay that treated these decisions as `independent-model` is **invalid as authoritative search evidence**.

All committed decision files have been corrected to `same-model` and retain an explicit provenance-correction record rather than hiding the original mistake.

## Candidate-review observation

Before the provenance issue was noticed, the misclassified replay produced four lazy-review batches (`K=2`). All eight blinded candidate comparisons were visually judged ties and, after their decisions were sealed, were found to come from the same recurrence/axial neighborhood.

This **does not establish an artistic result**. It does reveal a separate operational issue worth testing independently:

```text
global lazy cap + route-ordered traversal
→ early route can repeatedly fill the review batch
→ later routes may receive no reviewer attention
```

That scheduler hypothesis is isolated in `experiments/route-balanced-review-v1` and is calibrated with synthetic decisions only, so it does not depend on treating these same-model artistic judgments as authoritative.

## What this experiment supports

Supported:

- the image-input review bridge works end to end;
- blinded decisions can be recorded before sealed mappings are opened;
- same-model image review can provide advisory observations and expose operational failures;
- source-class provenance must be checked before route pruning or candidate promotion.

Not supported:

- dropping orbit or filament for this brief;
- promoting sheet or family as authoritative winners;
- any candidate-level artistic promotion;
- representation-family insufficiency or sufficiency from this run.

## Next evidence boundary

Authoritative artistic conclusions still require either:

1. strong human review; or
2. a genuinely independent model/reviewer whose provenance is distinct from the model driving the search.

Until that evidence exists, same-model image judgments may triage and order review work but must fail closed for artistic promotion.
