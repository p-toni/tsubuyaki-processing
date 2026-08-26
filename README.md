# tsubuyaki-processing

A production-oriented Agent Skill for authentic, tweet-sized **#つぶやきProcessing**: compact mathematical systems whose animated phenotype is disproportionately richer than the source.

## v0.10 direction — progressive route-aware discovery

Two frozen experiments changed the project’s default approach.

The first established that search matters and that one universal mutation policy is wrong.

The paired follow-up established a more precise rule:

> **route-aware search should determine the order in which mathematical degrees of freedom are explored, not permanently restrict the search space.**

The working pipeline is now:

```text
intent
→ compact representation
→ viable incumbent
→ brief invariants
→ stage 1: high-confidence route-aware search
→ preserve/promote elite
→ if saturated: unlock more brief-preserving structure
→ preserve/promote elite
→ visual + temporal selection
→ semantic checks where relevant
→ golf winner
→ exact verification
```

## Why the policy changed

The paired route-search experiment used 10 independently sampled viable mathematical starts per route. Each trial compared the exact same incumbent against:

- generic structural + numeric search;
- v0.8 route-aware search;
- mandatory parent elitism;
- nested search budgets `4 / 8 / 16 / 24`.

The key result was not a universal winner.

### Repeated families

Route-aware search remained healthy and visually strong. Early family-niche preservation improved search efficiency without materially limiting useful structure.

### Recurrence / living knot

Generic and route-aware policies converged quickly. This route naturally tolerates broad recurrence/family/projection exploration.

### Dense sheets

Route-aware projection/deformation search was substantially more efficient at small budgets, but deeper generic search still found additional preferred finalists.

Implication: **start narrow, then unlock sampling/structural geometry when early gains saturate**.

### Filaments

Numeric-only local search kept roughly 95% of mutations inside the axial niche, far above broad generic search. But deeper generic search still found stronger axial finalists through **brief-preserving discrete structure** such as harmonic/family/fold choices.

Implication:

```text
local numeric
→ axial-preserving structural genes
→ topology/projection change only if the brief changes
```

## Current route unlock schedules

### Repeated math family

1. local family/deformation/harmonic parameters;
2. family count, discrete harmonics, distance power, deformation operator;
3. selected projection changes while preserving the multi-instance niche.

### Recurrence / living knot

1. recurrence-role parameters + residue/family structure;
2. projection/deformation/time structure;
3. broader recurrence variant only when useful.

### Dense 2D sheet

1. projection/deformation family;
2. sampling geometry, latent x/y scale, fold-frequency structure;
3. broader sheet-compatible projection only if the brief remains intact.

### Intentional 1D filament / ribbon

1. local numeric tuning;
2. axial-preserving family count / harmonic family / fold law;
3. projection/topology change only when the requested niche changes.

### Morphology-first explicit anatomy

Evidence remains incomplete. Use local validated controls first, then limited contract-preserving family/attachment exploration. Broad body-plan search is still experimental.

See `references/discovery-search.md` for the full production policy.

## Elitism remains mandatory

Every round includes the incumbent unchanged:

```text
elite
+ challengers
→ inspect
→ promote only a better brief-adherent challenger
```

Search may improve, tie or fail. It must never force regression.

When a challenger wins, it becomes the natural center of the next search stage.

## Novelty and critics are not quality

Behavioral diversity is useful for deciding what deserves inspection. It is not the final objective.

The paired experiment also showed that lightweight framing/density/temporal critics can disagree with visual preference.

Therefore:

```text
hard validity → reject broken work
brief invariants → reject off-task work
novelty → diversify review candidates
validators → falsify claims
visual + temporal judgment → choose the art
```

Do not collapse these into one scalar aesthetic fitness.

## Math-first representation remains central

The strongest compact representation path remains:

```text
kernel → latent fields → family operator → nonlinear deformation → projection
```

See `references/math-first-generators.md`.

When repeated-family semantics matter, `scripts/check-family-math.mjs` can inspect each generator instance before rasterization.

## Morphology remains conditional

Use explicit morphology when the user needs named anatomy, attachment hierarchy or local editing.

The project does **not** treat morphology as the universal source of complexity. A small indirect mathematical generator may produce richer phenotypes precisely because it does not explicitly encode every visible part.

## Validation stack

Validators remain falsification tools, not creative fitness functions:

```text
check-family-math      → did repeated generator instances change coherently?
check-control-scope    → did rendered change stay in allowed structure?
check-control-effect   → did a simple visible observable move as intended?
visual/temporal review → is the phenotype actually worth keeping?
morphology survival    → did defining structure survive golf?
```

## Experiment evidence

The first search experiment is preserved under:

```text
experiments/search-lab/
```

The paired policy experiment is preserved under:

```text
experiments/paired-route-search/
```

The latter is evidence for **unlock order / search depth**, not a permanent implementation API.

## What is intentionally not hard-coded

The evidence still does not establish:

- exact unlock thresholds;
- optimal candidate budgets or mutation probabilities;
- independent LLM starts versus deeper search around one start;
- broad structural search for morphology-first anatomy;
- an automatic aesthetic scorer;
- candidate-level continuous autonomous optimization.

The experiment budgets `4 / 8 / 16 / 24` are diagnostic, not production requirements.

## Tweet constraint

The recommended executable form `CODE//#つぶやきProcessing` leaves **259 X-weighted characters for code**.

Always verify the complete post:

```sh
node scripts/check-length.mjs post.txt
```

280 is a ceiling, not a target.

## Current thesis

The project is not best described as a formula generator plus validators or as a fixed topology-specific mutation engine.

The strongest current model is:

> **good mathematical representation + progressive route-aware search + brief-aware selection + elitism.**

The goal is to reliably discover a **large phenotype from a small mathematical cause**.