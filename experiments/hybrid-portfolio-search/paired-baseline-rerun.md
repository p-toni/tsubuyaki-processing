# Paired baseline rerun

Automated review correctly identified a confound in the first version of this experiment: H1/H2 were fresh draws while the D1/B4 reference outcomes came from the previous experiment.

To reduce that confound, D1 and B4 were rerun on the **same four viable starts** used by the hybrid exploration and with the **same mutation generators**. Each baseline again receives 40 generated challengers.

This is one paired block, not a repeated randomized study. It reduces but does not eliminate candidate-sample variance.

## Deterministic seeds

```text
recurrence D1 rounds: 26082701, 26082702, 26082703, 26082704
recurrence B4:        26082710
family D1 rounds:     26082721, 26082722, 26082723, 26082724
family B4:            26082730
```

## Recurrence

### Paired D1

Start: `Rstart1`.

Promotions:

```text
Rstart1
-> RDP-R1-6
-> RDP-R2-2
-> round 3: no promotion
-> round 4: no promotion
```

Winner: **RDP-R2-2**.

### Paired B4

Starts: `Rstart1..Rstart4`, 10 challengers each.

Winner selected from the basin-1 branch: **RBP-S1-3**.

### Paired interpretation

The paired rerun does **not** rescue the hybrid claim. D1/B4 both remain competitive with or preferable to the tested H1/H2 finalists under the living-knot niche. Exact D1-vs-B4 order is a smaller-margin artistic decision and should not be overclaimed.

The important causal conclusion survives:

> allocating 20 candidates to broad exploration and then applying generic exploitation did not establish a new recurrence frontier.

## Repeated family

### Paired D1

Start: `Fstart1`.

Promotions:

```text
Fstart1
-> FDP-R1-8
-> FDP-R2-8
-> FDP-R3-6
-> round 4: no promotion
```

Winner: **FDP-R3-6**.

### Paired B4

Starts: `Fstart1..Fstart4`, 10 challengers each.

Winner: **FBP-S1-8**.

This fresh B4 winner came from basin 1 rather than the basin-4 winner in the previous breadth experiment. That is itself useful evidence: **small-sample basin identity is noisy**. Basin 4 was still ranked first by the hybrid's 5-candidate exploration phase, but a fresh 10-candidate-per-basin breadth sample produced a strong basin-1 winner.

### Paired interpretation

B4 remains stronger than the tested H1/H2 hybrids for the repeated-family niche. Generic exploitation again tends to walk promising families toward merged botanical morphology instead of preserving distinct related siblings.

## Revised strength of claim

The first experiment wording implied more confidence than one fresh hybrid draw against historical baselines justified.

After the paired rerun, the defensible result is:

```text
hybrid two-phase architecture: plausible
fixed H1/H2 allocations:       not supported
hybrids beat pure strategies:   not supported
basin ranking:                  useful but noisy
main bottleneck:                basin-preserving exploitation
```

The next search experiment should use route-aware trust-region exploitation and should preferably use paired or repeated blocks when comparing allocation policies.
