#!/usr/bin/env node
// Native Chromium acceptance for the Intervention Lab (evidence-lab/). Added 18 Nov 2026 because the review host
// could not launch Chromium and the lab had no native record. Every expectation below is the lab's own stated
// rule; the receipt binds the result to the lab's input bytes. Software GL: no GPU, pixel or shader claim.
// Usage: node tools/lab_browser_check.cjs [--json receipts/review-lab-browser.json] [--shot path.png]
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),http=require('node:http');
const ROOT=path.resolve(__dirname,'..');
const arg=(k,d)=>{const i=process.argv.indexOf('--'+k);return i>0?process.argv[i+1]:d;};
const OUT=path.resolve(ROOT,arg('json','receipts/review-lab-browser.json')),SHOT=arg('shot',null);
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const LAB=fs.readdirSync(path.join(ROOT,'evidence-lab')).sort().map(f=>'evidence-lab/'+f);
const inputs=()=>Object.fromEntries([...LAB,'tools/lab_browser_check.cjs','vendor/x_ite/x_ite.min.js'].map(f=>[f,sha(path.join(ROOT,f))]));
const MIME={'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.css':'text/css','.json':'application/json','.x3d':'model/x3d+xml','.wasm':'application/wasm','.svg':'image/svg+xml','.woff2':'font/woff2','.png':'image/png'};
// [mode, control setup, expected {n, pass}]
const CASES=[
 ['identity','original',{mutation:'original',rebind:false},{n:'=',pass:'true'}],
 ['identity','one newline, no rebind',{mutation:'whitespace',rebind:false},{n:'≠',pass:'false'}],
 ['identity','Box to Sphere, no rebind',{mutation:'geometry',rebind:false},{n:'≠',pass:'false'}],
 ['identity','Box to Sphere, self-rebound (consistent, no new witness)',{mutation:'geometry',rebind:true},{n:'=',pass:'true'}],
 ['controls','executed guard with failing fixtures kept',{strategy:'observed',negative:true},{n:'2/2',pass:'true'}],
 ['controls','executed guard, failing fixtures dropped',{strategy:'observed',negative:false},{pass:'false'}],
 ['controls','always-accept guard',{strategy:'always-pass',negative:true},{pass:'false'}],
 ['reuse','one consumer',{ledger:'one'},{n:'1',pass:'true'}],
 ['reuse','same consumption retried 3 times',{ledger:'retry'},{n:'1',pass:'true'}],
 ['reuse','a second input and target',{ledger:'second'},{n:'2',pass:'true'}],
 ['reuse','counting the originating domain',{ledger:'origin'},{n:'0',pass:'false'}],
 ['reuse','input changed without rebinding',{ledger:'stale'},{n:'0',pass:'false'}],
];
(async()=>{
 const rec={schema:'gobbler.lab-browser-check/1',status:'not_run',started_utc:new Date().toISOString(),node:process.version,
  scope:'Native Chromium (software GL) run of the three lab experiments against their stated rules. Not GPU, shader-compilation, pixel-fidelity or adoption evidence.',
  inputs_sha256:inputs(),checks:[],pageErrors:[],consoleErrors:[]};
 let browser,server;
 try{
  const {chromium}=require('playwright');
  server=http.createServer((q,s)=>{const u=decodeURIComponent(new URL(q.url,'http://x').pathname);let f=path.join(ROOT,u);
   if(!f.startsWith(ROOT+path.sep)){s.writeHead(403);return s.end();} if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');
   fs.readFile(f,(e,b)=>{if(e){s.writeHead(404);return s.end();}s.writeHead(200,{'content-type':MIME[path.extname(f)]||'application/octet-stream'});s.end(b);});});
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  try{browser=await chromium.launch();}catch(e){rec.status='not_run';rec.reason=String(e.message||e).slice(0,300);throw e;}
  rec.chromium=browser.version();
  const p=await browser.newPage({viewport:{width:1440,height:900}});
  p.on('pageerror',e=>rec.pageErrors.push(e.message));p.on('console',m=>m.type()==='error'&&rec.consoleErrors.push(m.text()));
  await p.goto(`http://127.0.0.1:${server.address().port}/evidence-lab/`);
  await p.waitForFunction(()=>window.__intervention?.ready===true||window.__intervention?.errors?.length>0,null,{timeout:60000});
  const ready=await p.evaluate(()=>({ready:window.__intervention.ready,errors:window.__intervention.errors}));
  rec.checks.push({name:'lab reports ready with no errors',pass:ready.ready===true&&ready.errors.length===0,observed:ready});
  const read=()=>p.evaluate(()=>({n:document.getElementById('resultNumber').textContent,title:document.getElementById('resultTitle').textContent,pass:document.querySelector('.result').dataset.pass}));
  const MODE={identity:0,controls:1,reuse:2};
  for(const [mode,name,set,exp] of CASES){
   await p.click(`[data-mode="${MODE[mode]}"]`);
   if(mode==='reuse'){await p.click('[data-mode="1"]');await p.selectOption('#strategy','observed');await p.setChecked('#negative',true);await p.click('[data-mode="2"]');}
   if('mutation' in set){await p.selectOption('#mutation',set.mutation);await p.setChecked('#rebind',set.rebind);}
   if('strategy' in set){await p.selectOption('#strategy',set.strategy);await p.setChecked('#negative',set.negative);}
   if('ledger' in set)await p.selectOption('#ledger',set.ledger);
   await p.waitForTimeout(300);
   const got=await read();
   rec.checks.push({name:`${mode}: ${name}`,pass:Object.entries(exp).every(([k,v])=>got[k]===v),expected:exp,observed:got});
  }
  const w=await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
  await p.setViewportSize({width:400,height:860});await p.waitForTimeout(300);
  const mw=await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
  rec.checks.push({name:'no horizontal overflow at 1440 and 400 px',pass:w<=0&&mw<=0,observed:{desktop:w,mobile:mw}});
  if(SHOT){await p.setViewportSize({width:1440,height:900});await p.waitForTimeout(300);await p.screenshot({path:path.resolve(ROOT,SHOT)});}
  rec.checks.push({name:'no page or console errors',pass:rec.pageErrors.length===0&&rec.consoleErrors.length===0});
  rec.status=rec.checks.every(c=>c.pass)?'pass':'fail';
 }catch(e){if(rec.status!=='not_run')rec.status='fail';rec.error=rec.error||String(e.message||e).slice(0,300);}
 finally{
  if(browser)await browser.close();if(server)server.close();
  const after=inputs();rec.inputs_unchanged=JSON.stringify(after)===JSON.stringify(rec.inputs_sha256);
  if(!rec.inputs_unchanged&&rec.status==='pass')rec.status='fail';
  rec.finished_utc=new Date().toISOString();
  fs.writeFileSync(OUT,JSON.stringify(rec,null,1)+'\n');
  for(const c of rec.checks)console.log((c.pass?'PASS ':'FAIL ')+c.name);
  console.log(JSON.stringify({status:rec.status,checks:rec.checks.length,output:path.relative(ROOT,OUT)}));
  process.exit(rec.status==='pass'?0:1);
 }
})();
