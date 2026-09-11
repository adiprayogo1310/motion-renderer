#!/usr/bin/env python3
"""build.mjs counterpart: baca specs/<slug>.json + timing VO (silencedetect) ->
generate video/index.html dari template per visual-type.

Usage: python3 scripts/build.py <slug>
Output: video/index.html (siap dirender render.mjs)
"""
import json, re, subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def vo_segments(path):
    """silencedetect -> daftar segmen suara [a,b]."""
    out = subprocess.run(
        ["ffmpeg", "-i", path, "-af", "silencedetect=noise=-40dB:d=0.12", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", out)]
    dur = float(re.findall(r"time=(\d+:\d+:[\d.]+)", out)[-1].split(":")[-1]) if "time=" in out else 0
    if not ends or ends[-1] < starts[-1]:
        ends.append(dur)
    segs, prev = [], 0.0
    for s, e in zip(starts, ends):
        if s - prev > 0.1:
            segs.append([round(prev, 2), round(s, 2)])
        prev = e
    if dur - prev > 0.1:
        segs.append([round(prev, 2), round(dur, 2)])
    return segs, round(dur, 2)

def main():
    slug = sys.argv[1]
    spec = json.load(open(f"{ROOT}/specs/{slug}.json"))
    vo_path = os.path.join(ROOT, spec["vo"])
    if not os.path.exists(vo_path):
        sys.exit(f"VO tidak ada: {vo_path} — push/paste dulu audionya.")
    segs, dur = vo_segments(vo_path)
    scenes = spec["scenes"]
    if len(segs) != len(scenes):
        print(f"WARN: {len(segs)} segmen suara vs {len(scenes)} scene di spec — "
              f"pausing antara segmen menyatu/menipis. Mapping berurutan tetap dipakai.")
    # mapping: scene i -> segmen i (berurutan); kelebihan segmen digabung ke scene terakhir
    sc_bounds = []
    # gabung segmen yang lebih banyak dari scene: segmen ekstra menempel ke scene terakhir yang cocok
    n_s, n_g = len(scenes), len(segs)
    if n_g < n_s:
        sys.exit(f"ERROR: segmen suara ({n_g}) lebih sedikit dari scene ({n_s}) — pecah caption di spec.")
    # distribusi proporsional: scene i dapat gap_count[i] segmen
    base = n_g // n_s
    extra = n_g % n_s
    counts = [base + (1 if i < extra else 0) for i in range(n_s)]
    gi = 0
    for i, c in enumerate(counts):
        a = segs[gi][0]
        b = segs[gi + c - 1][1]
        sc_bounds.append([a, b])
        gi += c

    T = spec["theme"]
    brand = spec["brand"]
    cap_lines = json.dumps([s["caption"] for s in scenes], ensure_ascii=False)
    scenes_js = json.dumps(scenes, ensure_ascii=False)
    bounds_js = json.dumps(sc_bounds)

    html = TEMPLATE
    kicker = spec.get("kicker", "PALUNG JAWA")
    html = html.replace("__KICKER__", kicker)
    html = html.replace("__TITLE__", f"{brand['name']}{brand['accent']} — {spec.get('kicker','')}")
    html = html.replace("__BG__", T["bg"])
    html = html.replace("__LINE__", T["line"])
    html = html.replace("__CYAN__", T["cyan"])
    html = html.replace("__RED__", T["red"])
    html = html.replace("__ORANGE__", T["orange"])
    html = html.replace("__FG__", T["fg"])
    html = html.replace("__DIM__", T["dim"])
    html = html.replace("__NAME__", brand["name"])
    html = html.replace("__ACCENT__", brand["accent"])
    html = html.replace("__DOT__", brand["dot"])
    html = html.replace("__THEME__", json.dumps(T))
    html = html.replace("__BRAND__", json.dumps(brand))
    html = html.replace("__SCENES__", scenes_js)
    html = html.replace("__BOUNDS__", bounds_js)
    html = html.replace("__CAPS__", cap_lines)
    html = html.replace("__DUR__", str(dur))
    out = f"{ROOT}/video/index.html"
    open(out, "w").write(html)
    print(f"built {out}: {len(scenes)} scenes, DUR={dur}s dari {spec['vo']}")

TEMPLATE = r"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>__TITLE__</title>
<style>
  :root{--bg:__BG__;--line:__LINE__;--cyan:__CYAN__;--red:__RED__;--orange:__ORANGE__;--fg:__FG__;--dim:__DIM__}
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{width:100%;height:100%;background:var(--bg);overflow:hidden;
    font-family:'Liberation Sans','DejaVu Sans',Arial,sans-serif}
  #stage{position:relative;width:720px;height:1280px;background:var(--bg);overflow:hidden}
  .lyr{position:absolute;inset:0}
  .tag{position:absolute;top:150px;left:40px;color:var(--dim);font-size:15px;letter-spacing:.24em}
  .tag b{color:var(--cyan);font-weight:400}
  .cap{position:absolute;left:0;width:100%;text-align:center;font-size:30px;font-weight:700;color:var(--fg);line-height:1.45}
  .cap .cy{color:var(--cyan)}
  .tt{position:absolute;padding:10px 16px;border:1.5px solid #ffffffcc;border-radius:10px;
      font-size:20px;font-weight:700;color:var(--fg);background:rgba(13,21,38,.85);white-space:nowrap}
  .tt .cy{color:var(--cyan)}
  .star{position:absolute;background:#22304d;border-radius:50%}
</style>
</head>
<body>
<div id="stage">
  <div id="stars"></div>
  <div id="depthline" style="position:absolute;right:56px;top:340px;width:3px;height:698px;background:var(--line)"></div>
  <div id="altlabels"></div>
  <div class="tag">[ FAKTA BUMI ] <b>__KICKER__</b></div>
  <svg width="720" height="1280" viewBox="0 0 720 1280" style="position:absolute;left:0;top:0" id="scene"></svg>
  <div id="tooltip" class="tt hidden"></div>
  <div id="caption" class="cap" style="bottom:210px"></div>
  <div id="logo" style="position:absolute;top:36px;left:36px;display:flex;align-items:center;gap:10px">
    <div style="width:40px;height:40px;border-radius:50%;background:__DOT__;display:flex;align-items:center;justify-content:center;font-weight:900;color:#fff;font-size:16px">G</div>
    <div style="font-weight:900;color:#fff;font-size:19px">__NAME__<span style="color:var(--cyan)">__ACCENT__</span></div>
  </div>
</div>
<script>
const SPEC=__SCENES__;
const BOUNDS=__BOUNDS__;
const CAPS=__CAPS__;
const DUR=__DUR__;
const W=720,H=1280;
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const lerp=(a,b,t)=>a+(b-a)*t;
const ease=t=>t<0?0:t>1?1:t*t*(3-2*t);
const pop=t=>t<0?0:t>1?1:1-Math.pow(1-t,3);
const seg=(t,a,b)=>clamp((t-a)/(b-a),0,1);
const $=id=>document.getElementById(id);
const stage=$('stage');
const SC=BOUNDS.flatMap((b,i)=>i===0?[b[0]]:[b[0]]).concat([DUR]);
const SCEND=BOUNDS.map(b=>b[1]);
function sceneIndex(t){for(let i=0;i<BOUNDS.length;i++){if(t>=BOUNDS[i][0]&&t<BOUNDS[i][1])return i;}return BOUNDS.length-1;}
const fadeRange=(t,a,b)=>Math.min(seg(t,a,a+0.4),1-seg(t,b-0.3,b));

stage.insertAdjacentHTML('beforeend',`
  <div id="depthline" style="position:absolute;right:56px;top:340px;width:3px;height:698px;background:var(--line)"></div>
  <div id="altlabels">
    <div class="alt" style="top:330px">0 <b>m</b></div>
    <div class="alt" style="top:510px">−2.000 <b>m</b></div>
    <div class="alt" style="top:700px">−4.000 <b>m</b></div>
    <div class="alt" style="top:890px">−6.000 <b>m</b></div>
    <div class="alt red" style="top:1035px">−7.192 <b>m</b></div>
  </div>
  <svg width="720" height="1280" viewBox="0 0 720 1280" style="position:absolute;left:0;top:0" id="scene">
    <defs><filter id="glowC" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
    <g id="sea" filter="url(#glowC)"><path id="seapath" d="" stroke="var(--cyan)" stroke-width="2.5" fill="none"/></g>
    <g id="boat" filter="url(#glowC)">
      <path d="M310 330 L410 330 L385 302 L335 302 Z" stroke="var(--cyan)" stroke-width="2.5" fill="rgba(77,216,255,.06)"/>
      <line x1="360" y1="302" x2="360" y2="240" stroke="var(--cyan)" stroke-width="2.5"/>
      <path d="M364 246 L400 298 L364 298 Z" stroke="var(--cyan)" stroke-width="2" fill="rgba(77,216,255,.05)"/>
      <path d="M356 250 L330 298 L356 298 Z" stroke="var(--orange)" stroke-width="2" fill="rgba(255,159,67,.07)"/></g>
    <g id="plumb" filter="url(#glowC)">
      <line x1="360" y1="340" x2="360" y2="900" stroke="var(--cyan)" stroke-width="2" stroke-dasharray="6 8" opacity=".7"/>
      <path d="M348 890 L360 912 L372 890 Z" fill="var(--cyan)"/></g>
    <g id="floor" filter="url(#glowC)">
      <path d="M40 900 L200 900 L300 1035 L420 1035 L520 900 L680 900" stroke="var(--red)" stroke-width="3" fill="none"/>
      <text id="floorLbl" x="360" y="1090" text-anchor="middle" font-size="22" fill="var(--red)" font-weight="800" opacity="0">PALUNG JAWA −7.192 m</text></g>
    <g id="semeru" filter="url(#glowC)">
      <path d="M110 340 L200 92 L290 340" stroke="var(--orange)" stroke-width="2.5" fill="rgba(255,159,67,.05)"/>
      <text x="200" y="70" text-anchor="middle" font-size="17" fill="var(--orange)" font-weight="700">SEMERU 3.676 m</text></g>
    <g id="plates" filter="url(#glowC)">
      <path d="M60 520 L660 505 L660 585 L60 600 Z" stroke="var(--cyan)" stroke-width="2.5" fill="rgba(77,216,255,.05)"/>
      <text x="90" y="480" font-size="17" fill="var(--cyan)" font-weight="700">LEMPENG EURASIA</text>
      <path d="M60 760 L480 730 L600 800 L470 1000 L60 900 Z" stroke="var(--orange)" stroke-width="2.5" fill="rgba(255,159,67,.05)"/>
      <text x="80" y="1058" font-size="17" fill="var(--orange)" font-weight="700">INDO-AUSTRALIA</text>
      <path d="M280 745 L360 800 L300 900" stroke="var(--red)" stroke-width="2.5" fill="none" stroke-dasharray="8 7"/>
      <g id="arrL"><rect x="80" y="1120" width="110" height="8" fill="var(--red)"/><path d="M190 1112 L220 1124 L190 1136 Z" fill="var(--red)"/></g>
      <g id="arrR"><rect x="530" y="1120" width="110" height="8" fill="var(--red)"/><path d="M530 1112 L500 1124 L530 1136 Z" fill="var(--red)"/></g></g>
    <g id="ruler3" filter="url(#glowC)">
      <rect x="70" y="560" width="580" height="24" stroke="var(--cyan)" stroke-width="2.5" fill="rgba(77,216,255,.05)"/>
      <rect id="rfill" x="73" y="563" width="0" height="18" fill="rgba(77,216,255,.35)"/>
      <path id="rmark" d="M73 528 L62 506 L84 506 Z" fill="var(--orange)"/>
      <text x="70" y="620" font-size="16" fill="var(--dim)">0 TH</text>
      <text x="650" y="620" text-anchor="end" font-size="16" fill="var(--dim)">100 TH</text>
      <text id="yr3" x="360" y="740" text-anchor="middle" font-size="58" font-weight="900" fill="var(--fg)">0 TAHUN</text>
      <text id="mtr3" x="360" y="820" text-anchor="middle" font-size="40" font-weight="800" fill="var(--cyan)">= 0 METER</text>
      <g id="nail">
        <rect x="330" y="920" width="14" height="70" rx="6" stroke="var(--cyan)" stroke-width="2" fill="rgba(77,216,255,.08)"/>
        <rect x="322" y="912" width="30" height="14" rx="4" stroke="var(--cyan)" stroke-width="2" fill="none"/>
        <text x="360" y="1055" text-anchor="middle" font-size="16" fill="var(--dim)">kuku tumbuh 6,5 cm/th</text></g></g>
    <g id="spring" filter="url(#glowC)">
      <rect x="90" y="560" width="190" height="110" stroke="var(--cyan)" stroke-width="2.5" fill="rgba(77,216,255,.05)"/>
      <rect x="440" y="560" width="190" height="110" stroke="var(--orange)" stroke-width="2.5" fill="rgba(255,159,67,.05)"/>
      <path id="zig" stroke="var(--red)" stroke-width="3" fill="none"/>
      <text x="185" y="625" text-anchor="middle" font-size="16" fill="var(--cyan)" font-weight="700">TEKANAN</text>
      <text x="535" y="625" text-anchor="middle" font-size="16" fill="var(--orange)" font-weight="700">TUMPUKAN</text>
      <g id="waves4"></g></g>
    <g id="eq" filter="url(#glowC)">
      <rect x="120" y="420" width="480" height="130" rx="14" stroke="var(--cyan)" stroke-width="2.5" fill="rgba(77,216,255,.06)"/>
      <text id="eqMain" x="360" y="478" text-anchor="middle" font-size="30" font-weight="900" fill="var(--fg)"></text>
      <text id="eqLine2" x="360" y="720" text-anchor="middle" font-size="22" fill="var(--fg)" opacity="0">Bukan <tspan fill="var(--red)" font-weight="900">KEJADIAN</tspan> yang datang tiba-tiba</text></g>
    <g id="outro" filter="url(#glowC)">
      <text id="o1" x="360" y="480" text-anchor="middle" font-size="52" font-weight="900" fill="var(--fg)" opacity="0">BUMI TIDAK <tspan fill="var(--cyan)">DIAM</tspan></text>
      <path id="fault6" d="M120 640 L340 628 L360 636 L600 620" stroke="var(--red)" stroke-width="3" fill="none" opacity="0"/></g>`);
$('stars').innerHTML=Array.from({length:42},(_,i)=>
  `<div class="star" style="left:${(i*173)%700}px;top:${(i*257)%1240}px;width:${2+(i%3)}px;height:${2+(i%3)}px;opacity:${.3+(i%5)*.12}"></div>`).join('');

function setWaves(t,base){let d='M40 '+base;for(let x=40;x<680;x+=80)d+=` Q${x+40} ${base-8+Math.sin(t*2+x)*3} ${x+80} ${base}`;return d;}
function springPath(cx1,cx2,y,comp){const n=8,zw=(cx2-cx1)/n;let d=`M${cx1} ${y}`;
  for(let i=0;i<n;i++)d+=` L${cx1+zw*(i+.5)} ${y+(i%2?20:-20)}`;return d+` L${cx2} ${y}`;}
function tooltip(t,showA,hideA,html,x,y){
  const el=$('tooltip');const p=pop(seg(t,showA,showA+0.3));
  const q=(t>hideA)?1-pop(seg(t,hideA,hideA+0.3)):p;
  if(p<=0||hideA-showA<0.05){el.classList.add('hidden');return;}
  el.classList.remove('hidden');el.innerHTML=html;
  el.style.left=x+'px';el.style.top=y+'px';
  el.style.opacity=q;el.style.transform=`scale(${lerp(.7,1,p)})`;}
function showCap(t,i){
  const c=$('caption');const p=seg(t,BOUNDS[i][0],Math.min(BOUNDS[i][0]+0.55,BOUNDS[i][1]-0.15));
  const parts=CAPS[i].split('|');const words=parts.map(s=>s.split(' '));
  let n=0,total=words.flat().length;let html='';
  for(let li=0;li<parts.length;li++){
    const line=words[li].map(w=>{n++;const wp=clamp((p*total-n+1),0,1);
      return `<span style="opacity:${wp};display:inline-block;transform:translateY(${(1-wp)*12}px)">${w}</span>`;}).join(' ');
    html+=`<div>${line}</div>`;}
  c.innerHTML=html;c.style.opacity=1;}
function sceneEls(ids,on){
  ids.forEach(k=>{const el=$(k);if(el)el.style.opacity=on;});}

function render(t){
  ['sea','boat','plumb','floor','semeru','plates','ruler3','spring','eq','outro'].forEach(k=>{
    const el=$(k);if(el)el.style.opacity=0;});
  $('tooltip').classList.add('hidden');
  const si=sceneIndex(t);
  for(let i=0;i<CAPS.length;i++)if(t>=BOUNDS[i][0]&&t<BOUNDS[i][1])showCap(t,Math.min(i,CAPS.length-1));
  const vid=SPEC[si].visual||{};const A=SC[si],B=SCEND[si];

  switch(vid.type){
    case 'boat':{
      $('sea').style.opacity=1;$('boat').style.opacity=1;
      $('seapath').setAttribute('d',setWaves(t,340));
      $('boat').setAttribute('transform',`translate(${Math.sin(t*.8)*8},${Math.sin(t*2.1)*5}) rotate(${Math.sin(t*1.6)*3} 360 315)`);
      break;}
    case 'plumb':{
      $('sea').style.opacity=1;$('plumb').style.opacity=.9;
      const p=ease(seg(t,A+0.2,B-0.2));
      $('plumb').querySelector('line').setAttribute('y2',340+p*663);
      $('plumb').querySelector('path').setAttribute('transform',`translate(0,${p*663})`);
      $('seapath').setAttribute('d',setWaves(t,340));
      if(vid.tooltip)tooltip(t,A+0.35,B-0.05,vid.tooltip.text.replace(/<cy>/g,'<span class="cy">').replace(/<\/cy>/g,'</span>'),vid.tooltip.x,vid.tooltip.y);
      break;}
    case 'floor':{
      $('sea').style.opacity=1;$('plumb').style.opacity=.9;$('floor').style.opacity=1;
      $('plumb').querySelector('line').setAttribute('y2',1003);
      $('plumb').querySelector('path').setAttribute('transform','translate(0,663)');
      $('floorLbl').style.opacity=pop(seg(t,A+0.3,B));
      $('seapath').setAttribute('d',setWaves(t,340));
      break;}
    case 'compare':{
      $('sea').style.opacity=1;$('floor').style.opacity=1;
      $('plumb').querySelector('line').setAttribute('y2',1003);
      $('plumb').querySelector('path').setAttribute('transform','translate(0,663)');
      $('floorLbl').style.opacity=1;
      const so=pop(seg(t,A+0.4,B-0.3));
      $('semeru').style.opacity=so;
      $('seapath').setAttribute('d',setWaves(t,340));
      if(vid.tooltip)tooltip(t,A+0.6,B-0.05,vid.tooltip.text.replace(/<cy>/g,'<span class="cy">').replace(/<\/cy>/g,'</span>'),vid.tooltip.x,vid.tooltip.y);
      break;}
    case 'plates':{
      $('plates').style.opacity=1;
      const inP=pop(seg(t,A+0.2,A+1));
      $('plates').setAttribute('transform',`translate(${lerp(-60,0,inP)},0)`);
      const c=(t*14)%30;
      $('arrL').setAttribute('transform',`translate(${c},0)`);
      $('arrR').setAttribute('transform',`translate(${-c},0)`);
      break;}
    case 'rate':{
      $('ruler3').style.opacity=1;
      const years=Math.floor(100*seg(t,A+0.3,B-0.4));
      $('rfill').setAttribute('width',years*5.8);
      const bounce=(years%25===0&&years>0)?Math.max(0,1-(t-A-years*0.048)/0.25):0;
      $('rmark').setAttribute('transform',`translate(${years*5.8},${-12*bounce})`);
      $('yr3').textContent=years+' TAHUN';
      const mtr=(vid.cm||6.5)*years/100;
      $('mtr3').textContent='= '+(mtr<10?mtr.toFixed(1).replace('.',','):Math.round(mtr))+' METER';
      $('nail').style.opacity=vid.analogy?1:0;
      break;}
    case 'spring':{
      $('spring').style.opacity=1;
      const st=seg(t,A,B-0.3);
      const comp=lerp(260,120,st);
      $('zig').setAttribute('d',springPath(280,440,615,comp));
      const snap=vid.snap;
      if(snap){
        const sp=t-A, wob=Math.sin(sp*16)*10*Math.exp(-sp*2.5);
        $('spring').querySelector('rect').setAttribute('transform',`translate(${-wob},0)`);
        let w='';
        for(let i=0;i<4;i++){
          const wp=seg(t,A+i*.25,B+1.5);
          if(wp>0&&wp<1)w+=`<circle cx="360" cy="615" r="${wp*560}" stroke="var(--red)" stroke-width="${3*(1-wp)+1}" fill="none" opacity="${(1-wp)*.7}"/>`;
        }
        $('waves4').innerHTML=w;
      }
      break;}
    case 'equation':{
      $('eq').style.opacity=1;
      const inP=pop(seg(t,A+0.1,A+0.6));
      $('eq').setAttribute('transform',`translate(0,${lerp(30,0,inP)})`);
      $('eqMain').innerHTML=`${vid.a} = <tspan fill="var(--red)">${vid.b}</tspan>`;
      $('eqLine2').style.opacity=vid.negate?pop(seg(t,B-1.4,B-0.8)):0;
      break;}
    case 'outro':{
      $('outro').style.opacity=1;
      $('o1').style.opacity=pop(seg(t,A+0.3,A+1));
      const fp=seg(t,A+0.9,DUR-0.4);
      $('fault6').style.opacity=fp;
      $('fault6').setAttribute('stroke-dasharray',`${fp*560} 999`);
      break;}
  }
}
const qp=new URLSearchParams(location.search);
if(qp.has('t')){render(parseFloat(qp.get('t')));}
else{let t0=performance.now();
  function loop(now){const t=Math.min((now-t0)/1000,DUR);render(t);requestAnimationFrame(loop);}
  requestAnimationFrame(loop);}
window.__seek=t=>render(t);
</script>
</body>
</html>"""

if __name__=="__main__":
    main()
