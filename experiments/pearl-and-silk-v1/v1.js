setup = () => createCanvas(400, 400);

draw = () => {
  background(16, 21, 27);
  const phase = frameCount * PI / 180;
  const pearlX = 82 * cos(phase);
  const pearlY = 179 + 58 * sin(phase);
  const load = max(0, pearlY + 18 - 198);

  strokeWeight(1.3);
  for (let i = 6741; i--;) {
    const x = i % 321 - 160;
    const layer = floor(i / 321) / 20;
    const bow = 1 - (x / 160) ** 2;
    const pocket = max(0, 1 - ((x - pearlX) / 76) ** 2) ** 2;
    stroke(177 - 109 * layer, 220 - 64 * layer, 213 - 45 * layer);
    point(200 + x, 198 + 42 * layer * bow + load * pocket * (1 - .3 * layer));
  }

  for (let diameter = 36; diameter > 0; diameter--) {
    const glint = (diameter - 36) / 7;
    stroke(254 - diameter, 236 - 2 * diameter, 222 - 2 * diameter);
    strokeWeight(diameter);
    point(200 + pearlX + glint, pearlY + glint);
  }
};
