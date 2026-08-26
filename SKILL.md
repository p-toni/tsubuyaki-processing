---
name: tsubuyaki-processing
description: "Create authentic #つぶやきProcessing p5.js sketches: compact mathematical systems whose animated phenotype is disproportionately richer than the source. Use for tweet-sized p5.js, mathematical organic forms, emergent creatures, controllable morphology, or code-golfed generative art. Discover a strong readable system, explore it with a route-aware elite-preserving search policy, then produce a verified <=280-character tweet version."
---

# Tsubuyaki Processing

Create **original #つぶやきProcessing**, not generic generative art that happens to be short.

The target is:

> a small mathematical cause that produces a surprising, coherent animated phenotype.

Do not assume the first valid formula is the final answer. First establish a viable **incumbent**, then explore around it with the search policy appropriate to its mathematical representation.

## Hard constraints

1. Complete post <=280 X-weighted characters and <=280 raw Unicode code points.
2. Use p5.js global mode unless asked otherwise.
3. Work in readable mathematical roles first; golf only after discovery/selection.
4. Prefer shared latent variables, recurrence, residue families and reusable generators over independent decorative effects.
5. Final code must execute.
6. 280 is a ceiling, not a target.
7. Do not reconstruct or lightly mutate a published artist's formula.

## Route before designing

Choose the **smallest mathematical representation that fits the request**.

### A. Single-field / abstract form

Load `references/mathematical-patterns.md` + `references/style-guide.md`.

- flattened 2D for dense membrane/tissue;
- intentional 1D for filament/ribbon material;
- iterated state for attractor/trajectory systems.

### B. Math-first emergent organism

When organism-like structure can emerge from compact dynamics, harmonics, residue families or nonlinear projection without explicit anatomy, also load:

- `references/math-first-generators.md`

Think:

```text
kernel → latent coordinates → family operator → deformation → projection
```

Do not invent a scene graph merely because the result resembles an animal.

### C. Morphology-first compound organism

When the user explicitly needs differentiated regions, attachment hierarchy, body-plan constraints or named anatomy, load:

- `references/morphology-composition.md`

Core rule: **reusable roles, not literal nouns**.

### D. Explicit controllability

When named semantic controls or controllability evaluation matter, additionally load:

- `references/control-strategies.md`
- `references/control-scopes.md`
- `references/semantic-effects.md`

Use the strongest source of truth available:

- math-family latent response;
- rendered scope/locality;
- simple mask/image effect;
- visual judgment.

### E. Discovery search

For quality-sensitive generation, load:

- `references/discovery-search.md`

Search **after** a viable incumbent exists, never instead of solving a broken representation.

### F. Code golf

After a winner is selected, load:

- `references/code-golf-techniques.md`

## Default discovery workflow

### 1. Build an incumbent

1. Choose kernel/topology.
2. Identify shared latent fields (`k/e/d/c/p/q/t` or equivalent).
3. If repetition exists, identify the family law (`i%N`, parity, phase class) before naming individual parts.
4. Establish silhouette/coherence before microtexture.
5. Couple internal motion rather than rigidly transforming a static object.
6. Render representative times.
7. Run visual/runtime diagnostics.

A generic torus/cloth, wire scribble, detached anatomy or textbook attractor is a **representation failure**. Repair the mathematical cause before starting broad search.

Once the system is clearly viable, freeze it as the incumbent/elite.

### 2. Freeze brief invariants

Write the smallest constraints that define the user's requested niche.

Examples:

```text
multi-instance family → distinct related bodies from one generator
filament → intentional axial/1D identity
dense membrane → true 2D sheet + legible negative space
living knot → recurrent state + materially transformed projection
```

A beautiful search result that violates a defining invariant can be kept as a side discovery, but it does not replace the incumbent for the current request.

### 3. Search according to route

Use `references/discovery-search.md` for details.

**Repeated math family**
- structural + parameter exploration is useful;
- explore family count/phase, latent harmonics, distance/deformation roles and selected projection changes;
- preserve the multi-instance/family niche.

**Recurrence / living knot**
- structural divergent search is strongly useful;
- explore recurrence roles, family/residue structure, deformation and projection;
- do not require locality from chaotic kernel parameters.

**Dense 2D sheet**
- actively explore projection/deformation family;
- projection changes can access high-value disconnected niches.

**Intentional 1D filament/ribbon**
- preserve incumbent;
- local numeric search first;
- avoid broad projection/topology mutation unless the incumbent fails or the request calls for it.

**Morphology-first explicit anatomy**
- evidence for broad structural search is incomplete;
- preserve the body plan and search conservatively through controls/family parameters/motion until dedicated evidence supports more.

### 4. Preserve elitism

The incumbent remains in every comparison.

Search may:

```text
improve incumbent
≈ tie incumbent
fail to improve incumbent
```

It must never force a regression by discarding a strong existing solution.

### 5. Use novelty only for exploration

Behavioral diversity can help choose what deserves review, but:

```text
novel != good
more coverage != better art
higher occupancy != success
```

Do not select the winner from descriptor novelty alone.

### 6. Select challengers visually and temporally

After a search round:

1. reject hard failures;
2. preserve a small behaviorally diverse review set;
3. inspect multiple representative times;
4. compare challengers against the incumbent;
5. replace the elite only when a challenger is brief-adherent and aesthetically preferable.

Prefer the pairwise question:

> If only one candidate could receive another round of exploration, which would you keep?

Keep these judgment dimensions separate:

- brief adherence;
- aesthetic preference;
- mathematical leverage;
- temporal quality;
- distinctiveness;
- likely tweet viability.

Do not collapse them into a universal beauty score.

### 7. Stage search effort

Search matters, but the optimal budget is not yet established.

Do not blindly require 24 candidates. Start with a small exploration round and expand only while useful new niches appear.

Stop when:

- the incumbent remains clearly stronger;
- mutations are merely parameter-neighbors;
- structural candidates repeatedly leave the brief;
- quality gains appear saturated;
- the winner is ready for golf.

## Math-first contract

Before equations, identify:

- **kernel** — recurrence / 1D / 2D / attractor;
- **latent fields** — the small coordinate/state vocabulary;
- **family law** — instance expression/count if repeated;
- **deformation** — nonlinear field creating differentiation;
- **projection** — how latent state reaches screen coordinates;
- **time entry points** — where animation changes kernel, deformation or projection.

Prefer controls/mutations attached to these mathematical roles over arbitrary canvas offsets.

## Pure math probes for repeated families

When repeated-family semantics matter, expose a design-time pure probe using `templates/math-probe.mjs` as the interface pattern:

```js
{
  family:'arms',
  instance:3,
  x:...,y:...,
  latent:{radial:...,axial:...,phase:...}
}
```

Then validate directly in latent space:

```sh
node scripts/check-family-math.mjs \
  probe.mjs math-contract.json armLength --factor=1.2
```

Use per-instance median response, directional agreement and dispersion to catch aggregate-family cheats.

The probe is a design-time artifact and never consumes tweet characters.

## Morphology-first invariants

For explicit body plans, write a short morphology contract: polarity, root mass, regions, organ families, symmetry/repetition, parent-relative attachment, inherited motion and surface detail.

Preserve:

- more apparent parts than independent formulas;
- children inherit parent structure;
- repeated siblings share one generator;
- structure and surface remain separable in readable code;
- morphology remains optional for emergent math, simple filaments and abstract sheets.

## Semantic validation

Validation is for **falsification**, not discovery fitness.

### Generator semantics

For repeated families, prefer `effect.source="math-family"` and `check-family-math.mjs` when an explicit latent role exists.

### Rendered scope

```sh
node scripts/check-control-scope.mjs \
  baseline.png variant.png morphology-contract.json controlName \
  --baseline-mask-dir=baseline-masks \
  --variant-mask-dir=variant-masks
```

Use dual-state mask support for moving geometry.

### Simple phenotype effect

When useful:

```sh
node scripts/check-control-effect.mjs \
  baseline.png variant.png morphology-contract.json controlName \
  --baseline-mask-dir=baseline-masks \
  --variant-mask-dir=variant-masks
```

A semantic control is convincing when math + scope + visible effect + visual judgment agree.

## Compression survival

For compound work, render defining `presence` / `void` feature masks for both expanded and golfed phenotypes and run:

```sh
node scripts/check-morphology-survival.mjs \
  expanded.png golfed.png morphology-contract.json \
  --expanded-feature-dir=expanded-features \
  --golfed-feature-dir=golfed-features
```

Do not collapse survival into one similarity score.

## Visual diagnostics

```sh
node scripts/check-visual.mjs frame-0.png frame-90.png frame-180.png
```

Heuristics are mode-dependent:

- `<2%` occupancy can be wrong for dense tissue but intentional for filaments/multi-instance constellations;
- `4–15%` is common useful territory for dense point material, not a target;
- dominant span `<55%` can indicate weak framing for a single body, but not necessarily for distributed families;
- inspect clipping, centering, cavities and temporal stability directly.

Sample count is not density.

## Golf only the selected winner

Search the mathematical cause, not minified syntax.

Then:

1. preserve the winner's high-leverage generator/deformation/projection relationships;
2. compress semantically;
3. golf JavaScript;
4. verify the complete post;
5. render the exact tweet code and confirm the phenotype survived.

`#つぶやきProcessing` costs 19 X-weighted characters. Recommended `CODE//#つぶやきProcessing` leaves **259 weighted characters for code**.

```sh
node scripts/check-length.mjs post.txt
```

## Required output

Unless the user asks for less, return:

### Concept
One or two sentences.

### Mathematical plan
For math-first work: kernel, latent fields, family law, deformation and projection.

### Morphology plan
Only when explicit body-plan structure is used.

### Discovery notes
Briefly state the incumbent and which route-specific alternatives were explored/why the winner survived selection.

### Expanded p5.js
Readable winner.

### Tweet-ready
One executable line with valid hashtag placement.

### Verification
Raw + X-weighted length, representative-frame visual diagnostics, and applicable semantic/survival evidence.

### Variation knobs
3–5 high-leverage mathematical/morphological controls.

## Failure routing

- wire/confetti → topology/sample distribution
- generic torus/cloth → kernel/projection/body-plan failure; repair incumbent before search
- emergent math coherent but explicit anatomy hard to edit → add morphology only where needed
- broad search leaves brief → tighten invariants / route policy, not aesthetic score
- incumbent beats all mutations → keep incumbent; search is allowed to return no improvement
- filament structural search creates loops/flowers → return to axial incumbent/local parameters
- high dual-state spill → dependency/scope failure
- aggregate effect passes but siblings disagree → math-family failure
- chaotic recurrence diverges globally → classify kernel control as global
- good readable phenotype loses defining structure after golf → compression-survival failure

A strong result should come from an **elite-preserving mathematical discovery process**, not merely a better first guess.