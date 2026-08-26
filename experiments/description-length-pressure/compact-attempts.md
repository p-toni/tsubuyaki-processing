# Exact Compact Attempts

These one-line attempts are the deployment artifacts used for the selected candidates in the description-length-pressure experiment.

They are evidence artifacts, not production templates.

## F12 — repeated family

246 code chars / ~267 X-weighted with suffix.

```js
t=0,draw=_=>{t++||createCanvas(w=400,w).stroke(w,55);background(9);for(i=3e4;i--;point(200+80*cos(a)+k*p,200+58*sin(a)+e*p))j=i%9,a=j*PI*2/9+sin(t/33+j)/12,u=i/9,k=14*sin(u/4)*sin(u/13+j),e=18*cos(u/7+j)*cos(u/17),p=1+.5*sin(hypot(k,e)/5-t/13+j)}
```

Survival: **pass — moderate**. Multi-body family survives; some expanded seed-like internal morphology becomes bead-like.

## S4 — dense sheet

212 code chars / ~233 X-weighted with suffix.

```js
t=0,draw=_=>{t++||createCanvas(w=400,w).stroke(w,55);background(9);for(i=3e4;i--;point(200+s*(28+a*4+7*sin(v/3-t/5)),200+v*5+u*sin(d/2-t/7)+u*cos(v/3)/2))u=i%180/9-10,v=i/1440-10,s=u<0?-1:1,a=abs(u),d=hypot(u,v)}
```

Survival: **pass — strong**.

## L9 — intentional filament

235 code chars / ~256 X-weighted with suffix.

```js
t=0,draw=_=>{t++||createCanvas(w=400,w).stroke(w,73);background(9);for(i=18e3;i--;u=i/573-15.7,j=i%4,q=sin(7*u-.096*t+j*.61),point(200+38*sin(1.73*u+.08*t)+.49*u+8*sin(3.1*u-.05*t+j),200+5.1*u+16*q*sin(u+j)+5*sin(1.6*u+1.7*j+.03*t)));}
```

Survival: **pass — strong**.

## R6 — recurrence shortlist-preflight winner

257 code chars / ~278 X-weighted with suffix.

```js
t=0,d=6e-4,draw=_=>{t++||createCanvas(w=400,w).stroke(w,48);background(9);for(x=y=z=9,i=3e4;i--;point(200+(r=75+3*x*(e=sin(t/80-x*x/99+i%2)+1))*cos(c=z/48+t/150+i%2/2)+y/3,200-(r+45*cos(c/2))*sin(c)+y/6))[x,y,z]=[x+9*(y-x)*d,y+(x*(27-z)-y)*d,z+(x*y-2*z)*d]}
```

Survival: **pass**. Expanded detail is reduced, but the recurrent transformed living-knot identity remains.

## R12 — late-only expanded winner

229 code chars / ~250 X-weighted with suffix.

```js
t=0,d=6e-4,draw=_=>{t++||createCanvas(w=400,w).stroke(w,48);background(9);for(x=y=z=9,i=3e4;i--;point(200+(r=115+x)*cos(c=z/52+t/145+i%3/2)+y/3,200-(r+45*cos(c/2))*sin(c)+y/4))[x,y,z]=[x+9*(y-x)*d,y+(x*(28-z)-y)*d,z+(x*y-2*z)*d]}
```

Survival: **fail**.

The code easily fits the medium, but the cross-wave / extra harmonic relationships that made R12 the expanded visual winner were removed. The result becomes a thin recurrent glyph rather than the selected living-knot phenotype.

## Runtime check

All five snippets parsed successfully under Node `new Function(...)`.

Each was then run for five frames under a minimal p5-compatible stub. All generated finite point coordinates with no runtime exception.
