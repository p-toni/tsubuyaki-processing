# Semantic empirical-memory hybrid causal replication v1 — result

**Decision:** `EMPIRICAL_MEMORY_REFINEMENT_NOT_REPLICATED`  
**Research-line status:** `STOPPED`

Authoritative workflow run: `33350686624`  
Authoritative experiment head: `0e012ecd6939f037563cd36400d73588556f087d`  
Aggregate artifact: `9743637929`  
Artifact ZIP digest: `sha256:4da6aa129ec9be86104150313ab03d534b145bdd40d843d579bfdf6408f033e3`

The complete fresh 20-seed × 8-concept rectangle passed every hard invariant. No seed-level semantic outcome was inspected before the aggregate reducer completed.

This was the preregistered final causal replication of the exact 48-breadth + 12-refinement architecture. The mean and memory arms shared the same 48-render prefix, same six parents, same 384 candidate proposals, same 60-render budget and same final semantic reranker. Only proposal ranking differed.

## Aggregate evidence

- empirical memory vs route/action mean: **-0.0009520** held-out F1;
- one-sided 95% seed lower bound: **-0.0051609**;
- only **3/8** concept means favored memory;
- **all 8/8 leave-one-concept-out memory-vs-mean effects were negative**;
- mean refinement vs breadth: **+0.0132463** F1, lower bound **+0.0079624**;
- memory refinement vs breadth: **+0.0122943** F1, lower bound **+0.0067237**;
- held-out top-1: breadth **65.0%**, mean hybrid **69.375%**, memory hybrid **69.375%**;
- memory top-1 improvement over breadth: **+4.375 percentage points**, below the frozen +5-point recognition gate;
- mean overlap between proposals selected by the two refinement controllers: **59.01%**.

## Interpretation

The previous 12-seed experiment left open a causal possibility: empirical memory beat breadth continuously and had a positive point estimate over the simpler mean controller, but its direct lower bound crossed zero.

The higher-power fresh replication resolves that ambiguity. The empirical-memory controller does **not** reproduce an advantage over the otherwise identical mean controller. Its point estimate is slightly negative, the uncertainty interval is incompatible with the preregistered positive-effect requirement, and the leave-one-concept-out pattern is uniformly negative.

The robust finding is instead architectural:

> preserve broad search, then spend a bounded suffix on target-reranked local refinement.

That pattern replicated strongly. Both refinement controllers beat pure breadth by roughly +0.012 to +0.013 held-out F1 with positive seed-level lower bounds. The expensive calibrated empirical-memory machinery is not required to obtain the gain.

This also clarifies what the system has and has not learned. The improvement is a search-allocation effect, not evidence that the target-free memory model learned a transferable local action-value function. Recognition remains below the independent advancement threshold, so no human-recognition package is authorized.

## Stop rule

The preregistered stop rule fires.

Do **not** tune another nearby semantic empirical-memory controller, neighborhood size, shrinkage value, action weight, parent count, or 48/12 allocation on the consumed suites. The semantic action-memory research line is closed.

Any future semantic work must begin from a different causal hypothesis. The supported reusable baseline is breadth followed by a small local-refinement suffix using the simpler controller.
