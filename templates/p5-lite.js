// Minimal offline p5-compatible runtime for Tsubuyaki Processing harnesses.
// Covers the global-mode primitives used by this skill; use ?full=1 in harness.html
// when a sketch needs full p5.js and network access is available.
(()=>{
  const g=globalThis;
  g.PI=Math.PI;g.TAU=g.TWO_PI=Math.PI*2;
  for(const n of ['sin','cos','tan','abs','sqrt','pow','floor','ceil','round','min','max'])g[n]=Math[n];
  g.mag=(...a)=>Math.hypot(...a);
  g.random=(a=1,b)=>b==null?Math.random()*a:a+Math.random()*(b-a);
  g.constrain=(v,a,b)=>Math.max(a,Math.min(b,v));
  let c,x,run=true,strokeStyle='rgba(255,255,255,1)',fillStyle='rgba(255,255,255,1)',useStroke=true,useFill=true,weight=1;
  const css=(args)=>{
    let [r=255,g=r,b=g,a=255]=args;
    if(args.length===2){a=g;g=b=r}
    if(args.length===1)g=b=r;
    return `rgba(${r},${g},${b},${a/255})`;
  };
  g.createCanvas=(w,h)=>{c=document.createElement('canvas');c.width=g.width=w;c.height=g.height=h;document.body.appendChild(c);x=c.getContext('2d');x.imageSmoothingEnabled=false;return {canvas:c,stroke:(...a)=>(g.stroke(...a),g)}};
  g.pixelDensity=()=>1;
  g.background=(...a)=>{x.save();x.globalCompositeOperation='source-over';x.fillStyle=css(a);x.fillRect(0,0,c.width,c.height);x.restore()};
  g.stroke=(...a)=>(strokeStyle=css(a),useStroke=true,g);
  g.noStroke=()=>useStroke=false;
  g.fill=(...a)=>(fillStyle=css(a),useFill=true,g);
  g.noFill=()=>useFill=false;
  g.strokeWeight=n=>weight=n;
  g.point=(a,b)=>{if(!useStroke)return;x.fillStyle=strokeStyle;x.fillRect(a-weight/2,b-weight/2,weight,weight)};
  g.circle=(a,b,d)=>{x.beginPath();x.arc(a,b,d/2,0,g.TWO_PI);if(useFill){x.fillStyle=fillStyle;x.fill()}if(useStroke){x.strokeStyle=strokeStyle;x.lineWidth=weight;x.stroke()}};
  g.line=(a,b,c1,d)=>{if(!useStroke)return;x.beginPath();x.moveTo(a,b);x.lineTo(c1,d);x.strokeStyle=strokeStyle;x.lineWidth=weight;x.stroke()};
  g.noLoop=()=>run=false;
  g.frameCount=0;
  const boot=()=>{
    try{if(typeof g.setup==='function')g.setup()}catch(e){g.__TSUBUYAKI_ERROR__=String(e.stack||e);throw e}
    const tick=()=>{if(!run)return;try{g.frameCount++;if(typeof g.draw==='function')g.draw()}catch(e){g.__TSUBUYAKI_ERROR__=String(e.stack||e);run=false;return}requestAnimationFrame(tick)};
    requestAnimationFrame(tick);
  };
  addEventListener('load',boot,{once:true});
})();