#!/usr/bin/env node
// Forecast registry CLI.
//   node forecasts.mjs validate forecasts.json          before any run; prints its sha256 to commit
//   node forecasts.mjs score forecasts.json outcomes.json   after the study closes
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import { validateForecasts, scoreForecasts } from './lib/forecasts.mjs';

const [command, file, outcomesFile] = process.argv.slice(2);
if (!['validate', 'score'].includes(command) || !file || (command === 'score' && !outcomesFile)) {
  console.error('usage: node forecasts.mjs validate FORECASTS.json | node forecasts.mjs score FORECASTS.json OUTCOMES.json');
  process.exit(2);
}
const text = fs.readFileSync(file, 'utf8'), doc = JSON.parse(text), check = validateForecasts(doc);
if (command === 'validate') {
  console.log(JSON.stringify({ ...check, sha256: createHash('sha256').update(text).digest('hex') }, null, 1));
  process.exitCode = check.ok ? 0 : 1;
} else {
  if (!check.ok) { console.error(check.errors.join('\n')); process.exit(1); }
  console.log(JSON.stringify(scoreForecasts(doc, JSON.parse(fs.readFileSync(outcomesFile, 'utf8'))), null, 1));
}
