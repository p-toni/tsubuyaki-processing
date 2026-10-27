// F01/v3: A quartic contour changes from one necked body to two lobes.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 90);
  for (let i = 6000; i--;) {

    const angle = i / 6000 * TAU;
    const width = 66 + 22 * sin(time) + 5 * sin(i);
    const discriminant = width ** 4 - 75 ** 4 * sin(2 * angle) ** 2;
    const radius = sqrt(max(0, 75 ** 2 * cos(2 * angle) + sqrt(max(0, discriminant))));
    stroke(240, discriminant > 0 ? 100 : 0);
    point(200 + radius * cos(angle), 200 + radius * sin(angle));
  }
};
