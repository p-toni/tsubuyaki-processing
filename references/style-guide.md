# Style Guide: Authentic Dense Organic #つぶやきProcessing

This guide narrows a broad historical practice to the requested contemporary mathematical-organic point aesthetic.

## 1. Core aesthetic

The image should look as though a continuous living structure was discovered inside a short equation.

Desired qualities:

- dense but legible
- mathematical but not diagrammatic
- organic without literal illustration
- mostly deterministic rather than random
- smoothly animated rather than noisy
- rich at both silhouette and micro-detail scales
- visually surprising relative to source length

A useful phrase is **apparent animacy**: geometry should seem to breathe, flex, unfurl, contract, or reorganize itself even though the code contains no anatomy.

## 2. Point density is the material

`point()` is not merely a cheap primitive. Thousands of overlapping samples create a luminous density field.

Default target:

- 10k–40k samples/frame
- one or two pixels of effective mark size
- pale stroke with moderate alpha
- nearly black ground

The points should merge perceptually into membranes, ribs, threads, and surfaces.

If individual points dominate at normal viewing size, either increase density or make the point size less visually explicit.

## 3. Monochrome first

Start with grayscale:

- background: 6–12
- stroke: white-ish, alpha 35–110

Why:

- every character contributes to geometry, not palette plumbing
- overlapping alpha naturally creates shading
- shape quality is easier to judge without color
- monochrome is strongly represented in contemporary high-density works

Only add color if it encodes a structural variable or the user explicitly asks for it.

## 4. Canvas

Default: **400×400**.

Reasons:

- widely seen in contemporary p5.js examples
- cheap square assignment: `createCanvas(w=400,w)`
- center is a convenient ~200
- `w` can be reused as an over-range white channel
- enough resolution for dense 1px points

Other valid historical/community sizes include 500, 540, 600, 720, 800, 900 and beyond. Choose another size only when visual/output requirements justify the extra source cost.

## 5. Silhouette hierarchy

At thumbnail scale, the work should have one dominant silhouette:

- bell
- pod
- shell
- folded disk
- larval ribbon
- bilateral mask
- blossom/tube
- knot

At full size, secondary structure should emerge:

- ribs
- pleats
- repeated lobes
- cavities
- tendrils
- density bands

At zoom, tertiary point texture should be visible.

If there is no hierarchy—only uniform noise—the formula is not doing enough compositional work.

## 6. Symmetry

Use symmetry as scaffolding, not as the final effect.

Good:

- bilateral body with phase-shifted sides
- radial base with nonuniform axial drift
- repeated lobes whose deformation depends on body position

Weak:

- perfect mandala rotating as one rigid object
- obvious kaleidoscope with no local variation

A tiny parity or modulo term often provides enough disagreement to make a symmetric body feel alive.

## 7. Motion

Preferred motion is **internal**:

- phase fields drift
- fold spacing changes
- body radius pulses
- lobes exchange prominence
- a singular feature migrates
- surface density breathes

Avoid motion that is only:

- whole-object spin
- whole-object translation
- random jitter

### Speed

Use a slow master clock. Common observed increments span roughly `PI/240` to `PI/20`; slower is often more convincing for organic work. Local phase multipliers can create faster micro-motion without making the whole object frantic.

The animation should reveal structure over several seconds, not exhaust its idea in half a second.

## 8. Mathematical reuse

The most authentic equations reuse latent quantities:

- `d` shapes both projection and deformation
- `e` controls axial placement and wrinkle phase
- `k` controls both lateral radius and tendril strength
- `t` enters multiple phases at different rates

This creates causal unity.

Anti-pattern: every term has its own unrelated `sin(i*randomConstant+t*randomConstant)`. That can look busy but not organism-like.

## 9. Controlled singularities

Terms like `1/k`, `1/d`, `tan(...)`, or extreme powers are welcome when they create a stable anatomical feature.

Desired:

- one thin spine
- a flare/tendril near the core
- a cusp at a lobe boundary
- a sudden but bounded frill

Undesired:

- most points shooting off-screen
- flickering NaN gaps
- shape disappearing when a denominator crosses zero

Tune singularities visually in motion, not only on one frame.

## 10. Density/shading

Translucent points act like a cheap volumetric shader:

- more overlapping samples → brighter ridges
- sparse regions → dark cavities
- moving manifolds → changing highlights

Do not add explicit shadow/highlight code until the density field itself has been exploited.

## 11. Randomness and noise

Historical #つぶやきProcessing includes plenty of random/noise work, but the requested target style is more formula-driven.

Use randomness/noise only when it adds a specific behavior:

- slight imperfection
- birth/death variation
- perturbation of a coherent field

Do not let `noise()` replace the mathematical body design.

## 12. Primitive hierarchy

Preferred for this specialization:

1. `point()` — default
2. `circle()` — when diameter/density is a meaningful variable
3. `line()` — for filament/ribbon systems
4. WEBGL primitives — valid, but a different lineage and often more character-expensive

Do not use many primitive types in one tiny work; it usually signals conventional scene construction rather than compressed field design.

## 13. Performance

High point counts are normal, but every extra nested trig call is paid 10k–40k times per frame.

Performance tactics that also help code size:

- reuse assigned subexpressions
- avoid callback-heavy `.map()` in the hottest loop unless it saves enough code and runs acceptably
- prefer one loop to nested loops
- avoid allocating arrays/objects per sample
- keep expensive randomness/noise out of the inner loop unless essential

A beautiful 40k-point equation that renders at 3 FPS is not production-ready animation.

## 14. Originality boundary

This skill is informed by a community vocabulary and by analysis of artists such as @yuruyurau. It should **not** produce a near-duplicate of a cited work.

Do:

- reuse abstract devices such as latent radial coordinates, dense point sampling, nested phase coupling, or modulo anatomy
- invent new equations and ratios
- change sampling topology and projection

Do not:

- copy a published one-liner and swap constants
- preserve the same formula skeleton with token substitutions
- claim a generated piece is by or endorsed by a real artist

## 15. Final visual checklist

Before golfing, ask:

- Does it have a strong silhouette at 25% scale?
- Do dense points resolve into a surface rather than confetti?
- Is there at least one macro, meso, and micro structure?
- Does motion deform the system internally?
- Are most visual effects consequences of shared latent variables?
- Is randomness secondary or absent?
- Would removing one term noticeably simplify the organism?
- Does it still look compelling in monochrome?

If yes, it is ready for compression.
