import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync, existsSync, rmSync, readdirSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';
import path from 'node:path';

const CHROME = process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9344;
const CONTENT = process.argv[2] || 'content.json';
const OUT = process.argv[3] || 'out';
const HERE = path.dirname(new URL(import.meta.url).pathname);
const FPS = 24;

mkdirSync(OUT, { recursive: true });
const framesDir = path.join(OUT, 'frames');
rmSync(framesDir, { recursive: true, force: true });
mkdirSync(framesDir, { recursive: true });

const content = JSON.parse(readFileSync(CONTENT, 'utf8'));
const engine = readFileSync(path.join(HERE, 'engine.js'), 'utf8');
const timingPath = path.join(OUT, 'timing.json');
const timing = existsSync(timingPath) ? JSON.parse(readFileSync(timingPath, 'utf8')) : null;

const meta = content.meta;
const buildHtml = `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#0c0c0c}#stage{display:block}</style></head>
<body><canvas id="stage" width="${meta.width}" height="${meta.height}"></canvas>
<script>window.__canvas=document.getElementById('stage');window.__ctx=window.__canvas.getContext('2d');
window.CONTENT=${JSON.stringify(content)};window.TIMING=${timing ? JSON.stringify(timing) : 'null'};</script>
<script>${engine}</script>
<script>window.seek(0);</script></body></html>`;
const buildPath = path.join(OUT, '_build.html');
writeFileSync(buildPath, buildHtml);

const userDir = `/tmp/vox-chrome-${Date.now()}`;
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`, '--disable-gpu',
  '--hide-scrollbars', '--mute-audio', '--no-first-run', '--no-default-browser-check',
  `--user-data-dir=${userDir}`, `--window-size=${meta.width},${meta.height}`, 'about:blank'], { stdio: 'ignore' });

async function getWs(){ for(let i=0;i<80;i++){ try{ const r=await fetch(`http://127.0.0.1:${PORT}/json/list`);
  const list=await r.json(); const p=list.find(t=>t.type==='page'); if(p&&p.webSocketDebuggerUrl) return p.webSocketDebuggerUrl; }catch{} await sleep(250);} throw new Error('no CDP'); }
let id=0; const pend=new Map(); let ws;
const send=(m,p={})=>new Promise((res,rej)=>{ const i=++id; pend.set(i,{res,rej}); ws.send(JSON.stringify({id:i,method:m,params:p})); });

async function main(){
  const url='file://'+path.resolve(buildPath);
  const wsUrl=await getWs(); ws=new WebSocket(wsUrl);
  await new Promise((res,rej)=>{ ws.onopen=res; ws.onerror=rej; });
  ws.onmessage=(ev)=>{ const m=JSON.parse(ev.data); if(m.id&&pend.has(m.id)){ const {res,rej}=pend.get(m.id); pend.delete(m.id); m.error?rej(new Error(JSON.stringify(m.error))):res(m.result);} };
  await send('Page.enable'); await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride',{width:meta.width,height:meta.height,deviceScaleFactor:1,mobile:false});
  await send('Page.navigate',{url});
  for(let i=0;i<80;i++){ const r=await send('Runtime.evaluate',{expression:'typeof window.seek==="function"',returnByValue:true}); if(r.result&&r.result.value) break; await sleep(200); }
  const metaR=await send('Runtime.evaluate',{expression:'JSON.stringify({fps:window.FPS,total:window.TOTAL})',returnByValue:true});
  const {fps,total}=JSON.parse(metaR.result.value);
  console.log(`render: ${total.toFixed(2)}s @ ${fps}fps -> ${framesDir}`);
  const n=Math.round(total*fps);
  for(let f=0; f<n; f++){
    await send('Runtime.evaluate',{expression:`window.seek(${f/fps})`});
    await sleep(18);
    const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
    writeFileSync(path.join(framesDir,`f_${String(f).padStart(5,'0')}.png`), Buffer.from(shot.data,'base64'));
    if(f%200===0) console.log('  frame',f,'/',n);
  }
  ws.close(); chrome.kill('SIGKILL');

  // encode
  const silent=path.join(OUT,'silent.mp4');
  await run('ffmpeg',['-y','-framerate','24','-i',path.join(framesDir,'f_%05d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-movflags','+faststart',silent]);
  const audio=path.join(OUT,'audio.wav');
  const final=path.join(OUT,'final.mp4');
  if(existsSync(audio)){
    await run('ffmpeg',['-y','-i',silent,'-i',audio,'-c:v','copy','-c:a','aac','-b:a','192k','-shortest',final]);
    console.log('wrote', final, '(video + audio)');
  } else {
    await run('ffmpeg',['-y','-i',silent,'-c','copy',final]);
    console.log('wrote', final, '(silent — no out/audio.wav)');
  }
  process.exit(0);
}
function run(cmd,args){ return new Promise((res,rej)=>{ const p=spawn(cmd,args,{stdio:['ignore','ignore','inherit']}); p.on('exit',c=>c===0?res():rej(new Error(cmd+' exit '+c))); }); }
main().catch(e=>{ console.error('render failed:',e.message); try{chrome.kill('SIGKILL');}catch{} process.exit(1); });
