// F03/v2: A broad fold travels with the reflected packet center.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 110);
  for (let i = 6000; i--;) {

    const u = i % 100 / 99;
    const v = floor(i / 100) / 59;
    const center = abs(time / 3 % 2 - 1);
    const packet = exp(-50 * (u - center) ** 2) * sin(24 * (u - center));
    point(50 + 300 * u, 90 + 220 * v + 60 * sin(PI * u) * sin(PI * v) * packet);
  }
};
