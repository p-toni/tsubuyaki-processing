// Hollow: a two-coordinate ring surface; a traveling fold changes its material.
setup = () => createCanvas(400, 400);
draw = () => {
  background(9);
  stroke(240, 60);
  const time = frameCount / 60;
  for (let i = 18000; i--;) {
    const around = i % 180 / 180 * TAU;
    const tube = i / 18000 * TAU;
    const radius = 94 + (24 + 6 * sin(time)) * cos(tube)
      + 8 * sin(7 * around + 2 * tube - time);
    point(200 + radius * cos(around),
      200 + .65 * radius * sin(around) + 32 * sin(tube));
  }
};
