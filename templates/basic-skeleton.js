// Readable design scaffold. Do not tweet this version.
// Goal: one dense 1D manifold, one latent body coordinate, one evolving projection.

let time = 0;
const SIZE = 400;
const SAMPLES = 10000;

function setup() {
  createCanvas(SIZE, SIZE);
  stroke(255, 70);
}

function samplePoint(index) {
  const u = index / 240;

  // Latent body coordinates. Replace these equations for every new work.
  const lateral = 6 * cos(u / 9);
  const axial = u / 18 - 9;
  const distance = mag(lateral, axial);

  // Couple body geometry and time. Avoid unrelated decorative waves.
  const phase = distance / 2 - time;
  const radius = 70 + lateral * lateral;

  const x = SIZE / 2 + radius * cos(phase);
  const y = SIZE / 2
    + 90 * sin(phase / 2)
    + lateral * axial * sin(distance * 3 - time * 2);

  point(x, y);
}

function draw() {
  background(8);
  time += PI / 180;

  for (let i = SAMPLES; i--;) {
    samplePoint(i);
  }
}
