# Hierarchical Control Scopes

v0.4 makes semantic control measurable against the morphology hierarchy rather than against one global image-diff statistic.

## Why global diff was insufficient

In a hierarchical organism, changing a parent can correctly move its descendants. A `bellWidth` change may alter both bell and tendril pixels because the tendrils inherit the bell's attachment frame. A `tendrilLength` change should usually stay inside the tendril family.

Therefore these two questions are different:

1. **How much changed?** — global image difference.
2. **Did change stay inside the influence that this control is supposed to have?** — semantic scope.

v0.4 addresses the second question.

## Morphology hierarchy

Represent regions as a parent graph in `morphology-contract.json`:

```json
{
  "regions": {
    "root": {"parent": null, "mask": "masks/root.png"},
    "bell": {"parent": "root", "mask": "masks/bell.png"},
    "tendrils": {"parent": "bell", "mask": "masks/tendrils.png"}
  }
}
```

The graph is design-time metadata. It does **not** appear in the tweet-ready code.

Region masks may overlap. Organic morphology rarely partitions into disjoint boxes, and attachment zones are often genuinely shared.

## Control scopes

Every semantic control used for locality testing declares one scope.

### `region`

Expected to act primarily inside one region.

Example:

```json
"tendrilLength": {"region":"tendrils","scope":"region"}
```

Use for appendage length, local cavity depth, local taper, local phase offset, etc.

### `subtree`

Expected to act on a region **and all descendants**.

Example:

```json
"bellWidth": {"region":"bell","scope":"subtree"}
```

This is the correct scope for a parent geometry control when attached children inherit its frame.

### `surface`

A local appearance/deformation control whose spatial permission is the named region, but whose intended meaning is surface/detail rather than body-plan structure.

Example:

```json
"foldFrequency": {"region":"bell","scope":"surface"}
```

The current validator treats `surface` spatially like `region`; the distinct label matters for interpretation and future metrics.

### `global`

Expected to affect the whole organism.

Example:

```json
"pulseStrength": {"region":"root","scope":"global"}
```

Do not penalize global controls for wide influence.

## Producing masks

Masks should describe the **expected image-space support of a region at the exact frame being tested**.

Recommended process:

1. keep readable source instrumentable;
2. expose `window.__TSUBUYAKI_REGION__` as a debug selector;
3. render the same frame once per region via:

```text
harness.html?frame=90&s=sketch.js&region=bell
```

4. draw the selected region as bright marks on a black/transparent ground;
5. save those PNGs under the paths named by the contract.

The mask does not need to be tweet-sized. It belongs only to the readable/testing representation.

### Mask design rule

A region mask should answer:

> If this anatomical region were isolated at this frame, which pixels could reasonably belong to it or its attachment zone?

Do not make masks so tight that harmless anti-aliasing becomes spill. Do not make them so broad that every control appears local.

## Validation

Run:

```sh
node scripts/check-control-scope.mjs \
  baseline.png variant.png morphology-contract.json tendrilLength
```

The validator computes luminance-difference energy and reports:

- total difference energy;
- allowed difference energy;
- unexpected spill energy;
- **spill ratio** = difference energy outside allowed scope / total difference energy;
- fraction of thresholded changed pixels inside allowed scope;
- per-region difference-energy fractions.

For `subtree`, the allowed mask is the union of the declared region and every descendant.

For `region` and `surface`, it is the named region mask.

For `global`, organism-wide influence is permitted.

## Interpreting spill

There is no universal magic threshold yet. Use comparative evidence.

Good tests:

- compare a local control before/after refactoring;
- compare several controls in one organism;
- compare the same control across animation frames;
- deliberately create a smeared dependency and verify that spill rises.

A local control with consistently low spill is more selective than one with the same global changed fraction but high spill.

### Do not optimize spill to zero blindly

Organic attachment creates legitimate boundary effects:

- appendage roots can alter parent attachment pixels;
- translucent overlap can make a child control change brightness in a shared region;
- antialiasing creates a small halo;
- positional inheritance can shift nearby tissue.

The goal is **predictable influence**, not artificial isolation.

## Control locality vs control usefulness

A perfectly local knob can still be useless if its effect is visually tiny. Evaluate both:

1. **effect strength** — did enough image energy change to matter?
2. **selectivity** — did most of that change occur where expected?

`check-control-scope.mjs` provides both total difference energy and spill ratio so a nearly-no-op control cannot look successful merely because it has zero spill.

## Structural routing

Do not require scope contracts for every sketch.

Use them when:

- the user explicitly asks for controllable morphology;
- a compound organism exposes named semantic anatomy controls;
- you are evaluating whether hierarchical attachment remains predictable.

Skip them when:

- the sketch is a single abstract field;
- a 1D filament has no meaningful anatomical regions;
- an attractor's parameters are intentionally global;
- the user only needs a final aesthetic output rather than a controllable design system.

This keeps v0.4 from taxing simpler Tsubuyaki workflows.