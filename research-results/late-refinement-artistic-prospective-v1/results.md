# Late-refinement artistic preference prospective v1 — results

## Decision

`LATE_REFINEMENT_ARTISTIC_PREFERENCE_NOT_SUPPORTED`

This run is protocol-valid. The 24 human ratings were committed at `89f268f7e0d8ebc6e5586ea30b85a65996cf8f35` before the separately sealed identity key artifact was opened.

## Frozen population

- review seeds: `758003, 758019, 758037, 758053, 758071, 758089, 758107, 758127`
- routes: recurrence, orbit, filament
- 24 blinded blocks
- reviewer artifact: `9861880751`, digest `sha256:cc5809c255270ee1abc076096584d77bbed14c6b77c4468d6745f466e97200d2`
- sealed key artifact: `9861881457`, digest `sha256:dd898bcf035939fd8d68f886344435b72c6f97ee416621a1a73c9fa59aa67782`

## Primary result

- human-reviewable: **24 / 24**
- human-decisive: **21 / 24**
- equivalent: **3 / 24**
- `q=0.75` wins among decisive blocks: **10 / 21**
- `q=0.75` decisive win rate: **0.4761904762**
- one-sided exact binomial p-value vs `p=0.5`: **0.6681880951**

## Route breakdown

| route | decisive | q=.75 wins | win rate |
|---|---:|---:|---:|
| recurrence | 6 | 3 | 0.5000 |
| orbit | 7 | 3 | 0.4286 |
| filament | 8 | 4 | 0.5000 |

## Frozen gate

1. >=18 reviewable: **PASS** (24)
2. >=12 decisive: **PASS** (21)
3. q=.75 win rate >.65: **FAIL** (0.4762)
4. one-sided exact binomial p<=.10: **FAIL** (0.6682)
5. every route with >=3 decisive has q=.75 win rate >=.50: **FAIL** (orbit 0.4286)

The post-hoc late-refinement signal observed across consumed `755xxx`–`757xxx` populations did not replicate on fresh `758xxx` data.

## Boundary

Close this line. Do not tune nearby quantiles, stage cutoffs, route-specific thresholds, operators, or seed sets on consumed reviewer populations. This result does not support changing search allocation based on generation order.

Visual-review experiments are paused after this result. Subsequent autonomous work should focus on mechanically answerable search-architecture questions unless a critical decision genuinely requires artistic evidence.
