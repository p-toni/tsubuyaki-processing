# Sampling-invariance capacity v1

Decision: **SAMPLING_INVARIANCE_CAPACITY_PROMISING**

The fixed `K=2` sample-invariant bandlimited field adds structural coverage to the existing five-representation portfolio under equal independent viable-candidate exposure. This is a capacity result, not a search-operator or artistic-admission result.

## Evidence

- Authoritative workflow run: `33280597919`
- Aggregate artifact: `9722902487` (`sampling-invariance-capacity-summary`)
- Artifact digest: `sha256:cb0e55e87861f235093341f0afaa73395dba710ee703c63d2adf5552432d6d47`
- Frozen scientific head: `ad837d36dcf2b8ccabbf647e928e4459ebb4f0d4`
- Population: 20 untouched master seeds x 15 fixed representation-neutral targets = 300 seed-target cells
- Representation arms: recurrence, orbit, family, sheet, filament, `bandlimited-k2`
- Exposure: exactly 48 viable independent candidates per representation x seed
- Metric: frozen single-frame binary-support `sparse-geometry-v1`
- No early stopping; no seed replacement; no target fitting.

Before the holdout opened, the cached binary scorer was proven exactly equivalent to the frozen metric on 90 excluded adversarial cases (`maxAbsoluteDifference = 0.0`).

## Preregistered gates

All passed:

1. complete hard-invariant holdout rectangle and equal viable exposure: **PASS**
2. mean field portfolio-added recovery >= `0.002`: **PASS** (`0.013569752797198934`)
3. mean field added recovery > median current-route leave-one-route-out mean contribution: **PASS** (`0.013569752797198934` > `0.008029389613904217`)
4. field meaningful-unique-contribution fraction >= current-route median: **PASS** (`0.44` >= `0.20`)
5. meaningful unique contribution in at least two target families: **PASS** (4/5 families)
6. no single target >35% of total positive contribution: **PASS** (largest `network-2`, `0.1637163676541526`)

All hard invariants also passed: complete seed/cell rectangles, identical representation lists/settings/target suite, and all per-block invariants.

## Primary portfolio-added effect

`field_added = max(0, recovery_bandlimited-k2 - best_current_5_recovery)`

Across 300 seed-target cells:

- mean: `0.013569752797198934`
- median: `0.0`
- SD: `0.018783678537781446`
- min: `0.0`
- max: `0.0839289621857443`
- meaningful unique contribution fraction (`>0.005`): `0.44`

At the master-seed level, mean added recovery was positive for all 20 seeds:

- mean: `0.013569752797198934`
- median: `0.01281550032775782`
- SD: `0.004212697531025184`
- range: `0.006184821646702798 .. 0.021669140336317727`

The signed competitive diagnostic remains negative overall (`mean = -0.05050792172907301`), which is expected for a niche portfolio arm: the field is not a replacement for the current repertoire and loses strongly on structures the existing portfolio already handles better.

## Current-route contribution baseline

Mean leave-one-route-out portfolio contribution on the same 300 cells:

- recurrence: `0.000056020851806776185`
- orbit: `0.008029389613904217`
- family: `0.0`
- sheet: `0.01827741580980741`
- filament: `0.01066203064292535`

Median current-route mean contribution: `0.008029389613904217`.

The new field's mean added recovery (`0.013569752797198934`) is therefore above the median contribution of an already-admitted route on this fixed structural suite.

## Family diagnostics

- concave-loops: mean added recovery `0.02916482369062252`; meaningful fraction `0.9666666666666667`; signed delta `+0.028963452729295215`
- nested-loops: `0.01505735243322951`; meaningful fraction `0.5333333333333333`; signed delta `+0.003974755526882475`
- open-networks: `0.013522713177623677`; meaningful fraction `0.4`; signed delta `-0.00046152287941118956`
- disconnected-loops: `0.010103874684518961`; meaningful fraction `0.3`; signed delta `-0.01524334943785158`
- dense-regions: `0.0`; meaningful fraction `0.0`; signed delta `-0.2697729445842799`

The dense-region family is an important negative control: the experiment did not simply construct a suite that rewards the field everywhere.

## Candidate-generation diagnostics

Every representation had mean unique rendered phenotype rate `1.0`. Mean raw attempts per accepted candidate were essentially one for all arms:

- `bandlimited-k2`: `1.0`
- recurrence: `1.0`
- family: `1.0`
- sheet: `1.0`
- filament: `1.0052083333333335`
- orbit: `1.009375`

The result is therefore not explained by one arm receiving materially more raw generation opportunities to obtain its 48 viable candidates.

## Interpretation

The supported claim is narrow but meaningful: **a finite-information implicit bandlimited geometry provides complementary structural capacity that the current five-route portfolio does not expose under equal independent viable-candidate budgets.**

This does not establish that `bandlimited-k2` should be registered as a production route. It does not validate a spectral mutation/search operator, temporal behavior, or artistic quality. It also does not validate deterministic arithmetic aliasing or state-dependent exponentiation; those remain separate hypotheses.

Per the preregistered Stage-B branch, the next step is to freeze this exact representation, target suite, renderer, metric, and archive semantics and power-plan **one fresh fixed-sample capacity confirmation**. Only if that confirmation passes should a spectral search operator be designed; only after objective search evidence should blinded artistic admission evidence be sought.
