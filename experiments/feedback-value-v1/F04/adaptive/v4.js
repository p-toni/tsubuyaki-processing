// F04/adaptive-v4: attach a visible delayed pulse to the deforming inner surfaces.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  const leftPulse = (.5 + .5 * sin(time)) ** 8;
  const rightPulse = (.5 + .5 * sin(time - 2)) ** 8;
  background(9);
  stroke(240, 100);
  for (let i = 9000; i--;) {
    const family = i % 3;
    const u = i / 9000;
    const pulse = (.5 + .5 * sin(time - 2 * (family < 2 ? family : u))) ** 8;
    const angle = u * TAU;
    const radius = 36 + 8 * cos(i) + 18 * pulse * cos(3 * angle);
    if (family < 2) point(100 + 200 * family + radius * cos(angle), 200 + radius * sin(angle));
    else point((136 + 18 * leftPulse) * (1 - u) + (264 + 18 * rightPulse) * u,
      200 + 42 * pulse * sin(PI * u) + 4 * sin(i));
  }
};
