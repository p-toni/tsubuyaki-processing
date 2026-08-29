# Repertoire architecture v1 — prepared, not activated

Status: **staging only**. This branch is prepared while fresh basin confirmation #73 runs. Do not merge or use it to change search behavior unless #73 is `CONFIRMED` under its preregistered rule.

## Why this layer exists

The current search collapses broad discovery into a small survivor set and then spends depth on those survivors. The #72 pilot supplied the first strong mechanistic evidence that discovery and exploitation should have different freedoms: a route-aware local subspace helps recover targets inside a selected mathematical basin and loses leverage when the target requires crossing the basin boundary.

If #73 confirms that result, the next architectural problem is no longer “what mutation scale is best?” It is:

> how do we preserve several mathematically distinct basins and phenotype niches long enough to allocate search depth intelligently among them?

This is a quality-diversity / repertoire problem.

## Layer 1 — explicit mathematical basin identity

`basin_identity.py` promotes the exact route partitions frozen in #72, but separates two concepts that the experiment intentionally froze together:

- **identity keys** define the mathematical basin;
- **sampling keys** define execution/resolution state;
- **local keys** can vary during trust-region exploitation.

A basin id is a stable hash of `route + identity signature`. Changing sampling resolution alone therefore does not invent a new mathematical basin, even though trust-region exploitation freezes both sampling and identity.

This distinction matters later if we want to render or evaluate the same basin at different fidelity without fragmenting the archive.

## Layer 2 — phenotype-structural niches

A repertoire niche is not a genome bucket and is not a route label. It is computed from rendered geometry after removing translation and global scale.

`phenotype_descriptors.py` measures:

- covariance anisotropy;
- central-void ratio;
- radial variation;
- angular coverage;
- shape motion after per-frame translation/scale normalization;
- intrinsic dimension (1-D vs 2-D mathematical manifold).

The first sparse niche grid deliberately uses only:

```text
intrinsic dimension
× 4 anisotropy bins
× 4 central-void bins
× 4 shape-motion bins
```

Maximum: 128 coarse structural cells.

`radial_cv` and `angular_coverage` are retained as diagnostics but do not create extra dimensions yet. This avoids immediately producing a mostly empty high-dimensional grid.

### Explicit exclusion

The v1 niche key does **not** use:

- raw occupancy;
- raw canvas span / bounding-box size;
- centering;
- diagnostic score.

Those quantities already participate in viability/composition heuristics. Reusing them as diversity axes would partially turn “quality” into “diversity” and preserve optimization artifacts rather than genuinely different forms.

The niche map itself must be qualified before allocation. `experiments/repertoire-niche-audit-v1/` preregisters an out-of-design consumed-seed audit for within-route diversity, cross-route overlap, and leakage against existing composition/fitness proxies. A failed map cannot be rescued by retuning the same axes or bins on that holdout.

## Layer 3 — review-gated archive

`repertoire_archive.py` is hierarchical:

```text
phenotype niche
  └── route stratum
        └── up to K distinct mathematical basins
```

v1 defaults to `K=2` basin representatives per route per niche.

Why retain route strata inside phenotype cells? The project treats the five routes as fixed strata rather than exchangeable random samples. Two representations may reach the same structural phenotype through different mathematical grammars. The archive should not let one route erase the other before we have evidence about which grammar is useful under future briefs.

### No implicit quality authority

Empty archive capacity may be filled automatically because nothing is displaced.

When a new candidate would replace an incumbent, the archive returns `review-required`. It contains **no** automatic “best score wins” path. `replace()` only applies a decision already made by an authorized caller. Explicit replacement is also forbidden from collapsing two archive slots to the same mathematical basin.

This preserves the existing authority rule:

- deterministic/same-model signals may triage or order work;
- they cannot independently establish artistic promotion.

## Layer 4 — allocation has two nested authorities

The next allocator must not replace the existing route-safety contract.

### Outer layer: route-safe budget

`route_allocation_policy.py` remains authoritative for how much compute each representation receives:

- unresolved routes retain nonzero minimum exposure;
- semantic/deterministic priors may order or focus extras but cannot hard-prune;
- only explicit strong human/independent `drop` evidence can eliminate a route;
- insufficient budget fails broad rather than silently becoming top-k.

This produces a budget `B_route` for each active route.

### Inner layer: repertoire allocation

Only *inside* each route's assigned budget may the quality-diversity allocator choose among that route's surviving `niche × basin` entries.

Candidate inner-layer signals include:

- unfilled phenotype niches;
- under-sampled basins;
- uncertainty / unresolved review evidence;
- demonstrated local improvement inside a basin;
- brief-conditioned relevance.

This nesting is deliberate. A QD pressure such as novelty or archive sparsity must never become a second, implicit mechanism for representation pruning.

The inner allocator is intentionally not hard-coded yet. It should be preregistered only after #73 resolves and the structural niche map qualifies. The current branch therefore implements preservation primitives, not a UCB/bandit formula selected before the substrate is validated.

## Activation gate

### If #73 confirms

1. persist and merge the confirmation;
2. validate and promote these basin/repertoire primitives;
3. run the preregistered consumed-seed niche-map audit;
4. only if the niche map qualifies, wire confirmed trust-region mutation to explicit `BasinIdentity` and preserve broad-discovery candidates in `RepertoireArchive`;
5. design a consumed-seed inner allocation contrast under fixed outer route-safe budgets;
6. only then consider fresh confirmation of an allocation policy;
7. keep independent/human artistic replication as the final promotion layer.

### If #73 does not confirm

Do not merge this branch as a search-policy change. The descriptor/archive code may remain useful infrastructure, but basin-restricted exploitation must stay experimental and no allocator may assume it is beneficial.

## Scientific boundary

This architecture is search infrastructure. It does not by itself:

- validate a mathematical representation;
- establish artistic quality;
- prune a route;
- change the production/default search;
- change `SKILL.md`;
- justify adding a new representation.
