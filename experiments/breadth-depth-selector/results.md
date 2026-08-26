# Breadth vs Depth + Selector Reliability — Results

## Executive result

The result is **route-dependent**, and the selector evidence is strong enough for the coarse conclusion but not for fine-grained optimization.

| route | primary ranking | blinded retest | robust conclusion |
|---|---|---|---|
| recurrence / storm organ | D1 > B8 > B4 | D1 > B4 > B8 | **depth wins** |
| repeated family / drifting spores | B4 > B8 > D1 | B8 > B4 > D1 | **breadth wins; B4 vs B8 unresolved** |

Therefore the experiment does **not** support either:

```text
always search deeper around one incumbent
```

or:

```text
always maximize independent starts
```

The stronger interpretation is:

> **independent starts are valuable for finding qualitatively different basins; depth is valuable once a promising basin has high local leverage.**

This motivates a future hybrid portfolio search, but that hybrid was not tested here and should not yet become production policy.

---

## Frozen protocol

See `protocol.md`.

For each route every condition received exactly 40 generated challengers:

- `D1`: one viable start, four sequential 10-candidate rounds around promoted elites;
- `B4`: four independent viable starts, ten challengers per start;
- `B8`: eight independent viable starts, five challengers per start.

D1 used start #1. B4 used starts #1–4. B8 used starts #1–8 from the same viable-start distribution.

Character count and tweet viability were excluded from artistic search and ranking.

---

# 1. Recurrence — storm organ

Brief:

- recurrent state as latent material rather than textbook attractor output;
- one coherent animated body;
- transformed projection with persistent internal crossings;
- slow + local temporal structure;
- no literal anatomy.

## D1 lineage

```text
Rstart1
-> D1-R1-3
-> D1-R2-10
-> D1-R3-5
-> final round retains D1-R3-5
```

The depth search improved the phenotype in stages:

1. R1-3 increased internal volume while preserving one body;
2. R2-10 improved full-horizon stability;
3. R3-5 added materially richer persistent crossings;
4. the final 10-candidate round did not beat the elite, so no promotion was forced.

## Condition winners

Primary artistic ranking:

```text
D1 > B8 > B4
```

Blinded retest on anonymized rows at offset times within the same temporal horizon:

```text
D1 > B4 > B8
```

Both passes therefore choose **D1**.

Why D1 won:

- materially denser internal crossing structure;
- coherent single-body identity across the horizon;
- stronger transformation of recurrent state into a folded object rather than a clean/simple glyph.

B4/B8 produced many additional regimes, but the best of those were either simpler, more iconic but less materially rich, or drifted toward detached residue bodies.

## Coverage diagnostic

| condition | viable / 40 | structural signatures `(projection,deformation,familyCount)` |
|---|---:|---:|
| D1 | 34 | 11 |
| B4 | 37 | 20 |
| B8 | 32 | 20 |

Breadth roughly doubled structural coverage, but did **not** improve the artistic winner.

This is direct evidence that:

```text
more behavior-space coverage != better art
```

for this recurrence brief.

---

# 2. Repeated family — drifting spores

Brief:

- 5+ distinct related bodies;
- one shared mathematical generator;
- visible repetition-with-variation;
- coordinated but non-identical motion;
- no per-instance literal formulas.

## D1 lineage

```text
Fstart1
-> FD1-R1-5
-> FD1-R2-1
-> FD1-R3-5
-> FD1-R4-1
```

Depth substantially improved start #1: static repeated seeds became a materially varied moving ring with stronger sibling-state differences.

## Breadth discovery

Both B4 and B8 found their best phenotype in **start #4**, a smoky asymmetric arc-family basin unavailable to D1.

Primary ranking:

```text
B4 > B8 > D1
```

Blinded retest:

```text
B8 > B4 > D1
```

The exact B4-vs-B8 preference is unstable, but **both selectors prefer a breadth condition over D1**.

Why the breadth basin beat D1:

- stronger asymmetric spatial rhythm;
- more convincing repetition-with-variation;
- less generic perfect-ring regularity;
- siblings occupy visibly different material states while remaining related by one law.

The key gain was **access to another basin**, not merely more local parameter coverage.

## Coverage diagnostic

| condition | viable / 40 | structural signatures `(layout,shape,deformation,familyCount)` |
|---|---:|---:|
| D1 | 40 | 26 |
| B4 | 38 | 28 |
| B8 | 39 | 33 |

B8 has the widest structural coverage, but the primary selector preferred B4. Again, coverage should not be promoted to a quality function.

---

# 3. Selector reliability

A second selector pass was performed only after primary winners were frozen.

The retest:

- anonymized condition identities;
- shuffled row order;
- used offset sample times inside the same route horizon;
- applied a separately stated rubric: invariants -> temporal identity -> composition/material -> temporal interest -> distinctiveness.

This is a **same-model blinded retest**, not an independent model evaluation.

## Agreement

### Recurrence

- primary: `D1 > B8 > B4`
- blind: `D1 > B4 > B8`
- exact top-1 agreement: **yes**
- pairwise agreement: **2 / 3**
- Spearman rho: **0.5**

### Family

- primary: `B4 > B8 > D1`
- blind: `B8 > B4 > D1`
- exact top-1 agreement: **no**
- winner class agreement (`breadth > depth`): **yes**
- pairwise agreement: **2 / 3**
- Spearman rho: **0.5**

## Interpretation

The selector is presently more trustworthy for **large preference margins / coarse decisions** than for differentiating close neighbors.

Robust across both passes:

```text
recurrence: D1 beats both breadth conditions
family:     both breadth conditions beat D1
```

Not robust:

```text
B4 vs B8 when the two breadth winners are visually close
```

Therefore the current selector evidence does **not** justify using a single model's fine-grained ranking as a continuous artistic fitness signal.

Pairwise judgment may still be useful for:

- eliminating clear regressions;
- identifying large-margin promotions;
- choosing broad search direction;
- reducing a review set before human or independent evaluation.

---

# 4. Main causal interpretation

The experiment suggests two different sources of value.

## Basin discovery

Breadth increases the probability of seeing qualitatively different mathematical regimes.

The family result is the clean example: start #4 contains a stronger artistic niche than anything reached by 40 sequential challengers around start #1.

## Basin exploitation

Depth compounds improvements when the local basin has useful structure.

The recurrence result is the clean example: the D1 lineage repeatedly improved material and temporal coherence and ultimately beat broader structural coverage.

So the likely high-leverage search topology is not either extreme. It is a hypothesis of the form:

```text
sample several viable basins
-> compare coarse artistic promise
-> allocate remaining budget deeper into one/few promising basins
```

This **hybrid portfolio search remains a hypothesis**. It must be tested under an equal total budget before becoming production policy.

---

# 5. What this changes in our research priorities

## Strongest next search experiment

Test a hybrid under the same 40-challenger budget, e.g.:

```text
H4:
4 starts x 5 challengers = 20
-> select promising basin(s)
-> spend remaining 20 on depth
```

Possible variants can decide whether to exploit one basin or retain two elites, but the protocol should be frozen before results.

Compare directly against the D1/B4/B8 evidence already collected where possible.

## Strongest selector experiment

Get genuinely independent preference evidence on a small set of large-margin and close-margin pairs:

- user blind judgments;
- independent model judgments if available;
- current selector.

Measure which dimensions are stable enough to automate.

The current same-model retest is not sufficient to train or tune a universal aesthetic scorer.

---

# 6. Production recommendation

**No production update yet.**

Current progressive search remains compatible with both observed routes. The experiment identifies a possible higher-level portfolio strategy, but it has not yet beaten the current extremes under a controlled hybrid condition.

Do not add:

- fixed number of independent starts;
- a structural-coverage fitness score;
- a scalar aesthetic scorer;
- route-independent breadth/depth constants.

The next information gain is from testing the hybrid search allocation, not adding rules.
