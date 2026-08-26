# tsubuyaki-processing

A production-oriented Agent Skill for authentic, tweet-sized **#つぶやきProcessing**: compact mathematical systems whose animated phenotype is disproportionately richer than the source.

## v0.8 direction — discovery, not just formula invention

The completed frozen search-lab experiment changed the project’s default approach.

The question is no longer only:

> can the model invent a better formula?

It is now:

> can the system establish a strong mathematical incumbent, search the right degrees of freedom for that representation, preserve the elite, and select a genuinely better phenotype without Goodharting novelty?

The working pipeline is:

```text
intent
→ compact representation
→ viable incumbent
→ brief invariants
→ route-aware search
→ elite preservation
→ aesthetic + temporal selection
→ semantic checks where relevant
→ golf winner
→ exact verification
```

## Evidence behind the change

The completed `experiments/search-lab/full-results.md` run used the frozen v0.6 grammar:

```text
4 briefs × 10 seeds × (1 fixed incumbent + 24 parameter mutations + 24 structural+parameter mutations)
= 1,960 raw candidates
```

After blind review, structural+parameter search was strongly productive for recurrent systems and dense sheets, conditionally useful for repeated plankton families, and actively harmful as a broad default for intentional 1D filaments.

Most importantly:

> **route interaction dominated the result.**

A single universal mutation policy is the wrong architecture.

## Current route-aware policy

### Repeated math family

Use structural + parameter exploration, but preserve the requested family niche.

Useful degrees of freedom:

- family count / phase spacing;
- latent harmonics;
- distance power;
- deformation operator;
- selected projection changes;
- time coupling.

Do not let novelty turn “multiple distinct bodies” into an unrelated connected fan/colony and call it a win.

### Recurrence / living knot

Use structural divergent search.

Explore recurrence roles, residue/family structure, deformation and projection. The recurrent state is latent material rather than a textbook attractor plot.

### Dense 2D sheet

Actively explore projection/deformation family. The frozen experiment repeatedly found high-value disconnected niches through structural projection changes.

### Intentional 1D filament / ribbon

Preserve the incumbent and search locally first.

Broad topology/projection mutation produced much more behavioral diversity but substantially worse discovery for this route.

### Morphology-first explicit anatomy

Search conservatively. The current experiment did not establish a broad structural-search policy for explicit body plans, so preserve morphology and explore validated controls/family/motion parameters until dedicated evidence says otherwise.

## Elitism is mandatory

A practical search loop should never discard a good current solution simply because it decided to search.

Every search round includes the incumbent unchanged:

```text
incumbent
+ challengers
→ compare
→ keep incumbent unless a better brief-adherent challenger appears
```

This corrects a defect in the frozen experiment where B/C mutation populations did not retain the parent.

## Novelty is not quality

Behavioral diversity is useful for deciding what deserves inspection. It is not the final objective.

The frozen experiment’s clearest warning was the filament route: structural mutation produced roughly **5×** the behavioral coverage of numeric mutation while performing dramatically worse aesthetically/adherently.

Therefore:

```text
novel != good
coverage != quality
occupancy != success
```

Final selection remains visual/temporal and brief-aware.

## Math-first representation remains central

v0.6’s core decomposition still defines the strongest compact representation path:

```text
kernel → latent fields → family operator → nonlinear deformation → projection
```

See `references/math-first-generators.md`.

When repeated-family semantics matter, `scripts/check-family-math.mjs` can inspect each generator instance before rasterization.

## Morphology remains conditional

Use explicit morphology when the user needs named anatomy, attachment hierarchy or local editing.

The project does **not** treat morphology as the universal source of visual complexity. A small indirect mathematical generator may produce richer phenotypes precisely because it does not explicitly encode every visible part.

## Discovery search reference

`references/discovery-search.md` defines the production policy:

- incumbent first;
- brief invariants before search;
- topology-aware mutation permissions;
- elitism;
- novelty only for archive/review diversity;
- visual + temporal challenger selection;
- staged search effort rather than a hard-coded candidate count;
- golf only after discovery.

## Validation stack

Validators are falsification tools, not creative fitness functions:

```text
check-family-math      → did repeated generator instances change coherently?
check-control-scope    → did rendered change stay in allowed structure?
check-control-effect   → did a simple visible observable move as intended?
visual/temporal review → is the phenotype actually worth keeping?
morphology survival    → did defining structure survive golf?
```

Do not collapse these into one scalar beauty objective.

## Search-lab evidence

The experiment remains preserved under:

```text
experiments/search-lab/
```

Important files:

```text
epistemology.md
briefs.json
search.mjs
render-genotype.mjs
scorecard.md
pilot-results.md
full-results.md
```

The experiment also identified its own limitations: fixed rather than independently sampled A baselines, no parent elitism in B/C, one evaluator, three-frame rather than full-animation review, and one fixed 24-candidate search budget.

Those are inputs to the next causal study, not reasons to erase the result.

## What is intentionally *not* hard-coded yet

The evidence does not yet establish:

- an optimal search budget;
- optimal mutation probabilities;
- whether many independent starts beat deeper search around one start;
- broad structural search for morphology-first explicit anatomy;
- an automatic aesthetic scorer;
- candidate-level continuous optimization.

The next paired experiment should measure those before they become architecture.

## Tweet constraint

The recommended executable form `CODE//#つぶやきProcessing` leaves **259 X-weighted characters for code**.

Always verify the complete post:

```sh
node scripts/check-length.mjs post.txt
```

280 is a ceiling, not a target.

## Current thesis

The project is no longer best described as a formula generator plus validators.

The strongest current model is:

> **good mathematical representation + topology-aware search + brief-aware selection + elitism.**

The goal is to reliably discover a **large phenotype from a small mathematical cause**.