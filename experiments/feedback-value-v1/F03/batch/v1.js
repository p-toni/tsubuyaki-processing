// F03/v1: A localized wave packet crosses and returns on an anchored sheet.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 100);
  for (let i = 6000; i--;) {

    const u = i % 100 / 99;
    const v = floor(i / 100) / 59;
    const center = abs(time / 3 % 2 - 1);
    const packet = exp(-80 * (u - center) ** 2) * sin(34 * u - 6 * time);
    point(50 + 300 * u, 90 + 220 * v + 40 * sin(PI * u) * sin(PI * v) * packet);
  }
};
