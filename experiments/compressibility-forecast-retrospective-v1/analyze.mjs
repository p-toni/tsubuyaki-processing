#!/usr/bin/env node
// Retrospective: does a mechanical forecast of the readable source predict the
// compact length the agent achieved? Node built-ins only. Run from this folder:
//   node analyze.mjs            -> writes results.json and mechanical-posts/
//   node analyze.mjs --audit    -> also runs the archived exact-equivalence
//                                  auditor on every mechanical post (slow)
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { spawn, spawnSync } from 'node:child_process';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { forecast, zone } from './forecast-length.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const experiments = join(here, '..');
const repo = join(experiments, '..');
const sha = text => createHash('sha256').update(text).digest('hex');
const rel = p => relative(here, p);
const weighted = file => {
  const r = spawnSync(process.execPath, [join(repo, 'scripts/check-length.mjs'), file], { encoding: 'utf8' });
  return JSON.parse(r.stdout).xWeightedLength;
};

// Every archived compact attempt with the readable version it compacts.
const attempts = [];
for (const [brief, version] of [['B01', 'v1'], ['B02', 'v2'], ['B03', 'v2']]) {
  attempts.push({ study: 'autonomous-discovery-pilot-v1', brief, arm: '-', attempt: 1, version,
    source: join(experiments, 'autonomous-discovery-pilot-v1', brief, `${version}.js`),
    post: join(experiments, 'autonomous-discovery-pilot-v1', brief, 'compact-1.txt') });
}
for (const study of ['feedback-value-v1', 'compact-preflight-v1']) {
  const record = JSON.parse(readFileSync(join(experiments, study, 'compact-attempts.json'), 'utf8'));
  for (const a of record.attempts) {
    attempts.push({ study, brief: a.brief, arm: a.arm, attempt: a.attempt, version: a.version,
      source: join(experiments, study, a.brief, a.arm, `${a.version}.js`),
      post: join(experiments, study, a.post) });
  }
}

// Logical attempts can reuse an identical post; count each unique post once.
const posts = new Map();
for (const a of attempts) {
  const src = readFileSync(a.source, 'utf8');
  const postText = readFileSync(a.post, 'utf8');
  const key = sha(postText);
  if (posts.has(key)) { posts.get(key).logicalUses.push(`${a.study}/${a.brief}/${a.arm}#${a.attempt}`); continue; }
  const f = forecast(src).forecastPostWeighted;
  const actual = weighted(a.post);
  posts.set(key, { ...a, source: rel(a.source), post: rel(a.post), sourceSha256: sha(src), postSha256: key,
    forecast: f, actual, ratio: +(actual / f).toFixed(4), fits: actual <= 280,
    logicalUses: [`${a.study}/${a.brief}/${a.arm}#${a.attempt}`] });
}
const unique = [...posts.values()];

const stats = xs => {
  const m = xs.reduce((s, x) => s + x, 0) / xs.length;
  const sd = Math.sqrt(xs.reduce((s, x) => s + (x - m) ** 2, 0) / xs.length);
  return { n: xs.length, mean: +m.toFixed(3), sd: +sd.toFixed(3), min: Math.min(...xs), max: Math.max(...xs) };
};
const ratios = { attempt1: stats(unique.filter(p => p.attempt === 1).map(p => p.ratio)),
  attempt2: stats(unique.filter(p => p.attempt === 2).map(p => p.ratio)), all: stats(unique.map(p => p.ratio)) };

// Outcome per unique readable source: did any attempt on it fit?
const sources = new Map();
for (const p of unique) {
  const s = sources.get(p.sourceSha256) ?? { source: p.source, study: p.study, brief: p.brief, version: p.version,
    forecast: p.forecast, zone: zone(p.forecast), attempts: 0, bestActual: Infinity };
  s.attempts += 1; s.bestActual = Math.min(s.bestActual, p.actual); s.delivered = s.bestActual <= 280;
  sources.set(p.sourceSha256, s);
}
const perSource = [...sources.values()].sort((a, b) => a.forecast - b.forecast);
const zones = Object.fromEntries(['green', 'amber', 'red'].map(z => {
  const xs = perSource.filter(s => s.zone === z);
  return [z, { sources: xs.length, delivered: xs.filter(s => s.delivered).length, attempts: xs.reduce((n, s) => n + s.attempts, 0) }];
}));

// Forecast trajectory of every readable version, including uncompacted ones.
const trajectories = [];
const arms = [['autonomous-discovery-pilot-v1', ['B01', 'B02', 'B03'], ['']],
  ['feedback-value-v1', ['F01', 'F02', 'F03', 'F04', 'F05', 'F06'], ['adaptive', 'batch']],
  ['compact-preflight-v1', ['P01', 'P02', 'P03', 'P04'], ['late', 'early']]];
for (const [study, briefs, armNames] of arms) for (const brief of briefs) for (const arm of armNames) {
  const versions = {};
  for (const v of ['v1', 'v2', 'v3', 'v4']) {
    const file = join(experiments, study, brief, arm, `${v}.js`);
    if (existsSync(file)) versions[v] = forecast(readFileSync(file, 'utf8')).forecastPostWeighted;
  }
  trajectories.push({ study, brief, arm: arm || '-', versions });
}

// Mechanical posts for every compacted source, for optional exact auditing.
mkdirSync(join(here, 'mechanical-posts'), { recursive: true });
const mechanical = perSource.map(s => {
  const src = readFileSync(join(here, s.source), 'utf8');
  const text = `${forecast(src).mechanicalCode}//#つぶやきProcessing`;
  const out = join(here, 'mechanical-posts', `${s.source.replace(/^\.\.\//, '').replace(/\.js$/, '').split('/').join('__')}.txt`);
  writeFileSync(out, text);
  return { source: s.source, post: rel(out), postSha256: sha(text), weighted: weighted(out) };
});

// Exact-equivalence audit (720 frames, every point) reuses the archived
// compact-preflight-v1 auditor. Results are cached per mechanical-post hash.
const auditFile = m => join(here, 'mechanical-posts', `${m.post.split('/').pop().replace(/\.txt$/, '')}.audit.json`);
if (process.argv.includes('--audit')) {
  const queue = mechanical.filter(m => {
    if (!existsSync(auditFile(m))) return true;
    return JSON.parse(readFileSync(auditFile(m), 'utf8')).compactSha256 !== m.postSha256;
  });
  const run = m => new Promise(done => {
    const child = spawn(process.execPath, [join(experiments, 'compact-preflight-v1/audit-source.mjs'), join(here, m.source), join(here, m.post), auditFile(m)], { stdio: ['ignore', 'ignore', 'pipe'] });
    let err = '';
    child.stderr.on('data', d => { err += d; });
    child.on('close', code => { if (code !== 0) writeFileSync(auditFile(m), JSON.stringify({ compactSha256: m.postSha256, error: err.slice(0, 600) }, null, 1)); done(); });
  });
  const workers = Array.from({ length: 4 }, async () => { while (queue.length) await run(queue.shift()); });
  await Promise.all(workers);
}
const audit = mechanical.map(m => {
  if (!existsSync(auditFile(m))) return { source: m.source, post: m.post, audited: false };
  const d = JSON.parse(readFileSync(auditFile(m), 'utf8'));
  if (d.compactSha256 !== m.postSha256) return { source: m.source, post: m.post, audited: false, stale: true };
  if (d.error) return { source: m.source, post: m.post, audited: true, executes: false, error: d.error };
  return { source: m.source, post: m.post, audited: true, executes: true, frames: d.frames, pointsPerFrame: d.pointsPerFrame,
    maxGeometryError: d.maxGeometryError, maxStyleError: d.maxStyleError, weighted: d.length.xWeightedLength,
    exactAndFits: d.maxGeometryError <= 1e-7 && d.maxStyleError <= 1e-7 && d.length.pass };
});

const results = {
  question: 'Does an idiom-free mechanical minification of the readable source forecast the compact length the agent achieved?',
  forecastTool: 'forecast-length.mjs',
  zoneRule: 'green <= 300 < amber <= 340 < red (forecast X-weighted post length)',
  uniquePosts: unique.length, logicalAttempts: attempts.length, uniqueCompactedSources: perSource.length,
  ratios, zones, perSource, perPost: unique, trajectories, mechanical, audit,
  limits: ['retrospective on consumed archives; describes these studies only',
    'exact-equivalence compaction regime (syntax/algebra only); does not cover semantic compression that drops causes',
    'zone thresholds were chosen after looking at these data; they need prospective validation'],
};
writeFileSync(join(here, 'results.json'), JSON.stringify(results, null, 1) + '\n');
console.log(JSON.stringify({ ratios, zones, uniquePosts: unique.length, logicalAttempts: attempts.length }, null, 1));
