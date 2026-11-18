#!/usr/bin/env python3
"""Build a deterministic, local-only evidence intervention laboratory.

The shader checker actually executes. The transfer ledger is an explicitly
authored protocol experiment, never a report of live repository adoption.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
ATLAS=ROOT/'flywheel-review/atlas'
sys.path.insert(0,str(ATLAS))
from shader_guard import inspect_shader_xml


def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()


def build_cases():
    specs=[('gamedev-raw-cdata.x3d',False,'negative'),('gamedev-raw-url.x3d',False,'negative'),
           ('gamedev-fixed-data-uri.x3d',True,'positive'),('positive-https-relative.x3d',True,'positive'),
           ('music-independent-data-uri.x3d',True,'consumer')]
    rows=[]
    for name,expected,role in specs:
        raw=(ATLAS/'fixtures/shader-foldback'/name).read_bytes()
        actual=inspect_shader_xml(raw)
        if actual['ok'] is not expected or actual['shaderParts']<1 or not actual['references']:
            raise ValueError('Independent known answer differs: '+name)
        rows.append({'id':name,'role':role,'expected_accepted':expected,'text':raw.decode(),
                     'sha256':digest(raw),'observed':actual})
    return {'schema':'gobbler.intervention-cases/1','authored_fixtures':True,
            'producer_sha256':digest(Path(__file__).read_bytes()),
            'guard':{'path':'flywheel-review/atlas/shader_guard.py','sha256':digest((ATLAS/'shader_guard.py').read_bytes()),
                     'scope':'Targeted structural GLSL-as-URL recognition. No shader fetch, compilation, linking or rendering.'},
            'fixtures':rows,'sources':[
                {'url':'https://www.w3.org/TR/prov-o/','use':'Separate artifacts, activities and agents; provenance vocabulary, not a certificate.'},
                {'url':'https://www.web3d.org/documents/specifications/19775-1/V4.0/Part01/components/shaders.html','use':'ShaderPart URL semantics.'}],
            'scope':'Actual local Python guard observations on authored fixtures. Interactive transfer rows are synthetic protocol examples. Hash agreement is byte consistency, not authenticated authorship.'}


def node(parent,tag,**attrs):return ET.SubElement(parent,tag,{k:str(v) for k,v in attrs.items()})
def vec(values):return ' '.join(f'{v:.6f}'.rstrip('0').rstrip('.') or '0' for v in values)
def shape(parent,color,tag,*,material_name=None,transparency=0,glow=.12,**attrs):
    s=node(parent,'Shape');a=node(s,'Appearance')
    m={'diffuseColor':color,'emissiveColor':vec([float(v)*glow for v in color.split()]),'specularColor':'.8 .73 .51','shininess':'.72','transparency':transparency}
    if material_name:m['DEF']=material_name
    node(a,'Material',**m);node(s,tag,**attrs);return s
def ring(parent,radius,tube,color,*,name=None):
    t=node(parent,'Transform',**({'DEF':name} if name else {}));pts=[];indices=[]
    for i in range(72):
        a=math.tau*i/72
        for j in range(8):
            b=math.tau*j/8
            pts.append(((radius+tube*math.cos(b))*math.cos(a),(radius+tube*math.cos(b))*math.sin(a),tube*math.sin(b)))
            indices.extend((i*8+j,((i+1)%72)*8+j,((i+1)%72)*8+(j+1)%8,i*8+(j+1)%8,-1))
    sh=shape(t,color,'IndexedFaceSet',solid='false',creaseAngle='3.14',coordIndex=' '.join(map(str,indices)))
    node(sh.find('IndexedFaceSet'),'Coordinate',point=' '.join(vec(p) for p in pts));return t
def label(parent,text,position,size=.28):
    t=node(parent,'Transform',translation=vec(position));sh=shape(t,'.73 .83 .8','Text',string=json.dumps(text),glow=.45)
    node(sh.find('Text'),'FontStyle',family='"SANS"',justify='"MIDDLE" "MIDDLE"',size=size)


def build_scene(cases_hash):
    root=ET.Element('X3D',{'profile':'Interchange','version':'4.0'});head=node(root,'head')
    node(head,'component',name='Text',level=1)
    for name,value in [('title','Gobbler / Three Evidence Instruments'),('cases-sha256',cases_hash),('scope','Static explanatory geometry. Gate colors are local control states; motion is illustrative and never activity.')]:node(head,'meta',name=name,content=value)
    sc=node(root,'Scene');node(sc,'WorldInfo',title='Gobbler / The Intervention Lab')
    node(sc,'Background',skyColor='.012 .027 .035');node(sc,'NavigationInfo',type='"EXAMINE" "ANY"',headlight='false')
    node(sc,'Viewpoint',DEF='Overview',position='0 5 30',orientation='1 0 0 -.12',centerOfRotation='0 1 0',fieldOfView='.7',description='Three evidence instruments')
    for i in range(3):node(sc,'Viewpoint',DEF=f'View{i}',position=f'{(i-1)*8} 2 12',centerOfRotation=f'{(i-1)*8} 1 0',fieldOfView='.75',description=['Identity','Discrimination','Reuse'][i])
    node(sc,'DirectionalLight',direction='-.3 -.6 -1',color='.7 .84 1',intensity='.9')
    node(sc,'DirectionalLight',direction='.5 .3 -.8',color='1 .69 .34',intensity='.6')
    floor=node(sc,'Transform',translation='0 -3.2 -1');shape(floor,'.026 .065 .072','Box',size='26 .18 7',glow=0)
    colors=['.29 .76 .92','.95 .71 .29','.4 .85 .65']
    titles=['01 / IDENTITY','02 / DISCRIMINATION','03 / REUSE']
    for i in range(3):
        t=node(sc,'Transform',translation=f'{(i-1)*8} .4 0')
        base=node(t,'Transform',translation='0 -3.25 0');shape(base,'.075 .13 .14','Box',size='6.7 .3 5.2',glow=0)
        ring(t,2.5,.055,colors[i]);ring(t,2.2,.018,'.45 .38 .22')
        cage=ring(t,1.65,.055,colors[i],name=f'Mechanism{i}')
        for j in range(12):
            a=math.tau*j/12
            petal=node(cage,'Transform',translation=vec([1.95*math.cos(a),1.95*math.sin(a),0]),rotation=vec([0,0,1,a-math.pi/2]),scale='.23 .64 .16')
            shape(petal,colors[i],'Sphere',radius=1,glow=.25)
            dot=node(t,'Transform',translation=vec([2.5*math.cos(a),2.5*math.sin(a),.04]));shape(dot,'.9 .72 .38','Sphere',radius='.07',glow=.3)
        core=node(t,'Transform',rotation='0 0 1 .785398',scale='.72 .72 .72')
        shape(core,'.4 .45 .47','Box',size='1.2 1.2 1.2',material_name=f'Gate{i}',glow=.3)
        for j,(x,c) in enumerate([(-.75,'.93 .32 .27'),(.75,'.3 .83 .65')]):
            track=node(t,'Transform',translation=f'{x} -1.25 .5')
            shape(track,c,'Sphere',radius='.18',material_name=f'Control{i}_{j}',glow=.4)
        label(t,titles[i],[0,-3.85,.1],.29)
    # Gold relational rails connect the instruments. They are declared links,
    # not sampled throughput or a principal-component axis.
    for x in [-4,4]:
        rail=node(sc,'Transform',translation=f'{x} .4 -.35',rotation='0 0 1 1.570796')
        shape(rail,'.62 .45 .2','Cylinder',radius='.018',height='3',glow=.4)
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)+b'\n'


def main():
    cases=canonical(build_cases());scene=build_scene(digest(cases))
    (HERE/'cases.json').write_bytes(cases);(HERE/'instruments.x3d').write_bytes(scene)
    (HERE/'cases.manifest.json').write_bytes(canonical({'schema':'gobbler.intervention-manifest/1','file':'cases.json','bytes':len(cases),'sha256':digest(cases),'scene_sha256':digest(scene)}))
    print(json.dumps({'status':'pass','executed_shader_fixtures':5,'cases_sha256':digest(cases),'scene_bytes':len(scene)}))


if __name__=='__main__':main()
