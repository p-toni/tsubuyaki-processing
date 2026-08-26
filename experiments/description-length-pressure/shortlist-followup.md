# Follow-up — Shortlist Size vs Adaptive Preflight

## Question

Given the frozen 48-candidate population and expanded visual rankings from the description-length-pressure experiment, how many visually ranked candidates need compression-survival preflight before deployment quality saturates?

No candidates are regenerated and no visual rankings are changed.

## Frozen expanded rankings

| route | rank 1 | rank 2 | rank 3 |
|---|---|---|---|
| family | F12 | F2 | F5 |
| sheet | S4 | S6 | S12 |
| filament | L9 | L10 | L7 |
| recurrence | R12 | R6 | R4 |

Known exact deployment outcomes from the parent experiment:

- F12: survives compression;
- S4: survives compression;
- L9: survives compression;
- R12: fits the budget but fails phenotype survival;
- R6: survives compression.

## Policies compared

### K=1

Preflight only the expanded visual winner. If it fails, deployment fails.

### K=2

Preflight the two highest-ranked expanded candidates and choose the highest-ranked survivor.

### K=3 / K=5

Same rule with a larger maximum visual shortlist.

### Adaptive sequential

1. preflight rank 1;
2. if it survives, stop;
3. if it fails, preflight rank 2;
4. continue down visual rank only when the previous candidate failed.

The adaptive policy preserves visual rank as the ordering signal; description length remains a falsification gate, not an optimization score.

## Result

| policy | deployable routes | candidates actually requiring preflight |
|---|---:|---:|
| K=1 | 3 / 4 | 4 |
| K=2 | **4 / 4** | 8 if both are always tested; **5 if evaluated sequentially** |
| K=3 | 4 / 4 | 12 if always tested; 5 with early stopping |
| K=5 | 4 / 4 | 20 if always tested; 5 with early stopping |
| adaptive sequential | **4 / 4** | **5** |

The only fallback required is:

```text
recurrence: R12 (fail survival) -> R6 (pass)
```

Family, sheet and filament stop after their rank-1 candidate.

## Interpretation

Within this frozen archive, deployment success saturates at visual rank 2.

However, the more general result is not `shortlist size = 2`.

The stronger policy is:

```text
rank candidates visually / temporally
-> compression-preflight current best
-> pass? commit
-> fail? try next visual candidate
-> repeat only as needed
```

This weakly dominates fixed top-k preflight in this experiment:

- same final candidate as K=2/K=3/K=5;
- same 4/4 deployment success;
- only 5 compression preflights rather than 8, 12 or 20 if a fixed shortlist is evaluated exhaustively;
- no need to define an unsupported universal shortlist size.

The experiment therefore does **not** justify hard-coding `top 2` or `top 3` into the skill.

## Production implication

Treat compression survival as an **ordered fallback gate attached to visual rank**, not as a separate selection objective and not as an exhaustive shortlist stage.

Recommended transition:

```text
expanded discovery
-> visual + temporal ranking
-> preflight visual elite
   -> survives: tweet-viable finalist
   -> fails: preflight next-ranked alternate
-> full golf
-> exact survival verification
```

The fallback chain should remain small in practice, but its maximum depth should be determined by whether remaining candidates are still artistically worth deploying, not by a fixed numeric `K` learned from this small experiment.

## Limitation

This is a retrospective nested analysis of the same four-route archive. It establishes saturation at rank 2 **for this archive**, not a universal probability distribution over compression failures. A larger archive would be needed before setting any numeric fallback cap.
