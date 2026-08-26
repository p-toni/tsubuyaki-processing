# tsubuyaki-processing

A production-oriented Agent Skill for authentic, tweet-sized **#つぶやきProcessing**: compact mathematical systems that render dense organic forms, emergent creatures, and controllable compound morphology.

## v0.6 — math-aware generators

The v0.5 cold test exposed a limit in image-first semantic validation: a repeated family could increase its aggregate bounding width even while several individual siblings shrank.

v0.6 moves one layer closer to the source of truth:

```text
math / latent generator → instance semantics
raster phenotype        → spatial scope
visual inspection       → aesthetic judgment
```

The core idea is simple:

> when the mathematics already contains family identity or dynamical structure, inspect that mathematics directly instead of reconstructing semantics from pixels.

## Two generation paths

### Math-first emergent form

For compact systems where organism-like structure emerges from equations:

```text
kernel → latent fields → family operator → nonlinear deformation → projection
```

Examples include:

- iterative/chaotic state with nonlinear projection;
- harmonic latent bodies with modulo-conditioned phase families;
- folded parametric systems whose apparent anatomy is emergent rather than explicitly assembled.

See `references/math-first-generators.md`.

### Morphology-first explicit anatomy

Use the existing morphology stack when the user explicitly needs named regions, attachment hierarchy, or local anatomical editing.

These paths can be combined: a math-first kernel can provide the root phenotype while a morphology layer adds only the controls that truly need explicit structure.

## What the @yuruyurau examples suggest

The useful lesson is structural, not formula copying.

One shared piece contains a Lorenz-like recurrent core with artistic parameters equivalent to:

```text
x' = 9(y-x)
y' = x(28-z)-y
z' = xy-2z
```

and then transforms that state through time/residue-dependent nonlinear projection. The visible form is therefore not a literal plot of `(x,y,z)` and not a conventional scene graph.

Another shared piece uses one bounded harmonic latent body plus a discrete `i%16` family variable. Sixteen apparent siblings come from one generator with phase-conditioned deformation.

That pattern motivates v0.6's math-first decomposition and family probes.

## Pure math probes

For a repeated family, keep a design-time pure probe alongside the readable sketch:

```js
export function sample(i,t,p){
  return {
    family:'arms',
    instance:i%5,
    x:...,
    y:...,
    latent:{radial:...,axial:...,phase:...}
  }
}
```

`templates/math-probe.mjs` shows the interface.

The probe is never part of the tweet-ready code.

## Instance-level semantic validation

A control can now use `effect.source="math-family"`:

```json
{
  "source":"math-family",
  "family":"arms",
  "field":"radial",
  "metric":"max",
  "direction":"increase",
  "variantFactor":1.2,
  "minMedianRelativeChange":0.05,
  "minAgreement":0.8,
  "maxRelativeMAD":0.15
}
```

Run:

```sh
node scripts/check-family-math.mjs \
  probe.mjs math-contract.json familyExtent --factor=1.2
```

The checker reports each sibling plus family-level:

- median relative change;
- directional agreement;
- response MAD / dispersion;
- min/max instance response.

This distinguishes a coherent family response such as:

```text
+9%, +7%, +9%, +8%, +8%
```

from an aggregate-box cheat such as:

```text
+4%, -3%, +77%, +66%, -6%
```

## Validation stack

For explicitly controllable repeated morphology:

```text
check-family-math      → did each generator instance change correctly?
check-control-scope    → did rendered change stay in allowed anatomy?
check-control-effect   → does a simple visible observable agree?
visual QA              → is the phenotype compelling?
morphology survival    → did defining structure survive golf?
```

No one layer replaces the others.

For chaotic recurrence parameters, local-family validation is usually inappropriate: small kernel perturbations may legitimately diverge globally. Prefer local controls in projection/deformation/family layers when predictable editing is desired.

## Workflow routing

- abstract dense sheet → base mathematical workflow;
- filament / axial ribbon → legitimate 1D path;
- iterative attractor → dynamical-system path;
- emergent organism from dynamics/harmonics/families → **math-first path**;
- explicit compound anatomy → morphology composition;
- repeated family with named controls → math probe + scope/effect checks when appropriate.

## Core v0.6 files

```text
references/math-first-generators.md
references/semantic-effects.md
scripts/check-family-math.mjs
templates/math-probe.mjs
templates/math-contract.json
```

Existing visual/scope/survival tools remain unchanged.

## Tweet constraint

The recommended executable form `CODE//#つぶやきProcessing` leaves **259 X-weighted characters for code**. Always verify the complete post:

```sh
node scripts/check-length.mjs post.txt
```

280 is a ceiling, not a target.

## Evaluation stance

Do not collapse math coherence, raster locality, feature survival, and aesthetics into one optimization target yet. The repository should first accumulate cold-agent evidence across:

- recurrence-driven emergent form;
- repeated harmonic family;
- explicit morphology;
- 1D filament;
- abstract dense sheet.

The desired outcome is not “more validators.” It is a better match between **the mathematical cause of the art and the way we reason about/control it**.