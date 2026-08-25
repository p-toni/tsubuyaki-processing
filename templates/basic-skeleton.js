// Readable default scaffold. Do not tweet this version.
// Goal: a dense flattened-2D sheet with shared latent geometry.

let time = 0;
const SIZE = 400;
const COLS = 180;
const SAMPLES = 30000;

function setup() {
  createCanvas(SIZE, SIZE);
  pixelDensity(1);
  stroke(255, 54);
}

function samplePoint(index) {
  // Flatten one loop into two sample coordinates.
  const u = index % COLS;
  const v = index / COLS; // continuous quotient is often visually useful

  // Hidden sheet/body coordinates. Replace these equations for every work.
  const lateral = u / 7 - 13;
  const axial = v / 7 - 11;
  const distance = mag(lateral, axial);

  // Shared geometry: the same latent quantities shape phase and radius.
  const phase = distance / 3 - time + axial / 6;
  const radius = 54
    + distance * 4
    + lateral * sin(v / 3 - time / 2);

  const x = SIZE / 2 + radius * cos(phase);
  const y = SIZE / 2
    + radius * sin(phase) / 2
    + axial * lateral * sin(distance * 2 + time);

  point(x, y);
}

function draw() {
  background(8);
  time += PI / 120;

  for (let i = SAMPLES; i--;) samplePoint(i);
}