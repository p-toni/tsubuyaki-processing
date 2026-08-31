# Restart cultivation v1 — result

**Decision:** `RESTART_CULTIVATION_NOT_PROMISING`

This experiment tested the remaining maturity loophole after #114: whether independent restart basins are structurally useful but artistically underdeveloped because they reach delivery after only one route-prior draw.

## Fresh three-arm result

20 fresh seeds × 3 routes × 15 targets = **900 paired cells**, with exact 20-candidate compute per arm.

The four-one-shot treatment replicated strongly on fresh seeds:

- archive oneShot-minus-baseline: **+0.0263992**, one-sided 95% lower **+0.0201612**
- delivery oneShot-minus-baseline: **+0.0249315**, lower **+0.0164008**
- every route positive on both surfaces

The cultivated treatment also remained strongly above baseline:

- archive cultivated-minus-baseline: **+0.0211803**, lower **+0.0154297**
- delivery cultivated-minus-baseline: **+0.0230821**, lower **+0.0157417**
- every route positive on both surfaces

But cultivation did **not** preserve the one-shot breadth advantage within the frozen non-inferiority margin:

- archive cultivated-minus-oneShot: **−0.0052189**, lower **−0.0070738**
- delivery cultivated-minus-oneShot: **−0.0018494**, lower **−0.0066370**

The route-level non-inferiority gates also failed, especially filament:

| Route | Cultivated − oneShot archive | Cultivated − oneShot delivery |
|---|---:|---:|
| recurrence | −0.0049615 | +0.0009418 |
| orbit | −0.0025313 | +0.0000256 |
| filament | −0.0081640 | −0.0065156 |

Validity remained high:

- baseline: **98.67%**
- one-shot: **98.58%**
- cultivated: **98.50%**
- restart parents: **99.17%**
- cultivation children: **99.17%**

## Interpretation

The maturity loophole is not supported under the frozen equal-budget test. One small local refinement per new basin does not compensate for giving up two independent basins. The scarce resource in this regime is **basin breadth**, not one-step local maturation.

Together with #112 and #114, the evidence now says:

1. independent starts robustly improve structural discovery;
2. directly substituting them into the supported 20-attempt runtime has not earned artistic authority;
3. preserving spectral refinement fixes the strongest operator-deletion confound but still does not clear the stricter artistic gate;
4. cultivating fewer restart basins sacrifices too much of the breadth advantage.

Per preregistration, automatic restart substitution is stopped. Do not tune restart count, cultivation count, scale, positions, seeds, or margins on consumed `753xxx` evidence.

The evidence-conservative integration endpoint is a **baseline-preserving optional restart sidecar**: the supported baseline search and its three-item delivery remain exactly unchanged, while independent-start discoveries can be generated and surfaced separately when extra exploration is explicitly desired. Baseline non-degradation is then guaranteed by architecture rather than inferred from the structural metric.

## Provenance

- authoritative run: `33433508367`
- frozen scientific head: `2ac23023dd2731ae9c90460ca64178968552f184`
- summary artifact: `9773719424`
- digest: `sha256:79ad992a83ab6c471ef8b34a85e8ab9d48c17b40403cf2c019c7b19c2bf86954`
- individual seed artifacts inspected: **no**
- excluded smoke: `753999`
