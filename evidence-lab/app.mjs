import {binding,sha256,qualifyControls,countReuses,snapshotXML} from './model.mjs';
const $=id=>document.getElementById(id),state=window.__intervention={ready:false,errors:[],mode:0};
let data,manifest,scene,sceneXML,revision=0,disposed=false,moving=false,raf,lastTime,angle=0;
const lifecycle=new AbortController();
async function bounded(task,milliseconds,label){
 if(lifecycle.signal.aborted)throw Error('Page disposed');
 let timer;const stop=()=>{};
 try{return await Promise.race([task(),new Promise((_,reject)=>{
  timer=setTimeout(()=>reject(Error(label+' timed out')),milliseconds);
  const aborted=()=>reject(Error('Page disposed'));
  lifecycle.signal.addEventListener('abort',aborted,{once:true});
  stop.abort=()=>lifecycle.signal.removeEventListener('abort',aborted);
 })]);}finally{clearTimeout(timer);stop.abort?.();}
}
async function getBytes(name){
 const request=new AbortController(),abort=()=>request.abort();lifecycle.signal.addEventListener('abort',abort,{once:true});
 if(lifecycle.signal.aborted)request.abort();
 try{return await bounded(async()=>{const r=await fetch(name,{cache:'no-store',signal:request.signal});if(!r.ok)throw Error(name+' unavailable');return r.arrayBuffer();},15000,name);}
 finally{request.abort();lifecycle.signal.removeEventListener('abort',abort);}
}
const entries=[
 {tag:'01 / A CONTENT-BOUND CLAIM',title:'One byte.\nA different claim.',question:'If the picture looks identical, does the old receipt still identify the input?',insight:'A newline changes byte identity without changing the authored scene. Rebinding the digest restores consistency; it does not supply an independent witness.'},
 {tag:'02 / A GUARD MUST DISCRIMINATE',title:'Green is not\nenough.',question:'What can a perfect pass rate hide when every control is already valid?',insight:'An always-accept checker looks successful on positive fixtures. Keep known failures in the experiment: a useful guard must distinguish the two.'},
 {tag:'03 / A RETURN HAS AN IDENTITY',title:'A retry is not\na return.',question:'Should running the same consumption three times give the organism three new capabilities?',insight:'Count distinct guard, target and input-digest tuples. A new row ID or repeated run cannot manufacture a new consumption. The count is still a protocol example, not live adoption.'}
];
function fail(e){if(disposed)return;state.errors.push(String(e));$('error').hidden=false;$('error').textContent=e?.message||String(e);$('status').textContent='The current operation did not complete';}
function safe(task){Promise.resolve().then(task).catch(fail);}
function rows(items){$('rows').replaceChildren(...items.map(([a,b])=>{const r=document.createElement('div'),x=document.createElement('b'),y=document.createElement('span');r.className='row';x.textContent=a;y.textContent=b;r.append(x,y);return r;}));}
function material(index,ok){if(!scene)return;const m=scene.getNamedNode('Gate'+index),c=ok?[.32,.87,.65]:[.95,.34,.27];m.diffuseColor=new X3D.SFColor(...c);m.emissiveColor=new X3D.SFColor(...c.map(v=>v*.3));}
function checkSceneContract(){
 const check=(name,type,fields)=>{const n=scene.getNamedNode(name);if(n.getNodeTypeName()!==type)throw Error(name+' has the wrong node type');
  for(const [field,expected] of Object.entries(fields))if(n.getFieldDefinition(field).getValue().getTypeName()!==expected)throw Error(name+'.'+field+' has the wrong field type');};
 for(let i=0;i<3;i++){check('Gate'+i,'Material',{diffuseColor:'SFColor',emissiveColor:'SFColor'});check('Mechanism'+i,'Transform',{rotation:'SFRotation'});check('View'+i,'Viewpoint',{set_bind:'SFBool'});}
 check('Overview','Viewpoint',{set_bind:'SFBool'});
}
function ledger(){const a=data.fixtures.find(f=>f.role==='consumer'),b=data.fixtures.find(f=>f.role==='positive'),base={guard:data.guard.sha256,target:'music',input_sha256:a.sha256,input_bound:true,accepted:a.observed.ok};
 const first={id:'authored:music-1',...base},selection=$('ledger').value;
 if(selection==='retry')return [first,{...base,id:'retry:2'},{...base,id:'renamed:3'}];
 if(selection==='second')return [first,{...base,id:'hypothetical:physics-2',target:'physics',input_sha256:b.sha256,accepted:b.observed.ok}];
 if(selection==='origin')return [{...first,target:'gamedev'}];if(selection==='stale')return [{...first,input_bound:false}];return [first];}
async function update(){
 if(!data||disposed)return;const rev=++revision,mode=state.mode,entry=entries[mode];
 $('tag').textContent=entry.tag;$('title').textContent=entry.title;$('question').textContent=entry.question;$('insight').textContent=entry.insight;
 ['identityControls','guardControls','reuseControls'].forEach((id,i)=>$(id).hidden=i!==mode);
 document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.mode)===mode)));
 let result,ok,number,title,detail,items;
 if(mode===0){const original=data.fixtures.find(f=>f.id==='gamedev-fixed-data-uri.x3d');let text=original.text;
  if($('mutation').value==='whitespace')text+='\n';else if($('mutation').value==='geometry')text=text.replace('<Box/>','<Sphere radius="1"/>');
  const expected=$('rebind').checked?await sha256(text):original.sha256;result=await binding(text,expected);ok=result.ok;number=ok?'=':'≠';title=ok?'These bytes match the selected digest':'The selected digest identifies different bytes';detail=$('rebind').checked?'Self-issued rebinding proves no independent review.':'The saved digest belongs to the original fixture.';items=[['Expected SHA-256',result.expected],['Observed SHA-256',result.observed],['Byte length',String(result.bytes)]];
 }else if(mode===1){result=qualifyControls(data.fixtures,{strategy:$('strategy').value,includeNegative:$('negative').checked});ok=result.qualified;number=result.qualified?'2/2':'—';title=ok?'Both sides of the control survive':'This control set does not qualify the guard';detail=`${result.positives} positive and ${result.negatives} negative fixtures · ${result.false_accepts} false accepts · ${result.false_rejects} false rejects`;items=result.rows.map(r=>[r.id,`${r.accepted?'accepted':'rejected'} · ${r.matched?'expected':'WRONG'}`]);
 }else{const controls=qualifyControls(data.fixtures,{strategy:$('strategy').value,includeNegative:$('negative').checked});result=countReuses(ledger(),{qualified:controls.qualified,qualifiedGuard:data.guard.sha256});ok=result.distinct_consumptions>0;number=String(result.distinct_consumptions);title='Distinct authored consumptions';detail=`${result.attempts} ledger rows; ${result.distinct_consumptions} unique qualified tuples. Controls ${controls.qualified?'qualified':'not qualified'}. Synthetic protocol data.`;items=result.records.map(r=>[r.id,r.reason]);}
 if(disposed||rev!==revision)return;
 const observation={schema:'gobbler.intervention-observation/1',experiment:mode,case_catalog_sha256:manifest.sha256,guard_sha256:data.guard.sha256,
  inputs:{mutation:$('mutation').value,self_rebind:$('rebind').checked,strategy:$('strategy').value,include_negative:$('negative').checked,ledger:$('ledger').value},result,
  scope:'Local inspection of authored fixture evidence. No live repository adoption, shader compilation, browser performance or authenticated publisher identity is established.'};
 state.observation=observation;$('resultNumber').textContent=number;$('resultTitle').textContent=title;$('resultDetail').textContent=detail;document.querySelector('.result').dataset.pass=String(ok);rows(items);$('observation').textContent=JSON.stringify(observation,null,2);$('scope').textContent=observation.scope;material(mode,ok);
}
function download(name,text,type){const u=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
function animate(now){if(!moving||disposed)return;const dt=lastTime===undefined?0:Math.min(.05,(now-lastTime)/1000);lastTime=now;angle+=dt*.18;
 for(let i=0;i<3;i++)scene.getNamedNode('Mechanism'+i).rotation=new X3D.SFRotation(0,0,1,angle*(i===1?-1:1));raf=requestAnimationFrame(animate);}
function setMotion(value){moving=Boolean(value&&scene&&!disposed);if(raf)cancelAnimationFrame(raf);lastTime=undefined;$('motion').setAttribute('aria-pressed',String(moving));$('motion').textContent=moving?'Pause illustration':'Illustrate motion';if(moving)raf=requestAnimationFrame(animate);}
const motionQuery=matchMedia('(prefers-reduced-motion: reduce)'),reduced=()=>setMotion(false);motionQuery.addEventListener('change',reduced);
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{state.mode=Number(b.dataset.mode);safe(update);});
for(const id of ['mutation','rebind','strategy','negative','ledger'])$(id).onchange=()=>safe(update);
$('overview').onclick=()=>{if(scene)scene.getNamedNode('Overview').set_bind=true;};$('focus').onclick=()=>{if(scene)scene.getNamedNode('View'+state.mode).set_bind=true;};$('motion').onclick=()=>setMotion(!moving);
$('exportJSON').onclick=()=>download('gobbler-intervention.json',JSON.stringify(state.observation,null,2),'application/json');
$('exportX3D').onclick=()=>safe(()=>{const xml=scene.toXMLString();download('gobbler-intervention.x3d',snapshotXML(xml,state.observation),'model/x3d+xml');});
document.addEventListener('visibilitychange',()=>{if(document.hidden)setMotion(false);});
addEventListener('pagehide',()=>{disposed=true;state.ready=false;revision++;lifecycle.abort();setMotion(false);motionQuery.removeEventListener('change',reduced);});
async function boot(){
 manifest=JSON.parse(new TextDecoder().decode(await getBytes('cases.manifest.json')));if(manifest.schema!=='gobbler.intervention-manifest/1')throw Error('Unknown case manifest');
 const raw=await getBytes('cases.json');if(raw.byteLength!==manifest.bytes||await sha256(raw)!==manifest.sha256)throw Error('Case bytes differ from manifest');data=JSON.parse(new TextDecoder().decode(raw));
 if(data.schema!=='gobbler.intervention-cases/1')throw Error('Unknown case catalog');for(const row of data.fixtures)if(await sha256(row.text)!==row.sha256)throw Error('Fixture identity mismatch');
 await update();$('exportJSON').disabled=false;$('provenance').textContent=`5 EXECUTED PYTHON FIXTURES · CATALOG ${manifest.sha256.slice(0,12)} · SYNTHETIC TRANSFER ROWS`;
 const rawScene=await getBytes('instruments.x3d');if(await sha256(rawScene)!==manifest.scene_sha256)throw Error('Scene bytes differ from manifest');sceneXML=new TextDecoder().decode(rawScene);
 await bounded(()=>customElements.whenDefined('x3d-canvas'),15000,'Local X3D runtime readiness');
 if(disposed)return;const browser=X3D.getBrowser($('world'));scene=await bounded(()=>browser.createX3DFromString(sceneXML),45000,'Scene parsing');if(disposed)return;await bounded(()=>browser.replaceWorld(scene),15000,'Scene replacement');if(disposed)return;
 checkSceneContract();state.scene=scene;await update();if(disposed)return;state.ready=true;$('exportX3D').disabled=false;$('status').textContent='Local bytes matched · X3D ready';
}
safe(boot);
