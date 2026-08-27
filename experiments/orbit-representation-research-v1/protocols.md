# Orbit representation research v1 — frozen protocols

The protocols below are recorded in the order they were frozen/run. Development intervention v1 is explicitly marked non-confirmatory; the later replications were frozen before candidate generation or inspection.

---

## Representation capacity map v1

**Question:** when recurrence, family, sheet, and filament receive equal selector-independent sampling, how often does the brief-first heuristic choose the same representation as blinded artistic evaluation?

**Design:** 8 unseen briefs balanced 2 per frozen heuristic route; deterministic seeds `585826`, `455675`, `838767`; 4 independent viable starts per representation; 24 blocks; identical representation-local RNG streams; generation completes before artistic selection; common bbox target `[0.50, 0.84]`.

**Evaluation:** blinded matched-time strips at `t=30,90,150`; resolve within-route capacity first, then compare route champions with route/heuristic identity sealed. Ties allowed. No code length or diagnostic score enters judgment.

**Primary:** strict heuristic regret. Secondary: heuristic exclusion, 3-seed route stability, representation win matrix, tie rate, validity/attempt counts.

**Guardrail:** measures representation capacity under equal independent sampling, not optimal allocation or search policy.

---

## Representation boundary map v1

**Question:** where are the practical artistic boundaries between recurrence, family, sheet, and filament, and does a small brief shift move the preferred representation in the intended direction?

**Design:** six unordered representation boundaries × two directional variants = 12 briefs; fresh seeds `275350`, `430019`, `768548`; 4 independent viable starts per representation; all four routes eligible; generation completes before artistic selection.

**Primary:** boundary responsiveness and intended-pair containment. Secondary: strict regret, one-sided dominance, off-pair leakage, 3-seed stability, pair-specific asymmetry.

**Guardrail:** this maps boundaries under equal static capacity and does not establish production routing thresholds.

---

## Orbit boundary intervention v1 — development-only

This intervention was prompted by the recurrence↔sheet failure and was **not preregistered confirmatory evidence**.

**Hypothesis:** the failure is caused by a missing topology: a closed 1-D recurrent manifold around a persistent void.

**Intervention:** add experimental `orbit` with closed periodic spine, persistent central aperture, angular coverage around the void, local asymmetric indentation/fold, subtle normal-offset side structure, and temporal phase motion while preserving closure.

**Development success criterion:** on the original boundary seeds, orbit should win recurrence-leaning `Folded Aperture` without displacing sheet on sheet-leaning `Aperture Current`.

---

## Orbit five-arm replication v1

Frozen before candidate generation or inspection.

**Question:** does orbit own a distinct closed-aperture niche without stealing recurrence, sheet, family, or filament briefs?

**Representations:** recurrence, orbit, family, sheet, filament.

**Sampling:** 10 unseen briefs, 2 per semantic niche; fresh deterministic seeds `365728`, `837514`, `275892`; 4 independent viable starts per representation per seed; representation-local deterministic RNG; candidate generation brief-independent; no mutation, adaptive search, racing, or allocation policy.

### Orbit niche

- `closed-pulse` — A sparse closed recurrent loop circling a persistent empty center, with asymmetric folds and coherent breathing motion. It must remain unmistakably a one-dimensional path rather than a membrane.
- `wounded-halo` — A self-returning organic ribbon forming an irregular halo around a void, with one localized indentation and subtle temporal drift. Avoid filled surfaces and open-ended threads.

### Recurrence controls

- `twisted-current` — An open self-crossing recurrent path with loops and returns, spanning the canvas without enclosing a persistent central void. Prefer complex recurrence over a simple axial stroke.
- `folded-stream` — A wandering open recurrent trajectory with layered self-crossings and coherent temporal deformation. It may curl back on itself but should not close into a ring.

### Sheet controls

- `punctured-membrane` — A continuous two-dimensional skin with a central perforation or slit and broad surface folds. The void is embedded in material, not merely encircled by a line.
- `draped-aperture` — A deforming two-dimensional veil around an opening, with row-column continuity, broad surface presence, and coherent temporal folding.

### Family controls

- `budded-crown` — Several sibling tendrils emerge from a shared root mass under one repeated growth law. Preserve obvious family resemblance and distinct anchors.
- `echo-cluster` — A compact living cluster of repeated sibling organs with shared scale and rhythm, visibly derived from one root rather than one continuous path.

### Filament controls

- `tension-stroke` — A sparse elongated one-dimensional filament under tension, with a clear axial direction and coherent bending. Avoid closed loops, membranes, and repeated sibling organs.
- `whip-fold` — A narrow whip-like filament with one or two broad folds and subtle breathing motion. Keep it open-ended and materially sparse rather than recurrently knotted.

**Blinding:** within-route candidate labels shuffled; five route champions shuffled globally; route identity sealed until all 30 verdicts frozen.

**Acceptance criterion:** orbit wins at least 5/6 orbit-niche blocks, including one 3/3 brief, and wins no more than 2/24 non-orbit controls.

**Interpretation:** positive result supports orbit as a first-class research candidate, not a production routing rule. Independent judge remains outstanding.

---

## Orbit boundary replication v1

Frozen before generation or inspection.

**Question:** does orbit occupy stable semantic boundaries against recurrence, sheet, filament, and family, or does it only win easy closed-loop prompts?

**Design:** four orbit pair-boundaries × two directional phrasings; fresh deterministic seeds `375211`, `370687`, `589395`; all five routes eligible so third-route leakage is observable; 4 independent viable starts per representation; fixed brief-independent archives; no mutation/adaptive search.

### Orbit ↔ recurrence

- `returning-knot` [orbit] — A self-returning recurrent line closes around a persistent empty center, with layered folds and asymmetry. It must be one continuous closed trajectory, not an open spiral or membrane.
- `open-knot` [recurrence] — A recurrent trajectory repeatedly curls back toward itself and nearly closes, but remains visibly open-ended with no persistent enclosed center. Prefer layered self-crossing recurrence over a simple stroke.

### Orbit ↔ sheet

- `ringed-aperture` [orbit] — A sparse one-dimensional closed ribbon circles an empty aperture; the boundary itself is the material. Keep the interior empty and avoid broad two-dimensional fill.
- `membrane-eye` [sheet] — A continuous two-dimensional skin surrounds an eye-shaped opening, with broad surface folds on both sides of the void. The aperture is embedded in a sheet, not merely outlined.

### Orbit ↔ filament

- `closed-whip` [orbit] — A narrow whip-like path bends back and seals into an irregular closed halo around a void. Preserve filament thinness while making the topology unmistakably closed.
- `almost-halo` [filament] — A narrow axial whip curves into a near-loop but retains distinct open ends and a clear directional stroke. Do not seal the path into a ring.

### Orbit ↔ family

- `lobed-halo` [orbit] — One continuous closed line forms a lobed organic halo; every lobe is a deformation of the same path, never a separate sibling organ.
- `wreath-buds` [family] — Multiple sibling buds or tendrils emerge under one repeated law from a shared root/body. Repetition should read as separate anchored organs, not lobes of one continuous ring.

**Primary criteria:** intended pair contains winner in at least 22/24 blocks; directional target wins at least 20/24; orbit wins at least 10/12 orbit-leaning blocks; intended non-orbit route wins at least 10/12 opposite blocks.

**Secondary:** each pair flips in at least 2/3 seeds; record third-route leakage and one-sided dominance.

**Interpretation:** passing supports publishing orbit into the research representation set. It still does not justify a production `SKILL.md` routing change without independent-judge replication.

---

## Orbit metaphorical holdout v1

Frozen before generation or inspection.

**Question:** do the five representations, especially orbit, remain separable when ordinary artistic/metaphorical language replaces explicit mathematical topology vocabulary?

**Design:** 10 cold briefs, two per intended niche; fresh deterministic seeds `274316`, `174976`, `251333`; all five routes eligible; 4 independent viable starts per representation; fixed brief-independent archives; no mutation or adaptive search. Prompts avoided route words and explicit terms such as `recurrence`, `sheet`, `filament`, `1-D`, `2-D`, and `aperture`.

**Primary criteria:** intended representation wins at least 26/30 global blocks; orbit wins at least 5/6 orbit-intent blocks; orbit wins no more than 2/24 non-orbit blocks.

**Blinding:** within-route winners selected first; five route champions then shuffled globally with route identity sealed until all 30 global verdicts were written.

**Interpretation:** passing supports language-generalization of the representation niches. It does not substitute for independent-judge replication because the same judging process supplied the artistic verdicts.
