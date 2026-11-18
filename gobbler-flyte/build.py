#!/usr/bin/env python3
"""Gobbler.flyte Mission Control: an art piece. build.py -> scene.x3d + data.json (figures are synthetic, seeded)."""
import json, math, pathlib, random
from xml.sax.saxutils import quoteattr
from urllib.parse import quote
from build_observatory import look_at, mfstring
HERE = pathlib.Path(__file__).resolve().parent
rnd = random.Random(9)
TAU = 2 * math.pi
DOMAINS = [("STEM", (0.25, 0.85, 1.0)), ("Physics", (1.0, 0.45, 0.2)), ("Music", (0.95, 0.3, 0.75)),
           ("Architecture", (0.95, 0.85, 0.35)), ("3D printing", (0.45, 1.0, 0.55)), ("Games", (0.6, 0.45, 1.0)),
           ("Education", (0.3, 1.0, 0.9)), ("Heritage", (1.0, 0.65, 0.3)), ("Ontology", (0.55, 0.7, 1.0))]
R_RING, Y_WHEEL, CORE = 27.0, 8.0, (0.0, 9.0, 0.0)
f = lambda x: ("%.3f" % x).rstrip("0").rstrip(".") or "0"
v = lambda p: " ".join(f(c) for c in p)
X = []; add = X.append

def polar(r, a, y=0.0): return (r * math.cos(a), y, r * math.sin(a))
def mat(d, e=None, t=0.0, name=None):
    e = e if e is not None else tuple(0.7 * c for c in d)
    return (f"<Appearance><Material{' DEF=' + quoteattr(name) if name else ''} diffuseColor='{v(d)}' emissiveColor='{v(e)}' "
            f"specularColor='0.4 0.4 0.4' shininess='0.6'{' transparency=' + quoteattr(f(t)) if t else ''}/></Appearance>")
def torus(R, r, nu=96, nv=18):
    pts, idx = [], []
    for i in range(nu):
        a = TAU * i / nu
        for j in range(nv):
            b = TAU * j / nv
            pts.append(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
    for i in range(nu):
        for j in range(nv):
            a, b = i * nv + j, ((i + 1) % nu) * nv + j
            c, d = ((i + 1) % nu) * nv + (j + 1) % nv, i * nv + (j + 1) % nv
            idx.append(f"{a} {b} {c} {d} -1")
    return (f"<IndexedFaceSet solid='false' creaseAngle='3' coordIndex='{' '.join(idx)}'><Coordinate point='{' '.join(v(p) for p in pts)}'/></IndexedFaceSet>")
def spin(name, period, axis="0 0 1", sign=1):
    add(f"<TimeSensor DEF='T_{name}' cycleInterval='{f(period)}' loop='true'/>"
        f"<OrientationInterpolator DEF='O_{name}' key='0 0.25 0.5 0.75 1' keyValue='{axis} 0 {axis} {f(sign*TAU/4)} {axis} {f(sign*TAU/2)} {axis} {f(sign*3*TAU/4)} {axis} {f(sign*TAU)}'/>"
        f"<ROUTE fromNode='T_{name}' fromField='fraction_changed' toNode='O_{name}' toField='set_fraction'/>"
        f"<ROUTE fromNode='O_{name}' fromField='value_changed' toNode='{name}' toField='set_rotation'/>")
HEAD = "#version 300 es\nprecision highp float;\n"
VS = HEAD + "uniform mat4 x3d_ProjectionMatrix;uniform mat4 x3d_ModelViewMatrix;in vec4 x3d_Vertex;out vec3 vP;void main(){vP=x3d_Vertex.xyz;gl_Position=x3d_ProjectionMatrix*x3d_ModelViewMatrix*x3d_Vertex;}"
NOISE = "float h(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}float n(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(mix(h(i),h(i+vec3(1,0,0)),f.x),mix(h(i+vec3(0,1,0)),h(i+vec3(1,1,0)),f.x),f.y),mix(mix(h(i+vec3(0,0,1)),h(i+vec3(1,0,1)),f.x),mix(h(i+vec3(0,1,1)),h(i+vec3(1,1,1)),f.x),f.y),f.z);}float fbm(vec3 p){float a=.5,s=0.;for(int k=0;k<5;k++){s+=a*n(p);p=p*2.03+7.;a*=.5;}return s;}"
COLS = "const vec3 C[9]=vec3[9](" + ",".join(f"vec3({c[0]},{c[1]},{c[2]})" for _, c in DOMAINS) + ");"
FLOOR = HEAD + "uniform float etime;in vec3 vP;out vec4 x3d_FragColor;" + COLS + NOISE + """
void main(){float r=length(vP.xz),t=etime;float a=atan(vP.z,vP.x);if(a<0.)a+=6.2831853;float s=6.2831853/9.;
float i=floor(a/s+.5);float d=abs(a-i*s);int k=int(mod(i,9.));
vec3 col=vec3(.012,.016,.04);
float ring=pow(.5+.5*sin(r*1.15+t*2.2),14.);col+=vec3(.25,.4,.9)*ring*.55*exp(-r*.03);
float ray=exp(-d*d*r*r*.22)*smoothstep(3.,8.,r)*(1.-smoothstep(24.,31.,r));
float flow=pow(.5+.5*sin(r*.9+t*4.5+i*1.7),5.);col+=C[k]*ray*(.3+1.*flow);col+=vec3(.5,.7,1.)*smoothstep(.992,1.,cos(r*6.2831853))*.1*exp(-r*.025);
float grid=smoothstep(.96,1.,cos(r*3.14159/3.))*.08+smoothstep(.985,1.,cos(a*36.))*.05;col+=vec3(.3,.5,1.)*grid*exp(-r*.02);
col+=vec3(1.,.8,.5)*exp(-r*r*.02)*(.6+.3*sin(t*3.));
col+=C[k]*.11*fbm(vec3(vP.xz*.12,t*.15))*exp(-r*.035);
col*=1.-smoothstep(40.,72.,r);x3d_FragColor=vec4(col,1.);}"""
SKY = HEAD + "uniform float etime;in vec3 vP;out vec4 x3d_FragColor;" + NOISE + """
void main(){vec3 d=normalize(vP);float t=etime*.012;
float n1=fbm(d*2.2+vec3(t,0.,-t)),n2=fbm(d*4.5-vec3(0.,t*1.7,t));
vec3 col=mix(vec3(.01,.012,.05),vec3(.14,.03,.24),smoothstep(.35,.8,n1));
col=mix(col,vec3(.02,.2,.3),smoothstep(.5,.85,n2)*.7);
col+=vec3(.9,.4,.15)*pow(smoothstep(.55,.95,n1*n2*2.2),2.)*.5;
float band=exp(-pow(d.y*3.+.6*sin(d.x*3.+t*6.),2.));col+=vec3(.12,.1,.3)*band*n2;
float cur=pow(.5+.5*sin(d.x*9.+n1*6.+t*20.),6.)*smoothstep(.05,.5,d.y)*(1.-smoothstep(.4,.95,d.y));col+=mix(vec3(.1,.9,.6),vec3(.7,.2,.9),n2)*cur*.35;vec3 g=normalize(vec3(-.5,.55,-.65));float gd=max(dot(d,g),0.);col+=vec3(1.,.75,.5)*pow(gd,60.)*1.2+vec3(.5,.3,.9)*pow(gd,8.)*.35*n1;col*=.35+.65*smoothstep(-.25,.35,d.y);x3d_FragColor=vec4(col,1.);}"""
def shader(name, fs):
    return (f"<ComposedShader DEF='{name}' language='GLSL'><field name='etime' type='SFTime' accessType='inputOutput' value='0'/>"
            f"<ShaderPart type='VERTEX' url={mfstring('data:x-shader/x-vertex,'+quote(VS,safe=''))}/>"
            f"<ShaderPart type='FRAGMENT' url={mfstring('data:x-shader/x-fragment,'+quote(fs,safe=''))}/></ComposedShader>")

# ---- data (synthetic, seeded) ---------------------------------------------------------------------
data = {"synthetic": True, "note": "Art piece. Every figure is invented by a seeded generator; none is a measurement.", "wheels": []}
for i, (name, col) in enumerate(DOMAINS):
    m = 0.35 + 0.65 * rnd.random()
    data["wheels"].append({"name": name, "color": col, "momentum": round(m, 3), "turns": int(400 + 9000 * m * rnd.random()),
                           "worlds": int(12 + 240 * m), "receipts": int(30 + 900 * m * rnd.random()), "period": round(14 - 10 * m, 2)})

# ---- sky, floor, stars ----------------------------------------------------------------------------
add("<TimeSensor DEF='CLOCK' cycleInterval='3600' loop='true'/>")
add(f"<Shape><Appearance>{shader('SkyShader', SKY)}</Appearance><Sphere radius='420' solid='false'/></Shape>")
add(f"<Transform translation='0 -0.05 0'><Shape><Appearance>{shader('FloorShader', FLOOR)}</Appearance>"
    "<IndexedFaceSet solid='false' coordIndex='0 1 2 3 -1'><Coordinate point='-75 0 -75 -75 0 75 75 0 75 75 0 -75'/></IndexedFaceSet></Shape></Transform>")
for s in ("SkyShader", "FloorShader"):
    add(f"<ROUTE fromNode='CLOCK' fromField='elapsedTime' toNode='{s}' toField='etime'/>")
for k in range(3):
    pts, cols = [], []
    for _ in range(1400):
        z = rnd.uniform(-0.25, 1); a = rnd.uniform(0, TAU); r = math.sqrt(1 - z * z); R = rnd.uniform(140, 330)
        pts.append((R * r * math.cos(a), R * z, R * r * math.sin(a)))
        b = rnd.uniform(0.35, 1); c = rnd.choice(DOMAINS)[1]; w = rnd.random() ** 2
        cols.append(tuple(b * (w * c[j] + (1 - w)) for j in range(3)))
    add(f"<Transform DEF='STARS{k}'><Shape><Appearance><PointProperties pointSizeScaleFactor='{f(1.4 + 0.7 * k)}' pointSizeMinValue='1' pointSizeMaxValue='4'/></Appearance>"
        f"<PointSet><Coordinate point='{' '.join(v(p) for p in pts)}'/><Color color='{' '.join(v(c) for c in cols)}'/></PointSet></Shape></Transform>")
    spin(f"STARS{k}", 500 + 260 * k, "0 1 0", 1 if k % 2 else -1)

# ---- the core: a fan of light --------------------------------------------------------------------
add("<Transform translation='0 0.4 0'><Shape>" + mat((0.08, 0.09, 0.16), (0.03, 0.04, 0.09)) + "<Cylinder radius='7' height='0.8'/></Shape></Transform>")
add("<Transform translation='0 1.1 0'><Shape>" + mat((0.1, 0.12, 0.22), (0.05, 0.07, 0.16)) + "<Cylinder radius='4.6' height='0.7'/></Shape></Transform>")
for R_, y_ in ((7.0, 0.8), (4.6, 1.45), (9.5, 0.06)):
    add(f"<Transform translation='0 {y_} 0' rotation='1 0 0 1.5708'><Shape>" + mat((1, 0.85, 0.6), (1, 0.8, 0.5)) + torus(R_, 0.05, 120, 6) + "</Shape></Transform>")
add(f"<Transform DEF='CORE' translation='{v(CORE)}'>")
add("<Transform DEF='HEART'><Shape>" + mat((1, 0.75, 0.3), (1, 0.7, 0.25), name="M_heart") + "<Sphere radius='1.5'/></Shape></Transform>")
add("<Shape>" + mat((1, 0.8, 0.5), (1, 0.75, 0.4), 0.72) + "<Sphere radius='2.5'/></Shape>")
for k, (R, ax, per) in enumerate(((3.4, "1 0 0", 9), (4.1, "0 1 0", 13), (4.9, "1 0 1", 17))):
    add(f"<Transform DEF='GYRO{k}'><Shape>" + mat((0.9, 0.95, 1), (0.75, 0.85, 1)) + torus(R, 0.07, 72, 6) + "</Shape></Transform>")
    spin(f"GYRO{k}", per, ax, 1 if k % 2 == 0 else -1)
add("</Transform>")
add("<TimeSensor DEF='T_beat' cycleInterval='1.5' loop='true'/><PositionInterpolator DEF='P_beat' key='0 0.08 0.2 0.32 1' keyValue='1 1 1 1.3 1.3 1.3 1 1 1 1.15 1.15 1.15 1 1 1'/>"
    "<ROUTE fromNode='T_beat' fromField='fraction_changed' toNode='P_beat' toField='set_fraction'/><ROUTE fromNode='P_beat' fromField='value_changed' toNode='HEART' toField='set_scale'/>")
# the fan: 27 feathers of light in three tiers behind the heart, each swaying on its own phase
add(f"<Transform translation='0 {f(CORE[1] - 1.5)} -1.2' rotation='1 0 0 -0.16'><Transform DEF='FAN'>")
NF = 27
for i in range(NF):
    tier = i % 3; u = i / (NF - 1); ang = (u - 0.5) * 2.9
    L = (12.5, 10.0, 7.6)[tier]; w = (0.62, 0.5, 0.4)[tier]
    c = DOMAINS[int(u * 8.999)][1]
    pts = [(0, 0, 0), (-w, L * 0.55, 0), (0, L, 0), (w, L * 0.55, 0), (0, L * 0.5, 0)]
    cols = [(0.5, 0.2, 0.05), tuple(0.45 * x for x in c), tuple(0.6 + 0.4 * x for x in c), tuple(0.45 * x for x in c), c]
    add(f"<Transform rotation='0 0 1 {f(-ang)}' translation='0 0 {f(-0.25 * tier)}'><Transform DEF='F{i}'>"
        f"<Shape><Appearance><UnlitMaterial emissiveColor='1 1 1' transparency='{f(0.05 + 0.1 * tier)}'/></Appearance>"
        f"<IndexedFaceSet solid='false' colorPerVertex='true' coordIndex='0 1 4 -1 1 2 4 -1 2 3 4 -1 3 0 4 -1'><Coordinate point='{' '.join(v(p) for p in pts)}'/>"
        f"<Color color='{' '.join(v(x) for x in cols)}'/></IndexedFaceSet></Shape>"
        f"<Transform translation='0 {f(L * 0.8)} 0.06'><Shape>" + mat(c, c) + f"<Sphere radius='{f(0.34 - 0.06 * tier)}'/></Shape></Transform>"
        f"<Transform translation='0 {f(L * 0.8)} 0.05'><Shape>" + mat((1, 1, 1), (1, 1, 1), 0.55) + f"<Sphere radius='{f(0.62 - 0.1 * tier)}'/></Shape></Transform>"
        "</Transform></Transform>")
    ph = u; sw = 0.11 + 0.03 * tier
    keys = [0, 0.25, 0.5, 0.75, 1]; vals = [sw * math.sin(TAU * (k + ph)) for k in keys]
    add(f"<OrientationInterpolator DEF='OF{i}' key='0 0.25 0.5 0.75 1' keyValue='{' '.join('0 0 1 ' + f(x) for x in vals)}'/>"
        f"<ROUTE fromNode='T_fan' fromField='fraction_changed' toNode='OF{i}' toField='set_fraction'/><ROUTE fromNode='OF{i}' fromField='value_changed' toNode='F{i}' toField='set_rotation'/>")
add("</Transform></Transform>")
X.insert(1, "<TimeSensor DEF='T_fan' cycleInterval='6' loop='true'/>")
add("<OrientationInterpolator DEF='O_fan' key='0 0.5 1' keyValue='1 0 0 -0.1 1 0 0 0.14 1 0 0 -0.1'/>"
    "<ROUTE fromNode='T_fan' fromField='fraction_changed' toNode='O_fan' toField='set_fraction'/><ROUTE fromNode='O_fan' fromField='value_changed' toNode='FAN' toField='set_rotation'/>")
# two helices of sparks drawn into the heart
for k in range(2):
    pts, cols = [], []
    for j in range(700):
        t = j / 700; a = TAU * 7 * t + k * math.pi; r = 0.6 + 6.5 * (1 - t) ** 1.6
        pts.append((r * math.cos(a), 0.8 + 26 * t, r * math.sin(a))); c = DOMAINS[j % 9][1]; cols.append(tuple(0.5 + 0.5 * x for x in c))
    add(f"<Transform DEF='HELIX{k}'><Shape><Appearance><PointProperties pointSizeScaleFactor='3' pointSizeMinValue='1' pointSizeMaxValue='5'/></Appearance>"
        f"<PointSet><Coordinate point='{' '.join(v(p) for p in pts)}'/><Color color='{' '.join(v(c) for c in cols)}'/></PointSet></Shape></Transform>")
    spin(f"HELIX{k}", 11 + 6 * k, "0 1 0", -1 if k else 1)
add(f"<PointLight location='{v(CORE)}' color='1 0.8 0.55' intensity='1' radius='90' attenuation='1 0.02 0.001'/>")

# ---- nine flywheels and their belts ----------------------------------------------------------------
add("<TimeSensor DEF='T_pulse' cycleInterval='4.5' loop='true'/>")
views = []
for i, w in enumerate(data["wheels"]):
    a = TAU * i / 9 + TAU / 4; c = w["color"]; p = polar(R_RING, a, Y_WHEEL); name = f"W{i}"
    add(f"<Transform translation='{v(p)}' rotation='0 1 0 {f(math.pi / 2 - a)}'>")
    add(f"<TouchSensor DEF='TS{i}' description={quoteattr(w['name'])}/>")
    add(f"<Transform DEF='{name}'><Shape>" + mat(c, tuple(0.85 * x for x in c)) + torus(4.2, 0.42) + "</Shape>"
        "<Shape>" + mat((1, 1, 1), (0.9, 0.95, 1)) + torus(2.5, 0.08, 72, 8) + "</Shape><Shape>" + mat((1, 1, 1), (0.95, 0.97, 1)) + torus(4.78, 0.045, 96, 6) + "</Shape>"
        "<Transform rotation='1 0 0 1.5708'><Shape>" + mat(c, c, 0.82) + "<Cylinder radius='4.1' height='0.05'/></Shape></Transform>")
    for k in range(9):
        b = TAU * k / 9
        add(f"<Transform rotation='0 0 1 {f(b)}'><Transform translation='0 2.1 0'><Shape>" + mat((0.9, 0.95, 1), tuple(0.5 + 0.5 * x for x in c)) + "<Box size='0.08 4.1 0.08'/></Shape></Transform>"
            f"<Transform translation='0 4.2 0'><Shape>" + mat((1, 1, 1), (1, 1, 1)) + "<Sphere radius='0.32'/></Shape></Transform></Transform>")
    add("<Shape>" + mat(c, c) + "<Sphere radius='0.8'/></Shape></Transform>")
    pts = [(5.4 * math.cos(TAU * j / 160) * (1 + 0.05 * math.sin(j * 1.7)), 5.4 * math.sin(TAU * j / 160) * (1 + 0.05 * math.sin(j * 1.7)), 0.4 * math.sin(j * 0.9)) for j in range(160)]
    add(f"<Transform DEF='H{i}'><Shape><Appearance><PointProperties pointSizeScaleFactor='3' pointSizeMinValue='1' pointSizeMaxValue='5'/></Appearance>"
        f"<PointSet><Coordinate point='{' '.join(v(q) for q in pts)}'/><Color color='{' '.join(v(tuple(0.4 + 0.6 * x for x in c)) for _ in pts)}'/></PointSet></Shape></Transform>")
    add(f"<Transform translation='0 6.3 0'><Billboard axisOfRotation='0 0 0'><Shape><Appearance><Material diffuseColor='0 0 0' emissiveColor='{v(tuple(0.5 + 0.5 * x for x in c))}'/></Appearance>"
        f"<Text string={mfstring(w['name'].upper())}><FontStyle family='\"SANS\"' justify='\"MIDDLE\" \"MIDDLE\"' size='1.0' style='BOLD'/></Text></Shape></Billboard></Transform>")
    add("</Transform>")
    spin(name, w["period"]); spin(f"H{i}", w["period"] * 2.3, sign=-1)
    add(f"<Transform translation='{v((p[0], Y_WHEEL / 2 - 2.4, p[2]))}'><Shape>" + mat(c, c, 0.86) + f"<Cylinder radius='0.5' height='{f(Y_WHEEL - 4.6)}'/></Shape></Transform>")
    add(f"<Transform translation='{v((p[0], 0.25, p[2]))}'><Shape>" + mat((0.1, 0.12, 0.22), tuple(0.35 * x for x in c)) + "<Cylinder radius='2.4' height='0.5'/></Shape></Transform>")
    # belt: three strands of light from the wheel to the heart, and pulses that run inward
    ctrl = polar(R_RING * 0.5, a, 19.0)
    def bez(t, off=0.0):
        q = [(1 - t) ** 2 * p[j] + 2 * (1 - t) * t * ctrl[j] + t * t * CORE[j] for j in range(3)]
        s = math.sin(math.pi * t) * off
        return (q[0] - math.sin(a) * s, q[1] + 0.4 * s, q[2] + math.cos(a) * s)
    for off in (-0.9, 0, 0.9):
        line = [bez(j / 40, off) for j in range(41)]
        add(f"<Shape><Appearance><Material emissiveColor='{v(c)}' transparency='{f(0.25 if off == 0 else 0.6)}'/></Appearance>"
            f"<IndexedLineSet coordIndex='{' '.join(map(str, range(41)))} -1'><Coordinate point='{' '.join(v(q) for q in line)}'/></IndexedLineSet></Shape>")
    path = [bez(j / 24) for j in range(25)]
    for k in range(3):
        sh = (k * 8 + i * 3) % 24; seq = path[sh:] + path[1:sh + 1]
        keys = " ".join(f(j / 24) for j in range(25))
        add(f"<Transform DEF='PU{i}_{k}'><Shape>" + mat((1, 1, 1), tuple(0.6 + 0.4 * x for x in c)) + f"<Sphere radius='{f(0.24 + 0.14 * w['momentum'])}'/></Shape>"
            "<Shape>" + mat(c, c, 0.88) + f"<Sphere radius='{f(0.5 + 0.2 * w['momentum'])}'/></Shape></Transform>"
            f"<PositionInterpolator DEF='PI{i}_{k}' key='{keys}' keyValue='{' '.join(v(q) for q in seq)}'/>"
            f"<ROUTE fromNode='T_pulse' fromField='fraction_changed' toNode='PI{i}_{k}' toField='set_fraction'/><ROUTE fromNode='PI{i}_{k}' fromField='value_changed' toNode='PU{i}_{k}' toField='set_translation'/>")
    eye = polar(12.5, a + 0.25, 7.0); views.append((f"V{i}", w["name"], eye, (p[0], Y_WHEEL - 0.5, p[2])))


# ---- more spectacle --------------------------------------------------------------------------------
def drive(tname, period, target, field, keys, vals, kind="Scalar"):
    n = f"I_{target}_{field}"
    if f"DEF='{tname}'" not in "".join(X):
        add(f"<TimeSensor DEF='{tname}' cycleInterval='{f(period)}' loop='true'/>")
    add(f"<{kind}Interpolator DEF='{n}' key='{' '.join(f(k) for k in keys)}' keyValue='{vals}'/>"
        f"<ROUTE fromNode='{tname}' fromField='fraction_changed' toNode='{n}' toField='set_fraction'/>"
        f"<ROUTE fromNode='{n}' fromField='value_changed' toNode='{target}' toField='{field}'/>")
# shockwaves that leave the heart on every beat and cross the floor
for k in range(4):
    add(f"<Transform translation='0 0.35 0' rotation='1 0 0 1.5708'><Transform DEF='SW{k}'><Shape>" + mat((1, 0.85, 0.6), (1, 0.8, 0.5), 0.5, f"M_SW{k}") + torus(1, 0.012, 96, 6) + "</Shape></Transform></Transform>")
    ks = [0, 1]; ph = k / 4
    keys = sorted({0, 1, ph}); val = lambda t: 2 + 62 * ((t - ph) % 1)
    kk, vv, tt = [], [], []
    for t in [0, max(ph - 1e-3, 0), ph, 1]:
        kk.append(t); r = 2 + 62 * ((t - ph) % 1) if not (t == max(ph - 1e-3, 0) and ph > 0) else 64
        if t == 1 and ph == 0: r = 64
        vv.append(f"{f(r)} {f(r)} {f(r)}"); tt.append(f(min(1, 0.25 + 0.75 * (r - 2) / 62)))
    drive("T_shock", 6.0, f"SW{k}", "set_scale", kk, " ".join(vv), "Position")
    drive("T_shock", 6.0, f"M_SW{k}", "set_transparency", kk, " ".join(tt))
# a beam from the heart into the sky
for k, (r, t) in enumerate(((0.35, 0.3), (0.9, 0.72), (1.8, 0.88), (3.2, 0.95))):
    add(f"<Transform translation='0 70 0'><Shape>" + mat((1, 0.9, 0.7), (1, 0.85, 0.6), t, f"M_beam{k}") + f"<Cylinder radius='{r}' height='122' top='false' bottom='false'/></Shape></Transform>")
    drive("T_beat", 1.6, f"M_beam{k}", "set_transparency", [0, 0.08, 0.3, 1], f"{f(t)} {f(max(0, t - 0.3))} {f(t)} {f(t)}")
# the heart changes colour through the nine domains
cyc = [c for _, c in DOMAINS] + [DOMAINS[0][1]]
drive("T_hue", 27, "M_heart", "set_emissiveColor", [i / 9 for i in range(10)], " ".join(v(tuple(0.35 + 0.65 * x for x in c)) for c in cyc), "Color")
# an armillary around the whole plaza
for k, (R, ax, per, c) in enumerate(((39, "1 0 0.3", 46, (0.5, 0.7, 1)), (42, "0.4 0 1", 61, (1, 0.6, 0.85)), (45, "1 0 -0.6", 83, (1, 0.85, 0.5)))):
    add(f"<Transform translation='0 9 0'><Transform DEF='ARM{k}'><Shape>" + mat(c, c, 0.35) + torus(R, 0.09, 160, 5) + "</Shape>")
    pts = [(R * math.cos(TAU * j / 60), R * math.sin(TAU * j / 60), 0) for j in range(60)]
    add(f"<Shape><Appearance><PointProperties pointSizeScaleFactor='5' pointSizeMinValue='2' pointSizeMaxValue='8'/></Appearance><PointSet><Coordinate point='{' '.join(v(q) for q in pts)}'/>"
        f"<Color color='{' '.join(v((1, 1, 1)) for _ in pts)}'/></PointSet></Shape></Transform></Transform>")
    spin(f"ARM{k}", per, ax, 1 if k != 1 else -1)
# lightning between neighbouring wheels
lr = random.Random(4)
for i in range(9):
    a0, a1 = TAU * i / 9 + TAU / 4, TAU * (i + 1) / 9 + TAU / 4
    for var in range(2):
        pts = []
        for j in range(15):
            t = j / 14; a = a0 + (a1 - a0) * t; amp = math.sin(math.pi * t)
            q = polar(R_RING + lr.uniform(-1.6, 1.6) * amp, a, Y_WHEEL + lr.uniform(-2.2, 2.2) * amp)
            pts.append(q)
        c = tuple(0.5 * (DOMAINS[i][1][j] + DOMAINS[(i + 1) % 9][1][j]) + 0.35 for j in range(3))
        nm = f"M_L{i}_{var}"
        add(f"<Shape><Appearance><Material DEF='{nm}' emissiveColor='{v(tuple(min(1, x) for x in c))}' transparency='1'/><LineProperties linewidthScaleFactor='2'/></Appearance>"
            f"<IndexedLineSet coordIndex='{' '.join(map(str, range(15)))} -1'><Coordinate point='{' '.join(v(q) for q in pts)}'/></IndexedLineSet></Shape>")
        t0 = ((i * 0.37 + var * 0.5) % 1) * 0.9
        drive("T_bolt", 3.0, nm, "set_transparency", [0, t0, t0 + 0.012, t0 + 0.03, t0 + 0.045, t0 + 0.08, 1], "1 1 0 0.8 0 1 1")
# comet swarms on tilted orbits
for k in range(4):
    pts, cols = [], []
    for j in range(260):
        t = (j / 260) ** 2.2; a = TAU * 0.55 * t; R = 33 + 4 * k
        pts.append((R * math.cos(a), R * math.sin(a), lr.uniform(-0.25, 0.25) * (1 + 6 * t))); b = 1 - t; c = DOMAINS[(k * 2) % 9][1]
        cols.append(tuple(b * (0.5 + 0.5 * x) for x in c))
    add(f"<Transform translation='0 10 0' rotation='{('1 0 0', '0.3 0 1', '1 0 0.8', '0 0 1')[k]} {f(1.1 + 0.35 * k)}'><Transform DEF='COMET{k}'><Shape><Appearance><PointProperties pointSizeScaleFactor='4' pointSizeMinValue='1' pointSizeMaxValue='7'/></Appearance>"
        f"<PointSet><Coordinate point='{' '.join(v(q) for q in pts)}'/><Color color='{' '.join(v(c) for c in cols)}'/></PointSet></Shape></Transform></Transform>")
    spin(f"COMET{k}", 9 + 3.5 * k, sign=-1 if k % 2 else 1)

# ---- the tour: one slow flight, 96 seconds ----------------------------------------------------------
N = 72; keys, pos, ori = [], [], []
for k in range(N + 1):
    t = k / N; a = TAU * t * 1.0 + 1.2; r = 52 + 11 * math.sin(TAU * t * 2) - 6 * math.sin(TAU * t * 3 + 1)
    y = 15 + 10 * math.sin(TAU * t * 2 + 0.6); eye = polar(max(r, 39), a, max(y, 3.5))
    keys.append(f(t)); pos.append(v(eye)); ori.append(" ".join(f(c) for c in look_at(eye, (0, 9 + 2 * math.sin(TAU * t * 3), 0))))
vp = [f"<Viewpoint DEF='V_tour' description='The tour' position='{pos[0]}' orientation='{ori[0]}' fieldOfView='0.8' centerOfRotation='0 9 0'/>",
      f"<TimeSensor DEF='T_tour' cycleInterval='90' loop='true'/><PositionInterpolator DEF='P_tour' key='{' '.join(keys)}' keyValue='{' '.join(pos)}'/>"
      f"<OrientationInterpolator DEF='O_tour' key='{' '.join(keys)}' keyValue='{' '.join(ori)}'/>"
      "<ROUTE fromNode='T_tour' fromField='fraction_changed' toNode='P_tour' toField='set_fraction'/><ROUTE fromNode='T_tour' fromField='fraction_changed' toNode='O_tour' toField='set_fraction'/>"
      "<ROUTE fromNode='P_tour' fromField='value_changed' toNode='V_tour' toField='set_position'/><ROUTE fromNode='O_tour' fromField='value_changed' toNode='V_tour' toField='set_orientation'/>",
      f"<Viewpoint DEF='V_front' description='Before the fan' position='0 6 21' orientation='{' '.join(f(c) for c in look_at((0, 6, 21), (0, 13.5, 0)))}' centerOfRotation='0 9 0'/>",
      f"<Viewpoint DEF='V_above' description='From above' position='0 78 1' orientation='{' '.join(f(c) for c in look_at((0, 78, 1), (0, 0, 0)))}' centerOfRotation='0 9 0'/>"]
for name, desc, eye, tgt in views:
    vp.append(f"<Viewpoint DEF='{name}' description={quoteattr(desc)} position='{v(eye)}' orientation='{' '.join(f(c) for c in look_at(eye, tgt))}' centerOfRotation='{v(tgt)}'/>")
head = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 4.0//EN" "https://www.web3d.org/specifications/x3d-4.0.dtd">
<X3D profile='Immersive' version='4.0' xmlns:xsd='http://www.w3.org/2001/XMLSchema-instance' xsd:noNamespaceSchemaLocation='https://www.web3d.org/specifications/x3d-4.0.xsd'>
<head><component name='Shaders' level='1'/><component name='Shape' level='5'/>
<meta name='title' content='Gobbler.flyte Mission Control'/>
<meta name='description' content='An art piece: nine flywheels feeding one fan of light. Every figure is synthetic.'/>
<meta name='generator' content='build.py'/></head>
<Scene>
<WorldInfo title='Gobbler.flyte Mission Control' info='"An art piece" "Every figure is synthetic"'/>
<NavigationInfo type='"EXAMINE" "FLY" "ANY"' speed='12' headlight='true' transitionType='"LINEAR"' transitionTime='2.5'/>
<Background skyColor='0.01 0.01 0.04'/>
"""
(HERE / "scene.x3d").write_text(head + "\n".join(vp) + "\n" + "\n".join(X) + "\n</Scene>\n</X3D>\n", encoding="utf-8")
data["views"] = [["V_tour", "The tour"], ["V_front", "Before the fan"], ["V_above", "From above"]] + [[n, d] for n, d, _, _ in views]
(HERE / "data.json").write_text(json.dumps(data, indent=1) + "\n")
print("scene.x3d", (HERE / "scene.x3d").stat().st_size, "bytes")
