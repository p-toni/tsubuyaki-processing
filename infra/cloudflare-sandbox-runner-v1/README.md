# Cloudflare Sandbox fallback runner v1

Status: **prepared, not deployed, not authoritative**.

> **#73 substrate lock:** GitHub Actions began executing the fresh 2000-series population on 2026-08-29 after this fallback was prepared. Therefore Cloudflare must **not** execute `mode=fresh` for #73, even if the arming secret is available. GitHub is now the authoritative substrate for that confirmation. This branch is retained as a reviewed execution pattern for future experiments and for excluded-seed smoke qualification only.

This runner was prepared as an execution escape hatch while GitHub-hosted Actions were globally queued. The queue later resumed before any Cloudflare deployment or execution occurred.

## Scientific contract

The implementation is pinned to the exact #73 experiment commit:

```text
cfb6153570a8b72dc97d54f9a7b1c81bad0702a1
```

It does not select a new policy, seed, route, metric, budget, target regime, or decision rule. It executes the existing repository code at that detached commit.

The implementation contains two modes for reproducibility/reference:

- `smoke` — excluded seed `9001` only; still safe to use for substrate qualification;
- `fresh` — the exact preregistered 32 × 5 #73 population; **historical/reference only now that GitHub has opened those seeds. Do not arm or run it.**

`fresh` was designed to fail closed unless the deployment has a Cloudflare secret named `FRESH_CONFIRMATION_ARMED` with the exact value:

```text
YES-OPEN-FROZEN-SEEDS
```

That secret must not be created for #73 now.

No public HTTP endpoint can start a run. Workflow instances are triggered explicitly with Wrangler or the Cloudflare dashboard.

## Why Sandbox + Workflows

- Sandbox provides isolated Linux containers, Git, filesystem access, and command execution.
- Workflows provides durable orchestration without request wall-clock coupling.
- The 40 route×four-seed blocks map to independent parallel workflow steps.
- Every block clones the public repository and checks out the pinned commit in detached HEAD state before installing dependencies.
- Fresh steps disable automatic retries so a transport failure cannot silently execute a fresh block twice.
- Excluded-seed smoke and aggregation are evidence-safe to retry.
- A separate aggregate sandbox writes all 160 returned JSON cells and invokes the unchanged `experiments/basin-trust-confirmation-v1/aggregate.py` reducer.

## Runtime parity gate

GitHub #73 was preregistered on CPython 3.12. The custom Sandbox image installs a uv-managed CPython 3.12 and the workflow refuses to proceed unless:

```text
python3.12 reports major.minor == 3.12
HEAD == cfb6153570a8b72dc97d54f9a7b1c81bad0702a1
```

The excluded smoke seed must then pass the same structural invariants as the GitHub workflow before any scientific runner derived from this template is trusted.

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

## Future experiment reuse

For a future fixed-sample experiment, copy this pattern **before** its fresh population is opened and replace all of the following under a new version/branch:

- frozen Git commit;
- seed population;
- route/block rectangle;
- smoke invariants;
- unchanged reducer path;
- arming secret name/value;
- Workflow name.

The substrate decision must be made before that experiment opens its fresh population. Once any substrate begins the fresh run, all alternative substrates become non-authoritative for that same population.

## Non-goals

This branch does not:

- change #73's statistical rule;
- authorize a second execution of #73 fresh seeds;
- replace GitHub permanently;
- change production/default artistic search;
- change the repertoire architecture in #74.
