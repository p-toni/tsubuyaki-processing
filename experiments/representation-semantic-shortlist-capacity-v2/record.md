# Representation semantic shortlist capacity v2

Fresh capacity falsification of the v1 brief-only two-route shortlist result.

## Question

Does top-2 containment survive when each representation has four independent starts and the exhaustive winner can come from meaningful within-route capacity?

## Result

```text
briefs:                    10
representation pairs:      10/10 covered
fresh seeds:                3
blocks:                    30
starts per representation:  4
candidates per block:      20
shortlist containment:     30/30
briefs with 0/3:            0
3/3 winner stability:      10/10
```

All 60 fixed candidate phenotypes (4 × 5 routes × 3 seeds) were generated before artistic inspection and were valid on their first generation attempt. The same fixed per-seed archives were reused across all briefs; only artistic intent changed.

Together with v1, this supports testing semantic top-2 eligibility as an upstream allocation policy. It does not yet show that reallocating the saved budget to the shortlisted routes improves final art.

No production `SKILL.md` change is made here.

---

# Frozen protocol

Frozen before candidate generation or inspection.

- representations: `recurrence`, `orbit`, `family`, `sheet`, `filament`;
- 10 fresh ordinary-language briefs, one for every unordered representation pair;
- every brief intentionally admits a plausible third interpretation;
- frozen top-2 before rendering;
- deterministic seeds `[687069, 426342, 889868]` from SHA-256(`representation-semantic-shortlist-capacity-v2`);
- 4 independent viable starts per representation per seed;
- candidate generation brief-independent and representation-local;
- all archives finish before artistic selection;
- no mutation, adaptive search, aesthetic scalar, code length, or compression pressure;
- support required at least 27/30 containment and no brief at 0/3.

## Frozen briefs

- **smoke-eye-tail** — A soft drifting body keeps circling a dark little eye while one restless tail-like current refuses to close with the rest. shortlist: `orbit` + `recurrence`
- **braided-buds** — A compact tangle seems made from several related growths, yet their paths braid together so tightly that the group nearly becomes one organism. shortlist: `family` + `recurrence`
- **crumpled-sail-current** — A broad translucent sail is pulled into a restless current, with soft material folds interrupted by a few tight internal crossings. shortlist: `sheet` + `recurrence`
- **wire-in-eddy** — A single narrow strand is caught in an eddy: still clearly one stretched stroke, but repeatedly curling back through its own wake. shortlist: `filament` + `recurrence`
- **wreath-of-pods** — Several sibling pod-like gestures collect around an empty middle, preserving their family resemblance while almost forming a continuous wreath. shortlist: `family` + `orbit`
- **softened-eye** — An empty eye is surrounded by material that alternates between a spare boundary and broad soft patches, as though a ring were turning into skin. shortlist: `orbit` + `sheet`
- **closed-whip-shadow** — A whip-like stroke bends so far back that it nearly becomes a sealed halo, but its sense of tension and directional sweep should remain visible. shortlist: `filament` + `orbit`
- **petal-cloth** — A thin translucent cloth seems to divide into a handful of related petal gestures, broad enough to feel like material yet rhythmic like siblings. shortlist: `sheet` + `family`
- **school-of-whips** — A sparse little school repeats one whip-like bending instinct across several related bodies, with enough separation that the empty gaps stay important. shortlist: `family` + `filament`
- **curtain-wire** — A very sparse strand sweeps through such broad folds that it starts to suggest a hanging curtain, without ever becoming a solid surface. shortlist: `filament` + `sheet`
