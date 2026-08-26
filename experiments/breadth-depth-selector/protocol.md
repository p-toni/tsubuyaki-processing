# Breadth vs Depth + Selector Reliability — Frozen Protocol

## Questions

1. Under a fixed candidate/render budget, does mathematical discovery improve more from deeper search around one viable basin or from multiple independent starts?
2. How stable is the artistic selector when candidate identities and search conditions are hidden and the same finalists are re-ranked under a second rubric?

No production policy changes are allowed until results are written.

## Routes

Two math-first routes with different expected landscapes:

### Recurrence — `storm organ`

Brief invariants:
- recurrent state is latent material, not a textbook attractor picture;
- one coherent animated body;
- transformed projection with persistent internal crossings;
- slow + local temporal structure;
- no literal creature anatomy.

### Repeated family — `drifting spores`

Brief invariants:
- 5+ distinct related bodies;
- one shared mathematical generator;
- visible repetition-with-variation;
- coordinated but non-identical motion;
- no per-instance literal formulas.

## Fixed search budget

Each condition gets **40 generated challengers per route**, excluding the initial viable starts.

### D1 — depth

```text
1 independent viable start
-> 10 challengers
-> visually select/promote elite
-> 10 challengers around new elite
-> visually select/promote
-> 10 challengers
-> visually select/promote
-> 10 challengers
```

Total: 40 challengers around one lineage, with elite preservation.

### B4 — medium breadth

```text
4 independent viable starts
-> 10 challengers around each
-> best artistic finalist across all four basins
```

Total: 40 challengers. No cross-basin refinement after the first 10.

### B8 — high breadth

```text
8 independent viable starts
-> 5 challengers around each
-> best artistic finalist across all eight basins
```

Total: 40 challengers.

The comparison is about allocation of the same challenger budget, not wall-clock time.

## Candidate generation

- Work in readable expanded mathematical roles.
- No character count or compactness information during generation or artistic selection.
- Mutation vocabulary follows current route policy, but the experiment does not require identical mutations across conditions.
- Hard validity/framing can reject broken work; rejected generated challengers still consume budget.
- Do not use a scalar aesthetic fitness function.

## Artistic selection

Primary selection uses representative frames over a route-appropriate temporal horizon.

Judgment dimensions remain separate:
- brief adherence (gate);
- composition / silhouette;
- material/coherence;
- temporal interest;
- mathematical leverage;
- distinctiveness / genericness.

The primary evaluator records pairwise/finalist preferences without source length.

## Selector reliability retest

After all search results and primary condition winners are frozen:

1. render a shuffled finalist set with anonymized IDs and no condition labels;
2. perform a second ranking using a separately stated rubric:
   - first reject invariant failures;
   - prefer coherent identity across the full temporal horizon;
   - then composition/material;
   - then temporal interest;
   - then distinctiveness;
3. compare primary vs blinded-retest ordering.

This is **same-model blinded retest**, not an independent model evaluation. Report that limitation explicitly.

Metrics:
- top-1 agreement;
- pairwise agreement among finalists;
- rank correlation where meaningful;
- disagreement reasons by dimension.

## Main breadth/depth outcomes

For each route and condition record:
- final artistic winner;
- number of distinct viable basins/starts represented among the top review set;
- whether the winner came from the initial start or required local refinement;
- qualitative winner margin;
- behavior/descriptor coverage only as diagnostic, not quality;
- primary + blinded selector result.

The strongest claim allowed:

- `depth wins` only if D1's winner is consistently preferred over B4/B8 under selector retest;
- `breadth wins` only if B4/B8 wins consistently;
- `mixed / route-dependent` if the routes differ or selector uncertainty crosses the condition difference.

## Deployment

This experiment is primarily about artistic discovery. Do **not** use tweet viability to choose breadth/depth winners.

After the artistic result is frozen, optional v0.14.1 compression preflight may be run on route winners only as a secondary observation. It cannot change the breadth/depth conclusion.

## Stop conditions

- exactly 40 generated challengers per condition per route;
- no extra rescue candidates after seeing results;
- do not tune condition rules post hoc;
- preserve failed or ambiguous outcomes.
