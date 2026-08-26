// v0.4 readable scaffold: compound morphology before golf.
// Design-time goal: one root mass + one repeated attached family + one surface field.
// Keep semantic controls separate until sensitivity testing is complete.
// For region masks, use harness.html?...&region=root|crown|appendages.

let time = 0;
const SIZE = 400;
const SAMPLES = 30000;
const COLS = 180;
const DEBUG_REGION = globalThis.__TSUBUYAKI_REGION__ || null;

// STRUCTURE CONTROLS
const rootWidth = 68;
const crownDepth = 0.9;
const cavityStrength = 15;
const appendageCount = 4;
const appendageLength = 54;
const attachmentHeight = 0.35;

// MOTION / SURFACE CONTROLS
const pulseStrength = 0.18;
const childPhaseLag = 0.35;
const foldFrequency = 7;

function setup() {
  createCanvas(SIZE, SIZE);
  stroke(255, DEBUG_REGION ? 255 : 55);
}

function sampleOrganism(index) {
  // Shared positional fields.
  const u = index % COLS;
  const v = index / COLS;
  const lateral = u / 7 - 13;
  const axial = v / 8 - 11;
  const distance = mag(lateral, axial);

  // Regional influence fields: crown + ventral attachment zone.
  const crown = max(0, 1 - abs((axial + 5) / 7));
  const ventral = max(0, 1 - abs((axial - attachmentHeight * 10) / 5));

  // Root field. Regions modify one shared body rather than becoming separate shapes.
  const rootPhase = distance / 3 - time / 4 + axial / 8;
  const pulse = 1 + pulseStrength * sin(time + axial / 5);
  const cavity = cavityStrength * crown * sin(distance * 0.8 - time);
  const rootRadius = pulse * (rootWidth + distance * 3 + crownDepth * crown * 24 - cavity);

  // Root-only projection is also the diagnostic support for root/crown masks.
  const rootFold = 7 * sin(distance * foldFrequency / 5 + axial - time * 2);
  const rootX = SIZE / 2 + (rootRadius + rootFold) * cos(rootPhase);
  const rootY = SIZE / 2 + rootRadius * sin(rootPhase) / 2 + axial * 8;

  if (DEBUG_REGION === 'root') return point(rootX, rootY);
  if (DEBUG_REGION === 'crown') {
    if (crown > 0.08) point(rootX, rootY);
    return;
  }

  // Repeated organ family. Residue identifies an instance; global fields make
  // siblings related but not exact copies.
  const organ = index % appendageCount;
  const sidePhase = organ * TWO_PI / appendageCount;
  const familyInfluence = ventral * (0.5 + 0.5 * sin(lateral / 3 + sidePhase));
  const childPhase = rootPhase + sidePhase + childPhaseLag * sin(time + organ);
  const childExtension = appendageLength * familyInfluence * sin(distance + time / 2);

  // Shared projection = attachment-by-phase-inheritance.
  const radius = rootRadius + childExtension;
  const surfaceFold = 7 * sin(distance * foldFrequency / 5 + axial - time * 2);
  const x = SIZE / 2 + (radius + surfaceFold) * cos(childPhase);
  const y = SIZE / 2 + radius * sin(childPhase) / 2 + axial * 8;

  if (DEBUG_REGION === 'appendages') {
    if (familyInfluence > 0.08) point(x, y);
    return;
  }

  point(x, y);
}

function draw() {
  background(8);
  time += PI / 100;
  for (let i = SAMPLES; i--;) sampleOrganism(i);
}

// Before golfing:
// 1. Render representative frames.
// 2. Perturb rootWidth, crownDepth, appendageLength, cavityStrength and childPhaseLag separately.
// 3. Render matching region masks at the same frame using &region=...
// 4. Validate declared region/subtree influence with check-control-scope.mjs.
// 5. Factor repeated anatomy/selectors only after control behavior is stable.