# Executable Discovery State

Use this layer when discovery lasts more than one small round and the agent needs a reproducible record of **which mathematical changes produced which phenotype, under which search rules, and why search depth changed**.

It is scientific bookkeeping and guardrails, not an aesthetic optimizer.

## v0.13 fidelity model

v0.13 binds two relationships that v0.12 only represented indirectly:

```text
mutation class <-> concrete operator
unlock evidence <-> historical review event
```

The state still contains **no scalar beauty score**.

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

## Initialize and pin the grammar

```sh
node scripts/discovery-state.mjs init _local/search-state.json \
  --route=sheet \
  --elite=E0 \
  --brief="abstract folded membrane" \
  --invariant="true 2D sheet sampling" \
  --invariant="legible negative space"
```

Initialization records the grammar path, version and exact SHA-256. Every later command verifies the pin.

## Add a challenger with bound causal changes

`--class` and `--operator` remain repeatable for CLI ergonomics, but they must be supplied in **equal counts** and are stored as paired objects:

```sh
node scripts/discovery-state.mjs add _local/search-state.json E7 \
  --parent=E1 \
  --class=fold-frequency \
  --operator="ribFreq:0->0.85" \
  --class=latent-scale \
  --operator="sx:8.4->7.2, sy:8.0->8.8"
```

State:

```json
"mutation": {
  "changes": [
    {"class": "fold-frequency", "operator": "ribFreq:0->0.85"},
    {"class": "latent-scale", "operator": "sx:8.4->7.2, sy:8.0->8.8"}
  ]
}
```

This prevents the provenance ambiguity of two parallel arrays whose elements could be reordered independently.

Every change class must be legal at the candidate's historical stage.

## Review

Keep validity, brief adherence and aesthetic preference separate:

```sh
node scripts/discovery-state.mjs review _local/search-state.json E7 \
  --valid=pass \
  --adherent=pass \
  --preference=archive \
  --reason="valid but only a near-neighbor"
```

`prefer` must come from visual + temporal comparison with the current elite, not from a scalar critic.

Review events record the decision as it existed at that point in history.

## Unlock with historically bound evidence

```sh
node scripts/discovery-state.mjs unlock _local/search-state.json 2 \
  --reason="stage 1 around E1 produced only near-neighbors" \
  --evidence=E8 \
  --evidence=E9
```

At write time, each evidence candidate must be a reviewed challenger from the current stage.

The unlock records both candidate identity and the exact review-event sequence that justified the decision:

```json
{
  "type": "unlock",
  "stage": 2,
  "reason": "...",
  "evidence": [
    {"candidateId": "E8", "reviewSeq": 14},
    {"candidateId": "E9", "reviewSeq": 16}
  ]
}
```

This is stronger than citing the candidate alone. If E8 is reviewed again later, the stage-2 unlock still points to what was actually known at sequence 14.

Validation requires that each evidence binding:

- names an existing candidate;
- comes from candidate stage `unlock.stage - 1`;
- points to an actual review event for that same candidate;
- points to a review event that occurred before the unlock;
- points to a completed review rather than unknown/undecided state.

Strong route guards remain:

- filament stage 3 requires `--brief-change=true`;
- morphology stage 3 requires `--experimental=true`.

## Promote a challenger

Promotion still requires:

```text
valid = pass
adherent = pass
preference = prefer
```

The former elite becomes `prior-elite`; it remains in lineage evidence.

## Historical legality

`validate` checks every `mutation.changes[].class` against the permissions available at `candidate.stage`, not against the route's eventual full vocabulary.

A stage-1 candidate cannot retroactively claim a stage-2 change merely because the search later unlocked stage 2.

## Inspect / validate

```sh
node scripts/discovery-state.mjs summary _local/search-state.json
node scripts/discovery-state.mjs validate _local/search-state.json
```

Validation covers:

- state version and basic integrity;
- grammar version + SHA-256 pin;
- route/stage existence;
- candidate parentage;
- paired causal-change shape;
- historical-stage legality;
- strictly ordered events;
- unlock evidence bindings to historical review events.

## Schema compatibility

v0.13 state is `version: 3`.

v0.12 `version: 2` states fail closed rather than being silently upgraded. They do not contain guaranteed class/operator pairing or review-event bindings, so silently reinterpreting them would defeat the purpose of this release.

## What belongs in state

Record:

- brief invariants;
- pinned grammar path/version/hash;
- route and current stage;
- candidate parent;
- paired mathematical changes (`class` + `operator`);
- representative artifacts;
- validity / adherence / visual-temporal preference;
- unlock reason + historically bound evidence;
- promotion reason.

Do **not** add one aggregate quality score.

## What this is not

This layer still does not define one universal genotype or automatically mutate arbitrary p5.js.

The readable mathematical system remains the semantic source of truth. The state layer exists to make the exploration around it inspectable without pretending that provenance is the same thing as aesthetic judgment.
