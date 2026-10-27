// F02/v3: Diagonal woven bands use explicit alternating gaps.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 90);
  for (let i = 8400; i--;) {

    const family = i % 2;
    const band = floor(i / 2) % 7 - 3;
    const along = i / 8400 * 250 - 125;
    const crossing = round(along / 32);
    const hidden = (crossing + band + family) % 2 && abs(along - crossing * 32) < 6;
    const width = 3 * sin(i);
    const x = (family ? band * 32 + width : along);
    const y = (family ? along : band * 32 + width);
    stroke(240, hidden ? 0 : 160);
    point(200 + .7 * (x - y) + 9 * sin((x + y) / 50 - time), 200 + .7 * (x + y));
  }
};
