# tsubuyaki-processing

A production-oriented Agent Skill for generating authentic, tweet-sized **#つぶやきProcessing**: dense mathematical p5.js sketches whose organic forms emerge from compact coupled equations.

**v0.2** changes the generation loop based on first real-use testing: dense-organic work now starts from flattened 2D sampling by default, visual density/framing are mechanically inspectable before code golf, and 1D is treated explicitly as a filament/ribbon topology rather than a generic density default.

## What the skill does

Given a direction such as “breathing seed pod,” “alien flower,” “folded creature,” or “abstract living knot,” an agent should:

1. choose topology from the desired visual material;
2. design a readable mathematical system;
3. render representative frames;
4. inspect image-space density, framing, centroid and clipping;
5. iterate until the visual system is coherent;
6. semantically code-golf the sketch;
7. return readable + tweet-ready p5.js;
8. mechanically verify the complete post length.

## Repository

```text
tsubuyaki-processing/
├── SKILL.md
├── README.md
├── references/
│   ├── research-notes.md
│   ├── code-golf-techniques.md
│   ├── mathematical-patterns.md
│   ├── style-guide.md
│   └── real-examples.md
├── templates/
│   ├── basic-skeleton.js          # flattened 2D dense-sheet default
│   ├── filament-skeleton.js       # deliberate 1D/ribbon topology
│   ├── advanced-parametrics.js
│   └── harness.html               # deterministic browser test harness
├── examples/
│   ├── 01-breathing-calyx.md
│   ├── 02-folded-creature.md
│   └── 03-coupled-attractor.md
└── scripts/
    ├── check-length.mjs
    └── check-visual.mjs
```

## v0.2 topology rule

For the targeted **dense tissue / membrane / folded-sheet** aesthetic, start with flattened 2D sampling:

```js
x=i%n
y=i/n
```

A 1D manifold is intrinsically a curve. It remains first-class for filaments, ribbons and axial creature forms, and several important real works use it successfully—but high point count alone does not transform a curve into a surface. If 20k samples still render as a wire, change topology or deliberately fold/decorrelate neighboring samples.

Parity/modulo creates anatomy; it does not increase dimensionality.

## Visual verification

Sample count is not visual density. v0.2 adds a dependency-free PNG checker for the properties that repeatedly required manual correction in first use.

Render a few representative frames, then run:

```sh
node scripts/check-visual.mjs frame-0.png frame-90.png frame-180.png
```

It reports per-frame:

- background-relative lit-pixel occupancy
- robust 1%–99% bounding box
- visible-pixel centroid
- edge-band contact
- diagnostic warnings

Default heuristics for this specialization:

- `<2%` occupancy: strong wire/sparse warning
- `2–4%`: visual inspection zone
- `4–15%`: common dense-organic territory
- `>15%`: inspect for overfill/lost cavities
- dominant robust span `<55%`: often too small
- centroid offset `>15%` on an axis: inspect composition

These are **not hard authenticity gates**. Metrics support visual judgment; unusual compositions can intentionally violate them.

The checker estimates the background from canvas corners and measures contrast relative to it, so it works for both pale-on-dark and dark-on-paper sketches.

### Checker limitations

`check-visual.mjs` intentionally stays dependency-free and supports non-interlaced 8-bit grayscale, RGB, grayscale+alpha, and RGBA PNGs. Browser screenshots normally satisfy this. If your screenshot pipeline produces another PNG mode, convert/export it to ordinary 8-bit PNG first.

## Browser harness

`templates/harness.html` removes the setup tax for headless/browser iteration.

Place the candidate as `sketch.js` beside the harness. The page exposes:

```js
window.__TSUBUYAKI_READY__
window.__TSUBUYAKI_ERROR__
window.__TSUBUYAKI_CAPTURE_FRAME__
window.__TSUBUYAKI_CAPTURED_FRAME__
```

Set a target capture frame, wait for the harness to pause after that frame, screenshot the canvas, and feed the PNG to `check-visual.mjs`.

The harness loads p5.js from jsDelivr; an offline environment should substitute a locally available p5 build.

## Length verification

X/Twitter uses weighted character counting. The included checker is exact for the intended domain of **code + hashtag, no URL/emoji**.

Lead with the file form so shell quoting cannot alter golfed code:

```sh
node scripts/check-length.mjs post.txt
```

Stdin is also supported.

### Real budget

`#つぶやきProcessing` costs **19 weighted characters**.

Therefore:

- bare hashtag placement leaves up to **261 weighted** for code, if syntax permits it;
- the recommended executable `CODE//#つぶやきProcessing` form leaves **259 weighted** for `CODE`;
- a separating space leaves one less.

**280 is a ceiling, not an optimization target.** A coherent system finishing comfortably under budget is better than spending spare characters on decoration.

## Dark and light grounds

The contemporary baseline remains near-black with pale translucent points, because overlap naturally creates luminous ridges.

For a paper-toned/light canvas, use dark translucent ink and usually lower alpha. Overlap then produces darker density. The mathematical system can remain identical; tune alpha/contrast for the compositing direction rather than blindly inverting numeric colors.

## Installation

Use the normal skill-directory mechanism for your Agent Skills-compatible host. The essential discovery path is:

```text
tsubuyaki-processing/SKILL.md
```

Copy the entire directory so the agent can progressively load the references, scaffolds and validation scripts.

## Example prompt

```text
Create an original #つぶやきProcessing sketch that feels like a translucent seed pod slowly unfolding. Use the tsubuyaki-processing skill. Give me the expanded source, tweet-ready code, visual diagnostics, verified length, and three mathematically meaningful variants.
```

## Design stance

### Authenticity over generic p5

The skill prioritizes compact latent geometry: coupled trigonometric fields, body coordinates, phase reuse, controlled nonlinearities, internal temporal deformation, and image-space density.

### Original systems, not artist copying

The research extracts structural techniques from real work. `references/real-examples.md` includes only short identifying fragments and analysis, not complete third-party one-liners.

### Readable → render → measure → golf

This is the v0.2 control loop. Code golf starts only after the expanded mathematical system works visually.

### Deterministic checks for deterministic constraints

The model should not eyeball weighted length, nor assume that “30k points” implies dense output. Mechanical evidence is used where it is cheap and reliable; aesthetic decisions remain visual.

## Research basis

See `references/research-notes.md` and `references/real-examples.md` for the source-backed history, community examples, code-golf literature, tool ecosystem, and design rationale.

Primary/reference sources include Hau-kun's origin material and official portal, WGG, Snowman-s, Watabo-shi/Kani, Gorilla Sun, Koma Tebe, the Anthropic Agent Skill guidance/algorithmic-art skill, and `twitter-text` v3.

## Future improvements

- make the harness fully offline by bundling or resolving a host-provided p5 build
- add automatic browser capture orchestration around the existing frame hooks
- add cross-frame visual regression between expanded and golfed forms
- calibrate occupancy/framing heuristics against a larger permissioned corpus instead of first-use evidence
- build a parameter explorer that exports tuned constants back into readable source
- add benchmark prompts for trigger precision, originality, syntax validity, frame rate, visual density, framing and length compliance