// Readable 1D scaffold. Do not tweet this version.
// Use when the intended material is a filament/ribbon/axial creature.
// A high sample count alone does NOT turn this curve into a sheet.

let time = 0;
const SIZE = 400;
const SAMPLES = 14000;

function setup() {
  createCanvas(SIZE, SIZE);
  pixelDensity(1);
  stroke(255, 70);
}

function samplePoint(index) {
  const u = index / 240;

  const lateral = 6 * cos(u / 9);
  const axial = u / 18 - 9;
  const distance = mag(lateral, axial);

  // Fold the curve aggressively enough that adjacent samples do not simply
  // read as one smooth wire. Residue classes can add anatomy, not dimension.
  const side = index % 2;
  const phase = distance / 2 - time + side * 3;
  const radius = 70 + lateral * lateral + 9 * sin(distance * 3 - time * 2);

  const x = SIZE / 2 + radius * cos(phase);
  const y = SIZE / 2
    + 90 * sin(phase / 2)
    + lateral * axial * sin(distance * 3 - time * 2);

  point(x, y);
}

function draw() {
  background(8);
  time += PI / 180;
  for (let i = SAMPLES; i--;) samplePoint(i);
}