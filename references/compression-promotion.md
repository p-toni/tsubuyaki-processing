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

## 2. Preflight candidates adaptively in visual-rank order

Start with the current visual elite.

For each candidate:

1. name the high-leverage mathematical relationships that define its identity;
2. sketch the cheapest plausible semantic compression that preserves those relationships;
3. estimate whether the resulting cause can plausibly fit the practical code budget;
4. if plausible, render representative times from the compressed form;
5. decide pass/fail on phenotype survival.

If it passes, stop and promote that candidate to **deployment finalist**.

If it fails, keep it as an artistic discovery and move to the next visually worthwhile candidate.

Do not hard-code a universal shortlist size. The evidence supports adaptive sequential fallback, not `top 2`, `top 3`, or another fixed K.

Stop fallback when there are no remaining candidates that are artistically worth deployment.

## 3. The preflight is a falsification gate

It answers:

```text
Can this candidate's defining relationships survive the deployment medium?
```

It does **not** answer:

```text
Which candidate has the smallest source?
Which candidate has the best compressibility score?
```

Do not introduce a scalar `compressibility`, `tweetability`, or `descriptionLengthFitness` objective into creative search.

## 4. What counts as a defining relationship

Examples:

- recurrence + residue family + transformed projection;
- shared family law + nonlinear deformation;
- true 2D sampling + fold relationship + negative-space structure;
- axial family + fold law + traveling phase relation;
- morphology parent/attachment relationship required by the brief.

Constants can often move or disappear. High-leverage relationships cannot.

A compact version that keeps the silhouette but loses the causal relationship responsible for the selected identity is a failure.

## 5. Full golf happens only after deployment promotion

Once a candidate passes preflight:

1. preserve the named high-leverage relationships;
2. compress semantically;
3. golf JavaScript representation;
4. verify the complete X-weighted post;
5. execute the exact tweet code;
6. render representative times;
7. confirm the defining phenotype still survives.

Preflight reduces the risk of wasting a full golf pass on the wrong candidate. It does not replace exact final verification.

## 6. Relationship to the discovery elite

Keep two concepts distinct without turning them into competing fitness functions:

```text
visual elite
= best artistic discovery under the brief

deployment finalist
= highest visually ranked candidate that passes compression-survival preflight
```

Often they are the same candidate.

When they differ, do not demote or rewrite the visual elite. Record that deployment constraints caused fallback.

## 7. Evidence

The description-length timing experiment compared three conditions over 48 shared candidates across family, sheet, filament and recurrence routes:

- late-only pressure: 3 / 4 deployable winners;
- shortlist preflight: 4 / 4;
- early compactness filtering: 4 / 4, but removed 17 / 48 candidates before artistic review.

The adaptive follow-up reused the same archive:

- rank-1-only: 3 / 4;
- adaptive sequential fallback: 4 / 4 with five total preflights;
- fixed top-2 / top-3 / top-5 added no deployment benefit over adaptive fallback.

The strongest current policy is therefore:

> **discover and rank freely; apply description length only as an adaptive promotion gate into deployment.**
