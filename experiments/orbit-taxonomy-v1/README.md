# Orbit taxonomy experiment v1

## Question

Should `orbit` be treated as a top-level research representation, or merely as a closed/polar subtype of the existing recurrence representation?

The operational criterion was reachability: if existing recurrence genomes can reach orbit-quality closed-aperture phenotypes through a small structural extension while preserving the same genome/mutation grammar, subtype is sufficient. If orbit-specific generation remains artistically superior even after minimal closure/polar repairs are valid, keep a separate top-level arm.

## Minimal-closure ladder

Same recurrence genomes, progressively stronger structural changes:

1. `recurrence-open` — unchanged recurrence;
2. `seam-closed` — connect the Cartesian recurrence endpoints;
3. `periodic-domain` — periodic reparameterization while retaining recurrence roles;
4. `polar-remap` — reinterpret the same recurrence genes around a circular base projection;
5. `orbit` — full orbit representation and gene set.

Two closed briefs and two open controls were evaluated across seeds `616842`, `216139`, `980564`, with four starts per condition and condition identity blinded.

Initial ladder result:

```text
closed briefs (6 blocks):
  polar-remap       5
  orbit             1
  simpler closure   0

open controls (6 blocks):
  recurrence-open   5
  seam-closed       1
  other closed      0
```

Simple endpoint closure and periodic reparameterization were insufficient. Polar projection was the first recurrence-derived transformation to become artistically competitive.

## Validity repair 1 — distributed seam correction

The original polar remap looked nearly closed but failed the orbit closure contract because the original nonperiodic recurrence phase left a small seam. A distributed C0 seam correction used no new genes.

Validity bridge:

```text
fresh recurrence genomes: 36/36 open-valid and 36/36 closed-valid
numeric mutations:        180/180 open-valid and 180/180 closed-valid
```

But blinded artistic retest on the same closed briefs reversed the initial result:

```text
closed briefs:
  orbit              5/6
  corrected polar    1/6

open controls:
  open recurrence    6/6
```

The global seam deformation purchased validity at meaningful artistic cost.

## Validity repair 2 — local smooth bridge

A stricter falsification preserved the original polar contour and closed only the tiny seam with a local quadratic bridge. It added no genes and retained the recurrence numeric mutation grammar.

Hard validity:

```text
fresh starts:
  open recurrence    60/60
  polar bridge       60/60
  dual-valid         60/60

numeric mutations:
  open recurrence    300/300
  polar bridge       300/300
  dual-valid         300/300
```

Final blinded artistic retest:

```text
closed briefs:
  full orbit         6/6
  polar bridge       0/6
  original polar     0/6

open controls:
  open recurrence    6/6
  polar variants     0/6
```

## Conclusion

`orbit` is **not** adequately modeled as “recurrence with its ends joined,” and even a valid closed/polar projection over the existing recurrence genome does not match the full orbit representation on its niche.

The current research architecture should therefore keep:

```text
recurrence   — open/axial recurrent manifold
orbit        — closed recurrent manifold organized around a persistent void
```

as separate top-level search arms.

They can still be grouped conceptually under a broader **1-D recurrent manifold family**, but they require distinct seed grammars, hard validity contracts, and search geometry.

This is a research taxonomy result only. It does not change production `SKILL.md` or routing guidance.

## Remaining gates

- independent-judge replication;
- deployment/compression survival of orbit phenotypes;
- representation allocation/racing policy;
- prevalence in arbitrary user traffic.
