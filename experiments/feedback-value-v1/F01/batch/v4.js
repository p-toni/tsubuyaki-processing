// F01/v4: A narrowing waist redistributes the lobes along a diagonal.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 90);
  for (let i = 6000; i--;) {

    const side = i % 2 * 2 - 1;
    const angle = i / 6000 * TAU;
    const split = .5 + .5 * cos(time);
    const radius = 38 + 12 * cos(i) + 10 * (1 - split) * cos(2 * angle + time);
    const x = side * 72 * split + radius * cos(angle);
    const y = radius * sin(angle) * (1.3 - .4 * split);
    point(200 + .94 * x - .34 * y, 200 + .34 * x + .94 * y);
  }
};
