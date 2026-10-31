#!/usr/bin/env node
// JUDGE-1 scorer. Run only after every judgment file is committed.
//   node score-judges.mjs --key=SEALED/key.json --judgments=DIR [--manifest=PACKAGE/manifest.json] [--out=judge-card.json]
// Verifies the key against the package manifest's commitment when given.
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { judgeCard } from './lib/judgecard.mjs';

const arg = name => process.argv.find(a => a.startsWith(`--${name}=`))?.split('=')[1];
const keyFile = arg('key'), dir = arg('judgments'), manifestFile = arg('manifest'), out = arg('out') ?? 'judge-card.json';
if (!keyFile || !dir) { console.error('usage: node score-judges.mjs --key=SEALED/key.json --judgments=DIR [--manifest=PACKAGE/manifest.json] [--out=FILE]'); process.exit(2); }
const keyText = fs.readFileSync(keyFile, 'utf8');
if (manifestFile) {
  const expected = JSON.parse(fs.readFileSync(manifestFile, 'utf8')).keySha256, actual = createHash('sha256').update(keyText).digest('hex');
  if (expected !== actual) { console.error(`key does not match the package commitment: ${actual} != ${expected}`); process.exit(1); }
}
const key = JSON.parse(keyText).items, judgments = {};
for (const file of fs.readdirSync(dir).filter(f => f.endsWith('.jsonl'))) {
  const judge = path.basename(file, '.jsonl');
  judgments[judge] = {};
  for (const line of fs.readFileSync(path.join(dir, file), 'utf8').split('\n').filter(Boolean)) {
    const j = JSON.parse(line);
    if (!['A', 'B', 'equal'].includes(j.choice)) throw new Error(`${file}: invalid choice ${j.choice}`);
    if (judgments[judge][j.id]) throw new Error(`${file}: duplicate judgment for ${j.id}`);
    judgments[judge][j.id] = j;
  }
}
const card = judgeCard(key, judgments);
fs.writeFileSync(out, JSON.stringify(card, null, 1) + '\n');
console.log(JSON.stringify({ judges: Object.keys(judgments), gateable: card.gateable, fleissKappa: card.panel.fleissKappa }, null, 1));
