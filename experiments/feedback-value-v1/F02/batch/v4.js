// F02/v4: Broad woven bands deform together around their intersections.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 90);
  for (let i = 6000; i--;) {

    const family = i % 2;
    const band = floor(i / 2) % 5 - 2;
    const along = i / 6000 * 260 - 130;
    const crossing = round(along / 48);
    const hidden = (crossing + band + family) % 2 && abs(along - crossing * 48) < 12;
    const width = 8 * sin(i);
    const x = family ? band * 48 + width : along;
    const y = family ? along : band * 48 + width;
    stroke(190 + 50 * cos(width / 8), hidden ? 0 : 200);
    point(200 + x + 12 * sin(y / 45 - time), 200 + y + 6 * sin(x / 50 - time));
  }
};
