// F01/v2: Filled lobes deform as their shared material separates.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 120);
  for (let i = 5000; i--;) {

    const side = i % 2 * 2 - 1;
    const angle = i * 2.399963;
    const split = .5 + .5 * sin(time);
    const radius = sqrt(i / 5000) * (55 - 15 * split) * (1 + .12 * cos(3 * angle - time));
    point(200 + side * 80 * split + radius * cos(angle),
      200 + radius * sin(angle) * (1 + .3 * split));
  }
};
