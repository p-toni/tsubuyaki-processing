// Gather revision: angular phase cohorts organize the contraction into three sectors.
setup = () => createCanvas(400, 400);
draw = () => {
  background(9);
  stroke(240, 95);
  const time = frameCount / 60;
  for (let i = 1800; i--;) {
    const distance = sqrt(i / 1800);
    const angle = i * 2.399963 + time * (1 - distance);
    const phase = time - .9 * distance + .6 * sin(3 * angle);
    const radius = 18 + 140 * distance * (.5 + .5 * sin(phase));
    point(200 + radius * cos(angle), 200 + .85 * radius * sin(angle));
  }
};
