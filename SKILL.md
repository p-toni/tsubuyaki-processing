---
name: tsubuyaki-processing
description: "Create authentic #つぶやきProcessing p5.js sketches: dense mathematical, organic, point-based animated forms compressed to a tweet-sized program. Use for Tsubuyaki Processing, tweet-sized p5.js, mathematical creature/floral forms, controllable compound organisms, or code-golfed generative art. Produce an original readable sketch plus a verified <=280-character tweet version."
---

# Tsubuyaki Processing

Create **original #つぶやきProcessing**, not generic generative art that happens to be short.

The output should feel larger than its source: a compact mathematical system whose sampling, body coordinates, deformation and motion produce a coherent organism or field.

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

Load:

- `references/mathematical-patterns.md`
- `references/style-guide.md`

Default dense tissue/sheet material to flattened 2D sampling. Use 1D deliberately for filaments/ribbons/axial curves, and iterative state for trajectory-driven forms.

### B. Compound organism

Only when the prompt asks for differentiated regions, appendages, symmetry or attachment, also load:

- `references/morphology-composition.md`

Core rule: **reusable roles, not literal nouns**. “Four instances of one attached appendage family” is better than “draw tentacle 1, tentacle 2, …”.

### C. Explicitly controllable compound organism

When the prompt also requires named semantic controls or controllability evaluation, additionally load:

- `references/control-strategies.md`
- `references/control-scopes.md`

Declare each tested control's expected influence as `region`, `subtree`, `surface` or `global`. Use region masks and `scripts/check-control-scope.mjs` to measure unexpected spill outside that declared scope.

### D. Code golf / tweet-ready output

After the readable system is stable, load:

- `references/code-golf-techniques.md`

For historical/community precedent, load `references/real-examples.md` only as needed.

## Base generation loop

1. **Choose material/topology.** 2D sheet for membrane/tissue; 1D for deliberate filament/ribbon; iterative state for attractor/trajectory material.
2. **Build shared body coordinates.** Reuse compact latent variables such as lateral/radial `k`, axial `e`, distance `d`, phase `c`, radius/offset `q`, and one master clock `t`.
3. **Create hierarchy before texture.** Establish a recognizable silhouette and polarity before micro-folds. If the result is generic toroidal cloth, fix the body plan rather than adding detail.
4. **Couple internal motion.** Prefer phase drift, breathing, folding and region deformation over rigid rotation/translation.
5. **Render representative frames.** Use `templates/harness.html?frame=90&s=your-sketch.js`. The bundled `p5-lite.js` works offline for the common point/circle/line subset; use `&full=1` only when full p5.js APIs are required and network access is available.
6. **Inspect image-space behavior.** Run `scripts/check-visual.mjs`; treat metrics as diagnostics, not universal aesthetic gates.
7. **Only then compress semantically and code-golf.** Verify the final complete post with `scripts/check-length.mjs`.

## Compound morphology gate

For a compound organism, write a short morphology contract before equations:

- polarity/main axis
- root mass
- named regions
- repeated organ families
- symmetry/repetition law
- parent-relative attachment
- motion inheritance
- surface detail

Then follow `references/morphology-composition.md`. Do not duplicate its workflow here.

Preserve these invariants:

- **Complexity is factorized.** More apparent parts than independent formulas.
- **Children inherit parent structure.** Appendages should remain attached as the root moves.
- **Structure and surface are separable in readable code.** Body-plan controls should not be hidden inside unrelated texture constants.
- **Repetition has variation.** Combine residue identity with continuous body fields rather than exact cloning.
- **Morphology is optional.** Do not force this machinery onto an attractor, filament, or abstract field that does not need it.

## Scope-aware semantic-control testing

For explicitly controllable compound work:

1. define a small readable set of semantic controls;
2. declare the region hierarchy and each control's expected scope in a morphology contract;
3. perturb one control at a time at the **same frame/time**;
4. render baseline, variant, and matching region masks;
5. run:

```sh
node scripts/check-control-scope.mjs baseline.png variant.png morphology-contract.json controlName
```

Interpretation:

- `region` — influence should stay mainly in one named region;
- `subtree` — influence may propagate through that region and descendants;
- `surface` — spatially local to a region but intended as appearance/deformation rather than body-plan structure;
- `global` — organism-wide influence is expected.

Use **spill ratio** as comparative evidence: lower spill means more of the observed change stayed inside the declared region/subtree. Do not optimize spill to zero blindly; attachment boundaries, overlap and antialiasing create legitimate cross-region effects.

The older `scripts/check-control.mjs` remains useful as a global diff diagnostic, but it is not a semantic locality validator.

## Visual diagnostics

Run:

```sh
node scripts/check-visual.mjs frame-0.png frame-90.png frame-180.png
```

Optional robust-bbox quantiles:

```sh
node scripts/check-visual.mjs frame.png --quantiles=.01,.99
```

Useful dense-organic heuristics:

- `<2%` occupancy: likely wire/sparse unless intentionally filamentary
- `2–4%`: inspect carefully
- `4–15%`: common useful territory, not a hard target
- `>15%`: inspect for overfill/lost cavities
- robust dominant span `<55%`: often framed too small
- centroid offset `>15%` on an axis: inspect composition
- visible edge contact: inspect clipping

Sample count is not density.

## Tweet budget

`#つぶやきProcessing` costs 19 X-weighted characters. The recommended executable form:

```text
CODE//#つぶやきProcessing
```

leaves **259 weighted characters for `CODE`**.

Write the complete post to a file and run:

```sh
node scripts/check-length.mjs post.txt
```

Do not add decoration merely because characters remain.

## Required output

Unless the user asks for less, return:

### Concept
One or two sentences on the mathematical behavior and intended visual character.

### Morphology plan
Only for compound pieces: root, regions, organ families, attachment/symmetry and motion inheritance.

### Expanded p5.js
Readable source with semantic controls separated from implementation where useful.

### Tweet-ready
One executable line including `//#つぶやきProcessing` or another valid hashtag placement.

### Verification
Raw code points, X-weighted length, pass/fail, plus rendered visual diagnostics when available. For scope-aware controllable work, report the tested controls, declared scopes and spill ratios.

### Variation knobs
3–5 mathematical/morphological controls, not merely colors.

## Failure routing

Diagnose the level before tuning constants:

- **wire/confetti** → topology/sample distribution
- **generic torus/cloth** → root polarity/body plan
- **floating parts** → attachment/local frame
- **everything equally loud** → regional hierarchy/envelopes
- **local control has high unexpected spill** → control dependency or attachment-scope design
- **good readable form collapses after golf** → restore high-leverage generator; remove lower-value detail

A strong result should resemble a **small developmental program**, not a miniature conventional scene graph.