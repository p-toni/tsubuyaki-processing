# Morphology Composition for Controllable Complexity

This reference translates ideas from procedural modeling, developmental encodings, implicit modeling, and generative morphology into a form useful for **tweet-sized p5.js**.

The goal is not biological realism. It is **controllable apparent anatomy**: a small number of mathematical rules should create a body that visibly contains differentiated regions, attached organ families, repetition-with-variation, and coherent motion.

## 1. Why complex creatures need indirect encoding

A 259-weighted-character JavaScript budget cannot afford a conventional scene graph with one object, transform, loop, and state block per body part.

The useful alternative is an **indirect encoding**:

- a small genotype = shared coordinates + selectors + generators + attachment rules
- a large phenotype = many visible regions/appendages produced by those rules

This mirrors a recurring idea in procedural systems: compact developmental descriptions can generate repeated, symmetric, hierarchical structure without specifying every instance independently.

For Tsubuyaki Processing, the practical implication is:

> count **independent rules**, not visible parts.

A creature with six tendrils may still use one tendril rule.

## 2. The morphology graph is design-time structure

Before code golf, sketch a directed graph:

```text
root body
├── crown / head region
├── lateral organ family ×2
└── ventral appendage family ×4
    └── local fringe detail
```

Each node/family has:

- parent
- attachment region
- local coordinate/frame
- extent/envelope
- repetition/symmetry rule
- inherited phase
- local deformation

Do **not** preserve this graph literally in the final code. It is a reasoning representation that should be compiled into shared algebra.

### Good graph

```text
shell
├── fin family ×2
└── tendril family ×6
```

Two reusable generators.

### Bad graph

```text
shell
├── left fin
├── right fin
├── tendril 1
├── tendril 2
├── tendril 3
...
```

This encourages independent formulas and destroys compression.

## 3. Positional information: one coordinate system, many interpretations

Developmental systems create regional identity from position. The useful abstraction here is simple: define shared coordinates once and let different anatomical rules respond to them.

Typical shared fields:

```js
e // axial position: crown → trunk → tail
k // lateral/radial position
 d=mag(k,e)
t // master developmental/animation time
```

Then regions are functions of `e/k/d`, not independent canvas positions.

Example:

```js
crown = e<0
trunk = e>=0
fold = sin(d*d-t)
```

The crown and trunk can have different width laws while sharing the same phase/material field.

**High leverage:** the same positional coordinate can control width, attachment location, fold amplitude, and motion lag.

## 4. Regional identity: hard selectors vs soft influence fields

### Hard selector

```js
e<a?A:B
```

Advantages:

- cheap
- crisp anatomical regime change
- easy to golf

Risks:

- visible seams
- abrupt motion discontinuity

Good for shell/body vs appendage regimes, head vs tail, or strongly distinct material zones.

### Triangular soft field

Readable:

```js
h=max(0,1-abs((e-a)/r))
```

This gives a local influence centered at `a` with radius `r`.

Useful for:

- shoulder/fin bases
- crown bulge
- cavity strength
- local pulse amplitude

### Rational soft field

```js
h=1/(1+((e-a)/r)**2)
```

Smooth long-tailed influence. More expensive, but useful during design.

### Periodic region field

```js
h=sin(e*f)
```

Useful for ribs, repeated segments, alternating body widths.

**Rule:** every envelope should ideally control multiple related anatomical consequences. If `h` only adds one decorative wiggle, it is probably not worth its characters.

## 5. Root body before children

The root is the organism's dominant mass. It should already establish:

- polarity / direction
- center of mass
- silhouette hierarchy
- cavity or volume cue
- primary deformation language

Common root families:

### Axial pod / larva

```js
width=A-e*e/s
k=width*sin(u)
```

### Bell / crown

Use a broad top-heavy envelope and a folded radial projection.

### Shell / folded sheet

Use flattened 2D sampling and couple radius/phase to `d` and one axial field.

### Bilateral torso

Use `side=i&1` only after establishing a centerline/root mass; parity should alter one generator rather than create two unrelated halves.

If the root is generic toroidal cloth, adding appendages usually produces generic toroidal cloth with appendages.

## 6. Local attachment frames

This is the most important control concept after regionalization.

A child organ should originate from a parent anchor and inherit parent orientation.

Readable 2D frame:

```js
X = Xp + u*cos(c) - v*sin(c)
Y = Yp + u*sin(c) + v*cos(c)
```

Where:

- `(Xp,Yp)` = parent anchor
- `c` = parent local orientation/phase
- `(u,v)` = child-local coordinates

This gives two key invariants:

1. moving/deforming the root carries the child with it;
2. changing child geometry does not require re-solving global placement.

### Golfed equivalent

Often you do not need an explicit matrix. Reuse the parent's phase/radius:

```js
C=c+r*a
Q=q+local
point(cx+Q*cos(C),cy+Q*sin(C)+...)
```

This is an **attachment frame encoded as phase inheritance**.

## 7. Skeletons and implicit influence

Skeletal/implicit modeling suggests a powerful mental model: anatomy can be organized around lower-dimensional structures (spines, curves, anchors) while the visible body is a field around them.

For tiny code:

- spine coordinate → `e`
- distance from spine → `k` or `d`
- field strength → width/radius envelope
- child attachment → particular `e` range plus side/repetition selector

You usually do not need an actual signed-distance implementation. The important abstraction is:

> **structure lives on a skeleton; material lives in a field around it.**

This naturally separates topology from appearance.

## 8. Repetition and symmetry as operators

### Bilateral

```js
s=i&1
```

Then use `s` to alter phase or lateral sign.

Do not merely duplicate:

```js
x*=s?1:-1
```

Prefer controlled disagreement:

```js
phase=base+s*3+e*.1
```

### N-fold family

```js
r=i%n
```

`r` can control:

- attachment angle
- attachment axial position
- local phase
- local length

### Family + side packing

For paired families:

```js
r=i%6
s=r&1
p=r>>1
```

One residue can encode side and family identity.

This is highly character-efficient because integer structure acts as a tiny morphology address.

## 9. Repetition with variation: the CPPN lesson

Compositional pattern-producing networks are useful here conceptually because they create regularity, symmetry and repetition from composed functions of position.

The Tsubuyaki equivalent is to let a repeated organ generator depend on both:

- discrete identity `r`
- global position/body fields `e/d/t`

Instead of exact copies:

```js
angle=r*a
```

use:

```js
angle=r*a+sin(e+t)*b
length=L+sin(r+e)*v
```

The same compact function creates a family whose members are recognizably related but not identical.

This often reads more life-like than perfect rotational or bilateral cloning.

## 10. Three composition modes

### Mode A — one continuous shared field

All regions alter the same `q/c/X/Y` map.

Use when:

- anatomy is one membrane/body
- regions differ mainly in width/fold/cavity behavior
- seamless attachment matters

Cheapest mode.

Example concept:

```js
width = base + crown*20 + finZone*side*15
```

### Mode B — sample multiplexing

One loop uses index ranges/residues for different material families.

Example design-time idea:

```js
if(i<Nbody) sampleBody(i)
else sampleTendril(i-Nbody)
```

Golf toward:

```js
r=i%M
r<k?bodyLaw:appendageLaw
```

Use when root is a 2D sheet but appendages need 1D filament topology.

### Mode C — separate generators

Separate functions/loops in readable code.

Use during design when it clarifies anatomy. Before final golf, attempt to convert to A or B.

Keep separate only if merging destroys the defining body plan.

## 11. Hierarchical deformation

Complex forms feel coherent when deformation follows hierarchy:

```text
world/root motion
  → region deformation
    → organ-family phase
      → micro-fold
```

Example:

```js
rootPhase = d/3-t/4
finPhase = rootPhase + side*3 + sin(e+t)/5
rib = sin(d*d/9+t*2)
```

This produces different motion scales from one clock.

Avoid:

```js
root rotates by t
fin wiggles by u
appendage jitters by noise(frameCount)
```

Independent motion sources make the anatomy look assembled.

## 12. Structure vs surface

Maintain this separation in the readable stage:

### Structural variables

- axial span
- root width
- region boundaries
- attachment anchors
- appendage count
- symmetry mode
- child length

### Surface variables

- fold frequency
- micro-rib amplitude
- point alpha
- small phase perturbation

When surface variables alter attachment or silhouette dramatically, control is lost.

During golf, variables may be algebraically merged **after** the distinction has been tested.

## 13. Morphological hierarchy

At thumbnail scale, the viewer should perceive levels:

1. root mass / overall pose
2. secondary organ families
3. tertiary regions/cavities/folds
4. point texture

If all scales have equal contrast, complexity becomes noise.

Ways to enforce hierarchy without extra drawing primitives:

- stronger envelope for root than child detail
- appendage widths smaller than root widths
- lower amplitude for micro-harmonics
- negative-space gaps around attachment families
- different density overlap rather than different colors

## 14. Negative space is part of anatomy

A complex organism needs separations so parts are legible.

Useful negative-space mechanisms:

- cavity term reducing radius in one region
- phase offsets that split lobes
- taper near attachment roots
- lower sampling density in internal zones
- singular folds that open dark seams

Do not fill every part of the robust bounding box. Density is material; empty regions reveal topology.

## 15. Morphology capacity under 259 weighted characters

Treat the tweet budget as a capacity bound on **independent morphology decisions**.

A realistic final structure might contain:

```text
1 shared sample/index system
1 root body law
1 selector/envelope for regional differentiation
1 repeated appendage-family law
1 shared projection
1 master time law
```

From those six ingredients, the image can contain many apparent parts.

A poor use of capacity is six unrelated visual decorations.

### Capacity heuristic

Before golf, ask of every body feature:

> Can this be expressed as another interpretation of an existing field?

If yes, it is cheap complexity.

If it requires a new coordinate system, loop, state machine, or isolated transform, it is expensive complexity.

## 16. Morphology compilation recipe

Given a complex request:

1. Draw a morphology graph in words.
2. Merge identical siblings into organ families.
3. Choose one main polarity coordinate `e`.
4. Choose one lateral/radial coordinate `k`.
5. Define the root silhouette.
6. Define 1–2 regional fields over `e/k/d`.
7. Attach one repeated family using parent phase/frame.
8. Add one position-dependent variation to that family.
9. Add one shared surface deformation.
10. Animate all layers from one master clock.
11. Render and verify hierarchy/attachment.
12. Replace explicit nodes with selectors/residue classes.
13. Merge topologies through sample multiplexing if useful.
14. Remove any rule whose deletion leaves the body plan recognizable.
15. Only then perform JavaScript code golf.

## 17. Failure diagnoses

### "Blob with random arms"
Cause: appendages positioned globally rather than attached to a parent frame.

Fix: define an anchor region and inherit root phase.

### "Perfect logo / mandala"
Cause: symmetry without positional variation.

Fix: let each repeated member depend on axial/body fields in addition to residue identity.

### "Busy but anatomically flat"
Cause: complexity placed in micro-harmonics rather than body regions.

Fix: create a root/secondary/tertiary amplitude hierarchy.

### "Creature falls apart while animating"
Cause: independent clocks or child positions.

Fix: parent-relative coordinates + phase inheritance.

### "Readable source is controllable; golfed version isn't"
Cause: semantic constants were merged before visual equivalence/control tests.

Fix: test controls first, then merge only parameters whose coupling is visually acceptable.

### "Cannot fit under 259"
Cause: too many independent rules.

Fix in this order:

1. merge sibling parts into one family;
2. reuse regional field for multiple effects;
3. use parity/modulo instead of branches;
4. use parent phase instead of explicit child transform;
5. remove tertiary detail;
6. simplify body plan deliberately.

Do not preserve complexity by making the code nonfunctional or visually incoherent.