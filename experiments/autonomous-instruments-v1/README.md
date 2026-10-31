# Autonomous instruments v1 — brief contracts and judge-panel tooling

Tooling for two studies proposed in the
[learning-progress review](../../references/learning-progress-review.md), built so
experiments can run with **no human involvement**:

- **CONTRACT-1** turns brief requirements into executable checks over a sketch's
  exact point stream, so adherence is verified rather than judged.
- **JUDGE-1** validates a model judge panel against *fixed points* — pairs whose
  better side is known by construction — before the panel may gate anything.

Everything uses Node.js built-ins and runs on the existing archives. Nothing here
changes a recorded grade, selection, or decision.

## Shared instruments (`lib/`)

| Module | Role |
| --- | --- |
| `runtime.mjs` | Runs a p5.js global-mode sketch in a Node `vm` and records each frame's points in draw order (position, stroke weight, colour, alpha), plus an optional per-point `role`. Every archived readable source uses only `createCanvas`, `background`, `stroke`, `strokeWeight`, and `point`, and is a stateless function of `frameCount`. Refuses sources of the in-flight `compact-representation-v1`. |
| `raster.mjs` | Software raster: `point()` as an anti-aliased disc of diameter `strokeWeight`, composited in draw order. Optional role weights give each cell's colour share per role. Deterministic PNG encoder. |
| `observables.mjs` | Regions, enclosed holes, morphology, lags, and a **non-similarity residual**: the deformation left after the best rotation, uniform scale, and translation. Rigid motion and global scaling score ~1e-14; real deformation scores 0.05–0.12 here. |
| `transforms.mjs` | **Degradations** (density, jitter, freeze, flatten, offset, flicker at three strengths) and **counterfeits** that keep a sketch's look but remove its cause: rotation, sway, scaling, flashing, a travelling stripe, image replacement, rigid halves, fading, a collapsed line, noise, rear-on-top, translucent front. |
| `evidence.mjs` | Judge evidence (16-frame contact sheets; motion sheets of brightness change over 0.1 s) and manipulation checks matched to each degradation (temporal for freeze, spatial otherwise). |
| `contract.mjs` | Contract context and runner, including full-horizon continuity. |
| `judgecard.mjs` | Judge card: position bias, flip consistency, known-answer accuracy by degradation and strength, Cohen and Fleiss κ, panel re-judgment of the October verdicts, and the frozen gate. |

`node --test test.mjs` runs 16 unit tests, including synthetic judges: an oracle,
an always-A judge, and a random judge must produce their known signatures.

## CONTRACT-1 on the archives

Six contracts cover Aperture, Separate, Relay, Reflect, Gather, and Hollow.
[`contracts/coverage.json`](contracts/coverage.json) classifies all **54
requirements of the 13 archived October briefs**: 30 are checkable from points
and rasters alone, 19 more once a sketch declares roles, and **5 need judgment**.
Twenty-four are implemented.

Thresholds were frozen in `b57306e` before the first validation run. Labels are the
October reviewer's own adherence calls, cited in
[`contracts/labels.json`](contracts/labels.json); they are a reference, not ground
truth. Role-dependent Aperture checks use documented shims written after reading
those sources, so they are not blind.

### Frozen run

[`results/contract-validation-v1-frozen.json`](results/contract-validation-v1-frozen.json):

- **Counterfeits: 20/20 rejected**, each by the requirement naming its failure mode
  — rigid halves by `material_deforms`, a translucent front by `opaque_occlusion`,
  random jitter by `coherent_paths`, a collapsed line by `cavity_remains`.
- **Archive labels:** 8/11 brief verdicts and 17/23 requirement verdicts agree.
  Aperture v1, which the October reviewer first passed although its opening never
  closed, fails `aperture_closure`, matching the corrected label.
- **Uncertain cases:** Separate v1 and v4, doubted for "overlapping hollow rings",
  fail `material_lobes` and `material_conserved`. Reflect v1, v2, and v3, doubted
  for faint or unclear reflection, pass every mechanical check: the doubt was about
  legibility, a question for the panel.

### Diagnosed defects and the post-hoc v1.1 repair

The three disagreements were instrument defects:

1. Aperture v3 draws 1-pixel points. At half resolution each covers about 0.2 of a
   cell, so the owner buffer (coverage ≥ 0.5) never saw the rear layer.
2. Closing and eroding role masks bridged small apertures, so adjacent rear and
   front points counted as overlap.
3. Relay measured bending against the frame used to find units, at which some
   units were already mid-pulse. The clean neighbor pairs already showed the true
   lag: 36 measured frames against 37.5 by construction.

v1.1 uses role-weighted compositing, per-pixel overlap at full resolution, and rest
positions as the bending reference. The repairs are labeled in the contract files.

[`results/contract-validation-v1.1-posthoc.json`](results/contract-validation-v1.1-posthoc.json):

- Archive labels: **11/11** brief verdicts and **23/23** requirement verdicts
  agree. Relay's neighbor lags are now 36 frames for all five pairs, with
  correlation ≥ 0.99.
- **Counterfeits: still 20/20 rejected**, including rear-on-top and the
  translucent front. The repair removed the false negatives without loosening
  the test.
- Aperture v3's occlusion check now passes *vacuously*: its visibility-selection
  construction draws almost no rear under the front (0.09% of front pixels). That
  is the right verdict, but it means the check did not test occlusion for that
  construction.

The v1.1 agreement is post hoc: the repairs were informed by the cases they are
re-tested on, so it shows consistency, not validation. The surviving counterfeit
battery is the stronger evidence. The independent test is prospective: contracts
written blind from fresh briefs, frozen before rendering.

## JUDGE-1 tooling

```sh
JUDGE_SEED=<secret> node build-judge-package.mjs --out=PACKAGE --sealed=SEALED
node score-judges.mjs --key=SEALED/key.json --judgments=JUDGMENTS --manifest=PACKAGE/manifest.json
```

The package holds only images and opaque item ids. Each pair is shown in both orders,
with randomized sides and item order. Protections:

- **No recurring images.** A degradation ladder reuses each original many times, so
  every pair draws its sixteen frames at its own random offset. A judge cannot spot
  the recurring original. The two orders of one pair share evidence exactly, which
  keeps the flip test clean.
- **Manipulation floor.** A known-answer pair must visibly differ. In the dry run
  the floor dropped exactly the two no-op pairs: flattening the shading of
  single-coloured sketches.
- **Custody.** The sealed key lives outside the package. The manifest commits
  `sha256(seed)` and `sha256(key.json)`. Unlike a lost prediction file, the key can
  also be recovered by re-rendering the archived sources.

Defaults: ten archived A/B-grade bases across briefs, six degradations at medium
and strong strength, and nine consequential archived pairs (Wake, Thread, Aperture,
Twist ×2, Divert, Weave, Exchange ×2) with the October verdicts sealed for
re-judgment. A two-base dry run built 19 pairs, 38 items, and 26 MB of sheets in
54 s. The full package runs to roughly 250 items, so build it on demand and commit
only its manifest.

[`judge-protocol.md`](judge-protocol.md) is the prompt for judge sessions. Each
judge runs in a fresh session with only the package, using at least two models
and both evidence formats, and commits its `jsonl` before the key is opened.
[`lib/judgecard.mjs`](lib/judgecard.mjs) applies the frozen rule: a distinction
gates only with at least 90% flip consistency and 90% known-answer accuracy; fine
B-versus-B preferences gate only if Fleiss κ ≥ 0.6.

## Limits

- The software raster approximates p5's browser rendering. It is consistent within
  every pair, not byte-identical to Chromium.
- Contracts verify what a brief states mechanically. They cannot judge legibility
  or quality. Five requirements in the coverage map stay with the panel.
- Labels and shims come from the same agent family that made the candidates.
  Agreement with them is consistency, not independent validation. Prospective use
  needs contracts written blind from brief text, in a separate session, before
  rendering.
- A model panel can be validated for consistency and sensitivity. Whether its
  preferences match human taste is outside what an autonomous program can
  establish.

## Reproduce

```sh
node --test test.mjs
node validate-contracts.mjs --out=results/contract-validation.json
JUDGE_SEED=dry-run node build-judge-package.mjs --out=/tmp/judge-package --sealed=/tmp/judge-sealed --bases=2 --levels=3
```

The runtime executes trusted archived JavaScript. It is not a sandbox.
