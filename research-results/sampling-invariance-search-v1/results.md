# Sampling-invariance search v1

Decision: **SPECTRAL_SEARCH_NOT_PROMISING**

The calibrated projective-geodesic operator is locally useful, but the preregistered single-lineage adaptive search does **not** robustly beat equal-budget independent breadth across target families. This is a search-topology failure, not evidence against the confirmed representation capacity or against the mutation geometry itself.

## Evidence

- Authoritative workflow run: `33282969465`
- Aggregate artifact: `9723541443` (`sampling-invariance-search-summary`)
- Artifact digest: `sha256:35451ac61052601e4bf6ef6f07fc5eef7c91d6799894ce9f8465f75dff1fb138`
- Frozen scientific head: `7f0d96f1355f89d9c1c91d97a6775be77b8dc13e`
- Population: 20 consumed master seeds x 15 frozen structural benchmark targets = 300 seed-target cells
- Policies: independent breadth, fixed-parent geodesic, adaptive geodesic
- Budget: exactly 4 shared valid starts + 16 incremental evaluations = 20 scored evaluations per policy x seed x target
- Frozen calibrated angles: `0.04, 0.08, 0.16, 0.32` radians repeated four times
- Metric: exact binary equivalent of frozen `sparse-geometry-v1`
- No invalid-candidate replacement, early stopping, restart, target fitting, or holdout-driven tuning.

## Preregistered gates

1. complete hard-invariant rectangle: **PASS**
2. mean adaptive vs independent breadth > 0: **PASS** (`0.001213541399666246`)
3. every leave-one-family-out adaptive-vs-breadth mean > 0: **FAIL**
4. mean adaptive vs fixed-parent > 0: **PASS** (`0.009803789123177935`)
5. >=30% cells have adaptive-vs-breadth > `0.005`: **PASS** (`0.44666666666666666`)
6. adaptive incremental valid yield >= `0.95`: **PASS** (`1.0`)
7. no family >60% of positive adaptive-vs-breadth contribution: **PASS** (max `0.25787661600854517`)

The only failed gate is cross-family robustness.

## Primary effects

### Adaptive geodesic vs independent breadth

Across 300 cells:

- mean: `0.001213541399666246`
- median: `0.002385860078604307`
- SD: `0.024427210498832626`
- min: `-0.10851440769373422`
- max: `0.06782292613466923`
- meaningful (`>0.005`) fraction: `0.44666666666666666`

The positive average is small relative to the cell-level variance and is not family-robust.

Leave-one-target-family-out means:

- omit concave-loops: `0.0005006512085515225`
- omit dense-regions: `0.0015070036388436236`
- omit disconnected-loops: `0.00245741781311532`
- omit nested-loops: **`-0.00020771334715955584`**
- omit open-networks: `0.0018103476849803193`

Nested-loop performance is therefore necessary to keep the aggregate adaptive-vs-breadth effect positive.

### Adaptive geodesic vs fixed-parent geodesic

- mean: `0.009803789123177935`
- median: `0.007678246204467942`
- SD: `0.014563386476406714`
- min: `-0.04976628681472439`
- max: `0.07123437856940706`

Adaptive parent updates beat fixed-parent mutation on average in **every target family**:

- disconnected-loops: `+0.011739527714413967`
- concave-loops: `+0.01162451893986886`
- open-networks: `+0.010848479363756602`
- dense-regions: `+0.007770847080656005`
- nested-loops: `+0.007035572517194237`

This is strong evidence that the calibrated projective mutation and objective parent updating provide genuine local search leverage.

### Adaptive gain from the shared initial starts

- mean: `0.031177753540076902`
- median: `0.026311537367004423`
- SD: `0.02157532430803123`
- min: `0.0`
- max: `0.11037967320596853`

So the adaptive search is not inert: it substantially improves its starting basin. The problem is that independent breadth often discovers a better basin within the same total evaluation budget.

## Family diagnostics: adaptive vs breadth

- nested-loops: mean `+0.006898560386969453`, meaningful fraction `0.5666666666666667`
- concave-loops: `+0.00406510216412514`, meaningful fraction `0.5166666666666667`
- dense-regions: `+0.000039692442956734686`, meaningful fraction `0.35`
- open-networks: `-0.001173683741590048`, meaningful fraction `0.38333333333333336`
- disconnected-loops: `-0.0037619642541300495`, meaningful fraction `0.4166666666666667`

Positive contribution is not concentrated in one family: largest share is nested-loops at `0.25787661600854517`.

## Search-quality diagnostics

- adaptive incremental valid yield: `1.0`
- fixed-parent incremental valid yield: `1.0`
- independent-breadth incremental valid yield: `1.0`
- adaptive unique rendered phenotype rate: `1.0`

Therefore the failure cannot be explained by invalid/no-op mutation tax or rendered duplicate collapse.

## Interpretation

The confirmed capacity remains intact. This pilot establishes a narrower result about search mechanics:

> **Projective geodesic mutation is locally navigable, and adaptive parent updates are useful, but committing all incremental budget to one greedily improving lineage is not robustly better than independent resampling of the spectral prior.**

The most plausible failed assumption is **single-basin allocation**. The data argue against blaming mutation scale: all calibrated angles had perfect valid/distinct yield, adaptive search beats fixed-parent mutation in every family, and adaptive search gains substantially from its initial candidates. What it lacks is reliable access to better basins.

Per preregistration, the exact operator/single-lineage policy will not be tuned on these consumed seeds. The next materially distinct hypothesis should combine global basin discovery with local projective exploitation—for example a repertoire-preserving or multi-parent spectral search that spends part of the fixed budget on fresh basins and part on geodesic refinement. That experiment requires new consumed seeds and a frozen allocation policy before outcome inspection.

No blinded artistic admission is justified yet.
