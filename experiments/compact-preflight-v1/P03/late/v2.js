// Relay v2: a shared arch of heights and curved material replace uniform spindles.
setup = () => { createCanvas(400, 400); strokeWeight(2); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  for (let i = 12000; i--;) {
    const unit = floor(i / 2000);
    const height = i % 2000 / 2000;
    const pulse = (.5 + .5 * cos(1.2 * time - .75 * unit)) ** 8;
    const length = 150 + 80 * sin(PI * (unit + .5) / 6);
    const width = 12 * sin(i) * sin(PI * height) * (1 + .9 * pulse);
    stroke(160 + 80 * cos(5 * height - .75 * unit), 150);
    point(45 + 54 * unit + 40 * pulse * height * height + 12 * sin(PI * height) * sin(1.7 * unit) + width,
      330 - length * height);
  }
};
