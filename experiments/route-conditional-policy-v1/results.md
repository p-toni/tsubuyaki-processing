# Route-conditional policy v1 — result

Source workflow run: `33211643298`

Execution head: `a3743716912c1a4705309d82f65d3449491bde0a`

All 15 fresh route × seed blocks and the preregistered aggregate job completed successfully.

## Primary result

| route | frozen simple policy | non-worse than adaptive | replacement support |
| --- | --- | ---: | --- |
| recurrence | fixed-parent-local | 1/3 | no |
| orbit | fixed-parent-local | 1/3 | no |
| family | independent-breadth | 2/3 | yes |
| sheet | fixed-parent-local | 3/3 | yes |
| filament | fixed-parent-local | 0/3 | no |

Predeclared classification:

```text
selected simple replacement support  2/5 routes
→ general route-only simplification not supported

strict selected-simple advantage     2/5 routes
→ general strict simple advantage not supported

universal fixed-parent support        2/5 routes
→ general universal fixed-parent replacement not supported
```

The `family→breadth` route exception also failed its dedicated holdout gate:

```text
family breadth > family fixed-parent  1/3 fresh seeds
→ route-conditioning exception not supported
```

So the training-derived route identity map does not generalize as a replacement for the staged adaptive baseline.

## Mean normalized improvement

```text
combined local+global score
  oracle best of three   0.1154
  adaptive               0.0769
  universal fixed        0.0738
  route-selected simple  0.0649

local target
  universal fixed        0.1093
  adaptive               0.1053
  route-selected simple  0.0866

global target
  adaptive               0.0485
  route-selected simple  0.0432
  universal fixed        0.0383
```

The local/global aggregate hides important instability. For example:

- `sheet` strongly favors fixed-parent on all three holdout seeds;
- `filament` strongly rejects fixed-parent, including a large adaptive advantage on seed `127`;
- `family` often beats adaptive with a simple policy, but the training-selected breadth exception is not stable against fixed-parent.

That instability is the central finding: **representation identity alone is too coarse to choose the topology**.

## The remaining opportunity

The best policy among adaptive, breadth, and fixed-parent reaches mean combined improvement `0.1154`, versus `0.0649` for the frozen route map. The mean oracle gap is `0.0505`.

That gap is diagnostic only—the oracle sees the final objective result and cannot be deployed. But it shows that policy choice matters materially at the individual search-instance level even though a static route map fails.

The next causal question is therefore not “which route gets which policy?” It is:

> Can a small amount of **online search evidence** choose the useful topology early enough to capture part of the oracle gap under the same total evaluation budget?

A natural next experiment is a probe-then-commit selector: spend a small fixed pilot budget on simple breadth/local arms, choose using only observed objective progress, then commit the remaining budget to the stronger arm. That selector does not need to know the hidden target regime or a permanent route label policy.

## Decision

- Reject route-only simple-policy replacement as a general architecture.
- Reject the trained `family→breadth` exception as a stable route rule.
- Keep current adaptive search as the research baseline for now.
- Do not add more stages to adaptive search yet.
- Test online topology selection from current-search evidence on a third untouched seed set.

## Evidence boundary

Objective search-mechanics evidence only. No human or independent-model artistic-quality evidence was used. This result does not authorize artistic candidate promotion, hard representation pruning, portfolio sufficiency claims, or production `SKILL.md` changes.

Machine-readable results are frozen in `results.json`; `reproduce.py` and `aggregate.py` retain the deterministic holdout protocol. Raw block artifacts remain in workflow run `33211643298`.
