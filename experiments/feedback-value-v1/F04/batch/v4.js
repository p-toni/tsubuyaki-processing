// F04/v4: A narrow neck and soft lobes share a traveling compression field.
setup = () => { createCanvas(400, 400); strokeWeight(1); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  stroke(240, 110);
  for (let i = 7000; i--;) {

    const angle = i / 7000 * TAU;
    const x = 140 * cos(angle);
    const wave = sin(time - (x + 140) / 110);
    const width = 6 + 70 * cos(angle) ** 4;
    point(200 + x, 200 + (width * (1 + .3 * wave) + 5 * sin(i)) * sin(angle));
  }
};
