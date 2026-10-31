// node --test test-machinery.mjs   (Node built-ins only)
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { test } from 'node:test';
import { assess, briefsFor, passProbability, shiftFor, tCritical } from './lib/design.mjs';
import { scoreForecasts, validateForecasts } from './lib/forecasts.mjs';
import { validateBank, verifyBank } from './brief-bank.mjs';

const here = path.dirname(new URL(import.meta.url).pathname);
const FIXTURE = path.join(here, 'test-fixtures/brief-bank');

// ---- design power ---------------------------------------------------------

test('t quantiles match tables', () => {
  assert.ok(Math.abs(tCritical(0.1, 23) - 1.3195) < 1e-3);
  assert.ok(Math.abs(tCritical(0.05, 5) - 2.015) < 1e-3);
});

test('power reproduces the review: October gate near 9%, 24 x 3 near 95%, false pass near alpha', () => {
  const october = passProbability({ briefs: 6, runs: 1, shift: 1.1, gate: (w, l) => w >= 4 && l <= 1 });
  assert.ok(october > 0.05 && october < 0.14, `october ${october}`);
  const big = assess({ briefs: 24, runs: 3, base: 0.5, effect: 0.25 });
  assert.ok(big.power > 0.9, `power ${big.power}`);
  assert.ok(big.falsePass > 0.06 && big.falsePass < 0.14, `false pass ${big.falsePass}`);
});

test('more briefs never need more than the search limit for a large effect', () => {
  const n = briefsFor({ runs: 3, base: 0.5, effect: 0.25, sims: 1500 }, 0.8);
  assert.ok(n !== null && n >= 8 && n <= 24, `briefs ${n}`);
  assert.ok(Math.abs(shiftFor(0.5, 0.25) - Math.log(3)) < 1e-9);
});

// ---- forecast registry ----------------------------------------------------

const study = (ps) => ({ study: 'demo', forecasts: ps.map((p, i) => ({ id: `f${i}`, quantity: i % 2 ? 'deliver' : 'prefer', p })) });

test('validation rejects malformed forecasts and warns when the study is mostly predicted', () => {
  assert.equal(validateForecasts({ study: 'x', forecasts: [{ id: 'a', quantity: 'deliver', p: 1.2 }] }).ok, false);
  assert.equal(validateForecasts({ study: 'x', forecasts: [{ id: 'a', quantity: 'deliver', p: 0.5 }, { id: 'a', quantity: 'deliver', p: 0.5 }] }).ok, false);
  const predictable = validateForecasts(study([0.02, 0.97, 0.95, 0.04, 0.5]));
  assert.equal(predictable.ok, true);
  assert.equal(predictable.warnings.length, 1);
  assert.equal(validateForecasts(study([0.3, 0.6, 0.5, 0.7])).warnings.length, 0);
});

test('scoring: perfect forecasts score 0; coin flips score 0.25; skill compares with the base rate', () => {
  const outcomes = { outcomes: { f0: 1, f1: 0, f2: 1, f3: 0 } };
  assert.equal(scoreForecasts(study([1, 0, 1, 0]), outcomes).brier, 0);
  const coin = scoreForecasts(study([0.5, 0.5, 0.5, 0.5]), outcomes);
  assert.equal(coin.brier, 0.25);
  assert.ok(Math.abs(coin.brierSkill) < 1e-12);
  assert.deepEqual(scoreForecasts(study([0.5, 0.5, 0.5]), { outcomes: { f0: 1 } }).missing, ['f1', 'f2']);
});

// ---- brief bank -------------------------------------------------------------

test('the gather fixture is a valid entry: reference passes, negative and counterfeits fail', async () => {
  const bank = await validateBank(FIXTURE), e = bank.entries[0];
  assert.equal(bank.valid, true);
  assert.equal(e.reference.passes, true);
  assert.deepEqual(e.negatives.map(n => n.failed), [['staggered_timing']]);
  assert.ok(e.counterfeits.every(c => c.rejected));
  assert.equal(e.reference.zone, 'green');
  assert.equal(verifyBank(FIXTURE, bank).unchanged, true);
});

test('the bank flags a negative that passes, and detects tampering', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'bank-'));
  fs.cpSync(FIXTURE, dir, { recursive: true });
  const entry = path.join(dir, 'gather-fixture');
  fs.writeFileSync(path.join(entry, 'contract.mjs'), `export { default } from '${path.join(here, 'contracts/B03-gather.mjs')}';\n`);
  fs.copyFileSync(path.join(entry, 'reference.js'), path.join(entry, 'negatives/not-really.js'));
  const bank = await validateBank(dir);
  assert.equal(bank.valid, false);
  assert.ok(bank.entries[0].problems.some(p => p.includes('negatives/not-really.js') || p.includes('not-really.js passes')));
  fs.appendFileSync(path.join(entry, 'reference.js'), '\n// edited after sealing\n');
  const check = verifyBank(dir, bank);
  assert.equal(check.unchanged, false);
  assert.ok(check.changes.some(c => c.includes('reference.js: changed')));
});
