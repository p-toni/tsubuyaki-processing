# Real Example Study Set

This file records **structural observations from real published #つぶやきProcessing works**. To respect creators and keep this skill generative rather than imitative, it does not reproduce complete third-party programs. Each entry gives a short identifying fragment, source, and the pattern worth learning.

## Reading key

- **Domain** — how points/geometry are sampled
- **Body** — latent coordinate construction
- **Projection** — how latent geometry becomes screen coordinates
- **Time** — animation clock behavior
- **Golf** — notable compression technique

---

## 1. @yuruyurau — widely circulated organic axial body (2025)

Source: https://x.com/yuruyurau/status/1933629116575855091

Short fragment: `d=mag(k=(4+sin(...))*cos(...),e=y/8-13)`

Observed pattern:

- **Domain:** 10k samples.
- **Body:** lateral oscillation `k` plus a linear axial coordinate `e`; `mag(k,e)` becomes the body radius.
- **Projection:** local displacement `q` is wrapped around a phase `c`, then the radius is also used as an axial offset.
- **Time:** very slow global step around `PI/240` with faster local harmonics.
- **Visual:** striking biological silhouette with frills/tendrils despite no explicit anatomy.
- **Golf:** helper default parameter computes and exposes latent variables; `q`/`c` assignments occur inside `point()`.

Lesson: the same `k/e/d` triplet governs silhouette, surface detail, and motion. This causal reuse is more important than any literal formula.

## 2. @yuruyurau — current 400px / 10k / `PI/240` work (Aug 2026)

Source feed: https://x.com/TweetProcessing

Short fragment: `background(9).stroke(w,66)`

Observed pattern:

- **Domain:** 10k 1D samples.
- **Body:** `k=5*cos(y*9)`, long axial `e`, radial `d`.
- **Projection:** one compact phase drives a wide horizontal body and folded vertical detail.
- **Time:** `PI/240`, plus a much faster `t*9` term locally.
- **Visual:** pale filament membrane on near-black.

Lesson: global motion can be extremely slow while one localized term moves much faster.

## 3. @yuruyurau — breathing distance offset variant (Aug 2026)

Source feed: https://x.com/TweetProcessing

Short fragment: `+sin(t)**4`

Observed pattern:

- **Domain:** 10k.
- **Body:** similar latent-coordinate strategy, but the radial distance includes a nonnegative breathing envelope.
- **Projection:** folds contain a reciprocal `1/d` term and a cubic radial term.
- **Time:** slow master phase.

Lesson: an even sine power is a tiny way to make the body inhale/exhale without reversing deformation sign.

## 4. @yuruyurau — high-nonlinearity 10k work (Aug 2026)

Source mirror/example: https://www.twstalker.com/pvncher

Short fragment: `mag(... )**3/1999`

Observed pattern:

- **Domain:** 10k samples partitioned by modulo.
- **Body:** product of several trig factors before cubing the latent distance.
- **Projection:** exponentiation with a sinusoidal exponent contributes sharp scale changes.
- **Time:** much faster master step around `PI/20` but divided heavily inside phases.

Lesson: master time increment alone does not determine perceived speed; downstream division/multiplication is the real temporal architecture.

## 5. @yuruyurau — 20k cubed-distance organism (2026)

Source mirror: https://mobile.twstalker.com/_brodz_

Short fragment: `mag(k=8*cos(y),e=y/8-12)**3/999+1`

Observed pattern:

- **Domain:** 20k.
- **Body:** extremely simple `k/e`, with complexity deferred to nonlinear distance and projection.
- **Projection:** `k/d` creates a controlled core singularity; parity shifts the phase.
- **Time:** around `PI/45`.

Lesson: keep the base body equation simple and spend complexity on one high-leverage deformation.

## 6. @yuruyurau — modulo-segmented 20k body (2025/26)

Source mirror: https://mobile.twstalker.com/charlesnuss

Short fragment: `i%5` and `i&1`

Observed pattern:

- **Domain:** 20k with multiple discrete families.
- **Body:** distance normalized by a modulo-dependent denominator.
- **Projection:** parity and five-way phase offsets create repeated anatomical segments.
- **Golf:** bitwise parity and modulo replace explicit branches/arrays.

Lesson: index residue classes can function as a tiny skeletal topology.

## 7. @yuruyurau — 20k flattened surface / folded radial form (older)

Source mirror: https://www6.twstalker.com/professor_arc

Short fragment: `a(i%100,i/100)`

Observed pattern:

- **Domain:** flattened 2D sheet from one loop.
- **Body:** `x` and continuous `y` become latent cross-section/axis.
- **Projection:** trigonometric radius plus `tan(1/k)` singular detail.
- **Time:** around `PI/90`.

Lesson: `i%n,i/n` is a compact way to sample a true sheet, and fractional quotient can be visually useful without flooring.

## 8. @yuruyurau — 40k dense sheet family

Source/examples are redistributed through the official hashtag bot: https://x.com/TweetProcessing

Short fragment: `for(...i=4e4;i--;)`

Observed pattern:

- **Domain:** 40k points.
- **Body:** two independent sample coordinates enter `cos`/`sin` and `abs`-based deformation.
- **Visual:** high-density sheets with rib-like interference.

Lesson: 40k points is not excessive by community standards when the inner formula is compact and allocation-free.

## 9. @yuruyurau — 30k folded surface family

Source/examples via community mirrors and hashtag feed: https://x.com/TweetProcessing

Short fragment: `i=3e4`

Observed pattern:

- **Domain:** 30k.
- **Body:** latent distance from `x/4`-like and `y/9`-like coordinates.
- **Projection:** radius/angle reuse builds a folded toroidal or shell-like surface.

Lesson: sample count and alpha are coupled design parameters—denser sheets often need lower opacity.

## 10. @yuruyurau — circle instead of point variant

Source feed/archive: https://x.com/TweetProcessing

Short fragment: `noStroke();fill(w,116);circle(...)`

Observed pattern:

- **Domain:** around 10k.
- **Primitive:** tiny circles with diameter switching between small values.
- **Visual:** stippled tissue rather than hairline dust.

Lesson: `circle()` is justified when mark size itself contributes to the material; otherwise `point()` is cheaper and cleaner.

## 11. @yuruyurau — vector-growth / accumulating particle family (2022)

Expanded-study source: https://qiita.com/youtoy/items/263f407021c4b3003365

Short fragment: `$=[]` and `background(0,9)`

Observed pattern:

- **Domain:** persistent vector state rather than independent samples.
- **Motion:** particles are updated and replenished; translucent background preserves trails.
- **Visual:** branching/growth behavior instead of an instantaneous manifold.

Lesson: contemporary-looking organicity is possible through stateful growth too; dense parametric fields are dominant in the requested style, not mandatory.

## 12. @yuruyurau — Lorenz-like 30k iterative work (2026)

Source mirror: https://www.twstalker.com/anotherpixelon

Short fragment: `[x,y,z]=[...]`

Observed pattern:

- **Domain:** 30k integration steps in one frame.
- **Body:** three coupled state variables with a tiny integration constant.
- **Projection:** the attractor state is wrapped through another oscillatory phase before plotting.
- **Golf:** destructuring preserves simultaneous-update semantics compactly.

Lesson: a famous dynamical-system *type* can be transformed into new visual geometry by treating the trajectory as latent material rather than drawing a textbook attractor directly.

## 13. @yuruyurau — late 2025 multi-regime body

Secondary breakdown/source citation: https://bestiariotopologico.blogspot.com/2026/

Short fragment: `i<2e4?...:...`

Observed pattern:

- **Domain:** 30k samples split into regimes.
- **Body:** a ternary uses different latent equations for different sample ranges.
- **Projection:** one phase unifies the regimes into a single form.

Lesson: a tiny piece can contain multiple anatomical systems if they share projection/time variables.

## 14. Hau-kun — early animated noise grid (Oct 2019)

Source: https://haukun.projectroom.jp/archives/362

Short fragment: `noise(i%30/10.0+t,...)`

Observed pattern:

- **Canvas:** 720×720.
- **Domain:** regular grid.
- **Visual:** noise-driven tiles rather than point-organic tissue.
- **Historical value:** demonstrates that early #つぶやきProcessing was visually diverse.

Lesson: authenticity is broader than one modern style; this skill specializes by design rather than claiming exclusivity.

## 15. Hau-kun — early 3D/tunnel lineage (2019)

Source/tag archive: https://haukun.projectroom.jp/archives/tag/%E3%81%A4%E3%81%B6%E3%82%84%E3%81%8Dprocessing

Short fragment: `size(720,720)`

Observed pattern:

- **Renderer:** Java Processing / 3D experiments.
- **Domain:** repeated angular/depth geometry.
- **Visual:** tunnel/space structures.

Lesson: repeated transforms and geometric depth are another authentic lineage, but less central to the requested p5 point-organic specialization.

## 16. WGG — additive repeated-circle field (2020)

Source: https://wgg.hatenablog.jp/entry/20200524/1590315560

Short fragment: `blendMode(ADD)`

Observed pattern:

- **State:** list of moving elements.
- **Visual:** repeated translucent circles accumulate light.
- **Golf:** aliases, packed initialization, and loop/body compression.

Lesson: rendering mode can create complexity “for free,” but point-density shading is more portable and usually cheaper for this skill's target.

## 17. Koma Tebe — golfed 3D ring of boxes (2022)

Source: https://medium.com/@koma.tebe/compressing-the-tiny-code-fceba1b3eb56

Short fragment: `f++||createCanvas(W=400,W,WEBGL)`

Observed pattern:

- **Geometry:** repeated boxes around an angular ring.
- **Golf:** first-frame guard, dimension reuse, aliases/short calls, scientific notation, expression side effects, renderer-specific hacks.

Lesson: the article is more valuable as a compression case study than as a visual template for this skill.

## 18. Gorilla Sun — combined p5.js golf example (2022)

Source: https://www.gorillasun.de/blog/9-tips-for-tsubuyaki-processing/

Short fragment: `for(f++||createCanvas(...),...;...;...)`

Observed pattern:

- **Golf:** uses all `for` clauses, arrow function, assignment expressions, and short state names.
- **Visual:** grid/circle animation rather than the modern organic point body.

Lesson: JavaScript expression semantics are a reusable compression toolkit independent of visual style.

## 19. Snowman-s — Processing/Java compression study (2020)

Source: https://qiita.com/Snowman-s/items/f405526a040e0729a5d7

Short fragment: `stroke(-1)`

Observed pattern:

- **Mode:** Processing Java rather than p5.js.
- **Golf:** merged declarations, custom frame counter, compact white literal, assignment expressions.

Lesson: language mode changes the optimal golf vocabulary; do not blindly apply Java tricks to p5.js or vice versa.

## 20. Watabo-shi / Kani — p5.js WEBGL practice (2021)

Source: https://note.com/aq_kani/n/nc25b1f26ba7d

Short fragment: `draw=_=>{t++||(...` 

Observed pattern:

- **Mode:** p5.js, including WEBGL.
- **Golf:** implicit globals, aliases for rotations/push/pop, compact nested loops.

Lesson: aliases become worthwhile when long transform functions repeat many times; in point-formula work, assignments inside the equation are usually higher leverage.

---

# Cross-example synthesis

Across the 20-study set, the target style's strongest recurring features are:

1. **A tiny number of latent variables control many visible effects.**
2. **Point count is high enough that geometry becomes material/shading.**
3. **Time is slow globally and heterogeneous locally.**
4. **`mag`, nested trig, powers, reciprocal terms, modulo and assignment expressions are unusually productive.**
5. **400×400 + near-black + translucent pale points is a powerful contemporary baseline, not a hard rule.**
6. **Golf happens at the representation level first.** The best code is not merely whitespace-stripped readable p5.
7. **Originality comes from changing the latent system and projection**, not from changing constants in someone else's one-liner.
