# Cloudflare Sandbox fallback runner v1

Status: **prepared, not deployed, not authoritative**.

This is an execution escape hatch for the frozen basin trust confirmation in PR #73 if GitHub-hosted Actions remain unavailable. It must not be used to open the fresh confirmation population until the project explicitly chooses Cloudflare as the authoritative substrate for that experiment.

## Scientific contract

The runner is pinned to the exact #73 experiment commit:

```text
cfb6153570a8b72dc97d54f9a7b1c81bad0702a1
```

It does not select a new policy, seed, route, metric, budget, target regime, or decision rule. It executes the existing repository code at that detached commit.

The only allowed modes are:

- `smoke` — excluded seed `9001` only; safe substrate qualification;
- `fresh` — the exact preregistered 32 × 5 confirmation population from #73.

`fresh` is fail-closed unless the deployment has a Cloudflare secret named `FRESH_CONFIRMATION_ARMED` with the exact value:

```text
YES-OPEN-FROZEN-SEEDS
```

No public HTTP endpoint can start a run. Workflow instances are triggered explicitly with Wrangler or the Cloudflare dashboard.

## Why Sandbox + Workflows

- Sandbox provides isolated Linux containers, Git, filesystem access, and command execution.
- Workflows provides durable orchestration without request wall-clock coupling.
- The 40 route×four-seed blocks are independent workflow steps and can execute concurrently.
- Every block clones the public repository and checks out the pinned commit in detached HEAD state before installing dependencies.
- Fresh steps disable automatic retries: a transport failure fails the run rather than silently executing a fresh block twice.
- A separate aggregate sandbox writes all 160 returned JSON cells and invokes the unchanged `experiments/basin-trust-confirmation-v1/aggregate.py` reducer.

## Runtime parity gate

GitHub #73 was preregistered on CPython 3.12. The custom Sandbox image installs a uv-managed CPython 3.12 and the workflow refuses to proceed unless:

```text
python3.12 reports major.minor == 3.12
HEAD == cfb6153570a8b72dc97d54f9a7b1c81bad0702a1
```

The excluded smoke seed must then pass the same structural invariants as the GitHub workflow before any fresh block is allowed to run.

## Deployment prerequisites

Cloudflare Sandbox/Containers requires Workers Paid. Docker must be available on the machine that runs `wrangler deploy` when the config points at the local Dockerfile.

From this directory:

```bash
npm install
npm run check
npx wrangler deploy
```

The package and container image are pinned to the same stable Sandbox SDK release line.

## Safe smoke

Trigger only the excluded smoke run:

```bash
npx wrangler workflows trigger tsubuyaki-basin-confirmation-v1 '{"mode":"smoke"}'
```

Inspect it with:

```bash
npx wrangler workflows instances describe tsubuyaki-basin-confirmation-v1 latest
```

This mode never touches a 2000-series confirmation seed.

## Fresh activation — only after explicit substrate decision

1. Stop/neutralize any still-queued GitHub #73 scientific run so only one substrate can open the population.
2. Verify a deployed `smoke` workflow completed successfully.
3. Arm the deployment interactively:

```bash
npx wrangler secret put FRESH_CONFIRMATION_ARMED
# enter: YES-OPEN-FROZEN-SEEDS
```

4. Trigger exactly once:

```bash
npx wrangler workflows trigger tsubuyaki-basin-confirmation-v1 '{"mode":"fresh"}'
```

5. Treat the Workflow output's unchanged #73 aggregate classification as authoritative.
6. Delete/disarm the secret after completion.

## Non-goals

This branch does not:

- change #73's statistical rule;
- run any fresh seed merely by being merged or deployed;
- replace GitHub permanently;
- add a second result if GitHub later runs the same population;
- change production/default artistic search;
- change the repertoire architecture in #74.
