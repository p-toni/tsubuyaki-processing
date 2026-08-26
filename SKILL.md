---
name: tsubuyaki-processing
description: "Create authentic #つぶやきProcessing p5.js sketches: dense mathematical, organic, point-based animated forms compressed to a tweet-sized program. Use for Tsubuyaki Processing, tweet-sized p5.js, mathematical creature/floral forms, controllable compound organisms, or code-golfed generative art. Produce an original readable sketch plus a verified <=280-character tweet version."
---

# Tsubuyaki Processing

Create **original #つぶやきProcessing**, not generic generative art that happens to be short. The output should feel larger than its source: a compact mathematical system whose sampling, body coordinates, deformation and motion produce a coherent organism or field.

## Hard constraints

1. Complete post <=280 X-weighted characters and <=280 raw Unicode code points.
2. Use p5.js global mode unless asked otherwise.
3. Design readable source first; golf only after rendering and visual judgment.
4. Prefer shared latent variables and reusable generators over independent decorative effects.
5. Final code must execute.
6. 280 is a ceiling, not a target.
7. Do not reconstruct or lightly mutate a published artist's formula.

## Route before designing

Choose the **smallest workflow that fits the request**.

### A. Single-field / abstract dense form
Load `references/mathematical-patterns.md` + `references/style-guide.md`. Default dense tissue to flattened 2D; use 1D deliberately for filament/ribbon material and iterated state for trajectory systems.

### B. Compound organism
When the prompt asks for differentiated regions, appendages, symmetry or attachment, also load `references/morphology-composition.md`.

Core rule: **reusable roles, not literal nouns**. One attached appendage-family generator is better than separate formulas for each appendage.

### C. Explicitly controllable compound organism
When named semantic controls or controllability evaluation are required, additionally load:

- `references/control-strategies.md`
- `references/control-scopes.md`
- `references/semantic-effects.md`

Each tested control may declare:

- **scope** — where influence is allowed (`region`, `subtree`, `surface`, `global`);
- **effect** — what observable should change (`width`, `height`, `area`, centroid, contrast, visibility) and in which direction.

Validate scope and effect independently.

### D. Code golf / tweet-ready output
After the readable system is stable, load `references/code-golf-techniques.md`.

## Base generation loop

1. Choose material/topology.
2. Build shared body coordinates (`k/e/d/c/q/t` or equivalent).
3. Establish silhouette/polarity before texture. Generic toroidal cloth is a **body-plan failure**, not a frequency-tuning problem.
4. Couple internal motion rather than rigidly transforming a static object.
5. Render representative frames with `templates/harness.html?frame=90&s=your-sketch.js`.
6. Run `scripts/check-visual.mjs` for density/framing diagnostics.
7. For compound controls, validate semantic behavior before golf.
8. Compress semantically, golf, and verify the complete post with `scripts/check-length.mjs`.
9. For compound work, test defining morphology through expanded → exact-golfed compression.

## Compound morphology invariants

Write a short morphology contract before equations: polarity, root mass, regions, organ families, symmetry/repetition, parent-relative attachment, inherited motion and surface detail.

Preserve:

- more apparent parts than independent formulas;
- children inherit parent structure;
- structure and surface are separable in readable code;
- repeated siblings share a generator but can vary through continuous body fields;
- morphology remains optional for attractors, simple filaments and abstract sheets.

## Semantic control validation

Perturb one readable control at a time at the **same frame/time** and render both baseline and variant region masks.

### 1. Scope: where did it change?

```sh
node scripts/check-control-scope.mjs \
  baseline.png variant.png morphology-contract.json controlName \
  --baseline-mask-dir=baseline-masks \
  --variant-mask-dir=variant-masks
```

For moving geometry, allowed support is the **union of baseline and variant masks**. `subtree` applies that union to the region and descendants. Use spill ratio comparatively; do not optimize masks/dilation to manufacture low spill.

### 2. Effect: did it change the intended observable?

If the control has an `effect` descriptor:

```sh
node scripts/check-control-effect.mjs \
  baseline.png variant.png morphology-contract.json controlName \
  --baseline-mask-dir=baseline-masks \
  --variant-mask-dir=variant-masks
```

Examples:

- `finSpan` → fin-region mask width should increase;
- `tailLength` → tail-region mask height should increase;
- attachment position → declared centroid axis should move;
- rib/surface strength → contrast or visible fraction should materially change.

A control is semantically convincing only when **scope + effect + visual judgment** agree. Low spill alone proves only dependency locality.

## Morphology survival through golf

For compound pieces, declare defining `survivalFeatures` as:

- `presence` — root/wing/appendage family should remain visibly represented;
- `void` — cavity/split should remain open.

Render feature masks for **both expanded and golfed phenotypes** at the same frame. The harness exposes:

```text
?feature=featureName
```

Then run:

```sh
node scripts/check-morphology-survival.mjs \
  expanded.png golfed.png morphology-contract.json \
  --expanded-feature-dir=expanded-features \
  --golfed-feature-dir=golfed-features
```

State-aware survival compares each feature in its own phenotype support: area, width/height, normalized centroid shift and appearance. Do not collapse this into one similarity score. Fixed-mask mode is legacy only because it can falsely penalize a feature that survives but moves during golf.

If a defining feature disappears or materially collapses after golf, restore the high-leverage generator and remove lower-value detail.

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

### Morphology plan
Only for compound work: root, regions, families, attachment/symmetry and motion inheritance.

### Expanded p5.js
Readable source with semantic controls.

### Tweet-ready
One executable line with a valid hashtag placement.

### Verification
Raw + X-weighted length, visual diagnostics, and for controllable compound work: scope spill, declared-effect result, and feature-wise morphology-survival notes.

### Variation knobs
3–5 meaningful mathematical/morphological controls.

## Failure routing

- wire/confetti → topology/sample distribution
- generic torus/cloth → root polarity/body plan
- floating parts → attachment/local frame
- everything equally loud → hierarchy/envelopes
- high dual-state spill → dependency/scope failure
- low spill but wrong effect descriptor → semantic-control failure
- good readable phenotype loses defining regions/voids after golf → compression-survival failure

A strong result should resemble a **small developmental program**, not a miniature conventional scene graph.