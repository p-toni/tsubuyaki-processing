# Paired Route-Aware Search — Results

Status: completed experiment; no production-policy changes in this branch.

## Question

> Given a viable starting mathematical system, does the v0.8 route-aware search policy discover better brief-adherent challengers more efficiently than the previous generic structural search policy?

## Setup

Four routes, 10 independently sampled viable starting genotypes per route:

- repeated math family;
- recurrence / living knot;
- dense 2D sheet;
- intentional axial filament.

Every paired trial shared the exact same incumbent across:

- **A:** incumbent only;
- **B:** generic structural + numeric search;
- **C:** v0.8 route-aware search.

B/C always retained A as an elite. Mutation budgets were nested `4 / 8 / 16 / 24`.

The 40 starting genotypes were deterministic independent draws from the frozen v0.6 genotype vocabulary, not 40 independent LLM generations. This experiment therefore tests search policy across diverse valid mathematical starts; it does not estimate one-shot model variance.

Candidate generation did not use aesthetic fitness. A lightweight post-generation critic was used to select one B and one C finalist for visual review. Because the visual audit disagreed with this critic on multiple routes, all critic-based curves below should be interpreted as **search/adherence-efficiency diagnostics**, not beauty measurements.

Representative times: `t=3`, `7.5`, `15`.

## Search-efficiency curves

### Repeated math family

| budget | B improves incumbent | C improves incumbent | B adherent mutations | C adherent mutations |
|---|---:|---:|---:|---:|
| 4 | 70% | **90%** | 95% | **97.5%** |
| 8 | 90% | **100%** | 95% | **98.8%** |
| 16 | 90% | **100%** | 96.9% | **99.4%** |
| 24 | 100% | 100% | **97.5%** | 97.1% |

Interpretation: v0.8's family-niche policy improves the probability of finding a useful challenger at small budgets without sacrificing much validity/adherence.

### Recurrence / living knot

| budget | B improves incumbent | C improves incumbent | B adherent mutations | C adherent mutations |
|---|---:|---:|---:|---:|
| 4 | 80% | 80% | **95%** | 85% |
| 8 | **90%** | 80% | **90%** | 80% |
| 16 | 100% | 100% | **88.8%** | 83.1% |
| 24 | 100% | 100% | **86.7%** | 86.3% |

Interpretation: the route-aware recurrence policy is not materially more efficient than the generic policy. The useful structural vocabulary is already fairly well aligned with this topology.

### Dense 2D sheet

| budget | B improves incumbent | C improves incumbent | B adherent mutations | C adherent mutations |
|---|---:|---:|---:|---:|
| 4 | 60% | **100%** | 35% | **55%** |
| 8 | 80% | **100%** | 30% | **52.5%** |
| 16 | 100% | 100% | 33.1% | **55%** |
| 24 | 100% | 100% | 35% | **50.8%** |

Interpretation: v0.8 strongly improves **early search efficiency** and keeps more candidates inside the sheet niche. At larger budgets, however, generic search reaches additional useful regions.

### Intentional axial filament

| budget | B improves incumbent | C improves incumbent | B adherent mutations | C adherent mutations |
|---|---:|---:|---:|---:|
| 4 | 30% | **100%** | 30% | **92.5%** |
| 8 | 70% | **100%** | 28.8% | **95%** |
| 16 | 80% | **100%** | 28.8% | **93.8%** |
| 24 | 90% | **100%** | 25.4% | **94.6%** |

Interpretation: the v0.8 local-search rule is extremely effective at avoiding wasted off-niche mutations. But the visual review below shows that its current numeric-only implementation is too conservative for deeper search.

## 24-mutation critic winner counts

The post-generation critic selected:

| route | B | C |
|---|---:|---:|
| family | 5 | 5 |
| recurrence | 3 | **7** |
| sheet | **7** | 3 |
| filament | **7** | 3 |

These are not aesthetic results. The critic strongly rewards framing/density/temporal proxies and demonstrably disagrees with visual preference in several trials.

## Visual audit of 24-budget finalists

A same-model qualitative review of three matched frames per finalist preferred approximately:

| route | incumbent A | generic B | route-aware C |
|---|---:|---:|---:|
| repeated family | 1 | 3 | **6** |
| recurrence | 0 | 5 | 5 |
| dense sheet | 0 | **6** | 4 |
| filament | 1 | **7** | 2 |

This audit is useful directional evidence, not an independent blinded human study. The same assistant produced the experiment and later reviewed the galleries, and a critic had already reduced the populations before review.

## Main finding

v0.8's topology routing is supported, but the evidence argues against interpreting it as a **fixed mutation boundary**.

The stronger model is:

> route-aware search should define the **order in which degrees of freedom are unlocked**, not permanently forbid broader within-niche structure.

### Family

Current policy looks healthy:

- preserve multi-instance niche;
- structural + parameter search is productive;
- route-aware challengers won the visual audit more often than generic ones.

### Recurrence

Generic and route-aware policies converge quickly.

The search space is already naturally aligned with the brief, so heavy route-specific restriction provides little benefit. Keep broad recurrence/family/projection exploration.

### Dense sheet

v0.8 wins on **small-budget efficiency**: every seed found a critic-improving challenger by budget 4 and adherence yield increased from 35% to 55%.

But generic search produced more visually preferred 24-budget finalists (6 vs 4).

Likely implication: start with projection/deformation-family mutations, then broaden into sampling geometry and parameter structure if early gains saturate.

### Filament

This is the clearest correction to v0.8.

Local numeric search preserves the brief exceptionally well (~95% adherent mutations versus ~25% for generic search), but generic search produced more visually preferred deep-search finalists.

Because finalists had to remain axial to pass the frozen adherence gate, the useful generic wins were not caused by switching to radial/looped projections. They came from **axial-preserving structural moves** such as discrete harmonic/family choices plus parameters.

Therefore the better policy is:

```text
stage 1: incumbent + local numeric search
stage 2: unlock axial-preserving structural genes
         (family count, harmonic family, fold law)
stage 3: change projection/topology only if the brief itself changes
```

This preserves the lesson of v0.7 without making the search too conservative.

## Epistemic update

The previous model was:

```text
route → fixed mutation policy
```

The new evidence favors:

```text
route
→ initial mutation prior
→ evaluate incumbent response
→ progressively unlock more within-niche degrees of freedom
→ preserve elite throughout
```

The key variable is increasingly **search depth / unlock schedule**, not merely search vs no-search or structural vs parameter mutation.

## What remains unresolved

- the aesthetic comparison used one model evaluator, not independent humans/models;
- post-generation critic reduction can hide candidates that a human would prefer;
- starting genotypes were independent grammar draws, not independent LLM outputs;
- we still have not measured a true preference win curve at budgets 4/8/16/24;
- morphology-first search remains untested;
- the exact unlock schedule and operator probabilities remain unknown.

## Recommended next policy hypothesis

Do not replace v0.8 with generic search.

Instead test a **progressive route-aware search**:

1. preserve incumbent;
2. small round using the route's highest-confidence operators;
3. if gains saturate, unlock additional **brief-preserving** structural genes;
4. never unlock topology-breaking operators merely for novelty;
5. stop when broader search stops producing preferred adherent challengers.

This reconciles the two experiments:

- broad search discovers disconnected valuable niches;
- topology-aware priors make early search much more efficient;
- permanent restrictions can leave quality on the table at deeper budgets.