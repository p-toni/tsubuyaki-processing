# Mathematical Patterns for Dense Organic Tsubuyaki Processing

This is a vocabulary for **inventing new formulas**, not a catalog to copy literally. Use roles and relationships; change equations, ratios, exponents, projections, and topology for every new work.

## 1. Core mental model: sample → latent body → deformation → projection

A strong sketch can often be understood as four layers:

1. **sample parameter(s)** — where are we on the hidden manifold?
2. **latent body coordinates** — what is the local axial/radial geometry?
3. **deformation field** — how is it folded, frilled, pinched, or breathed?
4. **projection** — where does that point land on the 2D canvas?

Readable schematic:

```js
u = sample / scale;
k = lateral(u, t);
e = axial(u, t);
d = hypot(k, e);
q = radius(k, e, d, u, t);
c = phase(k, e, d, u, t);
X = centerX + projectionX(q, c, ...);
Y = centerY + projectionY(q, c, ...);
point(X, Y);
```

The code-golf form may collapse all of this into one expression, but the design process should retain these conceptual layers.

## 2. The `k/e/d` latent-body family

A highly productive family is:

```js
k = A * cos(u * f + phase);
e = u / s - offset;
d = mag(k, e);
```

Interpretation:

- `e` behaves like a spine/head-to-tail coordinate
- `k` oscillates laterally around that spine
- `d` measures distance in the latent cross-section

Vary it aggressively:

```js
k=(A+sin(u*g-t)*B)*cos(u*f)
k=A*cos(u*f)*sin(u*h)
e=u/s-o+sin(u*j+t)*C
d=mag(k,e)**p/r+b
```

This can produce bells, pods, shells, centipede-like tissue, or floral tubes depending on projection.

## 3. Nonlinear distance transforms

`d=mag(k,e)` is only the start.

### Square / cube

```js
d=mag(k,e)**2/s
```

or

```js
d=mag(k,e)**3/s+b
```

Higher powers create stronger separation between core and exterior and often turn smooth tubes into shells/frills.

### Breathing offset

```js
d=mag(k,e)/s+sin(t)**4
```

Using an even power of sine creates a nonnegative pulse: expansion/contraction without sign reversal.

### Mixed body/ripple distance

```js
d=mag(k,e)+sin(e*f+t)*a-b
```

This makes the phase surface itself ripple along the body axis.

## 4. Polar projection

The most compact “living body” projection often uses:

```js
c=d*r-t*s
X=cx+q*cos(c)
Y=cy+q*sin(c)+axialOffset
```

The important move is not polar coordinates by themselves; it is to make `q` and `c` depend on the same latent variables that define the body.

Possible axial offset:

```js
+d*A
+e*A
+u/s
```

This turns a ring into a descending/ascending organism.

## 5. Half-angle and multi-angle projections

Using `c/2`, `c*2`, `c*4` in one coordinate breaks rigid circularity:

```js
X=R*sin(c)
Y=S*sin(c/2)+...
```

or

```js
Y=R*sin(c*4)+...
```

This produces lobes, folds, mirrored bell shapes, and multi-petal cross-sections.

## 6. Reciprocal singularities: tendrils and spikes

Small reciprocal terms create dramatic structure cheaply:

```js
.3/k
7/d*sin(k*2)
k/d*wave
```

Visual effect:

- near `k=0`: thin lateral cusp/tendril
- near `d=0`: central eruption or filament

Rules:

- use small coefficients
- inspect the region around zero
- allow some points to fly away only if the silhouette remains coherent
- avoid accidental all-frame `Infinity/NaN` cascades

A controlled singularity is one of the most character-efficient ways to create “anatomy.”

## 7. Nested trigonometric phase

Organic detail often comes from one periodic function warping another:

```js
sin(e*f-d*g+t*h)
sin(cos(e)*f-d*g+t)
sin(d*d-t+cos(e+t/2))
```

Why it works:

- the outer sine bounds the deformation
- the inner phase varies nonlinearly across the body
- reuse of `d/e/t` couples texture to form

Avoid piling unrelated nested functions. One or two phase couplings are usually richer than five decorative waves.

## 8. Quadratic phase: `d*d`

```js
sin(d*d-t)
```

This increases frequency with distance from the center, producing shell/ripple/frill structures. It is especially effective when multiplied by `k`, `e`, or `k/d`.

Variations:

```js
sin(d*d-t+m)
sin(d*d*.5-t*2)
cos(d*d+e-t)
```

## 9. Harmonic body texture

Use integer-ish ratios to create coherent segmentation:

```js
sin(k*2)
cos(e*9)
sin(d*3)
sin(y/25)
```

The ratios do not need to be musical or exact integers. The important property is **related scales**: one broad wave and one fine wave sharing the same coordinate.

Good exploration strategy:

- macro frequency: ~0.03–0.3 cycles/unit
- meso frequency: 2–5× macro
- micro frequency: 2–4× meso

Then compress numeric constants after visual tuning.

## 10. Parity and modulo as anatomy

Alternation:

```js
i%2
```

can switch two lobes, twist sides, or offset a phase by roughly π.

Segment families:

```js
i%5
i%9
i%16
```

can create petals/arms/strands without arrays.

Instead of a branch:

```js
phase += i%2*3
```

The value `3` is a cheap approximation to π when exact opposition is not required.

## 11. Bilateral symmetry with controlled disagreement

Pure mirroring often looks synthetic. Let parity create two related but phase-shifted sides:

```js
side=i%2
c=base+side*p
q=body+side*smallWarp
```

Then let the same `side` enter a nested sine. This produces bilateral “creature” cues while preserving dynamical variation.

## 12. Radial petals without explicit petal loops

Use a modulo family as a phase bucket:

```js
m=i%n
k=A*cos(u*f+m*p)
```

or encode petal count inside an angular harmonic:

```js
q=base+A*sin(c*n+warp)
```

The latter is often shorter and smoother.

## 13. Axial taper

Creature/flower forms need varying width along the body.

Cheap envelopes:

```js
A-e*e/s
A/(1+abs(e))
A+e*sin(...)
A*(1-(e/s)**2)
```

For golf, sometimes a term already present can serve as the envelope:

```js
k*e
k/d
u/s*k
```

The best tiny equations make one term perform two jobs.

## 14. Phase-coupled radius

Rather than a static radius:

```js
q=R+k*(A+B*sin(...))
```

or

```js
q=R-e*sin(k)+k/d*(A+B*sin(...))
```

This makes the silhouette itself ripple and breathe.

## 15. Time architecture

Use a **slow master clock** and derive local speeds algebraically.

Typical readable approach:

```js
t += Math.PI / 180;
```

Then:

```js
-t/8
+t/2
+t*2
+sin(t)*A
+sin(t*9-phase)
```

Do not use independent frame counters for different motions. One clock with multiple rational-ish rates creates coherence and saves characters.

## 16. Breathing envelopes

Smooth amplitude modulation:

```js
sin(t)
sin(t)**2
sin(t)**4
(1+sin(t))/2
```

Even powers are compact nonnegative envelopes. High even powers produce short pulses with long rests.

## 17. Drifting phase vs rotating object

Avoid merely rotating a finished shape. Instead alter the internal phase:

```js
c=d/2-t/8
warp=sin(e*9-d*2+t)
```

The geometry reorganizes itself as time passes, which reads as growth/breathing rather than rigid motion.

## 18. One-dimensional dense manifolds

A single sample `u` can generate elaborate 2D forms when several frequencies derive from it:

```js
u=i/s
k=A*cos(u*f)
e=u/g-o
d=mag(k,e)
```

Advantages:

- tiny loop syntax
- smooth filament/surface-like density
- easy to push to 10k+ points

Use when the form should read as a continuous ribbon/body.

## 19. Flattened two-dimensional manifolds

Derive two coordinates from one index:

```js
x=i%n
y=i/n
```

Then:

```js
k=x/s-o
e=y/g-p
d=mag(k,e)
```

Advantages:

- true surface sampling
- easy bilateral/radial structures
- 20k–40k points reveal smooth sheets

Avoid integer-flooring `y` if the continuous quotient creates a pleasing diagonal sampling and no indexing semantics require integers.

## 20. Iterated dynamical systems

Instead of mapping independent samples, update state:

```js
x += dt * F(x,y,z,t)
y += dt * G(x,y,z,t)
z += dt * H(x,y,z,t)
point(project(x,y,z,t))
```

Attractor-like systems produce a different authenticity: the dense shape emerges from a trajectory rather than a static manifold.

Golf opportunities:

- tiny `d=5e-4`-style integration step
- one loop with 20k–30k iterations
- array destructuring when simultaneous update semantics matter
- projection can add a periodic shell/rotation on top of the attractor

## 21. Sequentially coupled mini-attractor

For original experiments, a cheap iterative map can be:

```js
r=sin(x*y*a+t)+cos(y*b)
x=sin(y*c)+r*d
y=cos(x*e)+r*f
```

Because `y` uses the newly updated `x`, this is not a textbook simultaneous system—it is its own discrete map. That is fine if treated as intentional.

## 22. Pseudo-3D without WEBGL

A latent third coordinate can affect scale/angle rather than using a 3D renderer:

```js
s=1/(z+K)
X=cx+x*s
Y=cy+y*s
```

But division/perspective boilerplate can be expensive. A cheaper “depth” cue is often:

- radius changes with `d/e`
- alpha is fixed but overlap density varies
- phase shifts with latent depth

This is why many striking organic Tsubuyaki works remain plain 2D `point()` sketches.

## 23. Density as shading

With translucent stroke, the equation does not need explicit lighting. Regions where many samples land near each other become brighter.

This creates:

- surface curvature cues
- dark cavities
- luminous ribs
- motion blur-like tissue

Design implication: **sample distribution is part of the shading model**.

## 24. Controlled degeneracy

Useful forms often arise where a mapping nearly collapses a dimension:

```js
q≈0
k≈0
d≈constant
```

Near-degenerate regions create seams, cusps, spines, and sheets. Do not optimize them away merely because they look “mathematically awkward.”

## 25. Formula invention procedure

For a new sketch, do this in readable code:

1. Pick sample topology: 1D, flattened 2D, or iterative.
2. Define a boring body: `k`, `e`, `d`.
3. Produce a recognizable base silhouette with `q` and `c`.
4. Add **one** macro deformation tied to `d/e`.
5. Add **one** meso harmonic tied to `k/e`.
6. Add **one** temporal coupling.
7. Optionally add one controlled singularity or parity split.
8. Remove any term whose deletion does not materially change the piece.
9. Tune constants until both still frames and motion feel intentional.
10. Only then golf.

## 26. Variation matrix

To make meaningful variants, change rows rather than random constants.

| Axis | A | B | C |
|---|---|---|---|
| Domain | 1D filament | 2D sheet | iterative attractor |
| Body | linear axial | sinusoidal axial | coupled two-frequency |
| Distance | `mag` | squared | cubed + offset |
| Projection | polar | half-angle folded | axial/radial hybrid |
| Detail | harmonic | reciprocal cusp | parity segmentation |
| Time | slow drift | breathing envelope | nonlinear phase pulse |

A good variant changes at least three axes unless the goal is a controlled study.

## 27. Anti-patterns

Avoid these unless intentionally subverting the style:

- Perlin-noise flow field as the entire algorithm
- hundreds of independent randomized particles
- rainbow HSB cycling with no mathematical role
- explicit SVG-like flower petals
- static Lissajous curve plus rotation
- generic spirograph
- dozens of arbitrary magic numbers that do not share latent coordinates

The target is not merely “complex-looking.” It is **compressed causal geometry**.
