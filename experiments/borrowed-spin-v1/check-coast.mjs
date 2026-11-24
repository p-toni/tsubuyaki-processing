import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const sketch = readFileSync(new URL('sketch.txt', import.meta.url), 'utf8');
const transfer = '.055*(.035-v)';
assert.equal(sketch.split(transfer).length, 2, 'expected one contact torque term');

// Record the geometry and colour of every disc drawn by the archived sketch.
function player(source) {
  let discs, colour;
  const page = vm.createContext({
    cos: Math.cos, sin: Math.sin, max: Math.max,
    createCanvas() {}, noStroke() {}, background() {},
    fill(...rgb) { colour = rgb; },
    circle(x, y, diameter) { discs.push([x, y, diameter, ...colour]); },
  });
  vm.runInContext(source, page);
  page.setup();
  return frame => {
    discs = [];
    page.frameCount = frame;
    page.draw();
    assert.equal(discs.length, 130);
    return discs;
  };
}

// Read orientation from the smallest disc's offset relative to its outer rim.
function bearing(outer, inner) {
  return Math.atan2(inner[1] - outer[1], inner[0] - outer[0]);
}

function turnDegrees(delta) {
  return Math.atan2(Math.sin(delta), Math.cos(delta)) * 180 / Math.PI;
}

const original = player(sketch);
const control = player(sketch.replace(transfer, '0'));
const contact = [], degrees = [];
let controlReceiver, lastDriverAngle, lastReceiverAngle, touching = false;
for (let frame = 1; frame <= 720; frame++) {
  const actual = original(frame), disabled = control(frame);
  assert.deepEqual(actual.slice(0, 65), disabled.slice(0, 65), 'driver changed');
  controlReceiver ??= disabled.slice(65);
  assert.deepEqual(disabled.slice(65), controlReceiver, 'undriven receiver changed');

  const [x, y, diameter] = actual[0], rim = actual[65];
  const gap = Math.hypot(x - rim[0], y - rim[1]) - (diameter + rim[2]) / 2;
  assert.ok(gap > -1e-9, 'rims overlap');
  const meets = gap < 1e-9;
  if (meets && !touching) contact.push([frame, frame]);
  if (meets) contact.at(-1)[1] = frame;
  if (!contact.length) assert.deepEqual(actual, disabled, 'motion before first contact');
  touching = meets;

  const driverAngle = bearing(actual[0], actual[64]);
  const receiverAngle = bearing(rim, actual.at(-1));
  if (frame > 1) assert.ok(turnDegrees(driverAngle - lastDriverAngle) > 0, 'driver must turn clockwise');
  const receiverTurn = turnDegrees(receiverAngle - (lastReceiverAngle ?? receiverAngle));
  if (meets) assert.ok(receiverTurn < 0, 'receiver must turn the other way during contact');
  degrees.push(receiverTurn);
  lastDriverAngle = driverAngle;
  lastReceiverAngle = receiverAngle;
}

assert.equal(contact.length, 2);
const release = contact[0][1];
assert.ok(release + 120 < contact[1][0], 'measurement window must be wholly separated');
const sum = values => values.reduce((total, value) => total + value, 0);
const firstSecond = sum(degrees.slice(release, release + 60));
const nextSecond = sum(degrees.slice(release + 60, release + 120));
assert.ok(firstSecond < nextSecond && nextSecond < 0, 'expected a slowing counterclockwise turn');
console.log(JSON.stringify({
  frames: degrees.length, touchingFramesInclusive: contact,
  beforeFirstTouchIdenticalFrames: contact[0][0] - 1,
  driverIdenticalFrames: degrees.length, stationaryControlFrames: degrees.length,
  receiverDegreesFirstSecondAfterRelease: firstSecond,
  receiverDegreesNextSecondAfterRelease: nextSecond,
  controlDegreesAfterRelease: 0,
}, null, 2));
