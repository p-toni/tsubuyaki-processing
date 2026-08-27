# Representation portfolio development pilot v1

**Status:** protocol frozen before candidate generation.

## Question

Can delaying representation commitment through an equal four-route portfolio reduce artistic regret relative to a route-first heuristic under the same candidate-attempt budget?

This is a **development pilot**, not confirmatory evidence. No production policy change is allowed directly from this block.

## Policies

Per brief + seed, both policies receive exactly **32 candidate attempts**.

```text
route-first
→ all 32 attempts in brief.route_first

portfolio-equal
→ 8 attempts each in recurrence / family / sheet / filament
```

Each arm requests two viable starts. Representation-local deterministic RNG from the merged portfolio prototype is used.

## Primary outcome

Blinded final artistic preference:

```text
route-first finalist vs portfolio-equal finalist
→ A / B / tie
```

Policy identity is sealed until final judgments are recorded.

## Secondary outcomes

- representation-switch rate;
- judgment count;
- invalid-candidate count;
- unresolved-frontier behavior.

## Frozen seeds

```text
304886
910268
```

## Frozen briefs

### Hollow Tide — heuristic route: sheet

> A single pale living form with a persistent hollow center, broad but not flat, slowly opening and recoiling. Asymmetry, internal tension, and a sense of soft material matter more than anatomical readability or decorative repetition.

### Braided Weather — heuristic route: recurrence

> A single elongated organism-like presence that seems to braid through itself, with persistent internal crossing and slow lateral breathing. It should feel volumetric and alive rather than like a plotted mathematical curve.

### Soft Constellation — heuristic route: family

> A coherent living cluster with repeated echoes around a denser center, but no literal flower, tentacles, or named body parts. Related forms should feel genetically connected without mechanical repetition, drifting as one organism.

### Pressure Seam — heuristic route: filament

> A restrained elongated living seam that buckles, widens, and briefly suggests an opening or cavity. It should stay spare but not merely linear, with visible tension and motion traveling along its length.

All four representations are eligible for every brief. Composition target is `[0.50, 0.84]` dominant canvas span.
