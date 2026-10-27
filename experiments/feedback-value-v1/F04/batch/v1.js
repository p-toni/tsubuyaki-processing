// F04/v1: Two folded bodies and a bridge share the same delayed oscillation.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 90);
  for (let i = 9000; i--;) {

    const family = i % 3;
    const u = i / 9000;
    const phase = time - 2 * (family < 2 ? family : u);
    const angle = u * TAU;
    const radius = 30 + 7 * cos(i) + 10 * sin(phase) * cos(3 * angle);
    if (family < 2) point(120 + 160 * family + radius * cos(angle), 200 + radius * sin(angle));
    else point(120 + 160 * u, 200 + 14 * sin(phase) * sin(PI * u) + 3 * sin(i));
  }
};
