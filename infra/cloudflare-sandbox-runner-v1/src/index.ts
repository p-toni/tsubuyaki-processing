import { WorkflowEntrypoint, type WorkflowEvent, type WorkflowStep } from "cloudflare:workers";
import { getSandbox, type Sandbox as SandboxHandle } from "@cloudflare/sandbox";

export { Sandbox } from "@cloudflare/sandbox";

const REPOSITORY = "https://github.com/p-toni/tsubuyaki-processing.git";
const FROZEN_REF = "cfb6153570a8b72dc97d54f9a7b1c81bad0702a1";
const REPO_DIR = "/workspace/tsubuyaki-processing";
const PYTHON = `${REPO_DIR}/.venv/bin/python`;
const ARM_VALUE = "YES-OPEN-FROZEN-SEEDS";
const ROUTES = ["recurrence", "orbit", "family", "sheet", "filament"] as const;
const SEED_GROUPS = [
  [2003, 2011, 2017, 2027],
  [2029, 2039, 2053, 2063],
  [2069, 2081, 2083, 2087],
  [2089, 2099, 2111, 2113],
  [2129, 2131, 2137, 2141],
  [2143, 2153, 2161, 2179],
  [2203, 2207, 2213, 2221],
  [2237, 2239, 2243, 2251],
] as const;
const FRESH_SEEDS = SEED_GROUPS.flat();
const EXPECTED_FRESH = new Set(FRESH_SEEDS);

type Route = (typeof ROUTES)[number];
type Mode = "smoke" | "fresh";
type Params = { mode?: unknown };
type RunnerEnv = Env & { FRESH_CONFIRMATION_ARMED?: string };
type JsonObject = Record<string, unknown>;

type BlockResult = {
  route: Route;
  group: number;
  seeds: number[];
  records: JsonObject[];
};

type BlockSpec = {
  route: Route;
  group: number;
  seeds: readonly number[];
};

const NO_RETRY = {
  retries: { limit: 0, delay: "1 second", backoff: "constant" as const },
  timeout: "45 minutes",
};

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function asObject(value: unknown, label: string): JsonObject {
  assert(typeof value === "object" && value !== null && !Array.isArray(value), `${label} must be an object`);
  return value as JsonObject;
}

function parseObject(text: string, label: string): JsonObject {
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch (error) {
    throw new Error(`${label} emitted invalid JSON: ${String(error)}\n${text.slice(0, 1000)}`);
  }
  return asObject(parsed, label);
}

function validateMode(payload: Params): Mode {
  const mode = payload?.mode;
  assert(mode === "smoke" || mode === "fresh", "payload.mode must be exactly 'smoke' or 'fresh'");
  return mode;
}

function safeId(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9-]/g, "-").slice(0, 90);
}

async function execChecked(sandbox: SandboxHandle, command: string, label: string): Promise<string> {
  const result = await sandbox.exec(command);
  if (!result.success || result.exitCode !== 0) {
    throw new Error(
      `${label} failed with exit ${result.exitCode}\nstdout:\n${result.stdout}\nstderr:\n${result.stderr}`,
    );
  }
  return result.stdout;
}

async function prepareRepository(sandbox: SandboxHandle): Promise<void> {
  await execChecked(
    sandbox,
    [
      "set -euo pipefail",
      `rm -rf ${REPO_DIR}`,
      `git clone --filter=blob:none --no-checkout ${REPOSITORY} ${REPO_DIR}`,
      `cd ${REPO_DIR}`,
      `git checkout --detach ${FROZEN_REF}`,
      `test \"$(git rev-parse HEAD)\" = \"${FROZEN_REF}\"`,
      "python3.12 -c 'import sys; assert sys.version_info[:2] == (3, 12)'",
      "/root/.local/bin/uv venv --python 3.12 .venv",
      "/root/.local/bin/uv pip install --python .venv/bin/python -r prototypes/autonomous-discovery/requirements.txt",
      ".venv/bin/python -c 'import sys; assert sys.version_info[:2] == (3, 12)'",
    ].join(" && "),
    "prepare pinned repository",
  );
}

function validateCommonRecord(record: JsonObject): void {
  assert(record.mechanismFrozen === true, "mechanismFrozen drift");
  assert(record.metric === "sparse-geometry-v1", "metric drift");
  assert(record.sourceMechanism === "experiments/basin-trust-region-v1/run.py", "source mechanism drift");
  assert(record.exploitBudget === 20, "exploitation budget drift");

  const regimes = asObject(record.regimes, "regimes");
  for (const regimeName of ["same-basin", "identity-jump"]) {
    const regime = asObject(regimes[regimeName], `regime ${regimeName}`);
    const policies = asObject(regime.policies, `${regimeName}.policies`);
    const generic = asObject(policies.generic, `${regimeName}.generic`);
    const trust = asObject(policies["trust-region"], `${regimeName}.trust-region`);
    assert(generic.initialCandidate === trust.initialCandidate, `${regimeName} fork candidate drift`);
    assert(generic.candidateCount === 20 && trust.candidateCount === 20, `${regimeName} candidate budget drift`);
    assert(Array.isArray(trust.championFrozenDriftKeys) && trust.championFrozenDriftKeys.length === 0, `${regimeName} trust champion crossed frozen keys`);
  }

  const same = asObject(regimes["same-basin"], "same-basin");
  const sameTarget = asObject(same.target, "same-basin.target");
  assert(Array.isArray(sameTarget.frozenDeltaKeysFromAncestor) && sameTarget.frozenDeltaKeysFromAncestor.length === 0, "same-basin target crossed frozen keys");

  const jump = asObject(regimes["identity-jump"], "identity-jump");
  const jumpTarget = asObject(jump.target, "identity-jump.target");
  assert(Array.isArray(jumpTarget.identityDeltaKeysFromAncestor) && jumpTarget.identityDeltaKeysFromAncestor.length > 0, "identity-jump target did not cross identity boundary");
}

function validateSmoke(record: JsonObject): void {
  validateCommonRecord(record);
  assert(record.seed === 9001, "smoke seed drift");
  assert(record.route === "recurrence", "smoke route drift");
  assert(record.confirmationSeed === false, "smoke incorrectly marked confirmation seed");
  assert(record.freshSearchEvidence === false, "smoke incorrectly marked fresh evidence");
}

function validateFresh(record: JsonObject, route: Route, seed: number): void {
  validateCommonRecord(record);
  assert(record.route === route, `fresh route mismatch for ${route}/${seed}`);
  assert(record.seed === seed, `fresh seed mismatch for ${route}/${seed}`);
  assert(EXPECTED_FRESH.has(seed), `seed ${seed} is outside frozen population`);
  assert(record.confirmationSeed === true, `seed ${seed} not marked confirmation seed`);
  assert(record.freshSearchEvidence === true, `seed ${seed} not marked fresh evidence`);
}

async function runOne(sandbox: SandboxHandle, route: Route, seed: number): Promise<JsonObject> {
  const stdout = await execChecked(
    sandbox,
    `cd ${REPO_DIR} && ${PYTHON} experiments/basin-trust-confirmation-v1/run.py --route ${route} --seed ${seed}`,
    `confirmation ${route}/${seed}`,
  );
  return parseObject(stdout, `confirmation ${route}/${seed}`);
}

async function withSandbox<T>(env: RunnerEnv, id: string, fn: (sandbox: SandboxHandle) => Promise<T>): Promise<T> {
  const sandbox = getSandbox(env.Sandbox, safeId(id), {
    keepAlive: true,
    enableDefaultSession: false,
  });
  try {
    return await fn(sandbox);
  } finally {
    await sandbox.destroy();
  }
}

async function runSmoke(env: RunnerEnv, instanceId: string): Promise<JsonObject> {
  return withSandbox(env, `cf73-${instanceId}-smoke`, async (sandbox) => {
    await prepareRepository(sandbox);
    const record = await runOne(sandbox, "recurrence", 9001);
    validateSmoke(record);
    return record;
  });
}

async function runBlock(env: RunnerEnv, instanceId: string, block: BlockSpec): Promise<BlockResult> {
  return withSandbox(env, `cf73-${instanceId}-${block.route}-${block.group}`, async (sandbox) => {
    await prepareRepository(sandbox);
    const records: JsonObject[] = [];
    for (const seed of block.seeds) {
      const record = await runOne(sandbox, block.route, seed);
      validateFresh(record, block.route, seed);
      records.push(record);
    }
    const serialized = JSON.stringify(records);
    assert(serialized.length < 900_000, `block ${block.route}/${block.group} exceeds Workflow step result safety margin`);
    return { route: block.route, group: block.group, seeds: [...block.seeds], records };
  });
}

function allBlocks(): BlockSpec[] {
  const blocks: BlockSpec[] = [];
  for (const route of ROUTES) {
    SEED_GROUPS.forEach((seeds, group) => blocks.push({ route, group, seeds }));
  }
  assert(blocks.length === 40, "frozen block count drift");
  return blocks;
}

function validateCompleteRectangle(blocks: BlockResult[]): void {
  assert(blocks.length === 40, `expected 40 blocks, received ${blocks.length}`);
  const cells = new Set<string>();
  for (const block of blocks) {
    assert(block.records.length === 4, `block ${block.route}/${block.group} did not return four records`);
    for (const record of block.records) {
      const route = String(record.route);
      const seed = Number(record.seed);
      const key = `${route}/${seed}`;
      assert(!cells.has(key), `duplicate fresh cell ${key}`);
      cells.add(key);
    }
  }
  assert(cells.size === 160, `expected 160 route×seed cells, found ${cells.size}`);
  for (const route of ROUTES) {
    for (const seed of FRESH_SEEDS) assert(cells.has(`${route}/${seed}`), `missing fresh cell ${route}/${seed}`);
  }
}

async function aggregate(env: RunnerEnv, instanceId: string, blocks: BlockResult[]): Promise<JsonObject> {
  validateCompleteRectangle(blocks);
  return withSandbox(env, `cf73-${instanceId}-aggregate`, async (sandbox) => {
    await prepareRepository(sandbox);
    await execChecked(sandbox, "rm -rf /tmp/confirmation && mkdir -p /tmp/confirmation", "prepare aggregate directory");

    for (const block of blocks) {
      const dir = `/tmp/confirmation/${block.route}-${block.group}`;
      await sandbox.mkdir(dir, { recursive: true });
      for (const record of block.records) {
        const seed = Number(record.seed);
        await sandbox.writeFile(`${dir}/${block.route}-${seed}.json`, `${JSON.stringify(record, null, 2)}\n`);
      }
    }

    const stdout = await execChecked(
      sandbox,
      `cd ${REPO_DIR} && ${PYTHON} experiments/basin-trust-confirmation-v1/aggregate.py --results-dir /tmp/confirmation`,
      "unchanged #73 aggregate",
    );
    const summary = parseObject(stdout, "#73 aggregate");
    const population = asObject(summary.population, "aggregate.population");
    assert(population.completeMasterSeeds === 32, "aggregate master-seed count drift");
    assert(population.routeSeedBlocks === 160, "aggregate route×seed count drift");
    const invariants = asObject(summary.hardInvariants, "aggregate.hardInvariants");
    assert(Object.values(invariants).every((value) => value === true), "aggregate hard invariant failed");
    assert(summary.classification === "CONFIRMED" || summary.classification === "NOT_CONFIRMED", "unexpected aggregate classification");
    return summary;
  });
}

export class ConfirmationWorkflow extends WorkflowEntrypoint<RunnerEnv, Params> {
  async run(event: WorkflowEvent<Params>, step: WorkflowStep): Promise<JsonObject> {
    const mode = validateMode(event.payload ?? {});

    const smoke = await step.do("excluded-seed-substrate-smoke", NO_RETRY, async (ctx) => {
      assert(ctx.attempt === 1, "smoke step retry is forbidden");
      return runSmoke(this.env, event.instanceId);
    });

    if (mode === "smoke") {
      return {
        status: "SMOKE_ONLY_PASS",
        authoritative: false,
        frozenRef: FROZEN_REF,
        freshSeedsOpened: 0,
        smoke,
      };
    }

    assert(this.env.FRESH_CONFIRMATION_ARMED === ARM_VALUE, "fresh confirmation is not explicitly armed");

    const blockPromises = allBlocks().map((block) =>
      step.do(`fresh-${block.route}-${block.group}`, NO_RETRY, async (ctx) => {
        // A failed first attempt may have partially consumed its fixed cells. Never
        // let the Workflow runtime transparently execute those cells a second time.
        assert(ctx.attempt === 1, `retry forbidden for fresh block ${block.route}/${block.group}`);
        return runBlock(this.env, event.instanceId, block);
      }),
    );
    const blocks = await Promise.all(blockPromises);

    const summary = await step.do("reduce-frozen-confirmation", NO_RETRY, async (ctx) => {
      assert(ctx.attempt === 1, "aggregate retry is forbidden");
      return aggregate(this.env, event.instanceId, blocks);
    });

    return {
      status: "FRESH_CONFIRMATION_COMPLETE",
      authoritative: true,
      frozenRef: FROZEN_REF,
      freshSeedsOpened: 32,
      routeSeedBlocks: 160,
      summary,
    };
  }
}

export default {
  async fetch(): Promise<Response> {
    return new Response("No HTTP execution surface. Trigger the Workflow explicitly with Wrangler.", { status: 404 });
  },
};
