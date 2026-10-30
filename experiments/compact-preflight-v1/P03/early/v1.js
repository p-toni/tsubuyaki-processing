// Relay: a common localized pulse bends six rooted material units in sequence.
setup = () => { createCanvas(400, 400); strokeWeight(2); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  for (let i = 12000; i--;) {
    const unit = floor(i / 2000);
    const height = i % 2000 / 2000;
    const pulse = (.5 + .5 * cos(1.2 * time - .75 * unit)) ** 8;
    const width = 8 * sin(i) * sqrt(sin(PI * height)) * (1 + 1.5 * pulse * height);
    stroke(110 + 120 * height, 160);
    point(45 + 54 * unit + 48 * pulse * height * height + width, 325 - 240 * height);
  }
};
