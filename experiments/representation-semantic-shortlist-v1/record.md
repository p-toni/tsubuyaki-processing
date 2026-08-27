# Representation semantic shortlist v1

Frozen brief-only two-route eligibility test over the five research representations: recurrence, orbit, family, sheet, filament.

## Question

Can a two-representation shortlist chosen before rendering contain the exhaustive five-arm artistic winner on ambiguous ordinary-language prompts?

## Result

```text
briefs:                    12
fresh seeds:                3
blocks:                    36
starts per representation:  1
shortlist containment:     36/36
briefs with 0/3:            0
3/3 winner stability:      12/12
```

Every exhaustive winner was inside the frozen top-2. The experiment therefore supports semantic eligibility as a research hypothesis, but the single-start design does not establish robustness to within-route capacity.

No production policy change follows from this run alone.

---

# Frozen protocol

Frozen before candidate generation or inspection.

## Design

- 12 ordinary-language briefs, intentionally allowing a plausible third route;
- frozen two-route shortlist per brief before any rendering;
- fresh deterministic seeds `[230251, 633610, 920483]`;
- one viable candidate per representation per seed;
- candidate generation brief-independent and representation-local;
- all five arms rendered for the oracle;
- route identities hidden during exhaustive artistic selection;
- no mutation, adaptive search, proxy aesthetic score, code length or compression pressure.

Primary support required at least 32/36 blocks contained and no brief with 0/3 containment.

## Frozen briefs

- **eye-in-smoke** — A drifting smoky organism folds back toward itself around a small empty eye, but one side keeps stretching away like a loose current. shortlist: `orbit` + `recurrence`
- **gathered-sail** — A translucent sail seems gathered into one restless knot: broad soft folds at a distance, tangled internal crossings when you look closer. shortlist: `sheet` + `recurrence`
- **wreath-echoes** — Several related soft bodies gather into a wreath around an unoccupied middle, each echoing the others without becoming identical. shortlist: `family` + `orbit`
- **braided-whip** — One narrow living stroke keeps curling back through its own wake, somewhere between a whip under tension and a compact braided current. shortlist: `filament` + `recurrence`
- **petal-veil** — A thin veil opens into a handful of sibling petal-like gestures that still feel governed by one shared rhythm rather than separately drawn parts. shortlist: `sheet` + `family`
- **ribbon-school** — A small school of slender translucent ribbons repeats the same bending instinct with slight differences, sparse enough that the gaps matter. shortlist: `family` + `filament`
- **soft-ring-skin** — A breathing ring has an empty middle, but portions of its edge broaden and soften until it almost reads as a piece of skin rather than a line. shortlist: `orbit` + `sheet`
- **hollow-knot** — A compact living knot turns around a clean hollow center; crossings should feel active and vascular, while the hole remains unmistakable. shortlist: `orbit` + `recurrence`
- **blossoming-thread** — A single wandering thread periodically blossoms into related lobes along its course, without settling into either a simple stroke or a cluster of separate objects. shortlist: `recurrence` + `family`
- **curtain-thread** — One long translucent thread sweeps back and forth so broadly that it starts to suggest a hanging curtain, while still feeling materially sparse. shortlist: `filament` + `sheet`
- **interwoven-colony** — A compact colony of related forms interweaves until the group almost reads as one knotted body, but traces of sibling repetition should remain. shortlist: `family` + `recurrence`
- **anchored-wreath** — Narrow tendril-like gestures gather around a shared invisible center, repeating as a family while hinting at one continuous wreath. shortlist: `family` + `orbit`
