# Search Lab — Representation vs Search

This experiment freezes the v0.6 mathematical representation and asks a narrower causal question:

> How much of output quality comes from the representation itself, and how much comes from search / selection over that representation?

Do not add new semantic-control machinery while this experiment is active. The point is to hold the grammar stable and vary only the exploration policy.

## Hypotheses

- **H1 — representation bottleneck:** one-shot generation is already near the best reachable quality; B/C add little.
- **H2 — parameter-search bottleneck:** B > A, while C ≈ B.
- **H3 — structural-search bottleneck:** C > B > A because interesting phenotypes occupy disconnected structural niches.
- **H4 — route interaction:** morphology-first and math-first win on different brief classes; no universal route dominates.

## Conditions

### A — one-shot

One fresh agent generation from the frozen v0.6 skill. No candidate search after the first valid form.

### B — parameter exploration

Keep the same mathematical structure as A. Search numeric constants only: frequencies, scales, phase rates, integration step, amplitudes, alpha, etc.

No operator / topology / projection-family changes.

### C — structural + parameter divergent search

Use the same v0.6 grammar, but permit structural genes to mutate in addition to numeric parameters:

```text
kernel
latent-coordinate construction
family/residue law
nonlinear deformation operator
projection family
motion coupling
```

C is not allowed to invent a new grammar after seeing results. Structural options are fixed before the run.

## Search objective

Search is **not** allowed to optimize a scalar aesthetic score.

During candidate generation use only:

1. hard validity filters — executes, finite coordinates, no pathological clipping;
2. behavioral descriptors — occupancy, span, centroid, temporal displacement, family count, etc.;
3. novelty / archive coverage — retain candidates that reach new descriptor regions.

Aesthetic quality is evaluated only after candidate generation.

This deliberately separates **exploration** from **judgment**.

## Fixed benchmark briefs

See `briefs.json`. Four classes are used:

1. multi-instance emergent plankton family;
2. recurrent living knot;
3. dense folded membrane;
4. intentional filament / larval ribbon.

These cover the major v0.6 routes without introducing new representations.

## Evaluation

Evaluation is blind to condition whenever practical. Do not show A/B/C labels during preference judgment.

Each candidate is judged independently on:

- **brief adherence** — did it satisfy the requested visual/mathematical intent?
- **aesthetic preference** — would the evaluator keep / publish / explore it?
- **distinctiveness** — is it meaningfully different from nearby candidates and the existing archive?
- **mathematical leverage** — does a small cause create unexpectedly rich structure?
- **temporal quality** — does motion transform the system coherently rather than merely move it?
- **tweet viability** — can its high-leverage structure plausibly survive <=280 weighted chars?

Use pairwise preference for aesthetics where possible. Do not combine the dimensions into one training objective during this phase.

## Full experiment

Target:

```text
4 briefs
× 3 conditions
× 10 independent seeds
= 120 trial outcomes
```

For B/C, each trial may generate an internal population; only the selected finalist enters the 120-outcome comparison.

The evaluator should not know the condition when selecting among finalists.

## Interpretation

- **C >> B ≈ A** → structural search is the best lever.
- **C ≈ B >> A** → parameter exploration is sufficient; avoid building structural search complexity.
- **A ≈ B ≈ C** → representation/model quality is the bottleneck.
- **different winners by brief** → invest in routing / hybrid search rather than a universal generator.

## `pi-autoresearch`

Do not use it to maximize artwork aesthetic score.

A good future role is meta-optimization:

> Does mutation operator X improve quality/diversity across a frozen benchmark?

That is a repository-level keep/revert question. Candidate-level creative discovery remains a population/archive process.

## Pilot

`pilot-results.md` records the first 4-brief A/B/C smoke test. It is evidence about coverage and experimental design, **not** a final result about artistic quality.
