# Human route-screen selectivity v17

## Question

Can a human reviewer confidently eliminate enough anonymous visual grammars to make all-route probing plus authoritative visual screening computationally useful?

This is a selectivity/UX check, not a routing-accuracy holdout. It reuses the previously frozen v14 anonymous five-group visual grammar atlas.

## Frozen briefs

1. **Split orchard** — one wounded living body with a vertical cleft and small tendril growths.
2. **Open turbulence** — one long narrow trace under tension, compressing into a self-crossing knot and escaping again.
3. **Crowned aperture** — a clear empty center surrounded by irregular living material with repeated rim growths.

The reviewer was asked to mark every anonymous grammar `keep`, `drop`, or `defer`.

## Human response

The compact response named one keep per brief:

```text
split orchard      keep B
open turbulence    keep D
crowned aperture   keep B
```

Because the frozen task required a verdict for every group and the response supplied exactly one keep for each brief, omitted groups were encoded as `drop` rather than invented `defer` votes.

After unsealing:

```text
split orchard      family
open turbulence    recurrence
crowned aperture   family
```

## Frozen utility criteria

- each brief has at least one keep;
- median active routes (`keep + defer`) <= 3;
- at least 5/15 judgments are confident drops.

Observed:

```text
keeps                 3/15
drops                12/15
defers                0/15
median active routes      1
```

**Result: PASS.**

## Interpretation

The human route screen is not merely theoretically safe; on clear briefs it can be extremely selective. That means an architecture which gives every mathematical representation a cheap probe before pruning can still recover most of the deep-search compute savings that motivated semantic top-k routing.

The evidence supports:

```text
brief
→ advisory semantic prior
→ cheap nonzero probe for every representation
→ blinded authoritative visual screen
→ deep search only on kept / unresolved routes
```

It does **not** establish route-screen accuracy on ambiguous briefs, nor does it restore any justification for text-only hard exclusion.
