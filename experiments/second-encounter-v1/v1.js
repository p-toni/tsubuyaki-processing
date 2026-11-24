let wetPores = 0;
let bead = 0;

function setup() {
  createCanvas(400, 400);
}

function draw() {
  background(247, 240, 222);
  const phase = (frameCount - 1) % 360;
  if (phase === 0) bead = 64;

  // One dry pore takes one unit of ink when the bead reaches it.
  const position = constrain((phase - 72) / 2, 0, 96);
  if (bead > 0 && position >= wetPores + 1) {
    wetPores++;
    bead--;
  }

  noFill();
  strokeWeight(1.4);
  for (let pore = 1; pore <= 96; pore++) {
    const x = 60 + 2.7 * pore;
    const y = 160 + pore * pore / 100;
    const vane = 62 * sin(PI * pore / 96) * (0.94 + 0.06 * cos(pore * 0.7));
    stroke(pore <= wetPores ? '#26536c' : '#a78b65');
    line(x - 2.7, 160 + (pore - 1) ** 2 / 100, x, y);
    for (const side of [-1, 1]) {
      const span = side < 0 ? vane : vane * 0.72;
      bezier(x, y, x, y + side * span / 3, x + span * 0.4, y + side * span * 0.8,
        x + span * 0.8, y + side * span);
    }
  }

  if (bead > 0) {
    const free = max(0, phase - 264);
    const x = 60 + 2.7 * position + 1.35 * free;
    const fall = min(phase, 72) ** 2 / 40 - 129.6;
    const radius = 1.55 * sqrt(bead);
    const y = 160 + position * position / 100 + fall + free * (0.96 + free / 22) - radius;
    noStroke();
    fill('#153c57');
    circle(x, y, 2 * radius);
    fill('#b6d8d4');
    circle(x - radius / 3, y - radius / 3, radius / 3);
  }
}
