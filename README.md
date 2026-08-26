# tsubuyaki-processing

A production-oriented Agent Skill for authentic, tweet-sized **#つぶやきProcessing**: compact mathematical systems that render dense organic forms and controllable compound morphology.

## v0.5 — semantic effect validation

v0.4.1 answered **where did a control change the organism?** with dual-state region/subtree masks. A second cold test exposed the next gap: a control can have perfect locality and still do the wrong thing.

v0.5 separates three validation questions:

```text
scope     → where may the control act?
effect    → what observable should change?
survival  → what defining morphology must remain after golf?
```

These are complementary diagnostics, not one optimization score.

## Control contracts

A control can declare both spatial scope and a simple measurable effect:

```json
"finSpan": {
  "region": "fins",
  "scope": "region",
  "effect": {
    "source": "mask",
    "metric": "width",
    "direction": "increase",
    "minRelativeChange": 0.05
  }
}
```

Supported low-dimensional effect observables include region-mask `area`, `width`, `height`, `centroidX`, `centroidY`, and image-space `visibleFraction` / `meanContrast` inside each state's own region support.

The goal is falsification: `finSpan` should fail if it stays local to the fins but changes only fin height.

## Validate where + what

Render baseline and variant at the same frame, plus region masks for both states.

### Scope

```sh
node scripts/check-control-scope.mjs \
  baseline.png variant.png morphology-contract.json finSpan \
  --baseline-mask-dir=baseline-masks \
  --variant-mask-dir=variant-masks
```

Dual-state support prevents legitimate moved geometry from being counted as spill.

### Effect

```sh
node scripts/check-control-effect.mjs \
  baseline.png variant.png morphology-contract.json finSpan \
  --baseline-mask-dir=baseline-masks \
  --variant-mask-dir=variant-masks
```

A useful semantic control should pass both tests and still make visual sense.

## State-aware morphology survival

v0.4.1 introduced feature-wise expanded→golfed survival, but fixed expanded-state feature masks could penalize anatomy that survived while moving during compression.

v0.5 supports separate feature masks for both phenotypes:

```text
expanded-features/
  root.png
  appendages.png
  cavity.png

golfed-features/
  root.png
  appendages.png
  cavity.png
```

The harness exposes `?feature=<name>` for diagnostic feature rendering.

Run:

```sh
node scripts/check-morphology-survival.mjs \
  expanded.png golfed.png morphology-contract.json \
  --expanded-feature-dir=expanded-features \
  --golfed-feature-dir=golfed-features
```

The checker reports feature-wise geometry and appearance instead of one pixel-similarity score:

- area ratio
- width / height ratio
- normalized centroid shift
- contrast / visible-fraction behavior
- special negative-space interpretation for `void` features

This distinguishes **feature moved** from **feature disappeared**.

## Workflow routing

Morphology remains optional:

- abstract dense sheet → base mathematical workflow;
- filament / axial ribbon → legitimate 1D path;
- iterative attractor → dynamical-system path;
- compound anatomy → morphology composition;
- explicitly controllable compound anatomy → scope + semantic-effect validation.

See `SKILL.md` for routing and output requirements.

## Core files

```text
references/morphology-composition.md
references/control-strategies.md
references/control-scopes.md
references/semantic-effects.md
references/evaluation-matrix.md
scripts/check-visual.mjs
scripts/check-control-scope.mjs
scripts/check-control-effect.mjs
scripts/check-morphology-survival.mjs
templates/morphology-contract.json
templates/harness.html
```

## Tweet constraint

The recommended executable form `CODE//#つぶやきProcessing` leaves **259 X-weighted characters for code**. Always verify the complete post:

```sh
node scripts/check-length.mjs post.txt
```

280 is a ceiling, not a target.

## Evaluation stance

Do not collapse these measurements into a single autonomous objective yet. Low spill can be gamed by broad masks; effect thresholds can be gamed by exaggerated geometry; pixel survival can be gamed while aesthetic quality falls.

The intended stack is:

```text
hard correctness gates
+ scope evidence
+ effect evidence
+ feature survival
+ human/agent visual judgment
```

Once these metrics are calibrated across the compound, filament, attractor and abstract-sheet benchmark classes, the repository will be suitable for a continuous keep/revert experiment loop.