# Semantic shape steering v1

## Question

Can the current intrinsic-1D yuruyurau search be deliberately steered toward a requested named shape, rather than merely generating an archive that happens to contain structurally similar forms?

This experiment tests the first product-level version of:

> ask for X -> search intentionally moves toward X.

It does **not** test open-vocabulary language understanding. V1 uses a frozen catalog of eight literal prompt labels that map deterministically to procedural target silhouettes. A positive result therefore means "named-shape steering works for this frozen concept set," not "arbitrary natural-language concepts work."

## Frozen named concepts

Exactly eight prompts:

- `heart`
- `star`
- `crescent`
- `fish`
- `butterfly`
- `tree`
- `letter-a`
- `flower`

Each label resolves to one deterministic 400x400 binary target image. The target renderer is frozen before any consumed search outcome is generated.

The eight targets must:

1. satisfy the existing support/span target contract;
2. have distinct image fingerprints;
3. be disjoint by image fingerprint from every prior sampling-invariance / spectral-search / material-control target suite;
4. remain visually interpretable as line/skeleton targets rather than filled photographic masks.

If the target contract fails, the target geometry may be repaired **before smoke and consumed search begin**. Once smoke passes, target images are frozen.

## Runtime under test

Stacked on the confirmed runtime result from #92:

- mutation portfolio: `native-spectral-50-50-v1`;
- routes: `recurrence`, `orbit`, `filament`;
- K=2 spectral material control;
- amplitude 16;
- one valid start basin per route;
- 4 explore + 4 round-A + 12 refine challengers = exactly 20 challenger attempts per route;
- 10 native + 10 spectral challenger attempts per route;
- all existing route hard-validity checks remain active.

Each concept therefore gets a fixed total budget of exactly 60 challenger attempts per arm across the three intrinsic-1D routes.

## Compared arms

### `blind-mixed`

The already-integrated mixed runtime uses the existing `DeterministicTemporalSelector`. The requested concept/target is not visible to the selector while the trajectory is generated.

After the three route trajectories finish, the known target metric is allowed to choose the closest of the three final route champions. This gives the blind control a strong post-hoc target-aware route chooser; the only withheld capability is using X to decide which within-route mutations survive and become future parents.

### `guided-mixed`

The same mixed runtime, same starts, same search seed, same route budgets, same mutation operators, but pairwise promotion uses an experiment-only `TargetGeometrySelector`.

The selector:

1. invalid candidate loses to a valid candidate;
2. otherwise render each candidate as a binary t=90 structural phenotype;
3. compute frozen `sparse-geometry-v1` target distance;
4. promote the lower-distance candidate when the absolute difference exceeds `1e-9`;
5. exact/near ties preserve the incumbent.

No artistic proxy vote is mixed into target-directed promotion. This is intentionally a shape-steering experiment, not an aesthetic-selection experiment.

After all three route trajectories finish, the same frozen target distance chooses the closest final route champion.

## Identical starts

For each master seed x concept x route, a deterministic route-local RNG draws the first hard-valid start. That exact start candidate is deep-copied into both arms.

The start generator is target-label-dependent only through deterministic RNG partitioning; it never inspects target pixels. Therefore concept-specific starts are independent random baselines, not hand-shaped seeds.

## Selection metric versus evaluation metrics

Using the optimization metric itself as the only outcome would be circular. V1 therefore separates:

### Optimization metric

Frozen `sparse-geometry-v1` distance. Used only by `guided-mixed` promotion and by both arms' final three-route chooser.

### Held-out recognition proxies

The primary mechanical outcome is computed by two target-similarity proxies that are **not used anywhere during search**:

1. `coarseSoftIoU`: candidate and target binary support are reduced to 40x40 occupancy fields with BOX resampling; score is soft intersection / soft union.
2. `multiscaleF1`: after centroid alignment only for this evaluation, support overlap F1 is measured with symmetric dilation radii 6 and 12 pixels and averaged.

Both scores lie in [0,1], higher is better.

These proxies are still geometric, not human semantic authority. Their role is to establish deliberate movement toward the requested silhouette without evaluating on the exact objective used to steer search.

## Fresh consumed seeds

Exactly ten master seeds, searched in the repository before preregistration with no prior occurrence:

`125003, 125011, 125017, 125029, 125047, 125053, 125063, 125087, 125101, 125113`

Consumed seeds cannot be reused to tune concept geometry, search budget, operator split, selector threshold, metric definitions, or decision gates.

## Evidence rectangle

`10 seeds x 8 concepts = 80` paired concept/seed blocks.

Each block contains:

- 3 blind mixed trajectories;
- 3 guided mixed trajectories;
- 60 challenger attempts per arm;
- one target-selected final output per arm;
- held-out similarity scores for both final outputs;
- the best target distance among the three shared starts;
- the guided final target distance.

## Excluded smoke

Smoke seed: `124999`.

Before consumed search is authorized, smoke must prove for every concept and route:

1. blind and guided arms receive identical start genome + rendered phenotype;
2. each arm creates exactly 20 challengers per route;
3. mixed allocation is exactly 10 native + 10 spectral per route;
4. guided search is deterministic on exact replay;
5. target selector never promotes an invalid challenger over a valid incumbent;
6. final chosen output is hard-valid;
7. all target and evaluation scores are finite and within their declared ranges.

Smoke is transport/invariant evidence only and does not contribute to the decision.

## Paired outcomes

For each seed x concept:

- `deltaCoarse = guided.coarseSoftIoU - blind.coarseSoftIoU`
- `deltaMultiscale = guided.multiscaleF1 - blind.multiscaleF1`
- `guidedObjectiveGain = bestSharedStartDistance - guided.finalTargetDistance`

Master-seed inference averages each delta across the eight concepts before computing uncertainty.

Concept inference averages each delta across the ten fresh seeds.

## Preregistered mechanical decision gate

Decision **`SEMANTIC_SHAPE_STEERING_MECHANICALLY_PROMISING`** requires all:

1. complete hard-invariant 80-block rectangle;
2. exact 60-vs-60 total challenger budget in every block;
3. exact 30 native + 30 spectral challenger allocation per arm in every block;
4. mean `deltaCoarse > 0`;
5. one-sided 95% lower confidence bound over the ten master-seed mean `deltaCoarse` values > 0;
6. mean `deltaMultiscale > 0`;
7. one-sided 95% lower confidence bound over the ten master-seed mean `deltaMultiscale` values > 0;
8. at least 6/8 concepts have positive mean `deltaCoarse` **and** positive mean `deltaMultiscale`;
9. mean `guidedObjectiveGain > 0.01`;
10. at least 65% of the 80 blocks have `guidedObjectiveGain > 0`;
11. no one concept supplies >40% of total positive `deltaCoarse` contribution;
12. no one concept supplies >40% of total positive `deltaMultiscale` contribution.

One-sided t critical for df=9 is frozen as `1.8331129326536335`.

If any gate fails, decision is **`SEMANTIC_SHAPE_STEERING_NOT_READY`**. This exact eight-concept / 60-budget protocol may not be tuned on the consumed seeds.

## Mechanical results

Authoritative workflow run: `33313722689`.
Aggregate artifact: `9732898969`, digest `sha256:67283d2517ff7b50b1987f6f1a96d4808a37907e59f25c6757a49f152ff722ef`.

All target-contract and smoke gates passed, and all 80 consumed blocks completed.

Primary held-out results:

- mean `deltaCoarse`: `+0.002599407437562983`;
- one-sided 95% lower bound over master-seed coarse means: `+0.00003836126298378947`;
- mean `deltaMultiscale`: `+0.02768383727612065`;
- one-sided 95% lower bound over master-seed multiscale means: `+0.014148452084777172`;
- mean guided objective gain from the best shared start: `+0.0312971468854357`;
- guided objective gain positive in `79/80` blocks (`0.9875`);
- `7/8` concepts have positive mean improvement on both held-out proxies.

Concept-level held-out deltas:

| concept | delta coarse | delta multiscale |
|---|---:|---:|
| heart | +0.000279 | +0.029513 |
| star | +0.004346 | +0.022553 |
| crescent | +0.003066 | +0.053414 |
| fish | -0.013519 | +0.030976 |
| butterfly | +0.000377 | +0.006151 |
| tree | +0.012933 | +0.028559 |
| letter-a | +0.003268 | +0.015523 |
| flower | +0.010045 | +0.034782 |

Fish is the sole concept with a negative mean coarse-overlap delta, while it remains positive on multiscale F1 and has the strongest mean target-objective gain among the eight concepts (`+0.05057`). This heterogeneity was allowed by the preregistered 6/8 concept gate and does not trigger any post-hoc tuning.

Every preregistered mechanical gate passes.

## Mechanical decision

**`SEMANTIC_SHAPE_STEERING_MECHANICALLY_PROMISING`**

For this frozen eight-concept catalog and fixed equal budget, giving the requested silhouette authority over within-route mutation survival causes the generated forms to move toward the request in held-out geometry measures, not only in the metric used to steer them.

This establishes intentional **finite-catalog shape steering** mechanically. It still does not establish that a human looking only at the generated form recognizes the requested identity.

## Human recognition gate after a positive mechanical result

A positive mechanical result still does **not** establish that a person recognizes X.

Only after `SEMANTIC_SHAPE_STEERING_MECHANICALLY_PROMISING` may the experiment generate a blinded recognition package from eight separately preregistered display seeds (one per concept). The reviewer sees eight anonymous generated outputs plus the eight concept names and performs a one-to-one matching task.

The target silhouettes are not shown during matching.

This is intentionally lower burden and more direct than pairwise aesthetic ratings: the question is simply whether the requested identity survives the grammar.

Human recognition, not the geometric proxies, is the authority for the claim "it looks like X."

## Authority boundary

A positive v1 mechanical result means the system can use a frozen shape target to steer the intrinsic-1D mixed search toward named silhouettes better than an equally budgeted target-blind trajectory.

Even with a positive human matching result, v1 remains a finite-catalog demonstration. Open-vocabulary `prompt -> target representation` remains a separate layer to test later.
