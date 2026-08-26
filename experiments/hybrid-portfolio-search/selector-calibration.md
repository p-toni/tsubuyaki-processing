# Independent human selector calibration

The blinded panels were generated and their label mappings frozen before the human ranking was collected.

## Fixed mappings

### Recurrence

```text
K7 = D1
M2 = B4
Q9 = H1
```

Human ranking:

```text
K7 > M2 > Q9
=> D1 > B4 > H1
```

### Repeated family

```text
K7 = B8
M2 = H2
Q9 = B4
```

Human ranking:

```text
Q9 > K7 > M2
=> B4 > B8 > H2
```

## Interpretation

This is the first genuinely independent selector signal in the research sequence.

The human ranking agrees with the large-margin conclusions from the model-led experiments:

- recurrence: a pure strategy remains preferable to the tested hybrids;
- repeated family: B4 remains stronger than the tested H2 hybrid;
- the tested hybrids do not establish a new artistic frontier.

The human is **less favorable to recurrence H1** than the model's original `H1 ~= D1` judgment. Therefore the earlier equality claim should be treated as model uncertainty, not as evidence that H1 reached the human-quality frontier.

Family calibration is cleaner: the human order `B4 > B8 > H2` resolves the previously close model comparison in favor of B4.

## Selector policy implication

The evidence supports using model judgment for:

- hard visual regression detection;
- coarse basin triage;
- large-margin pairwise decisions;
- reducing the number of candidates requiring human inspection.

It does **not** support using model preference as a continuous artistic fitness function or trusting small-margin ranks without independent review.
