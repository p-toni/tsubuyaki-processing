# Human-calibrated representation routing — v12→v15

## Why this exists

The earlier semantic-shortlist experiments reported 66/66 containment, but those winners were selected by the same model family later shown to disagree sharply with an independent human judge. This sequence re-tests representation routing with human visual-grammar judgments and records the resulting architecture change.

## v12 — single-exemplar human holdout

Eight briefs reused one fixed phenotype per representation. Human top choice was inside the frozen text-only eligibility set on 5/8 briefs; the broader top-two/acceptable ranking intersected eligibility on 7/8.

This was useful as a falsification of overconfidence but not as a clean representation-capacity test: one phenotype per route confounded route capacity with sample quality.

## v13 — four-exemplar visual grammars

Five anonymous representation groups were each shown through four first-valid independent starts × three temporal frames. The same atlas was reused across ten fresh briefs. The v12 text router was frozen before review.

```text
human top-1 contained: 8/10
mean eligibility size: 2.7
complete top-1 misses: 2/10
```

The two misses were `mouth-in-current` and `closed-scar`; both human judgments selected the `family` visual grammar despite literal text structure suggesting recurrence/orbit-like routes.

This passed the frozen top-1 threshold but did not establish a reliable hard gate.

## v14 — affordance-first router

To avoid phrase→route patching, routing was rewritten as:

```text
brief text
→ structural visual affordances
→ representation capability profiles
→ compact 2–3 route set
```

A new atlas and 12 fresh briefs were frozen. The human answered the first ten. After those ten:

```text
contained:                 6/10
misses:                    4/10
best possible after 12:    8/12
frozen requirement:       10/12
mean eligibility size:     2.42
```

The experiment therefore failed early; the final two ratings were unnecessary. Misses concentrated in hybrid/metaphorical briefs rather than canonical structural briefs.

## Architecture consequence

Text/same-model semantics are retained only as a **prior**. They may order representations or distribute extra cheap probe budget, but they are not allowed to remove a mathematical representation from artistic search.

The safer architecture is:

```text
brief
→ advisory semantic prior
→ nonzero probe exposure for every representation
→ blinded visual route screen
→ hard route elimination only from strong human / independent-model evidence
→ deeper budget allocation
```

If the visual screen is incomplete or conflicting, allocation fails broad rather than collapsing to a semantic top-k.

## v15 prototype policy

`route_allocation_policy.py` encodes that authority boundary. `route_screen_queue.py` produces replay-safe blinded route-level review artifacts from actual probe phenotypes.

Local tests cover:

- every route receives nonzero probe exposure;
- same-model/text-prior evidence cannot hard-prune;
- low-confidence human evidence cannot hard-prune;
- conflicting authoritative evidence defers;
- partial authoritative screens fail broad;
- complete strong human/independent screens may narrow;
- insufficient budget cannot silently fall back to top-k;
- an all-drop screen fails broad rather than producing an empty search;
- route-screen decisions preserve sealed mapping, phenotype fingerprints, provenance, and confidence.

No production `SKILL.md` change is proposed here.
