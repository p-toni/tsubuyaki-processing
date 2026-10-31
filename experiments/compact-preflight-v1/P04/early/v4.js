// Wake v4: a visible forcing spot and its delayed ridge share one membrane sampler.
setup = () => createCanvas(400, 400);
draw = () => {
  const time = frameCount / 60;
  background(9);
  for (let i = 40000; i--;) {
    const u = i % 200 / 100 - 1;
    const v = i / 20000 - 1;
    const driveDistance = u - .8 * sin(time / 2);
    const delayedDistance = u - .8 * sin(time / 2 - .45);
    const height = 80 * exp(-30 * delayedDistance * delayedDistance) * (1 - v * v);
    stroke(driveDistance * driveDistance + v * v < .01 ? 255 : 150);
    point(200 + 150 * u, 200 + 90 * v * sqrt(1 - u * u) - height);
  }
};
