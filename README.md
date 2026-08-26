# tsubuyaki-processing

A production-oriented Agent Skill for generating authentic, tweet-sized **#つぶやきProcessing**: dense mathematical p5.js sketches whose organic forms emerge from compact coupled equations.

## v0.3.1 — reliability + progressive disclosure

v0.3 introduced controllable compound morphology. First-use testing showed the morphology model itself was useful, but exposed three implementation problems around it:

1. the browser harness still required network access;
2. the global image-diff checker could not actually prove semantic control locality in a hierarchy;
3. `SKILL.md` had absorbed too much of the morphology reference, taxing simple sketches with compound-organism instructions.

v0.3.1 fixes those without changing the morphology model.

## Repository

```text
tsubuyaki-processing/
├── SKILL.md
├── README.md
├── references/
│   ├── research-notes.md
│   ├── controllable-complexity-research.md
│   ├── code-golf-techniques.md
│   ├── mathematical-patterns.md
│   ├── morphology-composition.md
│   ├── control-strategies.md
│   ├── style-guide.md
│   └── real-examples.md
├── templates/
│   ├── basic-skeleton.js
│   ├── filament-skeleton.js
│   ├── compound-morphology.js
│   ├── advanced-parametrics.js
│   ├── p5-lite.js
│   └── harness.html
├── examples/
│   ├── 01-breathing-calyx.md
│   ├── 02-folded-creature.md
│   ├── 03-coupled-attractor.md
│   └── 04-compound-morphology.md
└── scripts/
    ├── check-length.mjs
    ├── check-visual.mjs
    └── check-control.mjs
```

## Workflow routing

v0.3.1 deliberately keeps morphology optional.

- **Single-field / abstract dense form:** use `mathematical-patterns.md` + `style-guide.md`.
- **Filament / ribbon / axial body:** intentionally take the 1D path; do not force compound morphology.
- **Iterated/coupled attractor:** use the dynamical-system path; morphology machinery should mostly stay out of the way.
- **Compound organism / explicit anatomical control:** additionally load `morphology-composition.md` + `control-strategies.md`.

This restores the intended progressive-disclosure behavior.

## Offline-first harness

The harness no longer depends on a CDN for the common Tsubuyaki subset.

Use:

```text
templates/harness.html?frame=90&s=my-sketch.js
```

The bundled `templates/p5-lite.js` provides the global-mode primitives normally needed by this skill: canvas creation, background/stroke/fill, point/circle/line, common math helpers, `frameCount`, `noLoop`, etc.

If a sketch genuinely requires APIs outside that subset and network access is available:

```text
templates/harness.html?frame=90&s=my-sketch.js&full=1
```

`full=1` loads p5.js 1.11.11 from jsDelivr. Offline cold-agent testing should use the default bundled runtime.

## Visual QA

Render several frames and run:

```sh
node scripts/check-visual.mjs frame-0.png frame-90.png frame-180.png
```

Optional arguments include:

```sh
--threshold=24
--edge=.02
--quantiles=.01,.99
```

`--quantiles=low,high` selects the robust bounding-box quantiles. The default `.01,.99` ignores the outer 1% of visible-pixel mass at each side when estimating framing, reducing sensitivity to isolated singular/outlier points.

The visual checker reports occupancy, robust bbox, centroid and edge contact. These remain diagnostics, not universal aesthetic gates.

Useful bands for dense-organic work:

- `<2%` occupancy: strong wire/sparse warning
- `2–4%`: inspect carefully
- `4–15%`: common useful territory, not a target
- `>15%`: inspect for overfill/lost cavities
- dominant robust span `<55%`: often too small
- centroid offset `>15%`: inspect composition

## Control-diff diagnostics

`check-control.mjs` compares same-frame renders after perturbing one readable control:

```sh
node scripts/check-control.mjs baseline.png variant.png --quantiles=.01,.99
```

It reports global changed-pixel fraction, mean/max luminance delta, robust difference bbox and difference centroid.

**Important v0.3.1 limitation:** this is not a semantic locality validator. In hierarchical morphology, a parent control may correctly move its descendants; global diff size/centroid cannot distinguish that from accidental smearing. Treat these numbers as visual-review evidence only.

Region/subtree-aware validation is the next measurement layer.

## Controllable morphology remains intact

The v0.3 principles that survived testing remain first-class:

- **reusable roles, not literal nouns**;
- more apparent parts than independent formulas;
- shared positional fields (`e/k/d`) interpreted into regions;
- child anatomy attached in parent-relative frames;
- parity/modulo for repeated organ families;
- repetition with variation rather than sterile cloning;
- one master motion hierarchy;
- structure controls separated from surface/detail controls in readable code;
- fix generic **toroidal cloth** at the body-plan level rather than decorating it.

Full mechanics live in `references/morphology-composition.md`; `SKILL.md` only routes into them when needed.

## Tweet budget

`#つぶやきProcessing` costs 19 X-weighted characters. The recommended executable form:

```text
CODE//#つぶやきProcessing
```

leaves **259 weighted characters for `CODE`**.

Verify the complete post with:

```sh
node scripts/check-length.mjs post.txt
```

280 is a ceiling, not a target.

## Research basis

See `references/controllable-complexity-research.md` for the research-to-tiny-code translation. Core influences include Karl Sims' indirect creature genotypes, L-system hierarchy/local frames, Wolpert-style positional information, CPPN-like repetition-with-variation, and skeletal implicit modeling.

The skill applies those as **design-time representation principles**, not literal runtimes that would be too expensive for tweet-sized code.

## Next evaluation frontier

The next release should test whether morphology remains optional and whether semantic controls can be measured against expected hierarchical scope. A balanced benchmark should include:

1. compound bell/creature — morphology should activate;
2. 1D filament/axial piece — legitimate 1D path;
3. coupled/iterative attractor — morphology should mostly stay out;
4. abstract dense sheet — essentially the v0.2 mathematical workflow.

For compound controls, the future validator should measure expected region/subtree influence versus unexpected spill rather than relying on global difference centroids.