// F02/v2: Alternating underpass gaps share a traveling coordinate warp.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 90);
  for (let i = 8400; i--;) {

    const family = i % 2;
    const band = floor(i / 2) % 7 - 3;
    const along = i / 8400 * 280 - 140;
    const crossing = round(along / 36);
    const hidden = (crossing + band + family) % 2 && abs(along - crossing * 36) < 7;
    const width = 4 * sin(i);
    const x = family ? band * 36 + width : along;
    const y = family ? along : band * 36 + width;
    stroke(240, hidden ? 0 : 150);
    point(200 + x + 10 * sin(y / 40 - time), 200 + y);
  }
};
