const $ = s => document.querySelector(s);
export const state = {ready:false, status:'loading', disposed:false, errors:[], selected:0, stage:-1, paused:false};
if(typeof window!=='undefined')window.__flywheel=state;
let browser, scene, data, atlas, atlasRequest;
let cadenceFrame=null, searchTimer=null, motionPreference=null;
const cleanups=[];
const sceneCleanups=[],pendingWaits=new Set();
export function createTaskScope(){
 let active=true;const revisions=new Map();
 return {begin(key){const revision=(revisions.get(key)||0)+1;revisions.set(key,revision);return ()=>active&&revisions.get(key)===revision;},
  invalidate(key){revisions.set(key,(revisions.get(key)||0)+1);},stop(){active=false;revisions.clear();},get active(){return active;}};
}
const tasks=createTaskScope();
const inactive=()=>new DOMException('The observatory was closed','AbortError');
const ensureActive=()=>{if(!tasks.active)throw inactive();};
export function withDeadline(promise,label,ms=15000){
 let timer,cancel;const stopped=new Promise((_,reject)=>{cancel=()=>reject(inactive());});pendingWaits.add(cancel);
 return Promise.race([promise,stopped,new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error(label+' timed out. Reload to retry.')),ms);})]).finally(()=>{clearTimeout(timer);pendingWaits.delete(cancel);});
}
function listen(target,type,handler,options){target.addEventListener(type,handler,options);cleanups.push(()=>target.removeEventListener(type,handler,options));}
function setStatus(value){state.status=value;document.body.dataset.state=value;}
const sceneControls=['#front','#close','#orbit','#focus-domain','#pause','#labels','#detail'];
const rgb = c => `rgb(${c.map(x=>Math.round(x*255)).join(',')})`;
const fmt = n => n.toLocaleString('en-US');
const setText = (id,t) => $(id).textContent=t;
const bind = n => scene.getNamedNode(n).set_bind=true;
const node = n => scene.getNamedNode(n);
const stories = {
 ontology:'A heritage object keeps its identity as Blender geometry becomes an X3D scene, a graph entity, and a testable claim.',
 ml:'A failed generated scene becomes a labelled fixture. A held-out task can then test whether the next model learned the rule.',
 maths:'A numerical invariant becomes a visible constraint, then a physics check, then a learner’s experiment.',
 stem:'A beautiful demonstration becomes a question: predict first, move one parameter, measure, then explain the difference.',
 gameplay:'A player’s surprising move becomes a reproducible trajectory, a useful counterexample, and a new challenge.',
 gamedev:'A rendering trap caught in a game becomes a small fixture that protects music, heritage, and science worlds.',
 physics:'An observed motion meets an analytical prediction. Its discrepancy becomes calibration data with units and tolerances.',
 music:'A reliable scene technique becomes a temporal instrument. Human listening supplies a witness that a waveform cannot.',
 data:'Repeated experiments become comparable only when dataset versions, split policies, pins, and failure records travel together.',
 heritage:'A letter, a recording, or a scan retains its source, interpretation, and rights as it changes representation.',
 'blender-io':'An authored object crosses formats and returns. Stable identities, transforms, normals, and material intent face roundtrip tests.',
 architecture:'An IFC element becomes a navigable X3D object while its semantic identity remains available to a query.'
};
function fillList(selector,items){const el=$(selector);el.replaceChildren();for(const x of items){const li=document.createElement('li');li.textContent=x;el.append(li)}}
export function selectDomain(i,focus=false){
 if(!tasks.active)return;
 if(!Number.isInteger(i)||!data?.domains[i])throw RangeError('Unknown domain feather');
 state.selected=i;const d=data.domains[i];$('.dossier').style.setProperty('--domain',rgb(d.color));
 setText('#domain-name',d.label);setText('#domain-role',d.role);setText('#feather-index',String(i+1).padStart(2,'0'));setText('#domain-mark',String(i+1).padStart(2,'0'));
 fillList('#domain-inputs',d.inputs);fillList('#domain-outputs',d.outputs);setText('#bridge-story',stories[d.id]||d.role);
 $('#repo-tags').replaceChildren(...d.repositories.map(r=>{const s=document.createElement('span');s.textContent=r;return s}));
 document.querySelectorAll('#feathers button').forEach((b,j)=>b.setAttribute('aria-pressed',String(i===j)));
 if(scene){data.domains.forEach((_,j)=>node('Halo'+j).whichChoice=j===i?0:-1);if(focus)bind('DomainView'+i)}
}
function inspect(title,parts,kind='EVIDENCE INSPECTOR'){
 if(!tasks.active)return;
 setText('#inspector-title',title);setText('#inspector-kind',kind);const body=$('#inspector-body');body.replaceChildren();
 for(const [type,value] of parts){const el=document.createElement(type==='json'?'pre':type==='link'?'a':'p');
 if(type==='json')el.textContent=JSON.stringify(value,null,2);
 else if(type==='link'){el.href=value;el.textContent='Open pinned source ↗';el.target='_blank';el.rel='noopener noreferrer'}
 else{el.textContent=value;if(type==='note')el.className='source-note'}body.append(el)}
 if(!$('#inspector').open)$('#inspector').showModal();
}
async function loadAtlas(){
 ensureActive();
 if(atlas)return atlas;
 if(!atlasRequest)atlasRequest=(async()=>{
 const res=await withDeadline(fetch('../flywheel-review/atlas/out/atlas.json'),'Atlas request');if(!res.ok)throw Error('Atlas file unavailable: '+res.status);
 const bytes=await withDeadline(res.arrayBuffer(),'Atlas response body');const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
 if(hash!==data.snapshot.sha256)throw Error('Atlas bytes do not match the compiled snapshot. Rebuild before inspecting.');
 ensureActive();atlas=JSON.parse(new TextDecoder().decode(bytes));state.atlasHashVerified=true;return atlas;
 })().catch(e=>{atlasRequest=null;throw e});
 return atlasRequest;
}
async function inspectRecord(n){
 const current=tasks.begin('record');
 const graph=await loadAtlas();const edges=graph.edges.filter(e=>e.s===n.id||e.o===n.id);
 if(!current())return;
 const parts=[['note','Pinned archive record. Stored grades and verdicts are historical; this view reruns no experiment.'],['json',n],['json',{edges}]];
 if(n.definedAt&&n.definedAt.startsWith('https://github.com/'))parts.push(['link',n.definedAt]);
 inspect(n.label||n.id,parts,n.type.toUpperCase()+' / '+n.id);
}
export async function search(){
 if(!tasks.active)return;
 const current=tasks.begin('search');tasks.invalidate('record');
 const query=$('#query').value.trim().toLowerCase(), results=$('#search-results');results.replaceChildren();
 if(!query){setText('#search-state','Try “ShaderPart”, “law/7”, or “fm/1”.');return}
 try{setText('#search-state','Reading the local graph…');const graph=await loadAtlas();
 if(!current()||$('#query').value.trim().toLowerCase()!==query)return;
 const hits=graph.nodes.filter(n=>n.id.toLowerCase()===query||JSON.stringify(n).toLowerCase().includes(query));
 hits.sort((a,b)=>(b.id.toLowerCase()===query)-(a.id.toLowerCase()===query));
 for(const n of hits.slice(0,18)){const b=document.createElement('button'),s=document.createElement('small'),t=document.createElement('span');s.textContent=n.type+' / '+n.id;t.textContent=(n.label||n.id).slice(0,110);b.append(s,t);b.onclick=()=>inspectRecord(n).catch(reportError);results.append(b)}
 setText('#search-state',hits.length?`${fmt(hits.length)} matches · showing ${Math.min(18,hits.length)} · SHA-256 matched`:'No matching record in this archive.');
 }catch(e){if(current()&&$('#query').value.trim().toLowerCase()===query){setText('#search-state',String(e));reportError(e)}}
}
export function reportError(e){if(!tasks.active||e?.name==='AbortError')return;state.errors.push(String(e));if(state.errors.length>40)state.errors.shift();console.error(e);setText('#operation-status',String(e));$('#operation-status').hidden=false;}
export function showStage(i){
 if(!tasks.active)return;
 if(!Number.isInteger(i)||i< -1||i>=data.demo.events.length)throw RangeError('Unknown teaching stage');
 state.stage=i;document.querySelectorAll('#replay-steps button').forEach((b,j)=>{b.classList.toggle('active',j<=i);b.setAttribute('aria-current',j===i?'step':'false')});
 if(i<0){setText('#replay-status','Step through a protocol example. These are invented records, not an archived run.');setText('#advance','Begin the foldback →');if(scene)node('LearningRing').scale=new X3D.SFVec3f(1,1,1);return}
 const e=data.demo.events[i];selectDomain(data.domains.findIndex(d=>d.id===e.domain));
 const explanations=[
  'CANDIDATE · A game effect proposes raw GLSL as a ShaderPart URL. This teaching artifact has not passed a witness.',
  'REPRODUCED · An invented run isolates the URL/source confusion. A named artifact and a content digest bind the observation.',
  'GUARDED · A narrow teaching guard rejects the bad example and accepts its paired control. This is not a complete shader validator.',
  'REUSED · A synthetic Music consumer references the guard and a distinct input digest. One illustrative transfer, counted once.'
 ];setText('#replay-status',explanations[i]);setText('#advance',i===3?'Inspect replay records ↗':'Next return →');
 if(scene){const r=1+i*.35;node('LearningRing').scale=new X3D.SFVec3f(r,r,r)}
}
export function pause(paused){
 if(!scene||!tasks.active)return;
 const now=Date.now()/1000;
 const clocks=['Breath','Clock_LearningRing',...data.domains.flatMap((_,i)=>['Clock_Wheel'+i,'Pulse'+i]),...Array.from({length:3},(_,i)=>'Clock_Orbit'+i)];
 for(const c of clocks)node(c)[paused?'pauseTime':'resumeTime']=now;
 state.paused=paused;$('#pause').setAttribute('aria-pressed',String(paused));setText('#pause',paused?'▶ Resume':'Ⅱ Pause');
}
function selectTab(tab,focus=false){
 const tabs=[...document.querySelectorAll('[data-tab]')];
 for(const t of tabs){const selected=t===tab;t.setAttribute('aria-selected',String(selected));t.tabIndex=selected?0:-1;}
 document.querySelectorAll('.tab-content').forEach(s=>s.hidden=s.id!==tab.dataset.tab+'-tab');
 if(focus)tab.focus();
}
function stopCadence(){if(cadenceFrame!==null)cancelAnimationFrame(cadenceFrame);cadenceFrame=null;}
function startCadence(){
 stopCadence();if(!tasks.active||!state.ready||document.hidden)return;
 let start=performance.now(),ticks=0;
 const cadence=now=>{if(!tasks.active||document.hidden){cadenceFrame=null;return;}ticks++;if(now-start>1500){state.uiHz=ticks*1000/(now-start);setText('#cadence',`${Math.round(state.uiHz)} Hz UI cadence · not GPU timing`);ticks=0;start=now;}cadenceFrame=requestAnimationFrame(cadence);};
 cadenceFrame=requestAnimationFrame(cadence);
}
export function dispose(){
 if(state.disposed)return;state.disposed=true;state.ready=false;setStatus('disposed');tasks.stop();
 for(const cancel of pendingWaits)cancel();
 clearTimeout(searchTimer);stopCadence();for(const cleanup of cleanups.splice(0))cleanup();
 for(const cleanup of sceneCleanups.splice(0))cleanup();
 $('#score').pause();$('#sound').disabled=true;sceneControls.forEach(id=>$(id).disabled=true);
 if($('#inspector').open)$('#inspector').close();
 state.scene=null;state.browser=null;scene=null;browser=null;
}
export async function boot(){
 ensureActive();
 sceneControls.forEach(id=>$(id).disabled=true);setStatus('loading');
 listen(window,'pagehide',e=>{stopCadence();$('#score').pause();$('#sound').setAttribute('aria-pressed','false');$('#sound').textContent='♪ Sound';if(!e.persisted)dispose();});
 listen(window,'pageshow',e=>{if(e.persisted)startCadence();});
 const response=await withDeadline(fetch('observatory.json'),'Observatory manifest');if(!response.ok)throw Error('Cannot open observatory.json; serve the project root over localhost.');
 const loaded=await withDeadline(response.json(),'Manifest response body');ensureActive();data=loaded;state.manifest=data;const s=data.snapshot,m=s.metrics;
 setText('#node-count',fmt(s.nodeCount));setText('#edge-count',fmt(s.edgeCount));setText('#law-count',s.counts.Law);
 setText('#quote-fraction',m.quotedNumbers+'/'+m.numbers);$('#quote-bar').style.width=(100*m.quotedNumbers/m.numbers)+'%';
 setText('#hash-state','Build: '+s.integrity.checks.filter(x=>x.check==='receipt-sha256'&&x.ok).length+'/8 recorded hashes match');
 setText('#snapshot-pin','docs '+s.pins['x3d.docs'].slice(0,7)+' · loom '+s.pins['x3d.loom'].slice(0,7));
 data.domains.forEach((d,i)=>{const b=document.createElement('button'),dot=document.createElement('i');b.style.setProperty('--c',rgb(d.color));b.append(dot,document.createTextNode(d.label));b.onclick=()=>selectDomain(i);b.setAttribute('aria-label','Inspect '+d.label+' feather');$('#feathers').append(b)});selectDomain(0);
 data.demo.events.forEach((e,i)=>{const li=document.createElement('li'),b=document.createElement('button'),n=document.createElement('b'),t=document.createElement('span');n.textContent=String(i+1).padStart(2,'0');t.textContent=e.state.charAt(0).toUpperCase()+e.state.slice(1);b.append(n,t);b.onclick=()=>showStage(i);li.append(b);$('#replay-steps').append(li)});
 $('#advance').onclick=()=>{if(state.stage<3)showStage(state.stage+1);else inspect(data.demo.incident.title,[['note',data.demo.incident.scope],['json',data.demo]],data.demo.label)};
 $('#reset-replay').onclick=()=>showStage(-1);
 $('#inspect-guard').onclick=async()=>{const current=tasks.begin('guard');try{const response=await withDeadline(fetch('../flywheel-review/foldback-run.json'),'Guard report');if(!response.ok)throw Error('Guard report unavailable');const run=await withDeadline(response.json(),'Guard response body');if(!current())return;const met=run.results?.filter(r=>r.expectationMet===true).length||0;inspect('Recorded local structural foldback',[
 ['note','Saved Python report, not executed by this page. Loading the report does not prove current source freshness or authenticate its author.'],['note',run.scope],['p',`${met}/${run.results?.length||0} saved fixture expectations met. Reported overall result: ${run.ok===true?'pass':run.ok===false?'fail':'unavailable'}.`],['json',run],...(run.limits||[]).map(l=>['p',l])],'RECORDED GUARD / AUTHORED FIXTURES');}catch(e){if(current())reportError(e)}};
 const tabs=[...document.querySelectorAll('[data-tab]')];tabs.forEach((b,index)=>{
  b.onclick=()=>{selectTab(b);if(b.dataset.tab==='search')$('#query').focus();};
  listen(b,'keydown',event=>{let i;if(event.key==='ArrowRight')i=(index+1)%tabs.length;else if(event.key==='ArrowLeft')i=(index+tabs.length-1)%tabs.length;else if(event.key==='Home')i=0;else if(event.key==='End')i=tabs.length-1;else return;event.preventDefault();selectTab(tabs[i],true);});
 });
 listen($('#query'),'input',()=>{tasks.invalidate('search');tasks.invalidate('record');clearTimeout(searchTimer);searchTimer=setTimeout(search,160);});
 $('#show-limits').onclick=()=>inspect('What this archive can establish',[
 ['note','Local consistency was checked during the build. The recorded source pins identify the historical snapshot. Hashes alone do not authenticate its author.'],
 ['p',`${m.quotedNumbers} of ${m.numbers} Number records have archived verified quote support. ${m.unlinkedFailureModes} of ${s.counts.FailureMode} failures lack an explicit law-ID join; ${m.unlinkedHeuristics} heuristics lack an evidence-ID edge.`],
 ['json',{metricDefinitions:s.metricDefinitions,source:s.source,sha256:s.sha256,pins:s.pins}],...s.limits.map(l=>['p',l])]);
 $('#close-inspector').onclick=()=>$('#inspector').close();listen($('#inspector'),'click',e=>{if(e.target===$('#inspector')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close()}});
 $('#related-records').onclick=()=>{const terms={ontology:'semantic',ml:'model',maths:'math',stem:'learn',gameplay:'game',gamedev:'ShaderPart',physics:'physics',music:'audio',data:'trace',heritage:'Armenian','blender-io':'Blender',architecture:'IFC'};document.querySelector('[data-tab=search]').click();$('#query').value=terms[data.domains[state.selected].id];search()};
 $('#front').onclick=()=>bind('ViewFront');$('#close').onclick=()=>bind('ViewClose');$('#orbit').onclick=()=>bind('ViewOrbit');$('#focus-domain').onclick=()=>selectDomain(state.selected,true);
 $('#pause').onclick=()=>pause(!state.paused);
 $('#labels').onclick=()=>{const visible=$('#labels').getAttribute('aria-pressed')!=='true';data.domains.forEach((_,i)=>node('Label'+i).whichChoice=visible?0:-1);$('#labels').setAttribute('aria-pressed',String(visible))};
 $('#detail').onclick=()=>{const visible=$('#detail').getAttribute('aria-pressed')!=='true';node('Stars').whichChoice=visible?0:-1;for(let i=0;i<3;i++)node('OrbitLayer'+i).whichChoice=visible?0:-1;$('#detail').setAttribute('aria-pressed',String(visible))};
 const score=$('#score');$('#sound').onclick=async()=>{const b=$('#sound');b.disabled=true;try{if(score.paused){await score.play();if(!tasks.active){score.pause();return;}b.setAttribute('aria-pressed','true');b.textContent='♪ Sound on'}else{score.pause();b.setAttribute('aria-pressed','false');b.textContent='♪ Sound'}}catch(e){reportError(e);if(tasks.active)b.textContent='♪ Unavailable'}finally{if(tasks.active)b.disabled=false}};
 if(!window.X3D)throw Error('The bundled X_ITE runtime did not load.');
 await withDeadline(customElements.whenDefined('x3d-canvas'),'X3D canvas initialization');ensureActive();
 browser=X3D.getBrowser($('#world'));state.browser=browser;
 if(!browser)throw Error('The X3D browser is unavailable');
 await withDeadline((async()=>{await browser.loadURL(new X3D.MFString('observatory.x3d'));})(),'X3D scene',45000);ensureActive();scene=browser.currentScene;state.scene=scene;
 for(let i=0;i<data.domains.length;i++){const sensor=node('Pick'+i);sensor.addFieldCallback('feather','touchTime',()=>selectDomain(i));sceneCleanups.push(()=>sensor.removeFieldCallback('feather','touchTime'));}
 selectDomain(0);bind('ViewFront');sceneControls.forEach(id=>$(id).disabled=false);
 motionPreference=window.matchMedia('(prefers-reduced-motion: reduce)');if(motionPreference.matches)pause(true);
 listen(motionPreference,'change',e=>{if(e.matches)pause(true);});
 setText('#load-status',`Archive snapshot · ${data.domains.length} proposed domains`);state.ready=true;setStatus('ready');
 listen(document,'visibilitychange',()=>{if(document.hidden)stopCadence();else startCadence();});startCadence();
}
export function failBoot(e){if(!tasks.active)return;reportError(e);state.ready=false;setStatus('error');stopCadence();for(const cleanup of sceneCleanups.splice(0))cleanup();scene=null;state.scene=null;sceneControls.forEach(id=>$(id).disabled=true);setText('#load-status','Could not open the X3D loom');$('#load-status').classList.add('error');setText('#search-state',String(e));const p=document.createElement('p');p.className='snapshot-note error';p.textContent='Open the project with python3 serve.py, then visit localhost:8831. '+String(e);$('.left-panel').append(p);}
if(typeof window!=='undefined'&&typeof document!=='undefined')boot().catch(failBoot);
