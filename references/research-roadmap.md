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

## Active priority — compact delivery of harder behavior

The actionable gap is a worthwhile readable behavior failing to become a worthwhile compact post within budget. Test compact representation and preflight on fresh briefs involving occlusion or delayed transfer. Leave the completed Weave and Exchange candidates closed; repairing them would not provide fresh evidence.

Use the existing [compression-promotion guidance](compression-promotion.md). Once a worthwhile incumbent exists, test a cheap exact compact version before spending the remaining budget on refinement. If it fails, diagnose whether syntax, representation, or the defining behavior consumes the budget. A simple representation change must preserve the brief's important relationships; reducing the task to fit the limit is a failure.

Before the next comparison, freeze fresh briefs, meaningful horizons, equal candidate and compact-attempt caps, and a decision rule. Compare preflight after the first worthwhile incumbent with the current late-selection timing. Count all runs, retain failures, and measure actual effort where available. Advancement must mean more verified, brief-adherent A/B deliveries without an artistic loss, not merely shorter code or more attempted golf. This extends the small earlier description-length study to harder complete discovery tasks; it is not a new default or a reason to build another runtime.

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

Do not tune against consumed evidence from the closed learned-world-model, late-refinement, independent-restart, generic visual-judge, morphology-context judge, family projected-spectral artistic, compact-symplectic, phase-native, compact-material-grammar, or feedback-value-v1 populations. Their negative results remain evidence, not optimizer input.

## Research discipline

For any decision-changing experiment:

1. state the decision it could change;
2. freeze hypothesis, population, comparison, budget, and advancement rule before results;
3. preserve the full valid archive and exact final artifacts;
4. use fresh evidence for artistic claims;
5. freeze any blinded ratings before unblinding, identifying whether the reviewer is human or a model;
6. close negative branches rather than tuning them against consumed ratings.

The immediate next step is a **fresh comparison of compact preflight timing on harder briefs**. Do not tune the completed pilot or feedback-comparison candidates to improve their recorded grades. Preserve historical protocols and results as evidence; the [older experiment roadmap](../experiments/ROADMAP.md) records an earlier prototype plan.
