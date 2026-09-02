# Late-refinement human-preference screen v0

## Status

`POST_HOC_HYPOTHESIS_GENERATION_ONLY`

This screen was run only after the `755xxx`, `756xxx`, and `757xxx` human ratings were consumed. It is not confirmatory evidence and must not be used to change search policy without a fresh prospective test.

## Observation

Each of the three prior prospective reviewer populations compared the generation-order `q=0.35` challenger with the `q=0.75` challenger under blinded/randomized A/B orientation.

Across all 72 decisive human judgments:

- `q=0.75` preferred: **45 / 72 = 0.625**
- `q=0.35` preferred: **27 / 72 = 0.375**
- one-sided exact binomial p vs `0.5`: **0.02218546**

By consumed population:

- `755xxx`: **15 / 24** prefer `q=0.75`
- `756xxx`: **14 / 24** prefer `q=0.75`
- `757xxx`: **16 / 24** prefer `q=0.75`

Aggregated by route:

- recurrence: **14 / 24** prefer `q=0.75`
- orbit: **15 / 24** prefer `q=0.75`
- filament: **16 / 24** prefer `q=0.75`

The direction is therefore positive in every population and every route when aggregated across populations.

## Interpretation

This is a much lower-capacity hypothesis than a learned artistic scorer: later within-trajectory challengers may be artistically preferable more often than earlier challengers. The signal could reflect useful local refinement, generation-stage structure, or another correlated property. The retrospective data cannot distinguish those explanations.

No nearby quantile, stage, seed, route, or operator tuning is authorized from these consumed labels.

## Next test

Run one fresh blinded prospective test with the exact same `q=0.35` versus `q=0.75` comparison on untouched `758xxx` seeds. The human reviewer must remain blind to quantile/search stage until all labels are frozen.
