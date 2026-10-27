// F05/v3: A traveling fold turns a dense sheet while its upper corners remain anchored.
setup = () => { createCanvas(400, 400); strokeWeight(4); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 90);
  for (let i = 8000; i--;) {

    const u = i % 100 / 99 * 2 - 1;
    const v = floor(i / 100) / 79;
    const angle = 2.5 * v * sin(4 * v - time);
    stroke(125 + 80 * cos(angle));
    point(200 + 125 * u * cos(angle), 65 + 260 * v + 50 * u * sin(angle));
  }
};
