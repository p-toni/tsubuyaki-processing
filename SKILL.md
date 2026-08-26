---
name: tsubuyaki-processing
description: "Create authentic #つぶやきProcessing p5.js sketches: compact mathematical systems whose animated phenotype is disproportionately richer than the source. Discover a strong readable system, explore it with progressive route-aware elite-preserving search, then produce a verified <=280-character tweet version."
---

# Tsubuyaki Processing

Create **original #つぶやきProcessing**: a small mathematical cause producing a surprising, coherent animated phenotype.

The skill is a **discovery process**, not only a one-shot formula generator.

## Hard constraints

1. Complete post <=280 X-weighted characters and <=280 raw Unicode code points.
2. Use p5.js global mode unless asked otherwise.
3. Work in readable mathematical roles first; golf only after selection.
4. Prefer shared latent variables, recurrence, residue families and reusable generators over independent decorative effects.
5. Final code must execute.
6. 280 is a ceiling, not a target.
7. Do not reconstruct or lightly mutate a published artist's formula.

## Route before designing

Choose the **smallest mathematical representation that fits the request**.

### Single-field / abstract
Load `references/mathematical-patterns.md` + `references/style-guide.md`.

- flattened 2D for dense membrane/tissue;
- intentional 1D for filament/ribbon;
- iterative state for attractor/trajectory systems.

### Math-first emergent form
When structure can emerge from dynamics/harmonics/residue families without explicit anatomy, also load `references/math-first-generators.md`.

Think:

```text
kernel → latent coordinates → family operator → deformation → projection
```

Do not invent a scene graph merely because the output resembles an animal.

### Morphology-first explicit anatomy
When the user needs named regions, attachment hierarchy or local anatomical editing, load `references/morphology-composition.md`.

Core rule: **reusable roles, not literal nouns**.

### Explicit controllability
When semantic controls matter, additionally load:

- `references/control-strategies.md`
- `references/control-scopes.md`
- `references/semantic-effects.md`

### Quality-sensitive discovery
Load `references/discovery-search.md` once a viable incumbent exists.

For multi-round search, also load `references/discovery-state.md` and use `scripts/discovery-state.mjs`. The state is provenance + guardrails, not an aesthetic scorer.

### Golf
Load `references/code-golf-techniques.md` only after selecting the winner.

## Default workflow

### 1. Build a viable incumbent

- choose kernel/topology;
- identify shared latent fields and family/residue law;
- establish silhouette/material before microtexture;
- couple internal motion;
- render representative times and run visual/runtime diagnostics.

A generic torus/cloth, wire scribble, textbook attractor or detached body plan is a **representation failure**. Repair the cause before search.

### 2. Freeze brief invariants

Record only the constraints that define the niche, e.g.:

```text
multi-instance family → distinct related bodies from one generator
filament → intentional axial / 1D identity
membrane → true 2D sheet + legible negative space
living knot → recurrent state + transformed projection
```

A beautiful mutation that violates a defining invariant is a side discovery, not the winner.

### 3. Search progressively by route

Route-aware policy controls **unlock order**, not a permanent mutation boundary.

| representation | stage 1 | later unlocks |
|---|---|---|
| repeated math family | local family/deformation/harmonic | family structure → selected projection |
| recurrence / living knot | recurrence/family roles | projection/deformation → broader recurrence |
| dense 2D sheet | projection/deformation | sampling geometry / structural parameters |
| intentional 1D filament | local numeric | axial-preserving harmonic/family/fold structure |
| morphology-first anatomy | local validated controls | limited contract-preserving family/attachment changes |

Only unlock a broader stage when the current stage has reviewed evidence of saturation/no preferable adherent challenger.

Do not unlock topology-breaking moves merely for novelty.

### 4. Preserve faithful discovery state

For multi-round search:

- pin the mutation grammar version + SHA-256 at initialization;
- record **all** causal mutation classes for a candidate, not only one convenient label;
- record concrete mathematical operators separately;
- attach representative artifacts;
- keep validity, adherence and preference separate;
- cite reviewed candidate IDs as evidence for every stage unlock;
- preserve prior elites and parentage.

Example compound cause:

```sh
node scripts/discovery-state.mjs add _local/search-state.json E7 \
  --class=fold-frequency \
  --class=latent-scale \
  --operator="ribFreq:0->0.85" \
  --operator="sx:8.4->7.2"
```

Historical legality matters: a candidate may only claim mutation classes that were already unlocked at its recorded stage.

### 5. Preserve and promote the elite

The incumbent remains available in every round. Search may improve, tie or fail; never force regression.

Promote only after:

```text
valid = pass
adherent = pass
preference = prefer
```

`prefer` means visual + temporal comparison against the elite—not a scalar critic.

### 6. Select after exploration

Novelty/coverage decides what deserves inspection, **not what wins**.

Keep these dimensions separate:

- brief adherence;
- aesthetic preference;
- mathematical leverage;
- temporal quality;
- distinctiveness;
- likely tweet viability.

### 7. Validate only what needs validation

Validators are falsification tools, not creative fitness.

- discovery-state integrity → `node scripts/discovery-state.mjs validate STATE`
- repeated-family latent semantics → `scripts/check-family-math.mjs`
- rendered scope → `scripts/check-control-scope.mjs`
- simple visible effect → `scripts/check-control-effect.mjs`
- expanded→golfed compound survival → `scripts/check-morphology-survival.mjs`
- density/framing → `scripts/check-visual.mjs`

### 8. Golf only the selected winner

Preserve high-leverage mathematical relationships, compress semantically, then golf JavaScript.

Verify the complete post:

```sh
node scripts/check-length.mjs post.txt
```

`CODE//#つぶやきProcessing` leaves about **259 X-weighted characters for code**.

Render the exact tweet code and confirm the defining phenotype survived compression.

## Important cautions

- Low occupancy can be correct for filaments and distributed families.
- High descriptor novelty can be actively harmful.
- Chaotic kernel perturbations can legitimately diverge globally; do not demand locality from them.
- Morphology is conditional, not the universal source of complexity.
- Do not hard-code experiment budgets as production policy.
- Filament stage 3 requires an actual brief change.
- Morphology body-plan mutation remains experimental.
- If the pinned mutation grammar changes during a search, start/migrate a new state rather than silently reinterpreting history.

## Required output

Unless the user asks for less:

### Concept
One or two sentences.

### Mathematical plan
For math-first work: kernel, latent fields, family law, deformation and projection.

### Morphology plan
Only for explicit body-plan work.

### Discovery notes
Summarize the recorded elite lineage, search stages, compound causal changes and evidence-backed unlocks.

### Expanded p5.js
Readable winner.

### Tweet-ready
One executable line with valid hashtag placement.

### Verification
Raw + X-weighted length, representative-time visual diagnostics, discovery-state validation when used, plus relevant semantic/survival evidence.

### Variation knobs
3–5 high-leverage mathematical/morphological controls.

## Failure routing

- wire/confetti → topology/sample distribution
- generic torus/cloth → representation failure; repair incumbent before search
- stage produces only near-neighbors → review them, cite them as unlock evidence, then unlock next brief-preserving class
- broader stage leaves brief → roll back to elite; do not reward novelty
- incumbent beats all mutations → keep incumbent; no improvement is valid
- mutation record omits a real causal change → discovery-state fidelity failure
- historical candidate claims a later-stage class → discovery-state integrity failure
- grammar pin changes → search-rule provenance failure
- aggregate effect passes but siblings disagree → math-family failure
- control leaks into unrelated anatomy → scope failure
- readable phenotype loses identity after golf → compression-survival failure

A strong result comes from an **elite-preserving mathematical discovery process with faithful causal provenance**, not merely a better first guess.
