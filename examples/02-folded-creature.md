# Example 02 — Folded Creature

An original flattened 2D manifold. One loop samples a sheet; the same latent distance controls wrap phase and local radius, while axial×lateral coupling creates a folded lower body.

## Expanded

```js
let time = 0;
const size = 400;
const columns = 196;
const samples = 30000;

function setup() {
  createCanvas(size, size);
  stroke(255, 54);
}

function creature(index) {
  const u = index % columns;
  const v = index / columns;
  const lateral = u / 7 - 14;
  const axial = v / 8 - 12;
  const distance = mag(lateral, axial);

  const phase = distance / 3 - time + axial / 5;
  const radius = 55 + distance * 4 + lateral * sin(v / 3);

  point(
    200 + radius * cos(phase),
    200 + radius * sin(phase) / 2
      + axial * lateral * sin(distance * 2 + time)
  );
}

function draw() {
  background(7);
  time += PI / 90;
  for (let i = samples; i--;) creature(i);
}
```

## Tweet-ready

```js
t=0,a=(u,v,d=mag(x=u/7-14,y=v/8-12))=>point(200+(q=55+d*4+x*sin(v/3))*cos(c=d/3-t+y/5),200+q*sin(c)/2+y*x*sin(d*2+t));draw=_=>{t||createCanvas(w=400,w);background(7);stroke(w,54);for(t+=PI/90,i=3e4;i--;)a(i%196,i/196)}//#つぶやきProcessing
```

## What changed during golf

- a 2D surface is flattened into one 30k countdown loop
- `v=i/196` remains continuous; no flooring is required by the equation
- `d`, `x`, `y`, `q`, and `c` are assignment-expression caches
- initialization is guarded by `t||...`

## Variation directions

- replace `d*4` with `d**2/5` for a shell-like widening
- add `+i%2*3` to `c` to split two body layers
- change `y/5` phase coupling to `sin(y/3)/2` for softer axial folding
