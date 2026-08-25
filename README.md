# tsubuyaki-processing

A production-oriented Agent Skill for generating authentic, tweet-sized **#つぶやきProcessing**: dense mathematical p5.js sketches whose organic forms emerge from compact coupled equations.

## v0.3 — controllable complexity

v0.2 fixed the generation mechanics: dense-organic work defaults to 2D sheet sampling, framing/density can be inspected mechanically, and 1D is treated as an intentional filament topology.

v0.3 addresses the next problem: **how do we make forms substantially more anatomically complex while retaining control and still fitting in a tweet?**

The answer is a morphology compiler:

```text
intent
→ morphology graph
→ shared positional fields
→ regional identity
→ attached/repeated organ families
→ hierarchical motion
→ semantic-control tests
→ render / visual QA
→ representational compression
→ JavaScript golf
```

The central rule is:

> **More apparent parts than independent formulas.**

A four-tendril family should normally be one mathematical generator instantiated four ways, not four formulas.

## Repository

```text
tsubuyaki-processing/
├── SKILL.md
├── README.md
├── references/
│   ├── research-notes.md
│   ├── controllable-complexity-research.md
│   ├── code-golf-techniques.md
│   ├── mathematical-patterns.md
│   ├── morphology-composition.md
│   ├── control-strategies.md
│   ├── style-guide.md
│   └── real-examples.md
├── templates/
│   ├── basic-skeleton.js
│   ├── filament-skeleton.js
│   ├── compound-morphology.js
│   ├── advanced-parametrics.js
│   └── harness.html
├── examples/
│   ├── 01-breathing-calyx.md
│   ├── 02-folded-creature.md
│   └── 03-coupled-attractor.md
└── scripts/
    ├── check-length.mjs
    ├── check-visual.mjs
    └── check-control.mjs
```

## What changed in v0.3

### 1. Morphology contracts

Before equations, compound requests are decomposed into:

- polarity / main axis
- root mass
- anatomical regions
- repeated organ families
- symmetry law
- attachment law
- motion inheritance
- surface detail

This makes the intended body plan explicit without forcing literal object-oriented drawing.

### 2. Shared positional fields

Instead of giving every part its own coordinate system, the organism establishes common body coordinates such as:

```js
e // axial position
k // lateral/radial position
d=mag(k,e)
t // master time
```

Regions interpret these shared fields differently. This turns one coordinate system into many anatomical behaviors cheaply.

### 3. Regional identity

Head/crown/trunk/cavity/attachment zones are encoded with compact selectors or influence fields:

```js
e<a?A:B
max(0,1-abs((e-a)/r))
sin(e*f)
```

A good region field drives several related consequences, such as width, fold amplitude and appendage attachment—not one decorative term.

### 4. Parent-relative attachment

Secondary anatomy inherits the parent's local frame/phase instead of being placed with arbitrary screen offsets.

Readable form:

```js
X=Xp+u*cos(c)-v*sin(c)
Y=Yp+u*sin(c)+v*cos(c)
```

Golfed forms often reuse the parent's `q/c` directly.

This makes appendages stay attached while the root breathes/deforms.

### 5. Repetition with variation

Parity/modulo encode organ families:

```js
s=i&1
r=i%n
```

But repeated parts should usually also depend on a continuous body field:

```js
phase=base+r*a+e*b+t*c
```

That produces siblings that are structurally related without sterile exact cloning.

### 6. Structure vs surface controls

The readable source separates semantic body-plan controls from texture/golf implementation:

```text
rootWidth
crownDepth
attachmentHeight
appendageCount
appendageLength
cavityStrength
pulseStrength
phaseLag
foldFrequency
```

The final tweet may inline/factor these after behavior is established.

### 7. Control-locality testing

A controllable system should respond predictably when one readable parameter changes.

Render the same frame before/after a 10–25% parameter perturbation, then run:

```sh
node scripts/check-control.mjs baseline.png variant.png
```

It reports:

- changed-pixel fraction
- mean/max luminance difference
- robust difference bounding box
- difference centroid

The script cannot know what a "fin" is. It provides evidence for visual inspection: a local fin-span control should not unexpectedly reorganize the whole organism.

## The v0.3 research synthesis

`references/controllable-complexity-research.md` documents the full translation. The architecture draws on several established procedural/developmental ideas without copying their literal implementations:

### Karl Sims — indirect morphology graphs

Sims' 1994 virtual-creature work uses directed genotype graphs, parent-relative attachment, reflection and repeated/recursive components so compact descriptions expand into larger creature morphologies.

v0.3 uses the same representation lesson at design time: define families once, attach them relative to parents, then compile the graph to algebra.

### L-systems — hierarchy and local frames

L-system/turtle systems demonstrate compact developmental rules, branching hierarchy and geometry expressed in a current local frame.

A literal string grammar would be too expensive for a tweet; v0.3 retains local-frame inheritance and reusable family rules.

### Wolpert — positional information

The positional-information abstraction suggests that a shared coordinate system can be interpreted differently to generate different spatial regions.

v0.3 translates this into common `e/k/d` body fields plus cheap regional selectors/envelopes.

### CPPNs — repetition with variation

Compositional Pattern Producing Networks show how compositions of simple functions over geometric coordinates can encode symmetry, repetition and repetition-with-variation.

v0.3 uses the compact analogue: discrete residue identity + continuous global/body fields.

### Skeletal implicit modeling — structure vs material

Skeletal implicit modeling separates lower-dimensional structural skeletons from the surface field built around them.

v0.3 uses this as a reasoning discipline: spine/anchor/attachment structure is distinct from folds, density and surface texture.

## Capacity model

The recommended executable form:

```text
CODE//#つぶやきProcessing
```

leaves **259 X-weighted characters for `CODE`**.

That is not enough for arbitrary conventional anatomy. It is enough for a few high-leverage rules that generate many apparent parts.

A realistic final compound sketch may have:

```text
1 sample/index system
1 root body law
1 regional selector
1 repeated organ-family law
1 shared projection
1 master clock
1 high-leverage surface deformation
```

The skill therefore measures complexity in **independent rules**, not visible part count.

If a requested body plan cannot be factorized without losing its identity, the correct action is deliberate simplification—not exceeding the tweet budget or pretending a conventional multi-object scene is authentic tiny-code morphology.

## Visual QA from v0.2 remains required

Render multiple frames and inspect density/framing:

```sh
node scripts/check-visual.mjs frame-0.png frame-90.png frame-180.png
```

Useful diagnostic bands for the dense-organic specialization remain:

- `<2%` occupancy: strong wire/sparse warning
- `2–4%`: inspect carefully
- `4–15%`: common useful territory, not a hard gate
- `>15%`: inspect for overfill/lost cavities
- dominant robust span `<55%`: often too small
- centroid offset `>15%`: inspect composition

For compound anatomy, visual review also asks:

- does root mass read before secondary organs?
- do appendages visibly originate on the body?
- does negative space reveal the body plan?
- do children remain attached through motion?
- do repeated siblings have controlled variation?

## Length verification

Write the complete post to a file and run:

```sh
node scripts/check-length.mjs post.txt
```

`#つぶやきProcessing` costs 19 weighted characters; `//#つぶやきProcessing` costs 21, leaving 259 weighted characters for code.

**280 is a ceiling, not a target.**

## Example complex prompt

```text
Create an original #つぶやきProcessing organism with a folded central shell, a bilateral fin family, four ventral tendrils, an internal cavity and slow inherited pulse motion. Treat fins/tendrils as reusable families rather than separate objects. Give the morphology plan, readable controls, rendered/control diagnostics, tweet-ready code and verified length.
```

## Design stance

### Developmental program, not tiny scene graph

The target is not `body + fin1 + fin2 + tentacle1 + ...`. The target is a small positional program whose rules unfold into body regions and organ families.

### Control before compression

Semantic parameters remain separate in readable code. Test their effects before algebraically merging constants or eliminating abstraction boundaries.

### Hierarchical motion

Children inherit root phase/pose and add local deformation. Independent clocks/absolute placement usually make a creature fall apart perceptually.

### Original systems

Research provides representation principles, not artist formulas. New sketches must invent their own morphology graph, equations, ratios, regionalization and projection.

## Research sources

Full notes and links are in `references/controllable-complexity-research.md`. Core sources include:

- Karl Sims, *Evolving Virtual Creatures* (SIGGRAPH 1994): https://www.karlsims.com/papers/siggraph94.pdf
- Przemyslaw Prusinkiewicz, *Graphical Applications of L-systems*: https://algorithmicbotany.org/papers/graphical.gi86.html
- Prusinkiewicz & Lindenmayer, *The Algorithmic Beauty of Plants*: https://algorithmicbotany.org/papers/
- Lewis Wolpert, *Positional information and the spatial pattern of cellular differentiation*: https://doi.org/10.1016/S0022-5193(69)80016-0
- Kenneth O. Stanley, *Compositional Pattern Producing Networks*: https://doi.org/10.1007/s10710-007-9028-8
- Jules Bloomenthal, *Interactive Techniques for Implicit Modeling*: https://www.bloomenthal.com/JBloom/pdf/interactive.pdf

## Next evaluation frontier

v0.3 should be benchmarked on prompts that require increasingly complex but factorable morphology:

1. bell + tendril family
2. bilateral torso + paired fins
3. root + two organ families
4. mixed 2D root + 1D appendage material
5. deliberate asymmetric variant

For each, evaluate body hierarchy, attachment through motion, control locality, expanded→golfed morphology survival, visual metrics, runtime and weighted length.