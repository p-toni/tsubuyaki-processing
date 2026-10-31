# <Study name> — prospective protocol

*Copy this directory to `experiments/<study>-v1/`, fill every section, run the
checks, and commit before any solver, judge, or render runs. Everything below runs
without human involvement. Commands are relative to
`experiments/autonomous-instruments-v1/`.*

## 1. Decision

- **Decision this study can change:** <the policy, skill rule, or default at stake>
- **Default if the result is inconclusive:** <what stays unchanged>
- **Smallest effect worth adopting:** <for example +15 points of verified delivery>

## 2. Learning-progress checks

All four must pass before freezing. Record each command's output in the commit.

| Check | Command | Passes when |
| --- | --- | --- |
| **Forecastable?** | `node forecasts.mjs validate ../<study>/forecasts.json` | valid, and at least 50% of forecasts fall within 0.1–0.9. Otherwise redesign or skip. |
| **Valid instrument?** | `node brief-bank.mjs validate <bank>` and the current judge card | every brief entry is valid. Quality outcomes use only distinctions the judge card lists as gateable. |
| **Powered?** | `node power.mjs --briefs=<n> --runs=<r> --base=<p> --effect=<e> --min-power=0.5` | power is at least 0.5 at the smallest effect worth adopting (aim for 0.8); record the false-pass rate. |
| **Frontier?** | competence map from the benchmark | intervention briefs come from strata with baseline success of 30–70%. Other strata are regression guards. |

## 3. Roles and sessions

Each role runs in a fresh session and sees only what is listed.

| Role | Sees | Never sees |
| --- | --- | --- |
| Brief author | the stratum definitions | solvers' work, archive grades |
| Solver (one session per arm and run) | its brief, the skill, its arm's instructions | contracts, reference solutions, other arms, sealed material |
| Judge (one session each; at least two models) | the judge package | sources, archives, the sealed key, other judges |
| Auditor | everything, after judgments are committed | — |

**Custody:** commit the bank manifest, `forecasts.json`, and judge-package
manifest hashes before any run. Keep bank content and keys out of solver and judge
sessions. Verify with `node brief-bank.mjs verify` before scoring.

## 4. Arms and budget

- **Arms:** <baseline as now; treatment changes exactly one thing>
- **Caps per run:** <readable candidates, compact attempts, wall time>
- **Runs per arm and brief:** <r>, independent sessions
- **Stopping:** <a run may stop early when no concrete improvement remains>

## 5. Outcomes and gate (frozen)

- **Primary (objective):** verified, contract-passing delivery: exact
  readable/compact equivalence, ≤ 280 raw and X-weighted characters, and every
  executable brief requirement passing.
- **Secondary:** panel preference, only at gateable distinctions (judge card
  version <v>).
- **Recorded:** session cost, readable and compact attempts, forecast trajectory
  of each candidate.
- **Gate:** <test, alpha, and direction from §2's power check>. A failed gate keeps
  the default. Report its likelihood ratio, not only pass or fail.

## 6. Rigor tier

- **Screening:** forecasts, contracts, panel judgments, and exact verification of
  delivered posts. No clips, galleries, or playback QA.
- **Confirmation or promotion:** add the full custody of earlier studies,
  including 720-frame audits, byte-identical sampled renders, and clips.

This study is: <screening | confirmation>.

## 7. Claims

Label every claim by its instrument: *mechanically verified*,
*contract-verified*, or *panel-judged (judge card <version>)*. None is human
validation.

## 8. Closure

Freeze results before documentation. Score `forecasts.json` with
`node forecasts.mjs score`. Do not tune or rescore this population afterward.
Labeled mechanism diagnostics that cannot change a recorded outcome remain allowed.
