# Hierarchical Control Scopes

v0.4.1 makes semantic control measurable against the morphology hierarchy **and against both geometric states being compared**.

## Why global diff was insufficient

In a hierarchical organism, changing a parent can correctly move its descendants. A `bellWidth` change may alter both bell and tendril pixels because the tendrils inherit the bell's attachment frame. A `tendrilLength` change should usually stay inside the tendril family.

Therefore these two questions are different:

1. **How much changed?** — global image difference.
2. **Did change stay inside the influence that this control is supposed to have?** — semantic scope.

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

```json
"tendrilLength": {"region":"tendrils","scope":"region"}
```

### `subtree`

Expected to act on a region **and all descendants**.

```json
"bellWidth": {"region":"bell","scope":"subtree"}
```

This is the correct scope for a parent geometry control when attached children inherit its frame.

### `surface`

A local appearance/deformation control whose spatial permission is the named region, but whose intended meaning is surface/detail rather than body-plan structure.

```json
"foldFrequency": {"region":"bell","scope":"surface"}
```

The validator treats `surface` spatially like `region`; the separate label matters for interpretation and future metrics.

### `global`

Expected to affect the whole organism.

```json
"pulseStrength": {"region":"root","scope":"global"}
```

Do not penalize global controls for wide influence.

## The moving-geometry problem

A region mask rendered only from the baseline state is insufficient for controls that move or resize anatomy.

If a tail endpoint moves from A to B, the image difference contains:

- disappearing pixels at A;
- appearing pixels at B.

A baseline-only tail mask covers A but not B. A correct local tail control can therefore look like it has large semantic spill.

**v0.4.1 rule:** for geometry-affecting controls, allowed spatial support is the union of the region mask rendered in the baseline state and the matching mask rendered in the variant state.

For a `subtree` control, union baseline+variant support for every region in the subtree.

## Producing dual-state masks

Keep the readable source instrumentable and render masks at the **exact same frame/time** as each phenotype.

Example baseline:

```text
harness.html?frame=90&s=baseline.js&region=tendrils
```

Example variant:

```text
harness.html?frame=90&s=variant.js&region=tendrils
```

Store them in parallel directories, preserving the mask filenames used by the morphology contract:

```text
baseline-masks/
  root.png
  bell.png
  tendrils.png
variant-masks/
  root.png
  bell.png
  tendrils.png
```

Then run:

```sh
node scripts/check-control-scope.mjs \
  baseline.png variant.png morphology-contract.json tendrilLength \
  --baseline-mask-dir=baseline-masks \
  --variant-mask-dir=variant-masks
```

Without dual-state mask directories the checker still runs for compatibility, but emits a warning for non-global controls because static masks can overestimate spill.

## Optional mask dilation

Small raster differences can arise from antialiasing, point footprints and shared attachment boundaries. A small tolerance can be applied:

```sh
--dilate=1
```

Dilation expands the **already unioned** allowed support by the given pixel radius.

Use it conservatively. Do not increase dilation simply to make a poor control score look good. A large tolerance erases the distinction between legitimate attachment halos and real dependency leakage.

## What the validator reports

- total difference energy;
- allowed difference energy;
- unexpected spill energy;
- **spill ratio** = difference energy outside allowed support / total difference energy;
- fraction of thresholded changed pixels inside allowed support;
- per-region difference-energy fractions;
- baseline/variant/union mask sizes, so suspiciously broad masks are visible;
- mask mode (`dual-state`, `baseline-override`, or `contract-static`).

For `subtree`, the allowed mask is the union of the region and descendants in both states.

For `region` and `surface`, it is the named region in both states.

For `global`, organism-wide influence is permitted.

## Interpreting spill

There is no universal magic threshold yet. Use comparative evidence.

Good tests:

- compare a local control before/after refactoring;
- compare several controls in one organism;
- compare the same control across animation frames;
- deliberately create a smeared dependency and verify that spill rises;
- verify that a geometry control's spill does **not** jump simply because its anatomy moved farther.

A local control with consistently low spill is more selective than one with the same global changed fraction but high spill.

### Do not optimize spill to zero blindly

Organic attachment creates legitimate boundary effects:

- appendage roots can alter parent attachment pixels;
- translucent overlap can change brightness in a shared region;
- positional inheritance can shift nearby tissue;
- rasterization creates a small halo.

The goal is **predictable influence**, not artificial isolation.

## Control locality vs control usefulness

A perfectly local knob can still be useless if its effect is visually tiny. Evaluate both:

1. **effect strength** — did enough image energy change to matter?
2. **selectivity** — did most of that change occur where expected?

The checker reports both total difference energy and spill ratio so a nearly-no-op control cannot look successful merely because it has zero spill.

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

This keeps morphology measurement from taxing simpler Tsubuyaki workflows.