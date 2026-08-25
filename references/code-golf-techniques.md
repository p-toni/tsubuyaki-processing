# Code-Golf Techniques for #つぶやきProcessing

Use this document after the readable sketch works. The ordering matters: high-level representation changes usually save more characters than punctuation tricks.

Legend:

- **Stable** — normal JavaScript/p5 semantics; preferred.
- **Contextual** — safe only when assumptions are true.
- **Fragile** — version/renderer/coercion dependent; test before shipping.

## 1. Eliminate `setup()` with a first-frame guard — Stable

Readable:

```js
let t=0;
function setup(){createCanvas(400,400)}
function draw(){t+=.01;/* ... */}
```

Golf shape:

```js
t=0,draw=_=>{t++||createCanvas(w=400,w);/* ... */}
```

If `t` must advance by a non-unit amount, separate initialization and update:

```js
t=0,draw=_=>{t||createCanvas(w=400,w);t+=PI/120;/* ... */}
```

Do not use `t++||...` if the precise value of `t` on the first frame is visually important and the later formula assumes another unit.

## 2. Replace `frameCount`, `width`, `height` — Stable

`frameCount` is long. Maintain `t`, `f`, or another one-letter clock.

For a square canvas:

```js
createCanvas(w=400,w)
```

Now `w` can also supply:

- center: `w/2`
- near-white stroke through p5 clamping: `stroke(w,80)` (contextual visual equivalence)
- loop/domain constants if useful

Break-even rule: assigning a repeated long literal/name is useful only when its reuses recover the assignment cost.

## 3. Arrow functions — Stable

```js
function draw(){...}
```

becomes:

```js
draw=_=>{...}
```

For helpers:

```js
function p(x,y){return ...}
```

becomes:

```js
p=(x,y)=>...
```

A dummy `_` avoids the two characters of `()` for a zero-argument arrow.

## 4. Implicit globals — Contextual

p5.js global-mode sketches are commonly run as non-module, non-strict scripts, allowing:

```js
i=0
```

instead of `let i=0`.

This is idiomatic in Tsubuyaki Processing but poor general JavaScript practice. It will fail under strict/module semantics. The skill assumes a conventional p5 global-script environment unless the user specifies otherwise.

## 5. Countdown loops — Stable

Instead of:

```js
for(i=0;i<10000;i++)
```

use:

```js
for(i=1e4;i--;)
```

The test expression is the post-decrement; zero is falsy.

Be aware that the index sequence changes. If order matters, compensate mathematically rather than assuming equivalence.

## 6. Flatten nested grids — Stable

Readable:

```js
for(y=0;y<n;y++)
  for(x=0;x<n;x++) sample(x,y)
```

Flatten:

```js
for(i=n*n;i--;)sample(i%n,~~(i/n))
```

In dense point art, exact integer `y` is sometimes unnecessary:

```js
a(i%n,i/n)
```

If the formula naturally tolerates fractional `i/n`, omitting `floor`/`~~` saves characters and may create smoother geometry.

## 7. Assignment expressions as local cache — Stable

JavaScript assignment returns the assigned value. This is fundamental to contemporary tiny formulas.

```js
point((q=...)*cos(c=...),q*sin(c))
```

This lets `q` and `c` be created at first use and reused later without separate statements.

Good candidates:

- `k,e` latent coordinates
- `d` radius/distance
- `q` local radius/displacement
- `c` phase/angle
- `p` a nonlinear power/envelope

Do not create a one-letter variable if it is used only once; the assignment itself costs characters.

## 8. Default parameters as cheap bindings — Stable with evaluation-order awareness

A powerful pattern:

```js
a=(u,d=mag(k=...,e=...))=>point(...)
```

The default expression is evaluated when the argument is omitted, and assignments inside it can establish globals used by the body.

Benefits:

- avoids a separate statement for `d`
- groups the “latent coordinate” calculation with the mapping function
- allows successive defaults to depend on earlier parameters

Rules:

- keep dependency order obvious in the expanded version
- never reference a later parameter from an earlier default
- test compressed behavior; clever evaluation order is a common source of broken golf

## 9. Comma operator / side-effect sequencing — Stable

Where a single expression is allowed:

```js
(a(),b(),c())
```

executes left to right and yields the final value.

Useful in:

- first-frame initialization
- `for` initializer/increment clauses
- arguments whose values are ignored by the callee

Example shape:

```js
for(init(),i=N;i--;draw(i))
```

This can eliminate braces when the entire loop body fits in the update expression.

## 10. Put work in `for` clauses — Stable

A `for` loop has three expression slots. Community golfers exploit all of them:

```js
for(INIT;TEST;STEP)
```

If rendering can happen in `STEP`, the body can be empty.

```js
for(i=1e4;i--;point(...));
```

Whether that trailing semicolon is shorter than braces depends on the exact construction.

## 11. Function aliases — Stable, use a break-even check

If a long function is called often:

```js
m=translate
```

then use `m(...)`.

Calculate the break-even point. Aliasing `sin` used twice is usually not worth it; aliasing `translate` or `pointLight` used repeatedly may be.

## 12. Shorter numeric notation — Stable

- `10000` → `1e4`
- `40000` → `4e4`
- `0.3` → `.3`
- `0.0005` → `5e-4`

Sometimes a nearby integer is visually indistinguishable and shorter, e.g. 99 instead of 100. This is a **visual approximation**, not semantic minification; use only after comparison.

## 13. Powers and envelopes — Stable

Use `**` when shorter than repeated multiplication or `pow()`:

```js
d*d
```

is shorter than `d**2`, but:

```js
d**3
```

is shorter than `d*d*d`.

Compare literal lengths; code golf is local arithmetic.

## 14. Omit default/irrelevant arguments — Stable when API permits

Examples:

- omit z=0 from a 3D translate if the API defaults it correctly
- use `circle(x,y,d)` instead of `ellipse(x,y,d,d)`
- use `TAU` instead of `PI*2` where supported and shorter

Always validate against the p5 version you intend to run.

## 15. Reuse visual clamping — Contextual

p5 color channels clamp at the configured max. With default RGB range, a canvas width like `w=400` can behave as white in:

```js
stroke(w,70)
```

This is shorter than assigning another 255 literal and is common in tiny work. It is a deliberate visual equivalence, not clean API style.

## 16. Boolean arithmetic — Stable

Booleans coerce to 0/1 in arithmetic:

```js
5*(i%2<1)
```

Useful for alternating petals, mirror offsets, or gated deformations.

Often even shorter:

```js
i%2*3
```

when the desired states are 0 and 3.

## 17. Modulo as a topology operator — Stable

`i%n` is not only a golf trick. It creates segment/petal/strand identity cheaply.

Examples of roles:

- `i%2` bilateral alternation
- `i%5` fivefold lobe phase
- `i%16*13` discrete phase families
- `i%n` x-coordinate in a flattened grid

Prefer modulo when the repeated structure is genuinely part of the design.

## 18. Bitwise integer shortcuts — Contextual

For values in safe 32-bit range:

```js
~~x
```

can replace `floor(x)` for positive values.

`x|0` is similarly compact but signed-32-bit and truncation semantics may differ for negatives/large values.

Use only when the domain is controlled.

## 19. Ternaries — Stable

```js
condition?a:b
```

replaces small `if/else` blocks.

If the false case contributes zero, arithmetic or `&&` may be shorter:

```js
condition*a
```

or sometimes:

```js
condition&&f()
```

Compare characters and semantics.

## 20. Logical short-circuit initialization — Stable

Canonical:

```js
t||createCanvas(...)
```

or:

```js
t++||createCanvas(...)
```

`||` runs the right side when the left is falsy; `&&` does the inverse.

Do not layer several truthiness tricks until no human—including the generating agent—can reason about frame 0.

## 21. Destructuring multiple state updates — Stable but often not shortest

For coupled systems, a simultaneous-looking update can be expressed as:

```js
[x,y,z]=[X,Y,Z]
```

This is especially useful when the new values must all use the old state. It may be more correct than sequential assignment, even when not the absolute shortest.

A current @yuruyurau Lorenz-like work uses this pattern because update semantics matter.

## 22. Sequential update as an intentional dynamical choice — Stable

If exact simultaneous integration is not required, updating `x` then using new `x` in the `y` equation can both save characters and create a different attractor. Treat this as a new system, not a minified equivalent.

## 23. Background accumulation vs hard redraw — Stable

`background(0,9)` can create trails/feedback but costs an alpha argument and changes the visual system. `background(9)` gives crisp density surfaces. `clear()` is shorter than `background(0)` in some contexts but creates transparency, not black, unless the host page supplies the background.

Do not use `clear()` as an invisible external dependency unless the posting/rendering environment is controlled.

## 24. Chained p5 calls — Fragile/version-sensitive

Some p5 global calls return the p5 instance, allowing patterns such as:

```js
background(9).stroke(400,96)
```

This appears in contemporary work, but return-value chaining has varied across functions/versions and is less portable than:

```js
background(9);stroke(400,96)
```

Use only after testing in the target p5 runtime.

## 25. Renderer-warning hacks — Fragile

Koma Tebe documents a WEBGL trick where a `box()` detail argument causes p5 to skip strokes after a warning, saving `noStroke()`. Clever, historically authentic, but it depends on implementation behavior.

Rule for this skill: **fragile tricks are last-mile only**. Never build the core sketch around undocumented behavior.

## 26. Giant geometry as a background — Contextual/Fragile

In WEBGL, a very large box or plane can sometimes substitute for background-clearing while serving another purpose. This is renderer-specific and may alter depth behavior. Test.

## 27. Arrays / `.map()` for symmetric repeated calls — Contextual

If two or more calls differ only by a sign/value:

```js
[-1,1].map(i=>f(i))
```

may beat two full calls. It is often useful for lights or mirrored structural elements, less often for hot inner loops because callback overhead can hurt performance.

## 28. Remove syntax only after minifying semantics

Recommended order:

1. change the algorithmic representation
2. collapse setup/state
3. collapse loops
4. reuse latent variables
5. alias repeated long symbols
6. choose shorter numerals/primitives
7. remove whitespace
8. rename to one characters
9. apply fragile quirks only if needed

A generic minifier handles steps 7–8 well. It cannot decide that a nested grid should become one 40k loop or that a point cloud can replace explicit geometry.

## 29. Character accounting

For authentic posting, the hashtag is part of the budget.

Recommended suffix:

```js
//#つぶやきProcessing
```

Do not assume “17 visible characters” equals 17 X/Twitter characters: the Japanese code points are weighted differently. Run `scripts/check-length.mjs` on the complete one-line post.

## 30. Golf quality test

A shortening is good when it satisfies all four:

1. saves characters measurably
2. preserves or intentionally improves the visual
3. does not add disproportionate runtime risk
4. still leaves the causal structure recoverable from the expanded source

The goal is not unreadability. The goal is **maximum expressive leverage per character**.
