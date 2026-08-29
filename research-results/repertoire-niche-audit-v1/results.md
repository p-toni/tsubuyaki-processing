# Repertoire niche audit v1

Decision: **NICHE_MAP_QUALIFIED**.

This audit qualifies `structural-v1` as a rendered phenotype map for repertoire experiments. It uses already-consumed evidence only and does not establish artistic quality or authorize any route pruning.

## Population

- 20 consumed master seeds not used to design the descriptor grid
- 5 fixed route strata
- 6 selector-independent hard-valid starts per route/seed
- **600 rendered phenotypes total**
- workflow run `33256954969`
- sealed aggregate artifact `9716101904`
- digest `sha256:38da442adee6daf66e9eb963baa0a867dbd3f8cbc429b464337fec87a7f04b12`

## Frozen map

`structural-v1` cell key:

`anisotropy × central-void × shape-motion`

with four bins per axis, for at most **64 cells**.

Descriptors are computed from binary visible rendered support after translation/global-scale normalization. Representation metadata, diagnostic score, occupancy, raw canvas span, centering, and foreground intensity do not define cells.

## Qualification gates

All preregistered gates passed:

1. complete 600-candidate valid rectangle — **PASS**
2. every route occupies at least 2 niches — **PASS**
3. at least 8 niches overall — **PASS**
4. at least 2 cross-route niches — **PASS**
5. at least 3 routes participate in shared niches — **PASS**
6. at least 10% of candidates are in shared niches — **PASS**
7. no cell axis is near-equivalent (`|Spearman| >= 0.90`) to diagnostic score / occupancy / raw span / centering, pooled or within route — **PASS**

## Structure of the resulting map

- occupied niches: **26 / 64**
- cross-route niches: **11**
- routes participating in shared niches: **5 / 5**
- candidates in shared niches: **457 / 600 = 76.17%**
- weighted dominant-route purity: **0.7067**

Unique occupied niches by route:

| route | niches |
|---|---:|
| recurrence | 7 |
| orbit | 10 |
| family | 4 |
| sheet | 4 |
| filament | 13 |

The map therefore is not merely a disguised route classifier: every route overlaps phenotypically with another route, while each route also spans more than one cell.

## Fitness/composition leakage

Maximum absolute Spearman over all preregistered pooled and within-route comparisons:

**0.79594 < 0.90**

Largest pooled relationship was `shape_motion` vs `occupancy_mean` at `-0.79594`. That is substantial correlation and should remain visible as a diagnostic, but it is below the frozen near-equivalence rejection threshold.

Maximum absolute within-route correlations:

- family: 0.2996
- filament: 0.6092
- orbit: 0.2860
- recurrence: 0.6304
- sheet: 0.5611

## Route-level descriptor diagnostics

Median `(anisotropy, central void, shape motion)`:

- recurrence: `(0.786, 0.399, 0.520)`
- orbit: `(0.193, 0.785, 0.341)`
- family: `(0.238, 0.535, 0.124)`
- sheet: `(0.195, 0.512, 0.052)`
- filament: `(0.658, 0.428, 0.591)`

These are descriptive only. They do not rank routes.

## Interpretation

`structural-v1` is adequate to support a first quality-diversity/repertoire allocation experiment:

- it preserves meaningful within-route variation;
- it creates substantial cross-route phenotype overlap;
- it is not near-equivalent to the existing diagnostic/composition objective;
- it remains small enough (64 cells) to reason about explicitly.

The result does **not** rescue #72's unconfirmed trust-region mutator. The next allocator contrast must operate inside the existing route-safe outer budget and use the current/generic search mechanics unless separately tested.

## Next

Preregister a consumed-seed contrast between:

- a baseline inner allocation that spends each route's assigned budget without repertoire guidance; and
- a repertoire-aware inner allocation that preserves phenotype-cell and basin-lineage coverage while respecting the exact same outer route budget and total candidate count.

No descriptor axis/bin may be retuned on these 20 holdout seeds.
