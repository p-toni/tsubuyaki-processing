# Restart sidecar intrinsic-2D budget v1 — result

**Decision:** `SIDECAR_2D_EIGHT_REQUIRED_FOR_COVERAGE`

The fresh intrinsic-2D budget curve confirms that the current eight-attempt exploratory sidecar budget should remain unchanged for both `family` and `sheet`.

No artistic judgment was collected. This is mechanical compute/coverage evidence only.

## Custody and execution

The first excluded smoke run failed before any authoritative `761xxx` seed job opened. The failure was confined to the smoke replay assertion: the experimental delivery hash and production sidecar canonical phenotype hash use different encodings. The assertion was corrected to compare production output against `restart_sidecar._phenotype_hash(...)`; no population, budget, scoring surface, target, gate, or reducer changed.

The corrected runner was re-frozen before execution. The second excluded smoke passed, including exact production API replay for both routes, and only then unlocked the authoritative matrix.

Authoritative evidence:

- 20 fresh master seeds × 2 routes = 40 route-seed cells;
- 320 / 320 maximum-budget sidecar attempts hard-valid;
- workflow run `33701810155` on frozen generation head `dbe969774306f2037f078912b42c5d8a618d1a4b`;
- summary artifact `9873898594`;
- summary artifact digest `sha256:b2a5e613d351296527c04f6e501575752636efbb4dc58bef0b01d4ee7fc60865`.

## k=8 prerequisite replication

All preregistered maximum-budget gates passed:

- sidecar validity: `320/320 = 1.000`;
- archive recovery delta: `+0.0520929`, one-sided 95% master-seed bootstrap lower `+0.0419958`;
- delivery recovery delta: `+0.0278077`, lower `+0.0191883`;
- minimum-pairwise-dispersion delta: `+0.00363106`;
- both routes positive on archive and delivery;
- archive and delivery pooled means exceed the historical meaningful-effect bar `0.003255297955511336`.

The previously observed eight-attempt 2-D effect therefore replicated cleanly on the fresh population.

## Budget curve

| k | Archive gain | vs k=8 | Delivery gain | vs k=8 | Dispersion gain | vs k=8 | Sufficient? |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `+0.0180230` | `34.6%` | `+0.0157217` | `56.5%` | `+0.00102104` | `28.1%` | no |
| 2 | `+0.0298470` | `57.3%` | `+0.0264082` | `95.0%` | `+0.00195642` | `53.9%` | no |
| 4 | `+0.0423179` | `81.2%` | `+0.0297713` | `107.1%` | `+0.00269848` | `74.3%` | no |
| 8 | `+0.0520929` | `100%` | `+0.0278077` | `100%` | `+0.00363106` | `100%` | yes |

The apparent k=4 delivery overshoot is not enough to authorize a smaller budget. The preregistered decision requires simultaneous >=90% retention on pooled archive, pooled delivery, pooled dispersion, and each route's own archive/delivery gain.

## Route-level reason k=4 fails

At k=4:

- `family` archive retains `87.7%` of its k=8 gain; delivery retains `162.9%`;
- `sheet` archive retains only `74.1%`; delivery retains `81.6%`;
- pooled dispersion retains only `74.3%`.

So k=4 fails multiple independent frozen conditions even though pooled delivery is higher than k=8 on this population.

## Consequence

No production change is authorized or needed. The current eight-attempt default for an enabled exploratory sidecar remains supported for the two intrinsic-2D routes, matching the existing eight-attempt requirement for the intrinsic-1D route class.

This closes the exact route-specific sidecar budget-reduction question. Do not tune a nearby lower-budget threshold on consumed `761xxx` evidence.
