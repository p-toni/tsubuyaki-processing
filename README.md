# tsubuyaki-processing

A production-oriented Agent Skill for generating authentic, tweet-sized **#つぶやきProcessing**: dense mathematical p5.js sketches whose organic forms emerge from compact coupled equations.

## v0.4 — scope-aware controllability

v0.3 introduced controllable compound morphology. v0.3.1 fixed the cold-agent harness and restored progressive disclosure. v0.4 addresses the remaining measurement gap:

> a control is only meaningfully local if its observed change stays mostly inside the anatomical influence it is supposed to have.

Global changed-pixel fraction and diff centroid cannot prove that. A parent control may correctly move its descendants, while a child-local control should not smear through the whole organism.

v0.4 therefore adds **hierarchical control scopes + region masks + spill measurement**.

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
│   ├── control-scopes.md
│   ├── evaluation-matrix.md
│   ├── style-guide.md
│   └── real-examples.md
├── templates/
│   ├── basic-skeleton.js
│   ├── filament-skeleton.js
│   ├── compound-morphology.js
│   ├── morphology-contract.json
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
    ├── check-control.mjs
    └── check-control-scope.mjs
```

## Workflow routing remains selective

Morphology is **not** mandatory.

- **Single-field / abstract dense form:** base mathematical workflow.
- **Filament / ribbon / axial body:** legitimate 1D path when intended.
- **Iterated/coupled attractor:** dynamical-system path; morphology mostly stays out.
- **Compound organism:** load morphology composition.
- **Compound organism with named semantic controls:** additionally load control strategies + control scopes.

The skill should behave like a router, not a universal morphology framework.

## Offline-first harness

Use:

```text
templates/harness.html?frame=90&s=my-sketch.js
```

The bundled `templates/p5-lite.js` handles the common point/circle/line Tsubuyaki subset without network access.

Use `&full=1` only when a sketch needs full p5 APIs and network access is available.

v0.4 also exposes a region selector for mask rendering:

```text
templates/harness.html?frame=90&s=my-sketch.js&region=crown
```

The readable sketch can inspect `window.__TSUBUYAKI_REGION__` and render only the requested region as a bright-on-dark diagnostic mask.

`templates/compound-morphology.js` demonstrates this pattern.

## Scope-aware morphology contract

`templates/morphology-contract.json` shows the design-time metadata:

```json
{
  "regions": {
    "root": {"parent": null, "mask": "masks/root.png"},
    "crown": {"parent": "root", "mask": "masks/crown.png"},
    "appendages": {"parent": "root", "mask": "masks/appendages.png"}
  },
  "controls": {
    "rootWidth": {"region": "root", "scope": "subtree"},
    "appendageLength": {"region": "appendages", "scope": "region"},
    "foldFrequency": {"region": "root", "scope": "surface"},
    "pulseStrength": {"region": "root", "scope": "global"}
  }
}
```

This metadata exists only for readable-stage testing. It never needs to fit in the tweet.

### Scope meanings

- **`region`** — expected mainly inside one named anatomical region.
- **`subtree`** — expected in that region plus all descendants; correct for parent geometry controls whose children inherit their frame.
- **`surface`** — spatially local to one region, but semantically a detail/deformation control rather than body-plan structure.
- **`global`** — organism-wide influence is expected.

Region masks may overlap.

## Scope-aware control validation

For one semantic control:

1. render a baseline at a fixed frame;
2. perturb only that readable control;
3. render the variant at the same frame;
4. render each declared region mask at that same frame;
5. run:

```sh
node scripts/check-control-scope.mjs \
  baseline.png variant.png morphology-contract.json appendageLength
```

The validator reports:

- total difference energy;
- allowed difference energy;
- unexpected spill energy;
- **spill ratio**;
- fraction of thresholded changed pixels inside allowed scope;
- per-region difference-energy fractions.

For a `subtree` control, the allowed mask is the union of the named region and its descendants.

For `region` / `surface`, it is the named region mask.

For `global`, wide influence is allowed.

### Why spill is better than global centroid

Two controls can both change ~8% of the frame and have almost identical diff centroids while behaving very differently semantically.

Example:

```text
rootWidth       → root + descendants       expected
appendageLength → appendages only          expected
```

A global diff statistic cannot tell them apart. Scope-aware spill can.

### Do not optimize spill to zero blindly

Legitimate spill exists because of:

- attachment boundaries;
- translucent overlap;
- antialiasing;
- parent-relative motion;
- shared positional fields.

Use spill comparatively across controls/refactors/frames. There is no universal pass threshold yet.

Also inspect **effect strength**: a control with nearly zero change and zero spill is not useful.

## Visual QA

Visual density/framing checks from v0.2 remain unchanged:

```sh
node scripts/check-visual.mjs frame-0.png frame-90.png frame-180.png
```

Optional arguments:

```sh
--threshold=24
--edge=.02
--quantiles=.01,.99
```

`--quantiles=low,high` selects robust bounding-box quantiles. Default `.01,.99` ignores the outer 1% of visible-pixel mass on each side, reducing sensitivity to isolated outliers.

Useful dense-organic diagnostics:

- `<2%` occupancy: strong wire/sparse warning unless intentional;
- `2–4%`: inspect carefully;
- `4–15%`: common useful territory, not a target;
- `>15%`: inspect for overfill/lost cavities;
- dominant robust span `<55%`: often too small;
- centroid offset `>15%`: inspect composition.

## Controllable morphology principles preserved

The v0.3 ideas that demonstrated value remain first-class:

- **reusable roles, not literal nouns**;
- more apparent parts than independent formulas;
- shared positional fields (`e/k/d`) interpreted into regions;
- child anatomy attached in parent-relative frames;
- parity/modulo for repeated organ families;
- repetition with variation rather than sterile cloning;
- one master motion hierarchy;
- structure controls separated from surface/detail controls in readable code;
- fix generic **toroidal cloth** at the body-plan level rather than decorating it.

Full mechanics live in `references/morphology-composition.md`; scope semantics live in `references/control-scopes.md`.

## Tweet budget

The recommended executable form:

```text
CODE//#つぶやきProcessing
```

leaves **259 X-weighted characters for `CODE`**.

Verify the complete post with:

```sh
node scripts/check-length.mjs post.txt
```

280 is a ceiling, not a target.

## v0.4 evaluation matrix

`references/evaluation-matrix.md` defines four cold-agent benchmark classes:

1. compound bell/creature — morphology + scope validation should activate;
2. 1D axial filament creature — legitimate 1D path;
3. coupled/iterative attractor — morphology should mostly stay out;
4. abstract dense sheet — essentially the v0.2 path.

The release criterion is not merely “better jellyfish.” It is:

> **better selective controllability for compound organisms without taxing simpler topologies.**