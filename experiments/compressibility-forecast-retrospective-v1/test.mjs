// node --test test.mjs   (Node built-ins only)
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { test } from 'node:test';
import { blockedStudy, forecast, mechanicalMinify, shortNumber, zone } from './forecast-length.mjs';

const tool = new URL('./forecast-length.mjs', import.meta.url).pathname;

test('numbers take their shortest exact form', () => {
  assert.equal(shortNumber('48000'), '48e3');
  assert.equal(shortNumber('0.625'), '.625');
  assert.equal(shortNumber('1.0'), '1');
  assert.equal(shortNumber('5999'), '5999');
  assert.equal(shortNumber('0x10'), '0x10');
});

test('declarations become implicit globals; initializer-free declarators disappear', () => {
  // `value` takes the first free single letter: a and b are already declared.
  assert.equal(mechanicalMinify('const value = 1;\nlet a, b;\na = value;'), 'c=1;a=c;');
  assert.equal(mechanicalMinify('for (let index = 3, j; index--;) point(index, 0)'), 'for(a=3;a--;)point(a,0)');
  assert.equal(mechanicalMinify('for (const k of [1,2]) { let a, b; a = k; }'), 'for(k of[1,2]){a=k}');
});

test('p5 names, property access and hooks are never renamed', () => {
  const out = mechanicalMinify('setup = () => createCanvas(400, 400);\ndraw = () => { const radius = sin(frameCount); point(radius, Math.PI); };');
  assert.ok(out.startsWith('setup=()=>createCanvas(400,400);draw=()=>{'));
  assert.ok(out.includes('sin(frameCount)') && out.includes('Math.PI'));
  assert.doesNotThrow(() => new Function(out));
});

test('forecast adds the hashtag weight and zones follow the documented cut-offs', () => {
  assert.equal(forecast('a=1;').forecastPostWeighted, 4 + 21);
  assert.equal(zone(300), 'green');
  assert.equal(zone(301), 'amber');
  assert.equal(zone(341), 'red');
});

test('the CLI refuses the in-flight study and forecasts archived sources', () => {
  const inFlight = new URL('../compact-representation-v1/R1/v1.js', import.meta.url).pathname;
  assert.equal(blockedStudy(inFlight), 'compact-representation-v1');
  const refused = spawnSync(process.execPath, [tool, inFlight], { encoding: 'utf8' });
  assert.equal(refused.status, 3);
  assert.equal(refused.stdout, '');
  const ok = spawnSync(process.execPath, [tool, new URL('../compact-preflight-v1/P04/early/v4.js', import.meta.url).pathname], { encoding: 'utf8' });
  assert.equal(ok.status, 0);
  assert.equal(JSON.parse(ok.stdout).forecastPostWeighted, 265);
});
