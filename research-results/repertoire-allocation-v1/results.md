# Repertoire allocation v1 — consumed-seed pilot

Decision: **PILOT_PROMISING**

This is a consumed-seed mechanical pilot only. It does not change default search behavior or carry artistic authority.

## Frozen comparison

Both arms used the same six starting basin lineages, exactly six current/generic mutation events per basin, the same route/basin budgets, mutation scales, and event-keyed RNG streams. Only parent selection differed:

- `lineage-depth`: mutate the latest valid descendant in the scheduled basin;
- `repertoire-preserving`: mutate the latest candidate from the least-exposed frozen `structural-v1` phenotype niche inside that same basin.

Neither allocator saw the eight-target evaluation portfolio.

## Population

- 16 already-consumed master seeds
- 5 fixed route strata
- 80 complete route×seed blocks
- 36 generated candidates per arm per block
- all hard invariants passed

## Preregistered gate

`PILOT_PROMISING` required all four:

1. complete hard-invariant rectangle;
2. complete-master-seed mean primary delta > 0;
3. every leave-one-route-out primary mean > 0;
4. complete-master-seed mean weakest-target robustness delta > 0.

All four passed.

## Primary target-portfolio recovery

Repertoire-preserving minus lineage-depth, after search:

- mean complete-master-seed effect: **+0.004784948350228155**
- median: `+0.0022263145175047162`
- SD: `0.005879840958679451`
- range: `0.0 .. +0.018282032478731655`
- leave-one-route-out range: **+0.0031958379399869615 .. +0.005459882398476392**

Route means are diagnostic only:

- recurrence `+0.005796865606704369`
- orbit `+0.0021076774685300443`
- family `+0.002085212157235207`
- sheet `+0.0027935965274782258`
- filament `+0.01114138999119293`

Largest route×seed cell: filament / seed 1063, `+0.09141016239365828`.

## Weakest-target robustness

Mean complete-master-seed effect over the four weakest targets:

- mean: **+0.0007000707385478852**
- median: `0.0`
- SD: `0.001250807235409159`
- range: `0.0 .. +0.0036952304916165065`

Every route mean was non-negative; sheet was nearly zero (`+0.000072973094477459`).

## Mechanism diagnostics

The result is **not** explained by greater terminal niche counts or rendered uniqueness:

- occupied niches: lineage `3.825`, repertoire `3.825`
- unique rendered phenotypes: lineage `41.15`, repertoire `41.15`
- unique phenotype rate: identical `0.980952380952381`
- valid yield: identical `0.9986111111111111`
- new-niche children: lineage `1.9`, repertoire `1.875`
- basin×niche slots: lineage `7.9`, repertoire `7.875`

So the supported pilot claim is narrower: **changing which niche history receives the next mutation improved later recovery of unseen target phenotypes under equal compute, even though simple terminal diversity counts did not increase.** This may reflect more useful branching geometry rather than more archive cells. Do not post-hoc relabel or tune the allocator from these diagnostics.

Target-level diagnostics were sparse/zero-inflated: local target deltas had mean `+0.0059377`, global target deltas mean `+0.0013266`; medians were zero. These are diagnostics only.

## Fresh confirmation plan

Robustness variance is the sample-size driver. A one-sided alpha=.05, ~80% normal approximation gives roughly 20 master seeds from the pilot robustness mean/SD. Freeze **24 fresh master seeds** for confirmation to give margin for Student-t uncertainty and zero inflation.

The allocator, target portfolio, metric, budgets, parent-selection rule, and route strata must remain unchanged. Fresh confirmation should require:

1. primary complete-master-seed one-sided 95% Student-t lower bound > 0;
2. every leave-one-route-out primary mean > 0;
3. weakest-target robustness complete-master-seed one-sided 95% Student-t lower bound > 0.

With n=24, df=23, one-sided 95% critical value is `1.713871527747048`.

## Provenance

Workflow run: `33257413808`

Sealed aggregate artifact: `9716996225`

Artifact digest: `sha256:18be7ab394cc79b21fd375d68436fba216d5ae33977784f2f2edbcc83c4c961e`

Experimental head: `5d46aa73f4e50af092b23238d0be36f15f048199`
