# Research roadmap

The primary research goal is **autonomous discovery capability**: given a fresh visual intent and a bounded budget, an agent chooses mathematical representations, constructs and inspects animated programs, learns from rendered observations, and delivers a verified compact result without requiring human rescue.

Finished animations are concrete evidence of this capability. A successful discovery must produce worthwhile behavior; reliable unattended execution alone is insufficient. One attractive result does not establish transfer across briefs. An honest failure is an appropriate way to stop, but still counts as an unsuccessful discovery attempt.

Discovery means finding useful original programs and behaviors for the task, not a claim of globally novel mathematics. The current medium remains p5.js and a complete post within 280 raw and X-weighted characters. Readable exploration may exceed that limit before compression.

## Simplest autonomous baseline

Start with the existing agent's coding, rendering, and inspection tools:

```text
choose representation
→ build and inspect a readable sketch
→ use observations to revise or change representation when useful
→ select a worthwhile result or stop with a documented failure
→ compress while preserving cause and motion
→ verify the exact post
```

The separate autonomous search runtime remains optional research machinery. Neither a learned search operator nor new automation is required to test the capability. Organic form and apparent life are the documented starting aesthetic; a filament is one possible representation rather than the destination for every brief.

## What the evidence currently says

Narrow supported claims:

- the [compact-preflight comparison](../experiments/compact-preflight-v1/README.md) delivered 3/4 briefs with early checking and 1/4 with late checking, but the delivered Wake lost artistic quality; its no-regression gate failed, and its late-first, shared-context design does not isolate a causal effect;
- the [rendered-feedback comparison](../experiments/feedback-value-v1/README.md) delivered 4/6 briefs in both arms, with zero adaptive pair wins, one batch preference, three equivalents, and two both-fail pairs; its same-agent, shared-context design does not establish a clean causal effect or broad batch superiority;
- the [first complete discovery pilot](../experiments/autonomous-discovery-pilot-v1/README.md) delivered three different compact studies from five readable candidates, two observation-led revisions, and one compact attempt per brief; all passed the frozen technical checks, with provisional B grades from the same agent that authored the briefs and candidates;
- intrinsic-1D native/spectral mixed search produced artistically preferred portfolios on its tested surface;
- target-blind max-dispersion improved the tested three-item delivery shortlist;
- in the complete filament workflow audit, all nine research candidates selected from brief-adherent shortlists were spectral, but none survived the frozen two-attempt <=280-character compression boundary with Grade-0/1 identity intact;
- the simplified filament workflow completed 12/12 verified posts with only 16 exploratory renders, while the research workflow produced 0/12 deployable finals after 240 generated attempts plus compression;
- three deployment-native compact enrichment strategies are now artistically negative on fresh evidence:
  - `compact-symplectic-material-v1`: SHEAR3 0/12 vs NATIVE 12/12;
  - `phase-native-material-v1`: PHASEPACK 2/10 decisive vs NATIVE 8/10, with two equivalents;
  - `compact-material-grammar-portfolio-v1`: MIXED12 4/12 vs NATIVE12 8/12 under equal candidate budget and the supported max-dispersion reducer;
- in the compact-grammar portfolio, material reached delivery in 10/12 mixed shortlists, so its negative result is not explained by the reducer hiding every material candidate;
- mechanically positive interventions do not automatically create artistic value;
- the tested generic visual and morphology-context judges are not reliable artistic authorities.

These results apply to their tested representations and budgets. They do not establish a universal search policy, automatic aesthetic scorer, or general autonomous discovery capability.

## Completed milestone — exercise the complete discovery loop

The [pilot archive](../experiments/autonomous-discovery-pilot-v1/README.md) preserves Hollow, Fronds, and Gather, all initial candidates and revisions, the selection decisions, exact posts, and ten-second clips. No human selection or formula correction was needed. Compact lengths were 233, 212, and 230 X-weighted characters. Every frame matched its readable source geometrically, and all 48 sampled PNG pairs were byte-identical.

The existing agent-plus-tools loop is a feasible baseline across these three representations. The pilot did not test representation switching, recovery from a failed brief, or the benefit of feedback against a comparison arm. The agent authored its own briefs and grades. Visual review used sampled stills; full-frame computation and playback checks do not substitute for perceptual assessment of every moment. Its three provisional successes are not a general reliability estimate.

## Completed comparison — value of rendered feedback

The [feedback-value-v1 archive](../experiments/feedback-value-v1/README.md) preserves six fresh briefs, all 41 charged candidates, selections made before character counting, and twelve compact attempts. Both arms had caps of four readable candidates and two compact attempts per brief. Batch sources were committed before rendering; adaptive generation closed before the remaining batch renders. Identical programs reused evidence, leaving 28 unique readable renders.

Adaptive revision produced six provisional B selections from 17 candidates; batch produced four from 24. The two extra adaptive readable successes, Weave and Exchange, exceeded the character limit after both allowed attempts. One failed Weave attempt also had a syntax error. These remain failed compact runs, not proof of an impossible representation. Both arms delivered four verified posts. The batch Twist had the only clear final preference; three pairs were equivalent and two had no successful delivery. All eight posts passed 720-frame geometry/style checks and 128 sampled raster comparisons.

The advancement rule required at least four adaptive wins, at most one batch win, and no fewer adaptive deliveries. It failed. Keep the small first-candidate loop and revise for concrete observed shortcomings. Do not require a fixed candidate count, expand revision machinery, or adopt a universal batch policy from this result. Fewer adaptive candidates do not establish lower total cost: active reasoning and review effort were not measured.

The same agent authored both arms and remembered its planned alternatives. Source commitments prevented batch edits but could not remove shared-context effects. Briefs and grades were model-authored; visual review used sampled stills. Neither clean causal isolation nor independent artistic validation has been demonstrated.

## Completed comparison — compact preflight timing

The [compact-preflight-v1 archive](../experiments/compact-preflight-v1/README.md) preserves four fresh briefs involving occlusion or delayed response. Both arms had caps of four readable candidates and two compact attempts per brief. The late arm froze all readable selections before either arm wrote compact code. The early arm then reused that exploration, charging each use, and could change representation after failed preflight. This gave the early arm knowledge of the late trajectory; source commitments cannot eliminate that limitation.

Early delivered 3/4 and late 1/4: two early pair wins, one equivalent pair, and one both-fail pair. Aperture recovered through a shared representation without a clear artistic loss. Relay fit through algebra and syntax changes available to both arms. Thread remained overlength. Wake fit early, but its material and exciter were less expressive than the late readable selection. All selected studies received provisional B grades, none A. All four deliveries passed 720-frame checks and 64 logical sampled image comparisons, with 48 unique pairs.

The advancement gate required at least two early wins, zero late wins, no fewer early deliveries, and no clear artistic regressions. **It failed on Wake's artistic loss.** Both arms consumed eight compact attempts; early used thirteen readable candidates and late eight. Active reasoning and review costs were not measured, so equal attempt caps do not establish equal total cost. Keep the production policy unchanged and close this population.

## Active priority — preserve artistic quality in compact representations

The actionable gap is a worthwhile readable behavior becoming too expensive to express compactly, or losing artistic expression when its representation changes. The clean Aperture recovery is evidence that a better shared construction can help; Wake shows why brief adherence and length alone are insufficient. Another timing sweep would leave that gap unresolved.

Start with one fresh difficult brief and two meaningfully different mathematical representations, using the existing agent and tools. Freeze the brief's defining relationships, horizon, a small candidate and compact-attempt budget, and the decision rule before rendering. Inspect and grade readable candidates before counting compact code. Preserve the more expressive readable incumbent for comparison even if it cannot be delivered. Do not reuse or repair the closed Thread or Wake candidates as fresh evidence.

Use the existing [compression-promotion guidance](compression-promotion.md). Test whether a shared construction can retain the important causal relationships, material, and motion in a complete post. Keep the smallest representation that achieves the artistic objective; shorter code alone is not a win. Stop if the remaining budget cannot produce a verified A/B delivery without a clear artistic loss against the readable incumbent. Record a failure instead of weakening the brief or upgrading a grade after a length pass.

A successful case would support a fresh replication across different briefs, not a universal policy. Count actual candidates and attempts, preserve failures and known effort, and distinguish artistic judgments from execution checks. No larger candidate quota, automatic aesthetic judge, or new runtime is needed for this next step.

Independent calibration would strengthen artistic claims without becoming a prerequisite for operating the loop. A separate review prompt does not create independent evidence. More filament experiments, learned search operators, and automatic aesthetic judges remain parked.

## Bottleneck discipline

Classify evidence before proposing a remedy:

| Observation | Next research surface |
| --- | --- |
| No inspected candidate is compelling | Mathematical representation and generation |
| Good candidates exist but do not reach delivery | Selection and delivery |
| Rendered feedback leads to repeated ineffective edits | Causal diagnosis and revision strategy |
| A good selected candidate loses identity in final form | Representation and compression |
| Good results require disproportionate work | Stopping and workflow simplification |

The earlier filament workflow audit classified nine briefs as `COMPRESSION_REPRESENTATION`. The compact-grammar study showed the new shallow material did reach delivery. Those are findings about the tested families, not a diagnosis for every fresh brief. Compare a proposed remedy with the simple autonomous baseline on fresh tasks at comparable total cost before adopting it.

## Conditional branches

### Selection and delivery

Reopen only when preserved evidence shows good generated candidates are routinely missed. Compare reducers on the same completed archive. Max-dispersion is supported only on its tested shortlist surface and does not become search-parent or route-allocation authority by implication.

Any future automatic preference learner must be trained on labels matching its actual decision, represent equivalence/uncertainty, and be evaluated prospectively on fresh evidence independently of fitting. Label model-only evidence accordingly; do not present subjective self-grades as a validated scalar reward.

### Recurrent learned discovery operator

The Sotaku-inspired recurrent **learned search operator** remains parked.

Reopen it only if a complete-workflow study using promising compact representations shows that useful final-post representations exist but current transitions repeatedly fail to reach them. Its first valid test remains isolated: weight-tied recurrent transition vs current mutation and equal-compute untied controls, with stability beyond training horizon and final-artifact evidence.

An experiment using recurrence inside the artwork does not satisfy that reopening condition. It tests an artwork representation, not a learned search transition.

## Closed populations

Do not tune against consumed evidence from the closed learned-world-model, late-refinement, independent-restart, generic visual-judge, morphology-context judge, family projected-spectral artistic, compact-symplectic, phase-native, compact-material-grammar, feedback-value-v1, or compact-preflight-v1 populations. Their negative results remain evidence, not optimizer input.

## Research discipline

For any decision-changing experiment:

1. state the decision it could change;
2. freeze hypothesis, population, comparison, budget, and advancement rule before results;
3. preserve the full valid archive and exact final artifacts;
4. use fresh evidence for artistic claims;
5. freeze any blinded ratings before unblinding, identifying whether the reviewer is human or a model;
6. close negative branches rather than tuning them against consumed ratings.

The immediate next step is a **small fresh test of quality-preserving compact representations**. Do not tune the completed pilot, feedback-comparison, or preflight-comparison candidates to improve their recorded grades. Preserve historical protocols and results as evidence; the [older experiment roadmap](../experiments/ROADMAP.md) records an earlier prototype plan.
