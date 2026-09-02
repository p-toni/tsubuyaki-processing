# Restart sidecar budget v1 — results

## Decision

**SIDECAR_EIGHT_REQUIRED_FOR_COVERAGE**

The optional baseline-preserving restart sidecar demonstrates a clear mechanical coverage effect on the fresh `759xxx` population, but the existing four-attempt convention does not capture enough of that effect. Under the frozen 90% sufficiency rule, only `k=8` is coverage-sufficient.

This is mechanical compute/coverage evidence only. It does not confer artistic authority on sidecar candidates and does not change baseline search or automatic delivery.

## Protocol

- 20 fresh master seeds × recurrence/orbit/filament = 60 route-seed cells.
- Exact supported baseline first: 20 generated attempts = 10 native + 10 spectral.
- Eight isolated production `restart-sidecar-v1` attempts per route, evaluated as nested phenotype-exact prefixes `k=1,2,4,8`.
- Structural scoring occurs only after target-blind archives and max-dispersion shortlists are frozen.
- 50,000-draw fixed-seed bootstrap at the master-seed level.

All preregistered hard invariants passed.

## Maximum-budget prerequisite

At `k=8`:

- validity: **479/480 = 99.79%**
- mean full-union structural-recovery gain: **+0.03747**; one-sided 95% bootstrap lower **+0.03195**
- mean max-dispersion delivery recovery gain: **+0.03622**; one-sided 95% bootstrap lower **+0.02895**
- mean minimum-pairwise-dispersion gain: **+0.0009691**
- archive and delivery gains are non-negative on recurrence, orbit, and filament.

Every prerequisite gate passes, so budget efficiency is interpretable.

## Budget curve

| attempts/route | archive gain | delivery gain | min-dispersion gain | archive fraction of k=8 | delivery fraction | dispersion fraction | sufficient? |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | +0.01327 | +0.01239 | +0.0001180 | 35.4% | 34.2% | 12.2% | no |
| 2 | +0.01643 | +0.01551 | +0.0003110 | 43.8% | 42.8% | 32.1% | no |
| 4 | +0.02445 | +0.01982 | +0.0006108 | 65.2% | 54.7% | 63.0% | no |
| 8 | +0.03747 | +0.03622 | +0.0009691 | 100% | 100% | 100% | **yes** |

The frozen rule requires at least 90% of the `k=8` gain on all three primary surfaces plus route non-regression. Only eight attempts meet it.

## Route check at k=8

| route | archive gain | delivery gain |
| --- | ---: | ---: |
| recurrence | +0.02744 | +0.02043 |
| orbit | +0.03817 | +0.03880 |
| filament | +0.04679 | +0.04943 |

The mechanical gain is positive across all three routes rather than being carried by one route.

## Interpretation and boundary

For the **optional, isolated** restart sidecar, eight attempts per enabled route are mechanically justified when the goal is to capture the demonstrated coverage/dispersion benefit. Four attempts leave substantial measurable coverage on the table.

Authorized next action: change the optional sidecar's recommended/default enabled budget from 4 to 8, provided that this does not enable the sidecar automatically or change its authority boundary. Sidecar candidates remain outside baseline `SearchState`, cannot parent baseline search, cannot replace baseline delivery automatically, and still require explicit review/handoff for artistic use.
