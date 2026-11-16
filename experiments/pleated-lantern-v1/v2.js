// A faint standing pleat remains in the skin between traveling creases.
setup = () => { createCanvas(400, 400); strokeWeight(2); };
draw = () => {
  background(12);
  for (let i = 46080; i--;) {
    const along = (i % 180) / 57;
    const around = i / 14400 - 1.6;
    const band = cos(along - frameCount * PI / 360) ** 4;
    const fold = cos(9 * around + 2 * along) * (.14 + band);
    const radius = 16 + (77 + 32 * fold) * sin(along);
    const facing = cos(around);
    const light = 92 + 75 * fold + 42 * facing;
    stroke(light + 38, light, 89);
    point(200 + 20 * cos(along) + radius * sin(around),
      67 + 79 * along + .38 * radius * facing);
  }
};
