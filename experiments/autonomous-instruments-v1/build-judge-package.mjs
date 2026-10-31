#!/usr/bin/env node
// JUDGE-1 package builder. Writes a judge-facing package (images and item ids
// only) and a separate sealed key. Node built-ins only.
//
//   JUDGE_SEED=<secret> node build-judge-package.mjs --out=DIR --sealed=DIR [--bases=N] [--levels=2,3] [--evidence=contact,motion]
//
// Keep the seed and the sealed directory away from judge sessions until every
// judgment is committed. The package manifest records sha256(seed) and
// sha256(key.json) so the reveal can be verified. The key is also recoverable
// from the sources by re-rendering, so losing it cannot erase the evidence.
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadSketch, transformed } from './lib/runtime.mjs';
import { DEGRADATIONS } from './lib/transforms.mjs';
import { contactSheet, motionSheet, manipulation } from './lib/evidence.mjs';
import { writePNG } from './lib/raster.mjs';

const here = path.dirname(fileURLToPath(import.meta.url)), experiments = path.join(here, '..');
const arg = (name, fallback) => process.argv.find(a => a.startsWith(`--${name}=`))?.split('=')[1] ?? fallback;
const seed = process.env.JUDGE_SEED, out = arg('out'), sealed = arg('sealed');
if (!seed || !out || !sealed) { console.error('usage: JUDGE_SEED=<secret> node build-judge-package.mjs --out=DIR --sealed=DIR [--bases=N] [--levels=2,3] [--evidence=contact,motion]'); process.exit(2); }
if ((path.resolve(sealed) + path.sep).startsWith(path.resolve(out) + path.sep)) { console.error('the sealed directory must not be inside the judge package'); process.exit(2); }
const levels = arg('levels', '2,3').split(',').map(Number), evidence = arg('evidence', 'contact,motion').split(',');
const sha = data => createHash('sha256').update(data).digest('hex');

// Archived A/B-grade readable selections across different briefs (none in flight).
const BASES = [
  'autonomous-discovery-pilot-v1/B01/v1.js', 'autonomous-discovery-pilot-v1/B02/v2.js', 'autonomous-discovery-pilot-v1/B03/v2.js',
  'feedback-value-v1/F01/adaptive/v2.js', 'feedback-value-v1/F03/adaptive/v2.js', 'feedback-value-v1/F05/batch/v4.js',
  'feedback-value-v1/F06/batch/v4.js', 'compact-preflight-v1/P01/early/v3.js', 'compact-preflight-v1/P03/late/v2.js',
  'compact-preflight-v1/P04/late/v2.js',
].slice(0, Number(arg('bases', 10)));

// Consequential archived pairs: no known answer; the archive's own verdict is recorded for re-judgment.
const REAL = [
  { brief: 'P04 Wake', first: 'compact-preflight-v1/P04/early/v4.js', second: 'compact-preflight-v1/P04/late/v2.js', archivedVerdict: 'second', note: 'gate-deciding regression' },
  { brief: 'P02 Thread', first: 'compact-preflight-v1/P02/early/v4.js', second: 'compact-preflight-v1/P02/late/v2.js', archivedVerdict: 'second' },
  { brief: 'P01 Aperture', first: 'compact-preflight-v1/P01/early/v3.js', second: 'compact-preflight-v1/P01/late/v2.js', archivedVerdict: 'equal' },
  { brief: 'F05 Twist', first: 'feedback-value-v1/F05/adaptive/v2.js', second: 'feedback-value-v1/F05/batch/v4.js', archivedVerdict: 'second' },
  { brief: 'F05 Twist', first: 'feedback-value-v1/F05/batch/v3.js', second: 'feedback-value-v1/F05/batch/v4.js', archivedVerdict: 'second' },
  { brief: 'F06 Divert', first: 'feedback-value-v1/F06/adaptive/v3.js', second: 'feedback-value-v1/F06/batch/v4.js', archivedVerdict: 'equal' },
  { brief: 'F02 Weave', first: 'feedback-value-v1/F02/adaptive/v4.js', second: 'feedback-value-v1/F02/batch/v3.js', archivedVerdict: 'first' },
  { brief: 'F04 Exchange', first: 'feedback-value-v1/F04/adaptive/v4.js', second: 'feedback-value-v1/F04/batch/v2.js', archivedVerdict: 'first' },
  { brief: 'F04 Exchange', first: 'feedback-value-v1/F04/adaptive/v4.js', second: 'feedback-value-v1/F04/adaptive/v3.js', archivedVerdict: 'first' },
];

// Manipulation floors, fixed before any judging: a known-answer pair must visibly differ.
const FLOOR = { spatial: 0.3, freeze: 0.2 };

// Seeded PRNG (mulberry32) from the secret seed.
let state = parseInt(sha(seed).slice(0, 8), 16);
const rand = () => { state = (state + 0x6d2b79f5) | 0; let t = Math.imul(state ^ (state >>> 15), 1 | state); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const framesFor = offset => Array.from({ length: 16 }, (_, j) => 1 + Math.round(offset + j * 672 / 15));

const pairs = [];
for (const rel of BASES) {
  const base = loadSketch(path.join(experiments, rel));
  for (const [kind, d] of Object.entries(DEGRADATIONS)) {
    for (const level of levels) {
      const strength = d.levels[level - 1], degraded = transformed(base, d.make(strength), `${kind}@${level}`);
      const magnitude = manipulation(base, degraded, kind), floor = kind === 'freeze' ? FLOOR.freeze : FLOOR.spatial;
      pairs.push({ type: 'known', base: rel, degradation: kind, level, strength, description: d.describe(strength), magnitude: +magnitude.toFixed(4),
        included: magnitude >= floor, sketches: [base, degraded], better: 0 });
    }
  }
}
for (const r of REAL) pairs.push({ type: 'real', ...r, included: true, sketches: [loadSketch(path.join(experiments, r.first)), loadSketch(path.join(experiments, r.second))] });

const included = pairs.filter(p => p.included), items = [], key = {};
fs.mkdirSync(path.join(out, 'items'), { recursive: true });
fs.mkdirSync(sealed, { recursive: true });
included.forEach((p, n) => {
  const offset = Math.floor(48 * rand()), frames = framesFor(offset);
  const sheets = p.sketches.map(s => Object.fromEntries(evidence.map(e => [e, (e === 'motion' ? motionSheet : contactSheet)(s, { frames })])));
  for (const flipped of [false, true]) {
    const id = sha(`${seed}:${n}:${flipped}`).slice(0, 12), dir = path.join(out, 'items', id), order = flipped ? [1, 0] : [0, 1];
    fs.mkdirSync(dir, { recursive: true });
    const item = { id };
    ['A', 'B'].forEach((side, i) => {
      item[side] = {};
      for (const e of evidence) { const file = `items/${id}/${side}-${e}.png`; writePNG(path.join(out, file), sheets[order[i]][e]); item[side][e] = file; }
    });
    items.push(item);
    const { sketches, included: _, ...meta } = p;
    key[id] = { pair: n, flipped, frames, ...meta, sideOfFirst: flipped ? 'B' : 'A', ...(p.type === 'known' ? { betterSide: order[0] === 0 ? 'A' : 'B' } : {}) };
  }
  console.error(`pair ${n + 1}/${included.length} ${p.type} ${p.type === 'known' ? `${p.degradation}@${p.level}` : p.brief}`);
});
for (let i = items.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [items[i], items[j]] = [items[j], items[i]]; }

const keyText = JSON.stringify({ excludedByManipulationFloor: pairs.filter(p => !p.included).map(p => ({ base: p.base, degradation: p.degradation, level: p.level, magnitude: p.magnitude })), floors: FLOOR, items: key }, null, 1) + '\n';
fs.writeFileSync(path.join(sealed, 'key.json'), keyText);
fs.writeFileSync(path.join(out, 'items.json'), JSON.stringify(items, null, 1) + '\n');
fs.copyFileSync(path.join(here, 'judge-protocol.md'), path.join(out, 'judge-protocol.md'));
const images = Object.fromEntries(items.flatMap(it => ['A', 'B'].flatMap(s => Object.values(it[s]))).sort().map(f => [f, sha(fs.readFileSync(path.join(out, f)))]));
const manifest = { study: 'JUDGE-1 judge-panel validation package', items: items.length, pairs: included.length, evidence, seedSha256: sha(seed), keySha256: sha(keyText), images };
fs.writeFileSync(path.join(out, 'manifest.json'), JSON.stringify(manifest, null, 1) + '\n');
console.log(JSON.stringify({ pairs: included.length, items: items.length, excluded: pairs.length - included.length, keySha256: manifest.keySha256, seedSha256: manifest.seedSha256 }));
