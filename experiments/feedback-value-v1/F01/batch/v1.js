// F01/v1: Two folded surfaces share a breathing separation variable.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 90);
  for (let i = 6000; i--;) {

    const side = i % 2 * 2 - 1;
    const angle = i / 6000 * TAU;
    const tube = i % 97 / 97 * TAU;
    const split = (.5 + .5 * sin(time)) ** 2;
    const radius = 42 + 14 * cos(tube) + 8 * sin(3 * angle - time) * (1 - split);
    point(200 + side * 75 * split + radius * cos(angle) * (1 - .25 * split),
      200 + .8 * radius * sin(angle) * (1 + .2 * split) + 12 * sin(tube));
  }
};
