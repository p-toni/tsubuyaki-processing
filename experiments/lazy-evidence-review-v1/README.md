# Lazy evidence review v1

## Purpose

Reduce reviewer burden in evidence-authoritative adaptive search without letting proxy judgments promote candidates.

PR #40 established the correct authority boundary, but unresolved candidate comparisons could still be queued eagerly during one replay even when an earlier authoritative promotion would make some of those comparisons unreachable.

This experiment asks three questions:

1. should a strong human/independent `tie` terminate review for that phenotype pair?
2. how many unresolved promotion-critical pairs should one replay expose before waiting for evidence?
3. what should happen when the active queue already contains resolved but non-authoritative evidence?

## Finding 1 — authoritative ties are terminal evidence

A strong human or independent-model tie now means:

```text
this pair was reviewed
→ neither phenotype is authorized to replace the other
→ preserve incumbent / frontier ambiguity
→ do not ask for the same pair again
```

Previously `winner_fingerprint=None` was treated the same as missing evidence, so an explicit strong tie could be re-queued forever. Conflicting authoritative sources also remain defer/no-promotion, but they do not trigger repeated review automatically.

## Finding 2 — bounded lazy review

The selector can now cap the number of unresolved review items present at once.

```text
replay
→ consume all existing authoritative phenotype evidence
→ queue at most K newly reachable unresolved pairs
→ preserve incumbent for later unresolved comparisons
→ review K pairs
→ replay from the same seeded search
→ newly reachable pairs may now appear
```

The queue itself is replay evidence: resolved decisions already present in the candidate-review directory are automatically decoded on the next run.

### Calibration A — strict preference orders

A frozen exhaustive simulation modeled the same incumbent/challenger rule used by search:

- candidates have a hidden strict total preference order;
- unknown comparisons preserve the incumbent;
- each replay exposes at most `K` unseen pairs;
- all exposed pairs are resolved before the next replay;
- the process continues until no unresolved comparison remains on the reachable path.

All hidden orders were enumerated for 4–8 candidates. Every cap preserved the fully evidenced result in every case.

At 8 candidates (40,320 hidden orders):

| pending cap | mean ratings | mean review rounds |
|---|---:|---:|
| 1 | 7.00 | 7.00 |
| 2 | 8.10 | 4.34 |
| 3 | 9.30 | 3.50 |
| eager/unbounded | 13.74 | 2.59 |

`K=2` uses **41.0% fewer ratings than eager batching**. Relative to `K=1`, it uses 15.8% more ratings but requires **38.0% fewer reviewer rounds**.

### Calibration B — arbitrary pairwise outcomes, including ties

The total-order assumption was then removed. For five candidates, all `3^10 = 59,049` possible pairwise outcome matrices were enumerated, where each pair may resolve to A, B, or tie. This includes non-transitive preference structures.

Every cap again converged to the same result as the fully evidenced sequential tournament in all 59,049 cases.

At 5 candidates:

| pending cap | mean ratings | mean review rounds |
|---|---:|---:|
| 1 | 4.00 | 4.00 |
| 2 | 4.70 | 2.59 |
| 3 | 5.30 | 2.30 |
| eager/unbounded | 6.00 | 2.00 |

Under this less structured preference model, `K=2` still uses **21.6% fewer ratings than eager batching** while requiring 35.2% fewer review rounds than `K=1`.

Because recent human calibration already showed rating fatigue, reviewer rounds are not free. `K=2` is therefore the best current operating point: materially less speculative work than eager batching without forcing one interruption per comparison.

These are structural synthetic calibrations, not claims about the empirical distribution of artistic preferences. `K=1`, `K=3`, and unbounded behavior remain explicit experimental options.

## Finding 3 — resolved weak evidence must not masquerade as a new review

The v3 queue stores one decision per phenotype pair. If the active queue already contains a low-confidence or advisory decision, calling `create_review_bundle` for that same pair does not create another independent record.

The selector therefore now distinguishes:

```text
pair already pending
→ leave it pending

pair already reviewed in this queue, but evidence is weak/advisory
→ preserve the existing record
→ do not claim another review was queued
→ require additional evidence from a new independent review bundle

pair absent from this queue and review capacity is available
→ queue it normally
```

This preserves provenance and avoids silently overwriting or pretending to duplicate evidence.

## Runtime changes

`EvidenceAuthoritySelector` now:

- optionally bounds pending review items;
- reloads resolved evidence from its own queue directory;
- does not requeue authoritative ties;
- does not automatically requeue authoritative conflicts;
- does not no-op requeue resolved weak evidence already stored in the active queue;
- still permits only strong human/independent winner evidence to replace an elite;
- still treats deterministic/same-model judgments as advisory only.

`screened_search.resume_adaptive_search(...)` defaults to:

```text
candidate_max_pending_reviews = 2
```

The CLI exposes `--candidate-max-pending-reviews`.

## Scope

Research/prototype only. No production `SKILL.md` change and no representation-family change.

The five-family insufficiency / yuruyurau trigger is still not reached; this experiment addresses the current bottleneck of evidence-efficient search.
