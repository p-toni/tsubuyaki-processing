# Search Lab Pilot — 4-brief smoke test

Status: **experimental / not a release benchmark**.

This pilot was run immediately after the epistemology review to test whether the A/B/C split produces materially different search behavior before investing in a 120-outcome study.

## Setup

Frozen representation: v0.6 math grammar.

Conditions:

- **A:** one baseline genotype;
- **B:** numeric parameter mutation only;
- **C:** fixed structural options + numeric mutation.

For B/C, candidate retention used only hard validity + simple behavioral novelty. No aesthetic score was used for search.

Four broad topologies were tested:

- plankton family;
- recurrent living knot;
- dense membrane;
- filament ribbon.

B/C attempted to retain 12 behaviorally distinct valid candidates per brief. The filament B condition only found 6 under the pilot novelty threshold, which is itself evidence of a narrower reachable neighborhood.

## Behavioral coverage

Mean pairwise distance in a simple descriptor space `(occupancy, width span, height span, centroid x/y)`:

| brief | B parameter only | C structural + parameter | C / B |
|---|---:|---:|---:|
| plankton family | 0.1370 | 0.3964 | **2.89×** |
| living knot | 0.1461 | 0.2551 | **1.75×** |
| dense membrane | 0.1375 | 0.1933 | **1.41×** |
| filament ribbon | 0.0507 | 0.2288 | **4.51×** |

This is evidence for **coverage**, not artistic superiority.

C also reached much wider span/occupancy ranges. In the plankton family, for example, C ranged from ~1.6% to ~10.2% occupancy and ~50% to full-canvas width, while B remained in a substantially tighter neighborhood.

## Qualitative observations

### Plankton family

A/B mostly preserve the same constellation-of-small-bodies phenotype. C discovers qualitatively different regimes: spiral colonies, looped repeated bodies, sparse phase families, denser organic clusters, and several forms that no longer look like simple parameter neighbors.

Preliminary interpretation: **strong evidence that structural genes expose disconnected niches**.

### Recurrent living knot

B mostly changes scale/density/spacing of the same recurrent family. C creates noticeably different colony organizations and projection behavior.

Preliminary interpretation: **structural projection/family choices matter beyond recurrence constants**.

### Dense membrane

C improves diversity less dramatically than in the other classes. Parameter search already moves meaningfully around the folded-sheet neighborhood, while structural changes produce bilateral/shell alternatives.

Preliminary interpretation: this may be a class where **B captures a larger fraction of useful variation**.

### Filament ribbon

C creates far more diversity than B, but several structurally novel outputs drift from the intended "long axial ribbon" brief into loops/radial flowers.

This is the most important methodological finding of the pilot:

> structural search can appear to win by leaving the task.

Therefore prompt/brief adherence must be evaluated independently from novelty and aesthetics.

## What the pilot does **not** establish

It does not establish C > B > A in artistic quality because:

1. the first gallery used condition-revealing ids (`A0/B*/C*`), so aesthetic review was not truly blind;
2. only one seed per brief was used;
3. frames rather than full motion were primarily inspected;
4. structural search occasionally exploited under-specified adherence boundaries;
5. no pairwise preference protocol was frozen before viewing results.

These are experiment-design defects, not reasons to discard the coverage signal.

## Changes required for the full run

1. anonymous finalist ids;
2. adherence criteria frozen in `briefs.json` before generation;
3. representative animation frames / motion review for every finalist;
4. pairwise aesthetic preference using `scorecard.md`;
5. 10 independent seeds per condition/brief;
6. no modification to the v0.6 grammar during the experiment;
7. archive novelty used for exploration only, never as the final quality objective.

## Pilot conclusion

The first evidence supports continuing the experiment.

Structural search clearly expands reachable behavior, often dramatically. The unresolved question is the important one:

> Does that additional coverage contain more **brief-adherent, aesthetically preferred, mathematically leveraged** outcomes, or merely more different outcomes?

That is what the full A/B/C experiment should measure.
