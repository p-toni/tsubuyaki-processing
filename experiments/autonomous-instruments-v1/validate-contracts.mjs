#!/usr/bin/env node
// CONTRACT-1 validation on archived candidates and counterfeits.
//   node validate-contracts.mjs            full run -> contract-validation.json
//   node validate-contracts.mjs --smoke    crash check only; prints no pass/fail values
//   node validate-contracts.mjs --only=P03-relay
// Node built-ins only. Executes trusted archived sketches; not a sandbox.
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadSketch, transformed } from './lib/runtime.mjs';
import { runContract } from './lib/contract.mjs';
import { counterfeit, COUNTERFEIT_MIMICS } from './lib/transforms.mjs';
import { SHIMS } from './contracts/shims.mjs';

const here = path.dirname(fileURLToPath(import.meta.url)), experiments = path.join(here, '..');
const labels = JSON.parse(fs.readFileSync(path.join(here, 'contracts/labels.json'), 'utf8'));
const smoke = process.argv.includes('--smoke'), only = process.argv.find(a => a.startsWith('--only='))?.slice(7);
const sha = file => createHash('sha256').update(fs.readFileSync(file)).digest('hex');

const names = [...new Set(labels.cases.map(c => c.contract))].filter(n => !only || n === only);
const contracts = Object.fromEntries(await Promise.all(names.map(async n => [n, (await import(`./contracts/${n}.mjs`)).default])));
const load = rel => loadSketch(path.join(experiments, rel), { roleShim: SHIMS[rel]?.fn ?? null });


function evaluate(contract, sketch) {
  const started = performance.now(), results = runContract(contract, sketch);
  return { verdict: results.every(r => r.pass) ? 'pass' : 'fail', seconds: +((performance.now() - started) / 1000).toFixed(1), results };
}

const runs = [];
for (const name of names) {
  const contract = contracts[name];
  const cases = labels.cases.filter(c => c.contract === name), fakes = labels.counterfeits.filter(c => c.contract === name);
  const jobs = smoke ? cases.filter(c => c.label === 'met').slice(0, 1) : cases;
  for (const c of jobs) {
    const r = evaluate(contract, load(c.source));
    runs.push({ contract: name, kind: 'archived', source: c.source, label: c.label, labelRequirements: c.requirements ?? null, ...r });
    console.error(`${name} ${c.source} ${smoke ? (r.results.some(x => x.error) ? 'ERROR ' + r.results.filter(x => x.error).map(x => x.id + ': ' + x.error).join('; ') : 'ran') : r.verdict} (${r.seconds}s)`);
  }
  for (const fake of smoke ? fakes.slice(0, 1).map(f => ({ ...f, kinds: f.kinds.slice(0, 1) })) : fakes) {
    const base = load(fake.base);
    for (const kind of fake.kinds) {
      const sketch = transformed(base, counterfeit(kind, fake.ref), kind), r = evaluate(contract, sketch);
      runs.push({ contract: name, kind: 'counterfeit', counterfeit: kind, mimics: COUNTERFEIT_MIMICS[kind], base: fake.base, ref: fake.ref, expected: 'fail', ...r });
      console.error(`${name} counterfeit ${kind} ${smoke ? (r.results.some(x => x.error) ? 'ERROR ' + r.results.filter(x => x.error).map(x => x.id + ': ' + x.error).join('; ') : 'ran') : r.verdict} (${r.seconds}s)`);
    }
  }
}
if (smoke) process.exit(runs.some(r => r.results.some(x => x.error)) ? 1 : 0);

// Agreement with the archive's own adherence labels and rejection of counterfeits.
const scored = runs.filter(r => r.kind === 'archived' && r.label !== 'uncertain');
const reqPairs = [];
for (const r of runs.filter(r => r.kind === 'archived' && r.labelRequirements)) {
  for (const res of r.results) {
    const lab = r.labelRequirements[contracts[r.contract].requirements.find(q => q.id === res.id)?.label];
    if (lab && lab !== 'uncertain') reqPairs.push({ contract: r.contract, source: r.source, requirement: res.id, label: lab, pass: res.pass });
  }
}
const fakes = runs.filter(r => r.kind === 'counterfeit');
const summary = {
  archivedBriefVerdicts: { scored: scored.length, agree: scored.filter(r => (r.verdict === 'pass') === (r.label === 'met')).length,
    disagreements: scored.filter(r => (r.verdict === 'pass') !== (r.label === 'met')).map(r => ({ source: r.source, label: r.label, verdict: r.verdict, failed: r.results.filter(x => !x.pass).map(x => x.id) })) },
  archivedRequirementVerdicts: { scored: reqPairs.length, agree: reqPairs.filter(p => p.pass === (p.label === 'met')).length,
    disagreements: reqPairs.filter(p => p.pass !== (p.label === 'met')) },
  uncertainCases: runs.filter(r => r.kind === 'archived' && r.label === 'uncertain').map(r => ({ source: r.source, verdict: r.verdict, failed: r.results.filter(x => !x.pass).map(x => x.id) })),
  counterfeits: { total: fakes.length, rejected: fakes.filter(r => r.verdict === 'fail').length,
    accepted: fakes.filter(r => r.verdict === 'pass').map(r => ({ contract: r.contract, counterfeit: r.counterfeit })),
    caughtBy: fakes.map(r => ({ contract: r.contract, counterfeit: r.counterfeit, failed: r.results.filter(x => !x.pass).map(x => x.id) })) },
};
const out = {
  study: 'CONTRACT-1 validation on archives (diagnostic; changes no recorded grade, selection or decision)',
  contracts: Object.fromEntries(names.map(n => [n, sha(path.join(here, `contracts/${n}.mjs`))])),
  labelsSha256: sha(path.join(here, 'contracts/labels.json')), shimsSha256: sha(path.join(here, 'contracts/shims.mjs')),
  summary, runs,
};
const outName = process.argv.find(a => a.startsWith('--out='))?.slice(6) ?? (only ? `contract-validation.${only}.json` : 'contract-validation.json');
fs.writeFileSync(path.resolve(here, outName), JSON.stringify(out, null, 1) + '\n');
console.log(JSON.stringify(summary, null, 1));
