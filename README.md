# tsubuyaki-processing

A production-oriented Agent Skill for authentic, tweet-sized **#つぶやきProcessing**: compact mathematical systems whose animated phenotype is disproportionately richer than the source.

## Current direction — progressive discovery with faithful provenance

The project treats generation as an **elite-preserving mathematical discovery process**:

```text
intent
→ compact representation
→ viable incumbent
→ brief invariants
→ progressive route-aware search
→ faithful causal lineage
→ visual + temporal selection
→ semantic checks where relevant
→ golf winner
→ exact verification
```

v0.10 established progressive route-aware search. v0.11 made elite/lineage state executable. v0.12 added compound-cause recording, evidence-backed unlocks, historical-stage validation and grammar pinning. v0.13 closes the remaining known ambiguity in that record without changing the search or aesthetic policy.

## v0.13 discovery-state evidence fidelity

### Paired causal changes

A candidate records each mutation class together with its concrete operator:

```sh
node scripts/discovery-state.mjs add _local/search-state.json E7 \
  --change=fold-frequency::ribFreq:0->0.85 \
  --change=latent-scale::sx:8.4->7.2
```

Stored form:

```json
"mutation": {
  "changes": [
    {"class": "fold-frequency", "operator": "ribFreq:0->0.85"},
    {"class": "latent-scale", "operator": "sx:8.4->7.2"}
  ]
}
```

This replaces ambiguous parallel `classes[]` / `operators[]` arrays.

Equal-count legacy `--class` / `--operator` CLI arguments are still accepted and converted immediately into paired changes; new work should use `--change=CLASS::OPERATOR`.

### Review-bound stage unlocks

Broadening search still requires reviewed evidence:

```sh
node scripts/discovery-state.mjs unlock _local/search-state.json 2 \
  --reason="stage 1 produced only near-neighbors" \
  --evidence=E8 \
  --evidence=E9
```

But the state now records the exact historical review event for each cited candidate:

```json
"evidence": [
  {"candidateId": "E8", "reviewSeq": 12},
  {"candidateId": "E9", "reviewSeq": 15}
]
```

Validation verifies that each review belongs to that candidate, came from the exhausted stage, was complete, and occurred before the unlock. Repointing an old unlock at an unrelated existing candidate therefore invalidates the state.

### Historical-stage legality + grammar provenance

Candidate changes are validated against the mutation permissions available at the candidate's historical stage.

Initialization also pins:

```json
"grammar": {
  "path": "templates/mutation-grammar.json",
  "version": 1,
  "sha256": "..."
}
```

Every later action verifies this exact rule set.

### State version

v0.13 uses discovery-state `version: 3`. v0.12 states fail closed because they do not contain paired causes or review-event-bound unlock evidence.

## Regression coverage

Run:

```sh
node scripts/test-discovery-state.mjs
```

The v0.13 regression checks:

- later-stage mutation classes fail while locked;
- unlocks without evidence fail;
- compound `{class, operator}` causes remain paired;
- unlock evidence points to the exact prior review event;
- promotion still requires validity + adherence + visual/temporal preference;
- filament topology change remains brief-gated;
- historical-stage corruption fails validation;
- malformed causal pairs fail validation;
- rewired / future review evidence fails validation;
- grammar-byte drift fails validation.

There is deliberately **no scalar beauty score**.

## Progressive route-aware search

The production unlock schedules remain unchanged:

### Repeated math family
1. local family/deformation/harmonic parameters;
2. family count, discrete harmonics, distance power, deformation operator;
3. selected projection changes while preserving the multi-instance niche.

### Recurrence / living knot
1. recurrence-role parameters + residue/family structure;
2. projection/deformation/time structure;
3. broader recurrence variant only when useful.

### Dense 2D sheet
1. projection/deformation family;
2. sampling geometry, latent x/y scale, fold-frequency structure;
3. broader sheet-compatible projection only while preserving sheetness.

### Intentional 1D filament / ribbon
1. local numeric tuning;
2. axial-preserving family/harmonic/fold structure;
3. projection/topology only when the brief changes.

### Morphology-first explicit anatomy
Use local validated controls first, then limited morphology-contract-preserving family/attachment exploration. Broad body-plan mutation remains experimental.

See:

```text
references/discovery-search.md
references/discovery-state.md
templates/mutation-grammar.json
scripts/discovery-state.mjs
```

## Selection principles

Elitism remains mandatory:

```text
elite + challengers
→ review
→ promote only a better brief-adherent challenger
```

Keep roles separate:

```text
hard validity → reject broken work
brief invariants → reject off-task work
novelty → diversify review candidates
validators → falsify claims
visual + temporal judgment → choose the art
state → preserve what actually happened
```

Novelty, occupancy and lightweight critics are not aesthetic fitness functions.

## Math-first representation

The strongest compact representation path remains:

```text
kernel → latent fields → family operator → nonlinear deformation → projection
```

Use explicit morphology only when the user actually needs named anatomy, attachment hierarchy or local editing.

## Evidence

Search experiments are preserved under:

```text
experiments/search-lab/
experiments/paired-route-search/
```

They justify progressive route-aware search; their diagnostic budgets/critics are not production requirements.

## Still unresolved

The project does not yet establish:

- exact unlock thresholds or candidate budgets;
- optimal mutation probabilities;
- independent LLM starts vs deeper search around one start;
- broad morphology-first structural search;
- an automatic aesthetic scorer;
- a universal cross-route genotype;
- fully autonomous candidate mutation.

The readable mathematical system remains the semantic source of truth.

## Tweet constraint

The recommended executable form `CODE//#つぶやきProcessing` leaves **259 X-weighted characters for code**.

Always verify the complete post:

```sh
node scripts/check-length.mjs post.txt
```

280 is a ceiling, not a target.

## Current thesis

> **good mathematical representation + progressive route-aware search + faithful causal provenance + brief-aware visual selection + elitism.**

The goal is to reliably discover a **large phenotype from a small mathematical cause** while preserving enough evidence to know how it was actually found.
