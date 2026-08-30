# Semantic shape recognition v1

## Purpose

This is the human-authority follow-up permitted by the positive mechanical decision `SEMANTIC_SHAPE_STEERING_MECHANICALLY_PROMISING`.

It asks one direct question:

> Without seeing the target silhouettes, can a human identify which named shape each guided yuruyurau output was asked to resemble?

This is a recognition test, not an aesthetic-quality rating.

## Frozen display sample

One fresh seed per frozen semantic concept, selected and repository-searched before any display output was generated:

| concept | display seed |
|---|---:|
| heart | 126001 |
| star | 126011 |
| crescent | 126019 |
| fish | 126031 |
| butterfly | 126037 |
| tree | 126047 |
| letter-a | 126053 |
| flower | 126071 |

No display seed may be replaced after generation because an output looks unusually good or bad.

For each concept/seed:

1. use the same guided `native-spectral-50-50-v1` search protocol from the mechanical experiment;
2. run recurrence, orbit, and filament from their deterministic hard-valid starts;
3. use frozen sparse-geometry target distance to choose the closest final route champion;
4. render only the resulting t=90 phenotype for human recognition.

The target silhouettes are not included in the review package.

## Blinding

The eight generated images are assigned anonymous panel IDs `A` through `H` using a deterministic shuffle whose mapping is written only to a separate sealed-key artifact.

Review artifact:
- anonymous contact sheet;
- eight individual anonymous panel PNGs;
- instructions containing only panel IDs and the eight allowed concept labels.

Sealed artifact:
- panel ID -> concept;
- concept -> display seed;
- generated route/candidate metadata needed for audit.

The sealed key must not be downloaded or inspected before the reviewer submits a complete one-to-one mapping.

## Reviewer task

Match every panel `A` through `H` to exactly one of:

`heart`, `star`, `crescent`, `fish`, `butterfly`, `tree`, `letter-a`, `flower`.

Use every label exactly once. No quality score or confidence score is required.

## Frozen recognition gate

Decision **`SEMANTIC_SHAPE_RECOGNITION_DEMONSTRATED`** requires at least **6/8 exact matches**.

Otherwise decision is **`SEMANTIC_SHAPE_RECOGNITION_NOT_DEMONSTRATED`**.

The 6/8 threshold was frozen before display generation. Under a uniformly random one-to-one assignment of eight labels, probability of at least six exact matches is `29 / 40320 ~= 0.000719` (exactly seven matches is impossible for a permutation).

This single-reviewer gate is evidence that recognizable identity survives the grammar for this frozen sample. It is not a population-level usability estimate.

## Authority boundary

A pass supports the finite-catalog claim:

> for these named concepts, target-aware search can generate forms whose intended identities are recognizable to the reviewer without showing the target silhouette.

It still does not establish arbitrary open-vocabulary prompt understanding. The mapping from unconstrained language to a useful structural target remains a separate problem.