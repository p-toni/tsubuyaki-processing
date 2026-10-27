// F03/v4: Two surface coordinates reveal a localized traveling ridge in projection.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 120);
  for (let i = 8000; i--;) {

    const u = i % 100 / 99;
    const v = floor(i / 100) / 79;
    const center = abs(time / 3 % 2 - 1);
    const height = 65 * sin(PI * u) * exp(-70 * (u - center) ** 2) * sin(PI * v);
    point(50 + 300 * u + .22 * height, 110 + 170 * v - height);
  }
};
