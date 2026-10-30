// Thread: back loop, broad traveling ribbon, then front loop.
setup = () => { createCanvas(400, 400); strokeWeight(3); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  for (let i = 15000; i--;) {
    const layer = floor(i / 5000);
    const along = i % 5000 / 4999;
    if (layer === 1) {
      const width = 12 * sin(i);
      const wave = sin(10 * along - time);
      stroke(160 + 65 * cos(width / 12) + 15 * wave);
      point(45 + 310 * along, 200 + 15 * wave * sin(PI * along) + width);
    } else {
      const angle = PI * (along + (layer === 2));
      const radius = 80 + 10 * sin(i);
      stroke(165 - 30 * layer + 45 * cos((radius - 80) / 10));
      point(200 + radius * cos(angle), 200 + .6 * radius * sin(angle));
    }
  }
};
