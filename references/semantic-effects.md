# Semantic Effect Descriptors

v0.5 separates two questions that v0.4.1 could not distinguish:

1. **scope correctness** — did change stay inside the region/subtree it was allowed to affect?
2. **effect correctness** — did the intended observable actually move in the intended direction?

A control can have perfect scope locality and still be semantically wrong. A `finSpan` parameter that only makes fins taller should not pass merely because it changes only fin pixels.

## Contract form

Add an `effect` descriptor to controls that have a meaningful measurable expectation:

```json
"finSpan": {
  "region": "fins",
  "scope": "region",
  "effect": {
    "source": "mask",
    "metric": "width",
    "direction": "increase",
    "minRelativeChange": 0.05
  }
}
```

The effect descriptor is design-time metadata and does not consume tweet characters.

## Sources

### `mask`

Use the region's own baseline/variant diagnostic masks. Best for geometry:

- `area`
- `width`
- `height`
- `centroidX`
- `centroidY`

Examples:

- fin span → mask width increases;
- tendril length → mask height increases;
- attachment control → centroid moves in a declared direction.

### `image`

Measure appearance inside each state's own region mask:

- `visibleFraction`
- `meanContrast`

Useful for surface/detail controls where geometry itself may not change much.

## Direction

- `increase`
- `decrease`
- `any`

`any` means the descriptor checks that a material effect occurred, but does not claim a sign.

Use `minRelativeChange` to reject controls that technically move the metric but are visually negligible. Keep thresholds conservative and calibrate them from repeated examples rather than treating 5% as universal.

## Validation

Render baseline and variant at the same frame, plus region masks for each state, then run:

```sh
node scripts/check-control-effect.mjs \
  baseline.png variant.png morphology-contract.json finSpan \
  --baseline-mask-dir=baseline-masks \
  --variant-mask-dir=variant-masks
```

Run this **in addition to** `check-control-scope.mjs`.

A useful semantic control should satisfy both:

```text
scope correctness  — changed where expected
effect correctness — changed what was expected
```

Neither implies the other.

## Examples

```json
"finSpan": {
  "region":"fins",
  "scope":"region",
  "effect":{"source":"mask","metric":"width","direction":"increase","minRelativeChange":0.05}
},
"tailLength": {
  "region":"tail",
  "scope":"region",
  "effect":{"source":"mask","metric":"height","direction":"increase","minRelativeChange":0.05}
},
"cavityStrength": {
  "region":"cavity",
  "scope":"region",
  "effect":{"source":"mask","metric":"area","direction":"increase","minRelativeChange":0.03}
},
"ribStrength": {
  "region":"shell",
  "scope":"surface",
  "effect":{"source":"image","metric":"meanContrast","direction":"increase","minRelativeChange":0.03}
}
```

The cavity example assumes the cavity itself is rendered as a diagnostic region mask. If the control instead changes darkness inside a fixed cavity, use an image metric.

## Limits

These are low-dimensional semantic observables, not computer vision understanding. A width increase can still be aesthetically bad. Use the validator as a falsification tool:

- it can prove a claimed simple effect did **not** occur;
- it cannot prove the resulting anatomy is beautiful or biologically plausible.

Prefer descriptors for controls whose intended effect can be stated clearly. Do not invent a weak metric merely to make every control machine-testable.