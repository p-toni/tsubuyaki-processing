# Search Lab Runbook

## 1. Generate candidates

From repository root:

```sh
node experiments/search-lab/search.mjs \
  --brief=plankton_family \
  --regime=C \
  --seed=17 \
  --count=24 \
  --out=_local/search-lab/plankton-C-17.json
```

Regimes:

- `A` — emits the frozen seed genotype only;
- `B` — numeric mutations only;
- `C` — numeric + fixed structural mutations.

Repeat with the same seed for all conditions.

## 2. Render deterministic frames

```sh
node experiments/search-lab/render-genotype.mjs \
  _local/search-lab/plankton-C-17.json \
  plankton_family-C-17-0 \
  _local/search-lab/plankton-C-17-0-f90.png \
  --time=7.5
```

Render at least three representative times for finalists. Use the same times for A/B/C within a brief.

Recommended pilot times:

```text
3.0
7.5
15.0
```

These are mathematical times, not p5 `frameCount` values.

## 3. Hard validity only during search

Candidates may be rejected automatically for:

- non-finite coordinates;
- severe clipping;
- effectively empty render;
- runtime failure.

Do not reject a filament because occupancy is low. Do not prefer a candidate because occupancy is high.

Behavioral descriptors can be used to maintain archive diversity, but never as aesthetic fitness.

## 4. Select finalists

Within B/C, select a small diverse set for review. Selection may use:

- archive novelty;
- hard adherence constraints that can be checked mechanically;
- agent/human review **only after** the generated population is complete.

Do not iteratively change the grammar based on observed candidates during the frozen experiment.

## 5. Blind ids

Before final evaluation, copy finalists to anonymous ids such as:

```text
P-017-A
P-017-B
P-017-C
```

The mapping to A/B/C must be stored separately and hidden from evaluators until scores/preferences are frozen.

Avoid ids containing regime letters in the visible gallery.

## 6. Evaluate

Use `scorecard.md`.

Required dimensions:

- brief adherence;
- pairwise aesthetic preference;
- distinctiveness;
- mathematical leverage;
- temporal quality;
- tweet viability.

Do not sum these into one search objective.

## 7. Reveal conditions and analyze

For each brief/seed record:

```text
winner by pairwise aesthetic preference
brief-adherence deltas
which condition produced the winner
temporal-quality failures
why a candidate was rejected
```

Across all trials compare win rates and dimension-specific behavior rather than only an average score.

## 8. Only golf selected winners

The experiment is about discovery, not minification throughput.

Once a finalist is selected:

1. preserve its high-leverage mathematical cause;
2. compile/golf using the normal skill workflow;
3. verify <=280 weighted chars;
4. check whether the defining phenotype survives compression.

Tweet viability is evaluated before golf; actual length is verified only for winners.
