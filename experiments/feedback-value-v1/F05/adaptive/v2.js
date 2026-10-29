// F05/v2: Opaque material and depth shading expose overlap in the twisting sheet.
setup = () => { createCanvas(400, 400); strokeWeight(3); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 90);
  for (let i = 8000; i--;) {

    const u = i % 100 / 99 * 2 - 1;
    const v = floor(i / 100) / 79;
    const angle = v * (1.8 * sin(time) + .8 * sin(4 * v - time));
    stroke(140 + 75 * cos(angle) + 30 * u * sin(angle));
    point(200 + 135 * u * cos(angle), 65 + 260 * v + 45 * u * sin(angle));
  }
};
