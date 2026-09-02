# Restart sidecar 2-D route-scope v1 — result

**Decision:** `SIDECAR_2D_SCOPE_MECHANICALLY_SUPPORTED`

This experiment tested whether the baseline-preserving eight-attempt independent-start sidecar, previously authorized only for the intrinsic-1D routes, produces mechanically useful coverage on the incumbent intrinsic-2D `family` and `sheet` routes.

No artistic judgment was collected. Production route authority remained unchanged throughout generation and scoring.

## Frozen evidence

- 20 authoritative fresh `760xxx` master seeds × 2 routes = 40 route-seed cells.
- 20 native-only baseline attempts per route-seed.
- 8 isolated sidecar attempts per route-seed.
- 320 / 320 sidecar attempts hard-valid (`1.000` validity rate).
- Mean distinct valid phenotypes added per route-seed: `8.0`.
- Complete baseline archive/state remained byte-stable across sidecar generation.
- Target construction/scoring occurred only after baseline and union archives/deliveries were fixed.
- Summary artifact: `9865933211`, digest `sha256:9a943940df1de9dd902b4c1ae4ae6cf374b836c5377b2e06948bd277aac77ce4`.
- Authoritative workflow run: `33680028709`, generation head `1d65fec4fa18f1ac0d4483dc7574eab035e46b1e`.

## Primary results

| Surface | Mean delta | One-sided 95% master-seed bootstrap lower | Gate |
| --- | ---: | ---: | --- |
| Full-archive structural recovery | `+0.0453416` | `+0.0383411` | pass |
| Target-blind max-dispersion delivery recovery | `+0.0238662` | `+0.0152194` | pass |
| Minimum pairwise delivery dispersion | `+0.00365073` | — | pass |

The preregistered historical meaningful-effect bar for archive and delivery recovery was `0.003255297955511336`; both pooled means exceed it substantially.

## Route-level non-regression

| Route | Archive delta | Delivery delta | Dispersion delta |
| --- | ---: | ---: | ---: |
| `family` | `+0.0369722` | `+0.00490496` | `+0.00533152` |
| `sheet` | `+0.0537109` | `+0.0428275` | `+0.00196994` |

Both routes are positive on every reported surface. The preregistered gate required positive route-specific archive and delivery means; both pass.

## Gate resolution

All preregistered conditions passed:

- pooled sidecar validity >=95%;
- archive mean above the historical meaningful-effect bar;
- archive one-sided bootstrap lower bound >0;
- delivery mean above the historical meaningful-effect bar;
- delivery one-sided bootstrap lower bound >0;
- pooled minimum-pairwise-dispersion delta >0;
- `family` and `sheet` archive means >0;
- `family` and `sheet` delivery means >0.

## Authority consequence

This result authorizes one narrow follow-up integration: add `family` and `sheet` to the **opt-in exploratory restart-sidecar route authority**.

It does **not** authorize:

- enabling the sidecar by default;
- allowing sidecar candidates into baseline `SearchState`;
- allowing sidecar candidates to parent baseline search;
- allowing automatic replacement of baseline delivery;
- any artistic-quality claim or artistic promotion.

The next integration should change only the explicit route-authority boundary and its regression coverage while preserving all existing sidecar isolation invariants.
