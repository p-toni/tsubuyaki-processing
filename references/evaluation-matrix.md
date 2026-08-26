# v0.4 Evaluation Matrix

The v0.3 jellyfish/bell experiment was a fair regression test for the feature it introduced, but not a fair test of general improvement. v0.4 therefore evaluates whether compound-morphology machinery activates only when it should.

Use the same cold-agent protocol across all four classes: load the skill fresh, generate readable source, render representative frames, run relevant checks, golf, and verify the final post.

## 1. Compound bell / creature — morphology should activate

Prompt shape:

> Create a creature-like bell with a differentiated crown, attached repeated appendages, a cavity, and two named controls: crown depth and appendage length.

Expected route:

- flattened 2D root mass;
- morphology contract required;
- `morphology-composition.md` loaded;
- `control-strategies.md` + `control-scopes.md` loaded;
- crown/appendage region masks rendered;
- crown control likely `region` or `subtree` depending on attachment design;
- appendage length likely `region`;
- scope-aware spill reported.

Failure signals:

- literal per-tentacle code;
- toroidal cloth with appendages pasted on;
- local controls not distinguishable by region/subtree influence;
- morphology disappears after golf.

## 2. 1D axial filament creature — legitimate 1D path

Prompt shape:

> Create a long translucent larval ribbon with one axial spine, alternating side filaments and traveling contraction waves. Keep it visibly filamentary rather than membrane-like.

Expected route:

- intentional 1D manifold;
- no forced 2D-sheet conversion merely to increase occupancy;
- morphology reference optional unless the side filaments are treated as a true attached family;
- low occupancy may be acceptable by intent;
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
- no region masks or semantic-scope testing unless the user explicitly asks for named controllable subregions;
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

- agent adds body-plan nouns because v0.3/v0.4 morphology exists;
- unnecessary control/mask overhead;
- generic toroidal cloth not challenged by body/silhouette reasoning.

# Report dimensions

For every class record:

- chosen route/topology;
- references loaded;
- number of iterations to viable form;
- occupancy / robust bbox / centroid / clipping;
- motion quality;
- whether morphology machinery was activated;
- expanded→golfed visual survival;
- raw + X-weighted length;
- final qualitative authenticity score.

For controllable compound work additionally record:

- morphology hierarchy;
- control → declared scope mapping;
- total difference energy;
- spill ratio;
- whether scope behavior is stable over at least 3 representative frames.

# Key release criterion

v0.4 is successful only if it improves **selective controllability for compound organisms without taxing simpler topologies**.

The skill should behave like a router, not like a universal morphology framework.