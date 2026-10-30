// Thread v2: broader folded material, a deforming loop, and oblique projection.
setup = () => { createCanvas(400, 400); strokeWeight(3); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  for (let i = 18000; i--;) {
    const layer = floor(i / 6000);
    const along = i % 6000 / 5999;
    let x, y;
    if (layer === 1) {
      const width = 20 * sin(i);
      const phase = 8 * along - time;
      x = 45 + 310 * along - .4 * width * sin(phase);
      y = 200 + 40 * sin(phase) * sin(PI * along) + width * cos(phase);
      stroke(160 + 65 * cos(width / 20) + 15 * sin(phase));
    } else {
      const angle = PI * (along + (layer === 2));
      const radius = 80 + 10 * sin(i) + 8 * cos(3 * angle - time / 2);
      x = 200 + radius * cos(angle);
      y = 200 + .6 * radius * sin(angle);
      stroke(165 - 30 * layer + 45 * cos(sin(i)));
    }
    point(x + .25 * (y - 200), y - .2 * (x - 200));
  }
};
