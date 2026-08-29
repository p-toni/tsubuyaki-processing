# Basin trust region v1 — result

## Decision

**PILOT_PROMISING.** Freeze the preregistered route partitions and trust-region mechanism and advance them unchanged to one fresh mechanical confirmation.

This is consumed-seed architecture triage only. It does not authorize a production/default change or establish artistic quality.

## Population and invariants

The pilot used 12 master seeds already consumed by #71 across all five route strata, for 60 complete route×seed blocks and two controlled target regimes per block.

All hard invariants passed:

```text
same representative for both exploitation policies    PASS
equal 20-candidate exploitation budgets              PASS
trust-region champion frozen-key drift = 0            PASS
same-basin target frozen-key drift = 0                PASS
identity-jump target crosses identity boundary        PASS
complete 5-route × 12-seed rectangle                  PASS
```

Both generic and trust-region exploitation had mean valid yield `1.0`.

## Primary result

Per complete master seed, effects are equal-route means of:

```text
delta = trust-region normalized improvement
      - generic normalized improvement
```

Aggregate:

```text
same-basin mean seed effect       +0.046880
same-basin median seed effect     +0.055711
identity-jump mean seed effect    -0.087213
mean specificity interaction      +0.134092
```

The interaction is:

```text
same-basin delta - identity-jump delta
```

So the trust region behaves as hypothesized: it helps when the target lies inside the selected basin and becomes disadvantageous when reaching the target requires changing frozen basin identity.

## Preregistered pilot checks

```text
every leave-one-route-out same-basin mean > 0    PASS
mean interaction > 0                             PASS

classification = PILOT_PROMISING
```

Leave-one-route-out same-basin mean range:

```text
+0.028265 .. +0.074632
```

This rules out the aggregate positive result being dependent on any one route stratum.

## Route diagnostics

```text
route        same-basin     identity-jump    interaction
recurrence   +0.076385      -0.096293        +0.172679
orbit        +0.042659      -0.121898        +0.164557
family       +0.058149      +0.027213        +0.030936
sheet        -0.064132      -0.068503        +0.004371
filament     +0.121336      -0.176582        +0.297918
```

Four routes have positive same-basin means. `sheet` is the important exception: its same-basin mean is negative even though the five-route aggregate remains positive under every leave-one-route-out analysis. The fresh confirmation therefore keeps routes as fixed strata and retains the preregistered aggregate/leave-one-route robustness contract; it does not convert route signs into votes or silently tune the sheet partition.

`family` has a positive same-basin effect but only weak specificity because trust-region search also slightly improves its identity-jump control. This remains a route diagnostic, not grounds for post-hoc partition changes before confirmation.

## Seed heterogeneity

Same-basin master-seed effects vary substantially:

```text
mean  +0.046880
SD     0.104491
```

The point estimate is therefore materially larger than the recent mutation-scale effect, but stochastic variation is still large. A fresh fixed-sample confirmation should be sized from this observed seed-level variance rather than reusing an arbitrary seed count.

Using the observed same-basin mean/SD with a one-sided alpha `0.05` directional test and ~80% planning power gives approximately 31 complete master seeds under a normal approximation. Use **32 fresh master seeds** as the fixed confirmation population. The interaction is larger relative to its variance (pilot mean `+0.134092`, SD `0.173223`) and is not the sample-size driver.

## Interpretation

This result supports the architectural distinction that the earlier hybrid search only suggested:

```text
broad discovery
!=
local exploitation
```

Once a basin is selected, generic whole-genome mutation wastes part of the exploitation budget changing dimensions that define a different mathematical niche. Restricting exploitation to route-specific local deformation/detail/time/material dimensions improves recovery of targets constructed inside the basin, while correctly losing leverage on targets that require an identity jump.

That specificity matters. A generic positive delta could simply indicate a better mutation operator. The positive same-basin / negative identity-jump split is evidence for **basin preservation as a mechanism**.

## Next

Preregister one fresh mechanical confirmation with:

- the exact frozen five route partitions;
- exact same broad discovery process;
- exact same target regimes;
- exact same 20-candidate exploitation fork;
- exact same event-keyed RNG scheme;
- 32 fixed fresh complete master seeds;
- no partition or budget tuning;
- no early stopping.

A confirmation should require:

1. a positive one-sided 95% Student-t lower bound for the complete-master-seed same-basin effect;
2. every leave-one-route-out same-basin mean > 0;
3. a positive one-sided 95% Student-t lower bound for the specificity interaction.

If confirmed, stop treating trust regions as a research-only mutation trick and integrate basin identity as an explicit search-state concept. Then test the next architecture layer: preservation/allocation across multiple phenotype-structural niches (repertoire / quality-diversity search). Artistic promotion still requires independent/human evidence.

## Provenance

- PR: #72
- workflow run: `33249133828`
- workflow conclusion: success
- aggregate artifact: `basin-trust-region-summary`
- artifact id: `9713885630`
- artifact digest: `sha256:63b4a35d1fb6a7c30788e127e779f12572baa99924f4739636292ffda34e65b2`
- smoke seed `9001` was infrastructure-only and excluded from analysis.

## Boundary

Mechanistic consumed-seed architecture evidence only. No artistic authority, representation promotion/pruning, production/default change, or `SKILL.md` change.