# Semantic Control Strategies

v0.3 aims for **controllable complexity**: a user should be able to ask for a wider crown, shorter appendages, stronger bilateral disagreement, a deeper cavity, or slower pulse without the entire organism changing unpredictably.

The readable source is where control lives. The final golfed source may collapse names and algebra after those behaviors are tested.

## 1. A good control has a semantic job

Prefer parameters that map to one visual concept:

```js
rootWidth
rootLength
crownDepth
attachmentHeight
finSpan
appendageLength
appendageCount
cavityStrength
foldFrequency
pulseStrength
phaseLag
```

Avoid a parameter that simultaneously means "root width + tentacle speed + fold count" unless that coupling is intentionally part of the organism's developmental logic.

## 2. Control classes

### Global structure

Changes the whole body plan:

- polarity / orientation
- overall root width/length
- root curvature
- symmetry mode

These may legitimately affect most pixels.

### Regional structure

Should mainly affect a bounded anatomical zone:

- crown depth
- thorax width
- tail taper
- cavity strength

### Organ-family controls

Should affect one repeated family:

- appendage count
- appendage length
- fin span
- family phase spread

### Motion controls

- root pulse amplitude
- child phase lag
- local bend amplitude

### Surface controls

- fold/rib frequency
- small deformation amplitude
- alpha / point size

Keep surface controls subordinate to structural controls.

## 3. Locality is the practical definition of control

A control is useful when changing it mostly changes the intended visual region or property.

For a regional/local knob:

```text
change intended region >> change unrelated regions
```

For a global knob, broad change is expected.

This is why control testing should compare **the same frame/time**. Otherwise ordinary animation is mistaken for parameter sensitivity.

## 4. Finite-difference testing

For each named control `p`:

```text
baseline: p
variant:  p * 1.1 .. 1.25
```

Render the exact same frame. Then inspect:

- changed pixel fraction
- robust difference bounding box
- difference centroid
- whether the changed region corresponds to the intended anatomy

The repository's `scripts/check-control.mjs` provides the mechanical part. Visual interpretation is still required.

## 5. Sensitivity scale

A useful semantic knob should usually respond to a modest change.

If +20% produces almost no visible difference:

- the control is too weak;
- another term dominates it;
- or it is not worth preserving as a named control.

If +5% destroys the entire organism:

- the parameter is near a singular regime;
- it controls too many dependencies;
- or it belongs in an expert/fragile category rather than normal variation knobs.

## 6. Disentanglement before golf

Do not prematurely reuse constants just because identical numeric values happen to work.

Readable stage:

```js
const finSpan=30;
const foldFrequency=30;
```

Even if both are `30`, keep them separate until control tests establish whether their coupling is desirable.

Golf stage may deliberately merge them if:

1. the final values can be shared;
2. future user variation is no longer required in the tweet code itself;
3. the rendered result remains equivalent.

The readable source remains the editable semantic master.

## 7. Parameter inheritance

Some coupling is desirable because it preserves organism coherence.

Example:

```text
root pulse
  └── appendage pulse = root pulse * 0.6 + phase lag
```

This is **hierarchical coupling**, not accidental entanglement.

Good inherited controls:

- child motion follows root motion
- organ thickness scales mildly with root scale
- attachment angle follows root local orientation

Bad inherited controls:

- changing cavity depth changes appendage count
- changing fold frequency moves the entire centroid
- changing point alpha changes anatomical attachment

## 8. Discrete controls

Counts and symmetry classes are discrete:

```js
appendageCount=4
lobeCount=6
```

These may reorganize a larger portion of the field because residue classes change.

Judge them by **family identity**, not difference locality:

- do appendages still attach in the right region?
- does the root remain recognizable?
- does increasing count create more instances rather than a different unrelated topology?

## 9. Stable ranges

For every important control, establish a useful range in the readable sketch.

Example:

```text
crownDepth:      0.7–1.3
appendageLength: 0.6–1.5
pulseStrength:   0–0.4
foldFrequency:   4–12
```

The exact values depend on the formula. The point is to know whether a semantic knob is robust or only works at one magic number.

A control that only works in a tiny interval is fragile and should not be offered casually as a variation knob.

## 10. Control budgets

Do not expose dozens of parameters. For a tweet-sized system, 4–8 meaningful readable controls are usually enough:

- 2–3 structural
- 1–2 organ-family
- 1–2 motion
- 1 surface

This matches the actual information capacity of the final program better than a large conventional generative-art control panel.

## 11. Control hierarchy for user prompts

Translate natural-language requests in this order:

### "more complex"
Increase **body-plan complexity** first:

1. add/differentiate a region;
2. add an organ family;
3. add repetition-with-variation;
4. only then add micro-detail.

### "more animal-like"
Increase:

- polarity
- attachment legibility
- region hierarchy
- bilateral/radial family structure
- hierarchical motion

Not simply noise/detail.

### "more alien"
Change relationships while preserving structural coherence:

- unusual repetition count
- asymmetric family phase
- nonlinear taper
- displaced cavity
- mismatched but inherited appendage phase

### "more delicate"
Reduce structural thickness/amplitude, increase negative space, lower alpha, lengthen thin appendages.

### "more massive"
Increase root envelope and overlap density while keeping secondary anatomy subordinate.

## 12. Variation protocol

When presenting variation knobs, state expected effect:

```text
appendageLength +20% → longer ventral family, root unchanged
cavityStrength +15%  → deeper central negative space
phaseLag +0.2        → appendages trail root pulse more visibly
foldFrequency 6→9    → tighter surface ribs, silhouette mostly unchanged
```

If you cannot predict the effect, the parameter is not yet a good semantic control.

## 13. When controls conflict

Two controls may compete for the same geometric degree of freedom.

Example:

- crown width modifies `q`
- fin span also modifies `q` in crown region

Resolve by:

1. regional envelope separation;
2. multiplicative hierarchy (`rootWidth * (1+finEnvelope*finSpan)`);
3. parent + child local coordinates;
4. intentionally documenting the coupling.

Do not solve it by adding unrelated absolute offsets.

## 14. Compression rule

Semantic control is required in the **expanded source and generation process**, not necessarily at runtime in the final tweet.

The final tweet is an instantiated organism, not a configurable UI.

Therefore it is valid to:

- inline tuned values;
- merge constants;
- algebraically factor controls away;

only after the readable version has demonstrated controllability and the final render preserves the selected phenotype.