---
name: tsubuyaki-processing
description: "Create authentic #つぶやきProcessing p5.js sketches: dense mathematical, organic, point-based animated forms compressed to a tweet-sized program. Use for Tsubuyaki Processing, tweet-sized p5.js, mathematical creature/floral forms, or code-golfed generative art. Produce an original readable sketch plus a verified <=280-character tweet version."
---

# Tsubuyaki Processing

Create **original #つぶやきProcessing**, not generic generative art that happens to be short.

The target aesthetic is the mature p5.js practice associated with the Japanese creative-coding community: a tiny program encoding a surprisingly rich dynamical system, often rendered as thousands of pale points whose coordinates are coupled by trigonometric fields and a slowly changing time variable.

## Non-negotiable constraints

1. **Tweet-sized is a hard gate.** The final post text, including `#つぶやきProcessing`, must be at most 280 X/Twitter weighted characters. Also keep raw Unicode code-point length <=280.
2. **Use p5.js global mode unless the user asks otherwise.** It is the most golfable and the dominant contemporary form.
3. **Generate an original system.** Study the pattern language in the references; do not reconstruct or lightly mutate a published artist's exact formula.
4. **Mathematical density beats decorative complexity.** Prefer one compact coupled field that creates many visual phenomena over many drawing primitives, assets, palettes, classes, or random objects.
5. **The final code must run.** Never sacrifice executable behavior merely to win characters.
6. **The readable version is the source of truth.** Golf only after the visual system is coherent.

## Load these references as needed

- For shortening: `references/code-golf-techniques.md`
- For inventing equations: `references/mathematical-patterns.md`
- For visual judgment: `references/style-guide.md`
- For researched precedents: `references/real-examples.md`
- For historical/tool context: `references/research-notes.md`
- Starting scaffolds: `templates/basic-skeleton.js`, `templates/advanced-parametrics.js`

## Generation workflow

### 1. Choose a visual organism

Pick one conceptual behavior, not an object to literally draw. Good targets include:

- breathing calyx / anemone
- ribbon animal / larval body
- jellyfish-like bell and tendrils
- folded flower / seed pod
- shell / torus / vortex tissue
- bilateral mask / moth-like field
- abstract cellular membrane
- coupled attractor / living knot

Translate the idea into **geometry + modulation + time**, not into polygon illustration.

### 2. Choose a sampling domain

Default to one of these:

- **1D manifold:** `i=1e4..4e4` and derive one parameter `u=i/s`.
- **Flattened 2D manifold:** derive `x=i%n`, `y=i/n` from one countdown loop.
- **Iterated state:** update a few state variables repeatedly and plot every iteration.

A dense point cloud should reveal a continuous body or field. Avoid sparse confetti.

### 3. Build an implicit body coordinate

Use two latent coordinates and a radius-like measure:

`k = lateral/oscillatory coordinate`

`e = axial/depth coordinate`

`d = mag(k,e)` or a nonlinear transform of it.

Typical ingredients:

- `k=A*cos(u*f+phase)` or coupled `sin/cos`
- `e=u/s-o`
- `d=mag(k,e)`
- powers such as `d**2`, `d**3`, reciprocal terms such as `1/d` or `1/k`, and bounded nested trig

This latent geometry is what creates body plans, folds, frills, cavities, and tendrils without explicitly modeling them.

### 4. Couple phases

Create at least two interacting phase scales:

- a slow global phase from `t`
- a body phase from `d`, `e`, `u`, or index parity/modulo

Examples of relationships to invent from, not copy literally:

- `c=d*r-t*s`
- `sin(e*f-d*g+t*h)`
- `sin(d*d-t)`
- `i%2*PI` for alternating lobes
- `i%n` for repeated petals/segments

The best forms use the same latent variables in several places, so geometry and motion feel causally linked.

### 5. Project to the canvas

Prefer a compact polar or pseudo-3D projection:

- compute a local radius/offset `q`
- compute an angle/phase `c`
- plot `point(cx+q*cos(c),cy+...)` or a related `sin/cos` pair

Do not center every term independently. Reuse `q`, `c`, `d`, `k`, and `e` through assignment expressions when golfing.

### 6. Tune the visual field before golfing

Start readable. Typical contemporary baseline:

- canvas: 400×400
- background: 6–12 grayscale
- stroke: pale gray/white with alpha 35–110
- samples: 10,000–40,000
- time step: roughly `PI/240` to `PI/20`, with slower values preferred for calm organic evolution
- primitive: `point()` first; `circle()` only when particle diameter contributes meaning

Change constants deliberately. Seek:

- a recognizable silhouette at a glance
- local detail on zoom
- coherent motion rather than jitter
- controlled singularities, not accidental explosions
- asymmetry or phase offsets sufficient to avoid a generic mandala

### 7. Compress semantically

Only after the expanded sketch works:

1. Merge setup into `draw` with a first-frame guard.
2. Replace `frameCount` with a one-letter clock.
3. Use square canvas assignment: `createCanvas(w=400,w)`.
4. Remove declarations where non-strict p5 global mode permits implicit globals.
5. Use arrow functions and one-character names.
6. Count down loops: `for(i=1e4;i--;)`.
7. Flatten nested loops when possible.
8. Alias a long p5 function only if reuse actually saves characters.
9. Use assignment expressions to create reusable intermediate values inside formulas.
10. Replace long numerals with scientific notation when shorter (`1e4`).
11. Remove leading zeroes (`.3`) and harmless defaults.
12. Reuse a dimension variable as a clamped light color when visually equivalent.
13. Apply fragile/version-sensitive tricks only after testing; prefer stable semantics when both fit.

See `references/code-golf-techniques.md` for the full catalog and break-even rules.

### 8. Verify the hard limit

Count the **complete post string**, not just JavaScript. Include the hashtag.

If shell execution is available:

```sh
printf %s 'FINAL_CODE_HERE' | node scripts/check-length.mjs
```

Do not declare success until both reported limits pass.

If no runtime is available, count conservatively and target <=270 raw code points to leave margin, but explicitly state that the weighted count was not mechanically verified.

### 9. Run or sanity-check

When execution is available, test the expanded and compressed forms. Confirm:

- no syntax error
- first-frame initialization occurs once
- variables used by default parameters/assignment expressions exist in the intended order
- no `NaN` cascade dominates the field
- intended loop count completes at interactive speed
- compressed output is visually equivalent enough to the expanded source

## Required output format

Unless the user asks for only one form, return exactly these sections:

### Concept
One or two sentences describing the mathematical behavior and intended visual character.

### Expanded p5.js
Readable, commented code. Use descriptive names and separate setup/draw.

### Tweet-ready
A single line containing the complete executable p5.js plus `//#つぶやきProcessing` or an equivalent valid hashtag placement.

### Length
Report:

- raw Unicode code points
- X/Twitter weighted length
- pass/fail against 280

### Variation knobs
Give 3–5 **mathematical** edits, such as changing a frequency ratio, exponent, time divisor, parity term, axial scale, or singularity strength. Do not merely suggest colors.

## Iteration protocol

When the user asks for another version, preserve only the requested invariants. Otherwise vary at least three of these five axes:

1. sampling topology — 1D / flattened 2D / iterative
2. latent body equation — how `k,e,d` are constructed
3. projection — polar / axial / pseudo-3D / folded
4. harmonic ratios — frequencies and phase couplings
5. temporal law — speed, breathing envelope, phase drift

For a family of variants, keep one mathematical invariant and mutate the others. Example: preserve the same `d=mag(k,e)` body coordinate while changing projection and phase coupling.

## Authenticity test

Reject or revise a candidate if three or more are true:

- fewer than ~2,000 samples without a strong reason
- shape is built mostly from explicit primitives rather than a field
- motion is just rotation/translation of a static object
- random/noise is doing most of the visual work
- formula contains many independent decorations instead of reused latent variables
- result looks like a generic flow field, starfield, spirograph, or particle fountain
- code was minified first and designed second
- final version exceeds the tweet budget

A strong result should feel **larger than its source**: a compressed mathematical organism, not a miniature conventional sketch.
