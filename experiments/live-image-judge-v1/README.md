# Live image judge v1

## Purpose

Exercise the screened autonomous-discovery loop with real image-input judgment rather than deterministic/synthetic preference evidence.

This experiment is intentionally staged so visual decisions are made before route or candidate identity is revealed.

## Frozen setup

```text
brief: prototypes/autonomous-discovery/brief.json
seed: 260828
routes: all five currently registered screened representations
route probes: 2 per route
matched times: production TIMES
route verdicts: keep | drop | defer
candidate pending-review cap: 2
review source: independent multimodal model, blinded to route/candidate identity
```

## Protocol

### Phase 1 — blinded route screen

1. Reconstruct the five-route probe archive from the frozen seed.
2. Export the anonymous route screen with two exemplars per route across matched times.
3. Inspect only `route-screen.png` plus the artistic brief.
4. Persist keep/drop/defer judgments before opening `sealed-mapping.json`.

### Phase 2 — evidence-authoritative adaptive search

1. Reconstruct the exact probe archive and verify source + rendered phenotype prefixes.
2. Apply the persisted route evidence.
3. Allocate the remaining start budget only through the production route-allocation policy.
4. Run adaptive search with `EvidenceAuthoritySelector`, `max_pending_reviews=2`.
5. Export at most two newly reachable blinded candidate comparisons.
6. Judge those panels from image input, persist evidence, and replay.
7. Repeat until the search reaches a clear result or authoritative ties leave a genuine frontier.

## Evidence boundary

The reviewer must not use:

- route identity;
- candidate IDs;
- genomes;
- diagnostic scores;
- code length or compression information;
- sealed mappings before a visual decision is recorded.

The experiment is about whether the current five-route search can be driven by auditable visual evidence with low review volume. It is not a calibration of the deterministic proxy.

## Representation insufficiency trigger

Do not add a sixth representation merely because one screen is weak. A representation-family insufficiency claim requires repeated evidence that all five current routes fail to produce a viable/interesting frontier for the brief despite valid search and authoritative visual review.
