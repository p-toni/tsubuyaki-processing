// Fronds: a shared root and seven axial families with a traveling bend.
setup = () => createCanvas(400, 400);
draw = () => {
  background(9);
  stroke(240, 50);
  const time = frameCount / 60;
  for (let i = 14000; i--;) {
    const along = i / 14000;
    const member = i % 7 - 3;
    const angle = member / 5 + along / 3 * sin(8 * along - 2 * time + member);
    const width = 8 * sin(i) * sin(PI * along);
    point(200 + 250 * along * sin(angle) + width,
      350 - 250 * along * cos(angle));
  }
};
