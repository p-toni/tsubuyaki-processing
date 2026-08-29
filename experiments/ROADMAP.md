# Experiment roadmap

This roadmap is a research dependency graph, not a backlog ordered by convenience.

The project should advance only when the evidence required by the next layer is strong enough. A failed or unresolved prerequisite blocks downstream optimization rather than becoming another hyperparameter to tune around.

## End state

The target system is not a single globally best generator or one universally optimal search policy.

It is an evidence-authoritative mathematical discovery system that:

```text
brief
→ expose multiple mathematical representations
→ preserve several viable niches / elites
→ allocate search budget adaptively
→ exploit promising basins without destroying their defining grammar
→ use independent artistic evidence for promotion
→ retain causal provenance
→ apply compression pressure only at deployment promotion
```

This is closer to a quality-diversity / repertoire-search problem than to ordinary single-objective optimization.

The practical implication is important:

```text
representation diversity is a resource to allocate
not noise to eliminate as early as possible
```

## Evidence already strong enough to freeze

Do not reopen these research lines without a concrete failure signal.

### Representation exposure and routing authority

Current five research representations:

```text
recurrence
orbit
family
sheet
filament
```

Human-calibrated routing showed that text/same-model semantics are useful only as a prior. Every mathematical representation receives nonzero probe exposure; semantic routing may order or bias cheap budget but cannot hard-prune a route.

Hard route elimination requires explicit strong human / independent-model evidence. Missing or conflicting review fails broad.

### Artistic evidence authority

Same-model and deterministic proxy judgments can triage or order review, but cannot provide fine-grained artistic promotion authority.

Candidate promotion requires strong human / independent-model evidence. Low-confidence or conflicting evidence defers.

### Reviewer scheduling

The K=2 bounded evidence-review policy reproduced eager trajectories under genuinely adaptive parent-dependent search while reducing ratings. Five-route scheduler stress then preserved exact search trajectories at larger workload.

Freeze reviewer-scheduler semantics for now. Search quality is the bottleneck.

### Deployment pressure

Description length is not a creative-search fitness function.

Creative discovery ranks the art first. Compression-survival then gates deployment promotion, followed by golf and exact phenotype verification.

## Active dependency: repair the search-quality instrument

Recent search-mechanics experiments #56–#63 were built around matched-frame pixel MAE.

#64 falsified that objective for sparse line art: blank images systematically beat small translations of the correct structure. It also retired the stochastic `seed majority → route majority` gate for confirmatory search-quality inference.

Therefore the current dependency chain is:

```text
measurement validity
        ↓
re-measure historical search evidence
        ↓
select one promising search contrast
        ↓
fresh confirmation
        ↓
search-architecture work
```

No mutation/operator optimization should jump this queue.

## Phase 1 — measurement rehabilitation

### #66 — recover the #65 structural replay

#65 attempted to remeasure #56–#61 under `sparse-shape-v1`, but the aggregate artifact was empty because experiment artifacts collided during download and the reducer error was hidden by a shell pipeline.

#66 repairs only experiment transport:

- preserve artifact namespaces;
- fail closed on reducer failure;
- require non-empty valid JSON output.

No scientific interpretation is allowed until the repaired reducer succeeds.

### #67 — structural-metric sensitivity audit

`sparse-shape-v1` fixes the background-dominance failure but has a known 3px tolerance plateau: an exact 3px translation receives zero distance.

#67 stress-tests it and a frozen `sparse-shape-v2` candidate on already-consumed targets using:

- graded translations;
- partial structure deletion;
- excess duplicated structure;
- dense wrong internal structure;
- alpha/material changes;
- route-native neighbors;
- unrelated valid phenotypes;
- blank controls.

`v2` replaces the single radius-3 tolerant F1 with the mean of radii `0,1,2,3`, keeping the same foreground rule and shape/mass weighting.

### Decision after #67

If v2 **passes** the preregistered sensitivity contract:

```text
v2 becomes eligible for consumed-seed historical replay
```

It still does not automatically become a production benchmark.

If v2 **fails**:

```text
pause search mechanics
→ metric-design experiment
```

The next metric-design candidates should be geometric rather than additional arbitrary scalar tuning, especially:

1. symmetric distance-transform / Chamfer-style foreground distance;
2. robust/trimmed geometric distance for partial structure;
3. explicit foreground mass or support penalty;
4. optional topology/skeleton diagnostics kept separate from the primary distance.

Any candidate must first defeat adversarial controls before it is allowed to evaluate search algorithms.

## Phase 2 — one coherent remeasurement of #56–#63

If #67 yields a qualified metric, replay the complete recent search-mechanics arc using **only already-consumed seeds**.

Historical scope:

```text
#56 search leverage
#57 route-conditional topology
#58 online topology probe
#59 start-state topology
#60 paid stage-1 response
#61 fixed hedge
#62 global mutation scale
#63 stage-specific mutation schedule
```

#65/#66 cover only #56–#61 and use v1. They are diagnostic evidence, not the final historical reinterpretation if v2 qualifies.

The full replay should preserve:

- historical targets;
- candidate generation;
- RNG streams;
- candidate budgets;
- calibration/holdout partitions;
- historical policy-selection rules where needed to reconstruct the policy;
- paired route×seed continuous effects.

Do **not** restore the old vote-of-votes gate.

### Required output

For every historical conclusion classify it as:

```text
SURVIVES
REVERSES
UNRESOLVED / HETEROGENEOUS
```

Preserve route-level heterogeneity instead of compressing five routes into one bit.

For policy comparisons report at minimum:

- all paired route×seed deltas;
- route means;
- overall mean and median;
- local/global decomposition when defined;
- calibration-choice changes;
- sensitivity to single-block outliers;
- uncertainty interval or paired randomization/bootstrap summary suitable for the final design.

The purpose is evidence triage, not retrospective significance mining.

## Phase 3 — select one fresh confirmatory search contrast

Only after the historical replay should a fresh-seed experiment be designed.

Do not run another broad operator grid immediately.

Choose the **single strongest surviving contrast** whose mechanism is interpretable and whose historical structural effect is not dominated by one route or one seed.

Potential outcomes:

### A. topology allocation remains promising

Test one adaptive depth/breadth policy against a simple equal-budget baseline.

### B. mutation schedule remains promising

Test the one frozen schedule against the exact current schedule.

### C. neither survives

Stop local search-mechanics tuning and move upward to representation/basin allocation rather than testing progressively smaller parameter tweaks.

### Statistical contract

Fresh confirmation should use paired scenarios / random streams wherever possible.

The unit of evidence is the paired effect, not a route win bit.

Primary interpretation should emphasize:

```text
effect magnitude
uncertainty
route heterogeneity
replication across fresh seeds
```

A binary adoption threshold may be preregistered, but should be applied to a continuous estimand rather than a two-stage majority vote.

## Phase 4 — representation-level budget allocation

Once the objective can distinguish search quality credibly, move from tuning within one route to allocating compute across the representation portfolio.

The architecture boundary from human routing remains fixed:

```text
every route receives probes
semantic prior can bias cheap allocation
no semantic hard-pruning
```

Compare under equal total generation/review budget:

1. **uniform portfolio** — equal exposure/depth across all live routes;
2. **screened fixed allocation** — probe all, then allocate a frozen share to promising routes;
3. **adaptive allocation** — progressively shift additional budget toward routes/basins with evidence of response while preserving minimum exposure elsewhere.

Useful algorithm families to test include successive-halving/racing and bandit-style allocation, but the experiment should compare mechanisms, not brand names.

Important invariant:

```text
a route with weak early evidence can lose extra budget
but cannot disappear without authoritative drop evidence
```

## Phase 5 — niche-preserving exploitation / trust regions

The earlier hybrid portfolio experiment already produced a clear qualitative mechanism:

```text
basin discovery works
broad generic exploitation can destroy what made the basin good
```

That result should become a direct experimental hypothesis once measurement is trustworthy.

Compare equal-budget policies after basin selection:

```text
broad exploitation
vs
route-aware trust-region exploitation
vs
trust-region exploitation + explicit escape/unlock when saturated
```

Trust-region mutations should preserve the basin's defining discrete relationships while varying lower-level continuous or compatible structural degrees of freedom.

Examples:

- family: preserve multi-instance layout/shared generator while tuning harmonics, deformation, phase/material;
- filament: preserve axial identity while tuning continuous geometry before axial-compatible structure;
- sheet: preserve 2D sheetness/negative-space contract while varying folds, latent scales, density;
- recurrence: preserve viable recurrence role while allowing somewhat broader projection/deformation exploration.

The goal is not merely lower target distance. The later artistic replication must verify that niche preservation improves useful finalists rather than just making search conservative.

## Phase 6 — repertoire / quality-diversity search

If representation allocation and trust-region exploitation show leverage, stop treating the search product as one provisional champion.

Test a small elite archive organized by interpretable behavior descriptors.

Candidate descriptor families include:

- occupancy/span;
- negative-space/cavity structure;
- family/repetition count;
- axial vs radial organization;
- temporal displacement/change;
- density/material distribution;
- route/basin identity.

Descriptors are for **illumination and diversity**, not artistic fitness.

The archive should answer:

```text
given the same budget,
does preserving several high-quality niches produce
better final human/independent choices and broader brief coverage
than champion-only elitism?
```

Do not adopt a descriptor because it is easy to calculate. It must correspond to a meaningful visual/behavioral distinction.

## Phase 7 — independent artistic replication

Objective target-recovery experiments are useful for search-mechanics research because the hidden target supplies a reproducible answer.

They do **not** establish artistic quality.

Before a search architecture becomes the creative default, run blinded temporal finalist panels with authoritative independent evidence.

Required separation:

```text
objective structural benchmark
→ search mechanics

human / independent-model preference
→ artistic usefulness
```

Same-model judgments may reduce review cost but cannot close this loop alone.

Measure at least:

- preferred finalist rate;
- strong-vs-defer rate;
- representation/niche diversity among preferred finalists;
- reviewer burden;
- failure modes where the objective improved but the art regressed.

## Phase 8 — representation-vocabulary expansion trigger

Do not add more mathematical families merely to increase route count.

Expand representation vocabulary only when one of these repeats:

1. authoritative route review returns `none fit` for current grammars;
2. preferred examples exhibit a structural grammar the current five cannot reproduce;
3. a class of briefs repeatedly fails despite adequate search within every current route.

When triggered, research new representation families from external mathematical/generative-art examples and test **incremental coverage**, not novelty for its own sake.

## Separate track — morphology-first work

Morphology-first explicit anatomy remains under-evidenced and should not silently share conclusions from the math-first route portfolio.

Its future sequence is separate:

```text
capacity / controllability audit
→ local mutation trust region
→ broad body-plan search
→ independent artistic review
→ compression-survival study
```

Run this when morphology-first briefs become a material bottleneck, not before.

## Graduation criteria for a default search change

A search-policy change should not reach the production/default path from one benchmark win.

Require all of:

1. **instrument validity** — the metric passed adversarial structural controls;
2. **fresh replication** — the policy survived a preregistered untouched-seed comparison;
3. **effect robustness** — improvement is not explained by one route/seed/outlier;
4. **architecture invariants** — representation exposure, evidence authority and deterministic replay remain intact;
5. **artistic replication** — blinded independent review shows useful finalist improvement or equivalent quality at materially lower cost;
6. **deployment compatibility** — no regression in compression-survival / exact final verification.

Until then, an experiment can inform the next experiment without becoming a default.

## Research stop rules

Avoid endless local optimization.

Pause a research line when:

- its measurement instrument is invalid;
- repeated credible contrasts produce only tiny heterogeneous effects;
- gains come from one representation while harming several others and no principled route-specific policy exists;
- the next proposed experiment is another nearby hyperparameter grid without a new mechanism;
- reviewer or compute cost grows faster than demonstrated finalist value.

When that happens, move **up one abstraction level**:

```text
mutation parameter
→ stage policy
→ basin policy
→ representation allocation
→ repertoire architecture
→ representation vocabulary
```

This prevents the system from overfitting its research budget to a locally convenient benchmark.

## External research lenses

The roadmap uses external work as design pressure, not as authority to copy an algorithm unchanged.

### Quality-diversity / repertoire search

- Mouret & Clune, *Illuminating search spaces by mapping elites* (MAP-Elites, 2015): search can intentionally preserve high-performing solutions across meaningful behavioral niches rather than collapse to one optimum.
- McCormack & Cruz Gambardella, *Quality-diversity for aesthetic evolution* (2022): applies quality-diversity directly to an aesthetic line-drawing generative system and reports value from multiple diverse high-quality phenotypes.
- Sfikas, Liapis & Yannakakis, *Monte Carlo Elites* (2021): frames archive parent allocation as an exploration/exploitation problem, relevant to later adaptive repertoire budgeting.

### Experimental design

- Strens & Moore, *Policy Search using Paired Comparisons* (JMLR, 2002): pairing start states/randomness can materially improve noisy policy comparisons and highlights the need for independent test scenarios.
- Patterson et al., *Empirical Design in Reinforcement Learning* (JMLR, 2024): emphasizes effect variability, hyperparameter bias, multiple tasks and statistically credible comparisons rather than weak aggregate claims.
- Demšar, *Statistical Comparisons of Classifiers over Multiple Data Sets* (JMLR, 2006): motivates preserving paired multi-task evidence and using robust paired/nonparametric analysis instead of ad-hoc win counting.

### Image / shape measurement

- Snell et al., *Learning to Generate Images with Perceptual Similarity Metrics* (2015): demonstrates that pixel losses can misalign with perceived image quality and motivates multi-scale structural comparisons.
- Ding et al., *Image Quality Assessment: Unifying Structure and Texture Similarity* (DISTS, 2020): further separates structural from texture similarity and adds geometric tolerance; useful conceptual evidence, though natural-image metrics should not be assumed valid for sparse line art.
- geometric matching literature around symmetric Chamfer / Hausdorff distances motivates testing explicit bidirectional foreground geometry when tolerant overlap metrics plateau.

The domain-specific rule remains:

```text
external metric/algorithm idea
→ adversarial local validation
→ consumed-seed replay
→ fresh confirmation
→ independent artistic replication
```

No external method bypasses that sequence.

## Immediate priority

Current order:

```text
#66 recover structural replay infrastructure
#67 metric sensitivity audit
        ↓
if v2 passes:
  full #56–#63 consumed-seed replay under v2
        ↓
  select one strongest mechanistic contrast
        ↓
  fresh paired confirmation
        ↓
  representation allocation / trust-region research

if v2 fails:
  geometric metric-design audit
  search mechanics remain paused
```

That is the active roadmap until new evidence changes it.
