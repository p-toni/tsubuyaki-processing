# tsubuyaki-processing

A production-oriented Agent Skill for authentic, tweet-sized **#つぶやきProcessing**: compact mathematical systems whose animated phenotype is disproportionately richer than the source.

## v0.12 direction — faithful discovery provenance

The project treats generation as an **elite-preserving mathematical discovery process**:

```text
intent
→ compact representation
→ viable incumbent
→ brief invariants
→ progressive route-aware search
→ explicit causal lineage
→ visual + temporal selection
→ semantic checks where relevant
→ golf winner
→ exact verification
```

v0.10 established progressive route-aware search. v0.11 made its elite/lineage state executable. The dense-sheet validation then exposed a provenance weakness: one winning phenotype can result from several mathematical changes, while the old state recorded only one `mutation.class`; unlock reasons also had no explicit evidence links, and validation did not enforce the rules that existed at a candidate's historical stage.

v0.12 fixes that layer without changing the aesthetic/search policy.

## v0.12 discovery-state fidelity

The multi-round state now records and enforces:

### Compound mathematical causes

A candidate may record multiple causal classes and concrete operators:

```sh
node scripts/discovery-state.mjs add _local/search-state.json E7 \
  --class=fold-frequency \
  --class=latent-scale \
  --operator="ribFreq:0->0.85" \
  --operator="sx:8.4->7.2, sy:8.0->8.8"
```

The state stores:

```json
"mutation": {
  "classes": ["fold-frequency", "latent-scale"],
  "operators": ["ribFreq:0->0.85", "sx:8.4->7.2, sy:8.0->8.8"]
}
```

At least one explicit operator is required. The state should preserve the mathematical cause, not merely label a picture as "structurally mutated."

### Evidence-backed stage unlocks

Broadening search must cite reviewed candidates from the current stage:

```sh
node scripts/discovery-state.mjs unlock _local/search-state.json 2 \
  --reason="stage 1 around E1 produced only near-neighbors" \
  --evidence=E8 \
  --evidence=E9
```

Unlock history therefore contains both the reasoning and the candidate IDs that support it.

### Historical-stage legality

Validation checks a candidate against the mutation classes available **when that candidate was created**.

A stage-1 filament candidate cannot later claim `harmonic-family` merely because the search eventually reached stage 2.

### Pinned mutation grammar

Initialization pins the rule system:

```json
"grammar": {
  "path": "templates/mutation-grammar.json",
  "version": 1,
  "sha256": "..."
}
```

Every subsequent CLI action verifies the version and exact SHA-256. A grammar change therefore cannot silently reinterpret an existing search history.

## Regression coverage

Run:

```sh
node scripts/test-discovery-state.mjs
```

The v0.12 regression checks:

- locked mutation classes fail at write time;
- unlocks without reviewed evidence fail;
- compound mutation classes/operators survive state writes;
- elite promotion still requires validity + adherence + visual/temporal preference;
- filament topology change remains brief-gated;
- manual historical-stage corruption fails validation;
- grammar-byte drift fails validation.

There is still deliberately **no scalar beauty score**.

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
