# Hybrid portfolio search — results

## Executive result

The hybrid idea is **partially supported**, but neither tested allocation is yet a production winner.

```text
recurrence: H1 reaches the D1 quality frontier, but does not clearly exceed it
family:     hybrid identifies the right basin, but extra generic exploitation does not clearly beat pure breadth
```

The most useful finding is therefore not `H1` or `H2` as a fixed policy.

It is:

> **basin discovery is useful; exploitation needs to preserve the basin's niche rather than broadly mutate away from it.**

## Conditions

All conditions use 40 generated challengers per route.

```text
H1
4 starts x5 = 20 exploration
-> rank basins
-> 20 exploitation candidates in the best basin

H2
4 starts x5 = 20 exploration
-> rank basins
-> 10 exploitation candidates in basin #1
-> 10 exploitation candidates in basin #2
```

H1 and H2 share the same starts and exploration candidates. Only exploitation allocation differs.

The merged D1/B4/B8 experiment remains the baseline.

---

## Recurrence

### Exploration

Viability: **15 / 20**.

Basin ranking was frozen before exploitation:

```text
1. basin 1 — strongest coherent recurrent body
   best: RE-S1-5

2. basin 3 — strongest distinct alternate basin
   best: RE-S3-3

3. basin 4
4. basin 2
```

### H1

The first ten exploitation candidates around RE-S1-5 produced a promoted intermediate. The remaining ten searched around that promoted candidate.

Winner: **RH1-R2-3**.

Compared with the merged D1 winner:

- H1 has richer/denser recurrent material;
- D1 reads more cleanly as one coherent knot;
- neither is a large-margin artistic winner over the other.

Given the selector uncertainty measured in the previous experiment, record:

```text
H1 ~= D1
```

rather than forcing a total order.

### H2

Winner: **RH2-B1-2**.

The ten candidates allocated to basin 3 produced genuinely different long/curved recurrence phenotypes, but none displaced the basin-1 lineage for the current living-knot niche.

Thus:

```text
second-ranked basin preserved optionality
but did not improve the final winner
```

### Recurrence interpretation

The hybrid does recover much of the benefit of depth after spending half its budget on basin discovery. That supports the two-phase architecture at a coarse level.

But with this budget, the 20-candidate exploitation phase does not clearly beat 40-candidate pure depth.

---

## Repeated family

### Exploration

Viability: **18 / 20**.

Basin ranking:

```text
1. basin 4 — materially richer repeated-family grammar
   best: FE-S4-1

2. basin 1 — clean coherent seed-family ring
   best: FE-S1-3

3. basin 3
4. basin 2
```

This independently reproduces the previous breadth experiment's key observation: **basin/start 4 contains leverage that depth from start 1 cannot reach**.

### H1

Winner: **FH1-R2-6**.

Additional depth makes the phenotype denser and more complex, but the family increasingly reads as a single merged botanical cluster rather than a collection of distinct related spores/seeds.

This is not a hard runtime failure. It is a **niche-preservation failure during exploitation**.

### H2

Winner: **FH2-B4-4**.

The second allocation to basin 1 generated clean ring/radial alternatives, but the final H2 winner still came from basin 4.

H2 is the stronger hybrid because it spends less depth walking basin 4 toward a merged morphology. However, it still does not clearly beat the merged B4/B8 pure-breadth winners.

### Family interpretation

The hybrid correctly answers the first question:

> Which mathematical basin deserves more compute?

But our current generic exploitation mutations are not yet good enough at the second question:

> How do we spend more compute **inside this basin without destroying what made the basin good?**

---

## What is supported

1. **Basin ranking is a real useful intermediate decision.**
   - recurrence selects the same type of basin that depth exploited successfully;
   - family finds the same high-leverage basin discovered by pure breadth.

2. **A 20/20 hybrid can recover much of both extremes.**
   - H1 reaches the recurrence D1 frontier;
   - H1/H2 preserve access to the strong family basin.

3. **Exploration breadth does not need to consume the entire budget to reveal useful basins.**

## What is not supported

1. Neither H1 nor H2 clearly beats the best pure strategy on both routes.
2. The second-ranked basin did not produce the final winner on either route.
3. `4 starts`, `20/20`, or `10/10` should not become production constants.

## New bottleneck: exploitation trust region

The failed part of the hypothesis is informative.

Current generic exploitation can mutate:

```text
projection/layout
family count
harmonics
shape law
deformation
time/material
```

That is useful for exploration, but after a basin has already been identified it can be too permissive.

The next search hypothesis should distinguish:

```text
basin exploration
= broad enough to discover structurally different regimes

basin exploitation
= trust-region mutations that preserve the basin's defining relationships
```

For example, after choosing a repeated-family basin, exploitation might lock the family layout / discrete identity and spend depth on:

- latent harmonic values;
- deformation strength/operator variants within the same family law;
- phase relationships;
- material/density;
- bounded projection constants.

Broader structural mutation would unlock only after local exploitation saturates.

That is consistent with the existing progressive-search evidence; the new contribution is **applying that idea at the basin-allocation level**.

## Selector implication

The recurrence H1-vs-D1 and family B4/B8/H2 comparisons are close enough that the current model selector should not be used to manufacture precise ranks.

The previous experiment already found only 2/3 pairwise agreement under a same-model blinded retest.

This strengthens the case for the next planned lever: **selector calibration**, ideally with independent human rankings on the blinded finalist panels.

## Production recommendation

**No production policy change yet.**

Do not encode H1/H2.

The next search experiment, after selector calibration, should test:

> broad basin discovery -> basin ranking -> route-aware trust-region exploitation

against the existing D1/B4/B8/H1/H2 frontier under an equal budget.
