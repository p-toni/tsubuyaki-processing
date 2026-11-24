import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

// The dark circle has diameter 3.1 * sqrt(ink units). Read the dose back
// from that mark, including the first frame when it passes the tip.
function replay(file, keep) {
  let paint, drop;
  const page = vm.createContext({
    PI: Math.PI, min: Math.min, max: Math.max, sin: Math.sin, cos: Math.cos, sqrt: Math.sqrt,
    createCanvas() {}, background() {}, noFill() {}, noStroke() {},
    stroke() {}, strokeWeight() {}, arc() {}, line() {},
    fill(colour) { paint = colour; },
    circle(x, y, diameter) {
      if (paint !== '#153c57') return;
      const inferred = (diameter / 3.1) ** 2;
      const units = Math.round(inferred);
      assert.ok(Math.abs(inferred - units) < 1e-9, 'drop area must encode a whole number of units');
      drop = { x, y, units };
    },
  });
  vm.runInContext(readFileSync(new URL(file, import.meta.url), 'utf8'), page);
  page.setup();
  const frames = [];
  let startWet;
  for (let frame = 1; frame <= 720; frame++) {
    if (frame === 361 && keep !== undefined) page.A.length = keep;
    if (frame === 1 || frame === 361) startWet = page.A.length;
    drop = null;
    page.frameCount = frame;
    page.draw();
    const wet = page.A.length;
    const units = drop?.units ?? 0;
    assert.equal(units + wet - startWet, 64, 'each incoming dose must be accounted for');
    frames.push({ wet, units, x: drop?.x ?? null, y: drop?.y ?? null });
  }
  return frames;
}

const full = replay('attempt-1.txt');
const lean = replay('attempt-2.txt');
const reset = replay('attempt-1.txt', 0);
const partial = replay('attempt-1.txt', 48);
const first = full.slice(0, 360);
assert.deepEqual(reset.slice(0, 360), first);
assert.deepEqual(reset.slice(360), first);
assert.deepEqual(partial.slice(0, 360), first);
for (const [i, frame] of full.entries()) {
  assert.equal(lean[i].wet, frame.wet);
  assert.equal(lean[i].units, frame.units);
  assert.equal(lean[i].x, frame.x);
  assert.ok(Math.abs(lean[i].y - frame.y) < 1e-9);
}

function outcome(pass) {
  const tip = 60 + 2.7 * 96;
  const exited = pass.findIndex(frame => frame.x !== null && frame.x > tip);
  const exhausted = pass.findIndex(frame => frame.units === 0);
  return {
    wetPairsAtStart: pass[0].wet,
    wetPairsAtEnd: pass.at(-1).wet,
    exitUnits: exited < 0 ? 0 : pass[exited].units,
    firstFramePastTipInPass: exited < 0 ? null : exited + 1,
    firstFrameExhaustedInPass: exhausted < 0 ? null : exhausted + 1,
    dropXAtFrame137: pass[136].x,
  };
}

const results = {
  first: outcome(first), second: outcome(full.slice(360)),
  cleared: outcome(reset.slice(360)), kept48: outcome(partial.slice(360)),
};
assert.deepEqual(results.first, results.cleared);
assert.deepEqual([results.first.exitUnits, results.kept48.exitUnits, results.second.exitUnits], [0, 16, 32]);
console.log(JSON.stringify(results, null, 2));
