# Example 03 — Coupled Attractor

An original iterated map rather than an independent point manifold. Each iteration updates a tiny nonlinear state and plots it; the dense trajectory becomes a living knot.

## Expanded

```js
let time = 0;
const size = 400;
const iterations = 20000;

function setup() {
  createCanvas(size, size);
  stroke(255, 40);
}

function draw() {
  background(6);

  let x = 0.1;
  let y = 0.1;

  for (let i = iterations; i--;) {
    const coupling = sin(x * y * 3 + time) + cos(y * 2);
    x = sin(y * 4) + coupling * 0.3;
    y = cos(x * 3) + coupling * 0.2;
    point(200 + x * 70, 200 + y * 70);
  }

  time += 0.01;
}
```

## Tweet-ready

```js
t=0,draw=_=>{t||createCanvas(w=400,w);background(6);stroke(w,40);for(x=y=.1,i=2e4;i--;){r=sin(x*y*3+t)+cos(y*2);x=sin(y*4)+r*.3;y=cos(x*3)+r*.2;point(200+x*70,200+y*70)}t+=.01}//#つぶやきProcessing
```

## What changed during golf

- local state variables become implicit globals reset each frame
- the coupled term `r` is reused across both state updates
- `x` is updated before `y` intentionally; this defines the discrete map
- no helper function is needed because the loop body is already compact

## Variation directions

- change `x*y*3` to `(x*x-y*y)*2` for a different attractor topology
- use `sin(time*2)` as one coupling coefficient for breathing
- map `point()` through a tiny polar phase for a pseudo-3D knot
