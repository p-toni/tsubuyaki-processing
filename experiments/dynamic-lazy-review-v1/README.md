# Dynamic lazy evidence review v1

## Question

Does the `K=2` bounded-review policy still preserve the result of eager evidence collection when search is genuinely adaptive — i.e. when an authoritative promotion changes the parent genome and therefore changes later candidate phenotypes?

This is stronger than the static tournament calibration in `lazy-evidence-review-v1`.

## Method

The experiment runs the production `search_engine.run_search` + `EvidenceAuthoritySelector` + v3 review queue/replay loop at the native 400×400 render size.

A deterministic synthetic pairwise oracle resolves temporary review bundles. It deliberately permits ties and non-transitive outcomes. It is only a control for search-policy convergence; it is not artistic preference evidence and is never persisted as such.

Policies compared:

```text
K=1
K=2
K=3
eager / unbounded
```

Scenarios:

```text
single recurrence
single family
paired recurrence + family
```

Seeds: `7`, `19`, `43`.

For every scenario/seed/policy, the search is replayed until no new authoritative review is required. The final comparison fingerprints the complete generated trajectory: candidate ids, routes, basins, parent relationships, stages, genomes, validity, allocation, artistic frontier, provisional champion, and winner.

## Result

All four policies produced the **exact same final candidate trajectory in all 9 blocks**.

| policy | mean ratings | mean review rounds | mean search replays |
|---|---:|---:|---:|
| K=1 | 5.22 | 5.22 | 6.22 |
| K=2 | 5.89 | 3.33 | 4.33 |
| K=3 | 7.44 | 2.78 | 3.78 |
| eager | 10.22 | 2.56 | 3.56 |

Relative to eager, `K=2` used **42.4% fewer ratings**. Relative to `K=1`, it required **36.2% fewer review rounds**.

This independently reproduces the operating-point conclusion from the static calibration under the stronger condition where evidence changes future generation.

## Important failed attempt

An initial attempt reduced canvas size to speed the calibration. It failed because the current recurrence representation contains pixel-scale genes and could not reliably seed a valid candidate at the smaller canvas. That shortcut was rejected. The final experiment preserves the native 400×400 geometry and reduces search depth instead.

A first full-size quick guardrail also took ~183 seconds in CI. The permanent regression was therefore reduced to the minimum search depth that still exercises parent-dependent generation; the complete prototype suite then ran in ~13.9 seconds on GitHub Actions.

## Decision

Keep:

```text
candidate_max_pending_reviews = 2
```

as the screened-search default.

`K=1` remains a useful explicit minimum-rating mode. Eager review remains useful for research/debugging, but its extra speculative ratings are not justified as the default.

No representation-family insufficiency signal was observed by this experiment; it tests evidence scheduling rather than artistic capacity.
