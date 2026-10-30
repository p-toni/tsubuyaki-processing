// Wake v2: rounded membrane sampling and a shaded exciter give the event material.
setup = () => { createCanvas(400, 400); strokeWeight(2); };
draw = () => {
  const time = frameCount / 60;
  const center = .8 * sin(time / 2);
  const delayedCenter = .8 * sin(time / 2 - .45);
  background(9);
  for (let i = 10000; i--;) {
    if (i >= 1000) {
      const u = (i - 1000) % 100 / 99 * 2 - 1;
      const v = floor((i - 1000) / 100) / 89 * 2 - 1;
      const height = 65 * exp(-25 * (u - delayedCenter) ** 2) * (1 - v * v) * (1 + .2 * cos(10 * u - 2 * time));
      stroke(185, 130);
      point(200 + 150 * u * sqrt(1 - .8 * v * v) + .12 * height,
        210 + 90 * v * sqrt(1 - .8 * u * u) - height);
    } else {
      const radius = 10 * sqrt(i / 1000);
      const angle = i * 2.399963;
      stroke(160 + 70 * sqrt(1 - i / 1000));
      point(200 + 150 * center + radius * cos(angle), 200 + radius * sin(angle));
    }
  }
};
