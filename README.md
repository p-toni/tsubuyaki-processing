# tsubuyaki-processing

A production-oriented Agent Skill for authentic, tweet-sized **#つぶやきProcessing**: compact mathematical systems whose animated phenotype is disproportionately richer than the source.

## v0.11 direction — progressive discovery with explicit state

The project now treats generation as an **elite-preserving mathematical discovery process** rather than a one-shot formula generator.

Two search experiments established the production policy:

1. search matters, but one universal structural-search policy is wrong;
2. route-aware search should control the **order** in which mathematical degrees of freedom are unlocked, not permanently restrict the search space.

The current pipeline is:

```text
intent
→ compact representation
→ viable incumbent
→ brief invariants
→ progressive route-aware search
→ explicit elite / lineage state when multi-round
→ visual + temporal selection
→ semantic checks where relevant
→ golf winner
→ exact verification
```

## Progressive route-aware search

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
3. broader sheet-compatible projection only if the brief remains intact.

### Intentional 1D filament / ribbon

1. local numeric tuning;
2. axial-preserving family count / harmonic family / fold law;
3. projection/topology change only when the requested niche changes.

### Morphology-first explicit anatomy

Evidence remains incomplete. Use local validated controls first, then limited morphology-contract-preserving family/attachment exploration. Broad body-plan search remains experimental.

See `references/discovery-search.md` for the complete policy.

## Executable discovery state

v0.11 adds a lightweight state/grammar layer for multi-round discovery:

```text
templates/mutation-grammar.json
scripts/discovery-state.mjs
templates/discovery-state.json
references/discovery-state.md
```

It records:

- route and current unlock stage;
- brief invariants;
- current elite and prior elites;
- candidate parentage;
- mutation class + concrete mathematical operator;
- representative render artifacts;
- validity / brief-adherence review;
- visual-temporal preference decision;
- stage unlock and promotion history.

It deliberately does **not** contain a scalar beauty score.

Example:

```sh
node scripts/discovery-state.mjs init _local/search-state.json \
  --route=filament \
  --elite=E0 \
  --brief="translucent larval ribbon" \
  --invariant="intentional axial / 1D identity"

node scripts/discovery-state.mjs add _local/search-state.json E1 \
  --class=numeric-frequency \
  --operator=secondaryFrequency

node scripts/discovery-state.mjs unlock _local/search-state.json 2 \
  --reason="stage 1 produced only near-neighbors"
```

The CLI enforces the search schedule. A locked mutation class cannot be added; unlocks are sequential; filament topology changes require an explicit brief change; experimental morphology body-plan search requires explicit opt-in; and candidates cannot become elite until validity, adherence and visual/temporal preference all pass.

This is intentionally **not** yet a universal genotype/mutation engine. The experiments support a common search process more strongly than they support one formula representation across recurrence, sheets, filaments, families and explicit morphology.

## Elitism is mandatory

Every round retains the current incumbent:

```text
elite
+ challengers
→ inspect
→ promote only a better brief-adherent challenger
```

Search may improve, tie or fail. It must never force regression.

When a challenger wins, it becomes the natural center of the next search stage while prior elites remain available as lineage evidence.

## Novelty and critics are not quality

Behavioral diversity is useful for deciding what deserves inspection. It is not the final objective.

The paired experiment also showed that lightweight framing/density/temporal critics can disagree with visual preference.

Therefore:

```text
hard validity → reject broken work
brief invariants → reject off-task work
novelty → diversify review candidates
validators → falsify claims
visual + temporal judgment → choose the art
```

Do not collapse these into one scalar aesthetic fitness.

## Math-first representation remains central

The strongest compact representation path remains:

```text
kernel → latent fields → family operator → nonlinear deformation → projection
```

See `references/math-first-generators.md`.

When repeated-family semantics matter, `scripts/check-family-math.mjs` can inspect each generator instance before rasterization.

## Morphology remains conditional

Use explicit morphology when the user needs named anatomy, attachment hierarchy or local editing.

The project does **not** treat morphology as the universal source of complexity. A small indirect mathematical generator may produce richer phenotypes precisely because it does not explicitly encode every visible part.

## Validation stack

Validators remain falsification tools, not creative fitness functions:

```text
check-family-math      → did repeated generator instances change coherently?
check-control-scope    → did rendered change stay in allowed structure?
check-control-effect   → did a simple visible observable move as intended?
visual/temporal review → is the phenotype actually worth keeping?
morphology survival    → did defining structure survive golf?
```

## Evidence

The first search experiment is preserved under:

```text
experiments/search-lab/
```

The paired route-policy experiment is preserved under:

```text
experiments/paired-route-search/
```

Those experiments justify the progressive unlock policy; their diagnostic budgets and critics are not production requirements.

## What is intentionally not hard-coded

The evidence still does not establish:

- exact unlock thresholds;
- optimal candidate budgets or mutation probabilities;
- independent LLM starts versus deeper search around one start;
- broad structural search for morphology-first anatomy;
- an automatic aesthetic scorer;
- a universal cross-route genotype;
- candidate-level continuous autonomous optimization.

## Tweet constraint

The recommended executable form `CODE//#つぶやきProcessing` leaves **259 X-weighted characters for code**.

Always verify the complete post:

```sh
node scripts/check-length.mjs post.txt
```

280 is a ceiling, not a target.

## Current thesis

The strongest current model is:

> **good mathematical representation + progressive route-aware search + explicit discovery lineage + brief-aware visual selection + elitism.**

The goal is to reliably discover a **large phenotype from a small mathematical cause**.
