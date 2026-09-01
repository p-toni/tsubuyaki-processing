# Semantic artistic judge prospective v1 — result

Decision: **SEMANTIC_JUDGE_PROSPECTIVE_INCONCLUSIVE_PROTOCOL_ARTIFACT_LOSS**.

## What was successfully frozen

- Fresh authoritative population: 24 blocks from 8 `755xxx` seeds across recurrence, orbit, and filament.
- Reviewer artifact: `9812890804`, digest `sha256:322e0d41969ea5bde6867eccfaaa6bb60a080d767f2398467e377540f9ef3ffe`.
- Model prediction commitment was created before human review and committed at `3f5b20bd05f834acaca4d6676c140de2da7bf264`.
- Committed prediction-file SHA-256: `3255d18f7f2827427a0647b1f7162d5e8d84c0a362fe17d25d7f004721ba54e0`.
- The commitment explicitly records `identityKeyOpenedBeforeCommitment=false` and `humanRatingsCollectedBeforeCommitment=false`.
- Human review subsequently produced 24 / 24 reviewable and 24 / 24 decisive labels; those labels are frozen in `human-ratings.json`.
- The sealed identity-key artifact was opened only after all human labels were fixed. It contains exactly eight recurrence, eight orbit, and eight filament blocks.

## Protocol failure

The exact model-prediction JSON bytes were intentionally stored outside the repository. The SHA-256 commitment survived, but the committed preimage did not survive into the continuation context and is not present in the repository or retained experiment artifacts available to the continuation run.

A cryptographic commitment is useful for verifying an already-preserved preimage; the hash alone cannot recover the 24 predictions. Re-judging the reviewer images after the human labels are known would violate the prospective blinding boundary and cannot substitute for the committed predictions.

Therefore the following preregistered quantities cannot be computed honestly:

- decisive model accuracy;
- one-sided exact binomial p-value;
- per-route decisive accuracy;
- model tie/abstention rate.

The preregistered `SEMANTIC_JUDGE_PROSPECTIVE_PROMISING` / `SEMANTIC_JUDGE_PROSPECTIVE_NOT_PROMISING` gate is therefore **not evaluated** for this run.

## Interpretation

This run is not evidence that the semantic judge succeeded, and it is not evidence that the semantic judge failed. The scientific failure is artifact custody: the experiment preserved the commitment but not the revealable committed object.

Do not reconstruct predictions from the now-consumed reviewer images, tune the prompt on these labels, change thresholds, or treat these 24 labels as prospective evidence in a rerun.

## Correct next boundary

Repeat the same first prospective semantic-judge question on a completely fresh, untouched population. Keep the judge prompt and frozen gate unchanged. Change only custody mechanics so the exact committed prediction object is durably retained before human review and can be revealed afterward.

The rerun is a replacement for this invalid first prospective test, **not** the positive-result second replication described in the original preregistration.
