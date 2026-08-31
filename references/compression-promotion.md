# Adaptive Compression-Survival Promotion

Description length is a **deployment constraint on promotion**, not an aesthetic objective and not a search objective.

The description-length experiments support this order:

```text
expanded discovery
-> visual + temporal ranking
-> preflight the current best candidate
-> if compression survival passes: promote to deployment finalist
-> if it fails: preserve the artistic discovery and preflight the next visually ranked candidate
-> full golf
-> exact runtime / length / phenotype verification
```

Do not filter the full creative population by character count or a compressibility score.

The discovery/preservation boundary and preservation grades are defined in `references/preservation-contract.md`.

## Why this gate exists

A candidate can fit under 280 characters and still fail deployment because the compression removed the relationships that made the expanded phenotype good.

Therefore:

```text
fits <=280 != defining phenotype survived
```

The preflight must test **survival of the defining mathematical cause**, not only source length.

## 1. Rank artistically before applying description pressure

Complete readable mathematical discovery first.

Use visual + temporal judgment to order the strongest brief-adherent candidates. Character count must not change this ranking.

Keep the artistic winner even if it later fails deployment. A non-deployable phenotype can still be an important discovery and should remain in the archive / lineage.

Discovery is intentionally plural: several mathematically different candidates can all be legitimate answers to one brief. Preservation becomes stricter only after one elite has been selected for deployment.

## 2. Choose the meaningful temporal horizon before preflight

Compression survival is temporal, not merely a static-frame property.

Before preflighting the first candidate, identify a **meaningful behavioral horizon** for the representation: long enough to expose the motion, phase relationships, recurrence drift or structural behavior that defines the selected phenotype.

Examples:

- a slow membrane may need enough time to show a complete fold / breathing change;
- a repeated family should expose meaningful relative phase behavior among siblings;
- a traveling filament should show the deformation moving through the axial body;
- a recurrent / chaotic system may need a substantially longer horizon to expose collapse, thinning or loss of crossings.

Do **not** hard-code universal frame numbers or one universal duration. The horizon is representation- and phenotype-dependent.

The production invariant is:

```text
choose meaningful horizon H
-> freeze observation contract over H
-> compression preflight over H
-> exact final verification over the same H
```

The observation contract records `H`, the sampled verification frames, the selected elite's brief invariants, and the named defining mathematical relationships.

Preflight and final verification may sample different frame density within `H`, but the final check must not rely on a materially longer behavioral horizon than the promotion decision.

If a longer final horizon reveals a failure that preflight could not see, treat that as a **preflight false pass** and strengthen the horizon before promoting another candidate.

Never shorten `H` after ranking or weaken the named relationships to rescue a compact artifact.

## 3. Preflight candidates adaptively in visual-rank order

Start with the current visual elite.

For each candidate:

1. name the high-leverage mathematical relationships that define its identity;
2. sketch the cheapest plausible semantic compression that preserves those relationships;
3. estimate whether the resulting cause can plausibly fit the practical code budget;
4. if plausible, render the compressed form across the chosen temporal horizon;
5. decide pass/fail on phenotype survival across that horizon;
6. require Grade 1 cause preservation before deployment promotion.

If it passes, stop and promote that candidate to **deployment finalist**.

If it fails, keep it as an artistic discovery and move to the next visually worthwhile candidate, using the same horizon unless that candidate's defining behavior requires a broader one.

Do not hard-code a universal shortlist size. The evidence supports adaptive sequential fallback, not `top 2`, `top 3`, or another fixed K.

Stop fallback when there are no remaining candidates that are artistically worth deployment.

## 4. The preflight is a falsification gate

It answers:

```text
Can this candidate's defining relationships survive the deployment medium over the meaningful behavioral horizon?
```

It does **not** answer:

```text
Which candidate has the smallest source?
Which candidate has the best compressibility score?
```

Do not introduce a scalar `compressibility`, `tweetability`, or `descriptionLengthFitness` objective into creative search.

### Preservation grades

Use the two grades from `references/preservation-contract.md`:

```text
Grade 0
= observable agreement over the frozen observation contract

Grade 1
= Grade 0 + every named defining relationship remains causal / recoverably defined
```

Grade 0 is necessary but **not** sufficient for promotion. A compact artifact that matches sampled frames, occupancy, a qualified shape metric, prototype F1 or another observation while dropping a named cause fails deployment.

Only Grade 1 may be promoted.

Mechanical verification remains a **veto rather than an intention certificate**: a failure blocks deployment; a pass preserves the prior artistic decision but does not establish that the artwork itself was intended or good.

## 5. What counts as a defining relationship

Examples:

- recurrence + residue family + transformed projection;
- shared family law + nonlinear deformation;
- true 2D sampling + fold relationship + negative-space structure;
- axial family + fold law + traveling phase relation;
- morphology parent/attachment relationship required by the brief.

Constants can often move or disappear. High-leverage relationships cannot.

A compact version that keeps the silhouette but loses the causal relationship responsible for the selected identity is a failure.

Temporal persistence can itself be part of the relationship. A recurrent knot that looks correct early but later collapses into a thin glyph has **not** survived compression.

## 6. Full golf happens only after deployment promotion

Once a candidate passes preflight:

1. preserve the named high-leverage relationships;
2. preserve the chosen temporal horizon and observation contract as part of the deployment contract;
3. compress semantically;
4. golf JavaScript representation;
5. verify the complete X-weighted post;
6. execute the exact tweet code;
7. render the exact code across the same meaningful temporal horizon;
8. confirm Grade 0 observation preservation;
9. confirm Grade 1 cause preservation.

Preflight reduces the risk of wasting a full golf pass on the wrong candidate. It does not replace exact final verification.

A final failure inside the already-chosen horizon means the semantic preflight was too optimistic. Return to deployment fallback; do not quietly weaken the phenotype criterion.

## 7. Relationship to the discovery elite

Keep two concepts distinct without turning them into competing fitness functions:

```text
visual elite
= best artistic discovery under the brief

deployment finalist
= highest visually ranked candidate that passes Grade 1 compression-survival preflight
```

Often they are the same candidate.

When they differ, do not demote or rewrite the visual elite. Record that deployment constraints caused fallback.

## 8. Evidence

The description-length timing experiment compared three conditions over 48 shared candidates across family, sheet, filament and recurrence routes:

- late-only pressure: 3 / 4 deployable winners;
- shortlist preflight: 4 / 4;
- early compactness filtering: 4 / 4, but removed 17 / 48 candidates before artistic review.

The adaptive follow-up reused the same archive:

- rank-1-only: 3 / 4;
- adaptive sequential fallback: 4 / 4 with five total preflights;
- fixed top-2 / top-3 / top-5 added no deployment benefit over adaptive fallback.

The fresh v0.14 cold test added a temporal result. On a new recurrence brief, a short preflight window made the artistic winner look deployable, while the longer final-verification horizon exposed later thinning and loss of persistent internal crossing. Aligning the horizons correctly rejected that candidate and promoted the next-ranked recurrence candidate; a fresh sheet control passed at rank 1.

The strongest current policy is therefore:

> **discover and rank freely; apply description length only as an adaptive promotion gate into deployment, freeze the observation/cause contract before compression, require Grade 1 cause preservation, and evaluate preflight and exact verification over the same meaningful behavioral horizon.**
