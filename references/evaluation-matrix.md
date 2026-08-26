# v0.5 Evaluation Matrix

Use the same cold-agent protocol across all four classes: load the skill fresh, generate readable source, render representative frames, run relevant checks, golf, and verify the final post.

v0.5 adds a new requirement for explicitly controllable compound work: **scope correctness and effect correctness must be tested separately**.

## 1. Compound creature — morphology + semantic validation should activate

Prompt shape:

> Create a creature with a differentiated root mass, an attached repeated organ family, a cavity or split, and at least two named controls affecting different anatomical levels.

Expected route:

- flattened 2D root mass when membrane/tissue-like;
- morphology contract required;
- morphology + control scope + semantic effect references loaded;
- baseline + variant region masks rendered at identical frames;
- geometry controls validated with dual-state mask union;
- simple effect descriptors attached where the requested semantic change has a measurable observable;
- defining positive anatomy and intentional voids declared as survival features;
- expanded and golfed **state-specific feature masks** rendered;
- scope, effect and survival reported independently.

### Required positive control test

Example:

```text
finSpan +20%
expected scope: fins
expected effect: fin mask width increases materially
```

It should pass both locality and effect checks.

### Required wrong-effect adversary

Construct a variant that stays inside the same allowed region but changes the **wrong observable**.

Example:

```text
finSpan variant changes fin height but not width
```

Expected result:

- scope spill remains low;
- semantic effect check fails.

This proves the effect layer contributes information beyond scope locality.

### Required smeared adversary

Construct a variant that produces the correct local effect **plus** an unrelated change elsewhere.

Expected result:

- effect may pass;
- scope spill should worsen materially.

This proves scope and effect are orthogonal.

Failure signals:

- literal per-organ code;
- generic toroidal cloth with appended parts;
- static-mask validation penalizes moved anatomy;
- wrong-effect adversary passes semantic effect validation;
- smeared adversary scores like a selective control;
- defining morphology disappears after golf but state-aware survival does not reveal it;
- masks are broadened merely to improve metrics.

## 2. 1D axial filament creature — legitimate 1D path

Prompt shape:

> Create a long translucent larval ribbon with one axial spine, alternating side filaments and traveling contraction waves. Keep it visibly filamentary rather than membrane-like.

Expected route:

- intentional 1D manifold;
- no forced 2D conversion because of occupancy heuristics;
- morphology/control machinery optional unless explicitly requested;
- low occupancy acceptable by intent;
- authenticity judged by folding, hierarchy and motion.

Failure signals:

- 2D forced solely to increase occupancy;
- compound-control contracts become boilerplate;
- generic spirograph/static Lissajous result.

## 3. Coupled / iterative attractor — morphology should mostly stay out

Prompt shape:

> Create an original coupled iterative system that reads like a living knot or vascular attractor. Do not make it resemble a named animal.

Expected route:

- iterated state selected early;
- mathematical/style guidance sufficient;
- no morphology contract by default;
- no scope/effect/survival tooling unless explicitly requested;
- visual QA + length verification remain required.

Failure signals:

- invented anatomy without request;
- morphology graph becomes mandatory;
- attractor forced into a 2D sheet.

## 4. Abstract dense sheet — essentially v0.2 path

Prompt shape:

> Create a dense abstract folded membrane with cavities and slow internal phase drift. It should feel organic but not creature-like.

Expected route:

- flattened 2D default;
- shared latent fields/density shading;
- no anatomy contract;
- no semantic-control overhead;
- visual occupancy/framing across multiple frames;
- golf only after visual stability.

Failure signals:

- unnecessary body-plan nouns/contracts;
- control/mask overhead appears without request;
- generic toroidal cloth is accepted without silhouette reasoning.

# Report dimensions

For every class record:

- chosen route/topology;
- references loaded;
- iterations to viable form;
- occupancy / bbox / centroid / clipping;
- motion quality;
- morphology machinery activation;
- raw + X-weighted length;
- qualitative authenticity.

For compound work additionally record:

- state-aware expanded→golfed feature geometry;
- feature area/width/height ratios;
- normalized centroid shift;
- presence-feature appearance retention;
- intentional-void fill behavior;
- deliberate simplifications made to meet tweet budget.

For controllable compound work additionally record:

- hierarchy and control scopes;
- effect descriptor per machine-testable control;
- dual-state spill across at least 3 frames;
- effect metric baseline/variant/delta and pass/fail;
- wrong-effect adversarial result;
- smeared-control adversarial result.

# Key release criterion

v0.5 succeeds only if it can distinguish:

```text
correct place + correct effect
correct place + wrong effect
correct effect + wrong place
```

while state-aware survival distinguishes **feature moved** from **feature disappeared**, and simpler topologies remain unburdened.

The skill is a router plus falsification stack, not a universal scalar optimizer.