// Wake: one moving center drives a delayed localized deformation of a membrane.
setup = () => { createCanvas(400, 400); strokeWeight(2); };
draw = () => {
  const time = frameCount / 60;
  const center = .5 + .4 * sin(time / 2);
  const delayedCenter = .5 + .4 * sin(time / 2 - .45);
  background(9);
  for (let i = 10000; i--;) {
    if (i >= 1000) {
      const u = (i - 1000) % 100 / 99;
      const v = floor((i - 1000) / 100) / 89;
      const height = 45 * exp(-80 * (u - delayedCenter) ** 2) * sin(PI * v) * (1 + .3 * cos(14 * u - 2 * time));
      stroke(175, 100);
      point(50 + 300 * u + .15 * height, 135 + 150 * v - height);
    } else {
      const radius = 10 * sqrt(i / 1000);
      const angle = i * 2.399963;
      stroke(240);
      point(50 + 300 * center + radius * cos(angle), 195 + radius * sin(angle));
    }
  }
};
