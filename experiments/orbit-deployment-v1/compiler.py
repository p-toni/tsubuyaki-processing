from __future__ import annotations
import math

def num(x,d=2):
    s=f'{x:.{d}f}'.rstrip('0').rstrip('.')
    if s.startswith('0.'): s=s[1:]
    if s.startswith('-0.'): s='-'+s[2:]
    return s

def compile_orbit(g):
    R=round(g['radius']); A=max(24,min(48,round(g['alpha']*.8)))
    L=num(g['lobe'],2); P=num(g['ripple'],2); AS=num(g['asym'],2); D=num(g['dent'],2); K=num(g['dent_k'],1)
    PH=num(g['phase'],1); AP=num(g['asym_phase'],1); DP=num(g['dent_phase'],1); W=num(g['warp'],2); SY=num(g['sy'],2)
    T=round(g['time']); T2=round(g['time2']); T3=round(g['time3']); S=max(3,round(g['side']))
    return f't=0,draw=_=>{{t++||createCanvas(w=400,w);background(9);stroke(w,{A});for(i=2e4;i--;point(200+(r={R}*(1+{L}*sin({g["f1"]}*q+t/{T})+{P}*sin({g["f2"]}*q-t/{T2}+{PH})+{AS}*cos(q-{AP})-{D}/exp({K}-{K}*cos(q-{DP})))+i%2*{S})*cos(a=q+{W}*sin({g["f3"]}*q+t/{T3})),200+{SY}*r*sin(a)))q=i/300}}//#つぶやきProcessing'

def compact_period_points(g,t,n=3000):
    # Semantic period corresponding exactly to the compiled formula, using the same quantization.
    R=round(g['radius']); L=float(num(g['lobe'],2)); P=float(num(g['ripple'],2)); AS=float(num(g['asym'],2)); D=float(num(g['dent'],2)); K=float(num(g['dent_k'],1))
    PH=float(num(g['phase'],1)); AP=float(num(g['asym_phase'],1)); DP=float(num(g['dent_phase'],1)); W=float(num(g['warp'],2)); SY=float(num(g['sy'],2))
    T=round(g['time']); T2=round(g['time2']); T3=round(g['time3'])
    pts=[]
    for j in range(n+1):
        q=2*math.pi*j/n
        r=R*(1+L*math.sin(g['f1']*q+t/T)+P*math.sin(g['f2']*q-t/T2+PH)+AS*math.cos(q-AP)-D/math.exp(K-K*math.cos(q-DP)))
        a=q+W*math.sin(g['f3']*q+t/T3)
        pts.append((200+r*math.cos(a),200+SY*r*math.sin(a)))
    return pts

def compact_draw_points(g,t):
    R=round(g['radius']); L=float(num(g['lobe'],2)); P=float(num(g['ripple'],2)); AS=float(num(g['asym'],2)); D=float(num(g['dent'],2)); K=float(num(g['dent_k'],1))
    PH=float(num(g['phase'],1)); AP=float(num(g['asym_phase'],1)); DP=float(num(g['dent_phase'],1)); W=float(num(g['warp'],2)); SY=float(num(g['sy'],2));S=max(3,round(g['side']))
    T=round(g['time']);T2=round(g['time2']);T3=round(g['time3'])
    pts=[]
    for i in range(19999,-1,-1):
        q=i/300
        r=R*(1+L*math.sin(g['f1']*q+t/T)+P*math.sin(g['f2']*q-t/T2+PH)+AS*math.cos(q-AP)-D/math.exp(K-K*math.cos(q-DP)))+(i%2)*S
        a=q+W*math.sin(g['f3']*q+t/T3)
        pts.append((200+r*math.cos(a),200+SY*r*math.sin(a)))
    return pts

def weighted_length(text):
    one=((0,4351),(8192,8205),(8208,8223),(8242,8247))
    return sum(1 if any(a<=ord(ch)<=b for a,b in one) else 2 for ch in text)
