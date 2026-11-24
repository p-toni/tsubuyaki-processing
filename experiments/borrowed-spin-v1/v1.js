let receiverAngle = 0;
let receiverSpeed = 0;

function setup() {
  createCanvas(400, 400);
  noStroke();
}

function draw() {
  background(16, 21, 24);

  // At tangency the centres are 120 apart horizontally and 50 vertically.
  const driverX = min(162, 139 - 49 * cos(frameCount / 58));
  const driverSpeed = 0.035;
  const touching = driverX === 162;
  receiverSpeed += touching ? 0.055 * (driverSpeed - receiverSpeed) : -0.016 * receiverSpeed;
  receiverAngle -= receiverSpeed;

  for (let side = 0; side < 2; side++) {
    const x = side ? 282 : driverX;
    const y = side ? 175 : 225;
    const spin = side ? receiverAngle : frameCount * driverSpeed;

    // Each smaller disc moves along a spiral inside the preceding layers.
    for (let depth = 0; depth < 65; depth++) {
      const angle = spin + depth / 19;
      const offset = 0.59 * depth;
      const light = 147 + 48 * cos(depth * 0.83) + 17 * cos(depth * 0.17);
      fill(light * (side ? 0.67 : 1.18), light * (side ? 1 : 0.82), light * (side ? 1.12 : 0.54));
      circle(x + offset * cos(angle), y + offset * sin(angle), 130 - 2 * depth);
    }
  }
}
