# 04 — Compound Morphology: Crowned Bilateral Creature

This example demonstrates the **v0.3 compiler**, not a literal animal preset. The readable system distinguishes a root axial body from a crown region and bilateral side family; the final tweet collapses those decisions into a region selector, parity, shared phase and one projection.

## Morphology plan

```text
root: axial folded body
├── crown region: wider lateral skeleton, quieter local deformation
└── bilateral side family: parity-separated phase, stronger body deformation

shared:
- axial coordinate e
- lateral coordinate k
- radial distance d
- parent projection phase c
- one master clock t
```

The important property is that the crown and sides are **interpretations of one positional system**. They are not separately positioned objects.

## Readable design form

```js
let time = 0;
const size = 400;
const samples = 20000;

// Semantic controls kept separate during design.
const crownBoundary = 8;
const crownWidth = 9;
const trunkWidth = 4;
const crownDeformation = 3;
const trunkDeformation = 7;
const bilateralPhase = 3;

function setup() {
  createCanvas(size, size);
  stroke(255, 70);
}

function sampleCreature(i) {
  const y = i / 650;
  const crown = y < crownBoundary;

  // Shared positional information.
  const lateral = (crown ? crownWidth : trunkWidth + cos(y)) * cos(i / 23);
  const axial = y / 6 - 12;
  const distance = mag(lateral, axial);

  // Root phase; parity encodes a related bilateral family.
  const phase = distance / 3 - time / 4 + (i % 2) * bilateralPhase;

  // Regional interpretation of the same body field.
  const deformation = crown ? crownDeformation : trunkDeformation;
  const radius = 70
    + lateral * lateral / 2
    + lateral * sin(distance * distance / 9 - time) * deformation;

  // One shared projection keeps the morphology coherent.
  point(
    200 + radius * cos(phase),
    200 + radius * sin(phase) / 2 + distance * axial * 2
  );
}

function draw() {
  background(9);
  time += PI / 80;
  for (let i = samples; i--;) sampleCreature(i);
}
```

## Compilation steps

1. `crownBoundary` becomes the cheap positional selector `y<8`.
2. Crown/trunk widths become two branches inside the **same** `k` body coordinate.
3. Crown/trunk deformation strengths reuse the same selector instead of creating two generators.
4. Bilateral anatomy is encoded by `i%2*3` and inherits the root phase.
5. The root and regions share `k/e/d/q/c`; no absolute child placement survives.
6. Semantic control names are inlined only after the phenotype is chosen.

## Tweet-ready

```js
a=(y,d=mag(k=(y<8?9:4+cos(y))*cos(i/23),e=y/6-12))=>point((q=70+k*k/2+k*sin(d*d/9-t)*(y<8?3:7))*cos(c=d/3-t/4+i%2*3)+200,200+q/2*sin(c)+d*e*2);t=0,draw=_=>{t||createCanvas(w=400,w);background(9).stroke(w,70);for(t+=PI/80,i=2e4;i--;)a(i/650)}//#つぶやきProcessing
```

Verified for the complete post:

- raw Unicode code points: **258**
- X-weighted length: **262**
- result: **PASS**

This finishes 18 weighted characters below the hard limit. The spare budget should not be filled unless another rule materially improves the morphology.

## What to vary before golf

- `crownBoundary`: moves the regional identity boundary.
- `crownWidth`: changes the upper/root hierarchy without changing the trunk rule.
- `trunkDeformation`: changes lower-body activity while retaining the crown.
- `bilateralPhase`: alters the disagreement between the two side families.
- time divisor: changes inherited body motion without introducing a second clock.

## Limitation

This compact example demonstrates **regionalization + bilateral family reuse**, not the maximum possible v0.3 complexity. More compound requests should add a second organ family only when it can be expressed through the same positional/attachment system rather than by adding independent object code.