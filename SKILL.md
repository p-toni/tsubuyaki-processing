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
When organism-like structure can emerge from dynamics/harmonics/residue families without explicit anatomy, also load `references/math-first-generators.md`.

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

### Golf
Load `references/code-golf-techniques.md` only after selecting the winner.

## Default workflow

### 1. Build a viable incumbent

- choose kernel/topology;
- identify shared latent fields;
- identify family/residue law before individual parts;
- establish silhouette/material before microtexture;
- couple internal motion;
- render representative times and run visual/runtime diagnostics.

A generic torus/cloth, wire scribble, textbook attractor or detached body plan is a **representation failure**. Repair the cause before search.

### 2. Freeze brief invariants

Record only the constraints that define the requested niche, e.g.:

```text
multi-instance family → distinct related bodies from one generator
filament → intentional axial/1D identity
membrane → true 2D sheet + legible negative space
living knot → recurrent state + transformed projection
```

A beautiful mutation that violates a defining invariant is a side discovery, not the winner for the current request.

### 3. Search progressively by route

Route-aware policy controls **unlock order**, not a permanent mutation boundary.

Load `references/discovery-search.md` for the full schedules.

| representation | stage 1 | later unlocks |
|---|---|---|
| repeated math family | local family/deformation/harmonic search | family structure → selected projection changes |
| recurrence / living knot | broad recurrence/family roles | projection/deformation → broader recurrence variant |
| dense 2D sheet | projection/deformation family | sampling geometry / structural parameters |
| intentional 1D filament | local numeric search | axial-preserving harmonic/family/fold structure |
| morphology-first anatomy | local validated controls | limited contract-preserving family/attachment changes |

Only unlock a broader stage when the current stage produces no clearly better adherent challenger or appears saturated.

Do not unlock topology-breaking moves merely for novelty.

### 4. Preserve and promote the elite

The incumbent remains available in every round.

Search may improve, tie, or fail to improve it. Never force regression because search was attempted.

If a challenger is clearly better and brief-adherent, promote it to the new elite and normally search around it next.

### 5. Select after exploration

Novelty/coverage decides what deserves inspection, **not what wins**.

Review challengers at multiple representative times and compare them against the elite.

Keep these dimensions separate:

- brief adherence;
- aesthetic preference;
- mathematical leverage;
- temporal quality;
- distinctiveness;
- likely tweet viability.

Do not collapse them into one beauty score. Lightweight critics may reduce review volume, but visual/temporal judgment chooses the winner.

### 6. Validate only what needs validation

Validators are falsification tools, not creative fitness.

- repeated-family latent semantics → `scripts/check-family-math.mjs`
- rendered scope → `scripts/check-control-scope.mjs`
- simple visible effect → `scripts/check-control-effect.mjs`
- expanded→golfed compound survival → `scripts/check-morphology-survival.mjs`
- density/framing → `scripts/check-visual.mjs`

Use the relevant references for detailed contracts/commands.

### 7. Golf only the selected winner

Preserve the high-leverage mathematical relationships, compress semantically, then golf JavaScript.

Verify the complete post:

```sh
node scripts/check-length.mjs post.txt
```

`CODE//#つぶやきProcessing` leaves about **259 X-weighted characters for code**.

Render the exact tweet code and confirm the defining phenotype survived compression.

## Important mode-specific cautions

- Low occupancy can be correct for filaments and distributed families.
- High descriptor novelty can be actively harmful.
- Chaotic kernel perturbations can legitimately diverge globally; do not demand locality from them.
- Morphology is conditional, not the universal source of complexity.
- Do not hard-code the experiment's `4/8/16/24` budgets as production policy.
- For filaments, after numeric search saturates, unlock **axial-preserving** family/harmonic/fold structure before considering any projection/topology change.
- For sheets, start with projection/deformation but allow sampling/structural exploration when early gains saturate.

## Required output

Unless the user asks for less:

### Concept
One or two sentences.

### Mathematical plan
For math-first work: kernel, latent fields, family law, deformation and projection.

### Morphology plan
Only for explicit body-plan work.

### Discovery notes
State the incumbent, which search stages were explored/unlocked, and why the winner survived selection.

### Expanded p5.js
Readable winner.

### Tweet-ready
One executable line with valid hashtag placement.

### Verification
Raw + X-weighted length, representative-time visual diagnostics, plus relevant semantic/survival evidence when applicable.

### Variation knobs
3–5 high-leverage mathematical/morphological controls.

## Failure routing

- wire/confetti → topology/sample distribution
- generic torus/cloth → kernel/projection/body-plan failure; repair incumbent before search
- stage produces only near-neighbors → unlock next brief-preserving structural class
- broader stage repeatedly leaves brief → roll back to elite; do not reward novelty
- incumbent beats all mutations → keep incumbent; no improvement is valid
- filament numeric search saturates → unlock axial-preserving discrete structure, not radial projection
- aggregate effect passes but siblings disagree → math-family failure
- control leaks into unrelated anatomy → scope failure
- good readable phenotype loses identity after golf → compression-survival failure

A strong result comes from an **elite-preserving mathematical discovery process with progressive search depth**, not merely a better first guess.