#!/usr/bin/env node
// Brief bank: sealed, stratified briefs with executable contracts.
//
//   node brief-bank.mjs validate BANK_DIR [--out=bank-manifest.json]
//   node brief-bank.mjs verify   BANK_DIR MANIFEST
//
// Each entry is a directory:
//   brief.json    { id, stratum, text, counterfeits: [kinds], counterfeitRef? }
//   contract.mjs  default export: a contract (see lib/contract.mjs)
//   reference.js  a feasible readable solution; declares `role` if the contract needs roles
//   negatives/    optional programs that violate the brief and must fail
//
// An entry is valid when its contract passes the reference, rejects every
// negative and every listed counterfeit of the reference. The reference's
// length forecast gives an independent difficulty score. The manifest's
// hashes are the seal: commit it, keep the bank content away from solver
// sessions, and verify it unchanged before scoring.
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { loadSketch, transformed } from './lib/runtime.mjs';
import { runContract } from './lib/contract.mjs';
import { counterfeit } from './lib/transforms.mjs';
import { forecast, zone } from '../compressibility-forecast-retrospective-v1/forecast-length.mjs';

export const STRATA = { S1: 'one body, one law', S2: 'one body with a traveling or delayed event', S3: 'two coupled actors, or an actor and a medium', S4: 'depth order or occlusion' };
const sha = file => createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const files = dir => fs.readdirSync(dir, { withFileTypes: true }).flatMap(e => (e.isDirectory() ? files(path.join(dir, e.name)) : [path.join(dir, e.name)]));
const verdict = results => ({ pass: results.every(r => r.pass), failed: results.filter(r => !r.pass).map(r => r.id), errors: results.filter(r => r.error).map(r => `${r.id}: ${r.error}`) });

export async function validateEntry(dir) {
  const problems = [], brief = JSON.parse(fs.readFileSync(path.join(dir, 'brief.json'), 'utf8'));
  if (!brief.id) problems.push('brief.json: missing id');
  if (!STRATA[brief.stratum]) problems.push(`brief.json: stratum must be one of ${Object.keys(STRATA).join(', ')}`);
  if (!brief.text) problems.push('brief.json: missing text');
  const contract = (await import(pathToFileURL(path.join(dir, 'contract.mjs')).href)).default;
  if (!contract?.requirements?.length) problems.push('contract.mjs: no requirements');
  const referenceFile = path.join(dir, 'reference.js'), reference = loadSketch(referenceFile);
  const ref = verdict(runContract(contract, reference));
  if (!ref.pass) problems.push(`reference fails its own contract: ${ref.failed.join(', ')}${ref.errors.length ? ` (${ref.errors.join('; ')})` : ''}`);
  const negDir = path.join(dir, 'negatives');
  const negatives = fs.existsSync(negDir) ? fs.readdirSync(negDir).filter(f => f.endsWith('.js')).sort().map(f => {
    const v = verdict(runContract(contract, loadSketch(path.join(negDir, f))));
    if (v.pass) problems.push(`negative ${f} passes the contract`);
    return { file: `negatives/${f}`, rejected: !v.pass, failed: v.failed };
  }) : [];
  const fakes = (brief.counterfeits ?? []).map(kind => {
    const v = verdict(runContract(contract, transformed(reference, counterfeit(kind, brief.counterfeitRef ?? 1), kind)));
    if (v.pass) problems.push(`counterfeit ${kind} passes the contract`);
    return { kind, rejected: !v.pass, failed: v.failed };
  });
  if (!negatives.length && !fakes.length) problems.push('no negatives or counterfeits: the contract is untested against failure');
  const length = forecast(fs.readFileSync(referenceFile, 'utf8')).forecastPostWeighted;
  return {
    id: brief.id, stratum: brief.stratum, valid: problems.length === 0, problems,
    reference: { passes: ref.pass, forecastPostWeighted: length, zone: zone(length) },
    negatives, counterfeits: fakes,
    requirements: contract.requirements.map(r => ({ id: r.id, kind: r.kind })),
    files: Object.fromEntries(files(dir).sort().map(f => [path.relative(dir, f), sha(f)])),
  };
}

export async function validateBank(bankDir) {
  const entries = [];
  for (const name of fs.readdirSync(bankDir).sort()) {
    const dir = path.join(bankDir, name);
    if (fs.statSync(dir).isDirectory() && fs.existsSync(path.join(dir, 'brief.json'))) entries.push(await validateEntry(dir));
  }
  const strata = Object.fromEntries(Object.keys(STRATA).map(s => [s, entries.filter(e => e.stratum === s).length]));
  return { entries, strata, valid: entries.length > 0 && entries.every(e => e.valid) };
}

export function verifyBank(bankDir, manifest) {
  const changes = [];
  for (const e of manifest.entries) {
    const dir = path.join(bankDir, e.id);
    for (const [rel, hash] of Object.entries(e.files)) {
      const file = path.join(dir, rel);
      if (!fs.existsSync(file)) changes.push(`${e.id}/${rel}: missing`);
      else if (sha(file) !== hash) changes.push(`${e.id}/${rel}: changed`);
    }
    if (fs.existsSync(dir)) for (const f of files(dir)) if (!(path.relative(dir, f) in e.files)) changes.push(`${e.id}/${path.relative(dir, f)}: added`);
  }
  return { unchanged: changes.length === 0, changes };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [command, bank, manifestFile] = process.argv.slice(2);
  if (command === 'validate' && bank) {
    const result = await validateBank(bank), out = process.argv.find(a => a.startsWith('--out='))?.slice(6);
    if (out) fs.writeFileSync(out, JSON.stringify(result, null, 1) + '\n');
    console.log(JSON.stringify({ valid: result.valid, strata: result.strata, entries: result.entries.map(e => ({ id: e.id, stratum: e.stratum, valid: e.valid, zone: e.reference.zone, problems: e.problems })) }, null, 1));
    process.exitCode = result.valid ? 0 : 1;
  } else if (command === 'verify' && bank && manifestFile) {
    const result = verifyBank(bank, JSON.parse(fs.readFileSync(manifestFile, 'utf8')));
    console.log(JSON.stringify(result, null, 1));
    process.exitCode = result.unchanged ? 0 : 1;
  } else {
    console.error('usage: node brief-bank.mjs validate BANK_DIR [--out=MANIFEST] | node brief-bank.mjs verify BANK_DIR MANIFEST');
    process.exit(2);
  }
}
