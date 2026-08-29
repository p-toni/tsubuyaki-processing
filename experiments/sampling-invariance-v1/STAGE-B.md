# sampling-invariance-v1 — Stage B capacity protocol

Status: **preregistered before any holdout execution**.

Stage A is frozen and valid. Stage B asks a different question: does the fixed `K=2` sample-invariant field add useful **structural coverage** to the existing five-representation portfolio under equal independent viable-candidate exposure?

This is not a mutation/search-operator test and not an artistic-admission test.

## Architecture-correct estimand

A sixth representation does not replace the existing five. Therefore the primary quantity is not

```text
new route - best current route
```

averaged with negative penalties on target classes the current repertoire already handles.

The primary quantity is the recovery added by **including** the new representation:

```text
field_added(seed, target)
  = max(0, recovery_field - max(recovery_current_5))
```

For calibration against the current architecture, each existing route receives the analogous leave-one-route-out contribution inside the current five-route portfolio:

```text
route_added_r(seed, target)
  = max(0, recovery_r - max(recovery_other_current_4))
```

The signed `field - best_current` delta is still reported as a diagnostic, but negative values cannot make a portfolio worse because the allocator can retain the existing winner.

## Representation arms

Current portfolio:

```text
recurrence
orbit
family
sheet
filament
```

New arm:

```text
bandlimited-k2
```

`bandlimited-k2` uses the exact Stage-A basis and coefficient prior:

- bandwidth `K=2`;
- coefficient dimension `25`;
- projective zero-set geometry DOF `24`;
- independent standard-normal real coefficients;
- constant coefficient multiplied by `0.25`;
- coefficient vector normalized;
- zero level set is the phenotype.

No target inversion, least-squares fitting to targets, gradient fitting, or SVD reconstruction from target points is allowed in Stage B. SVD remains a Stage-A identifiability instrument only.

## Candidate exposure

Primary archive size:

```text
48 viable independent candidates per representation x master seed
```

All candidate generation is completed before target scoring.

For current routes, use their native frozen seed priors and native hard validity contracts under a Stage-B-specific RNG stream.

For `bandlimited-k2`, each raw coefficient draw is rendered through one fixed viewport and accepted only by a broad target-independent hard-validity contract:

- nonempty finite support;
- support pixel count in `[80, 8000]`;
- dominant bounding-box span >= `0.35` of the canvas.

The viewport is fixed before exposure:

```text
400 x 400 canvas
50 px margin
field domain [0,1]^2 mapped to the central 300 x 300 square
201 x 201 analytic sign grid
```

A cell is part of the rendered zero set when its four analytic field values straddle zero. Cell centers are mapped to the common canvas.

This is a rendering/observation convention, not a target-specific fit.

Every representation may use up to `20 x archive_size` raw attempts to obtain 48 viable independent candidates. Attempts-to-valid and unique rendered phenotype rate are diagnostics. The evidence budget is equal viable exposure, matching the project’s existing representation-capacity semantics.

## Common rendering

Stage B isolates support geometry from route-specific material/alpha.

Every representation is converted to the same binary support image:

```text
background = 9
foreground = 255
canvas = 400 x 400
```

Current routes are sampled at the single canonical static time `t=90` through their native geometry function, then rendered with fixed full-alpha support. The field is rendered from its analytic zero-set support with the same foreground/background values.

Using one canonical frame prevents a static-field experiment from becoming an accidental temporal-motion comparison.

## Metric

Primary target distance: frozen `sparse-geometry-v1` applied to the single common binary-support frame.

```text
recovery = 1 - sparse_geometry_distance
```

No metric weights or tolerances are changed for Stage B.

## Frozen representation-neutral target suite

Targets are deterministic geometric constructions, not outputs of any compared representation and not reference artwork.

Five families x three targets = **15 challenges**:

### disconnected-loops

Multiple separated rotated ellipses with 2, 3, then 4 components.

### nested-loops

Outer contours with one or two offset interior contours; one case uses a non-elliptic closed spline outer boundary.

### concave-loops

Single closed Catmull-Rom contours with distinct smooth concavities / localized curvature.

### open-networks

Open cubic-Bezier arc systems: crossing pair, three-arm branch, and three-arc woven network.

### dense-regions

Filled support regions constructed independently from the compared routes: eccentric ellipse, annular/cavity region, and two-lobed union.

This suite intentionally contains both field-natural and field-unnatural structure. The primary portfolio-added estimand allows a niche representation to be useful without pretending it should dominate all five families.

Target images must pass only preregistered sanity invariants before any candidate outcome is interpreted:

- nonempty finite support;
- dominant span in `[0.45, 0.85]` of canvas;
- support count in `[250, 40000]`;
- all 15 target fingerprints distinct.

A target-contract failure is an instrumentation failure and invalidates execution before outcome interpretation.

## Populations

### Excluded design / engineering population

```text
93001
93007
93019
93037
```

These four seeds may be inspected. They exist only to validate implementation, candidate viability, target sanity, runtime, and reducer contracts. They are not confirmatory evidence.

### Untouched capacity holdout

Frozen before the excluded design run is interpreted:

```text
51001
51031
51043
51047
51059
51061
51071
51109
51131
51133
51137
51151
51157
51169
51193
51197
51199
51203
51217
51229
```

No holdout seed replacement or early stopping.

## Meaningful-win margin

A cell is a **meaningful unique contribution** when its representation beats the relevant current-portfolio comparator by more than:

```text
0.005 recovery
```

This is fixed before design outcomes are inspected and is used only for prevalence/robustness gates; raw continuous added recovery remains primary.

## Advancement gate

After excluded design infrastructure passes, run the 20-seed holdout exactly once with the frozen implementation.

`SAMPLING_INVARIANCE_CAPACITY_PROMISING` iff all hold:

1. complete hard-invariant holdout rectangle and exactly 48 viable candidates per representation/seed;
2. mean field portfolio-added recovery >= `0.002` across all 300 seed-target cells;
3. mean field portfolio-added recovery > the median of the five current-route leave-one-route-out mean added recoveries on the same frozen suite;
4. field meaningful-unique-contribution fraction (`added > 0.005`) >= the median analogous fraction across current routes;
5. field has at least one meaningful unique contribution in **at least two of five** target families;
6. no single one of the 15 targets contributes more than `35%` of total positive field added recovery.

All six gates are applied to the complete fixed sample. Report signed competitive deltas, family effects, target effects, current-route contribution baselines, attempt counts, and unique phenotype rates regardless of decision.

## Stop / advance rules

If not promising:

```text
freeze the negative capacity result
→ do not tune K, coefficient prior, viewport, target suite, or field renderer on these 20 seeds
→ either close this representation line or define a materially new mechanism on a different holdout
```

If promising:

```text
freeze Stage-B representation + target suite + archive semantics
→ power-plan one fresh fixed-sample capacity confirmation
→ only after confirmation design a spectral search operator
→ only after objective search evidence seek blinded artistic admission evidence
```

Neither deterministic arithmetic aliasing nor state-dependent exponentiation may be added to repair this experiment.
