# Orbit historical cold-brief holdout v1 + matched cause ablation

These two evidence layers were run after `orbit-representation-research-v1` was merged. They extend the research record without changing production routing.

## 7. Historical pre-orbit cold-brief holdout

### Question

Does orbit appear naturally in briefs authored before the representation existed, and does adding it steal work from established pre-orbit routes?

### Source rule

Only text committed before orbit was proposed was eligible. Wording was preserved verbatim except that explicit route labels in section headings were removed from evaluator-facing text while retained as sealed metadata.

Historical sources:

- `experiments/search-lab/briefs.json` — blob `381f09c3f657112de95eacc11c43e7bdb14f8d27` (2026-08-26 02:49:14Z): family, living-knot recurrence, dense membrane, filament ribbon.
- `experiments/v014-cold-e2e/protocol.md` — blob `d8c2c1fb8b102827f745308414582a4f919c9507` (2026-08-26 17:11:49Z): tidal living knot, split veil.
- `experiments/breadth-depth-selector/protocol.md` — blob `0614e13bf766624e487df968f39ecd8d6f1af4ea` (2026-08-26 17:34:36Z): `storm organ` recurrence invariants and `drifting spores` repeated-family invariants.
- `experiments/morphology-route-pair/protocol.md` — blob `3ee64351d95bbdbe7730d7caa2db2ec35104e10a` (2026-08-26 19:37:39Z): negative morphology control asking for one compact mathematical generator with emergent organism identity. This source had no assigned subtype among recurrence/family/sheet/filament and is treated as subtype-ambiguous.

The positive morphology control was excluded because the five-arm capacity map does not implement morphology-first scene-graph semantics.

### Frozen design

- 9 historical briefs/specs.
- 8 established-route controls: recurrence ×3, family ×2, sheet ×2, filament ×1.
- 1 historical subtype-ambiguous math-first brief.
- eligible representations: recurrence / orbit / family / sheet / filament.
- fresh deterministic seeds: `359541`, `133902`, `823347`.
- 4 independent viable starts per representation per seed.
- generation is brief-independent and finishes before artistic selection.
- all 60 unique candidates were valid on the first attempt.
- within-route capacity choice is frozen before cross-route comparison.
- five route champions are shuffled globally; route and historical-route metadata stay sealed until all 27 verdicts are recorded.

### Guardrail

The result passes the non-stealing gate only if:

- orbit wins no more than 2/24 established-route blocks; and
- no established-route brief is won by orbit in all 3 seeds.

Orbit performance on the subtype-ambiguous historical brief is observational natural-prevalence evidence, not part of the pass criterion.

### Result

```text
established-route blocks: 24
prior-route wins:         24/24
orbit steals:              0/24
established orbit sweeps:  none

subtype-ambiguous blocks:  3
orbit wins:                3/3
```

Per brief:

```text
search-plankton-family       family      3/3
search-living-knot           recurrence  3/3
search-dense-membrane        sheet       3/3
search-filament-ribbon       filament    3/3
v014-tidal-living-knot       recurrence  3/3
v014-split-veil              sheet       3/3
breadth-storm-organ          recurrence  3/3
breadth-drifting-spores      family      3/3
morphology-emergent-form     orbit       3/3
```

### Interpretation

The clean non-stealing result extends the prior designed-control evidence. More importantly, orbit is selected 3/3 on one genuinely pre-orbit brief that asked for a single compact cause whose organism identity emerges without explicit anatomical parts, but did not prescribe any of the four old mathematical subtypes.

This supports **existence of natural orbit demand** in historical text. It does not estimate how frequent that demand is in arbitrary user traffic.

---

## 8. Matched cause ablation v1

Frozen after the historical holdout result but before ablation rendering or judgment.

### Question

Did orbit win the historical subtype-ambiguous brief because its specific sparse closed recurrent cause fits the request, or merely because a lobed closed silhouette looks attractive/organism-like?

### Subjects

Use the exact orbit winners from the historical holdout; no new search or genome optimization:

- seed `359541`: `OH2`
- seed `133902`: `OH1`
- seed `823347`: `OH3`

### Conditions

At the same matched temporal horizon, derive three render conditions from each exact winning genome:

1. **closed** — intact orbit: sparse closed contour + side structure around the persistent interior void.
2. **gap** — preserve most of the same animated lobed contour but remove a fixed ~14% angular arc, creating visible open ends and breaking closure.
3. **filled** — preserve the same animated outer silhouette but radially fill it into a surface-like body, destroying sparse path/aperture identity.

A/B/C condition identity is shuffled and sealed per seed until all three verdicts are frozen.

### Falsification criterion

The specific closed-sparse cause is supported only if:

- `closed` wins at least 2/3; and
- neither `gap` nor `filled` wins at least 2/3.

### Result

```text
closed: 3/3
gap:    0/3
filled: 0/3
```

### Interpretation

The preference does not survive two matched interventions that preserve much of the outer shape while removing the defining topology/material cause. This weakens a generic silhouette-attractiveness explanation and strengthens the interpretation that closure + sparse one-dimensional material around a void is doing real semantic work for the historical brief.

## Limitations

Both layers still use the same artistic judging process as the earlier orbit studies. They do not replace independent-judge replication. The historical sample is also small and repo-derived, so the 1/9 brief observation must not be turned into a general prevalence percentage.
