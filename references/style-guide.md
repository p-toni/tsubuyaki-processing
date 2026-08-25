# Style Guide: Authentic Dense Organic #つぶやきProcessing

This guide narrows the broad historical practice to the contemporary mathematical-organic point aesthetic targeted by this skill.

## 1. Core aesthetic

The image should look as though a continuous living structure was discovered inside a short equation.

Desired qualities:

- dense but legible
- mathematical but not diagrammatic
- organic without literal illustration
- mostly deterministic rather than random
- smoothly animated rather than noisy
- strong silhouette plus local structure
- visually surprising relative to source length

A useful phrase is **apparent animacy**: geometry seems to breathe, flex, unfurl, contract, or reorganize itself even though the code contains no anatomy.

## 2. Topology determines material

For dense membranes, folded tissue, cavities and sheets, prefer a **flattened 2D manifold** as the starting point.

A 1D manifold naturally draws a curve. It is excellent for ribbons, axial organisms and filamentary bodies, but high sample count alone does not make it surface-like. If a 1D result reads as a visible wire, change topology or deliberately decorrelate adjacent samples before tuning more constants.

Iterated systems are a third lineage: a dense body can emerge from one long trajectory.

## 3. Point count is not density

`point()` is the material, but sample count only tells you how many marks were attempted. It does not tell you how much image space they occupy.

Typical ranges:

- flattened 2D: 20k–40k points/frame
- 1D/iterative: often 10k–30k
- one or two pixels effective mark size

Twenty thousand samples can still collapse into a 1% wire. Judge **image-space coverage and overlap**, not count alone.

When screenshots are available, run `scripts/check-visual.mjs` and interpret occupancy diagnostically:

- `<2%`: likely wire/sparse unless that is intentional
- `2–4%`: inspect carefully
- `4–15%`: common useful range for this specialization
- `>15%`: valid, but inspect for overfill and disappearing cavities

These are heuristics, not universal aesthetic gates.

## 4. Dark ground baseline

The most common default for this specialization:

- background: grayscale 6–12
- stroke: pale gray/white, alpha roughly 35–110

Overlap naturally produces brighter ridges and darker cavities. Start monochrome because geometry is easier to judge without palette plumbing.

## 5. Light / paper ground

Light ground is equally valid when the surrounding product/site requires it.

Use:

- the actual paper/background tone
- dark ink instead of pale points
- usually lower alpha than the dark-ground equivalent

The compositing logic inverts: overlap becomes **darker**, not brighter. Do not use an absolute brightness threshold to judge density. `check-visual.mjs` estimates the background and measures contrast relative to it so both regimes can be inspected with the same tool.

On very warm/off-white paper, tune ink color structurally only if the extra source cost is justified; otherwise grayscale/dark neutral remains the golf-friendly baseline.

## 6. Canvas and framing

Default canvas: **400×400**.

A good formula can still be badly composed. Projection offsets, reciprocal terms and axial drift can move the visible centroid away from the mathematical center.

For the usual single-organism composition:

- dominant robust span often works around 55–85% of the canvas
- visible centroid usually stays within ~10–15% of canvas center on each axis
- avoid meaningful clipping unless it is intentional

Do not turn these into hard rules. Tall, narrow, asymmetric and negative-space-heavy compositions can be excellent.

When measuring, prefer a **robust bounding box** (for example central 98% of visible pixels) over raw min/max, because one singular runaway point should not define the framing.

## 7. Silhouette hierarchy

At thumbnail scale: one dominant silhouette.

At normal size: secondary ribs, pleats, lobes, cavities, tendrils or density bands.

At zoom: tertiary point texture.

If there is no hierarchy—only uniform noise—the formula is not doing enough compositional work.

## 8. Symmetry

Use symmetry as scaffolding, not the final effect.

Good:

- bilateral body with phase-shifted sides
- radial base with nonuniform axial drift
- repeated lobes whose deformation depends on body position

Weak:

- perfect mandala rotating rigidly
- obvious kaleidoscope with no local variation

Parity/modulo provides anatomy cheaply. It does **not** solve a density/topology problem by itself.

## 9. Motion

Preferred motion is internal:

- phase fields drift
- fold spacing changes
- body radius pulses
- lobes exchange prominence
- singular features migrate
- density breathes

Avoid motion that is only whole-object spin, translation or random jitter.

Common master increments range roughly `PI/240` to `PI/20`. Slower is often more convincing for organic work; local multipliers can produce faster micro-motion.

Inspect several separated frames, not just the first attractive still.

## 10. Mathematical reuse

The most authentic equations reuse latent quantities:

- `d` shapes projection and deformation
- `e` controls placement and wrinkle phase
- `k` controls radius and singular anatomy
- `t` enters several phases at different rates

This creates causal unity.

Anti-pattern: every visible detail has its own unrelated `sin(i*constant+t*constant)`.

## 11. Controlled singularities

Terms like `1/k`, `1/d`, `tan(...)`, or extreme powers are welcome when they create stable anatomical features.

Desired: one spine, cusp, flare, tendril or frill.

Undesired: most points off-screen, flickering `NaN` gaps, or framing dominated by rare runaway samples.

## 12. Density as shading

Translucent points form a cheap volumetric shader:

- more overlap → stronger contrast
- sparse regions → cavities
- changing overlap → apparent illumination/motion

Exploit this before adding explicit shadow/highlight code.

## 13. Randomness and noise

Historical #つぶやきProcessing includes random/noise work, but this specialization is formula-driven.

Randomness may add slight imperfection or perturbation. It should not replace the mathematical body.

## 14. Primitive hierarchy

Preferred:

1. `point()`
2. `circle()` when mark diameter is meaningful
3. `line()` for explicitly filamentary systems
4. WEBGL primitives for a different lineage

Many primitive types in one tiny work usually signal conventional scene construction rather than compressed field design.

## 15. Performance

High point counts are normal, but every nested trig call is paid thousands of times per frame.

- reuse assigned subexpressions
- avoid allocations in the hot loop
- prefer one flattened loop
- keep noise/random out of the inner loop unless essential

A beautiful equation at 3 FPS is not production-ready animation.

## 16. Originality boundary

Do:

- reuse abstract devices such as dense sampling, latent radial coordinates, nested phase coupling and modulo anatomy
- invent new equations and ratios
- change topology and projection

Do not:

- copy a published one-liner and swap constants
- preserve the same formula skeleton with token substitutions
- claim generated work is by or endorsed by a real artist

## 17. Visual verification checklist

Before golfing:

- Does it have a strong silhouette at 25% scale?
- Does the intended material read correctly: sheet, filament or trajectory?
- Do points resolve into structure rather than confetti?
- Is there macro, meso and micro organization?
- Does the form occupy the canvas intentionally?
- Is the centroid/framing stable across representative frames?
- Are important features clipped?
- Does motion deform internally?
- Are effects consequences of shared latent variables?
- Would removing one term materially simplify the organism?

If screenshots are available, use the mechanical diagnostics as evidence alongside visual judgment. **The metrics support taste; they do not replace it.**