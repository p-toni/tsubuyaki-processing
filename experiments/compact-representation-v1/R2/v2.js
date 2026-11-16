// Implicit solid v2: the field's actual surface gradient controls directional light.
setup = () => { createCanvas(400, 400); strokeWeight(2); };
draw = () => {
  const time = frameCount / 60;
  background(9);
  for (let i = 64000; i--;) {
    const x = (i % 320 - 160) / 170;
    const y = (floor(i / 320) - 100) / 170;
    const distance = x - .75 * sin(time / 2);
    const pulse = exp(-40 * distance * distance);
    const contraction = 1 - .6 * pulse;
    const contractionSlope = 48 * distance * pulse;
    const sharedRoot = sqrt(1.44 * x * x + .625 ** 4);
    const radialSquared = sharedRoot - x * x - .36;
    const radialSlope = 1.44 * x / sharedRoot - 2 * x;
    const contractedSquared = contraction * contraction * radialSquared;
    const frontSquared = contractedSquared - y * y;
    const depth = sqrt(max(0, frontSquared));
    const normalX = -2 * contraction * contractionSlope * radialSquared
      - contraction * contraction * radialSlope;
    const normalY = 2 * y;
    const normalZ = 2 * depth;
    const normalLength = sqrt(max(.000001,
      normalX * normalX + normalY * normalY + normalZ * normalZ));
    const light = max(0, (-.35 * normalX - .4 * normalY + .85 * normalZ) / normalLength);
    const highlight = (normalZ / normalLength) ** 16;
    stroke(frontSquared > 0 ? 40 + 170 * light + 45 * highlight : 9);
    point(200 + 160 * x + 45 * y, 200 - 65 * x + 150 * y);
  }
};
