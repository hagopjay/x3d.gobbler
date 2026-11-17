const $ = s => document.querySelector(s);
const state = window.__flywheel = {ready:false, errors:[], selected:0, stage:-1, paused:false};
let browser, scene, data, atlas, atlasRequest;
const sceneControls=['#front','#close','#orbit','#focus-domain','#pause','#labels','#detail'];
sceneControls.forEach(id=>$(id).disabled=true);
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
function selectDomain(i,focus=false){
 state.selected=i;const d=data.domains[i];$('.dossier').style.setProperty('--domain',rgb(d.color));
 setText('#domain-name',d.label);setText('#domain-role',d.role);setText('#feather-index',String(i+1).padStart(2,'0'));setText('#domain-mark',String(i+1).padStart(2,'0'));
 fillList('#domain-inputs',d.inputs);fillList('#domain-outputs',d.outputs);setText('#bridge-story',stories[d.id]);
 $('#repo-tags').replaceChildren(...d.repositories.map(r=>{const s=document.createElement('span');s.textContent=r;return s}));
 document.querySelectorAll('#feathers button').forEach((b,j)=>b.setAttribute('aria-pressed',String(i===j)));
 if(scene){data.domains.forEach((_,j)=>node('Halo'+j).whichChoice=j===i?0:-1);if(focus)bind('DomainView'+i)}
}
function inspect(title,parts,kind='EVIDENCE INSPECTOR'){
 setText('#inspector-title',title);setText('#inspector-kind',kind);const body=$('#inspector-body');body.replaceChildren();
 for(const [type,value] of parts){const el=document.createElement(type==='json'?'pre':type==='link'?'a':'p');
 if(type==='json')el.textContent=JSON.stringify(value,null,2);
 else if(type==='link'){el.href=value;el.textContent='Open pinned source ↗';el.target='_blank';el.rel='noopener noreferrer'}
 else{el.textContent=value;if(type==='note')el.className='source-note'}body.append(el)}
 $('#inspector').showModal();
}
async function loadAtlas(){
 if(atlas)return atlas;
 if(!atlasRequest)atlasRequest=(async()=>{
 const res=await fetch('../flywheel-review/atlas/out/atlas.json');if(!res.ok)throw Error('Atlas file unavailable: '+res.status);
 const bytes=await res.arrayBuffer();const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
 if(hash!==data.snapshot.sha256)throw Error('Atlas bytes do not match the compiled snapshot. Rebuild before inspecting.');
 atlas=JSON.parse(new TextDecoder().decode(bytes));state.atlasHashVerified=true;return atlas;
 })().catch(e=>{atlasRequest=null;throw e});
 return atlasRequest;
}
async function inspectRecord(n){
 const graph=await loadAtlas();const edges=graph.edges.filter(e=>e.s===n.id||e.o===n.id);
 const parts=[['note','Pinned archive record. Stored grades and verdicts are historical; this view reruns no experiment.'],['json',n],['json',{edges}]];
 if(n.definedAt&&n.definedAt.startsWith('https://github.com/'))parts.push(['link',n.definedAt]);
 inspect(n.label||n.id,parts,n.type.toUpperCase()+' / '+n.id);
}
async function search(){
 const query=$('#query').value.trim().toLowerCase(), results=$('#search-results');results.replaceChildren();
 if(!query){setText('#search-state','Try “ShaderPart”, “law/7”, or “fm/1”.');return}
 try{setText('#search-state','Reading the local graph…');const graph=await loadAtlas();
 if($('#query').value.trim().toLowerCase()!==query)return;
 const hits=graph.nodes.filter(n=>n.id.toLowerCase()===query||JSON.stringify(n).toLowerCase().includes(query));
 hits.sort((a,b)=>(b.id.toLowerCase()===query)-(a.id.toLowerCase()===query));
 for(const n of hits.slice(0,18)){const b=document.createElement('button'),s=document.createElement('small'),t=document.createElement('span');s.textContent=n.type+' / '+n.id;t.textContent=(n.label||n.id).slice(0,110);b.append(s,t);b.onclick=()=>inspectRecord(n).catch(reportError);results.append(b)}
 setText('#search-state',hits.length?`${fmt(hits.length)} matches · showing ${Math.min(18,hits.length)} · SHA-256 matched`:'No matching record in this archive.');
 }catch(e){setText('#search-state',String(e));reportError(e)}
}
function reportError(e){state.errors.push(String(e));console.error(e)}
function showStage(i){
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
function pause(paused){
 const now=Date.now()/1000;
 const clocks=['Breath','Clock_LearningRing',...data.domains.flatMap((_,i)=>['Clock_Wheel'+i,'Pulse'+i]),...Array.from({length:3},(_,i)=>'Clock_Orbit'+i)];
 for(const c of clocks)node(c)[paused?'pauseTime':'resumeTime']=now;
 state.paused=paused;$('#pause').setAttribute('aria-pressed',String(paused));setText('#pause',paused?'▶ Resume':'Ⅱ Pause');
}
async function boot(){
 const response=await fetch('observatory.json');if(!response.ok)throw Error('Cannot open observatory.json; serve the project root over localhost.');
 data=await response.json();state.manifest=data;const s=data.snapshot,m=s.metrics;
 setText('#node-count',fmt(s.nodeCount));setText('#edge-count',fmt(s.edgeCount));setText('#law-count',s.counts.Law);
 setText('#quote-fraction',m.quotedNumbers+'/'+m.numbers);$('#quote-bar').style.width=(100*m.quotedNumbers/m.numbers)+'%';
 setText('#hash-state','Build: '+s.integrity.checks.filter(x=>x.check==='receipt-sha256'&&x.ok).length+'/8 recorded hashes match');
 setText('#snapshot-pin','docs '+s.pins['x3d.docs'].slice(0,7)+' · loom '+s.pins['x3d.loom'].slice(0,7));
 data.domains.forEach((d,i)=>{const b=document.createElement('button'),dot=document.createElement('i');b.style.setProperty('--c',rgb(d.color));b.append(dot,document.createTextNode(d.label));b.onclick=()=>selectDomain(i);b.setAttribute('aria-label','Inspect '+d.label+' feather');$('#feathers').append(b)});selectDomain(0);
 data.demo.events.forEach((e,i)=>{const li=document.createElement('li'),b=document.createElement('button'),n=document.createElement('b'),t=document.createElement('span');n.textContent=String(i+1).padStart(2,'0');t.textContent=e.state.charAt(0).toUpperCase()+e.state.slice(1);b.append(n,t);b.onclick=()=>showStage(i);li.append(b);$('#replay-steps').append(li)});
 $('#advance').onclick=()=>{if(state.stage<3)showStage(state.stage+1);else inspect(data.demo.incident.title,[['note',data.demo.incident.scope],['json',data.demo]],data.demo.label)};
 $('#reset-replay').onclick=()=>showStage(-1);
 $('#inspect-guard').onclick=async()=>{try{const response=await fetch('../flywheel-review/foldback-run.json');if(!response.ok)throw Error('Guard report unavailable');const run=await response.json();inspect('A real local structural foldback',[
 ['note',run.scope],['p','Both raw-source controls were rejected. The repaired data URI, normal URL controls, and a separately authored Music fixture passed the same narrow guard.'],['json',run],...run.limits.map(l=>['p',l])],'EXECUTED GUARD / AUTHORED FIXTURES');}catch(e){reportError(e)}};
 document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-tab]').forEach(t=>t.setAttribute('aria-selected',String(t===b)));document.querySelectorAll('.tab-content').forEach(s=>s.hidden=s.id!==b.dataset.tab+'-tab');if(b.dataset.tab==='search')$('#query').focus()});
 $('#query').addEventListener('input',()=>{clearTimeout(state.searchTimer);state.searchTimer=setTimeout(search,160)});
 $('#show-limits').onclick=()=>inspect('What this archive can establish',[
 ['note','Local consistency was checked during the build. The recorded source pins identify the historical snapshot. Hashes alone do not authenticate its author.'],
 ['p',`${m.quotedNumbers} of ${m.numbers} Number records have archived verified quote support. ${m.unlinkedFailureModes} of ${s.counts.FailureMode} failures lack an explicit law-ID join; ${m.unlinkedHeuristics} heuristics lack an evidence-ID edge.`],
 ['json',{metricDefinitions:s.metricDefinitions,source:s.source,sha256:s.sha256,pins:s.pins}],...s.limits.map(l=>['p',l])]);
 $('#close-inspector').onclick=()=>$('#inspector').close();$('#inspector').addEventListener('click',e=>{if(e.target===$('#inspector')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close()}});
 $('#related-records').onclick=()=>{const terms={ontology:'semantic',ml:'model',maths:'math',stem:'learn',gameplay:'game',gamedev:'ShaderPart',physics:'physics',music:'audio',data:'trace',heritage:'Armenian','blender-io':'Blender',architecture:'IFC'};document.querySelector('[data-tab=search]').click();$('#query').value=terms[data.domains[state.selected].id];search()};
 $('#front').onclick=()=>bind('ViewFront');$('#close').onclick=()=>bind('ViewClose');$('#orbit').onclick=()=>bind('ViewOrbit');$('#focus-domain').onclick=()=>selectDomain(state.selected,true);
 $('#pause').onclick=()=>pause(!state.paused);
 $('#labels').onclick=()=>{const visible=$('#labels').getAttribute('aria-pressed')!=='true';data.domains.forEach((_,i)=>node('Label'+i).whichChoice=visible?0:-1);$('#labels').setAttribute('aria-pressed',String(visible))};
 $('#detail').onclick=()=>{const visible=$('#detail').getAttribute('aria-pressed')!=='true';node('Stars').whichChoice=visible?0:-1;for(let i=0;i<3;i++)node('OrbitLayer'+i).whichChoice=visible?0:-1;$('#detail').setAttribute('aria-pressed',String(visible))};
 const score=$('#score');$('#sound').onclick=async()=>{const b=$('#sound');b.disabled=true;try{if(score.paused){await score.play();b.setAttribute('aria-pressed','true');b.textContent='♪ Sound on'}else{score.pause();b.setAttribute('aria-pressed','false');b.textContent='♪ Sound'}}catch(e){reportError(e);b.textContent='♪ Unavailable'}finally{b.disabled=false}};
 if(!window.X3D)throw Error('The bundled X_ITE runtime did not load.');
 browser=X3D.getBrowser($('#world'));state.browser=browser;
 await browser.loadURL(new X3D.MFString('observatory.x3d'));scene=browser.currentScene;state.scene=scene;
 for(let i=0;i<data.domains.length;i++)node('Pick'+i).addFieldCallback('feather','touchTime',()=>selectDomain(i));
 selectDomain(0);bind('ViewFront');sceneControls.forEach(id=>$(id).disabled=false);
 if(window.matchMedia('(prefers-reduced-motion: reduce)').matches)pause(true);
 setText('#load-status','Archive snapshot · 12 proposed domains');state.ready=true;
 let start=performance.now(),ticks=0;
 function cadence(now){ticks++;if(now-start>1500){state.uiHz=ticks*1000/(now-start);setText('#cadence',`${Math.round(state.uiHz)} Hz UI cadence · WebGL2`);ticks=0;start=now}requestAnimationFrame(cadence)}requestAnimationFrame(cadence);
}
boot().catch(e=>{reportError(e);setText('#load-status','Could not open the X3D loom');$('#load-status').classList.add('error');setText('#search-state',String(e));const p=document.createElement('p');p.className='snapshot-note error';p.textContent='Open the project with python3 serve.py, then visit localhost:8831. '+String(e);$('.left-panel').append(p)});
