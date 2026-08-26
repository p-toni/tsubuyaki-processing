# Executable Discovery State

Use this layer when a search lasts more than one small round and the agent needs to preserve **which mathematical move produced which phenotype**.

It is bookkeeping and guardrails, not an aesthetic optimizer.

## Components

```text
templates/mutation-grammar.json
  route -> stage -> allowed mutation classes

search-state.json
  brief invariants
  current stage
  elite
  candidate lineage
  review decisions
  unlock / promotion history

scripts/discovery-state.mjs
  enforces the state transitions
```

The state deliberately contains **no scalar beauty score**.

## Initialize

From repository root:

```sh
node scripts/discovery-state.mjs init _local/search-state.json \
  --route=filament \
  --elite=E0 \
  --brief="translucent larval ribbon" \
  --invariant="intentional axial / 1D identity" \
  --invariant="traveling internal deformation"
```

Routes currently encoded by the lightweight grammar:

```text
family
recurrence
sheet
filament
morphology
```

`templates/discovery-state.json` shows the file shape.

## Add a challenger

Only currently unlocked mutation classes are accepted:

```sh
node scripts/discovery-state.mjs add _local/search-state.json E1 \
  --parent=E0 \
  --class=numeric-frequency \
  --operator=secondaryFrequency \
  --artifact=_local/E1-f90.png \
  --note="stage-1 frequency perturbation"
```

Trying `--class=harmonic-family` during filament stage 1 fails because that class belongs to stage 2.

The mutation class is the **causal category**. `--operator` can name the concrete mathematical change.

## Review

Hard validity, brief adherence and aesthetic preference stay separate:

```sh
node scripts/discovery-state.mjs review _local/search-state.json E1 \
  --valid=pass \
  --adherent=pass \
  --preference=archive \
  --reason="valid but only a near-neighbor"
```

Allowed preference states:

```text
prefer
archive
reject
undecided
incumbent
```

`prefer` must mean the challenger survived **visual + temporal comparison against the current elite**. Do not derive it mechanically from density, novelty, framing or another critic.

## Unlock the next stage

Unlocks are sequential and require a reason:

```sh
node scripts/discovery-state.mjs unlock _local/search-state.json 2 \
  --reason="stage 1 produced only near-neighbors"
```

The grammar encodes strong safety rails from the experiments:

- filament stage 3 requires `--brief-change=true` because projection/topology change leaves the ordinary axial brief;
- morphology stage 3 requires `--experimental=true` because broad body-plan mutation is not established production policy.

Do not use those flags merely to bypass a locked stage.

## Promote a challenger

A candidate cannot become the elite unless:

```text
valid = pass
adherent = pass
preference = prefer
```

Then:

```sh
node scripts/discovery-state.mjs promote _local/search-state.json E7 \
  --reason="stronger segmented identity across matched times"
```

The old elite becomes `prior-elite`; it is not deleted. Future challengers default to the new elite as parent.

This gives the search an explicit lineage:

```text
E0 incumbent
├─ E1 numeric-frequency   -> archive
├─ E2 numeric-fold        -> reject
└─ E7 harmonic-family     -> promote
    ├─ E8 phase-relation
    └─ E9 fold-law
```

## Inspect / validate

```sh
node scripts/discovery-state.mjs summary _local/search-state.json
node scripts/discovery-state.mjs validate _local/search-state.json
```

`summary` reports the current elite, stage, unlocked classes and candidate-status counts.

`validate` checks basic state integrity, candidate parents, route/stage existence and mutation-class membership.

## What belongs in state

Record facts needed to reproduce a discovery decision:

- brief invariants;
- route and current unlock stage;
- candidate parent;
- mutation class and concrete operator;
- representative render artifacts;
- hard validity outcome;
- brief-adherence outcome;
- pairwise visual/temporal preference decision;
- why a stage was unlocked;
- why an elite was promoted.

Do **not** put a single aggregate quality score in the state.

If lightweight critics are used to reduce review volume, keep their outputs in separate diagnostic artifacts rather than turning them into promotion authority.

## What this is not

This layer does not yet define a universal mathematical genotype and does not mutate arbitrary p5.js automatically.

That is intentional.

The experiments support a common **search process** more strongly than they support one universal formula representation. The readable mathematical system remains the semantic source of truth; the agent maps its variables/operators onto the mutation classes appropriate to the selected route.

A future mutation engine can consume the same grammar/state once a stable cross-route genotype abstraction is established.
