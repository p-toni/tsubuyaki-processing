# Phenotype evidence authority v1

## Bug found while integrating v3 evidence

The v3 review bundle correctly sealed anonymous A/B rows to phenotype fingerprints, but its legacy decoder returned only `a` / `b` labels. Because the pair id is order-independent, that label is not sufficient for safe replay when the same phenotype pair is later presented in reversed candidate order.

The artifact contained enough information; the replay representation was wrong.

## Repair

New research-only evidence path:

```text
v3 blinded review artifact
→ decode winning phenotype fingerprint (or tie)
→ resolve strong human / independent evidence by fingerprint
→ orient fingerprint to current candidate a/b order
→ authorize promotion only if orientation is unambiguous
```

Legacy v3 `PreferenceEvidence` and its decoder are left untouched for historical reproducibility.

## Authority rules

- hard mathematical validity can reject an invalid candidate immediately;
- strong `human` / `independent-model` phenotype evidence can promote;
- `same-model` and deterministic proxy preferences are advisory only;
- low-confidence human/independent evidence cannot promote;
- missing evidence queues a v3 review bundle and returns tie/defer;
- conflicting authoritative sources return tie/defer;
- pixel-identical phenotype pairs return tie/defer;
- no scalar preference score is introduced.

## Tests

```text
human winner survives A/B reversal               PASS
same-model strong vote cannot promote            PASS
low-confidence human vote cannot promote         PASS
conflicting authoritative sources defer          PASS
missing evidence queues review, no promotion      PASS
hard validity remains authoritative               PASS
```

## Next integration

Use `EvidenceAuthoritySelector` as the promotion selector in the route-screened adaptive flow. Advisory selectors can still be attached for review prioritization / diagnostics, but their verdict cannot replace an incumbent.
