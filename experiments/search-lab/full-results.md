# Search Lab Full Run — Representation vs Search

Status: **completed frozen experiment / evidence, not a skill release**.

This run used the frozen `v0.7-search-lab` protocol without changing the v0.6 representation grammar or mutation operators after viewing intermediate results.

## Question

> Given the frozen v0.6 representation, how much does exploration improve the discovered phenotype, and does the useful search policy depend on topology?

Conditions:

- **A — fixed seed / no search**
- **B — 24 numeric parameter mutations**
- **C — 24 fixed structural-grammar + numeric mutations**

For B/C, generation used no aesthetic objective. Hard validity + behavioral novelty reduced each 24-candidate population to 6 candidates. A single evaluator then reviewed the complete 6+6 pool blind to B/C labels and selected one B and one C finalist. Final A/B/C comparisons were again condition-blind and used three matched frames (`t=3`, `7.5`, `15`).

## Population

```text
4 briefs × 10 seeds × (1 A + 24 B + 24 C)
= 1,960 raw candidates
```

Validity:

| regime | raw | hard-valid |
|---|---:|---:|
| A | 40 | 40 |
| B | 960 | 955 |
| C | 960 | 954 |
| **total** | **1,960** | **1,949** |

Hard failures were concentrated in a few filament B/C and recurrent C mutations. No aesthetic metric was used to reject candidates during generation.

## Search-space coverage

Mean within-population pairwise distance in the frozen behavioral descriptor space (density/span/centroid, with the experiment's fixed scaling):

| brief | B parameter | C structural+parameter | C/B |
|---|---:|---:|---:|
| plankton family | 0.184 | 0.447 | **2.42×** |
| living knot | 0.162 | 0.241 | **1.49×** |
| dense membrane | 0.124 | 0.257 | **2.07×** |
| filament ribbon | 0.048 | 0.244 | **5.05×** |

This repeats the pilot result more strongly: structural mutation reaches much broader phenotype space. It still does **not** imply that the broader space is better.

## Blind aesthetic first-place results

Question used for ranking:

> If only one candidate could be kept for another hour of exploration, which one would you keep?

| brief | A | B | C |
|---|---:|---:|---:|
| plankton family | 0 | 2 | **8** |
| living knot | 0 | 1 | **9** |
| dense membrane | 0 | 3 | **7** |
| filament ribbon | **8** | 1 | 1 |
| **total** | **8** | **7** | **25** |

Rank-position totals across all 40 trials:

| regime | 1st | 2nd | 3rd |
|---|---:|---:|---:|
| A | 8 | 3 | 29 |
| B | 7 | 32 | 1 |
| C | 25 | 5 | 10 |

Pairwise preference counts:

| comparison | result |
|---|---:|
| B vs A | **31–9** |
| C vs A | **30–10** |
| C vs B | **25–15** |

By route, the interaction is much stronger than the aggregate:

| brief | B vs A | C vs A | C vs B |
|---|---:|---:|---:|
| plankton | **10–0** | **9–1** | **8–2** |
| living knot | **10–0** | **10–0** | **9–1** |
| dense membrane | **10–0** | **10–0** | **7–3** |
| filament ribbon | 1–**9** | 1–**9** | 1–**9** |

Do not treat these counts as a formal population-level significance test. There was one evaluator and A is a fixed baseline rather than an independently sampled one-shot distribution.

## Brief-adherence correction

The pilot warned that structural novelty could be purchased by leaving the task. That happened in the plankton brief.

Several raw C winners were aesthetically strong but transformed the intended `multiple distinct related bodies` brief into a connected fan/wave/colony. Applying the frozen scorecard threshold `brief adherence >= 3` and falling back to the next-ranked adherent finalist changes the winner table to:

| brief | A | B | C |
|---|---:|---:|---:|
| plankton family | 0 | **6** | 4 |
| living knot | 0 | 1 | **9** |
| dense membrane | 0 | 3 | **7** |
| filament ribbon | **8** | 1 | 1 |
| **total** | **8** | **11** | **21** |

This is the most important correction in the run: **C's coverage advantage is real, but some of its apparent quality advantage is task drift.**

## What structural genes actually won

### Plankton family

Raw C wins: 8/10.

The winning structural variants often changed:

- family count toward 7/9;
- distance power toward 2.5/3;
- deformation from baseline `power-sine` into `cubic`, `sine-feedback`, or `reciprocal`;
- latent harmonics.

Only 3 of the 8 raw C winners changed projection away from the baseline harmonic projection. The useful structural search here is broader than `try another projection`.

After strict adherence review, B and C are much closer (6 vs 4), suggesting that plankton search needs stronger preservation of the **multi-instance** behavioral niche.

### Living knot

C won 9/10 and remained brief-adherent.

Common winning changes included:

- family count 7/9, often 9;
- `beta` / recurrence-variant changes;
- occasional `sigma` changes;
- `folded` / `double-polar` projection in several winners.

Only 4 of 9 C winners changed projection, so recurrence/family structure itself contributes substantial value.

### Dense membrane

C won 7/10.

This route has the clearest operator signal: **6 of the 7 C winners used the structural `bilateral` projection and the remaining C winner used `shell`**. B won the other three by tuning the original folded projection.

Projection-family search is therefore a high-leverage operator for this particular sheet representation.

### Filament ribbon

A won 8/10; B and C won once each.

Every winner remained on the `axial` projection. The broader C search space was enormous (5.05× B's descriptor coverage), but that extra coverage was mostly irrelevant or harmful to the requested axial-ribbon niche.

This is direct evidence that **more search-space coverage can produce worse discovery**.

## Hypotheses after the run

### H1 — representation bottleneck

**Rejected as a universal explanation.**

On plankton, recurrence, and sheet routes, searched candidates overwhelmingly beat the fixed seed baseline.

### H2 — parameter-search bottleneck

**Partially supported.**

B beat A 10/10 on three routes and provides a strong conservative fallback. It did not improve the filament seed reliably.

### H3 — structural-search bottleneck

**Supported for recurrence and dense-sheet routes; conditionally supported for plankton; rejected as a universal policy.**

C strongly beats B on living knot and dense membrane. Raw plankton results favor C, but adherence correction removes much of that advantage. Filament strongly favors the incumbent/local route.

### H4 — route interaction

**Strongly supported.**

This is the dominant result of the study.

A single universal mutation/search policy is the wrong architecture.

## Two experimental defects discovered by the full run

### 1. A is not an independent one-shot distribution

The frozen `search.mjs` emits the same seed genotype for every A seed. The 10 A outcomes per brief therefore repeat one fixed baseline.

The current experiment answers:

> Can B/C search beat this fixed incumbent?

It does **not** cleanly answer:

> How does search compare with the natural distribution of 10 independent one-shot generations?

Do not repair this inside the completed run; fix it in the next paired experiment.

### 2. B/C do not preserve the incumbent

B and C contain mutations only; the original seed is not kept as an elite candidate.

This makes search capable of regression. The filament result exposes the problem clearly: the seed is already a strong local solution, and almost all mutations are worse.

A practical search system should never be forced to discard a good incumbent. With simple elitism, the observed filament result would become mostly **ties plus occasional improvement**, rather than eight apparent search regressions.

## Other limitations

- one evaluator (the assistant), despite condition-blind ids;
- three representative frames rather than full continuous animation review;
- B/C receive 24 candidate attempts while A receives one — intentionally testing the value of search effort, not compute-matched methods;
- descriptor-novelty reduction can discard aesthetically valuable candidates before final review;
- tweet viability was judged conceptually; the 40 winners were not all code-golfed and length-verified;
- the grammar is still a small hand-authored sample of possible mathematical operators.

## Decision

**Do not add more morphology/control machinery now.**

The best current lever is a **route-aware, elite-preserving search system over the v0.6 mathematical representation**.

The evidence suggests different search policies:

```text
math-first repeated family
  → structural + parameter exploration
  → but preserve the multi-instance behavioral niche

recurrence / living knot
  → structural + parameter divergent search
  → family count + recurrence roles + projection are productive

dense 2D sheet
  → structural projection search is highly productive

intentional 1D filament
  → preserve incumbent
  → local parameter exploration first
  → avoid broad projection/topology mutation unless explicitly requested
```

## Next causal experiment

The clean next study should be **paired from independent starting points**:

1. Generate/freeze 10 independent v0.6 seed genotypes per brief **before search**.
2. For each seed, A/B/C all start from that exact same genotype.
3. B/C archives always include the parent genotype (**elitism**).
4. Measure best-of-budget curves at 4 / 8 / 16 / 24 mutations instead of only one search budget.
5. Keep aesthetics out of generation; preserve blind final evaluation.
6. Add at least one independent second evaluator and actual animation review.
7. Only after that replication test route-specific mutation policies against the generic C grammar.

That experiment can distinguish:

- search improves weak seeds but not strong ones;
- structural search adds value beyond numeric tuning;
- the benefit saturates at a small candidate budget;
- route-aware operators improve efficiency without merely narrowing diversity.

## Bottom line

The project should no longer be framed as `teach the model a better formula` versus `add more semantic validators`.

The current evidence points to:

> **good mathematical representation + topology-aware divergent search + selection + elitism**

as the likely discovery engine.

The key remaining uncertainty is no longer whether search matters. It is **how to allocate search effort and mutation types by representation without Goodharting novelty or drifting from the brief**.
