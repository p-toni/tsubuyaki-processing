# Representation portfolio development pilot v1 — results

## Headline

The blinded final comparisons were:

```text
portfolio-equal wins: 4
route-first wins:      0
ties:                  4
```

Representation switched away from the frozen route-first heuristic in **4/8** blocks. All four switches produced a blinded portfolio win.

That headline is **not a valid matched-budget policy result**.

## Final block outcomes

| brief | seed | route-first route | portfolio route | blind final |
|---|---:|---|---|---|
| Hollow Tide | 304886 | sheet | family | portfolio |
| Hollow Tide | 910268 | sheet | family | portfolio |
| Braided Weather | 304886 | recurrence | recurrence | tie — exact visible convergence |
| Braided Weather | 910268 | recurrence | recurrence | tie — exact visible convergence |
| Soft Constellation | 304886 | family | family | tie — exact visible convergence |
| Soft Constellation | 910268 | family | family | tie — exact visible convergence |
| Pressure Seam | 304886 | filament | recurrence | portfolio |
| Pressure Seam | 910268 | filament | recurrence | portfolio |

## Critical confound discovered by the pilot

Every final candidate was the first viable start for its representation:

```text
family     FP1
filament   LP1
recurrence RP1
sheet      SP1
```

The conservative deterministic selector promoted no local mutation that mattered to the final policy comparison. The initial eight blocks emitted **436 unresolved phenotype pairs**, of which only **24** were cross-representation; **412** were within-representation ties.

The session resolved only the comparisons needed to determine representation frontiers:

```text
initial cross-route judgments: 24
replay cross-route judgments:   10
forced blinded policy finals:    8
----------------------------------
total visual judgments:         42
```

Therefore route-first's extra local budget was not converted into extra artistic selection evidence. Its 32-attempt arm and the corresponding 8-attempt portfolio arm often ended on the same `P1` phenotype. Portfolio, meanwhile, could gain from cross-representation human judgments.

The causal comparison was consequently asymmetric:

```text
route-first extra local attempts
→ mostly unresolved proxy ties
→ no promotion value

portfolio representation breadth
→ human-resolved cross-route evidence
→ possible representation switch
```

Treating `4-0-4` as evidence that equal portfolio allocation is superior would overclaim the experiment.

## What the pilot does support

Two narrower findings survived the confound:

1. **Representation regret is real enough to measure.** On two of four briefs, both seeds preferred a phenotype from a representation different from the frozen heuristic route.
2. **Representation choice can dominate within-route effort under the current selector.** Hollow Tide switched `sheet → family`; Pressure Seam switched `filament → recurrence`; both switches produced clear blinded final wins.

The no-switch controls are also useful: Braided Weather and Soft Constellation converged to the same visible phenotype under both policies because the heuristic route already matched the portfolio's surviving route.

## What is not supported

Do not infer:

- equal four-route portfolio is a production policy;
- 8 attempts per representation is an optimal split;
- route-first is generally inferior;
- family or recurrence are universally stronger representations;
- current deterministic proxy is adequate for local artistic refinement.

No `SKILL.md` change is justified.

## Next experiment

The pilot says to separate **representation capacity** from **resource allocation**.

Next test:

```text
novel brief
→ equal fixed archive of independent viable starts per representation
→ generation finishes before any artistic selection
→ resolve within-route frontiers
→ compare resolved route champions
→ measure heuristic representation regret + route stability across seeds
```

This is intentionally not a policy comparison. It asks the more fundamental diagnostic question first: **which mathematical representation can best express the brief when each receives equal representational sampling?**

The new `representation_capacity.py` runner implements that boundary with selector-independent archives and representation-local RNG.
