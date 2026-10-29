// F06/adaptive-v2: persistent brightness differences expose material transport.
setup = () => { createCanvas(400, 400); strokeWeight(1.5); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  for (let i = 1600; i--;) {
    const lane = (i % 40 - 19.5) * 5;
    const x = (i / 1600 * 400 + time * 40) % 400 - 200;
    const y = lane + (lane > 0 ? 1 : -1) * 65 * exp(-x * x / 2500);
    stroke(240, 60 + 180 * (.5 + .5 * sin(i * .39)) ** 4);
    point(200 + x, 200 + y);
  }
};
