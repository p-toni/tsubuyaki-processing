// Readable advanced scaffold. Invent new equations before golfing.
// Demonstrates a flattened 2D manifold with shared latent geometry.

let time = 0;
const SIZE = 400;
const COLS = 196;
const SAMPLES = 30000;

function setup() {
  createCanvas(SIZE, SIZE);
  stroke(255, 54);
}

function mapSurface(index) {
  const u = index % COLS;
  const v = index / COLS; // intentionally continuous; floor only if the design needs it

  // Hidden sheet coordinates.
  const lateral = u / 7 - 14;
  const axial = v / 8 - 12;
  const distance = mag(lateral, axial);

  // One phase ties together rotation, axial position and time.
  const phase = distance / 3 - time + axial / 5;

  // Radius deformation: macro distance + one coupled harmonic.
  const radius = 55
    + distance * 4
    + lateral * sin(v / 3);

  const x = SIZE / 2 + radius * cos(phase);
  const y = SIZE / 2
    + radius * sin(phase) / 2
    + axial * lateral * sin(distance * 2 + time);

  point(x, y);
}

function draw() {
  background(7);
  time += PI / 90;

  for (let i = SAMPLES; i--;) {
    mapSurface(i);
  }
}
