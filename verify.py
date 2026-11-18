#!/usr/bin/env python3
"""Portable validation of the new iteration. No network, browser, XSD, or GPU claim."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
ATLAS = ROOT/'flywheel-review'/'atlas'
DEMO = ROOT/'gobbler-flyte'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    checks=[]
    def check(name, ok, **details):
        checks.append({'name':name,'ok':bool(ok),**details})
        print(('PASS ' if ok else 'FAIL ')+name,flush=True)
    test=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ATLAS/'tests'),'-v'])
    check('kernel and snapshot regression tests',test.returncode==0)
    run=subprocess.run([sys.executable,str(ATLAS/'flywheel_kernel.py'),'--check'])
    check('compiled archive view matches source bytes',run.returncode==0)
    manifest=json.loads((DEMO/'observatory.json').read_text())
    before=sha(DEMO/'observatory.x3d')
    build=subprocess.run([sys.executable,str(DEMO/'build_observatory.py')])
    check('scene generator rebuilds to identical bytes',build.returncode==0 and sha(DEMO/'observatory.x3d')==before)
    lab_paths=[ROOT/'evidence-lab'/name for name in ('cases.json','cases.manifest.json','instruments.x3d')]
    lab_before={p.name:sha(p) for p in lab_paths}
    lab_build=subprocess.run([sys.executable,str(ROOT/'evidence-lab/build_lab.py')],capture_output=True,text=True)
    check('executed intervention cases and scene rebuild identically',lab_build.returncode==0 and lab_before=={p.name:sha(p) for p in lab_paths},details=lab_build.stdout.strip() if lab_build.returncode==0 else lab_build.stderr[-1000:])
    tree=ET.parse(DEMO/'observatory.x3d')
    definitions={}; errors=[]
    for el in tree.iter():
        name=el.get('DEF')
        if name:
            if name in definitions: errors.append('duplicate DEF '+name)
            definitions[name]=el.tag
        use=el.get('USE')
        if use and definitions.get(use)!=el.tag: errors.append('missing/mismatched preceding DEF '+use)
    for r in tree.iter('ROUTE'):
        for field in ['fromNode','toNode']:
            if r.get(field) not in definitions: errors.append('unresolved route '+str(r.attrib))
    check('new scene XML and named references',not errors,errors=errors)
    sensors=[n for n in tree.iter('TouchSensor') if n.get('DEF','').startswith('Pick')]
    expected={f'Pick{i}' for i in range(len(manifest['domains']))}
    check('one scene selector for every manifest feather',{n.get('DEF') for n in sensors}==expected)
    meta={n.get('name'):n.get('content') for n in tree.iter('meta')}
    check('scene binds Atlas and domain manifest digests',meta.get('atlas-sha256')==manifest['snapshot']['sha256'] and meta.get('manifest-sha256')==sha(DEMO/'observatory.json'))
    key_errors=[]
    for el in tree.iter():
        if el.tag in ['PositionInterpolator','OrientationInterpolator']:
            keys=list(map(float,el.get('key').split())); values=list(map(float,el.get('keyValue').split()))
            width=3 if el.tag=='PositionInterpolator' else 4
            if any(b<a for a,b in zip(keys,keys[1:])) or len(values)!=len(keys)*width:
                key_errors.append(el.get('DEF'))
    check('animation keys and tuple counts',not key_errors,errors=key_errors)
    # Includes every SAI-controlled DEF; node type/field conformance needs the full validator.
    controlled=['ViewFront','ViewClose','ViewOrbit','LearningRing','Clock_LearningRing','Breath','Stars']
    for i in range(12): controlled.extend(f'{p}{i}' for p in ['Halo','Label','Pick','DomainView','Clock_Wheel','Pulse'])
    for i in range(3): controlled.extend(f'{p}{i}' for p in ['OrbitLayer','Clock_Orbit'])
    check('browser controls resolve scene names',all(n in definitions for n in controlled),missing=[n for n in controlled if n not in definitions])
    html=(DEMO/'index.html').read_text()
    js=(DEMO/'observatory.js').read_text()
    ids=set(re.findall(r'\bid="([^"]+)"',html))
    used=set(re.findall(r'''['"]#([a-z][\w-]*)['"]''',js))
    check('browser controls resolve document IDs',not (used-ids),missing=sorted(used-ids))
    links=re.findall(r'(?:href|src)="([^"]+)"',html)
    missing=[p for p in links if not p.startswith(('data:','http:','https:','#')) and not (DEMO/p).exists()]
    check('entry page local assets exist',not missing,missing=missing)
    check('scene has no Script or external URL',not list(tree.iter('Script')) and not list(tree.iter('Inline')) and not any(n.get('url') for n in tree.iter()))
    sa=subprocess.run([sys.executable,str(DEMO/'build_standalone.py'),'--output',str(ROOT/'.standalone-check.html')],capture_output=True)
    chk=ROOT/'.standalone-check.html'
    check('committed single-file export is current',sa.returncode==0 and (ROOT/'Gobbler-Evidence-Loom.html').exists() and chk.read_bytes()==(ROOT/'Gobbler-Evidence-Loom.html').read_bytes())
    chk.unlink(missing_ok=True)
    leak=subprocess.run([sys.executable,str(ROOT/'tools'/'leak_sweep.py')],capture_output=True,text=True)
    check('leak sweep',leak.returncode==0,out=leak.stdout.strip()[:300])
    report={'schema':'flywheel.verification/1','scope':'local-code-and-artifact-consistency','ok':all(x['ok'] for x in checks),'checks':checks,
            'tool_sha256':sha(Path(__file__)),
            'notRun':['native browser rendering and interaction (current review receipt: receipts/review-browser.json; older browser receipts are historical)','X3D XSD/field typing (separate tools/validate_scene.py)','GPU timing or visual fidelity','audio listening','original experiments and full Atlas witness','current GitHub inventory or PR publication']}
    (ROOT/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    return 0 if report['ok'] else 1
if __name__=='__main__':
    raise SystemExit(main())
