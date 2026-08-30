# Sampling-invariance capacity confirmation v1

Decision: **SAMPLING_INVARIANCE_CAPACITY_CONFIRMED**

A fresh fixed 24-master-seed confirmation replicated the positive Stage-B capacity result using the exact frozen scientific implementation. `bandlimited-k2` therefore has confirmed complementary structural capacity under equal independent viable-candidate exposure.

## Evidence

- Authoritative workflow run: `33282503619`
- Aggregate artifact: `9723423972` (`sampling-invariance-capacity-confirmation-summary`)
- Artifact digest: `sha256:f96c528bbae7eabd81f21893cec7cab2f47766cedc44e0bb8f5e3adc6bc0c10c`
- Frozen confirmation head: `45a5ddf26836e38dc96e8e59167bd4e09919d45b`
- Population: 24 fresh master seeds x 15 frozen targets = 360 seed-target cells
- Exposure: exactly 48 viable independent candidates per representation x seed
- Scientific generation/scoring files were Git-blob locked to the Stage-B pilot versions before fresh execution.
- Exact cached metric equivalence re-passed before seed execution.
- No early stopping, seed replacement, target fitting, or holdout-driven tuning.

## Confirmation gates

All passed:

1. complete 24-seed confirmation rectangle: **PASS**
2. every original Stage-B gate replicated: **PASS**
3. one-sided 95% lower bound for master-seed field mean added recovery > `0.002`: **PASS** (`0.012700310418414745`)
4. one-sided 95% lower bound for paired field-added margin vs the current-route median > `0`: **PASS** (`0.006472761113494259`)
5. one-sided 95% lower bound for paired meaningful-contribution margin vs the current-route median > `0`: **PASS** (`0.2074082153866363`)
6. frozen Stage-B source blobs exact: **PASS**
7. metric-equivalence audit exact: **PASS**

Inference is clustered at the master-seed level. Student-t: df `23`, one-sided 95% critical `1.7138715277470473`.

## Master-seed inference

### Field portfolio-added recovery

Mean of the 15 target-level added recoveries within each master seed:

- n: `24`
- mean: `0.014413646281798158`
- median: `0.013561003919459011`
- SD: `0.004897448327199987`
- min: `0.006162260936306755`
- max: `0.023996020207798008`
- one-sided 95% lower bound: `0.012700310418414745`
- preregistered null threshold: `0.002`

### Paired added-recovery margin vs current-route median

For each seed, field mean added recovery minus the median of the five current-route mean leave-one-route-out contributions:

- mean: `0.008586918641751122`
- median: `0.007825161783567314`
- SD: `0.006043168459540849`
- min: `-0.0025855139243798966`
- max: `0.021198870344237272`
- one-sided 95% lower bound: `0.006472761113494259`

One seed can be negative without invalidating the preregistered population-level claim; the clustered lower bound remains clearly positive.

### Paired meaningful-contribution margin

For each seed, field meaningful-target fraction minus the median analogous fraction across current routes:

- mean: `0.24166666666666667`
- median: `0.26666666666666666`
- SD: `0.09792533880807525`
- min: `0.06666666666666665`
- max: `0.5333333333333333`
- one-sided 95% lower bound: `0.2074082153866363`

## Replicated Stage-B portfolio result

Across all 360 fresh seed-target cells:

- field portfolio-added recovery mean: `0.014413646281798158`
- current-route median mean leave-one-route-out contribution: `0.007782076079689072`
- field meaningful unique-contribution fraction: `0.43333333333333335`
- current-route median meaningful fraction: `0.20`
- largest single-target positive-contribution share: `0.16582590573162778` (`concave-1`), below the `0.35` cap
- meaningful unique contribution appears in 4/5 families

The signed field-vs-best-current mean remains negative (`-0.051096828211667854`), which reinforces the intended interpretation: this is a complementary niche arm, not a replacement for the current repertoire.

## Family diagnostics

- concave-loops: mean added recovery `0.030444407615261546`; meaningful fraction `0.875`; signed mean `+0.02814570606102548`
- nested-loops: `0.01735967086679774`; meaningful fraction `0.625`; signed mean `+0.005896396267712916`
- open-networks: `0.013901387589784257`; meaningful fraction `0.3611111111111111`; signed mean `-0.00417344227258587`
- disconnected-loops: `0.010362765337147245`; meaningful fraction `0.3055555555555556`; signed mean `-0.015697026110701482`
- dense-regions: `0.0`; meaningful fraction `0.0`; signed mean `-0.26965577500379034`

The dense-region family again acts as a strong negative control rather than a field-favoring target class.

## Candidate-generation diagnostics

Every representation again had mean and minimum unique rendered phenotype rate `1.0`. Mean attempts per accepted candidate remained effectively one:

- `bandlimited-k2`: `1.0`
- recurrence: `1.0`
- family: `1.0`
- sheet: `1.0`
- filament: `1.0017361111111112`
- orbit: `1.0052083333333333`

## Interpretation

The capacity claim is now confirmed across an independent fresh master-seed population: **a finite-information sample-invariant implicit bandlimited field adds structural coverage that the existing five-route portfolio does not expose under equal viable independent-candidate budgets.**

This still does not admit `bandlimited-k2` as a production route. No spectral mutation/search operator has been tested, no temporal behavior has been established, and no artistic preference evidence exists.

Per preregistration, the next research layer is a **separate spectral search-operator experiment**. It must test whether the confirmed capacity can be navigated efficiently under equal candidate-evaluation budgets before any blinded artistic admission study is justified. Deterministic arithmetic aliasing and state-dependent exponentiation remain separate hypotheses.
