setup = () => createCanvas(400, 400);

draw = () => {
  background(18, 23, 29);
  const phase = frameCount * PI / 180;
  const pearlX = 82 * cos(phase);
  const immersion = 8 * sin(phase);
  const surface = x => 184 + x / 10 + 24 * cos(x / 102);
  const pearlY = surface(pearlX) + immersion * abs(immersion) - 16;

  for (let strand = 16; strand--;) {
    // Each layer gives the pearl a softer highlight and the silk a distinct thread.
    stroke(246 - 7 * strand);
    const glint = (strand - 15) / 4;
    strokeWeight(2 + 2 * strand);
    point(200 + pearlX + glint, pearlY + glint);

    strokeWeight(1.25);
    for (let x = -160; x <= 160; x += .5) {
      const rest = surface(x) + 3 * strand * cos(x / 102);
      const load = max(0, immersion - (x - pearlX) ** 2 / 710 - strand / 12) ** 2;
      point(200 + x, rest + load);
    }
  }
};
