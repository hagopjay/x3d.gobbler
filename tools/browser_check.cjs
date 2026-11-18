#!/usr/bin/env node
/* Actual native-browser acceptance, independently scoped from source/XML checks.
 * A missing/blocked browser always writes not_run and exits nonzero.
 * node tools/browser_check.cjs [--root DIR] [--page PATH] [--out DIR] [--json FILE]
 * node tools/browser_check.cjs --self-test  (HTTP boundary controls only)
 */
const http=require('node:http'),fs=require('node:fs'),fsp=require('node:fs/promises');
const path=require('node:path'),os=require('node:os'),crypto=require('node:crypto');
const {createRequire}=require('node:module');
const arg=(k,d)=>{const i=process.argv.indexOf('--'+k);return i>0?process.argv[i+1]:d;};
const ROOT=path.resolve(arg('root',path.join(__dirname,'..')));
const PAGE=arg('page','gobbler-flyte/index.html');
const OUT=path.resolve(arg('out',path.join(ROOT,'receipts','browser-review')));
const JSONOUT=path.resolve(arg('json',path.join(ROOT,'receipts','review-browser.json')));
const ALLOW_ASSETS=process.argv.includes('--allow-missing-assets');
const MIME={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css',
 '.json':'application/json','.x3d':'model/x3d+xml','.wasm':'application/wasm','.wav':'audio/wav',
 '.png':'image/png','.svg':'image/svg+xml','.ttl':'text/turtle','.md':'text/markdown','.woff2':'font/woff2'};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const need=(ok,message)=>{if(!ok)throw new Error(message);};
const within=(base,p)=>p===base||p.startsWith(base+path.sep);

function staticServer(root){
 const base=fs.realpathSync(root);
 return http.createServer(async(q,r)=>{
  try{
   let requestPath;
   try{requestPath=decodeURIComponent(q.url.split('?')[0]);}catch(_){r.writeHead(400);r.end();return;}
   const candidate=path.resolve(base,'.'+(requestPath.startsWith('/')?requestPath:'/'+requestPath));
   if(!within(base,candidate)){r.writeHead(403);r.end();return;}
   let actual=await fsp.realpath(candidate);
   if(!within(base,actual)){r.writeHead(403);r.end();return;}
   if((await fsp.stat(actual)).isDirectory())actual=await fsp.realpath(path.join(actual,'index.html'));
   if(!within(base,actual)){r.writeHead(403);r.end();return;}
   const bytes=await fsp.readFile(actual);
   r.writeHead(200,{'content-type':MIME[path.extname(actual)]||'application/octet-stream','cache-control':'no-store'});r.end(bytes);
  }catch(_){r.writeHead(404);r.end();}
 });
}
const listen=srv=>new Promise((resolve,reject)=>{srv.once('error',reject);srv.listen(0,'127.0.0.1',resolve);});
const close=srv=>new Promise(resolve=>srv?.listening?srv.close(resolve):resolve());

async function selfTest(){
 const assert=require('node:assert/strict'),temp=await fsp.mkdtemp(path.join(os.tmpdir(),'gobbler-http-'));
 const base=path.join(temp,'public'),sibling=path.join(temp,'public-private');let srv;
 try{
  await fsp.mkdir(base);await fsp.mkdir(sibling);await fsp.writeFile(path.join(base,'index.html'),'gobbler');
  await fsp.writeFile(path.join(base,'tiny.wasm'),Buffer.from([0,97,115,109]));await fsp.writeFile(path.join(sibling,'secret'),'outside');
  await fsp.symlink(path.join(sibling,'secret'),path.join(base,'escape'));
  srv=staticServer(base);await listen(srv);
  const get=p=>new Promise((resolve,reject)=>{http.get({host:'127.0.0.1',port:srv.address().port,path:p},r=>{let body='';r.on('data',b=>body+=b);r.on('end',()=>resolve({status:r.statusCode,mime:r.headers['content-type'],body}));}).on('error',reject);});
  assert.deepEqual(await get('/'),{status:200,mime:'text/html',body:'gobbler'});
  assert.equal((await get('/tiny.wasm')).mime,'application/wasm');
  assert.equal((await get('/%ZZ')).status,400);
  assert.equal((await get('/%2e%2e%2fpublic-private/secret')).status,403);
  assert.equal((await get('/escape')).status,403);
  console.log(JSON.stringify({status:'pass',controls:5,scope:'Actual loopback HTTP MIME, malformed URI, sibling-prefix and symlink confinement. No browser executed.'}));
 }finally{await close(srv);await fsp.rm(temp,{recursive:true,force:true});}
}

function sourceInventory(){
 const names=['gobbler-flyte/index.html','gobbler-flyte/observatory.js','gobbler-flyte/observatory.css',
  'gobbler-flyte/observatory.json','gobbler-flyte/observatory.x3d','flywheel-review/atlas/out/atlas.json',
  'Gobbler-Evidence-Loom.html'];
 const walk=(dir)=>{for(const e of fs.readdirSync(path.join(ROOT,dir),{withFileTypes:true})){const p=dir+'/'+e.name;if(e.isDirectory())walk(p);else if(e.isFile())names.push(p);}};
 walk('vendor/x_ite');
 return Object.fromEntries(names.sort().map(name=>[name,sha(fs.readFileSync(path.join(ROOT,name)))]));
}

async function main(){
 const R={schema:'gobbler.browser-check/2',status:'not_run',ok:false,page:PAGE,node:process.version,
  started_utc:new Date().toISOString(),tool_sha256:sha(fs.readFileSync(__filename)),
  scope:'Actual native X_ITE browser/interaction checks when launched. Software GL cadence is not a GPU benchmark.',
  checks:[],consoleErrors:[],pageErrors:[],failedRequests:[],httpErrors:[],optionalAssetFailures:[]};
 let srv,browser;
 const check=(name,ok,detail)=>{R.checks.push({name,ok:!!ok,...(detail===undefined?{}:{detail})});console.log((ok?'PASS ':'FAIL ')+name);};
 try{
  need(!path.isAbsolute(PAGE)&&!PAGE.split(/[\\/]/).includes('..'),'--page must be a relative in-project path');
  R.inputs_sha256=sourceInventory();
  let req=require;
  try{req.resolve('playwright');}catch(error){
   need(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,'Playwright unavailable; install it or set NODE_PATH');
   req=createRequire(path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,'..','package.json'));
  }
  const {chromium}=req('playwright');R.playwright=req('playwright/package.json').version;
  const executable=process.env.CHROMIUM_EXECUTABLE_PATH||(fs.existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined);
  R.executable=executable||'Playwright managed Chromium';
  try{browser=await chromium.launch({executablePath:executable,headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});}
  catch(error){R.blocker=String(error);throw error;}
  R.status='fail';R.browser='Chromium '+browser.version();R.gl='requested software SwiftShader; hardware/GPU performance not inferred';
  srv=staticServer(ROOT);await listen(srv);const port=srv.address().port;
  const ctx=await browser.newContext({viewport:{width:1440,height:900},deviceScaleFactor:1});const page=await ctx.newPage();
  const relative=url=>url.replace(/^http:\/\/127\.0\.0\.1:\d+/,'');
  page.on('console',m=>{if(m.type()==='error')R.consoleErrors.push({text:m.text().slice(0,500),url:relative(m.location().url||'')});});
  page.on('pageerror',e=>R.pageErrors.push(String(e).slice(0,500)));
  page.on('requestfailed',q=>R.failedRequests.push(relative(q.url())));
  page.on('response',r=>{if(r.status()>=400)R.httpErrors.push({url:relative(r.url()),status:r.status()});});
  await fsp.mkdir(OUT,{recursive:true});
  const t0=Date.now();await page.goto(`http://127.0.0.1:${port}/${PAGE}`,{waitUntil:'load'});
  await page.waitForFunction(()=>window.__flywheel?.ready===true||window.__flywheel?.status==='error',{},{timeout:60000});
  R.bootMs=Date.now()-t0;R.readiness=await page.evaluate(()=>({ready:window.__flywheel?.ready,status:window.__flywheel?.status,errors:window.__flywheel?.errors||[]}));
  check('explicit successful application readiness',R.readiness.ready===true&&R.readiness.status==='ready',R.readiness);
  need(R.readiness.ready===true,'Application did not reach successful scene readiness');
  const scene=await page.evaluate(()=>{
   const c=document.querySelector('x3d-canvas'),b=c?.browser,w=b?.currentScene;
   const named=['ViewFront','LearningRing','Pick0','Pick11','Clock_Wheel0'];
   return {roots:w?.rootNodes.length||0,version:b?.getVersion?.(),expectedNames:named.map(name=>{try{return {name,found:!!w.getNamedNode(name)};}catch(_){return {name,found:false};}})};
  });
  check('expected Gobbler world and named controls loaded',scene.roots>0&&scene.expectedNames.every(n=>n.found),scene);
  const nat=await page.evaluate(()=>{const c=document.querySelector('x3d-canvas'),cv=c?.shadowRoot?.querySelector('canvas');return cv?{w:cv.width,h:cv.height}:null;});
  check('native WebGL canvas has size',nat&&nat.w>100&&nat.h>100,nat);
  await page.waitForTimeout(1000);await page.screenshot({path:path.join(OUT,'01-boot.png')});
  const expected=JSON.parse(fs.readFileSync(path.join(ROOT,'gobbler-flyte/observatory.json'),'utf8')).snapshot;
  const counts=await page.evaluate(()=>({nodes:document.querySelector('#node-count')?.textContent,edges:document.querySelector('#edge-count')?.textContent}));
  check('rendered archive counters equal current manifest',Number(counts.nodes.replaceAll(',',''))===expected.nodeCount&&Number(counts.edges.replaceAll(',',''))===expected.edgeCount,counts);
  const feathers=await page.$$('#feathers button');check('twelve feather buttons',feathers.length===12,feathers.length);
  const seen=[];for(const i of [0,5,11]){await feathers[i].click();await page.waitForTimeout(100);seen.push(await page.textContent('#domain-name'));}
  check('feather selection changes dossier',new Set(seen).size===3,seen);
  await page.click('[data-tab=foldback]');await page.click('#advance');
  check('synthetic foldback advances explicitly',await page.evaluate(()=>window.__flywheel.stage===0),(await page.textContent('#replay-status')).slice(0,150));
  await page.click('[data-tab=search]');await page.fill('#query','fm/1');
  await page.waitForFunction(()=>document.querySelector('#search-state')?.textContent.includes('SHA-256 matched'),{},{timeout:30000});
  const hits=await page.$$eval('#search-results > *',e=>e.length);check('hash-verified Atlas search returns records',hits>0,{hits});
  const pausedBefore=await page.getAttribute('#pause','aria-pressed');await page.click('#pause');
  check('pause toggles from actual prior state',(await page.getAttribute('#pause','aria-pressed'))!==pausedBefore);
  await page.click('#close');await page.waitForTimeout(1000);await page.screenshot({path:path.join(OUT,'02-loom-heart.png')});
  const cadence=await page.evaluate(()=>new Promise(resolve=>{let n=0;const start=performance.now();const frame=()=>{n++;if(performance.now()-start>2000)resolve(n/((performance.now()-start)/1000));else requestAnimationFrame(frame);};requestAnimationFrame(frame);}));
  R.uiCadenceRafPerSec=+cadence.toFixed(1);check('UI cadence remains live under software rendering',cadence>1,{raf_per_second:R.uiCadenceRafPerSec,not_gpu_fps:true});
  await page.setViewportSize({width:390,height:844});await page.waitForTimeout(500);await page.screenshot({path:path.join(OUT,'03-mobile.png')});
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);check('mobile width has no horizontal overflow',overflow<=1,{pixels:overflow});
  // Optional omissions are visible in the receipt. Never suppress generic console errors.
  const optional=url=>ALLOW_ASSETS&&/^\/assets\/(?:fonts\/[^?]+\.(?:woff2?|ttf)|images\/(?:logo|x_ite)[^/?]*\.(?:svg|png))(?:\?|$)/i.test(url);
  R.optionalAssetFailures=[...R.failedRequests.filter(optional),...R.httpErrors.filter(e=>optional(e.url))];
  check('no uncaught page errors',R.pageErrors.length===0,R.pageErrors);
  check('no console errors',R.consoleErrors.every(e=>optional(e.url)),R.consoleErrors);
  check('no failed required requests',R.failedRequests.filter(u=>!optional(u)).length===0&&R.httpErrors.filter(e=>!optional(e.url)).length===0,{failed:R.failedRequests,http:R.httpErrors});
  const after=sourceInventory();check('checked source bytes remain unchanged',JSON.stringify(after)===JSON.stringify(R.inputs_sha256));
  R.ok=R.checks.every(c=>c.ok);R.status=R.ok?'pass':'fail';
 }catch(error){R.error=String(error.stack||error);console.error(R.error);}
 finally{
  await browser?.close().catch(()=>{});await close(srv);
  R.finished_utc=new Date().toISOString();R.report_sha256=sha(JSON.stringify(R));
  await fsp.mkdir(path.dirname(JSONOUT),{recursive:true});await fsp.writeFile(JSONOUT,JSON.stringify(R,null,2)+'\n');
  console.log(JSON.stringify({status:R.status,checks:R.checks.length,output:JSONOUT}));
  process.exitCode=R.status==='pass'?0:R.status==='not_run'?2:1;
 }
}

if(require.main===module)(process.argv.includes('--self-test')?selfTest():main()).catch(error=>{console.error(error);process.exitCode=1;});
module.exports={staticServer};
