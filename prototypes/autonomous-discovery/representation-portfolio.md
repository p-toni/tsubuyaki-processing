# Representation Portfolio Prototype

This layer prepares the next controlled experiment: **route-first selection vs equal-allocation representation portfolio** under a matched generation-attempt budget and the existing phenotype-safe artistic judge.

It is experimental infrastructure only. It does not change `SKILL.md`, production discovery-state, compression policy, or the meaning of artistic promotion.

## Canonical autonomous representations

The prototype now has four math-first adapters:

- `recurrence` — existing recurrent/filament-like living form, behavior preserved;
- `family` — existing repeated attached family, behavior preserved;
- `sheet` — true 2-D sampled membrane with route-specific dimensionality checks;
- `filament` — intentional 1-D axial ribbon with route-specific axiality checks.

`morphology` remains deliberately outside this first portfolio. It needs the semantic activation gate established by the earlier morphology-route experiment before becoming a generic portfolio arm.

## Representation-local random streams

Portfolio arms use:

```text
SHA256(master seed, representation id, representation version, stream id)
```

Adding/reordering another representation cannot perturb a route's candidate stream. Route-first and portfolio therefore share the same prefix of candidate proposals for the same representation; the treatment is budget allocation / representation optionality, not unrelated RNG drift.

The legacy `run.py` search path keeps its existing shared-RNG behavior.

## Exact policy budget

`total-budget` counts **every candidate-generation attempt**, including invalid candidates.

`route-first` spends the full budget in `brief.route_first`.

`portfolio-equal` requires the budget to divide evenly across all `eligible_routes` and gives each representation an equal attempt budget.

Each arm:

```text
2 viable-start attempts when possible
→ round-robin local incumbent challenges
→ periodic broader numeric perturbation every fifth mutation
→ route-local artistic frontier
```

The deterministic proxy can reject invalid candidates or make clear coarse decisions, but unresolved artistic comparisons escalate through the existing phenotype-safe queue/model judge.

## Brief shape

See `portfolio-brief.example.json`:

```json
{
  "name": "...",
  "artistic_intent": "...",
  "eligible_routes": ["recurrence", "family", "sheet", "filament"],
  "route_first": "sheet",
  "bbox_target": [0.55, 0.82]
}
```

The example is a smoke brief, **not** a confirmatory experiment brief.

## Run one policy

```bash
python portfolio.py \
  --brief portfolio-brief.example.json \
  --seed 12345 \
  --policy portfolio-equal \
  --total-budget 48 \
  --out _generated/portfolio \
  --judge-queue _generated/q0
```

Route-first uses the same command with `--policy route-first`.

## Run the paired experiment harness

```bash
python paired_portfolio_experiment.py \
  --brief portfolio-brief.example.json \
  --seed 12345 \
  --total-budget 48 \
  --out _generated/paired-r0 \
  --judge-queue _generated/q0
```

The harness runs both policies under the same block seed and budget. It does **not** compare provisional policy champions while either policy still has an unresolved artistic frontier.

After judging `q0/decisions-template.json`, replay with a fresh queue:

```bash
python paired_portfolio_experiment.py \
  --brief portfolio-brief.example.json \
  --seed 12345 \
  --total-budget 48 \
  --out _generated/paired-r1 \
  --blind-decisions-dir _generated/q0 \
  --judge-queue _generated/q1
```

For later rounds, pass every completed queue; the cumulative ledger rejects conflicting decisions:

```bash
--blind-decisions-dir _generated/q0 \
--blind-decisions-dir _generated/q1 \
--blind-decisions-dir _generated/q2
```

Once both policy frontiers are singular, the same blinded selector is asked for the final route-first-vs-portfolio comparison. If unresolved, that final pair appears in the next queue without exposing policy or representation identity to the evaluator.

## Outputs

Each policy writes:

- `representation_champions.png`
- `finalists.png`
- `winner_timeline.png`
- `portfolio_report.json`
- `portfolio_state.json`

The paired harness also writes `paired_report.json` with matched budgets, arm costs, internal frontier status, and final policy comparison when available.

## Regression

```bash
python test_checkers.py
python test_selector.py
python test_judge_queue.py
python test_multimodal_judge.py
python test_representation_portfolio.py
```

The new regression covers:

- frozen recurrence/family seed + rendered-phenotype parity sentinels;
- valid starts for all four autonomous math-first representations;
- topology-breaking sheet/filament adversaries;
- representation-local RNG determinism;
- common-random-prefix behavior across shallow/deep arm budgets;
- exact equal attempt-budget accounting;
- evaluator-facing queue blindness;
- cumulative phenotype-safe decision replay.

## Next scientific step

Do not tune the allocator yet. Freeze a small set of new development/pilot briefs and compare:

```text
route-first
vs
four-route equal portfolio
```

under matched total attempt budgets, with final blinded artistic preference as the primary outcome. Only if representation diversity itself shows value should the next experiment test adaptive representation racing.
