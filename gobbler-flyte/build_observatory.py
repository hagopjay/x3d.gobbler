#!/usr/bin/env python3
"""Deterministic X3D Gobbler evidence observatory; Python stdlib, no network.
Animation is an illustration. Snapshot metrics are loaded separately by observatory.js.
"""
from __future__ import annotations
import hashlib
import json
import math
import random
from pathlib import Path
from xml.sax.saxutils import quoteattr

HERE = Path(__file__).resolve().parent
TAU = math.tau
X: list[str] = []
add = X.append
rnd = random.Random(1701)
MESHES: dict[tuple, str] = {}
f = lambda n: f"{n:.4f}".rstrip("0").rstrip(".") or "0"
v = lambda q: " ".join(f(n) for n in q)

def material(color, alpha=0, glow=0.65):
    return (f"<Appearance><Material diffuseColor='{v(tuple(.32*c for c in color))}' "
            f"emissiveColor='{v(tuple(glow*c for c in color))}' transparency='{f(alpha)}' "
            "specularColor='0.7 0.8 1' shininess='0.8'/></Appearance>")

def torus(radius=1.0, tube=.025, segments=64, sides=6):
    key = (radius, tube, segments, sides)
    if key in MESHES:
        return f"<IndexedFaceSet USE='{MESHES[key]}'/>"
    name = f"Mesh{len(MESHES)}"
    MESHES[key] = name
    pts = []
    idx = []
    for i in range(segments):
        a = TAU*i/segments
        for j in range(sides):
            b = TAU*j/sides
            pts.append(((radius+tube*math.cos(b))*math.cos(a),
                        (radius+tube*math.cos(b))*math.sin(a),tube*math.sin(b)))
            idx.extend((i*sides+j,((i+1)%segments)*sides+j,
                        ((i+1)%segments)*sides+(j+1)%sides,i*sides+(j+1)%sides,-1))
    return (f"<IndexedFaceSet DEF='{name}' solid='false' creaseAngle='3.14' coordIndex='{' '.join(map(str,idx))}'>"
            f"<Coordinate point='{' '.join(v(p) for p in pts)}'/></IndexedFaceSet>")

def shape(geometry, color, alpha=0, glow=.65):
    return '<Shape>'+material(color,alpha,glow)+geometry+'</Shape>'

def line(points, color, alpha=0):
    return shape(f"<IndexedLineSet coordIndex='{' '.join(str(i) for i in range(len(points)))} -1'>"
                 f"<Coordinate point='{' '.join(v(p) for p in points)}'/></IndexedLineSet>",color,alpha,1)

def text(label, pos, size, color):
    return (f"<Transform translation='{v(pos)}'><Billboard axisOfRotation='0 0 0'>"
            +shape(f"<Text string={quoteattr(chr(34)+label+chr(34))}><FontStyle family='&quot;SANS&quot;' "
                   f"justify='&quot;MIDDLE&quot; &quot;MIDDLE&quot;' size='{f(size)}'/></Text>",color,glow=1)
            +'</Billboard></Transform>')

def clock(name, period):
    add(f"<TimeSensor DEF='{name}' cycleInterval='{f(period)}' loop='true'/>")

def route(src, field, dst, target):
    add(f"<ROUTE fromNode='{src}' fromField='{field}' toNode='{dst}' toField='{target}'/>")

def spin(name, period, axis='0 0 1', direction=1):
    clock('Clock_'+name,period)
    add(f"<OrientationInterpolator DEF='Spin_{name}' key='0 .25 .5 .75 1' "
        f"keyValue='{' '.join(axis+' '+f(direction*TAU*k/4) for k in range(5))}'/>")
    route('Clock_'+name,'fraction_changed','Spin_'+name,'set_fraction')
    route('Spin_'+name,'value_changed',name,'rotation')

def build():
    manifest=json.loads((HERE/'observatory.json').read_text())
    domains=manifest['domains']
    X.clear(); MESHES.clear(); rnd.seed(1701)
    add("<WorldInfo title='Gobbler / The Evidence Loom' info='&quot;Archive evidence and illustrative animation&quot;'/>")
    add("<NavigationInfo type='&quot;EXAMINE&quot; &quot;ANY&quot;' headlight='true' transitionTime='1.2' speed='6'/>")
    add("<Background skyColor='0.006 0.011 0.028'/>")
    add("<Viewpoint DEF='ViewFront' description='The whole Gobbler' position='0 15 61' centerOfRotation='0 13 0' fieldOfView='.72'/>")
    add("<Viewpoint DEF='ViewClose' description='The loom heart' position='0 10.5 29' centerOfRotation='0 11 0' fieldOfView='.8'/>")
    add("<Viewpoint DEF='ViewOrbit' description='A different perspective' position='33 20 46' orientation='0 1 0 .62' centerOfRotation='0 12 0' fieldOfView='.8'/>")
    add("<DirectionalLight direction='-.4 -.5 -1' color='.6 .8 1' intensity='.8'/>")
    add("<PointLight location='0 9 9' color='1 .7 .3' intensity='1' radius='60'/>")
    clock('Breath',6)
    # A single batched star field. All seeded; point sizes are artistic.
    pts=[]; cols=[]
    for _ in range(1500):
        pts.append((rnd.uniform(-120,120),rnd.uniform(-40,100),rnd.uniform(-110,-24)))
        b=rnd.uniform(.15,.65); cols.append((b*.65,b*.8,b))
    add("<Switch DEF='Stars' whichChoice='0'><Group><Shape><Appearance><PointProperties pointSizeScaleFactor='1.4' pointSizeMaxValue='3'/></Appearance>"
        f"<PointSet><Coordinate point='{' '.join(v(p) for p in pts)}'/><Color color='{' '.join(v(c) for c in cols)}'/></PointSet></Shape></Group></Switch>")
    # Loom plinth and circular memory tracks.
    add("<Transform translation='0 -1.6 -1' scale='1 1 .7'>"+shape("<Cylinder radius='24' height='.7'/>",(.08,.12,.22),glow=.14)+"</Transform>")
    for radius in (5,8,13,19,24):
        add(f"<Transform translation='0 -1.15 -1' rotation='1 0 0 1.5708'>"+
            shape(torus(radius,.025,128),(.17,.38,.62),.3)+"</Transform>")
    # Fan: each feather is an inspectable domain. Its eye is itself a flywheel.
    for i,d in enumerate(domains):
        a=-1.22+2.44*i/(len(domains)-1)
        length=22+1.5*math.cos(a*2); color=tuple(d['color'])
        add(f"<Transform rotation='0 0 1 {f(-a)}' translation='0 5 -3'><Transform DEF='Feather{i}'>")
        add(f"<TouchSensor DEF='Pick{i}' description={quoteattr(d['label'])}/>")
        # Smooth tapered vane, central shaft and many barbs: geometry rather than a billboard.
        pts=[]; colors=[]; idx=[]
        for j in range(45):
            t=j/44; y=length*t
            width=1.42*math.sin(math.pi*t)**.8*(.5+.5*t)
            for side in (-1,0,1):
                pts.append((side*width,y,.35*math.sin(t*math.pi)+(.1 if side==0 else 0)))
                weight=(.12+.52*t) if side else (.5+.5*t)
                colors.append(tuple(c*weight for c in color))
            if j:
                n=3*j
                idx.extend((n-3,n,n+1,n-2,-1,n-2,n+1,n+2,n-1,-1))
        add("<Shape><Appearance><Material emissiveColor='1 1 1' transparency='.18'/></Appearance>"
            f"<IndexedFaceSet solid='false' colorPerVertex='true' coordIndex='{' '.join(map(str,idx))}'>"
            f"<Coordinate point='{' '.join(v(p) for p in pts)}'/><Color color='{' '.join(v(c) for c in colors)}'/></IndexedFaceSet></Shape>")
        add(line([(0,0,.5),(0,length,.5)],tuple(.6+.4*c for c in color),.15))
        for j in range(4,39,2):
            t=j/44; width=1.42*math.sin(math.pi*t)**.8*(.5+.5*t)
            for sign in (-1,1):
                add(line([(0,length*(t-.055),.51),(sign*width,length*t,.4)],color,.24))
        # Flywheel ocellus: neutral shared mesh, 12 rotating spokes, distinct per-domain hue.
        y=length*.81
        add(f"<Transform translation='0 {f(y)} .7'>")
        add(shape(torus(1.34,.035),tuple(.45+.55*c for c in color)))
        add(shape(torus(1.09,.06),color,glow=1))
        add(f"<Transform DEF='Wheel{i}'>")
        for k in range(12):
            b=TAU*k/12
            add(line([(.34*math.cos(b),.34*math.sin(b),0),(1.05*math.cos(b),1.05*math.sin(b),0)],color))
            add(f"<Transform translation='{v((1.09*math.cos(b),1.09*math.sin(b),0))}'>"+shape("<Sphere radius='.065'/>",color,glow=1)+"</Transform>")
        add(shape(torus(.4,.07),color,glow=1))
        add(shape("<Sphere radius='.21'/>",(.9,.95,1),glow=1))
        add("</Transform>")
        add(f"<Switch DEF='Halo{i}' whichChoice='-1'><Group>"+shape(torus(1.6,.055),(.95,.82,.42),glow=1)+"</Group></Switch>")
        add("</Transform>")
        add(f"<Switch DEF='Label{i}' whichChoice='0'><Group>"+text(d['label'].upper(),(0,length+1.05,.4),.38,tuple(.5+.5*c for c in color))+"</Group></Switch>")
        add("</Transform></Transform>")
        spin('Wheel'+str(i),20+i*.9,direction=1 if i%2 else -1)
        # A tether from each eye to the heart. It carries illustrative packets only.
        tip=(math.sin(a)*y,5+math.cos(a)*y,-2.2)
        end=(0,8,3); control=(tip[0]*.55,tip[1]*.65,5)
        path=[]
        for j in range(33):
            t=j/32
            path.append(tuple((1-t)**2*tip[k]+2*t*(1-t)*control[k]+t*t*end[k] for k in range(3)))
        add(line(path,color,.65))
        add(f"<Transform DEF='Packet{i}'>"+shape("<Sphere radius='.095'/>",tuple(.4+.6*c for c in color),glow=1)+"</Transform>")
        add(f"<PositionInterpolator DEF='Flow{i}' key='{' '.join(f(j/32) for j in range(33))}' keyValue='{' '.join(v(p) for p in path)}'/>")
        clock('Pulse'+str(i),6+i*.13)
        route('Pulse'+str(i),'fraction_changed','Flow'+str(i),'set_fraction')
        route('Flow'+str(i),'value_changed','Packet'+str(i),'translation')
        eye=(math.sin(a)*y*.67,5+math.cos(a)*y,29)
        add(f"<Viewpoint DEF='DomainView{i}' description={quoteattr(d['label'])} position='{v(eye)}' centerOfRotation='{v(tip)}' fieldOfView='.82'/>")
    # Gobbler: a faceted body, curved neck and luminous, observant head.
    gold=(1,.65,.27); ice=(.5,.85,1)
    add("<Transform DEF='Heart' translation='0 7 2' scale='2.7 3.5 2'>"+shape("<Sphere radius='1'/>",(.14,.25,.4),glow=.5)+"</Transform>")
    for r,z in ((2.9,3.2),(2.4,4),(1.7,4.3)):
        add(f"<Transform translation='0 7 {f(z)}'>"+shape(torus(r,.045),gold,glow=1)+"</Transform>")
    # Two folding wings built from thin curved threads.
    for sign in (-1,1):
        for j in range(9):
            points=[]
            for k in range(25):
                t=k/24
                points.append((sign*(.8+3.8*math.sin(t*math.pi*.8)),8.7-4.8*t+j*.12,3+1.2*math.sin(t*math.pi)))
            add(line(points,tuple(.35+.55*c for c in ice),j*.035))
    neck=[(-.3,9,2),(0,10,2),(1.15,11,2),(1.7,12.5,2),(1.2,13.5,2),(.2,14,2)]
    for p in neck:
        add(f"<Transform translation='{v(p)}' scale='.68 .95 .65'>"+shape("<Sphere radius='1'/>",(.22,.5,.65),glow=.5)+"</Transform>")
    add("<Transform translation='-.3 14.3 2'>"+shape("<Sphere radius='1.05'/>",(.28,.6,.7),glow=.6)+"</Transform>")
    add("<Transform translation='-1.5 14.2 2' rotation='0 0 1 1.5708'>"+shape("<Cone bottomRadius='.4' height='1.5'/>",gold,glow=.7)+"</Transform>")
    add("<Transform translation='-.65 14.6 2.9'>"+shape("<Sphere radius='.23'/>",(.95,.98,1),glow=1)+"</Transform>")
    add("<Transform translation='-.7 14.61 3.1'>"+shape("<Sphere radius='.09'/>",(.02,.04,.09),glow=.1)+"</Transform>")
    for j in range(5):
        a=(j-2)*.22
        add(line([(-.25,15,2),(-.25+a*2,16+math.cos(a),2)],gold))
        add(f"<Transform translation='{v((-.25+a*2,16+math.cos(a),2))}'>"+shape("<Sphere radius='.1'/>",gold,glow=1)+"</Transform>")
    # Memory core: seven station rings; a lesson leaves a durable trace.
    stages=['WEAVE','WITNESS','RECEIPT','FOLD BACK','TEACH','SHOW','REUSE']
    for i,label in enumerate(stages):
        a=-math.pi*.92+math.pi*1.84*i/6
        p=(13*math.sin(a),.9,6*math.cos(a)+1)
        add(f"<Transform translation='{v(p)}'><Transform rotation='1 0 0 1.5708'>"+shape(torus(.8,.035),ice)+"</Transform>"+shape("<Sphere radius='.13'/>",gold,glow=1)+"</Transform>")
        add(text(label,(p[0],p[1]-.6,p[2]),.33,(.45,.62,.8)))
    # Selected foldback stage rises as a ring in the heart, controlled by page.
    add("<Transform translation='0 7 5'><Transform DEF='LearningRing'>"+shape(torus(1,.085),(.4,1,.73),glow=1)+"</Transform></Transform>")
    spin('LearningRing',12,axis='0 1 0')
    # Slow armillary behind the fan.
    for i in range(3):
        add(f"<Switch DEF='OrbitLayer{i}' whichChoice='0'><Group><Transform translation='0 11 -7' rotation='{('1 0 0','0 1 0','0 0 1')[i]} {f(.6+i*.6)}'><Transform DEF='Orbit{i}'>"+
            shape(torus(26+i*1.8,.018,160),(.12,.24,.42),.25)+"</Transform></Transform></Group></Switch>")
        spin('Orbit'+str(i),180+i*30,axis='0 1 0')
    # Hash references the exact local snapshot; it is identity, not authentication.
    digest=manifest['snapshot']['sha256']
    head=("<?xml version='1.0' encoding='UTF-8'?>\n<X3D profile='Immersive' version='4.0'>"
          "<head><component name='Shape' level='5'/>"
          "<meta name='title' content='Gobbler / The Evidence Loom'/>"
          f"<meta name='atlas-sha256' content='{digest}'/>"
          f"<meta name='manifest-sha256' content='{hashlib.sha256((HERE/'observatory.json').read_bytes()).hexdigest()}'/>"
          "<meta name='animation' content='Illustrative; domain mappings are proposals, not measured transfer'/></head><Scene>")
    target=HERE/'observatory.x3d'
    target.write_text(head+'\n'.join(X)+'</Scene></X3D>\n',encoding='utf-8')
    print(f'{target.name}: {target.stat().st_size:,} bytes; {len(domains)} feathers; {len(MESHES)} shared meshes')

if __name__=='__main__':
    build()
