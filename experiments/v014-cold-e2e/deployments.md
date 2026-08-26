# Exact deployment finalists

## Recurrence — R3 (artistic rank 2 after R12 fallback)

```js
t=0,d=5e-4,draw=_=>{t++||createCanvas(w=400,w);stroke(w,48);background(9);for(x=y=z=9,i=3e4;i--;point((r=100+x+y*sin(x*y/48-t/8+i%2)/3)*cos(c=z/55+t/61+i%2/2)+200,r*sin(c)+y/2+200))[x,y,z]=[x+10*(y-x)*d,y+(x*(26-z)-y)*d,z+(x*y-2.4*z)*d]}//#つぶやきProcessing
```

- code chars: 237
- estimated X-weight total: 258
- raw post code points: 254
- 150-frame runtime: pass
- bad/non-finite point calls: 0
- compression survival: pass

Defining relationships retained: recurrent state, two residue phases, `x*y` state-cross deformation, transformed polar knot projection.

## Dense sheet — S5 (artistic rank 1)

```js
t=0,draw=_=>{t++||createCanvas(w=400,w);stroke(w,38);background(9);for(i=3e4;i--;abs(u)>1.5&&point(200+s*(23+abs(u)*4.7+7*sin(.6*v-t/9)*cos(.3*u+t/14)),200+v*4.8+u*sin(mag(u,v)/1.8-t/10)+3*cos(.7*v+u/2)))u=i%180/9-10,v=i/1800-8.3,s=u<0?-1:1}//#つぶやきProcessing
```

- code chars: 241
- estimated X-weight total: 262
- raw post code points: 258
- 150-frame runtime: pass
- bad/non-finite point calls: 0
- compression survival: pass

Defining relationships retained: flattened 2D sampling, central seam, cross-coupled fold field, split membrane projection.
