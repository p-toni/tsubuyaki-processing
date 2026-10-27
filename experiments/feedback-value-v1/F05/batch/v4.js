// F05/v4: An asymmetric fold moves through an opaque sheet with fixed upper edge.
setup = () => { createCanvas(400, 400); strokeWeight(4); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 90);
  for (let i = 8000; i--;) {

    const u = i % 100 / 99 * 2 - 1;
    const v = floor(i / 100) / 79;
    const angle = v * (1.8 * sin(time) + .8 * sin(PI * u));
    stroke(130 + 80 * cos(angle));
    point(200 + 125 * u * cos(angle), 65 + 260 * v + 45 * u * sin(angle));
  }
};
