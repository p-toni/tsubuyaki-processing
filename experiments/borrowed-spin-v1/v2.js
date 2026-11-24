let receiverAngle = 0;
let receiverSpeed = 0;

function setup() {
  createCanvas(400, 400);
  noStroke();
}

function draw() {
  background(16, 21, 24);

  const time = frameCount / 58;
  const gap = max(0, 22 + 42 * cos(time));
  const distance = 130 + gap;
  const bearing = 0.33 + 0.38 * sin(time);
  const driverSpeed = 0.035;
  receiverSpeed += gap === 0 ? 0.055 * (driverSpeed - receiverSpeed) : -0.016 * receiverSpeed;
  receiverAngle -= receiverSpeed;

  for (let side = 0; side < 2; side++) {
    const x = side ? 276 : 276 - distance * cos(bearing);
    const y = side ? 190 : 190 + distance * sin(bearing);
    const spin = side ? receiverAngle : frameCount * driverSpeed;
    const warmth = side ? -27 : 46;

    for (let depth = 0; depth < 65; depth++) {
      const angle = spin + depth / 19;
      const offset = 0.59 * depth;
      // The ridge brightens as its eccentric centre turns toward a fixed light.
      const light = 125 + 48 * cos(depth * 0.83) + 26 * cos(angle + 1);
      fill(light + warmth, light, light - warmth);
      circle(x + offset * cos(angle), y + offset * sin(angle), 130 - 2 * depth);
    }
  }
}
