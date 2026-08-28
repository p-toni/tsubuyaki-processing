# Route-screened adaptive search v1

## Purpose

Wire the human-calibrated route-allocation policy into the actual autonomous discovery search without breaking the evidence chain.

The central invariant is:

```text
what the route reviewer sees
=
what becomes the adaptive search basin
```

A screen is not allowed to choose a representation and then silently regenerate unrelated starts.

## Flow

```text
brief
→ optional semantic prior (allocation/order only)
→ deterministic route-specific probe archive
→ blinded route screen
→ authoritative keep/drop/defer evidence
→ exact source + rendered-phenotype prefix replay
→ safely allocated extra independent starts
→ existing adaptive explore/refine search from those exact starts
```

The experimental orbit arm is explicitly registered before default five-route probing. It remains outside the baseline registry.

## Probe depth

The first human evidence for selective route screening used **four independent exemplars per representation**. Therefore this integration defaults to:

```text
minimum_per_route = 4
```

A lower value is possible for experiments but is explicit and auditable; the runtime never silently assumes one exemplar is sufficient.

For five routes and target depth 10 starts/route:

```text
unscreened breadth             50 starts
4 probes/route + keep 1        26 starts   (48% less)
4 probes/route + keep 2        32 starts   (36% less)
4 probes/route + keep 3        38 starts   (24% less)
```

This is generation count only; reviewer/model inference cost is separate.

## Evidence safety

Before adaptive search begins, every surviving route is regenerated from its deterministic route stream and both are checked:

1. source signature (id/route/basin/genome/check result), and
2. rendered phenotype fingerprint across the reviewed temporal horizon.

Any mismatch fails closed.

`run_search_from_starts` validates that:
- every active route has at least one reviewed start;
- no inactive route is injected;
- start IDs are unique;
- every start owns its basin ID;
- every supplied start remains hard-valid under the active brief.

## Scope boundary

This closes **route-allocation provenance** only.

The downstream adaptive candidate selector remains the existing research proxy unless the caller supplies another selector. The independent-human calibration already showed that same-model/proxy judgments should not be treated as authoritative fine-grained artistic ground truth. Integrating the v3 preference-evidence policy into candidate promotion is the next separate step.
