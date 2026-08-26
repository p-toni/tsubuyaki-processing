---
name: tsubuyaki-processing
description: "Create authentic #つぶやきProcessing p5.js sketches: dense mathematical, organic, point-based animated forms compressed to a tweet-sized program. Use for Tsubuyaki Processing, tweet-sized p5.js, mathematical creature/floral forms, controllable compound organisms, or code-golfed generative art. Produce an original readable sketch plus a verified <=280-character tweet version."
---

# Tsubuyaki Processing

Create **original #つぶやきProcessing**, not generic generative art that happens to be short. The output should feel larger than its source: a compact mathematical cause producing a surprisingly rich phenotype.

## Hard constraints

1. Complete post <=280 X-weighted characters and <=280 raw Unicode code points.
2. Use p5.js global mode unless asked otherwise.
3. Design readable source first; golf only after rendering and visual judgment.
4. Prefer shared latent variables, recurrence, and reusable generators over independent decorative effects.
5. Final code must execute.
6. 280 is a ceiling, not a target.
7. Do not reconstruct or lightly mutate a published artist's formula.

## Route before designing

Choose the **smallest mathematical representation that fits the request**.

### A. Single-field / abstract form

Load `references/mathematical-patterns.md` + `references/style-guide.md`.

- flattened 2D for dense membrane/tissue;
- 1D deliberately for filament/ribbon material;
- iterated state for attractor/trajectory systems.

### B. Math-first emergent organism

When an organism-like form can emerge from compact dynamics, harmonics, residue families, or nonlinear projection **without explicit anatomy**, load:

- `references/math-first-generators.md`
- `references/mathematical-patterns.md`

Think:

```text
kernel → latent coordinates → family operator → deformation → projection
```

Do not invent a scene graph merely because the output resembles an animal. Strong tiny-code forms often derive apparent anatomy from a dynamical kernel or one phase-conditioned family generator.

### C. Morphology-first compound organism

When the user explicitly needs differentiated regions, attachment, body-plan hierarchy, or named anatomy, also load `references/morphology-composition.md`.

Core rule: **reusable roles, not literal nouns**. One attached appendage-family generator is better than separate formulas for each appendage.

### D. Explicitly controllable compound / repeated-family system

When named semantic controls or controllability evaluation are required, additionally load:

- `references/control-strategies.md`
- `references/control-scopes.md`
- `references/semantic-effects.md`

Use the strongest available source of truth:

- **math-family effect** — how repeated generator instances changed in latent space;
- **scope** — where the rendered change was allowed;
- **image/mask effect** — simple phenotype observable when useful;
- **visual judgment** — whether the phenotype is actually good.

### E. Code golf / tweet-ready output

After the readable system is stable, load `references/code-golf-techniques.md`.

## Base generation loop

1. Choose kernel/topology.
2. Identify shared latent fields (`k/e/d/c/p/q/t` or equivalent).
3. If repetition exists, identify the family law (`i%N`, parity, phase class) before naming individual parts.
4. Establish silhouette/coherence before microtexture. Generic toroidal cloth is a structural failure, not a frequency-tuning problem.
5. Couple internal motion rather than rigidly transforming a static object.
6. Render representative frames with `templates/harness.html?frame=90&s=your-sketch.js`.
7. Run `scripts/check-visual.mjs` for density/framing diagnostics.
8. Validate semantic controls before golf.
9. Compress semantically, golf, and verify the complete post with `scripts/check-length.mjs`.
10. For compound work, test defining morphology through expanded → exact-golfed compression.

## Math-first contract

Before equations, identify:

- **kernel** — recurrence / 1D / 2D / attractor;
- **latent fields** — the small coordinate/state vocabulary;
- **family law** — instance expression/count if repeated;
- **deformation** — nonlinear field creating differentiation;
- **projection** — how latent state reaches screen coordinates;
- **time entry points** — where animation changes kernel, deformation, or projection.

Prefer controls attached to these mathematical roles over arbitrary canvas offsets.

For recurrence-driven work, distinguish the underlying dynamical state from its projection. A chaotic kernel parameter can legitimately change the entire future trajectory; do not apply local-family expectations to it.

## Pure math probes for repeated families

When repeated family semantics matter, expose a design-time pure probe. Use `templates/math-probe.mjs` as the interface pattern:

```js
{
  family:'arms',
  instance:3,
  x:...,y:...,
  latent:{radial:...,axial:...,phase:...}
}
```

Then validate a control directly in latent space:

```sh
node scripts/check-family-math.mjs \
  probe.mjs math-contract.json armLength --factor=1.2
```

A coherent repeated-family control should usually show:

- the intended median per-instance change;
- high directional agreement across siblings;
- reasonable dispersion/MAD when coherent family response is intended.

This catches aggregate-image cheats where a few siblings grow dramatically while others shrink.

The probe and contract are **design-time artifacts only**. They never consume tweet characters.

## Morphology-first invariants

For explicit body plans, write a short morphology contract: polarity, root mass, regions, organ families, symmetry/repetition, parent-relative attachment, inherited motion and surface detail.

Preserve:

- more apparent parts than independent formulas;
- children inherit parent structure;
- structure and surface are separable in readable code;
- repeated siblings share one generator;
- morphology remains optional for attractors, math-first emergent forms, simple filaments and abstract sheets.

## Semantic control validation

Perturb one readable control at a time at the **same time/frame**.

### 1. Generator semantics — what changed mathematically?

For repeated families with a meaningful latent identity, prefer `effect.source="math-family"` and run `check-family-math.mjs`.

Use this to validate family-wide latent roles such as radial extent, axial extent, phase, or another explicit probe field.

### 2. Scope — where did the rendered change occur?

```sh
node scripts/check-control-scope.mjs \
  baseline.png variant.png morphology-contract.json controlName \
  --baseline-mask-dir=baseline-masks \
  --variant-mask-dir=variant-masks
```

For moving geometry, allowed support is the **union of baseline and variant masks**. `subtree` applies that union to the region and descendants. Use spill comparatively; do not broaden masks merely to improve a score.

### 3. Simple phenotype effect — did a visible observable move?

When useful:

```sh
node scripts/check-control-effect.mjs \
  baseline.png variant.png morphology-contract.json controlName \
  --baseline-mask-dir=baseline-masks \
  --variant-mask-dir=variant-masks
```

Mask/image descriptors remain useful for width, height, area, centroid, contrast, or visibility. For repeated families, math-family validation is stronger than one aggregate bounding box.

A control is semantically convincing when **math + scope + visible effect + visual judgment** are mutually consistent.

## Morphology survival through golf

For compound pieces, declare defining `survivalFeatures`:

- `presence` — defining mass/family should remain represented;
- `void` — cavity/split should remain open.

Render feature masks for **both expanded and golfed phenotypes** and run:

```sh
node scripts/check-morphology-survival.mjs \
  expanded.png golfed.png morphology-contract.json \
  --expanded-feature-dir=expanded-features \
  --golfed-feature-dir=golfed-features
```

Review feature existence/scale/placement and appearance separately. Do not collapse survival into one similarity score.

## Visual diagnostics

```sh
node scripts/check-visual.mjs frame-0.png frame-90.png frame-180.png
```

Useful dense-organic heuristics:

- `<2%` occupancy: likely wire/sparse unless intentionally filamentary
- `2–4%`: inspect carefully
- `4–15%`: common useful territory, not a hard target
- `>15%`: inspect for overfill/lost cavities
- robust dominant span `<55%`: often framed too small
- centroid offset `>15%`: inspect composition
- edge contact: inspect clipping

Sample count is not density.

## Tweet budget

`#つぶやきProcessing` costs 19 X-weighted characters. Recommended `CODE//#つぶやきProcessing` leaves **259 weighted characters for CODE**.

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

### Expanded p5.js
Readable source with semantic controls.

### Tweet-ready
One executable line with a valid hashtag placement.

### Verification
Raw + X-weighted length, visual diagnostics, and when applicable: math-family response, scope spill, simple effect result, and feature-wise survival.

### Variation knobs
3–5 meaningful mathematical/morphological controls.

## Failure routing

- wire/confetti → topology/sample distribution
- generic torus/cloth → kernel/projection/body-plan failure
- emergent math is coherent but explicit anatomy is hard to edit → add morphology layer only where needed
- floating parts → attachment/local frame
- high dual-state spill → dependency/scope failure
- low spill but wrong aggregate effect → semantic-effect failure
- aggregate effect passes but siblings disagree → math-family failure
- chaotic recurrence diverges globally → classify control as kernel/global; do not force locality
- good readable phenotype loses defining regions/voids after golf → compression-survival failure

A strong result should encode a **large phenotype in a small mathematical cause**.