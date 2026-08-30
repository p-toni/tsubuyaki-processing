# Semantic perceptual steering v1

## Why this exists

`semantic-shape-steering-v1` established a narrow mechanical fact: sparse geometric target distance can steer the mixed intrinsic-1D runtime toward a frozen target. The subsequent blinded human review did **not** establish semantic recognition. The reviewer confidently named four anonymous panels and all four names were wrong under the sealed key; the preregistered forced-choice gate was unscorable because the completion reused panels.

The follow-up therefore changes the **objective representation**, not the search budget or operator portfolio.

Question:

> Does a target representation that preserves global perceptual structure and prototype discriminability produce outputs that are mechanically more recognizable than the old sparse-geometry selector, at the same search budget?

A positive result is still not authority for `looks like X`; it only authorizes another blinded human recognition test.

## Intervention

Baseline: `target-geometry-steering-v1`, the frozen sparse-geometry selector from the previous experiment.

Candidate: `prototype-perceptual-steering-v1`.

Both arms use:

- intrinsic-1D routes only: recurrence, orbit, filament;
- confirmed `native-spectral-50-50-v1` mutation portfolio;
- one shared hard-valid start per route;
- 4 explore + 4 round-A + 12 refine challenger attempts per route;
- exactly 20 challengers per route = 60 per concept/arm;
- exactly 30 native + 30 spectral attempts per concept/arm;
- identical start genomes and identical deterministic search RNG partitions.

Only the pairwise semantic objective and final route chooser differ.

## Perceptual prototype representation

Every candidate and target is first normalized by support bounding box: translation and isotropic scale are removed while orientation and aspect ratio are preserved. A 96x96 centered field is then described by seven equally weighted blocks:

1. multiresolution spatial mass at 32x32, 16x16, and 8x8;
2. horizontal and vertical projection distributions;
3. radial-angular occupancy (4 radial bands x 16 angular sectors);
4. 12-bin stroke-orientation histogram;
5. 24-bin outer radial profile;
6. vertical, horizontal, and 180-degree symmetry errors;
7. robust coarse topology: foreground components, holes, and aspect deviation.

No learned model or human rating enters the metric.

For requested concept X, the selector compares the candidate against **all eight frozen prototypes**. Ranking is lexicographic:

1. candidate whose nearest prototype is X beats one whose nearest prototype is not X;
2. then lower perceptual distance to X;
3. then larger X-vs-next-best prototype margin.

This explicitly rejects the previous failure mode where a generic curve can become somewhat closer to X while remaining equally or more compatible with another concept.

## Metric calibration before fresh outcomes

Before smoke or consumed search, the metric must pass a target-only calibration on both the previous eight prototypes and the new eight prototypes.

Each prototype is tested under six identity-preserving transforms combining:

- isotropic scale 0.80 or 1.00;
- rotation -3, 0, or +3 degrees;
- small translations for scaled variants.

Calibration requires:

- 100% top-1 recovery for previous prototypes;
- 100% top-1 recovery for fresh prototypes;
- minimum prototype margin > 0.05 in both suites;
- all scores finite.

Failure => `PERCEPTUAL_PROTOTYPE_METRIC_INVALID`; no consumed search is authorized.

## Fresh concepts

Exactly eight new prompt labels, disjoint from the previous semantic suite:

- `diamond`
- `spiral`
- `lightning`
- `leaf`
- `umbrella`
- `crown`
- `letter-s`
- `sailboat`

They are deterministic 400x400 line/skeleton prototypes and must pass the existing support/span contract, have distinct fingerprints, and be image-fingerprint-disjoint from every prior structural and semantic target suite.

## Fresh seeds

Repository search for prefix `7319` returned no prior occurrences before preregistration.

Excluded smoke seed: `731899999`.

Consumed master seeds:

`731900011, 731900027, 731900039, 731900057, 731900081, 731900103, 731900119, 731900143, 731900157, 731900181, 731900207, 731900229`

No consumed seed may be reused to tune descriptors, target geometry, budgets, gates, or selector ordering.

## Evidence rectangle

`12 seeds x 8 concepts = 96` paired blocks.

Each block generates three baseline route trajectories and three perceptual route trajectories. The baseline final route is chosen by the old sparse target distance. The perceptual final route is chosen by the new prototype ranking.

## Held-out mechanical recognition proxy

The selection descriptor is not used as the primary comparison outcome.

A separate normalized multiscale support-F1 evaluator compares each final output against all eight prototypes using dilation radii 2, 4, and 7 on normalized support. For each final output it records:

- target F1;
- best-other F1;
- target-vs-best-other margin;
- whether the requested prototype is held-out top-1.

This remains a geometric proxy; human recognition is still final authority.

## Excluded smoke

For all eight concepts, smoke must establish:

- identical starting genome and phenotype across arms;
- exact 20 attempts/route/arm;
- exact 10 native + 10 spectral attempts/route/arm;
- valid final champions;
- deterministic exact replay of the perceptual arm;
- perceptual selector never promotes invalid over valid;
- all reported scores finite.

## Preregistered advancement gate

Decision `PERCEPTUAL_SEMANTIC_STEERING_MECHANICALLY_PROMISING` requires all:

1. complete hard-invariant 96-block rectangle;
2. exact equal 60-vs-60 budget and 30/30 operator allocation in every block;
3. mean perceptual-minus-baseline held-out target F1 >= +0.025;
4. one-sided 95% lower bound over 12 master-seed mean F1 deltas > 0;
5. mean held-out prototype-margin delta > 0;
6. one-sided 95% lower bound over 12 master-seed mean margin deltas > 0;
7. perceptual held-out requested-top1 fraction >= 0.60;
8. perceptual-minus-baseline held-out top1 improvement >= +0.20;
9. perceptual selection-metric requested-top1 fraction >= 0.70;
10. at least 6/8 concepts have positive mean held-out target-F1 delta;
11. at least 5/8 concepts have perceptual held-out top1 fraction >= 0.50;
12. no concept supplies >35% of total positive F1 improvement.

One-sided t critical for df=11 is frozen at `1.795884819`.

Any failure => `PERCEPTUAL_SEMANTIC_STEERING_NOT_READY`.

## Diagnostic interpretation

If the new selector reaches high selection-metric top1 but low held-out top1, the perceptual metric is still construct-invalid.

If both selection and held-out top1 remain low, the likely bottleneck is current grammar/search capacity rather than the old objective alone; do not tune weights on consumed seeds.

If the full gate passes, generate a fresh blinded human package with separate display seeds. The first human pass must be spontaneous/free-label recognition before any concept list is shown; only afterward may a forced-choice list be used. Human recognition remains the sole authority for `ask for X -> it looks like X`.
