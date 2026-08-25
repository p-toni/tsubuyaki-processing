---
name: tsubuyaki-processing
description: "Create authentic #つぶやきProcessing p5.js sketches: dense mathematical, organic, point-based animated forms compressed to a tweet-sized program. Use for Tsubuyaki Processing, tweet-sized p5.js, mathematical creature/floral forms, or code-golfed generative art. Produce an original readable sketch plus a verified <=280-character tweet version."
---

# Tsubuyaki Processing

Create **original #つぶやきProcessing**, not generic generative art that happens to be short.

The target aesthetic is the mature p5.js practice associated with the Japanese creative-coding community: a tiny program encoding a surprisingly rich dynamical system, often rendered as thousands of points whose coordinates are coupled by trigonometric fields and a slowly changing time variable.

## Non-negotiable constraints

1. **Tweet-sized is a hard gate.** The complete post, including the hashtag/comment marker, must be <=280 X/Twitter weighted characters and <=280 raw Unicode code points.
2. **Use p5.js global mode unless the user asks otherwise.**
3. **Generate an original system.** Learn structural devices from the references; do not reconstruct or lightly mutate a published artist's exact formula.
4. **Mathematical density beats decorative complexity.** Prefer one compact coupled field over many independent decorations.
5. **The final code must run.** Never sacrifice executable behavior merely to win characters.
6. **Design and verify visually before golfing.** The readable version is the source of truth.
7. **280 is a ceiling, not a target.** Do not spend spare characters unless they materially improve the piece.

## Load these references as needed

- shortening: `references/code-golf-techniques.md`
- equations/topology: `references/mathematical-patterns.md`
- visual judgment: `references/style-guide.md`
- researched precedents: `references/real-examples.md`
- historical/tool context: `references/research-notes.md`
- dense-sheet scaffold: `templates/basic-skeleton.js`
- filament scaffold: `templates/filament-skeleton.js`
- advanced sheet scaffold: `templates/advanced-parametrics.js`
- deterministic browser harness: `templates/harness.html`

## Generation workflow

### 1. Choose a visual organism

Pick one conceptual behavior, not an object to literally draw: breathing calyx, larval ribbon, jellyfish-like bell, folded seed pod, shell tissue, bilateral field, cellular membrane, living knot.

Translate the idea into **geometry + modulation + time**, not polygon illustration.

### 2. Choose sampling topology from the desired material

For the requested dense-organic/tissue aesthetic, **default to a flattened 2D manifold**:

```js
x=i%n
y=i/n
```

Use roughly 20k–40k samples when practical. Two independent sample coordinates naturally create sheets, cavities, membranes and density gradients.

Use a **1D manifold** deliberately when the intended material is a filament, ribbon, axial creature or strongly folded curve. A 1D manifold is intrinsically a curve: increasing sample count alone makes the curve smoother, not surface-like. To make a 1D system read as tissue, intentionally fold/decorrelate adjacent samples with sufficiently different phase scales, residue classes, singular deformation or related structure.

Use **iterated state** when the dense body should emerge from a trajectory rather than independent samples.

**Do not confuse anatomy with dimensionality.** Parity/modulo can create bilateral lobes or segment families, but does not by itself turn a 1D curve into a dense sheet.

### 3. Build an implicit body coordinate

Use latent coordinates and a radius-like measure:

- `k` = lateral/radial coordinate
- `e` = axial/depth coordinate
- `d=mag(k,e)` or a nonlinear transform

Useful ingredients include coupled `sin/cos`, `d**2`, `d**3`, bounded nested trig, and controlled `1/d` or `1/k` terms. Reuse these latent quantities throughout the projection and animation.

### 4. Couple phases

Create at least two interacting phase scales:

- slow global phase from `t`
- body phase from `d`, `e`, sample coordinates, or index residue

Examples to invent from rather than copy literally:

```js
c=d*r-t*s
sin(e*f-d*g+t*h)
sin(d*d-t)
i%2*PI
```

The same latent variables should affect several visible phenomena so the organism feels causally unified.

### 5. Project to the canvas

Prefer compact polar, axial or pseudo-3D projection. Compute a local radius/offset `q`, an angle/phase `c`, then plot a related `sin/cos` pair.

Projection terms can move the centroid and scale in non-obvious ways. Never assume that using `w/2` inside the formula means the visible form is centered.

### 6. Tune the visual field before golfing

Typical dark-ground baseline:

- canvas: 400×400
- background: grayscale 6–12
- stroke: pale gray/white, alpha ~35–110
- samples: 20k–40k for flattened 2D; 10k–30k commonly works for 1D/iterative systems
- master time step: roughly `PI/240` to `PI/20`
- primitive: `point()` first

For a **light/paper ground**, invert the material logic: use dark ink and usually lower alpha. Overlap now creates darker density rather than luminous additive-looking ridges. Judge contrast against the actual background rather than using dark-ground brightness thresholds.

Seek:

- recognizable silhouette at thumbnail scale
- macro, meso and micro structure
- internal motion rather than rigid rotation
- controlled singularities
- meaningful cavities/density bands
- enough asymmetry/phase disagreement to avoid generic mandalas

### 7. Mechanically inspect density and framing when rendering is available

Render at least 3 representative frames, preferably separated in time, and run:

```sh
node scripts/check-visual.mjs frame-0.png frame-90.png frame-180.png
```

The checker reports background-relative occupancy, robust bounding box, visible-pixel centroid and edge contact. Treat these as **diagnostics, not universal aesthetic laws**.

Useful heuristics for the dense-organic target:

- `<2%` occupancy: strong wire/sparse warning unless intentionally filamentary
- `2–4%`: inspect whether it reads as tissue or a curve
- `4–15%`: common useful territory, not a required band
- `>15%`: valid, but inspect for overfill/lost cavities
- dominant robust span below ~55%: often framed too small
- visible centroid >15% of canvas away from center on either axis: inspect composition
- substantial edge contact: inspect clipping

Sample count is **not** a density metric. Twenty thousand points can still collapse onto a visible wire.

### 8. Compress semantically

Only after the expanded sketch passes visual judgment:

1. Merge setup into `draw` with a first-frame guard.
2. Replace `frameCount` with a one-letter clock.
3. Use square canvas assignment: `createCanvas(w=400,w)`.
4. Remove declarations where non-strict p5 global mode permits implicit globals.
5. Use arrow functions and one-character names.
6. Count down loops: `for(i=3e4;i--;)`.
7. Flatten nested loops when possible.
8. Alias long functions only when reuse actually saves characters.
9. Use assignment expressions for shared intermediate values.
10. Use shorter equivalent numerals such as `3e4`, `.3`.
11. Remove harmless defaults and redundant syntax.
12. Apply fragile/version-sensitive tricks only after testing.

See `references/code-golf-techniques.md` for the full catalog.

### 9. Verify the hard limit

Write the **complete post string** to a file and check it safely:

```sh
node scripts/check-length.mjs post.txt
```

Stdin is also supported, but avoid shell quoting that can corrupt real code.

Budget details:

- `#つぶやきProcessing` costs **19 X-weighted characters**.
- Therefore bare `CODE#つぶやきProcessing` leaves 261 weighted characters for code, if syntactically valid in context.
- The recommended executable comment form `CODE//#つぶやきProcessing` spends two additional `/` characters, leaving **259 weighted characters for `CODE`**.
- A separating space leaves one fewer.

Do not declare success until the actual complete post passes. Finishing comfortably under 280 is normal and preferable to adding decoration merely because characters remain.

### 10. Run and compare

Use `templates/harness.html` or an equivalent p5 runtime. Test readable and compressed forms and confirm:

- no syntax error
- one-time initialization occurs once
- no dominant `NaN` cascade
- intended sample count completes at interactive speed
- visual form remains framed across time
- compressed output is visually equivalent enough to the readable source

If screenshots can be captured, compare both occupancy and robust bbox as a cheap regression signal in addition to visual inspection.

## Required output format

Unless the user requests only one form, return exactly:

### Concept
One or two sentences describing the mathematical behavior and intended visual character.

### Expanded p5.js
Readable, commented code.

### Tweet-ready
One line containing complete executable p5.js plus `//#つぶやきProcessing` or another valid hashtag placement.

### Verification
Report:

- raw Unicode code points
- X/Twitter weighted length
- pass/fail
- if rendered: visual occupancy/framing diagnostics and any warnings

### Variation knobs
Give 3–5 **mathematical** edits: frequency ratio, exponent, time divisor, topology, axial scale, singularity strength, etc. Do not merely suggest colors.

## Iteration protocol

When the user asks for another version, preserve only requested invariants. Otherwise vary at least three axes:

1. sampling topology
2. latent body equation
3. projection
4. harmonic ratios
5. temporal law

If the output looks like a wire when tissue was intended, **change topology or adjacency decorrelation before endlessly tuning constants**.

## Authenticity test

Reject or revise a candidate if three or more are true:

- low image-space coverage for the intended material, even if sample count is high
- shape is built mostly from explicit primitives rather than a field
- motion is only rotation/translation of a static object
- random/noise does most of the visual work
- formula contains many independent decorations instead of reused latent variables
- result looks like a generic flow field, starfield, spirograph, or particle fountain
- code was minified before the visual system was designed and checked
- final post exceeds the budget

A strong result should feel **larger than its source**: a compressed mathematical organism, not a miniature conventional sketch.