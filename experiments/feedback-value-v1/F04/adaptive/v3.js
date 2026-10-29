// F04/v3: One continuous dumbbell surface carries a phase-delayed deformation.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 100);
  for (let i = 7000; i--;) {

    const angle = i / 7000 * TAU;
    const x = 140 * cos(angle);
    const pulse = (.5 + .5 * sin(time - (x + 140) / 140)) ** 8;
    const width = 8 + 65 * cos(angle) ** 4 + 18 * pulse;
    point(200 + x, 200 + (width + 5 * sin(i)) * sin(angle));
  }
};
