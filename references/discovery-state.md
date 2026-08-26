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
  compound mutation cause
  review decisions
  evidence-backed unlock / promotion history

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

Initialization records:

```json
"grammar": {
  "path": "templates/mutation-grammar.json",
  "version": 1,
  "sha256": "..."
}
```

Every later command verifies that both the grammar version and exact file bytes still match this pin. If the grammar changes, the old search state no longer silently inherits new rules.

Routes currently encoded:

```text
family
recurrence
sheet
filament
morphology
```

## Add a challenger with its complete cause

A phenotype can result from more than one mathematical change. Record all causal classes and the concrete operators that matter:

```sh
node scripts/discovery-state.mjs add _local/search-state.json E7 \
  --parent=E1 \
  --class=fold-frequency \
  --class=latent-scale \
  --operator="ribFreq:0->0.85" \
  --operator="sx:8.4->7.2, sy:8.0->8.8" \
  --artifact=_local/E7-f90.png
```

`--class` and `--operator` are repeatable.

The classes are causal categories governed by the unlock grammar. Operators record the concrete mathematical edit. At least one explicit operator is required; the state should not claim reproducibility while only saying "some fold mutation happened."

A class that is not unlocked at the current stage is rejected at write time.

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

## Unlock with evidence

An unlock is a causal decision and must cite the reviewed candidates that justify broadening search:

```sh
node scripts/discovery-state.mjs unlock _local/search-state.json 2 \
  --reason="stage 1 around E1 produced only near-neighbors" \
  --evidence=E8 \
  --evidence=E9
```

Evidence candidates must:

- exist;
- be searched challengers rather than the original incumbent;
- belong to the current stage;
- have completed review.

The unlock event records:

```json
{
  "type": "unlock",
  "stage": 2,
  "reason": "...",
  "evidenceCandidateIds": ["E8", "E9"]
}
```

This makes "why did we expose broader structure?" inspectable instead of relying on conversational memory.

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

`validate` no longer asks only whether a mutation class exists somewhere in the route.

It checks whether every class recorded for a candidate was already unlocked at that candidate's **historical stage**.

Therefore a manually edited state like:

```text
candidate.stage = 1
mutation.classes = ["harmonic-family"]   # filament stage-2 class
```

fails validation even if the current search has since reached stage 2.

This protects the scientific record from retroactively granting earlier candidates permissions they did not have.

## Inspect / validate

```sh
node scripts/discovery-state.mjs summary _local/search-state.json
node scripts/discovery-state.mjs validate _local/search-state.json
```

`summary` includes the pinned grammar identity, elite, stage, unlocked classes and candidate/status counts.

`validate` checks:

- state version / basic integrity;
- grammar version + SHA-256 pin;
- route and stage existence;
- candidate parentage;
- compound mutation shape;
- historical-stage legality of all mutation classes;
- event ordering;
- evidence references on unlock events.

## What belongs in state

Record facts needed to reproduce a discovery decision:

- brief invariants;
- pinned grammar path/version/hash;
- route and current stage;
- candidate parent;
- all causal mutation classes;
- concrete mathematical operators;
- representative artifacts;
- validity and brief-adherence review;
- pairwise visual/temporal preference;
- unlock reason + evidence candidate IDs;
- promotion reason.

Do **not** put one aggregate quality score in the state.

If a lightweight critic reduces review volume, keep its output in separate diagnostic artifacts rather than giving it promotion authority.

## What this is not

This layer still does not define one universal mathematical genotype or automatically mutate arbitrary p5.js.

That remains intentional. Current evidence supports a common **search process and provenance record** more strongly than it supports one formula representation across recurrence, sheets, filaments, repeated families and explicit morphology.

The readable mathematical system remains the semantic source of truth; v0.12 makes the discovery record faithful enough to inspect and reproduce the search decisions around it.
