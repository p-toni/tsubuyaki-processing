# tsubuyaki-processing

A production-oriented Agent Skill for authentic, tweet-sized **#つぶやきProcessing**: compact mathematical systems whose animated phenotype is disproportionately richer than the source.

## Current direction — discovery first, deployment pressure later

The project treats generation as an **elite-preserving mathematical discovery process with adaptive deployment promotion**:

```text
intent
→ compact representation
→ viable incumbent
→ brief invariants
→ progressive route-aware search
→ faithful causal lineage
→ visual + temporal ranking
→ adaptive compression-survival preflight
→ deployment finalist
→ golf
→ exact verification
```

v0.10 established progressive route-aware search. v0.11 made elite/lineage state executable. v0.12–v0.13 made causal/search provenance faithful. The description-length experiments then showed that character pressure belongs **after artistic ranking but before deployment commitment**.

## v0.14 adaptive compression-survival promotion

Description length is now treated as a **deployment constraint on promotion**, not a creative-search objective.

The production policy is:

```text
visual / temporal ranking
→ preflight current best
   ├─ survives compression → deployment finalist
   └─ fails → preserve artistic discovery and try next-ranked candidate
→ full golf
→ exact survival verification
```

The key distinction is:

```text
fits <=280 != defining phenotype survived
```

A candidate can fit the character limit and still fail because the compact form removed the relationships that made the expanded phenotype good.

### No fixed shortlist size

The adaptive follow-up found that rank 2 was enough in the tested archive, but the production rule is **not** `top 2`.

Preflight candidates sequentially in visual-rank order and stop at the first one whose defining mathematical relationships survive plausible compact representation.

Continue only while remaining candidates are still artistically worth deployment.

### No compression fitness

Do not add character count, compressibility, tweetability or description length to creative fitness.

Keep the roles separate:

```text
hard validity → reject broken work
brief invariants → reject off-task work
novelty → diversify review candidates
visual + temporal judgment → rank the art
discovery state → preserve what actually happened
compression survival → gate deployment promotion
```

See `references/compression-promotion.md`.

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

The state records the exact historical review event for each cited candidate:

```json
"evidence": [
  {"candidateId": "E8", "reviewSeq": 12},
  {"candidateId": "E9", "reviewSeq": 15}
]
```

Validation verifies that each review belongs to that candidate, came from the exhausted stage, was complete, and occurred before the unlock.

### Historical-stage legality + grammar provenance

Candidate changes are validated against the mutation permissions available at the candidate's historical stage.

Initialization pins the grammar version and exact SHA-256, so later grammar changes cannot silently reinterpret an old search record.

v0.13 uses discovery-state `version: 3`.

## Progressive route-aware search

The production unlock schedules remain:

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
references/compression-promotion.md
templates/mutation-grammar.json
scripts/discovery-state.mjs
```

## Math-first representation

The strongest compact representation path remains:

```text
kernel → latent fields → family operator → nonlinear deformation → projection
```

Use explicit morphology only when the user actually needs named anatomy, attachment hierarchy or local editing.

## Evidence

Search and deployment experiments are preserved under:

```text
experiments/search-lab/
experiments/paired-route-search/
experiments/description-length-pressure/
```

The description-length timing experiment found:

- late-only pressure: 3 / 4 deployable winners;
- shortlist preflight: 4 / 4;
- early compactness filtering: 4 / 4 while removing 17 / 48 candidates before artistic review.

The adaptive follow-up found the same deployment outcome with sequential fallback and no universal shortlist K.

These experiments justify production policy; their candidate counts, diagnostic budgets and critic proxies are not production constants.

## Still unresolved

The project does not yet establish:

- exact unlock thresholds or candidate budgets;
- optimal mutation probabilities;
- independent LLM starts vs deeper search around one start;
- broad morphology-first structural search;
- morphology-first compression-preflight behavior;
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

> **good mathematical representation + progressive route-aware search + faithful causal provenance + brief-aware visual ranking + adaptive compression-survival deployment promotion.**

The goal is to reliably discover a **large phenotype from a small mathematical cause** without making description length suppress the creative search that discovers it.
