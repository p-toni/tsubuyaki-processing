# Orbit representation research v1

This package records the evidence that led from a representation-boundary failure to an experimental **closed 1-D recurrence** representation (`orbit`).

The production `SKILL.md` is intentionally unchanged. This is research/prototype evidence only.

## Research sequence

### 1. Four-route capacity map

Equal fixed archives across recurrence / family / sheet / filament produced **23/24 heuristic-route matches (95.8%)**. Seven of eight briefs were 3/3 seed-stable. This established that the original four adapters had distinct semantic niches, but the briefs were deliberately easy-niche probes.

### 2. Four-route boundary map

Six pairwise boundaries × two directional phrasings × three fresh seeds produced:

```text
pair containment: 36/36
intended directional flip:
  5/6 boundaries = 3/3 seeds
  recurrence ↔ sheet = 0/3 seeds
```

The failure was localized: recurrence-leaning `Folded Aperture` was won by sheet in 3/3 seeds, while sheet-leaning `Aperture Current` was also won by sheet in 3/3.

The diagnosis was topological rather than allocational. Existing recurrence is an open axial 1-D manifold; it cannot form a sparse self-returning path around a persistent void.

### 3. Targeted orbit intervention

`orbit` adds a closed periodic 1-D spine with:

- persistent central aperture;
- angular coverage around the void;
- local asymmetric indentation/fold;
- subtle normal-offset side structure;
- coherent temporal phase motion while preserving closure.

On the exact failed boundary:

```text
Folded Aperture:  orbit / orbit / orbit
Aperture Current: sheet / sheet / sheet
```

Hardening at this point showed 39/40 first starts valid and 117/120 local numeric mutations valid (97.5%). Non-periodic winding, collapsed axes, and aperture collapse fail closed.

### 4. Fresh five-arm non-stealing replication

A frozen experiment used 10 unseen briefs, two assigned to each semantic niche, three fresh seeds, and four independent starts per representation. All candidate generation finished before artistic selection; global route identities stayed sealed until all 30 verdicts were written.

Result:

```text
orbit niche:       6/6 orbit wins
non-orbit controls: 0/24 orbit wins
overall intended niche: 30/30
```

Every representation won both of its intended briefs in all 3/3 seeds.

### 5. Fresh orbit boundary replication

The harder gate tested orbit against every original representation with directional near-neighbor briefs, all five arms still eligible:

```text
directional target wins: 24/24
intended-pair containment: 24/24
orbit-leaning blocks: 12/12 orbit
opposite-direction blocks: 12/12 intended non-orbit route
third-route leakage: 0
```

All four boundaries flipped in the intended direction in **3/3 seeds**:

- orbit ↔ recurrence: closed self-returning knot vs open recurrent knot;
- orbit ↔ sheet: line-bound aperture vs membrane aperture;
- orbit ↔ filament: sealed whip vs open near-halo;
- orbit ↔ family: lobes of one continuous ring vs separate sibling organs.

### 6. Metaphorical cold-language holdout

A final local robustness gate removed explicit topology vocabulary from the prompts. Ten cold metaphorical briefs described the same five semantic niches without using route names or terms such as `recurrence`, `sheet`, `filament`, `1-D`, `2-D`, or `aperture`. Three fresh seeds and four fixed independent starts per representation were judged with route identity sealed.

```text
overall intended niche: 30/30
orbit metaphor niche:    6/6 orbit wins
non-orbit metaphors:     0/24 orbit wins
```

Every metaphorical brief selected its intended representation in 3/3 seeds. This reduces the concern that orbit only succeeds when the prompt effectively names its mathematical topology. It is still not independent-judge evidence.

### 7. Historical pre-orbit cold-brief holdout

To test natural prevalence rather than prompts designed around orbit, a frozen holdout reused **9 briefs/specs authored before orbit existed**. Eight had established pre-orbit route ownership (family / recurrence / sheet / filament); one historical negative-morphology control was only specified as a compact math-first emergent form, without a subtype assignment. Three fresh seeds and four independent starts per representation were judged route-blind.

```text
established-route controls: 24/24 prior-route wins
orbit steals on controls:     0/24
subtype-ambiguous old brief:  orbit 3/3
```

This is the first evidence in the sequence that orbit demand occurs in text authored before the representation was proposed. The sample is intentionally small and should not be read as a prevalence estimate for arbitrary creative briefs.

### 8. Matched cause ablation

The three orbit winners from the historical subtype-ambiguous brief were then ablated **without new search**. Each exact genome was rendered as: (a) the intact closed sparse orbit, (b) the same contour with a fixed angular gap, or (c) the same animated outer silhouette filled radially into a surface-like body. Condition identity was sealed until all three judgments were frozen.

```text
closed sparse cause: 3/3
open-gap contour:    0/3
filled silhouette:   0/3
```

This weakens the alternative explanation that orbit won merely because a lobed creature-like silhouette is visually attractive: breaking closure or replacing the sparse path with a filled surface removed the preference while preserving much of the outer shape.

## Current conclusion

The evidence supports treating `orbit` as a **first-class research representation candidate** rather than a one-off repair. It appears to occupy a coherent topology niche: a closed one-dimensional recurrent manifold around a persistent void.

The historical holdout now provides **limited evidence of natural orbit demand**: one subtype-ambiguous pre-orbit brief selected orbit in 3/3 fresh seeds while orbit stole 0/24 established-route controls. This is evidence of existence, not a population prevalence estimate.

It does **not** yet justify:

- a production `SKILL.md` routing change;
- a claim about how common orbit briefs are in arbitrary cold traffic;
- an allocation/racing policy;
- collapsing orbit into recurrence as a subtype versus keeping it top-level.

The main remaining gate is **independent-judge replication**. All artistic verdicts in this research sequence came from one judging session/process.

## Files

- `protocols.md` — the frozen protocols in experimental order.
- `results.json` — machine-readable results for the first six evidence layers.
- `historical-holdout-v1.md` — frozen historical-holdout + matched-ablation protocol, provenance, and interpretation.
- `historical-holdout-v1.json` — machine-readable results for evidence layers 7–8.
- `../../prototypes/autonomous-discovery/orbit_representation.py` — experiment-safe registration of the new representation without mutating the baseline four-route registry on import.
- `../../prototypes/autonomous-discovery/test_orbit_representation.py` — topology, validity, and archive-independence regression coverage.
