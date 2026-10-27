// F06/v2: A circular clearance shapes the paired paths around the obstacle.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 180);
  for (let i = 2400; i--;) {

    const lane = (i % 40 - 19.5) * 5;
    const x = (i / 2400 * 400 + time * 40) % 400 - 200;
    const y = (lane > 0 ? 1 : -1) * sqrt(lane * lane + max(0, 3600 - x * x));
    point(200 + x, 200 + y);
  }
};
