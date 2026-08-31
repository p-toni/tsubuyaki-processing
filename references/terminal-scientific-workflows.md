# Terminal scientific workflows

## Purpose

A scientific workflow becomes **terminal** once its authoritative result has been persisted and its preregistered decision boundary has closed the experiment.

At that point CI must not behave as though the original scientific population is still runnable.

## Contract

For a terminal experiment:

1. the authoritative `research-results/.../results.json` remains immutable;
2. the historical source, workflow, seed population, and reduction logic remain recoverable from the authoritative head recorded by the result and from git history;
3. the current GitHub Actions workflow must not regenerate smoke, calibration, or authoritative scientific seeds;
4. `workflow_dispatch` is archive verification only, not a rerun escape hatch;
5. pull requests touching the terminal experiment, its result, or its workflow run a small archive-integrity check;
6. archive integrity verifies the exact authoritative result blob and terminal decision;
7. later changes to shared runtime dependencies do not retroactively invalidate historical evidence and therefore do not trigger the terminal workflow;
8. a new scientific test requires a new experiment/version, fresh namespace, new preregistration, and a new workflow.

## Why

Previously several completed semantic workflows kept broad `prototypes/autonomous-discovery/**` PR triggers while their preflight intentionally asserted that no persisted result existed. Once results were archived, any unrelated runtime change therefore produced a red check whose only meaning was “correctly refusing to rerun consumed evidence.”

That was scientifically safe but operationally misleading.

Terminalization preserves the safety property and removes the false failure mode: consumed evidence cannot reopen because the seed-generating jobs no longer exist in the current workflow definition.

The original workflows remain available at their authoritative historical commits for audit and reconstruction, but not for accidental execution.
