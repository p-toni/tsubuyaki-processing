# Search measurement geometry v1

## Purpose

Design and qualify a structural target-recovery metric after two distinct failures:

```text
pixel MAE
→ sparse background dominates; blank can beat a small translation

sparse-shape-v1 / v2
→ overlap tolerance handles sparsity but repeated/periodic geometry can re-align with itself under translation
```

The #67 sensitivity audit showed the second failure clearly. `sparse-shape-v2` had monotonic aggregate translation means, yet target-level monotonicity failed heavily for repeated families and sheets.

The next hypothesis is therefore architectural rather than another F1-radius/weight tweak:

> separate global placement from intrinsic foreground geometry.

Search-policy optimization remains paused during this experiment.

## Evidence isolation

### Known metric-design population

The earlier #64/#67 audits already exposed:

```text
101, 103, 107
```

These 30 route×seed×regime targets may be reported only as diagnostics.

### Metric holdout

Qualification is decided on:

```text
109, 113, 127
```

These seeds were already consumed by the historical search-policy arc, so this experiment consumes **no fresh search evidence**. But they have not been used in the measurement-design audits, making them an out-of-design metric holdout.

Five routes × three seeds × local/global target = **30 holdout target cases**.

Later already-consumed seeds remain available for a subsequent metric iteration if this candidate fails.

## Frozen controls

For every target:

```text
exact
shift1
shift2
shift3
shift6
shift12
fade50
blank
validAlpha
validNeighbor
unrelatedValid
deleteRightThird
denseBBox
duplicateShift6
```

Control construction matches #67.

## Candidate: sparse-geometry-v1

The metric has four independently interpretable frame-level components.

### 1. Placement

Compute the foreground centroid of candidate and target.

```text
placement = min(1,
  euclidean_centroid_distance /
  (0.10 * min(canvas_width, canvas_height)))
```

At the native 400×400 canvas, a 40px displacement saturates this component.

Rationale: absolute placement is part of target recovery, but it should not be inferred indirectly from local foreground overlap where repeated ribs/instances can alias.

### 2. Translation-aligned shape

Translate the candidate by the rounded centroid offset so candidate and target foreground centroids align, then compute the #64 tolerant foreground F1 at radius 3px.

```text
shape = 1 - aligned_tolerant_F1(radius=3px)
```

Rationale: once global placement has its own component, intrinsic structure can retain raster tolerance without using global overlap as a proxy for displacement.

### 3. Extent

Compare foreground bounding-box width and height:

```text
extent = mean(
  min(1, abs(candidate_width-target_width) / max(target_width,1)),
  min(1, abs(candidate_height-target_height) / max(target_height,1))
)
```

Rationale: centering should not make a contracted, expanded, deleted, or duplicated structure look equivalent merely because its central strokes align.

### 4. Ink mass

Reuse the #64 relative foreground ink-mass error:

```text
mass = abs(candidate_mass-target_mass) / max(candidate_mass,target_mass,epsilon)
```

### Final distance

No post-hoc weight search:

```text
distance = mean(placement, shape, extent, mass)
```

All four components are bounded to `[0,1]` and receive equal weight.

Blank candidate behavior is explicitly defined as all four components = 1, so blank distance = 1.

## Why this should address #67

For a pure integer translation with no clipping:

```text
aligned shape = 0
extent        = 0
mass          = 0
placement     = monotonic displacement
```

Therefore a repeated sheet cannot score a 3px displacement below a 2px displacement merely because another rib happens to overlap after translation.

The metric still has to prove that this decomposition does not create a new failure elsewhere.

## Preregistered holdout qualification contract

`sparse-geometry-v1` qualifies for a full consumed-seed #56–#63 replay only if the **30 metric-holdout targets** satisfy all of:

```text
30/30 exact == 0
30/30 blank == 1
30/30 shift1 < shift2 < shift3 < shift6 < shift12
30/30 shift3 < fade50
>=27/30 shift12 < deleteRightThird
>=27/30 validAlpha < deleteRightThird
30/30 deleteRightThird < blank
>=27/30 validNeighbor < unrelatedValid
>=27/30 validNeighbor < denseBBox
>=27/30 duplicateShift6 > fade50
>=27/30 duplicateShift6 > shift12
```

The strict 30/30 translation requirement is intentional. Unlike v2's overlap behavior, pure displacement is now represented explicitly and should not depend on route periodicity.

The `27/30` thresholds allow route-native phenotype controls to vary naturally while still requiring broad ordering behavior.

## Diagnostic outputs

Report separately for design and holdout populations:

- contract pass counts;
- mean distance per control;
- route-level pass counts;
- component means per control;
- any target violating a qualification relation.

Do not repair a failed relation by adjusting the component weights after results are opened.

## Decision rule

If holdout passes:

```text
sparse-geometry-v1
→ qualified for complete consumed-seed #56–#63 remeasurement
```

It is still not a production artistic metric.

If holdout fails:

```text
search mechanics remain paused
→ inspect which component/construct failed
→ use a later already-consumed seed block for the next metric candidate
```

Do not consume fresh search-policy seeds to rescue the instrument.

## Boundary

Instrument validation only. No artistic promotion, representation pruning, production/default change, benchmark adoption, or `SKILL.md` change follows directly from this experiment.
