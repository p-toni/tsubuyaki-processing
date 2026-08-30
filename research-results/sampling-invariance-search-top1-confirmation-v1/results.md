# Sampling-invariance top-one search confirmation v1 — result

## Decision

**SPECTRAL_TOP1_SEARCH_CONFIRMED**

Authoritative workflow: `33285217619`  
Aggregate artifact: `9724203949` (`sampling-invariance-search-top1-confirmation-summary`)  
Artifact digest: `sha256:842bc9670568ecd7846de7d7d5cf8de2e3a432e3b596daab5899b214b70d211c`

## Frozen experiment

- 24 fresh master seeds × 15 fresh targets = 360 seed×target cells.
- Fresh target suite is fingerprint-disjoint from both v1 and v2 target suites.
- Exact policy under test:
  - 4 valid independent starts;
  - 8 independent discovery draws;
  - then either 8 additional independent breadth draws or 8 adaptive top-one projective-geodesic events;
  - 20 scored evaluations per policy×target.
- Frozen geodesic angle sequence: `(0.04, 0.08, 0.16, 0.32) × 2`.
- Frozen representation: `bandlimited-k2`.
- Frozen outcome metric: exact-binary equivalent of `sparse-geometry-v1`.

No seed replacement, early stopping, target exclusion, route vote, post-hoc family weighting, or parameter tuning occurred.

## Confirmation gates

| Gate | Result |
|---|---|
| Complete hard-invariant rectangle | PASS |
| Overall mean top1-vs-breadth > 0 | PASS |
| One-sided 95% master-seed lower bound > 0 | PASS |
| Every target-family mean > 0 | PASS |
| Every leave-one-family-out mean > 0 | PASS |
| ≥30% cells exceed +0.005 meaningful margin | PASS |
| Exploitation valid yield ≥0.95 | PASS |
| No family >60% of positive contribution | PASS |

## Primary effect

Across all 360 cells:

- mean `top1_vs_breadth`: **+0.006597**
- median: `+0.006705`
- SD: `0.015733`
- min: `-0.056590`
- max: `+0.049757`
- cells above the preregistered `+0.005` meaningful margin: **56.1%**

At the preregistered independent replicate level (24 master-seed means):

- mean effect: **+0.006597**
- median: `+0.006656`
- SD: `0.007320`
- one-sided 95% Student-t lower bound: **+0.004036**
- range: `-0.012034` to `+0.018930`

Three of 24 seed means are negative, but the complete-sample confidence bound remains clearly above zero.

## Family robustness

Mean top1-vs-breadth effect by fresh target family:

| Family | Mean effect | Meaningful-cell fraction |
|---|---:|---:|
| concave-loops | +0.006115 | 51.4% |
| dense-regions | +0.005549 | 56.9% |
| disconnected-loops | +0.005264 | 56.9% |
| nested-loops | +0.008648 | 56.9% |
| open-networks | +0.007410 | 58.3% |

Every family is positive, including the dense-region controls.

Leave-one-family-out means are also all positive:

- omit concave-loops: `+0.006718`
- omit dense-regions: `+0.006859`
- omit disconnected-loops: `+0.006930`
- omit nested-loops: `+0.006084`
- omit open-networks: `+0.006394`

Largest family share of aggregate positive contribution is only `22.1%`, far below the `60%` concentration ceiling.

## Search diagnostics

- top-one exploitation valid yield: `1.0`
- breadth-tail valid yield: `1.0`
- top-one unique rendered phenotype rate: `1.0`
- accepted improving children across eight geodesic events: mean `2.23`, median `2`

These diagnostics support the mechanism interpretation but do not override the primary gate.

## Interpretation

The objective search policy is now fresh-confirmed:

> **After 12 breadth-discovery evaluations, allocating the final eight evaluations to calibrated adaptive projective-geodesic search around the strongest discovered basin robustly outperforms spending those same eight evaluations on further independent breadth for the fixed K=2 spectral representation under this structural benchmark.**

This resolves the earlier search sequence:

- v1: local geodesic search with insufficient basin discovery did not robustly beat breadth;
- v2: fixed top-two basin hedging diluted the stronger lineage and was rejected;
- fresh confirmation: breadth-first discovery followed by top-one local exploitation is robust on new targets and new master seeds.

## Boundary

This confirms **objective navigability**, not artistic superiority or production-route authority. Do not retune the 12/8 split, angle schedule, bandwidth, prior, renderer, or metric using these confirmation outcomes.

## Next evidence layer

Freeze the confirmed search policy and move to an independent **blinded artistic usefulness/admission test**. That test must hide representation identity, use equal candidate budgets, avoid reference-image/Yuruyurau copying, and keep artistic judgment independent from the structural benchmarks used here.
