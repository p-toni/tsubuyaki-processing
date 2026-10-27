// F05/v1: A ruled sheet twists progressively away from a fixed top edge.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 90);
  for (let i = 8000; i--;) {

    const u = i % 100 / 99 * 2 - 1;
    const v = floor(i / 100) / 79;
    const angle = v * (1.4 * sin(time) + .7 * sin(4 * v - time));
    stroke(180 + 60 * cos(angle), 100);
    point(200 + 135 * u * cos(angle), 65 + 270 * v + 40 * u * sin(angle));
  }
};
