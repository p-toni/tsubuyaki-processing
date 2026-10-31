// Implicit solid: product of squared distances to two stationary centers.
// Radial contraction changes their shared transverse metric; the joint field stays connected.
setup = () => createCanvas(400, 400);
draw = () => {
  const time = frameCount / 60;
  background(9);
  for (let i = 64000; i--;) {
    const x = (i % 320 - 160) / 170;
    const y = (floor(i / 320) - 100) / 170;
    const distance = x - .75 * sin(time / 2);
    const contraction = 1 - .6 * exp(-40 * distance * distance);
    const radialSquared = sqrt(1.44 * x * x + .625 ** 4) - x * x - .36;
    const contractedSquared = contraction * contraction * radialSquared;
    const frontSquared = contractedSquared - y * y;
    const depth = sqrt(max(0, frontSquared));
    const shade = 70 + 170 * depth / (.04 + sqrt(max(0, contractedSquared)));
    stroke(frontSquared > 0 ? shade : 9);
    point(200 + 170 * x, 200 + 170 * y);
  }
};
