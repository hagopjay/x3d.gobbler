#!/usr/bin/env python3
"""Build the Gobbler mascot scenes from data. Standard library only; every vertex is computed, nothing is drawn by hand.

    python3 mascot/build_mascot.py v5 --board frontier/runs/<run>/board.json --out mascot/v5/gobbler-v5.x3d
    python3 mascot/build_mascot.py v6 --board ... --genome mascot/v6/elites.json --cell 4 --out mascot/v6/gobbler-v6.x3d

v5 "Loomwright": a solid faceted bird whose tail fan is the frontier board. One feather per frontier: length is the
balanced score, colour is the family, the gem at the tip is the worst Assayer check, beads on the shaft count the
checks passed. The ring under its feet carries one stud per Atlas thesis.

v6 "Demiurge": the same data on a body woven from 44 warp ribbons (one per Loom law) around a visible heart, with
the fan's shape taken from a genome (spread, curl, twist, taper, tiers, length profile) that `evolve.py` breeds.

Look: solid low-poly facets with a cosmic surround (lattice, stars, three coloured lights on sine paths).
Profile Immersive plus Shape:5 for PointProperties; no PhysicalMaterial, no Script, no remote URL.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

FAMILY_RGB = {"A": (0.25, 0.85, 0.95), "G": (0.95, 0.35, 0.80), "E": (0.98, 0.72, 0.20), "S": (0.95, 0.22, 0.20), "D": (0.35, 0.90, 0.50)}
WORST_RGB = {"pass": (1.0, 0.84, 0.30), "note": (0.85, 0.85, 0.9), "warn": (1.0, 0.55, 0.10), "gate": (0.30, 0.55, 1.0), "stop": (1.0, 0.10, 0.10)}
FAMILY_ORDER = "GADES"      # the largest family (domain) stands in the middle of the fan
DEFAULT_GENOME = {"spread": 200.0, "curl": 0.0, "twist": 0.0, "taper": 0.6, "tiers": 1, "profile": 1.0, "width": 0.46, "tilt": 12.0}
GENE_RANGE = {"spread": (110.0, 250.0), "curl": (-0.35, 0.9), "twist": (-1.2, 1.2), "taper": (0.3, 1.2), "tiers": (1, 3),
              "profile": (0.5, 2.2), "width": (0.25, 0.75), "tilt": (0.0, 30.0)}
PIVOT = (0.0, 3.5, -1.5)


def f(x: float) -> str:
    s = f"{x:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def v3(p) -> str:
    return " ".join(f(c) for c in p)


def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def norm(a):
    n = math.sqrt(sum(c * c for c in a)) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


def look_at(eye, target):
    """Viewpoint orientation (axis, angle) that looks from eye to target with +Y up."""
    fw = norm(sub(target, eye)); r = norm(cross(fw, (0, 1, 0))); u = cross(r, fw)
    m = [[r[0], u[0], -fw[0]], [r[1], u[1], -fw[1]], [r[2], u[2], -fw[2]]]
    tr = m[0][0] + m[1][1] + m[2][2]
    ang = math.acos(max(-1.0, min(1.0, (tr - 1) / 2)))
    if ang < 1e-6: return (0, 1, 0, 0)
    raw = (m[2][1] - m[1][2], m[0][2] - m[2][0], m[1][0] - m[0][1])
    if math.sqrt(sum(c * c for c in raw)) < 1e-6:
        # A half turn: the antisymmetric part vanishes, so take the axis from the diagonal. Without this branch
        # a camera looking straight back down +Z was written as '0 0 0 3.142' (caught by x3d_mcp rotation-zero-axis).
        ax = norm(tuple(math.sqrt(max(0.0, (m[i][i] + 1) / 2)) for i in range(3)))
        return (*ax, math.pi)
    return (*norm(raw), ang)


class Mesh:
    """Faces with one colour each, written as a single flat-shaded IndexedFaceSet."""
    def __init__(self): self.p, self.faces, self.cols = [], [], []
    def face(self, pts, col):
        i = len(self.p); self.p += pts; self.faces.append(list(range(i, i + len(pts)))); self.cols.append(col)
    def x3d(self, *, emissive=(0, 0, 0), solid=True, spec=0.25, shin=0.3, transparency=0.0, name=None) -> str:
        if not self.faces: return ""
        tag = f"<Shape DEF='{name}'>" if name else "<Shape>"
        idx = " ".join(" ".join(map(str, fc)) + " -1" for fc in self.faces)
        return (f"{tag}<Appearance><Material diffuseColor='0.6 0.6 0.6' specularColor='{v3((spec,) * 3)}' shininess='{f(shin)}' "
                f"emissiveColor='{v3(emissive)}' transparency='{f(transparency)}'/></Appearance>"
                f"<IndexedFaceSet solid='{'true' if solid else 'false'}' creaseAngle='0' colorPerVertex='false' coordIndex='{idx}'>"
                f"<Coordinate point='{' '.join(v3(p) for p in self.p)}'/><Color color='{' '.join(v3(c) for c in self.cols)}'/></IndexedFaceSet></Shape>\n")


def icosphere(level: int):
    t = (1 + 5 ** .5) / 2
    V = [norm(p) for p in [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]]
    F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
         (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    for _ in range(level):
        cache, F2 = {}, []
        def mid(a, b):
            k = (min(a, b), max(a, b))
            if k not in cache:
                V.append(norm(mul(add(V[a], V[b]), .5))); cache[k] = len(V) - 1
            return cache[k]
        for a, b, c in F:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            F2 += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        F = F2
    return V, F


def blob(mesh: Mesh, centre, radii, level, palette, rng, jitter=0.06):
    V, F = icosphere(level)
    P = [add(centre, (v[0] * radii[0] * (1 + rng.uniform(-jitter, jitter)), v[1] * radii[1] * (1 + rng.uniform(-jitter, jitter)),
                      v[2] * radii[2] * (1 + rng.uniform(-jitter, jitter)))) for v in V]
    for a, b, c in F:
        base = rng.choice(palette); k = rng.uniform(0.75, 1.15)
        mesh.face([P[a], P[b], P[c]], tuple(min(1.0, ch * k) for ch in base))


def octa(mesh: Mesh, c, r, col):
    P = [add(c, d) for d in [(r, 0, 0), (-r, 0, 0), (0, r, 0), (0, -r, 0), (0, 0, r), (0, 0, -r)]]
    for a, b, d in [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]:
        mesh.face([P[a], P[b], P[d]], col)


def feather_frames(angle_deg, length, g, tier=0, n=7):
    """Centre line and half-width vectors of one feather, in world space. Returns [(centre, side, t)]."""
    a = math.radians(angle_deg); tilt = math.radians(g["tilt"] + 9 * tier)
    d = (math.sin(a), math.cos(a) * math.cos(tilt), -math.cos(a) * math.sin(tilt))      # along the shaft
    back = norm((0.0, -math.sin(tilt), -math.cos(tilt)))                                  # fan normal, pointing aft
    side0 = norm(cross(d, back))
    r0 = 1.15 + 0.25 * tier
    out = []
    for i in range(n + 1):
        t = i / n
        c = add(PIVOT, add(mul(d, r0 + t * length), mul(back, g["curl"] * t * t * length - 0.18 * tier)))
        tw = g["twist"] * t
        side = add(mul(side0, math.cos(tw)), mul(back, math.sin(tw)))
        w = g["width"] * (math.sin(math.pi * min(1.0, t * 0.92 + 0.04)) ** g["taper"]) * (0.55 + 0.45 * length / 8.0)
        out.append((c, mul(side, w), t))
    return out, back


def fan_layout(rows: list[dict], g: dict):
    """Feather angle, length and tier for every board row. Sorted by family, then by score, so the fan reads as sectors."""
    order = []
    for fam in FAMILY_ORDER:                       # each family is one scallop: its best frontier stands in the middle
        best = sorted((r for r in rows if r["family"] == fam), key=lambda r: (-r["score"], r["id"]))
        order += best[1::2][::-1] + best[0::2]
    lo, hi = min(r["score"] for r in rows), max(r["score"] for r in rows)
    tiers = int(g["tiers"]); out = []
    for i, r in enumerate(order):
        tier = i % tiers
        u = (i + 0.5) / len(order)
        s = ((r["score"] - lo) / (hi - lo)) if hi > lo else 1.0
        length = (3.2 + 5.6 * s ** g["profile"]) * (1 - 0.16 * tier)
        out.append({"row": r, "angle": (u - 0.5) * g["spread"], "length": length, "tier": tier})
    return out


def build_fan(rows, g, with_beads=True):
    vane, shaft, beads, gems, samples = Mesh(), Mesh(), Mesh(), [], []
    for ft in fan_layout(rows, g):
        r = ft["row"]; col = FAMILY_RGB[r["family"]]
        frames, back = feather_frames(ft["angle"], ft["length"], g, ft["tier"])
        lift = mul(back, -0.05)
        for (c0, s0, t0), (c1, s1, t1) in zip(frames, frames[1:]):
            k0 = 0.45 + 0.55 * t0
            left = tuple(min(1, ch * k0) for ch in col); right = tuple(min(1, ch * k0 * 0.62) for ch in col)
            m0, m1 = add(c0, lift), add(c1, lift)
            vane.face([sub(c0, s0), m0, m1, sub(c1, s1)], left)
            vane.face([m0, add(c0, s0), add(c1, s1), m1], right)
            q = 0.035
            shaft.face([add(m0, (q, 0, 0.02)), add(m1, (q, 0, 0.02)), add(m1, (-q, 0, 0.02)), add(m0, (-q, 0, 0.02))], (0.95, 0.9, 0.75))
            samples.append((add(mul(add(c0, c1), .5), mul(s0, .5)), r["id"])); samples.append((sub(mul(add(c0, c1), .5), mul(s0, .5)), r["id"]))
        tip = frames[-1][0]
        gems.append((add(tip, mul(back, -0.08)), WORST_RGB[r["assay"]["worst"]], 0.11 + 0.012 * r["assay"]["passed"], r["id"]))
        if with_beads:
            for k in range(r["assay"]["passed"]):
                c = frames[1][0]; e = frames[-2][0]; u = (k + 1) / 11
                octa(beads, add(add(c, mul(sub(e, c), u)), mul(back, -0.12)), 0.045, (1.0, 0.93, 0.7))
    return vane, shaft, beads, gems, samples


def ring(mesh, centre, radius, width, n, col, y_thick=0.06):
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        pts = []
        for a, r in ((a0, radius - width), (a0, radius + width), (a1, radius + width), (a1, radius - width)):
            pts.append(add(centre, (r * math.cos(a), y_thick, r * math.sin(a))))
        mesh.face(pts[::-1], tuple(ch * (0.8 + 0.2 * (i % 2)) for ch in col))


def head_and_neck(mesh, rng, palette):
    pts = [(0, 4.3, 1.5), (0, 5.0, 2.0), (0, 5.8, 2.2), (0, 6.5, 2.35)]
    for i, p in enumerate(pts):
        r = 0.62 - 0.11 * i
        blob(mesh, p, (r, r * 1.25, r), 1, palette, rng)
    blob(mesh, (0, 7.1, 2.55), (0.50, 0.52, 0.58), 1, [(0.42, 0.52, 0.70), (0.30, 0.40, 0.62), (0.55, 0.36, 0.42)], rng, 0.03)
    return (0, 7.1, 2.55)


def beak_wattle(head):
    m = Mesh(); hx, hy, hz = head
    tip = (0, hy - 0.12, hz + 1.05); b = [(-0.17, hy + 0.10, hz + 0.45), (0.17, hy + 0.10, hz + 0.45), (0.14, hy - 0.16, hz + 0.42), (-0.14, hy - 0.16, hz + 0.42)]
    for i in range(4): m.face([b[i], b[(i + 1) % 4], tip][::-1], (0.98, 0.78 - 0.08 * (i % 2), 0.22))
    w = Mesh(); rng = random.Random(3)
    blob(w, (0, hy - 0.62, hz + 0.38), (0.16, 0.42, 0.16), 1, [(0.90, 0.10, 0.12), (0.70, 0.05, 0.10)], rng, 0.05)   # wattle
    blob(w, (0.0, hy + 0.05, hz + 0.72), (0.07, 0.07, 0.30), 0, [(0.95, 0.15, 0.15)], rng, 0.0)                    # snood
    return m, w


def legs():
    m = Mesh()
    for sx in (-0.55, 0.55):
        top, foot = (sx, 2.2, 0.15), (sx, 0.12, 0.35)
        for i in range(4):
            a0, a1 = math.pi / 2 * i, math.pi / 2 * (i + 1); r = 0.09
            m.face([add(top, (r * math.cos(a0), 0, r * math.sin(a0))), add(foot, (r * math.cos(a0), 0, r * math.sin(a0))),
                    add(foot, (r * math.cos(a1), 0, r * math.sin(a1))), add(top, (r * math.cos(a1), 0, r * math.sin(a1)))], (0.85, 0.62, 0.22))
        for dx, dz in ((-0.38, 0.75), (0, 0.95), (0.38, 0.75), (0, -0.35)):
            tip = add(foot, (dx, -0.06, dz))
            m.face([add(foot, (-0.07, 0.05, 0)), add(foot, (0.07, 0.05, 0)), tip], (0.95, 0.72, 0.25))
            m.face([add(foot, (0.07, 0.05, 0)), add(foot, (-0.07, 0.05, 0)), tip], (0.75, 0.52, 0.18))
    return m


def warp_body(n_warp=44, n_weft=13):
    """v6: the body as a loom. 44 warp ribbons run nose to tail over an ellipsoid; 13 weft rings cross them."""
    m = Mesh(); c = (0, 3.3, 0.1); R = (1.75, 1.55, 2.3)
    def pt(u, a, k=1.0):                       # u along the body 0..1, a around it
        th = math.pi * (0.06 + 0.88 * u)
        return add(c, (R[0] * k * math.sin(th) * math.cos(a), R[1] * k * math.sin(th) * math.sin(a), R[2] * k * math.cos(th)))
    for i in range(n_warp):
        a = 2 * math.pi * i / n_warp; da = 0.022
        col = (1.0, 0.80, 0.30) if i % 2 else (0.95, 0.55, 0.18)
        for s in range(18):
            u0, u1 = s / 18, (s + 1) / 18
            m.face([pt(u0, a - da), pt(u0, a + da), pt(u1, a + da), pt(u1, a - da)], tuple(ch * (0.6 + 0.4 * math.sin(math.pi * u0)) for ch in col))
    for j in range(n_weft):
        u = (j + 1) / (n_weft + 1); du = 0.006
        for s in range(44):
            a0, a1 = 2 * math.pi * s / 44, 2 * math.pi * (s + 1) / 44
            m.face([pt(u - du, a0, 1.02), pt(u + du, a0, 1.02), pt(u + du, a1, 1.02), pt(u - du, a1, 1.02)], (0.35, 0.75, 1.0))
    return m


def halo(n: int) -> Mesh:
    """One bead per Loom failure mode, laid as three spiral arms on the floor around the wheel: oldest inside, gold;
    newest outside, cyan. The count is read from the Loom (loom_counts.py), so the spiral grows with it."""
    m = Mesh()
    for i in range(n):
        t = i / max(1, n - 1); arm = i % 3
        r = 4.7 + 6.3 * t; a = 2 * math.pi * (arm / 3 + 1.15 * t)
        col = (1.0 - 0.75 * t, 0.80 + 0.05 * t, 0.30 + 0.70 * t)
        octa(m, (r * math.cos(a), 0.16 + 0.05 * (i % 2), 0.2 + r * math.sin(a)), 0.085 + 0.03 * (i % 5 == 0), col)
    return m


def lattice(radius=15.0, centre=(0, 6, 0)):
    V, F = icosphere(1); edges = set()
    for a, b, c in F:
        for e in ((a, b), (b, c), (c, a)): edges.add((min(e), max(e)))
    pts = " ".join(v3(add(centre, mul(v, radius))) for v in V)
    idx = " ".join(f"{a} {b} -1" for a, b in sorted(edges))
    return (f"<Shape><Appearance><LineProperties linewidthScaleFactor='1.5'/><Material emissiveColor='0.25 0.45 0.9' diffuseColor='0 0 0' transparency='0.55'/></Appearance>"
            f"<IndexedLineSet coordIndex='{idx}'><Coordinate point='{pts}'/></IndexedLineSet></Shape>\n"), len(edges)


def stars(rng, n=1800):
    out = ""
    for size, share in ((1.4, 0.7), (2.4, 0.25), (3.4, 0.05)):
        pts, cols = [], []
        for _ in range(int(n * share)):
            z = rng.uniform(-1, 1); a = rng.uniform(0, 2 * math.pi); r = (1 - z * z) ** .5
            pts.append((90 * r * math.cos(a), 90 * z + 6, 90 * r * math.sin(a)))
            k = rng.uniform(0.5, 1.0); cols.append(rng.choice([(k, k, k), (k, k * .8, k * .55), (k * .6, k * .75, k), (k, k * .5, k * .8)]))
        out += (f"<Shape><Appearance><PointProperties pointSizeScaleFactor='{size}' pointSizeMinValue='1' pointSizeMaxValue='4'/></Appearance><PointSet>"
                f"<Coordinate point='{' '.join(v3(p) for p in pts)}'/><Color color='{' '.join(v3(c) for c in cols)}'/></PointSet></Shape>\n")
    return out


def sine_light(name, col, centre, amp, period, phase):
    keys = [i / 24 for i in range(25)]
    vals = [add(centre, (amp[0] * math.sin(2 * math.pi * k + phase), amp[1] * math.sin(4 * math.pi * k + phase), amp[2] * math.cos(2 * math.pi * k + phase))) for k in keys]
    return (f"<PointLight DEF='L_{name}' color='{v3(col)}' intensity='0.9' radius='60' attenuation='1 0.02 0.002' location='{v3(vals[0])}'/>"
            f"<Transform DEF='B_{name}' translation='{v3(vals[0])}'><Shape><Appearance><Material diffuseColor='0 0 0' emissiveColor='{v3(col)}'/></Appearance><Sphere radius='0.16'/></Shape></Transform>"
            f"<TimeSensor DEF='T_{name}' cycleInterval='{period}' loop='true'/><PositionInterpolator DEF='P_{name}' key='{' '.join(f(k) for k in keys)}' keyValue='{' '.join(v3(p) for p in vals)}'/>"
            f"<ROUTE fromNode='T_{name}' fromField='fraction_changed' toNode='P_{name}' toField='set_fraction'/>"
            f"<ROUTE fromNode='P_{name}' fromField='value_changed' toNode='L_{name}' toField='set_location'/>"
            f"<ROUTE fromNode='P_{name}' fromField='value_changed' toNode='B_{name}' toField='set_translation'/>\n")


def build(version: str, board: dict, genome: dict, seed: int = 5, counts: dict | None = None) -> tuple[str, dict]:
    """version 'glass' is the v6 bird with translucent vanes, named shapes for a Blender pass, and a body and a
    failure-mode spiral sized by `counts` (laws, theses, failure_modes) instead of typed numbers."""
    rng = random.Random(seed)
    glass = version == "glass"
    nm = (lambda n: n) if glass else (lambda n: None)
    counts = counts or {"laws": 44, "theses": len(board["theses"]), "failure_modes": 0}
    rows = board["rows"]; g = dict(DEFAULT_GENOME, **genome)
    vane, shaft, beads, gems, _ = build_fan(rows, g)
    title = {"v5": "Gobbler 5, the Loomwright", "v6": "Gobbler 6, the Demiurge", "glass": "Gobbler 6.1, the Glass Demiurge"}[version]
    t = board["score_tuple"]
    S = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE X3D PUBLIC \"ISO//Web3D//DTD X3D 4.0//EN\" \"https://www.web3d.org/specifications/x3d-4.0.dtd\">\n"
         "<X3D profile='Immersive' version='4.0' xmlns:xsd='http://www.w3.org/2001/XMLSchema-instance' xsd:noNamespaceSchemaLocation='https://www.web3d.org/specifications/x3d-4.0.xsd'>\n"
         "<head><component name='Shape' level='5'/>\n"
         f"<meta name='title' content='{title}'/>\n"
         f"<meta name='description' content='Mascot draft. The tail fan is the Loom frontier board: one feather per frontier, {len(rows)} in all. Ranks are one model&apos;s opinion, graded Suspected.'/>\n"
         f"<meta name='generator' content='mascot/build_mascot.py'/>\n<meta name='reference' content='board registry sha256 {t['registry_sha256'][:16]}, atlas rev {t['atlas_rev']}'/>\n</head>\n<Scene>\n"
         f"<WorldInfo title='{title}' info='\"feather length = balanced score\" \"feather colour = family\" \"tip gem = worst Assayer check\" \"beads = checks passed\"'/>\n"
         "<NavigationInfo type='\"EXAMINE\" \"FLY\" \"ANY\"' headlight='true' speed='6' transitionType='\"LINEAR\"' transitionTime='2'/>\n"
         "<Background skyColor='0 0 0.015 0.03 0.012 0.07 0.10 0.03 0.09' skyAngle='1.25 1.75' groundColor='0.02 0.01 0.04 0.10 0.03 0.09' groundAngle='1.4'/>\n"]
    seats = (("Face", "Face", (0, 6.6, 16.5), (0, 6.9, 0)), ("Wide", "Wide", (7, 8, 22.5), (0, 6.9, 0)),
                                 ("Fan", "The fan, from behind", (0, 8.5, -26), (0, 7.5, 0)), ("Heart", "The heart", (5.5, 4.2, 7.5), (0, 3.4, 0.4)),
                                 ("Above", "From above", (0, 34, 6), (0, 4, -1)))
    if glass:   # two more seats for the Blender pass: the whole fan with room to breathe, and a low seat over the mirror floor
        seats += (("Hero", "The whole bird", (0, 7.6, 22.5), (0, 7.2, 0)), ("Low", "Low, over the floor", (-7.5, 1.6, 15.5), (0, 6.4, 0)))
    for name, desc, eye, tgt in seats:
        S.append(f"<Viewpoint DEF='V_{name}' description='{desc}' position='{v3(eye)}' orientation='{' '.join(f(c) for c in look_at(eye, tgt))}' centerOfRotation='0 6 0' fieldOfView='0.72'/>\n")
    palette = [(0.36, 0.25, 0.16), (0.22, 0.20, 0.26), (0.48, 0.33, 0.14), (0.16, 0.30, 0.34), (0.30, 0.18, 0.30)]
    body = Mesh()
    if version == "v5":
        blob(body, (0, 3.3, 0.1), (1.75, 1.55, 2.3), 2, palette, rng)
        for sx in (-1, 1):
            blob(body, (sx * 1.55, 3.45, -0.1), (0.5, 1.05, 1.75), 1, [(0.30, 0.22, 0.30), (0.20, 0.28, 0.36), (0.42, 0.28, 0.14)], rng)
    head = head_and_neck(body, rng, palette)
    S.append("<Transform>\n" + body.x3d(spec=0.35, shin=0.45, name=nm("Body")))
    woven = version in ("v6", "glass")
    if version == "v6":
        S.append(warp_body().x3d(emissive=(0.22, 0.14, 0.03), solid=False, spec=0.5, shin=0.6))
    if glass:
        S.append(warp_body(counts["laws"], counts["theses"]).x3d(emissive=(0.22, 0.14, 0.03), solid=False, spec=0.5, shin=0.6, name="Loom"))
    beak, wattle = beak_wattle(head)
    S.append(beak.x3d(emissive=(0.25, 0.16, 0.02), name=nm("Beak")) + wattle.x3d(emissive=(0.25, 0.0, 0.0), name=nm("Wattle")) + legs().x3d(solid=False, name=nm("Legs")))
    for sx in (-0.26, 0.26):
        S.append(f"<Transform translation='{f(sx)} {f(head[1] + 0.12)} {f(head[2] + 0.42)}'><Shape><Appearance><Material diffuseColor='0 0 0' emissiveColor='1 0.9 0.5'/></Appearance><Sphere radius='0.085'/></Shape></Transform>\n")
    heart_r = 0.62 if woven else 0.34
    heart_pos = (0, 3.3, 0.1) if woven else (0, 3.55, 2.32)
    S.append(f"<Transform DEF='Heart' translation='{v3(heart_pos)}'><Shape><Appearance><Material diffuseColor='0 0 0' emissiveColor='1 0.78 0.25'/></Appearance><Sphere radius='{f(heart_r)}'/></Shape></Transform>\n"
             f"<PointLight color='1 0.75 0.35' intensity='0.8' radius='30' attenuation='1 0.05 0.01' location='{v3(add(heart_pos, (0, 0, 0.6 if version == 'v5' else 0)))}'/>\n"
             "<TimeSensor DEF='T_beat' cycleInterval='1.6' loop='true'/><PositionInterpolator DEF='P_beat' key='0 0.12 0.24 0.4 1' keyValue='1 1 1 1.28 1.28 1.28 1 1 1 1.14 1.14 1.14 1 1 1'/>\n"
             "<ROUTE fromNode='T_beat' fromField='fraction_changed' toNode='P_beat' toField='set_fraction'/><ROUTE fromNode='P_beat' fromField='value_changed' toNode='Heart' toField='set_scale'/>\n")
    S.append(f"<Transform DEF='Fan' center='{v3(PIVOT)}'>\n" + vane.x3d(emissive=(0.05, 0.05, 0.05), solid=False, spec=0.4, shin=0.5, transparency=0.45 if glass else 0.0, name=nm("Vanes"))
             + shaft.x3d(emissive=(0.3, 0.27, 0.2), solid=False, name=nm("Shafts")) + beads.x3d(emissive=(0.5, 0.42, 0.2), name=nm("Beads")))
    for p, col, r, _id in gems:
        gem_tag = f"<Shape DEF='Gem_{_id.replace('-', '_')}'>" if glass else "<Shape>"
        S.append(f"<Transform translation='{v3(p)}'>{gem_tag}<Appearance><Material diffuseColor='{v3(mul(col, 0.4))}' emissiveColor='{v3(col)}'/></Appearance><Sphere radius='{f(r)}'/></Shape></Transform>\n")
    S.append("</Transform>\n<TimeSensor DEF='T_fan' cycleInterval='9' loop='true'/><OrientationInterpolator DEF='O_fan' key='0 0.25 0.5 0.75 1' keyValue='0 0 1 0 0 0 1 0.035 0 0 1 0 0 0 1 -0.035 0 0 1 0'/>\n"
             "<ROUTE fromNode='T_fan' fromField='fraction_changed' toNode='O_fan' toField='set_fraction'/><ROUTE fromNode='O_fan' fromField='value_changed' toNode='Fan' toField='set_rotation'/>\n</Transform>\n")
    wheel = Mesh(); ring(wheel, (0, 0, 0.2), 3.6, 0.28, 52, (0.75, 0.55, 0.18)); ring(wheel, (0, -0.02, 0.2), 2.2, 0.08, 40, (0.3, 0.6, 0.9))
    n_theses = len(board["theses"])
    for i in range(n_theses):
        a = 2 * math.pi * i / n_theses
        octa(wheel, (3.6 * math.cos(a), 0.3, 0.2 + 3.6 * math.sin(a)), 0.2, (1.0, 0.85, 0.35))
    spiral = halo(counts["failure_modes"]) if glass else Mesh()
    S.append(spiral.x3d(emissive=(0.35, 0.3, 0.2), name="FailureModes"))
    S.append("<Transform DEF='Wheel' center='0 0 0.2'>\n" + wheel.x3d(emissive=(0.2, 0.15, 0.05), solid=False, name=nm("WheelRing")) + "</Transform>\n"
             "<TimeSensor DEF='T_wheel' cycleInterval='40' loop='true'/><OrientationInterpolator DEF='O_wheel' key='0 0.25 0.5 0.75 1' keyValue='0 1 0 0 0 1 0 1.5708 0 1 0 3.1416 0 1 0 4.7124 0 1 0 6.2832'/>\n"
             "<ROUTE fromNode='T_wheel' fromField='fraction_changed' toNode='O_wheel' toField='set_fraction'/><ROUTE fromNode='O_wheel' fromField='value_changed' toNode='Wheel' toField='set_rotation'/>\n")
    lat, n_edges = lattice()
    S.append("<Transform DEF='Lattice' center='0 6 0'>\n" + lat + "</Transform>\n"
             "<TimeSensor DEF='T_lat' cycleInterval='120' loop='true'/><OrientationInterpolator DEF='O_lat' key='0 0.25 0.5 0.75 1' keyValue='0.3 1 0.1 0 0.3 1 0.1 1.5708 0.3 1 0.1 3.1416 0.3 1 0.1 4.7124 0.3 1 0.1 6.2832'/>\n"
             "<ROUTE fromNode='T_lat' fromField='fraction_changed' toNode='O_lat' toField='set_fraction'/><ROUTE fromNode='O_lat' fromField='value_changed' toNode='Lattice' toField='set_rotation'/>\n")
    S.append(stars(rng))
    S.append(sine_light("red", (1.0, 0.25, 0.2), (0, 7, 4), (9, 3, 6), 17, 0.0) + sine_light("blue", (0.25, 0.5, 1.0), (0, 8, 2), (10, 4, 7), 23, 2.1)
             + sine_light("gold", (1.0, 0.8, 0.3), (0, 5, 5), (7, 2.5, 5), 13, 4.2))
    S.append("</Scene>\n</X3D>\n")
    x = "".join(S)
    facts = {"version": version, "title": title, "feathers": len(rows), "beads": len(beads.faces) // 8, "gems": len(gems),
             "faces": sum(len(m.faces) for m in (body, vane, shaft, beads, wheel, beak, wattle)), "lattice_edges": n_edges,
             "thesis_studs": n_theses, "genome": g, "bytes": len(x.encode())}
    if glass:
        facts.update(warp_ribbons=counts["laws"], weft_rings=counts["theses"], failure_mode_beads=len(spiral.faces) // 8, counts=counts)
    return x, facts


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("version", choices=["v5", "v6", "glass"])
    ap.add_argument("--counts", type=Path, help="loom_counts.py output (glass only)")
    ap.add_argument("--board", type=Path, required=True)
    ap.add_argument("--genome", type=Path); ap.add_argument("--cell", type=int, default=0)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    board = json.loads(a.board.read_text(encoding="utf-8"))
    genome = {}
    if a.genome:
        genome = json.loads(a.genome.read_text(encoding="utf-8"))["elites"][a.cell]["genome"]
    counts = json.loads(a.counts.read_text(encoding="utf-8")) if a.counts else None
    x, facts = build(a.version, board, genome, counts=counts)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(x, encoding="utf-8")
    a.out.with_suffix(".facts.json").write_text(json.dumps(facts, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(facts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
