# Executable Discovery State

Use this layer when discovery lasts more than one small round and the agent needs a reproducible record of **which mathematical changes produced which phenotype, under which search rules, and why search depth changed**.

It is scientific bookkeeping and guardrails, not an aesthetic optimizer.

## Components

```text
templates/mutation-grammar.json
  route -> stage -> allowed mutation classes

search-state.json
  pinned grammar identity
  brief invariants
  current stage
  elite + lineage
  paired causal changes
  review decisions
  review-bound unlock evidence
  promotion history

scripts/discovery-state.mjs
  enforces state transitions and historical legality
```

The state deliberately contains **no scalar beauty score**.

## Initialize and pin the grammar

```sh
node scripts/discovery-state.mjs init _local/search-state.json \
  --route=sheet \
  --elite=E0 \
  --brief="abstract folded membrane" \
  --invariant="true 2D sheet sampling" \
  --invariant="legible negative space"
```

Initialization pins the grammar path, version and SHA-256. Every later command verifies the exact pin. Grammar drift invalidates the old state rather than silently changing its search rules.

Routes currently encoded:

```text
family
recurrence
sheet
filament
morphology
```

## Add a challenger with paired causal changes

One phenotype may result from several mathematical changes. Each causal class is stored together with its concrete operator:

```sh
node scripts/discovery-state.mjs add _local/search-state.json E7 \
  --parent=E1 \
  --change=fold-frequency::ribFreq:0->0.85 \
  --change=latent-scale::sx:8.4->7.2,sy:8.0->8.8 \
  --artifact=_local/E7-f90.png
```

State shape:

```json
"mutation": {
  "changes": [
    {"class": "fold-frequency", "operator": "ribFreq:0->0.85"},
    {"class": "latent-scale", "operator": "sx:8.4->7.2,sy:8.0->8.8"}
  ]
}
```

This avoids parallel `classes[]` / `operators[]` arrays whose pairing could become ambiguous.

For command compatibility, equal-count repeated `--class` and `--operator` arguments are still accepted and are immediately converted into paired `changes`. Prefer `--change=CLASS::OPERATOR` for new work.

A class not unlocked at the current stage is rejected at write time.

## Review

Keep validity, brief adherence and aesthetic preference separate:

```sh
node scripts/discovery-state.mjs review _local/search-state.json E7 \
  --valid=pass \
  --adherent=pass \
  --preference=archive \
  --reason="valid but only a near-neighbor"
```

Preference values:

```text
prefer
archive
reject
undecided
incumbent
```

`prefer` must come from visual + temporal comparison with the current elite, not from a density/novelty/critic scalar.

Each review is an event with its own sequence number.

## Unlock with historical review evidence

An unlock must cite reviewed candidates that justify broadening search:

```sh
node scripts/discovery-state.mjs unlock _local/search-state.json 2 \
  --reason="stage 1 around E1 produced only near-neighbors" \
  --evidence=E8 \
  --evidence=E9
```

At write time each evidence candidate must be a reviewed challenger from the current stage. The unlock records the exact review event that existed at that moment:

```json
{
  "type": "unlock",
  "stage": 2,
  "reason": "...",
  "evidence": [
    {"candidateId": "E8", "reviewSeq": 12},
    {"candidateId": "E9", "reviewSeq": 15}
  ]
}
```

Validation later reconstructs that history. It checks that:

- the candidate existed in the exhausted stage (`unlock.stage - 1`);
- `reviewSeq` names a review event for that exact candidate;
- the review happened before the unlock event;
- the cited review was complete rather than `unknown` / `undecided`.

This means an unlock cannot later be rewritten to point at an unrelated existing candidate without invalidating the state.

Strong guards remain:

- filament stage 3 requires `--brief-change=true`;
- morphology stage 3 requires `--experimental=true`.

## Promote a challenger

Promotion still requires:

```text
valid = pass
adherent = pass
preference = prefer
```

```sh
node scripts/discovery-state.mjs promote _local/search-state.json E7 \
  --reason="stronger membrane identity across matched times"
```

The former elite becomes `prior-elite`; it remains in lineage evidence.

## Historical legality

`validate` checks every paired causal change against the mutation classes available at the candidate's **historical stage**.

A manually edited record like this fails even after the search later reaches stage 2:

```json
{
  "stage": 1,
  "mutation": {
    "changes": [
      {"class": "harmonic-family", "operator": "5->7"}
    ]
  }
}
```

## Inspect / validate

```sh
node scripts/discovery-state.mjs summary _local/search-state.json
node scripts/discovery-state.mjs validate _local/search-state.json
```

`validate` checks:

- state version / basic integrity;
- grammar version + SHA-256 pin;
- route and stage existence;
- candidate parentage;
- paired mutation shape;
- historical-stage legality;
- strictly ordered events;
- unlock evidence candidate/stage identity;
- exact historical review-event identity and ordering.

## Schema version

v0.13 uses discovery state `version: 3`.

v0.12 (`version: 2`) states fail closed rather than being silently reinterpreted because their parallel causal arrays and candidate-ID-only unlock evidence do not contain enough information to guarantee the v0.13 provenance model.

## What belongs in state

Record facts needed to reproduce a discovery decision:

- brief invariants;
- pinned grammar path/version/hash;
- route and current stage;
- candidate parent;
- paired causal `{class, operator}` changes;
- representative artifacts;
- validity and brief-adherence review;
- pairwise visual/temporal preference;
- unlock reason + exact cited review events;
- promotion reason.

Do **not** put one aggregate quality score in the state.

If a lightweight critic reduces review volume, keep its output in separate diagnostic artifacts rather than giving it promotion authority.

## What this is not

This layer still does not define one universal mathematical genotype or automatically mutate arbitrary p5.js.

That remains intentional. Current evidence supports a common **search process and provenance record** more strongly than it supports one formula representation across recurrence, sheets, filaments, repeated families and explicit morphology.

The readable mathematical system remains the semantic source of truth. v0.13 closes the remaining known ambiguity in causal pairing and unlock-history evidence; further state machinery should require a concrete failure from a real discovery run.
