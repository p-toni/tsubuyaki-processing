// Each entry records when a previously dry pair of barbs took one unit of ink.
const stainedAt = [];
let bead = 0;
let position = 0;

function setup() {
  createCanvas(400, 400);
}

function draw() {
  background(247, 240, 222);
  const phase = (frameCount - 1) % 360;
  if (phase === 0) {
    bead = 64;
    position = 0;
  }
  if (phase > 72 && bead > 0) {
    const dry = position >= stainedAt.length && position < 96;
    position += dry ? 0.375 : 0.75;
    if (stainedAt.length < 96 && position >= stainedAt.length + 1) {
      stainedAt.push(frameCount);
      bead--;
    }
  }

  noFill();
  for (let ink = 0; ink < 2; ink++) {
    stroke(ink ? '#26536c' : '#a78b65');
    strokeWeight(ink ? 1.7 : 1);
    const count = ink ? stainedAt.length : 96;
    for (let pore = 1; pore <= count; pore++) {
      const x = 60 + 2.7 * pore;
      const y = 160 + pore * pore / 100;
      const radius = 1 + 68 * sin(PI * pore / 96) * (0.9 + 0.1 * cos(pore / 2));
      const spread = ink ? min(1, 8 * sqrt(frameCount - stainedAt[pore - 1] + 1) / radius) : 1;
      arc(x + radius, y, 2 * radius, 2 * radius, PI - 0.82 * spread, PI + 1.23 * spread);
      line(x - 2.7, 160 + (pore - 1) ** 2 / 100, x, y);
    }
  }

  if (bead > 0) {
    const x = 60 + 2.7 * position;
    const fall = min(phase, 72) ** 2 / 40 - 129.6;
    const radius = 1.55 * sqrt(bead);
    const y = 160 + position * position / 100 + fall + max(0, position - 96) ** 2 / 7 - radius;
    noStroke();
    fill('#153c57');
    circle(x, y, 2 * radius);
    fill('#b6d8d4');
    circle(x - radius / 3, y - radius / 3, radius / 3);
  }
}
