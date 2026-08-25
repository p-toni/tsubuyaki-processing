# Example 01 — Breathing Calyx

An original 1D manifold. A cosine lateral coordinate and linear axis form a hidden body; radial distance controls both the wrap angle and the fold pattern.

## Expanded

```js
let time = 0;
const size = 400;
const samples = 10000;

function setup() {
  createCanvas(size, size);
  stroke(255, 70);
}

function calyx(index) {
  const u = index / 240;
  const lateral = 6 * cos(u / 9);
  const axial = u / 18 - 9;
  const distance = mag(lateral, axial);

  const phase = distance / 2 - time;
  const radius = 70 + lateral * lateral;

  point(
    200 + radius * cos(phase),
    200 + 90 * sin(phase / 2)
      + lateral * axial * sin(distance * 3 - time * 2)
  );
}

function draw() {
  background(8);
  time += PI / 180;
  for (let i = samples; i--;) calyx(i);
}
```

## Tweet-ready

```js
t=0,a=(u,d=mag(x=6*cos(u/9),y=u/18-9))=>point((70+x*x)*cos(q=d/2-t)+200,200+90*sin(q/2)+x*y*sin(d*3-t*2));draw=_=>{t||createCanvas(w=400,w);background(8);stroke(w,70);for(t+=PI/180,i=1e4;i--;)a(i/240)}//#つぶやきProcessing
```

## What changed during golf

- helper default parameter computes `d`, while `x/y` assignments expose latent coordinates
- phase `q` is assigned at first use inside `point()`
- setup folds into the first frame
- one canvas variable supplies both dimensions and near-white stroke
- countdown loop + `1e4`

## Variation directions

- replace `x*x` with `abs(x)*12` for a thinner bell
- change `sin(d*3-t*2)` to `sin(d*d-t)` for concentric frills
- introduce `i%2*3` into `q` for a bilateral split
