// Aperture: an opaque folded annulus covers a moving rear material.
setup = () => { createCanvas(400, 400); strokeWeight(3); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  for (let i = 12000; i--;) {
    if (i >= 8000) {
      const radius = 60 * sqrt((i - 8000) / 4000);
      const angle = i * 2.399963 + time / 3;
      stroke(75 + 45 * sin(radius / 5 - time + angle));
      point(200 + radius * cos(angle), 200 + radius * sin(angle));
    } else {
      const angle = i % 160 / 160 * TAU;
      const across = floor(i / 160) / 49;
      const inner = 22 + 30 * (.5 + .5 * sin(time)) * (1 + .2 * cos(3 * angle - time));
      const radius = inner + across * (135 - inner);
      const fold = 10 * sin(6 * angle + 4 * across - time) * sin(PI * across);
      stroke(135 + 70 * cos(6 * angle + 4 * across - time));
      point(200 + radius * cos(angle), 200 + .75 * radius * sin(angle) + fold);
    }
  }
};
