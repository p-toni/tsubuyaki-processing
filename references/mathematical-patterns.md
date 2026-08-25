# Mathematical Patterns for Dense Organic Tsubuyaki Processing

This is a vocabulary for **inventing new formulas**, not a catalog to copy literally. Change equations, ratios, exponents, projections, and topology for every new work.

## 1. Core model: sample → latent body → deformation → projection

Think in four layers even if the golfed program collapses them:

```js
sample coordinates
→ k,e,d              // latent body
→ q,c                // deformation / phase
→ X,Y                // projection
```

The strongest tiny systems reuse the same latent quantities across several layers.

## 2. Sampling topology is a visual decision

Topology determines what material the point field can naturally become.

### Flattened 2D — default for dense tissue/sheets

```js
x=i%n
y=i/n
```

This samples two independent coordinates from one loop. It is the recommended starting point when the target is a membrane, folded surface, shell tissue, cavity-rich organism, or other dense sheet-like form.

Typical range: 20k–40k points.

### 1D — deliberately for filaments/ribbons/axial bodies

```js
u=i/s
```

A 1D manifold is intrinsically a **curve**, not a cloud. Consecutive `i` values normally land at neighboring points. Increasing point count makes the curve smoother; it does not change its dimensionality.

A 1D sketch can still produce excellent dense organic work, but it must intentionally fold or decorrelate neighboring samples using devices such as:

- sufficiently separated harmonic scales
- nonlinear phase such as `d*d`
- residue classes / multiple strands
- reciprocal singular deformation
- projection that repeatedly folds the trajectory through image space

Use it when a filamentary or axial skeleton is part of the desired character. If the result reads as a wire or generic spirograph when tissue was intended, change topology before endlessly tuning constants.

### Iterated state — trajectories as material

```js
x+=F(x,y,t)
y+=G(x,y,t)
point(project(x,y))
```

Use when the body should emerge from a dynamical trajectory rather than independent samples.

## 3. Sample count is not density

Ten thousand or forty thousand points can still occupy only a thin curve if many land on nearly the same image-space path.

Treat image-space occupancy, overlap structure, cavities, and framing as separate from point count. Sample count is mainly a performance/resolution parameter.

## 4. The `k/e/d` latent-body family

A productive body model is:

```js
k=A*cos(u*f+phase)
e=u/s-o
d=mag(k,e)
```

Interpretation:

- `e`: axial/spine coordinate
- `k`: lateral/radial oscillation
- `d`: body distance

For 2D sampling, `k` and `e` can derive independently from `x` and `y` rather than a single `u`.

Vary aggressively:

```js
k=(A+sin(x*g-t)*B)*cos(y*f)
e=y/s-o+sin(x*j+t)*C
d=mag(k,e)**p/r+b
```

## 5. Nonlinear distance transforms

`d=mag(k,e)` is only the start:

```js
d=mag(k,e)**2/s
d=mag(k,e)**3/s+b
d=mag(k,e)/s+sin(t)**4
d=mag(k,e)+sin(e*f+t)*a-b
```

Higher powers separate core/exterior more strongly. Even sine powers provide nonnegative breathing envelopes.

## 6. Polar / folded projection

Compact living-body projections often use:

```js
c=d*r-t*s
X=cx+q*cos(c)
Y=cy+q*sin(c)+axialOffset
```

The important move is not polar coordinates themselves; `q` and `c` should depend on the same variables that define the body.

Use half/multi-angle relationships to break rigid circularity:

```js
X=R*sin(c)
Y=S*sin(c/2)+...
```

## 7. Reciprocal singularities

Small terms such as:

```js
.3/k
7/d*sin(k*2)
k/d*wave
```

can create tendrils, cusps, spines and flares very cheaply. Keep coefficients controlled and inspect zero crossings so singularity does not become an accidental `NaN`/off-screen cascade.

## 8. Nested and quadratic phase

High-leverage phase families:

```js
sin(e*f-d*g+t*h)
sin(cos(e)*f-d*g+t)
sin(d*d-t)
cos(d*d+e-t)
```

`d*d` increases phase frequency with distance and is particularly effective for shells, frills and ripple bands.

## 9. Harmonic hierarchy

Use related scales rather than unrelated decorative waves:

- macro frequency: broad silhouette
- meso: folds / ribs / lobes
- micro: texture

One broad wave plus one or two related higher frequencies is generally richer than many independent terms.

## 10. Parity and modulo are anatomy, not density

```js
i%2
i%5
i%9
```

Residue classes can create bilateral sides, petals, strands or segment families without arrays.

They **do not increase intrinsic sampling dimensionality**. `i%2*3` can give a 1D trajectory two anatomical sides, but it does not by itself turn a curve into a sheet.

## 11. Bilateral symmetry with controlled disagreement

```js
side=i%2
c=base+side*p
q=body+side*warp
```

Pure mirroring looks synthetic. Let side/parity also alter one internal phase so both halves share anatomy but not identical deformation.

## 12. Radial petals without explicit petal loops

Use residue classes or angular harmonics:

```js
m=i%n
k=A*cos(u*f+m*p)
```

or

```js
q=base+A*sin(c*n+warp)
```

The harmonic form is often shorter and smoother.

## 13. Axial taper

Cheap envelopes:

```js
A-e*e/s
A/(1+abs(e))
A*(1-(e/s)**2)
k*e
k/d
```

A good tiny term often performs more than one job.

## 14. Phase-coupled radius

```js
q=R+k*(A+B*sin(...))
q=R-e*sin(k)+k/d*(A+B*sin(...))
```

When radius depends on the same body coordinates as the phase, the silhouette itself appears to breathe and reorganize.

## 15. Time architecture

Use one slow master clock and derive local rates algebraically:

```js
t+=PI/180
-t/8
+t/2
+t*2
+sin(t)*A
```

One clock with heterogeneous local multipliers is coherent and golfable.

## 16. Breathing envelopes

```js
sin(t)
sin(t)**2
sin(t)**4
(1+sin(t))/2
```

High even powers produce brief pulses and long rests.

## 17. Internal drift, not rigid motion

Prefer:

```js
c=d/2-t/8
warp=sin(e*9-d*2+t)
```

over computing a static object and rotating it wholesale. Time should reorganize internal geometry.

## 18. One-dimensional manifold checklist

Use 1D when:

- the piece should contain a visible filament/ribbon/spine
- the trajectory intentionally folds through itself many times
- phase changes are strong enough that adjacent samples do not merely reveal a wire

Before accepting a 1D result, render it and inspect occupancy. If tissue was intended and coverage remains very low, switch to flattened 2D rather than assuming 20k points will solve it.

## 19. Flattened two-dimensional manifold checklist

```js
x=i%n
y=i/n
k=x/s-o
e=y/g-p
d=mag(k,e)
```

Advantages:

- true sheet sampling
- reliable membrane/cavity density
- easy bilateral/radial structures
- one countdown loop still suffices

Do not automatically floor `y`; the continuous quotient can create useful diagonal sampling.

## 20. Iterated dynamical systems

```js
x+=dt*F(x,y,z,t)
y+=dt*G(x,y,z,t)
z+=dt*H(x,y,z,t)
point(project(x,y,z,t))
```

Attractor-like systems create dense material from a trajectory. Destructuring is useful when simultaneous-update semantics matter.

## 21. Sequential mini-attractors

```js
r=sin(x*y*a+t)+cos(y*b)
x=sin(y*c)+r*d
y=cos(x*e)+r*f
```

Sequential updates define their own discrete map. Treat that as intentional rather than pretending it is a textbook system.

## 22. Pseudo-3D without WEBGL

Depth can be encoded through radius, phase and overlap rather than paying for a 3D renderer:

```js
s=1/(z+K)
X=cx+x*s
Y=cy+y*s
```

Often a cheaper depth cue is simply `d/e`-dependent radius plus density shading.

## 23. Density as shading

With translucent points, overlap is a rendering model:

- denser overlap → stronger ridge
- sparse overlap → cavity
- moving overlap → changing apparent illumination

On a dark ground, pale overlap becomes brighter. On a light ground, dark translucent ink becomes darker. The geometry can remain the same while the alpha regime changes.

## 24. Controlled degeneracy

Near-collapse regions such as `q≈0`, `k≈0`, or nearly constant `d` create seams, cusps and sheets. Do not remove them merely because they look mathematically awkward.

## 25. Formula invention procedure

1. Decide desired material: sheet, filament, or trajectory.
2. Choose topology accordingly; **default to flattened 2D for dense tissue**.
3. Define a boring body: `k`, `e`, `d`.
4. Produce a recognizable base silhouette with `q` and `c`.
5. Add one macro deformation tied to the body.
6. Add one meso harmonic.
7. Add one temporal coupling.
8. Optionally add one controlled singularity or anatomical parity split.
9. Render representative frames.
10. Inspect occupancy, robust bbox, centroid and clipping; fix topology/framing before decoration.
11. Remove any term whose deletion does not materially change the piece.
12. Only then golf.

## 26. Variation matrix

| Axis | A | B | C |
|---|---|---|---|
| Domain | 1D filament | 2D sheet | iterative attractor |
| Body | linear axial | sinusoidal axial | coupled two-frequency |
| Distance | `mag` | squared | cubed + offset |
| Projection | polar | half-angle folded | axial/radial hybrid |
| Detail | harmonic | reciprocal cusp | parity segmentation |
| Time | slow drift | breathing envelope | nonlinear pulse |

A useful variant changes at least three axes unless the goal is a controlled study.

## 27. Anti-patterns

Avoid unless intentionally subverting the style:

- Perlin-noise flow field as the entire algorithm
- independent randomized particle confetti
- explicit SVG-like anatomy
- static Lissajous plus rotation
- generic spirograph
- assuming high sample count implies dense image-space coverage
- adding terms merely because tweet budget remains

The target is **compressed causal geometry**.