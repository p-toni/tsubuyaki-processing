---
name: tsubuyaki-processing
description: "Create authentic #つぶやきProcessing p5.js sketches: dense mathematical, organic, point-based animated forms compressed to a tweet-sized program. Use for Tsubuyaki Processing, tweet-sized p5.js, mathematical creature/floral forms, controllable compound organisms, or code-golfed generative art. Produce an original readable sketch plus a verified <=280-character tweet version."
---

# Tsubuyaki Processing

Create **original #つぶやきProcessing**, not generic generative art that happens to be short.

The target is a tiny p5.js program encoding a surprisingly rich dynamical system. v0.3 adds **controllable complexity**: the agent can design compound creature-like forms with differentiated regions, appendage families, symmetry, attachment and hierarchical motion, then factor that morphology into a tweet-sized indirect encoding.

## Non-negotiable constraints

1. **Tweet-sized is a hard gate.** The complete post, including the hashtag/comment marker, must be <=280 X/Twitter weighted characters and <=280 raw Unicode code points.
2. **Use p5.js global mode unless the user asks otherwise.**
3. **Generate an original system.** Learn structural devices from the references; do not reconstruct or lightly mutate a published artist's exact formula.
4. **Mathematical density beats decorative complexity.** Prefer shared fields and reusable generators over many independent effects.
5. **The final code must run.** Never sacrifice executable behavior merely to win characters.
6. **Design and verify visually before golfing.** The readable version is the source of truth.
7. **280 is a ceiling, not a target.** Do not spend spare characters unless they materially improve the piece.
8. **Complexity must be factorized.** Do not write one independent branch or draw loop per organ. Encode body regions and repeated families from shared coordinates, selectors and phase laws.
9. **Structure and appearance are separate controls.** In the readable source, body plan / attachment / region extent must be distinguishable from folds / texture / alpha / micro-detail.

## Load these references as needed

- shortening: `references/code-golf-techniques.md`
- equations/topology: `references/mathematical-patterns.md`
- controllable compound anatomy: `references/morphology-composition.md`
- semantic controls and sensitivity testing: `references/control-strategies.md`
- visual judgment: `references/style-guide.md`
- researched precedents: `references/real-examples.md`
- historical/tool context: `references/research-notes.md`
- dense-sheet scaffold: `templates/basic-skeleton.js`
- filament scaffold: `templates/filament-skeleton.js`
- compound morphology scaffold: `templates/compound-morphology.js`
- advanced sheet scaffold: `templates/advanced-parametrics.js`
- deterministic browser harness: `templates/harness.html`

## Core idea: morphology as an indirect encoding

A complex organism should contain **more apparent parts than independent formulas**.

Design a readable body plan first, then compile it:

`intent → morphology graph → shared positional fields → regional generators → attachments/repetition → unified motion → render/test → factor → golf`

The final one-liner is a compact genotype. The rendered body is the larger phenotype.

## Generation workflow

### 1. Write a morphology contract before equations

For anything more structured than a single membrane/ribbon, explicitly decide:

- **polarity / main axis** — top-bottom, head-tail, radial, bilateral
- **root mass** — bell, torso, pod, shell, tube, disk, folded sheet
- **regions** — e.g. crown / trunk / ventral zone / cavity / tail
- **organ families** — e.g. 2 fins, 4 tendrils, 6 lobes, repeated segments
- **symmetry law** — bilateral, radial, alternating, deliberately asymmetric
- **attachment law** — where each family originates on its parent
- **motion hierarchy** — what the root does and how children inherit/offset it
- **surface detail** — folds/ribs/cavities added after structure

Keep the first readable morphology to roughly **1 root + 1–2 organ families + 1 detail field**. Add more only when they can reuse an existing generator.

Do not begin with literal nouns such as “draw four tentacles.” Begin with reusable roles such as “four instances of one attached appendage field.”

### 2. Choose topology per morphological role

For dense root masses and membranes, default to a **flattened 2D manifold**:

```js
x=i%n
y=i/n
```

For filaments, tails, antennae and tendril families, a **1D manifold** is often appropriate.

For trajectory-like knots or nervous/vascular-looking systems, use **iterated state**.

A compound organism may mix topologies in the readable version. During golf, try to multiplex them through one loop/index before keeping separate loops.

A 1D manifold is intrinsically a curve. Point count alone does not turn it into tissue.

### 3. Establish shared positional fields

Before creating regions, define a common coordinate language:

- `e` — main axial / positional coordinate
- `k` — lateral / radial coordinate
- `d=mag(k,e)` or related body distance
- `c` — parent phase/orientation field
- `t` — one master clock

These are the organism's equivalent of positional information. Different regions should **interpret the same fields differently** instead of inventing unrelated coordinate systems.

For a 2D sheet, derive `k/e` from separate sample coordinates. For an axial 1D creature, derive them from one parameter only when a curve-like skeleton is intended.

### 4. Regionalize with cheap influence fields

Give each anatomical region a **selector or envelope** over shared coordinates.

Use a hard selector when a sharp regime change is useful and cheap:

```js
e<4 ? headLaw : trunkLaw
```

Use a soft envelope when regions should blend:

```js
max(0,1-abs((e-a)/r))
1/(1+((e-a)/r)**2)
```

Use periodic fields for segmentation/repeated zones:

```js
sin(e*f)
i%m
```

Design rule: a regional field should control **several related consequences** (width + fold amplitude + appendage base, for example), not merely decorate one term.

### 5. Build the root mass first

The root must work without appendages.

Use the established `k/e/d` vocabulary to produce a strong silhouette and internal material. For dense tissue, establish useful occupancy/framing before adding secondary anatomy.

If the root already looks like an undifferentiated torus/cloth, extra organs will not rescue it. Create polarity and a dominant mass hierarchy first.

### 6. Attach children in the parent's local frame

A child should be positioned **relative to its parent anatomy**, not directly with arbitrary canvas constants.

Readable local-frame form:

```js
X=Xp+u*cos(c)-v*sin(c)
Y=Yp+u*sin(c)+v*cos(c)
```

Here `(Xp,Yp)` is an anchor on the parent and `c` is the parent's local phase/orientation. The child inherits that frame, then adds its own local bend/phase.

For golf, often avoid a full matrix and instead inherit the parent's `q/c` variables:

```js
childPhase=c+offset
childRadius=q+localWarp
```

**Attachment invariant:** changing the root pose or breathing should carry attached anatomy with it. If a fin/tendril stays in absolute screen space while the body moves, the design is not structurally coupled.

### 7. Encode symmetry, repetition and repetition-with-variation

Use index structure as compressed developmental instructions:

```js
s=i&1        // bilateral side
r=i%m        // repeated organ family
p=r>>1       // family/region id when useful
```

Parity provides symmetry/alternation. Modulo provides repeated instances. But exact copies often look synthetic.

Create **repetition with variation** by letting the repeated generator also read a global field:

```js
phase=base+r*a+e*b+t*c
size=baseSize+sin(r+e)*variation
```

This keeps one generator while making each organ respond to its position in the whole body.

### 8. Compose anatomy with the cheapest correct mechanism

Choose among three composition modes:

**A. Shared deformation — cheapest and most cohesive**

Several regional envelopes contribute to one `q/c/X/Y` mapping. Best for crown/trunk/cavity/wing-like masses that remain one continuous sheet.

**B. Sample multiplexing — best for different anatomical materials**

Use index ranges/residue classes to make one loop generate root-sheet samples and appendage-curve samples. Share the same parent fields and clock.

**C. Separate generators — readable-stage fallback**

Use separate loops/functions while designing if it makes topology/attachment clear. Before golf, attempt to factor them into A or B.

Do not introduce a branch per visible appendage. One organ **family** should usually equal one generator.

### 9. Use hierarchical motion, not independent animation

Start with one slow master clock `t`.

- root phase: `c=f(d,e)-t*a`
- child phase: `c+localOffset+t*b`
- micro-detail: `sin(sharedField+t*c)`

Children inherit parent motion and add smaller local motion. Independent clocks or unrelated rigid rotations make the body look assembled rather than alive.

### 10. Expose semantic controls in readable source

Before golfing, name a small set of controls. Prefer controls with one clear visual meaning:

**Structure**
- root length / width
- region boundary or attachment position
- appendage count
- symmetry mode

**Regional geometry**
- crown depth
- fin span
- appendage length
- cavity strength
- taper

**Motion**
- pulse strength
- phase lag
- bend amplitude

**Surface**
- fold frequency
- rib amplitude

Do not reuse one readable constant for unrelated semantic effects merely because it may save characters later. First make controls intelligible; alias/factor them during golf only after behavior is proven.

### 11. Test control locality before golfing

For each important semantic knob:

1. render a baseline frame;
2. change only that knob by roughly 10–25%;
3. render the **same frame/time** again;
4. inspect where the image changed;
5. verify that the intended anatomy changed more than unrelated regions.

When available:

```sh
node scripts/check-control.mjs baseline.png variant.png
```

The script reports changed-pixel fraction and a robust difference bounding box. It is diagnostic, not a semantic oracle.

A local control such as `finSpan` should not reorganize the entire organism. A global control such as root curvature legitimately can.

If one knob has multiple unrelated effects, split the dependency in readable code or decide that the coupling is biologically/visually intentional and document it.

### 12. Tune and mechanically inspect the visual field

Typical dark-ground baseline:

- canvas: 400×400
- background: grayscale 6–12
- pale stroke alpha ~35–110
- 20k–40k root-sheet samples
- time step roughly `PI/240` to `PI/20`
- `point()` first

For a light/paper ground, use dark ink and usually lower alpha; overlap creates darker density.

Render at least 3 representative frames and run:

```sh
node scripts/check-visual.mjs frame-0.png frame-90.png frame-180.png
```

Useful diagnostics for the dense-organic target:

- `<2%` occupancy: likely wire/sparse unless intentionally filamentary
- `2–4%`: inspect carefully
- `4–15%`: common useful territory, not a rule
- `>15%`: inspect for overfill/lost cavities
- robust dominant span `<55%`: often too small
- centroid offset `>15%` of canvas on an axis: inspect composition
- edge contact: inspect clipping

For complex anatomy also inspect **hierarchy**:

- root mass reads first
- secondary organ family reads second
- tertiary folds/textures read last
- appendages visibly originate from the body
- negative space separates regions enough to reveal the body plan

### 13. Compile the morphology before ordinary code golf

First perform **representational compression**:

1. Replace individual organs with one repeated-family generator.
2. Replace absolute child coordinates with parent-relative fields.
3. Merge region-specific equations that differ only by a selector/parameter.
4. Reuse positional fields across structure and texture.
5. Fold separate loops into index ranges/residue classes when semantics permit.
6. Convert smooth readable envelopes to cheaper approximations only if the silhouette remains equivalent.
7. Remove a region whose deletion does not materially change the body plan.

Only then apply normal JavaScript golf:

- setup first-frame guard
- one-letter names
- countdown loop
- assignment expressions
- implicit globals where safe
- scientific notation / leading-zero removal
- aliases only past break-even

See `references/code-golf-techniques.md`.

### 14. Respect the morphology capacity of the tweet budget

`#つぶやきProcessing` costs 19 X-weighted characters. The recommended `CODE//#つぶやきProcessing` form leaves **259 weighted characters for `CODE`**.

That budget usually supports only a few **independent rules**, but each rule can generate many visible parts.

Prefer:

- 1 root field
- 1 repeated organ-family rule
- 1 regional/detail law
- shared clock / projection

over:

- torso formula
- left fin formula
- right fin formula
- tentacle 1 formula
- tentacle 2 formula
- separate texture formula

If the requested body plan cannot be factorized without losing its defining structure, say so and simplify the morphology deliberately. Do not pretend arbitrary anatomical complexity fits 259 characters.

### 15. Verify the hard limit

Write the complete post to a file:

```sh
node scripts/check-length.mjs post.txt
```

Do not declare success until raw and weighted limits pass. Finishing under budget is normal.

### 16. Run and compare readable vs golfed forms

Use `templates/harness.html` or another p5 runtime. Confirm:

- no syntax error / NaN cascade
- initialization occurs once
- frame rate is viable
- anatomy remains attached across motion
- region hierarchy survives compression
- semantic-control behavior was established before names/constants were inlined
- golfed output remains visually equivalent enough to readable source

## Required output format

Unless the user requests only one form, return exactly:

### Concept
One or two sentences describing the organism and dynamical behavior.

### Morphology plan
For simple single-field pieces, one short paragraph. For compound pieces, state root mass, regions, repeated families, attachment/symmetry and motion inheritance.

### Expanded p5.js
Readable, commented code with semantic controls separated from implementation.

### Tweet-ready
One line containing complete executable p5.js plus `//#つぶやきProcessing` or another valid hashtag placement.

### Verification
Report:

- raw Unicode code points
- X/Twitter weighted length
- pass/fail
- if rendered: occupancy/framing diagnostics
- for compound pieces: which semantic controls were sensitivity-tested

### Variation knobs
Give 3–5 meaningful controls. Prefer morphology/attachment/motion controls over cosmetic color changes.

## Iteration protocol

When revising a compound organism, identify **which level failed** before changing equations:

1. **material failure** — wire/confetti/flat density → change topology/distribution
2. **body-plan failure** — generic cloth/toroid → change root polarity/regions
3. **attachment failure** — floating/disconnected parts → repair local frames/inheritance
4. **hierarchy failure** — all regions equally loud → change regional envelopes/scale
5. **control failure** — one knob affects everything → separate dependencies
6. **compression failure** — anatomy disappears after golf → restore high-leverage generator, remove lower-value detail

Do not endlessly tune constants when the problem is structural.

## Authenticity and controllable-complexity test

Reject or revise if three or more are true:

- low image-space coverage for the intended material, regardless of sample count
- result is a generic flow field, starfield, spirograph, torus cloth or particle fountain
- multiple anatomical parts are placed with unrelated absolute canvas offsets
- appendages do not inherit parent motion/orientation
- each visible organ has its own independent formula instead of family reuse
- symmetry is exact duplication with no positional variation where variation would improve life-like character
- complexity exists only as micro-texture; thumbnail silhouette has no hierarchy
- changing one local semantic control reorganizes unrelated anatomy
- random/noise does most of the visual work
- motion is only rigid rotation/translation
- code was minified before the body plan was designed/tested
- final post exceeds the budget

A strong v0.3 result should feel like a **small developmental program**: a few positional rules unfold into a coherent organism with identifiable regions, repeated anatomy, attachment and internal motion.