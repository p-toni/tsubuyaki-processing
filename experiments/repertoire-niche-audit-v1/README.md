# Repertoire niche audit v1 — preregistered, not executed

Status: prepared on draft architecture PR #74 while fresh basin confirmation #73 is pending. No workflow is attached yet, so this file consumes no evidence.

## Question

Before an allocator can treat phenotype cells as a repertoire, does the frozen `structural-v1` descriptor grid actually preserve useful **visible rendered structural diversity** rather than merely recreating representation labels, generator discretization, or existing composition/fitness heuristics?

## Descriptor under test

Frozen implementation:

`prototypes/autonomous-discovery/phenotype_descriptors.py`

The production descriptor path rasterizes through the exact prototype renderer and converts each frame to **binary visible foreground support** (`pixel > 20`) before computing niche geometry. This intentionally removes generator point count, curve parameterization, and foreground intensity above the visibility threshold from the cell definition.

Spatial descriptors are translation/global-scale normalized. Temporal `shape_motion` compares occupied cells in a normalized support grid rather than corresponding generator-point indices, so resampling the same path does not create motion. Rotation is intentionally retained as visible temporal behavior.

Cell key:

```text
4 anisotropy bins
× 4 central-void bins
× 4 shape-motion bins
```

Maximum: **64 phenotype cells**.

`intrinsic_dimension`, `radial_cv`, and `angular_coverage` remain diagnostics only. `intrinsic_dimension` is explicitly excluded from the cell key because it comes from the representation specification rather than rendered phenotype geometry; route/grammar identity is already preserved separately by the archive's route stratum.

No bin edge, axis, transform, or route-specific descriptor is selected from this audit.

## Out-of-design consumed holdout

Use the 20 master seeds from #71 that were not used in #72's 12-seed trust-region pilot:

```text
1087,1091,1093,1097,
1103,1109,1117,1123,
1129,1151,1153,1163,
1171,1181,1187,1193,
1201,1213,1217,1223
```

These seeds are already consumed search evidence from #71, so this audit spends no fresh search-policy evidence. They were not inspected when the structural descriptor axes or 4-bin grid were defined.

## Fixed population

For every master seed and every route:

```text
recurrence, orbit, family, sheet, filament
```

generate exactly six valid independent candidates using the existing selector-independent `representation_capacity._generate_route_archive` path.

Expected rectangle:

```text
20 seeds × 5 routes × 6 candidates = 600 valid phenotypes
```

Candidate generation is complete before any audit statistic is computed.

### Viability conditioning is explicit

`_generate_route_archive` rejects candidates only through the existing representation-specific **hard structural validity** checks before accepting six starts. It does not rank/select starts by `diagnostic_score`, occupancy target fit, or a pairwise selector. Diagnostic score is computed only after hard validity succeeds.

The audit therefore describes the repertoire of **viable forms**, not the unconditional genome prior. This is intentional because invalid forms would never be admissible archive entries. Acceptance attempts by route/seed should be reported as diagnostics so strong route-specific truncation remains visible, but attempt rate is not a post-hoc qualification gate.

## Recorded data

For every candidate retain:

- route and master seed;
- candidate id and genome-independent archive fingerprint where available;
- rendered-support structural descriptor and niche key;
- intrinsic dimension as a diagnostic only;
- diagnostic score;
- raw occupancy mean;
- dominant bbox span;
- centering error;
- hard-validity result.

For every route×seed block also retain the number of generation attempts needed to obtain six valid starts.

The composition fields are recorded only to test descriptor leakage. They never define cells.

## Preregistered qualification gates

`NICHE_MAP_QUALIFIED` only if all hold:

1. all 600 candidates are present and hard-valid;
2. every route occupies at least **2** distinct phenotype niches;
3. the complete population occupies at least **8** distinct phenotype niches;
4. at least **2** phenotype niches contain candidates from more than one route;
5. at least **3 of the 5 routes** participate in a cross-route niche;
6. at least **10% of all candidates** fall in phenotype niches shared by two or more routes;
7. for each cell-defining continuous axis (`anisotropy`, `central_void`, `shape_motion`), absolute Spearman correlation is **< 0.90** against each of the following, both pooled across all routes **and separately within every route**:
   - diagnostic score;
   - raw occupancy mean;
   - dominant raw bbox span;
   - raw centering error.

The cross-route candidate gate prevents a map from passing on token cell collisions while remaining effectively a route classifier. The within-route leakage check prevents pooled correlations from hiding route-conditioned near-equivalence (Simpson-style masking).

The `0.90` leakage threshold is intentionally coarse: it rejects near-equivalence to an existing quality/composition signal, not ordinary geometric correlation.

## Diagnostics, not gates

Also report:

- unique niches per route;
- route set per niche;
- routes participating in shared niches;
- fraction/count of candidates in shared niches;
- weighted dominant-route purity across occupied niches;
- descriptor ranges and quartiles by route;
- intrinsic-dimension values by route;
- `radial_cv` and angular-coverage distributions;
- pooled and route-conditioned correlation matrices;
- niche occupancy histogram;
- generation attempts and acceptance efficiency by route/seed.

These may motivate a later descriptor version but cannot rescue a failed v1.

## Failure discipline

If any gate fails:

- classify `NICHE_MAP_NOT_QUALIFIED`;
- do not tune the same descriptor axes or binning against these 20 seeds;
- do not run a repertoire allocation experiment on v1;
- any v2 must declare a new descriptor hypothesis and use a different already-consumed holdout before execution.

## Pass discipline

If the map qualifies **and** #73 confirms basin-preserving exploitation:

1. promote explicit basin-lineage/anchor + niche preservation primitives;
2. compose repertoire allocation *inside* the existing route-safe outer budget policy;
3. preregister a consumed-seed allocation contrast before testing it.

A descriptor pass alone does not authorize trust-region exploitation or any production/default change.

## Boundary

Measurement/architecture qualification only. No artistic authority, representation ranking/pruning, fresh confirmation, production/default change, or `SKILL.md` change.
