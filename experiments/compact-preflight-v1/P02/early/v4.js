// Thread v4: one common parameterization, three opaque painter layers.
setup = () => { createCanvas(400, 400); strokeWeight(2); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  for (let i = 30000; i--;) {
    const layer = floor(i / 10000);
    const along = i % 10000 / 10000;
    const angle = PI * (along + (layer === 2));
    const radius = 80 + 10 * sin(i);
    const x = layer === 1 ? 300 * along - 150 : radius * cos(angle);
    const y = layer === 1 ? (40 * sin(2 * angle - time) + 14 * sin(i)) * sin(angle) : .6 * radius * sin(angle);
    stroke(150 - 30 * layer + 80 * cos(sin(i)));
    point(200 + x + .2 * y, 200 + y - .2 * x);
  }
};
