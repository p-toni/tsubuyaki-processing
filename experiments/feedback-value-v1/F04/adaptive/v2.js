// F04/v2: A localized pulse deforms the source, traverses the bridge, then arrives.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 90);
  for (let i = 9000; i--;) {

    const family = i % 3;
    const u = i / 9000;
    const pulse = (.5 + .5 * sin(time - 2 * (family < 2 ? family : u))) ** 8;
    const angle = u * TAU;
    const radius = 30 + 7 * cos(i) + 15 * pulse * cos(3 * angle);
    if (family < 2) point(120 + 160 * family + radius * cos(angle), 200 + radius * sin(angle));
    else point(120 + 160 * u, 200 + 24 * pulse * sin(PI * u) + 3 * sin(i));
  }
};
