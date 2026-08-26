# v0.4.1 Evaluation Matrix

The v0.3 jellyfish/bell experiment was a fair regression test for the feature it introduced, but not a fair test of general improvement. v0.4/v0.4.1 therefore evaluate whether compound-morphology machinery activates only when it should, whether semantic controls stay inside their intended moving scope, and whether defining morphology survives code golf.

Use the same cold-agent protocol across all four classes: load the skill fresh, generate readable source, render representative frames, run relevant checks, golf, and verify the final post.

## 1. Compound creature — morphology + scope validation should activate

Prompt shape:

> Create a creature with a differentiated root mass, an attached repeated organ family, a cavity or split, and at least two named controls affecting different anatomical levels.

Expected route:

- flattened 2D root mass when membrane/tissue-like;
- morphology contract required;
- `morphology-composition.md` loaded;
- `control-strategies.md` + `control-scopes.md` loaded;
- baseline + variant region masks rendered at identical frames;
- geometry controls validated with dual-state mask union;
- parent geometry control likely `subtree`;
- organ-local length/span control likely `region`;
- defining positive anatomy and intentional voids declared as `survivalFeatures`;
- scope spill + morphology survival reported.

Failure signals:

- literal per-organ code;
- toroidal cloth with appendages pasted on;
- static-mask validation falsely penalizes moved anatomy;
- a deliberately smeared control scores similarly to a selective one;
- morphology disappears after golf while occupancy/bbox still look healthy;
- survival features are gamed with overbroad masks.

## 2. 1D axial filament creature — legitimate 1D path

Prompt shape:

> Create a long translucent larval ribbon with one axial spine, alternating side filaments and traveling contraction waves. Keep it visibly filamentary rather than membrane-like.

Expected route:

- intentional 1D manifold;
- no forced 2D-sheet conversion merely to increase occupancy;
- morphology reference optional unless the side filaments are treated as a true attached family;
- low occupancy may be acceptable by intent;
- no region-mask/control-survival overhead unless explicit controllable subregions are requested;
- authenticity judged by folding/decorrelation, hierarchy and motion rather than tissue density.

Failure signals:

- agent switches to 2D because `<2%` occupancy is treated as a hard gate;
- compound morphology machinery overwhelms a simple axial system;
- generic spirograph or static Lissajous rotation.

## 3. Coupled / iterative attractor — morphology should mostly stay out

Prompt shape:

> Create an original coupled iterative system that reads like a living knot or vascular attractor. Do not make it resemble a named animal.

Expected route:

- iterated state selected early;
- `mathematical-patterns.md` + style guidance sufficient;
- no morphology contract by default;
- no region masks or semantic-scope testing unless explicitly requested;
- visual QA + length verification still apply.

Failure signals:

- agent invents crown/appendage anatomy without request;
- morphology graph becomes mandatory boilerplate;
- attractor is forced into a 2D sheet.

## 4. Abstract dense sheet — essentially v0.2 path

Prompt shape:

> Create a dense abstract folded membrane with cavities and slow internal phase drift. It should feel organic but not creature-like.

Expected route:

- flattened 2D default;
- shared latent fields / density shading;
- no anatomy contract;
- no control scopes unless explicit controls requested;
- check visual occupancy/framing across several frames;
- golf after visual stability.

Failure signals:

- agent adds body-plan nouns because morphology tooling exists;
- unnecessary control/mask overhead;
- generic toroidal cloth not challenged by silhouette reasoning.

# Report dimensions

For every class record:

- chosen route/topology;
- references loaded;
- number of iterations to viable form;
- occupancy / robust bbox / centroid / clipping;
- motion quality;
- whether morphology machinery was activated;
- raw + X-weighted length;
- final qualitative authenticity score.

For compound work also record:

- expanded→golfed defining-feature survival;
- positive-region energy retention;
- intentional-void fill delta;
- which morphology features were intentionally simplified to meet the tweet budget.

For controllable compound work additionally record:

- morphology hierarchy;
- control → declared scope mapping;
- baseline and variant region-mask support sizes;
- total difference energy;
- dual-state spill ratio;
- spill stability over at least 3 representative frames;
- one adversarial smeared-control case that should score worse than the intended selective control.

# Key release criterion

v0.4.1 is successful only if it improves **selective controllability for moving compound anatomy, detects morphology loss during golf, and does not tax simpler topologies**.

The skill should behave like a router, not like a universal morphology framework.