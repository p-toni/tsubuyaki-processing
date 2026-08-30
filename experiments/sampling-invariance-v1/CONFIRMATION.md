# sampling-invariance capacity — fresh confirmation v1

Status: **preregistered before fresh confirmation execution**.

This confirmation follows the positive Stage-B capacity pilot recorded at `research-results/sampling-invariance-capacity-v1/`. It confirms the same narrow claim: under equal independent viable-candidate exposure, does the frozen `bandlimited-k2` representation add structural recovery to the existing five-route portfolio?

It does **not** test a spectral search operator, temporal behavior, or artistic quality.

## Frozen scientific implementation

The confirmation must use the exact Stage-B scientific files that produced authoritative pilot run `33280597919`:

```text
experiments/sampling-invariance-v1/field.py
  git blob 66f59d92ab39379d3a2016d18adbd271827997dd

experiments/sampling-invariance-v1/capacity.py
  git blob fa5aa481ddab9babff17abdf1e4342d7ed74d2a2

experiments/sampling-invariance-v1/aggregate_capacity.py
  git blob bf163da46b3b7728beaa13013d42eadf93d98fae

experiments/sampling-invariance-v1/fast_binary_metric.py
  git blob 7e1c875350050312971d9397091e8708752c0bcd

experiments/sampling-invariance-v1/run_capacity.py
  git blob 4fd07ccd9b548b2537fe86ee3e64914a30fc88bd

experiments/sampling-invariance-v1/validate_fast_metric.py
  git blob ece688dbd8f489c3f6ed03bb55b11dd236eb4f8e

experiments/sampling-invariance-v1/STAGE-B.md
  git blob f9cef9e3c66a0f4161c444d6340d32cd7b32abbb
```

The workflow fails closed if any blob differs. Confirmation-only wrappers may change seed authorization, artifact labeling, and inferential reduction; they may not change scientific generation/scoring semantics.

## Exact reused design

Unchanged from Stage B:

- representations: recurrence, orbit, family, sheet, filament, `bandlimited-k2`;
- `bandlimited-k2`: fixed `K=2`, 25 coefficients / 24 projective geometry DOF;
- coefficient prior and viewport;
- 15 deterministic representation-neutral targets in five families;
- 48 viable independent candidates per representation x seed;
- generation completed before target scoring;
- common binary support rendering at canonical `t=90`;
- frozen `sparse-geometry-v1` distance via its exact-equivalent cached implementation;
- meaningful unique-contribution margin `0.005`;
- portfolio-added estimand and current-route leave-one-route-out baseline;
- no target fitting, mutation search, gradient fitting, or SVD target reconstruction.

## Fresh fixed population

Confirmation uses the first 24 prime integers strictly greater than `61000`, fixed before execution:

```text
61001
61007
61027
61031
61043
61051
61057
61091
61099
61121
61129
61141
61151
61153
61169
61211
61223
61231
61253
61261
61283
61291
61297
61331
```

No replacement, early stopping, or seed addition.

This population is disjoint from Stage A, excluded Stage-B design, and Stage-B holdout seeds.

## Power plan

Inference is clustered at the master-seed level; the 15 targets within a seed are not treated as independent experimental units.

Pilot master-seed field-added recovery:

```text
n = 20
mean = 0.013569752797198934
SD = 0.004212697531025184
min = 0.006184821646702798
max = 0.021669140336317727
```

The pilot aggregate margin over the median current-route mean portfolio contribution was:

```text
0.013569752797198934 - 0.008029389613904217
= 0.005540363183294717
```

The pilot reducer did not persist the paired per-seed baseline-difference SD. To avoid optimistic power accounting, the confirmation design assumes a seed-level paired SD of `0.009`, more than twice the observed field-added seed SD.

For a one-sided alpha `0.05` Student-t test, `n=24`, true margin `0.005540363183294717`, and SD `0.009`, noncentral-t power is approximately `0.90` (`0.8998`).

Therefore the fixed confirmation sample is 24 master seeds.

## Master-seed inference

For each fresh seed, compute:

```text
field_mean(seed)
  = mean fieldAddedRecovery over the 15 targets

current_route_mean_r(seed)
  = mean leave-one-route-out added recovery for current route r over 15 targets

current_median_mean(seed)
  = median_r current_route_mean_r(seed)

paired_added_margin(seed)
  = field_mean(seed) - current_median_mean(seed)
```

Also compute:

```text
field_meaningful_fraction(seed)
  = fraction of 15 targets with field signed delta > 0.005

current_meaningful_fraction_r(seed)
  = analogous fraction for current route r

paired_meaningful_margin(seed)
  = field_meaningful_fraction(seed)
    - median_r current_meaningful_fraction_r(seed)
```

For each continuous master-seed quantity, use the one-sided 95% Student-t lower confidence bound with `df=23` and fixed critical value:

```text
t_0.95,23 = 1.7138715277470473
```

## Confirmation gate

`SAMPLING_INVARIANCE_CAPACITY_CONFIRMED` iff all hold on the complete 24-seed sample:

1. every original Stage-B fresh-sample gate passes unchanged;
2. one-sided 95% lower bound for mean `field_mean(seed)` is > `0.002`;
3. one-sided 95% lower bound for mean `paired_added_margin(seed)` is > `0`;
4. one-sided 95% lower bound for mean `paired_meaningful_margin(seed)` is > `0`;
5. exact frozen-source blob checks and metric-equivalence audit pass.

Report regardless of decision:

- all original Stage-B aggregate diagnostics;
- master-seed mean/median/SD/min/max for the three inferential quantities;
- their one-sided lower bounds;
- per-family and per-target effects;
- current-route contribution baselines;
- archive attempt and uniqueness diagnostics.

## Stop / advance rule

If confirmation fails:

```text
freeze the failed confirmation
→ do not tune K, coefficient prior, viewport, targets, renderer, metric, or archive semantics on these 24 seeds
→ do not build the spectral search operator from this evidence line
```

If confirmation passes:

```text
freeze capacity evidence as confirmed
→ design a spectral mutation/search operator as a new experiment
→ require objective search evidence before any blinded artistic admission study
```

Deterministic arithmetic aliasing and state-dependent exponentiation remain separate hypotheses and may not be injected into this confirmation.
