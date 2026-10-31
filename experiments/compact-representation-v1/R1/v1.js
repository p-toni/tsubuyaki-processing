// Swept surface: two chambers share one axial radius and one traveling contraction.
setup = () => { createCanvas(400, 400); strokeWeight(2); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  for (let i = 48000; i--;) {
    const axial = i / 24000 - 1;
    const across = i % 240 / 120 - 1;
    const distance = axial - .8 * sin(time / 2);
    const contraction = 1 - .6 * exp(-40 * distance * distance);
    const radius = (25 + 90 * axial * axial) * sqrt(1 - axial * axial) * contraction;
    stroke(70 + 170 * sqrt(1 - across * across));
    point(200 + 150 * axial, 200 + radius * across);
  }
};
