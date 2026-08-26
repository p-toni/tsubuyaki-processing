# tsubuyaki-processing

A production-oriented Agent Skill for generating authentic, tweet-sized **#つぶやきProcessing**: dense mathematical p5.js sketches whose organic forms emerge from compact coupled equations.

## v0.4.1 — moving-scope correctness + morphology survival

The first v0.4 cold test exposed two measurement gaps:

1. **static region masks overestimated semantic spill for geometry controls that move/resize anatomy**;
2. occupancy/bbox parity could look healthy even when code golf erased a defining morphological feature.

v0.4.1 fixes both without changing the core morphology architecture.

## Repository additions / changes

```text
tsubuyaki-processing/
├── SKILL.md
├── README.md
├── references/
│   ├── morphology-composition.md
│   ├── control-strategies.md
│   ├── control-scopes.md
│   ├── evaluation-matrix.md
│   └── ...
├── templates/
│   ├── morphology-contract.json
│   ├── harness.html
│   ├── p5-lite.js
│   └── ...
└── scripts/
    ├── check-length.mjs
    ├── check-visual.mjs
    ├── check-control.mjs
    ├── check-control-scope.mjs
    └── check-morphology-survival.mjs
```

## 1. Dual-state control scopes

A geometry control creates difference pixels at both the **old** and **new** positions of the anatomy it moves.

A baseline-only mask therefore creates a false-positive spill pattern:

```text
old position   →   new position
baseline mask      not covered
```

v0.4.1 defines allowed region support as:

```text
baseline region mask ∪ variant region mask
```

For `subtree` controls, that union is applied to the parent region and every descendant.

### Recommended workflow

Render baseline + variant at the same frame, then render matching diagnostic masks into parallel directories:

```text
baseline-masks/
  root.png
  wings.png
  tail.png
variant-masks/
  root.png
  wings.png
  tail.png
```

Run:

```sh
node scripts/check-control-scope.mjs \
  baseline.png variant.png morphology-contract.json tailLength \
  --baseline-mask-dir=baseline-masks \
  --variant-mask-dir=variant-masks
```

The checker reports:

- total / allowed / spill difference energy;
- spill ratio;
- changed-pixel containment;
- region energy fractions;
- baseline/variant/union mask sizes;
- whether mask mode is `dual-state`, `baseline-override`, or `contract-static`.

Static-mask mode remains available for compatibility but emits a warning for non-global controls.

### Optional dilation

```sh
--dilate=1
```

A tiny dilation can tolerate raster halos or attachment boundaries. It should not be increased merely to improve a score.

## 2. Morphology survival through code golf

Compound morphology should survive **semantic compression**, not merely retain similar image occupancy.

A golfed phenotype may preserve framing while losing:

- a cavity;
- a split body plan;
- a wing/fin family;
- a secondary appendage family;
- another defining region.

`morphology-contract.json` now supports design-time `survivalFeatures`:

```json
{
  "survivalFeatures": {
    "rootMass": {
      "mask": "masks/root.png",
      "kind": "presence"
    },
    "appendageFamily": {
      "mask": "masks/appendages.png",
      "kind": "presence"
    },
    "centralCavity": {
      "mask": "masks/cavity.png",
      "kind": "void"
    }
  }
}
```

Run:

```sh
node scripts/check-morphology-survival.mjs \
  expanded.png golfed.png morphology-contract.json
```

For `presence` features it reports contrast-energy retention and visible-coverage change.

For `void` features it reports whether the final phenotype filled the intended negative space.

This is intentionally **feature-wise**, not one global similarity score. A legitimate golfed system may deform substantially while preserving its defining morphology.

## 3. Routing remains selective

Morphology is not mandatory:

- abstract dense field → mathematical workflow;
- intentional filament/ribbon → 1D path;
- coupled/iterative attractor → dynamical-system path;
- compound organism → morphology composition;
- compound + named semantic controls → control scopes;
- compound + tweet-ready compression → morphology-survival check.

The skill should behave like a router, not a universal morphology framework.

## 4. Offline-first harness

Use:

```text
templates/harness.html?frame=90&s=my-sketch.js
```

The bundled `p5-lite.js` supports the common Tsubuyaki point/circle/line subset without network access. Add `&full=1` only when a sketch requires broader p5 APIs and network access exists.

Diagnostic region masks use:

```text
templates/harness.html?frame=90&s=my-sketch.js&region=wings
```

## 5. Visual and length gates remain unchanged

Visual QA:

```sh
node scripts/check-visual.mjs frame-0.png frame-90.png frame-180.png
```

Tweet verification:

```sh
node scripts/check-length.mjs post.txt
```

The recommended `CODE//#つぶやきProcessing` form leaves **259 X-weighted characters for `CODE`**.

## Continuous research-loop decision

We evaluated `davebcn87/pi-autoresearch` as a possible autonomous optimization loop. Its edit → benchmark → keep/revert infrastructure is a strong fit **once the objective is stable**.

We are intentionally **not integrating it yet**. At this stage, automatically optimizing a scalar such as spill ratio or morphology retention would risk Goodharting immature diagnostics: an agent could broaden masks, weaken controls, or preserve pixels while reducing artistic quality.

The repository is being made loop-ready first:

- deterministic rendering;
- explicit control scopes;
- measurable spill;
- feature-wise morphology survival;
- independent visual / runtime / length safeguards;
- cross-topology evaluation matrix.

Once these measurements are calibrated across a broader corpus, an autoresearch session can safely optimize a multi-metric objective under hard backpressure checks rather than optimizing one proxy blindly.

## Core design principles preserved

- **reusable roles, not literal nouns**;
- more apparent parts than independent formulas;
- parent-relative attachment;
- shared positional fields interpreted into regions;
- repetition with variation;
- hierarchical motion;
- structure before surface detail;
- fix generic toroidal cloth at the body-plan level;
- 280 is a ceiling, not a target.