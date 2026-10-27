// F06/v4: Lane-dependent speed makes material shear visible around the obstacle.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 180);
  for (let i = 2400; i--;) {

    const lane = (i % 40 - 19.5) * 5;
    const x = (i / 2400 * 400 + time * 55 / (1 + abs(lane) / 100)) % 400 - 200;
    const y = lane + (lane > 0 ? 1 : -1) * 65 * exp(-x * x / 2500);
    point(200 + x, 200 + y);
  }
};
