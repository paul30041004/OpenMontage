/* vox-explainer engine — data-driven, no LLM needed.
   All content comes from window.CONTENT. Only text/fields change per video. */
(function () {
  const FPS = (window.CONTENT.meta && window.CONTENT.meta.fps) || 24;
  const CFG = window.CONTENT.meta;
  const W = CFG.width || 1920, H = CFG.height || 1080;
  const C = CFG.palette;
  const SANS = CFG.sans, MONO = CFG.mono;
  const clamp = (v,a,b)=>Math.max(a,Math.min(b,v));
  const col = (c)=> (c==null ? C.navy : (C[c] || c));
  const step2 = t => Math.floor(t*FPS/2)*2/FPS;
  const at = (lt,t0)=> lt>=t0 ? 1 : 0;
  function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}

  function wrap(g,text,maxW,size,weight){
    g.font=`${weight} ${size}px ${SANS}`;
    const words=String(text).split(" "); const lines=[]; let cur="";
    for(const w of words){ const t=cur?cur+" "+w:w;
      if(g.measureText(t).width<=maxW){cur=t;continue;}
      if(cur){lines.push(cur);cur="";}
      if(g.measureText(w).width<=maxW){cur=w;continue;}
      let part=""; for(const ch of w){ if(g.measureText(part+ch).width>maxW){lines.push(part);part=ch;} else part+=ch; } cur=part;
    }
    if(cur)lines.push(cur); return lines;
  }
  function bigText(g,text,o){
    o=o||{};
    const x=o.x==null?W/2:o.x, y=o.y==null?H/2:o.y, maxW=o.maxW==null?W*0.86:o.maxW,
          size=o.size||150, weight=o.weight||900, color=col(o.color), align=o.align||"center",
          reveal=o.reveal==null?1:o.reveal;
    if(reveal<=0) return;
    const lines=wrap(g,text,maxW,size,weight); const lh=o.lineH||size*1.12;
    const startY=y-(lines.length-1)*lh/2;
    g.save(); g.font=`${weight} ${size}px ${SANS}`; g.textAlign=align; g.textBaseline="middle";
    lines.forEach((ln,i)=>{ g.fillStyle=color; g.fillText(ln,x,startY+i*lh); }); g.restore();
  }
  function roundRect(g,x,y,w,h,r){ r=Math.min(r,w/2,h/2); g.beginPath();
    g.moveTo(x+r,y); g.arcTo(x+w,y,x+w,y+h,r); g.arcTo(x+w,y+h,x,y+h,r); g.arcTo(x,y+h,x,y,r); g.arcTo(x,y,x+w,y,r); g.closePath(); }
  function chip(g,text,x,y,fill,color,size){ size=size||30;
    g.save(); g.font=`800 ${size}px ${SANS}`; g.textAlign="left"; g.textBaseline="middle";
    const w=g.measureText(text).width+48,h=size+30; roundRect(g,x,y,w,h,8); g.fillStyle=col(fill); g.fill();
    g.fillStyle=col(color); g.fillText(text,x+24,y+h/2); g.restore(); }
  function sourceChip(g,text){ if(!text)return;
    g.save(); g.font=`700 26px ${SANS}`; g.textAlign="left"; g.textBaseline="middle";
    const w=g.measureText(text).width+44,h=48,x=64,y=H-96; roundRect(g,x,y,w,h,8); g.fillStyle="rgba(20,33,61,0.9)"; g.fill();
    g.fillStyle=C.cream; g.fillText(text,x+22,y+h/2); g.restore(); }
  function corner(g){ if(!CFG.corner)return;
    g.save(); g.font=`800 24px ${SANS}`; g.textAlign="right"; g.textBaseline="middle";
    g.fillStyle="rgba(20,33,61,0.45)"; g.fillText(CFG.corner,W-64,78); g.restore(); }

  function tornRect(g,x,y,w,h,seed,amp){ const r=mulberry32(seed); const pts=[];
    const sx=Math.max(14,Math.round(w/46)), sy=Math.max(14,Math.round(h/22));
    for(let i=0;i<=w;i+=sx) pts.push([x+i,y+(r()-0.5)*amp]);
    for(let i=sy;i<=h;i+=sy) pts.push([x+w+(r()-0.5)*amp,y+i]);
    for(let i=w-sx;i>=0;i-=sx) pts.push([x+i,y+h+(r()-0.5)*amp]);
    for(let i=h-sy;i>0;i-=sy) pts.push([x+(r()-0.5)*amp,y+i]);
    g.beginPath(); g.moveTo(pts[0][0],pts[0][1]); for(let i=1;i<pts.length;i++)g.lineTo(pts[i][0],pts[i][1]); g.closePath(); }
  function tornCard(g,x,y,w,h,seed,fill,shadow){ g.save();
    if(shadow!==false){ g.shadowColor="rgba(20,33,61,0.30)"; g.shadowBlur=30; g.shadowOffsetY=16; }
    tornRect(g,x,y,w,h,seed,16); g.fillStyle=col(fill); g.fill(); g.restore();
    g.save(); tornRect(g,x,y,w,h,seed,16); g.lineWidth=2; g.strokeStyle="rgba(20,33,61,0.10)"; g.stroke(); g.restore(); }

  function bg(g,fr){
    g.fillStyle=C.paper; g.fillRect(0,0,W,H);
    g.save(); g.fillStyle="rgba(20,33,61,0.055)";
    for(let y=46;y<H;y+=56){ const off=((Math.floor(y/56))%2)*28; for(let x=46;x<W;x+=56){ g.beginPath(); g.arc(x+off,y,3.1,0,Math.PI*2); g.fill(); } } g.restore();
    const rg=mulberry32(777+fr); g.save();
    for(let i=0;i<7000;i++){ const x=rg()*W,y=rg()*H; g.fillStyle=rg()>0.5?"rgba(20,33,61,0.05)":"rgba(255,255,255,0.07)"; g.fillRect(x,y,2,2); } g.restore();
    const vg=g.createRadialGradient(W/2,H/2,H*0.28,W/2,H/2,H*0.86);
    vg.addColorStop(0,"rgba(0,0,0,0)"); vg.addColorStop(1,"rgba(20,33,61,0.30)"); g.fillStyle=vg; g.fillRect(0,0,W,H);
    g.save(); g.globalCompositeOperation="screen";
    g.fillStyle="rgba(184,49,42,0.16)"; g.fillRect(0,0,16,H);
    g.fillStyle="rgba(43,120,180,0.14)"; g.fillRect(W-16,0,16,H);
    g.fillStyle="rgba(242,194,48,0.10)"; g.fillRect(0,0,W,11); g.fillRect(0,H-11,W,11); g.restore();
    corner(g);
  }
  function glyph(g,x,y,s,color,icon){ g.save(); g.translate(x,y); g.strokeStyle=col(color); g.lineWidth=Math.max(2,s*0.12);
    if(icon==="key"){ const r=s*0.30;
      g.beginPath(); g.arc(-s*0.28,0,r,0,Math.PI*2); g.stroke();
      g.beginPath(); g.moveTo(-s*0.28+r*0.7,0); g.lineTo(s*0.4,0); g.stroke();
      g.beginPath(); g.moveTo(s*0.4,0); g.lineTo(s*0.4,s*0.24); g.stroke();
      g.beginPath(); g.moveTo(s*0.16,0); g.lineTo(s*0.16,s*0.20); g.stroke();
    } else { g.fillStyle=col(color); g.beginPath(); g.arc(0,0,s*0.28,0,Math.PI*2); g.fill(); }
    g.restore();
  }
  function counter(g,o){ const p=clamp(step2(o.lt)/(o.dur||1.8),0,1), e=1-Math.pow(1-p,3), v=(o.value||0)*e, dec=o.dec||0;
    const s=v.toLocaleString("en-US",{minimumFractionDigits:dec,maximumFractionDigits:dec});
    bigText(g,s+(o.suffix||""),{x:o.x,y:o.y,size:o.size||230,color:o.color||C.navy}); }

  const D = { cAt:[1.5,1.7], capSize:58, counterDur:1.9 };

  function renderShot(g,s,lt,dur){
    switch(s.type){
      case "kinetic": {
        const card=s.card ? (tornCard(g,W*0.08,H*0.30,W*0.84,H*0.22,21,s.cardFill||"cream"),true) : false;
        (s.lines||[]).forEach((ln,i)=>{
          const y=ln.y!=null?H*ln.y:(card?H*0.41+i*0.25:H*(0.34+i*0.213));
          bigText(g,ln.text,{y,size:ln.size||(i===0?150:158),color:ln.color||(i%2?"red":"navy"),reveal:at(lt, ln.at!=null?ln.at:i*0.55)});
        }); break; }
      case "counter": {
        if(s.title) bigText(g,s.title,{y:H*(s.titleY||0.22),size:s.titleSize||66,weight:800,color:s.titleColor||"navy",reveal:at(lt,0)});
        counter(g,{value:s.value,dur:s.counterDur||D.counterDur,lt:lt-(s.lead||0.15),y:H*(s.y||0.42),size:s.size||280,dec:s.dec||0,suffix:s.suffix||"",color:s.color||"navy"});
        const cat=s.captionsAt||D.cAt;
        (s.caption||[]).forEach((t,i)=> bigText(g,t,{y:H*((s.captionY||0.65)+i*0.07),size:s.capSize||D.capSize,weight:800,color:(s.captionColors||["navy","red"])[i]||"navy",reveal:at(lt,cat[i]!=null?cat[i]:cat[cat.length-1])}));
        sourceChip(g,s.source); break; }
      case "grid": {
        const cols=s.cols||12, rows=s.rows||4, tw=s.tw||140, th=s.th||120;
        const gx=(W-cols*tw)/2, gy=H*(s.gy||0.26), total=cols*rows, shown=Math.round(clamp(step2(lt)/(s.fillAt||1.6),0,1)*total);
        for(let k=0;k<total;k++){ const cx=gx+(k%cols)*tw+tw/2, cy=gy+Math.floor(k/cols)*th+th/2;
          glyph(g,cx,cy,s.iconSize||72, k<shown?(s.onColor||"red"):"rgba(20,33,61,0.13)", s.icon||"key"); }
        (s.caption||[]).forEach((t,i)=> bigText(g,t,{y:H*((s.captionY||0.80)+i*0.08),size:s.capSize||78,weight:900,color:(s.captionColors||["navy","red"])[i]||"navy",reveal:at(lt,(s.captionsAt||[1.2,1.4])[i])}));
        sourceChip(g,s.source); break; }
      case "code": {
        tornCard(g,W*0.14,H*(s.y||0.28),W*0.72,H*(s.h||0.40),33,s.fill||"#0f1730",true);
        g.save(); g.font=`700 44px ${MONO}`; g.textAlign="left"; g.textBaseline="middle";
        (s.code||[]).forEach((L,k)=>{ g.fillStyle=col(L.color); if(L.text) g.fillText(L.text,W*0.18,H*((s.codeY||0.37)+k*0.065)); }); g.restore();
        if(s.marker){ const m=s.marker,x=W*(m.x||0.585),y=H*(m.y||0.44),r=m.r||150;
          g.save(); g.strokeStyle=col(m.color||"red"); g.lineWidth=6; g.setLineDash([14,11]);
          g.beginPath(); g.arc(x,y,r,0,Math.PI*2*clamp(step2(lt)/(m.at||1.0),0,1)); g.stroke(); g.restore(); }
        if(s.caption) bigText(g,s.caption,{y:H*(s.captionY||0.80),size:s.capSize||76,weight:900,color:s.captionColor||"red",reveal:at(lt,s.captionAt||1.1)});
        sourceChip(g,s.source); break; }
      case "beforeafter": {
        bigText(g,s.title,{y:H*0.20,size:s.titleSize||112,color:s.titleColor||"navy",reveal:at(lt,0)});
        tornCard(g,W*0.14,H*0.34,W*0.30,H*0.28,5,"cream"); tornCard(g,W*0.56,H*0.34,W*0.30,H*0.28,6,"cream");
        bigText(g,s.left,{x:W*0.29,y:H*0.48,size:92,color:s.leftColor||"navy",reveal:at(lt,0.2)});
        bigText(g,s.right,{x:W*0.71,y:H*0.48,size:92,color:s.rightColor||"red",reveal:at(lt,0.6)});
        g.save(); g.strokeStyle="rgba(20,33,61,0.5)"; g.lineWidth=5;
        g.beginPath(); g.moveTo(W*0.47,H*0.48); g.lineTo(W*0.53,H*0.48); g.stroke();
        g.beginPath(); g.moveTo(W*0.53,H*0.48); g.lineTo(W*0.51,H*0.46); g.moveTo(W*0.53,H*0.48); g.lineTo(W*0.51,H*0.50); g.stroke(); g.restore();
        bigText(g,s.caption,{y:H*0.72,size:72,weight:900,color:"navy",reveal:at(lt,s.captionAt||1.2)});
        if(s.sub) bigText(g,s.sub,{y:H*0.80,size:94,weight:900,color:"red",reveal:at(lt,(s.captionAt||1.2)+0.3)});
        sourceChip(g,s.source); break; }
      case "cards": {
        bigText(g,s.title,{y:H*0.18,size:s.titleSize||110,color:"navy",reveal:at(lt,0)});
        tornCard(g,W*0.16,H*0.32,W*0.30,H*0.34,71,s.left.fill||"cream");
        tornCard(g,W*0.54,H*0.32,W*0.30,H*0.34,72,s.right.fill||"navy");
        (s.left.lines||[]).forEach((t,i)=> bigText(g,t,{x:W*0.31,y:H*(0.44+i*0.09),size:60,weight:800,color:s.left.color||"navy",reveal:at(lt,(s.left.at||[0.2,0.35])[i])}));
        (s.right.lines||[]).forEach((t,i)=> bigText(g,t,{x:W*0.69,y:H*(0.44+i*0.09),size:60,weight:800,color:s.right.color||"yellow",reveal:at(lt,(s.right.at||[0.7,0.85])[i])}));
        g.save(); g.strokeStyle=col("red"); g.lineWidth=6;
        g.beginPath(); g.moveTo(W*0.47,H*0.49); g.lineTo(W*0.53,H*0.49); g.stroke();
        g.beginPath(); g.moveTo(W*0.53,H*0.49); g.lineTo(W*0.505,H*0.465); g.moveTo(W*0.53,H*0.49); g.lineTo(W*0.505,H*0.515); g.stroke(); g.restore();
        if(s.caption) bigText(g,s.caption,{y:H*0.80,size:78,weight:900,color:"red",reveal:at(lt,s.captionAt||1.1)});
        break; }
      case "headline": {
        tornCard(g,W*0.12,H*(s.y||0.26),W*0.76,H*(s.h||0.34),91,s.cardFill||"cream");
        bigText(g,s.brand,{y:H*0.36,size:s.brandSize||118,color:"navy",reveal:at(lt,0)});
        bigText(g,s.sub,{y:H*0.47,size:78,weight:900,color:"red",reveal:at(lt,0.5)});
        if(s.chip) chip(g,s.chip,W*0.12+40,H*0.62,C.navy,C.cream,34);
        if(s.bottom) bigText(g,s.bottom,{y:H*(s.bottomY||0.79),size:s.bottomSize||64,weight:800,color:"navy",reveal:at(lt,s.bottomAt||1.3)});
        sourceChip(g,s.source); break; }
      case "badge": {
        bigText(g,s.title,{y:H*0.18,size:64,weight:800,color:"navy",reveal:at(lt,0)});
        counter(g,{value:s.value,dur:s.counterDur||2.1,lt:lt-0.2,y:H*0.44,size:s.size||210,dec:s.dec||0,suffix:s.suffix||"",color:s.color||"red"});
        if(s.sub) bigText(g,s.sub,{y:H*0.60,size:62,weight:800,color:"navy",reveal:at(lt,1.8)});
        if(s.badge && at(lt,s.badge.at||2.0)){ tornCard(g,W*0.66,H*0.66,W*0.22,H*0.16,42,s.badge.fill||"yellow");
          bigText(g,s.badge.value,{x:W*0.77,y:H*0.73,size:92,color:"navy"});
          bigText(g,s.badge.label,{x:W*0.77,y:H*0.85,size:44,weight:800,color:"navy"}); }
        sourceChip(g,s.source); break; }
      default: bigText(g,s.text||"",{reveal:at(lt,0)});
    }
  }

  // duration source: timing.json (with narration) overrides content dur
  const DURS = (window.TIMING && window.TIMING.shot) ? window.TIMING.shot : (window.CONTENT.shots.map(s=>s.dur||3));
  const cum=[]; { let a=0; for(const d of DURS){ cum.push(a); a+=d; } }
  const TOTAL = cum[cum.length-1] + DURS[DURS.length-1];

  function seek(t){
    const ctx = window.__ctx; ctx.setTransform(1,0,0,1,0,0); ctx.clearRect(0,0,W,H);
    let idx = DURS.length-1;
    for(let i=0;i<DURS.length;i++){ if(t < cum[i]+DURS[i]){ idx=i; break; } }
    const lt = step2(t - cum[idx]);
    bg(ctx, Math.round(t*FPS));
    renderShot(ctx, window.CONTENT.shots[idx], lt, DURS[idx]);
  }
  window.FPS=FPS; window.TOTAL=TOTAL; window.SHOTS=DURS.map((d,i)=>({index:i,dur:d})); window.seek=seek;
})();
