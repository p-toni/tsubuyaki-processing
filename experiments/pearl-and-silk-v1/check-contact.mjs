// Counterfactual for this sketch's sixteen interleaved pearl layers and threads.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('v2.js', import.meta.url), 'utf8');
function change(before, after) {
  assert.equal(source.split(before).length, 2);
  return source.replace(before, after);
}
const unloaded = change('const load = max(0, immersion - (x - pearlX) ** 2 / 710 - strand / 12) ** 2;', 'const load = 0;');
const shifted = change('const pearlX = 82 * cos(phase);', 'const pearlX = 82 * cos(phase) + 40;');
const groupSize = 642; // One pearl layer, then 641 samples from x = 40 through 360.
const pairCount = 16 * groupSize;
function capture(program) {
  const points = new Float64Array(pairCount * 2);
  let index;
  const noop = () => {};
  const page = vm.createContext({
    PI: Math.PI, cos: Math.cos, sin: Math.sin, abs: Math.abs, max: Math.max,
    createCanvas: noop, background: noop, stroke: noop, strokeWeight: noop,
    point(x, y) { points[index++] = x; points[index++] = y; },
  });
  vm.runInContext(program, page);
  page.setup();
  return frame => {
    index = 0;
    page.frameCount = frame;
    page.draw();
    assert.equal(index, points.length);
    return points;
  };
}
const original = capture(source);
const withoutLoad = capture(unloaded);
const firstRest = withoutLoad(1).slice();
const topStart = 2 * (15 * groupSize + 1);
let loadedFrames = 0, separatedFrames = 0, touchingFrames = 0, largestPocket = 0;
function compare(actual, control) {
  let indentation = 0, peakX;
  for (let i = 0; i < actual.length; i += 2) {
    assert.equal(actual[i], control[i]);
    const inGroup = (i / 2) % groupSize;
    const dy = actual[i + 1] - control[i + 1];
    if (inGroup === 0) {
      assert.equal(dy, 0, 'pearl moved when the load was removed');
    } else {
      assert.equal(control[i + 1], firstRest[i + 1], 'unloaded silk moved');
      if (inGroup === 1 || inGroup === groupSize - 1) assert.equal(dy, 0, 'anchor moved');
      if (dy > indentation) { indentation = dy; peakX = actual[i]; }
    }
  }
  return { indentation, peakX };
}
for (let frame = 1; frame <= 720; frame++) {
  const actual = original(frame), rest = withoutLoad(frame);
  const pocket = compare(actual, rest);
  // Interpolate the unloaded top thread at the observed centre of the outer pearl.
  const pos = 2 * (actual[0] - 40), left = Math.floor(pos), fraction = pos - left;
  const y = topStart + 2 * left + 1;
  const depth = actual[1] + 16 - (rest[y] + fraction * (rest[y + 2] - rest[y]));
  if (depth > .001) {
    assert.ok(pocket.indentation > .001);
    loadedFrames++;
  } else {
    assert.ok(pocket.indentation < .001);
    if (depth < -.001) separatedFrames++;
    else touchingFrames++;
  }
  largestPocket = Math.max(largestPocket, pocket.indentation);
}

// Change the pearl's horizontal position independently of the animation clock.
const rest = withoutLoad(90);
const atDepth = original(90);
const displaced = capture(shifted)(90);
const unshifted = compare(atDepth, rest);
const shiftedRest = capture(unloaded.replace('82 * cos(phase)', '82 * cos(phase) + 40'))(90);
const afterShift = compare(displaced, shiftedRest);
assert.equal(displaced[0] - atDepth[0], 40);
assert.equal(afterShift.peakX - unshifted.peakX, 40);
assert.equal(unshifted.indentation, afterShift.indentation);
console.log(JSON.stringify({ frames: 720, loadedFrames, separatedFrames, touchingFrames, largestPocket,
  pearlAndAnchorsIdenticalThroughout: true, peakAtFrame90: unshifted, peakAfter40pxShift: afterShift }, null, 2));
