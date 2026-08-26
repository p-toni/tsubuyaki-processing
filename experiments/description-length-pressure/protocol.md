# Description-Length Pressure Experiment

## Question

How early should the hard #つぶやきProcessing description-length constraint influence artistic selection?

The deployment medium is fixed: final executable post <=280 X-weighted characters. The uncertainty is whether that pressure should enter only after artistic selection, at shortlist selection, or during search itself.

## Hypotheses

- **H1 — late-only pressure is too late.** Choosing the expanded visual winner first can select phenotypes whose defining cause cannot survive golf.
- **H2 — shortlist preflight is the best tradeoff.** A cheap compression-survival check on a small expanded shortlist should improve final tweet quality without collapsing creative search.
- **H3 — early pressure harms discovery.** Filtering the full candidate pool by description-length proxy before visual selection should sacrifice expanded quality/diversity more than it helps deployment.

## Frozen conditions

All conditions receive the **same expanded candidate pool** for each brief. This isolates selection timing from generator/search differences.

### A — late only

```text
expanded pool
→ visual/temporal selection
→ choose expanded winner
→ golf winner
→ accept success/failure
```

Description length has no influence until after the expanded winner is chosen.

### B — shortlist preflight

```text
expanded pool
→ visual/temporal top-3 shortlist
→ cheap compression preflight on all three
→ choose best tweet-viable finalist
→ full golf
```

The preflight is a falsification gate, not a scalar quality score. It asks whether the high-leverage relationships that define the candidate plausibly survive inside the executable budget.

### C — early pressure

```text
expanded pool
→ remove candidates that fail compact-cause proxy
→ visual/temporal selection within surviving pool
→ full golf
```

This models description-length pressure during discovery/selection without changing the underlying generated population.

## Briefs / routes

Use four math-first routes so the experiment includes prior positive and negative compression regimes:

1. repeated family — multiple distinct related translucent bodies from one shared generator;
2. dense 2D sheet — true sheet sampling + legible negative space;
3. intentional 1D filament — axial identity + traveling internal deformation;
4. recurrence / living knot — recurrent state transformed into one coherent non-textbook phenotype.

## Candidate pool

For each route:

- generate 12 readable expanded candidates from the same route-aware vocabulary;
- retain only runtime-valid, brief-adherent candidates;
- render at three matched representative times;
- do not use code length as a generation objective.

The candidate model exposes explicit structural operators so compact-cause cost can be estimated consistently.

## Expanded evaluation

Blind to A/B/C, rank candidates by:

- brief adherence;
- visual preference;
- temporal quality;
- mathematical leverage / surprise.

Do not include tweet length or compressibility in the expanded ranking.

## Description-length proxy

Each candidate has a deterministic compact-cause estimate built from the operators required to preserve its defining phenotype.

The proxy is allowed to say only:

```text
plausibly tweet-viable
borderline
implausible
```

It must not become an aesthetic score.

For final shortlisted candidates, replace the proxy with an actual compact executable attempt and exact length check.

## Outcomes

For each route and condition record:

1. expanded candidate selected;
2. expanded visual rank;
3. compact-cause estimate;
4. exact tweet length after golf;
5. runtime validity;
6. phenotype-survival judgment across matched times;
7. final tweet visual preference.

Primary comparisons:

- successful deployable winner rate;
- final tweet pairwise preference;
- expanded-quality sacrifice relative to condition A;
- cases where B changes the winner because A's expanded elite does not survive;
- cases where C removes the eventual best deployable candidate or collapses diversity.

## Interpretation

- **B > A, B > C:** add compression preflight between visual shortlist and final selection.
- **A ≈ B > C:** keep description length late; recurrence failure was route-specific.
- **C ≥ B:** description-length pressure should enter discovery earlier than current policy.
- **route interaction:** use route-specific compression timing rather than one universal gate.

## Guardrails

- Same expanded candidate pools across A/B/C.
- No aesthetic scalar during search.
- No changing candidate generator after seeing results.
- No changing the compact-cause proxy after seeing which candidates win.
- 280 remains a deployment ceiling, not an optimization target.
- A failed golf attempt is an experimental result, not a reason to rewrite the candidate.
