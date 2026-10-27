// F03/v3: A single rounded crest reflects while the lateral edges stay fixed.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 110);
  for (let i = 6000; i--;) {

    const u = i % 100 / 99;
    const v = floor(i / 100) / 59;
    const center = abs(time / 3 % 2 - 1);
    const packet = exp(-100 * (u - center) ** 2);
    point(50 + 300 * u, 90 + 220 * v + 75 * sin(PI * u) * sin(PI * v) * packet);
  }
};
