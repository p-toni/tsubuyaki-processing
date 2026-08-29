# Search measurement sensitivity v1 — result

## Executive result

Neither structural metric passed the preregistered sensitivity contract.

```text
sparse-shape-v1  FAIL
sparse-shape-v2  FAIL
```

`v1` retains the known tolerance plateau. `v2` successfully removes that plateau and looks monotonic in aggregate, but fails target-level displacement sensitivity on repeated/periodic geometries.

The benchmark objective therefore remains unresolved. Search-policy optimization stays paused.

## Run

Workflow: `search-measurement-sensitivity` run `33228589447`.

Population:

```text
5 routes
× 3 already-consumed seeds (101,103,107)
× local/global target
= 30 target cases
```

No fresh search seed was consumed.

## sparse-shape-v1

Preregistered failures:

| contract | passes | required |
|---|---:|---:|
| exact == 0 | 30/30 | 30 |
| blank >= .99 | 30/30 | 30 |
| shift3 > 0 | **0/30** | 30 |
| shift1 <= shift2 <= shift3 | 30/30 | 27 |
| shift3 < shift6 < shift12 | **26/30** | 27 |
| fade50 < deleteRightThird | 30/30 | 27 |
| deleteRightThird < blank | 30/30 | 30 |
| denseBBox > validNeighbor | 30/30 | 27 |
| unrelatedValid > validNeighbor | 30/30 | 27 |
| duplicateShift6 > fade50 | **26/30** | 27 |

Mean translation distances:

```text
shift1   0
shift2   0
shift3   0
shift6   0.12555
shift12  0.23306
```

Decision: reject v1 as a sufficiently sensitive structural search objective.

## sparse-shape-v2

`v2` replaced the single radius-3 tolerant F1 with the mean of F1 at radii `0,1,2,3`, keeping the same foreground rule and 80/20 shape/mass weighting.

It solved the hard zero plateau:

```text
shift3 > 0   30/30
```

and passed all non-translation corruption controls:

```text
exact == 0                  30/30
blank >= .99                30/30
fade50 < deleteRightThird   30/30
deleteRightThird < blank    30/30
denseBBox > validNeighbor   30/30
unrelatedValid > neighbor   30/30
duplicateShift6 > fade50    30/30
```

But the preregistered translation contracts failed:

| contract | passes | required |
|---|---:|---:|
| shift1 <= shift2 <= shift3 | **19/30** | 27 |
| shift3 < shift6 < shift12 | **24/30** | 27 |

Route decomposition exposes the failure:

| route | short monotonic | long strict |
|---|---:|---:|
| recurrence | 6/6 | 6/6 |
| orbit | 6/6 | 5/6 |
| family | **1/6** | 5/6 |
| sheet | **0/6** | 5/6 |
| filament | 6/6 | **3/6** |

Yet aggregate means appear cleanly monotonic:

```text
shift1   0.13459
shift2   0.19329
shift3   0.23247
shift6   0.33599
shift12  0.41192
```

This is an important methodological result: the aggregate mean hides a route-structured metric pathology.

## Failure mechanism

The individual blocks show why a tolerance-overlap metric is insufficient.

Repeated or dense geometries can partially re-align with their own neighboring structure after translation. Examples from the frozen run:

```text
family / seed101 / local
shift1  0.17288
shift2  0.07533
shift3  0.18942

sheet / seed101 / local
shift1  0.19869
shift2  0.22240
shift3  0.12958

filament / seed101 / local
shift6  0.60301
shift12 0.49978
```

Those are not random noise. They are consequences of matching foreground support without explicitly representing global placement: periodic/repeated strokes can find new nearby correspondences as displacement changes.

Therefore the next step should **not** tune F1 radii or the 80/20 weight.

## Decision

Reject `sparse-shape-v2` as the benchmark candidate.

Do not:

- replay #56–#63 under v2;
- spend fresh seeds on search-policy confirmation;
- resume mutation-scale/operator optimization;
- choose a better-looking radius mixture after inspecting these results.

Proceed to a new metric-design experiment with a different decomposition.

## Next metric hypothesis

Separate global placement from intrinsic foreground geometry.

Candidate architecture:

```text
placement
  explicit centroid / frame displacement

shape
  compare foreground geometry after removing global translation
  (centroid-aligned tolerant geometry or a symmetric distance-transform / Chamfer family)

extent
  compare foreground span / bbox geometry

mass
  compare foreground ink/support mass
```

This decomposition attacks the observed failure directly:

- a translated periodic sheet cannot become "closer" merely by re-aligning with another rib because placement is scored independently;
- after alignment, intrinsic shape can remain tolerant to small rasterization differences;
- deletion, dense-fill and duplication remain visible through shape/extent/mass terms.

The next candidate and its weights/normalizations must be frozen before opening its results.

## Boundary

Instrument validation only. No artistic promotion, representation pruning, production/default search change, benchmark adoption, or `SKILL.md` change follows from this result.
