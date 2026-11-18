// Execute the actual controller with a small DOM/SAI adapter. This is not native
// X_ITE, audio-device, accessibility-reader or browser-pixel evidence.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {webcrypto} from 'node:crypto';

const root=new URL('../',import.meta.url),source=fs.readFileSync(new URL('gobbler-flyte/observatory.js',root),'utf8');
const html=fs.readFileSync(new URL('gobbler-flyte/index.html',root),'utf8');
const manifest=JSON.parse(fs.readFileSync(new URL('gobbler-flyte/observatory.json',root)));
const atlasBytes=fs.readFileSync(new URL('flywheel-review/atlas/out/atlas.json',root));
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
let serial=0;
class Target{
 constructor(){this.listeners=new Map();}
 addEventListener(type,fn){if(!this.listeners.has(type))this.listeners.set(type,new Set());this.listeners.get(type).add(fn);}
 removeEventListener(type,fn){this.listeners.get(type)?.delete(fn);}
 dispatch(type,props={}){const event={target:this,preventDefault(){this.prevented=true;},...props};for(const fn of [...this.listeners.get(type)||[]])fn(event);return event;}
}
class Element extends Target{
 constructor(id=''){super();this.id=id;this.children=[];this.dataset={};this.attributes=new Map();this.style={setProperty(){}};this.textContent='';this.hidden=false;this.classList={add(){},toggle(){}};this.value='';this.open=false;}
 append(...items){this.children.push(...items);}
 replaceChildren(...items){this.children=items;}
 setAttribute(name,value){this.attributes.set(name,String(value));}
 getAttribute(name){return this.attributes.get(name)??null;}
 focus(){document.activeElement=this;}
 click(){return this.onclick?.();}
 showModal(){assert(!this.open,'showModal must not be repeated on an open dialog');this.open=true;}
 close(){this.open=false;}
}
function environment(){
 const elements=new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element(m[1])]));
 const tabs=['tab-evidence','tab-foldback','tab-search'].map((id,i)=>{const e=elements.get(id);e.dataset.tab=['snapshot','foldback','search'][i];return e;});
 const dossier=new Element(),left=new Element(),doc=new Target();
 Object.assign(doc,{body:new Element(),hidden:false,activeElement:null,createElement:()=>new Element(),createTextNode:text=>({textContent:text}),
  querySelector(selector){if(selector.startsWith('#'))return elements.get(selector.slice(1));if(selector==='.dossier')return dossier;if(selector==='.left-panel')return left;if(selector==='[data-tab=search]')return tabs[2];throw Error('Unhandled selector '+selector);},
  querySelectorAll(selector){if(selector==='[data-tab]')return tabs;if(selector==='.tab-content')return ['snapshot-tab','foldback-tab','search-tab'].map(id=>elements.get(id));if(selector==='#feathers button')return elements.get('feathers').children;if(selector==='#replay-steps button')return elements.get('replay-steps').children.flatMap(n=>n.children);throw Error('Unhandled selector '+selector);}});
 const win=new Target(),preference=new Target();preference.matches=false;win.matchMedia=()=>preference;
 const named=new Map(),scene={getNamedNode(name){if(!named.has(name))named.set(name,{callbacks:new Map(),addFieldCallback(key,field,fn){this.callbacks.set(key+field,fn);},removeFieldCallback(key,field){this.callbacks.delete(key+field);}});return named.get(name);}};
 const browser={currentScene:scene,async loadURL(){}};
 win.X3D={getBrowser:()=>browser,MFString:class extends Array{},SFVec3f:class{constructor(x,y,z){Object.assign(this,{x,y,z});}}};
 const frames=new Map();let frame=0;
 const score=elements.get('score');score.paused=true;score.pause=()=>{score.paused=true;};score.play=async()=>{score.paused=false;};
 globalThis.document=doc;globalThis.window=win;globalThis.X3D=win.X3D;globalThis.customElements={whenDefined:async()=>{}};
 globalThis.requestAnimationFrame=fn=>{frames.set(++frame,fn);return frame;};globalThis.cancelAnimationFrame=id=>frames.delete(id);
 if(!globalThis.crypto)Object.defineProperty(globalThis,'crypto',{value:webcrypto,configurable:true});
 const normalFetch=async url=>{if(url==='observatory.json')return new Response(JSON.stringify(manifest));if(url.includes('atlas/out/atlas.json'))return new Response(atlasBytes);throw Error('Unhandled fetch '+url);};globalThis.fetch=normalFetch;
 return {elements,tabs,doc,win,preference,browser,named,frames,score,normalFetch};
}
async function controller(){
 // Avoid browser auto-boot while importing. Each case gets a fresh task scope.
 delete globalThis.window;delete globalThis.document;
 return import('data:text/javascript;base64,'+Buffer.from(source).toString('base64')+'#case'+(++serial));
}
let passed=0;
async function check(name,fn){await fn();passed++;console.log('PASS '+name);}

await check('independent task keys, latest intent and permanent disposal',async()=>{
 const {createTaskScope}=await controller(),scope=createTaskScope(),a=scope.begin('search'),b=scope.begin('guard');assert(a()&&b());const newer=scope.begin('search');assert(!a()&&newer()&&b());scope.invalidate('guard');assert(!b());scope.stop();assert(!newer());assert(!scope.begin('search')());
});
await check('bounded request wait rejects instead of indefinite loading',async()=>{
 const {withDeadline}=await controller();await assert.rejects(withDeadline(new Promise(()=>{}),'Planted request',3),/Planted request timed out/);assert.equal(await withDeadline(Promise.resolve(7),'Fast request',100),7);
});
await check('readiness waits for actual scene completion; callbacks and frames dispose',async()=>{
 const mod=await controller(),env=environment(),load=deferred();env.browser.loadURL=()=>load.promise;
 const pending=mod.boot();await new Promise(r=>setImmediate(r));assert.equal(mod.state.ready,false);assert.equal(env.doc.body.dataset.state,'loading');assert(env.elements.get('front').disabled);
 load.resolve();await pending;assert.equal(mod.state.ready,true);assert.equal(env.doc.body.dataset.state,'ready');assert.equal(env.frames.size,1);assert.equal(env.named.get('Pick0').callbacks.size,1);
 mod.dispose();assert.equal(mod.state.ready,false);assert.equal(mod.state.status,'disposed');assert.equal(env.frames.size,0);assert.equal(env.named.get('Pick0').callbacks.size,0);mod.dispose();
});
await check('pending boot cannot commit a scene after pagehide',async()=>{
 const mod=await controller(),env=environment(),load=deferred();env.browser.loadURL=()=>load.promise;const pending=mod.boot();await new Promise(r=>setImmediate(r));env.win.dispatch('pagehide',{persisted:false});load.resolve();await assert.rejects(pending,e=>e.name==='AbortError');assert.equal(mod.state.ready,false);assert.equal(mod.state.scene,null);assert.equal(env.frames.size,0);
});
await check('pagehide cancels pending waits without needing a network completion',async()=>{
 const mod=await controller(),env=environment();env.browser.loadURL=()=>new Promise(()=>{});const pending=mod.boot();await new Promise(r=>setImmediate(r));env.win.dispatch('pagehide',{persisted:false});await assert.rejects(pending,e=>e.name==='AbortError');assert.equal(mod.state.status,'disposed');
});
await check('a partial scene-hookup failure clears callbacks and exposes fatal status',async()=>{
 const mod=await controller(),env=environment(),get=env.browser.currentScene.getNamedNode;
 env.browser.currentScene.getNamedNode=name=>{if(name==='Pick2')throw Error('Planted missing selector');return get(name);};
 const previous=console.error;console.error=()=>{};try{await mod.boot().catch(mod.failBoot);}finally{console.error=previous;}
 assert.equal(mod.state.ready,false);assert.equal(mod.state.status,'error');assert.equal(env.doc.body.dataset.state,'error');assert.equal(mod.state.scene,null);assert.equal(env.named.get('Pick0').callbacks.size,0);assert.equal(env.elements.get('front').disabled,true);mod.dispose();
});
await check('reduced-motion changes pause clocks; hidden pages stop cadence',async()=>{
 const mod=await controller(),env=environment();await mod.boot();env.preference.dispatch('change',{matches:true});assert.equal(mod.state.paused,true);assert.equal(env.elements.get('pause').getAttribute('aria-pressed'),'true');assert.equal(typeof env.named.get('Breath').pauseTime,'number');
 env.doc.hidden=true;env.doc.dispatch('visibilitychange');assert.equal(env.frames.size,0);env.doc.hidden=false;env.doc.dispatch('visibilitychange');assert.equal(env.frames.size,1);mod.dispose();
});
await check('tab keyboard navigation keeps exactly one roving tab stop',async()=>{
 const mod=await controller(),env=environment();await mod.boot();const e=env.tabs[0].dispatch('keydown',{key:'End'});assert(e.prevented);assert.equal(env.doc.activeElement,env.tabs[2]);assert.deepEqual(env.tabs.map(t=>t.tabIndex),[-1,-1,0]);assert.equal(env.elements.get('search-tab').hidden,false);assert.equal(env.elements.get('snapshot-tab').hidden,true);
 env.tabs[2].dispatch('keydown',{key:'ArrowRight'});assert.equal(env.doc.activeElement,env.tabs[0]);mod.dispose();
});
await check('abandoned search failure cannot overwrite current empty search',async()=>{
 const mod=await controller(),env=environment(),read=deferred();await mod.boot();globalThis.fetch=url=>url.includes('atlas/out/atlas.json')?read.promise:env.normalFetch(url);
 env.elements.get('query').value='fm/1';const old=mod.search();env.elements.get('query').value='';env.elements.get('query').dispatch('input');await mod.search();const message=env.elements.get('search-state').textContent;read.reject(Error('Old network error'));await old;assert.equal(env.elements.get('search-state').textContent,message);assert.equal(mod.state.errors.length,0);mod.dispose();
});
await check('Atlas identity mismatch refuses results and produces a visible error',async()=>{
 const mod=await controller(),env=environment();await mod.boot();globalThis.fetch=async()=>new Response('{"nodes":[],"edges":[]}');env.elements.get('query').value='fm/1';const previous=console.error;console.error=()=>{};try{await mod.search();}finally{console.error=previous;}
 assert.equal(env.elements.get('search-results').children.length,0);assert.equal(mod.state.atlasHashVerified,undefined);assert.equal(env.elements.get('operation-status').hidden,false);assert.match(env.elements.get('operation-status').textContent,/bytes do not match/);mod.dispose();
});
await check('audio resolving after disposal is paused and never labeled playing',async()=>{
 const mod=await controller(),env=environment(),play=deferred();await mod.boot();env.score.play=async()=>{await play.promise;env.score.paused=false;};const pending=env.elements.get('sound').onclick();mod.dispose();play.resolve();await pending;assert.equal(env.score.paused,true);assert.notEqual(env.elements.get('sound').getAttribute('aria-pressed'),'true');assert.equal(env.elements.get('sound').disabled,true);
});
await check('saved guard result is reported as recorded data without a hardcoded pass',async()=>{
 const mod=await controller(),env=environment();await mod.boot();globalThis.fetch=async()=>new Response(JSON.stringify({scope:'Authored fixture',ok:false,results:[{expectationMet:false}],limits:['No rendering.']}));await env.elements.get('inspect-guard').onclick();const text=env.elements.get('inspector-body').children.map(e=>e.textContent).join(' ');assert.match(text,/0\/1 saved fixture expectations met/);assert.match(text,/overall result: fail/);assert.match(text,/not executed by this page/);assert.equal(env.elements.get('inspector').open,true);mod.dispose();
});
console.log(JSON.stringify({status:'pass',controls:passed,scope:'Actual frontend controller with DOM/SAI/media adapters. Not a native browser, listening or pixel acceptance result.'}));
