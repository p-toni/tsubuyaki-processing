# Simple arm readable sources — candidate render 1

These are the readable semantic sources for the first compact S-arm candidates. The compact post may rename variables and collapse algebra, but it must preserve the relationships named here and in `briefs.json`.

## B01 — breathing recurrent knot

```js
setup = () => createCanvas(400, 400)
draw = () => {
  background(9)
  stroke(255, 80)
  let x = 0, y = 0
  for (let i = 0; i < 2600; i++) {
    const previousX = x
    x = sin(2*y + frameCount/90) + cos(3*x)
    y = sin(2*previousX) - cos(3*y - frameCount/120)
    point(200 + 72*x, 200 + 72*y)
  }
}
```

Cause: two coupled recurrent state variables with different temporal phases; the dense projection is the knot.

## B02 — asymmetric drifting braid

```js
setup = () => createCanvas(400, 400)
draw = () => {
  background(9)
  stroke(255, 75)
  let x = .2, y = .1
  for (let i = 0; i < 3000; i++) {
    const previousX = x
    x = sin(3*y) + cos(2*x + frameCount/110)
    y = sin(2.7*previousX) - cos(2.2*y - frameCount/170)
    const drift = 18*sin(i/90)
    point(200 + 82*x + drift, 200 + 58*y)
  }
}
```

Cause: anisotropic coupled recurrence plus a non-rigid secondary displacement along the generated braid.

## B03 — hollow recurrent skein

```js
setup = () => createCanvas(400, 400)
draw = () => {
  background(9)
  stroke(255, 70)
  let x = .3, y = .2
  for (let i = 0; i < 2800; i++) {
    const previousX = x
    x = sin(2.6*y + frameCount/80) + .7*cos(3.1*x)
    y = sin(2.4*previousX - frameCount/150) - .8*cos(2.9*y)
    const radialGap = 28/mag(x, y)
    point(200 + 66*x + x*radialGap, 200 + 66*y + y*radialGap)
  }
}
```

Cause: coupled recurrence projected through an explicit radial-gap transform that keeps the center hollow.

## B04 — mass-exchanging stretched loop

```js
setup = () => createCanvas(400, 400)
draw = () => {
  background(9)
  stroke(255, 70)
  let x = .1, y = .2
  for (let i = 0; i < 2600; i++) {
    const previousX = x
    x = sin(2.3*y) + cos(3*x + frameCount/120)
    y = sin(2.8*previousX - frameCount/140) - cos(2.1*y)
    const exchange = 12*sin(x + frameCount/80)
    point(200 + 92*x, 200 + 48*y + exchange)
  }
}
```

Cause: elongated recurrence projection plus a slower deformation coupled to the current recurrent x-state.

## B05 — unequal three-lobed tangle

```js
setup = () => createCanvas(400, 400)
draw = () => {
  background(9)
  stroke(255, 75)
  let x = .2, y = .4
  for (let i = 0; i < 2800; i++) {
    const previousX = x
    x = sin(3*y) + .8*cos(2*x - frameCount/180)
    y = sin(2*previousX) + .7*cos(3*y + frameCount/130)
    const precession = i/900 + frameCount/600
    point(200 + 68*x + 12*cos(3*precession), 200 + 68*y + 8*sin(3*precession))
  }
}
```

Cause: asymmetric recurrent tangle with a slow threefold positional perturbation layered onto, not replacing, the recurrence.

## B06 — breathing-gap sparse recurrence

```js
setup = () => createCanvas(400, 400)
draw = () => {
  background(9)
  stroke(255, 85)
  let x = .2, y = .2
  for (let i = 0; i < 1800; i++) {
    const previousX = x
    x = sin(2.4*y) + .65*cos(2.7*x + frameCount/120)
    y = sin(2.1*previousX) - .7*cos(2.5*y - frameCount/160)
    const radialGap = (22 + 10*sin(frameCount/70))/mag(x, y)
    point(200 + x*(64 + radialGap), 200 + y*(64 + radialGap))
  }
}
```

Cause: sparse coupled recurrence with one global time-varying radial gap.

## B07 — tapered traveling ribbon

```js
setup = () => createCanvas(400, 400)
draw = () => {
  background(9)
  stroke(255, 120)
  for (let i = 0; i < 900; i++) {
    const u = i/450 - 1
    const taper = pow(1 - abs(u), .7)
    const spine = 200 + 52*taper*sin(9*u - frameCount/28)
    point(200 + 165*u, spine)
    point(200 + 165*u, spine + 10*taper*sin(18*u - frameCount/20))
  }
}
```

Cause: open axial coordinate, bilateral taper and two coupled traveling phases.

## B08 — two-rate interference filament

```js
setup = () => createCanvas(400, 400)
draw = () => {
  background(9)
  stroke(255, 110)
  for (let i = 0; i < 1000; i++) {
    const u = i/500 - 1
    const y = 200 + 44*sin(7*u - frameCount/32) + 18*sin(15*u + frameCount/47)
    point(200 + 165*u, y)
  }
}
```

Cause: one open axial coordinate carrying two traveling waves with different directions/rates.

## B09 — quiet-center active-end ribbon

```js
setup = () => createCanvas(400, 400)
draw = () => {
  background(9)
  stroke(255, 110)
  for (let i = 0; i < 900; i++) {
    const u = i/450 - 1
    const endAmplitude = .2 + .8*pow(abs(u), 1.5)
    const y = 200 + 58*endAmplitude*sin(8*u - frameCount/30)
    point(200 + 165*u, y)
    point(200 + 165*u, y + 8*sin(18*u - frameCount/44))
  }
}
```

Cause: axial parameter with amplitude explicitly increasing toward both ends plus a smaller traveling ripple.

## B10 — counter-propagating woven filament

```js
setup = () => createCanvas(400, 400)
draw = () => {
  background(9)
  stroke(255, 105)
  for (let i = 0; i < 1000; i++) {
    const u = i/500 - 1
    const coarse = 46*sin(7*u - frameCount/34)
    const fine = 9*sin(31*u + frameCount/19)
    point(200 + 165*u, 200 + coarse + fine)
  }
}
```

Cause: an open axis carrying coarse and fine waves with opposite temporal phase directions.

## B11 — sharp continuous lightning ribbon

```js
setup = () => createCanvas(400, 400)
draw = () => {
  background(9)
  stroke(255, 115)
  for (let i = 0; i < 850; i++) {
    const u = i/425 - 1
    const sharpContinuousBend = 55*pow(sin(5*u), 3)
    const pulse = 12*sin(14*u - frameCount/35)
    point(200 + 165*u, 200 + sharpContinuousBend + pulse)
  }
}
```

Cause: a continuous cubic-sine axial bend carrying a separate traveling pulse.

## B12 — moving-waist S filament

```js
setup = () => createCanvas(400, 400)
draw = () => {
  background(9)
  stroke(255, 110)
  for (let i = 0; i < 1000; i++) {
    const u = i/500 - 1
    const waistPosition = u - .55*sin(frameCount/80)
    const movingWaist = 1 - .6/(1 + 20*waistPosition*waistPosition)
    const y = 200 + 62*sin(3.2*u)*movingWaist
    point(200 + 165*u, y)
  }
}
```

Cause: a persistent open S-shaped axis whose local amplitude is attenuated by a moving rational waist.
