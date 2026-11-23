#!/usr/bin/env node
/* Render a mascot scene in the bundled X_ITE and save stills per named Viewpoint.
 * node mascot/shot.cjs <scene.x3d> <outdir> [--views Face,Wide] [--w 1600 --h 1000] [--scale 2]
 * Rig: bundled X_ITE (vendor/x_ite), headless Chromium, software GL unless a GPU is present. A black frame fails. */
const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..');
const arg=(k,d)=>{const i=process.argv.indexOf('--'+k);return i>0?process.argv[i+1]:d;};
const scene=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);
const views=arg('views','Face,Wide,Fan,Heart').split(','),W=+arg('w',1600),H=+arg('h',1000),SCALE=+arg('scale',1);
const MIME={'.html':'text/html','.js':'text/javascript','.css':'text/css','.x3d':'model/x3d+xml','.wasm':'application/wasm','.json':'application/json','.woff2':'font/woff2'};
const srv=http.createServer((q,r)=>{const p=path.resolve(ROOT,'.'+decodeURIComponent(q.url.split('?')[0]));
  if(!p.startsWith(ROOT)||!fs.existsSync(p)||fs.statSync(p).isDirectory()){r.writeHead(404);return r.end();}
  r.writeHead(200,{'content-type':MIME[path.extname(p)]||'application/octet-stream'});r.end(fs.readFileSync(p));});
(async()=>{
  await new Promise(ok=>srv.listen(0,'127.0.0.1',ok));const port=srv.address().port;
  fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch({headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const pg=await b.newPage({viewport:{width:W,height:H},deviceScaleFactor:SCALE});
  const errs=[];pg.on('pageerror',e=>errs.push(String(e)));pg.on('console',m=>{if(m.type()==='error')errs.push(m.text());});
  const rel=path.relative(path.join(ROOT,'mascot'),scene).split(path.sep).join('/');
  await pg.goto(`http://127.0.0.1:${port}/mascot/index.html?bare=1&scene=${encodeURIComponent(rel)}`);
  await pg.waitForFunction(r=>document.body.dataset.ready===r||document.body.dataset.ready==='error',rel,{timeout:90000});
  const info=await pg.evaluate(()=>{const br=document.getElementById('world').browser;const g=document.createElement('canvas').getContext('webgl2');const e=g&&g.getExtension('WEBGL_debug_renderer_info');
    return {name:br.name,version:br.version,ready:document.body.dataset.ready,gl:e?g.getParameter(e.UNMASKED_RENDERER_WEBGL):'unknown'};});
  const res={scene:rel,rig:{engine:`${info.name} ${info.version}`,gl:info.gl,chromium:b.version(),viewport:[W,H],scale:SCALE},stills:[],errors:errs};
  for(const v of views){
    await pg.evaluate(v=>{const br=document.getElementById('world').browser;const n=br.currentScene.getNamedNode('V_'+v);n.set_bind=true;},v);
    await pg.waitForTimeout(3500);
    const file=path.join(out,`${path.basename(scene,'.x3d')}-${v.toLowerCase()}.webp`);
    const buf=await pg.screenshot({path:file,timeout:90000,animations:'disabled'});
    const lit=await pg.evaluate(async src=>{const im=new Image();im.src=src;await im.decode();const c=document.createElement('canvas');c.width=160;c.height=100;const x=c.getContext('2d');x.drawImage(im,0,0,160,100);const d=x.getImageData(0,0,160,100).data;let n=0;for(let i=0;i<d.length;i+=4)if(d[i]+d[i+1]+d[i+2]>90)n++;return n/16000;},'data:image/png;base64,'+buf.toString('base64'));
    res.stills.push({view:v,file:path.relative(ROOT,file),lit_fraction:+lit.toFixed(4),bytes:buf.length});
  }
  res.status=res.stills.every(s=>s.lit_fraction>0.02)?'pass':'fail';
  fs.writeFileSync(path.join(out,`${path.basename(scene,'.x3d')}-render.json`),JSON.stringify(res,null,1)+'\n');
  console.log(JSON.stringify(res));
  await b.close();srv.close();process.exit(res.status==='pass'?0:1);
})().catch(e=>{console.error(e);process.exit(2);});
