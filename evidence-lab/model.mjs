// Pure, testable intervention rules. A protocol count is not empirical adoption.
const need=(x,message)=>{if(!x)throw Error(message);};
export async function sha256(text){const bytes=typeof text==='string'?new TextEncoder().encode(text):text;return [...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');}
export async function binding(text,expected){const observed=await sha256(text);return {ok:observed===expected,expected,observed,bytes:new TextEncoder().encode(text).length};}
export function qualifyControls(fixtures,{strategy='observed',includeNegative=true}={}){
 need(['observed','always-pass'].includes(strategy),'Unknown guard strategy');
 need(Array.isArray(fixtures)&&typeof includeNegative==='boolean','Malformed control collection');
 const ids=new Set();for(const f of fixtures){need(typeof f?.id==='string'&&!ids.has(f.id),'Duplicate or missing fixture identity');ids.add(f.id);}
 const selected=fixtures.filter(f=>f.role==='positive'||(includeNegative&&f.role==='negative'));
 need(selected.length>0,'No control fixtures');
 const rows=selected.map(f=>{need(typeof f.expected_accepted==='boolean'&&typeof f.observed?.ok==='boolean','Malformed control');const accepted=strategy==='always-pass'?true:f.observed.ok;return {id:f.id,role:f.role,expected:f.expected_accepted,accepted,matched:accepted===f.expected_accepted};});
 const positives=rows.filter(r=>r.role==='positive').length,negatives=rows.filter(r=>r.role==='negative').length;
 return {qualified:positives>0&&negatives>0&&rows.every(r=>r.matched),positives,negatives,false_accepts:rows.filter(r=>!r.expected&&r.accepted).length,false_rejects:rows.filter(r=>r.expected&&!r.accepted).length,rows,
  scope:'Agreement with independently specified outcomes on this bounded authored control corpus. No shader compilation or universal correctness.'};
}
export function countReuses(rows,{origin='gamedev',qualified=true,qualifiedGuard,domains=['gamedev','music','physics']}={}){
 need(Array.isArray(rows)&&typeof qualified==='boolean'&&domains.includes(origin)&&/^[0-9a-f]{64}$/.test(qualifiedGuard),'Malformed reuse collection or missing qualified guard identity');
 const keys=new Set(),ids=new Set(),records=[];
 for(const row of rows){
  need(typeof row.id==='string'&&!ids.has(row.id),'Duplicate or missing ledger row identity');ids.add(row.id);
  need(domains.includes(row.target)&&/^[0-9a-f]{64}$/.test(row.guard)&&/^[0-9a-f]{64}$/.test(row.input_sha256)&&typeof row.input_bound==='boolean'&&typeof row.accepted==='boolean','Malformed reuse identity');
  let reason='counted',counted=false;
  if(!qualified)reason='guard lacks paired controls';else if(row.guard!==qualifiedGuard)reason='different guard has no bound qualification';else if(!row.input_bound)reason='input digest mismatch';
  else if(row.accepted!==true)reason='consumer did not pass';else if(row.target===origin)reason='origin is not a cross-domain consumer';
  else{const key=JSON.stringify([row.guard,row.target,row.input_sha256]);if(keys.has(key))reason='retry of the same consumption';else{keys.add(key);counted=true;}}
  records.push({...row,counted,reason});
 }
 return {distinct_consumptions:keys.size,attempts:rows.length,records,scope:'Content-bound synthetic protocol count; no live repository adoption or independence of scientific evidence is established.'};
}
export function snapshotXML(xml,observation){
 need(typeof xml==='string'&&xml.includes('</head>'),'Expected owned scene XML');
 const content=JSON.stringify(observation).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
 return xml.replace('</head>',()=>`<meta name="gobbler.intervention-observation" content="${content}"/></head>`);
}
