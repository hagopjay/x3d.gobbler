// Actual intervention controller with a strict DOM/SAI adapter. These controls
// do not execute native X_ITE, a screen reader, pixels, shaders or a GPU.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash,webcrypto} from 'node:crypto';

const base=new URL('../evidence-lab/',import.meta.url),model=new URL('model.mjs',base).href;
const read=name=>fs.readFileSync(new URL(name,base)),html=read('index.html').toString(),catalog=read('cases.json'),manifest=JSON.parse(read('cases.manifest.json')),xml=read('instruments.x3d');
const sha=b=>createHash('sha256').update(b).digest('hex');
const defer=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
class Target{constructor(){this.listeners=new Map();}addEventListener(k,f){if(!this.listeners.has(k))this.listeners.set(k,new Set());this.listeners.get(k).add(f);}removeEventListener(k,f){this.listeners.get(k)?.delete(f);}dispatch(k,p={}){for(const f of [...this.listeners.get(k)||[]])f({target:this,...p});}}
class Element extends Target{constructor(id=''){super();this.id=id;this.children=[];this.dataset={};this.attributes=new Map();this.hidden=false;this.disabled=false;this.checked=false;this.value='';this.textContent='';}append(...n){this.children.push(...n);}replaceChildren(...n){this.children=n;}setAttribute(k,v){this.attributes.set(k,String(v));}getAttribute(k){return this.attributes.get(k)??null;}click(){if(!this.disabled)return this.onclick?.();}}
class Color{constructor(...v){this.values=v;}}
class Rotation{constructor(...v){this.values=v;}}
const fields={Material:{diffuseColor:'SFColor',emissiveColor:'SFColor'},Transform:{rotation:'SFRotation'},Viewpoint:{set_bind:'SFBool'}};
function strictScene(source,{omit,wrongField}={}){
 const named=new Map(),writes=[];
 for(const [,type,,name]of source.matchAll(/<([A-Za-z]\w*)\b([^>]*?)\bDEF="([^"]+)"/g)){
  if(name===omit)continue;const schema={...fields[type]},values={};
  if(wrongField?.node===name)schema[wrongField.field]=wrongField.type;
  const node={getNodeTypeName:()=>type,getTypeName:()=>type,getField(field){assert(schema[field],`Missing field ${name}.${field}`);return {getTypeName:()=>schema[field],getValue:()=>values[field]};},getFieldDefinition(field){assert(schema[field],`Missing field ${name}.${field}`);return {getValue:()=>({getTypeName:()=>schema[field]})};}};
  named.set(name,new Proxy(node,{get(t,k){if(k in t)return t[k];if(k in schema)return values[k];throw Error(`Unknown native node property ${name}.${String(k)}`);},set(t,k,v){assert(schema[k],`Illegal SAI field ${name}.${String(k)}`);const expected=schema[k];if(expected==='SFColor')assert(v instanceof Color,`${name}.${k} must receive SFColor`);else if(expected==='SFRotation')assert(v instanceof Rotation,`${name}.${k} must receive SFRotation`);else if(expected==='SFBool')assert.equal(typeof v,'boolean');values[k]=v;writes.push({name,field:k,value:v});return true;}}));
 }
 return {named,writes,rootNodes:[{}],getNamedNode(name){assert(named.has(name),'Missing named node '+name);return named.get(name);},toXMLString:()=>source};
}
function environment(options={}){
 const elements=new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element(m[1])])),buttons=[0,1,2].map(i=>{const e=new Element();e.dataset.mode=String(i);return e;}),result=new Element(),doc=new Target(),win=new Target(),preference=new Target(),frames=new Map();let frame=0;
 for(const [id,value]of Object.entries({mutation:'original',strategy:'observed',ledger:'one'}))elements.get(id).value=value;
 elements.get('negative').checked=true;elements.get('exportJSON').disabled=elements.get('exportX3D').disabled=true;elements.get('error').hidden=true;
 Object.assign(doc,{hidden:false,getElementById:id=>{assert(elements.has(id),'Missing document target '+id);return elements.get(id);},querySelector:s=>{assert.equal(s,'.result');return result;},querySelectorAll:s=>{assert.equal(s,'[data-mode]');return buttons;},createElement:()=>new Element()});
 const parsed=strictScene(xml.toString(),options),browser={createCalls:0,replaceCalls:0,async createX3DFromString(source){this.createCalls++;assert.equal(source,xml.toString(),'Only hash-matched scene bytes may reach native creation');if(options.createWait)await options.createWait.promise;return parsed;},async replaceWorld(s){assert.equal(s,parsed);this.replaceCalls++;}};
 const files={'cases.manifest.json':JSON.stringify(options.manifest||manifest),'cases.json':options.catalog||catalog,'instruments.x3d':options.sceneBytes||xml};
 globalThis.document=doc;globalThis.window=win;globalThis.matchMedia=()=>preference;globalThis.addEventListener=win.addEventListener.bind(win);globalThis.removeEventListener=win.removeEventListener.bind(win);
 globalThis.X3D={getBrowser:()=>browser,SFColor:Color,SFRotation:Rotation};globalThis.customElements={whenDefined:async()=>{}};
 globalThis.requestAnimationFrame=fn=>{frames.set(++frame,fn);return frame;};globalThis.cancelAnimationFrame=id=>frames.delete(id);
 Object.defineProperty(globalThis,'crypto',{configurable:true,value:{subtle:{digest:(...args)=>webcrypto.subtle.digest(...args)}}});
 globalThis.fetch=options.fetcher|| (async(name,init)=>{assert(name in files,'Unexpected request '+name);assert.equal(init?.cache,'no-store');return new Response(files[name]);});
 return {elements,buttons,doc,win,preference,frames,browser,parsed,result};
}
let serial=0;
async function launch(options){const env=environment(options),source=read('app.mjs').toString().replace("from './model.mjs'",'from '+JSON.stringify(model));await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64')+'#ui'+(++serial));return env;}
async function until(fn,label){const deadline=Date.now()+4000;while(!fn()){assert(Date.now()<deadline,'Timed out: '+label);await new Promise(r=>setTimeout(r,5));}}
const done=()=>window.__intervention.ready||window.__intervention.errors.length>0;
const cleanup=env=>env.win.dispatch('pagehide');
let passed=0;async function check(name,fn){await fn();passed++;console.log('PASS '+name);}

await check('hash-matched catalog and scene boot; actual fields receive typed colors and rotations',async()=>{
 const env=await launch();await until(done,'successful boot');assert.equal(window.__intervention.ready,true,JSON.stringify(window.__intervention.errors));assert.equal(window.__intervention.errors.length,0);assert.equal(env.browser.createCalls,1);assert.equal(env.browser.replaceCalls,1);assert(env.parsed.writes.some(w=>w.name==='Gate0'&&w.field==='diffuseColor'));
 env.elements.get('focus').click();assert(env.parsed.writes.some(w=>w.name==='View0'&&w.field==='set_bind'&&w.value===true));env.elements.get('motion').click();assert.equal(env.frames.size,1);const [id,fn]=env.frames.entries().next().value;env.frames.delete(id);fn(1000);assert(env.parsed.writes.some(w=>w.name==='Mechanism0'&&w.field==='rotation'));cleanup(env);assert.equal(env.frames.size,0);assert.equal(env.preference.listeners.get('change').size,0);assert.equal(window.__intervention.ready,false);
});
await check('unknown manifest is refused before catalog or native scene creation',async()=>{
 const env=await launch({manifest:{...manifest,schema:'unrecognized'}});await until(done,'manifest refusal');assert.equal(window.__intervention.ready,false);assert.match(env.elements.get('error').textContent,/manifest/i);assert.equal(env.browser.createCalls,0);cleanup(env);
});
await check('catalog bytes mismatching manifest are refused before native creation',async()=>{
 const env=await launch({catalog:Buffer.concat([catalog,Buffer.from('\n')])});await until(done,'catalog refusal');assert.equal(window.__intervention.ready,false);assert.match(env.elements.get('error').textContent,/bytes differ/i);assert.equal(env.browser.createCalls,0);cleanup(env);
});
await check('rebound catalog with internally stale fixture digest is refused',async()=>{
 const changed=JSON.parse(catalog);changed.fixtures[0].text+='\n';const raw=Buffer.from(JSON.stringify(changed)),env=await launch({catalog:raw,manifest:{...manifest,bytes:raw.length,sha256:sha(raw)}});await until(done,'fixture refusal');assert.equal(window.__intervention.ready,false);assert.match(env.elements.get('error').textContent,/fixture identity/i);assert.equal(env.browser.createCalls,0);cleanup(env);
});
await check('scene identity mismatch is refused before native parsing',async()=>{
 const env=await launch({sceneBytes:Buffer.concat([xml,Buffer.from('\n')])});await until(done,'scene refusal');assert.equal(window.__intervention.ready,false);assert.match(env.elements.get('error').textContent,/scene bytes/i);assert.equal(env.browser.createCalls,0);cleanup(env);
});
await check('missing native Gate rejects readiness instead of preserving false success',async()=>{
 const env=await launch({omit:'Gate0'});await until(done,'missing Gate refusal');assert.equal(window.__intervention.ready,false);assert.match(env.elements.get('error').textContent,/Gate0/);cleanup(env);
});
await check('an unused malformed native Gate is checked before readiness',async()=>{
 const env=await launch({omit:'Gate2'});await until(done,'all Gate contract checks');assert.equal(window.__intervention.ready,false);assert.match(env.elements.get('error').textContent,/Gate2/);cleanup(env);
});
await check('incorrect native field type is refused before successful readiness',async()=>{
 const env=await launch({wrongField:{node:'Gate1',field:'diffuseColor',type:'SFVec3f'}});await until(done,'typed field refusal');assert.equal(window.__intervention.ready,false);assert.match(env.elements.get('error').textContent,/Gate1.diffuseColor/);cleanup(env);
});
await check('stale identity calculation cannot overwrite the controls experiment',async()=>{
 const env=await launch();await until(done,'race baseline');const original=JSON.parse(catalog).fixtures.find(f=>f.id==='gamedev-fixed-data-uri.x3d').text,wait=defer();let held=false;
 Object.defineProperty(globalThis,'crypto',{configurable:true,value:{subtle:{async digest(...args){if(!held&&new TextDecoder().decode(args[1])===original+'\n'){held=true;await wait.promise;}return webcrypto.subtle.digest(...args);}}}});
 env.elements.get('mutation').value='whitespace';env.elements.get('mutation').onchange();await until(()=>held,'old digest held');env.buttons[1].click();await until(()=>window.__intervention.observation.experiment===1,'new controls state');const current=env.elements.get('observation').textContent;wait.resolve();await new Promise(r=>setTimeout(r,20));assert.equal(env.elements.get('observation').textContent,current);assert.equal(window.__intervention.observation.experiment,1);cleanup(env);
});
await check('scene finishing after pagehide never commits or becomes ready',async()=>{
 const wait=defer(),env=await launch({createWait:wait});await until(()=>env.browser.createCalls===1,'pending scene');cleanup(env);wait.resolve();await new Promise(r=>setTimeout(r,20));assert.equal(env.browser.replaceCalls,0);assert.equal(window.__intervention.ready,false);assert.equal(window.__intervention.errors.length,0);
});
await check('pagehide aborts the active fetch and suppresses its late error',async()=>{
 const wait=defer();let signal;const env=await launch({fetcher:async(name,init)=>{signal=init.signal;return wait.promise;}});await until(()=>signal,'request started');cleanup(env);assert.equal(signal.aborted,true);wait.reject(Error('Late abandoned network failure'));await new Promise(r=>setTimeout(r,20));assert.equal(window.__intervention.ready,false);assert.equal(window.__intervention.errors.length,0);assert.equal(env.elements.get('error').hidden,true);
});
console.log(JSON.stringify({status:'pass',controls:passed,scope:'Actual intervention controller, actual Web Crypto, owned fixture/scene bytes, strict typed DOM/SAI adapter and asynchronous negative controls. Not native X_ITE pixels or device validation.'}));
