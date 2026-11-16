// Swept surface v2: contraction gathers a folded skin on a curved, obliquely viewed body.
setup = () => { createCanvas(400, 400); strokeWeight(2); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  for (let i = 48000; i--;) {
    const axial = i / 24000 - 1;
    const angle = (i % 240 / 240 - .5) * PI;
    const distance = axial - .8 * sin(time / 2);
    const squeeze = .6 * exp(-40 * distance * distance);
    const fold = cos(10 * angle);
    const radius = (25 + 90 * axial * axial) * sqrt(1 - axial * axial)
      * (1 - squeeze) * (1 + .25 * squeeze * fold);
    const depth = radius * cos(angle);
    stroke(65 + 140 * cos(angle) - 35 * sin(angle) + 50 * squeeze * fold);
    point(195 + 150 * axial + .35 * depth,
      205 + 30 * sin(2 * axial) + radius * sin(angle) - .25 * depth);
  }
};
