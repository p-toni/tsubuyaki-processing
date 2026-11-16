// A wave of pleats runs down one tapered skin. Each fold shapes and lights it.
setup = () => { createCanvas(400, 400); strokeWeight(2); };
draw = () => {
  background(12);
  for (let i = 28800; i--;) {
    const along = (i % 180) / 57;
    const around = i / 9000 - 1.6;
    const band = (1 + cos(2 * along - frameCount / 78)) / 2;
    const fold = cos(9 * around + 2 * along) * band * band;
    const radius = 16 + (77 + 32 * fold) * sin(along);
    const depth = radius * cos(around);
    const light = 92 + 75 * fold + 42 * cos(around);
    stroke(light + 38, light, 89);
    point(200 + 20 * cos(along) + radius * sin(around),
      67 + 79 * along + .38 * depth);
  }
};
