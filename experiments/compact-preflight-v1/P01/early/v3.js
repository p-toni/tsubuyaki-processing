// Aperture v3: visibility selection replaces separately sampled foreground/rear layers.
setup = () => createCanvas(400, 400);
draw = () => {
  const time = frameCount / 60;
  background(9);
  for (let i = 30000; i--;) {
    const angle = i * 2.399963;
    const radius = 130 * sqrt(i / 30000);
    const opening = max(0, 50 * sin(time) + 10 * cos(3 * angle));
    const distance = max(0, radius - opening);
    const phase = 5 * angle + radius / 20 - time;
    const rearShade = 80 + 40 * sin(radius / 6 - time);
    const frontShade = 180 + 60 * sin(phase);
    stroke(radius < opening ? rearShade : frontShade);
    point(200 + radius * cos(angle),
      200 + .75 * radius * sin(angle) + 8 * sin(phase) * sin(distance / 40));
  }
};
