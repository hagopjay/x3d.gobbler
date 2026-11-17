#!/usr/bin/env python3
"""Fly the Atlas: out/atlas.json -> out/atlas-world.x3d and out/atlas-panel.json.

A walkable X3D 4.0 scene of the graph, with no Script node. Standard library only, no clock.

  centre          a mast with one ring per X_ITE version, and a thread to every number that stands on it
  courtyard       failure modes tied to no law, loose, sorted by class K1 to K11
  ring of laws    44 columns by theme; height grows with linked failure modes; teal has a mechanical check,
                  amber has review only; white collars count the diagnostics; a path of stones leads to each
  arms            23 chapters; numbers on the ground (green C, amber L, pink S; small when the instrument is 'same';
                  a gold plate when a ledger quote is verified), heuristics on a shelf above (faint when their
                  evidence cites no id), drills on top (red when not run)
  lines           tethers where one row cites another by id; gold threads from quoted numbers to their pins

Every item has a TouchSensor whose description names it; atlas-panel.json holds the 'how do we know' answer for each.
"""
import collections
import hashlib
import json
import math
import os
import pathlib
import re
import sys
from xml.sax.saxutils import quoteattr

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(os.environ.get("ATLAS_OUT", HERE / "out"))   # ATLAS_OUT: write a replay beside the archived out/
sys.path.insert(0, str(HERE))
import atlas as Q  # noqa: E402

R_COURT0, R_COURT1 = 5.5, 15.0
R_LAW = 30.0
R_GATE, R_ARM = 38.0, 40.5
R_GROUND = 76.0
WIDE, STEP_R, STEP_T = 5, 0.9, 0.85
Y_NUM, Y_HEU, Y_DRL = 0.45, 3.0, 5.5
GRADE = {"C": (0.30, 0.95, 0.55), "L": (1.00, 0.72, 0.20), "S": (0.95, 0.30, 0.60), "?": (0.6, 0.6, 0.6)}
CLASS_HUES = [(0.90, 0.35, 0.35), (0.95, 0.60, 0.25), (0.92, 0.85, 0.30), (0.55, 0.85, 0.35), (0.30, 0.80, 0.60),
              (0.30, 0.75, 0.90), (0.40, 0.55, 0.95), (0.65, 0.45, 0.95), (0.90, 0.45, 0.85), (0.75, 0.70, 0.60),
              (0.60, 0.75, 0.75)]
XITE_RAMP = [(0.95, 0.30, 0.25), (1.00, 0.55, 0.15), (0.88, 0.90, 0.96), (0.40, 0.90, 0.95), (0.55, 0.65, 1.00)]   # gold is kept for quotes


def f(x):
    s = f"{x:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def v3(p):
    return " ".join(f(c) for c in p)


def polar(r, a, y=0.0):
    return (r * math.cos(a), y, r * math.sin(a))


def sid(node_id):
    return "T_" + re.sub(r"[^A-Za-z0-9]", "_", node_id)     # letters, digits and underscores only (naming convention)


def look_at(eye, target):
    """Viewpoint orientation (axis, angle) that looks from eye to target with +Y up."""
    fx, fy, fz = (target[i] - eye[i] for i in range(3))
    n = math.sqrt(fx * fx + fy * fy + fz * fz)
    fx, fy, fz = fx / n, fy / n, fz / n
    rx, ry, rz = -fz, 0.0, fx                      # f x up
    n = math.sqrt(rx * rx + rz * rz) or 1.0
    rx, rz = rx / n, rz / n
    ux, uy, uz = ry * fz - rz * fy, rz * fx - rx * fz, rx * fy - ry * fx
    m = [[rx, ux, -fx], [ry, uy, -fy], [rz, uz, -fz]]
    tr = m[0][0] + m[1][1] + m[2][2]
    ang = math.acos(max(-1.0, min(1.0, (tr - 1) / 2)))
    if ang < 1e-6:
        return (0, 1, 0, 0)
    if ang > math.pi - 1e-3:
        # Near a half turn the antisymmetric part vanishes and (m21-m12, ...)/2sin(a) collapses to a zero-length axis
        # (the V_laws viewpoint, orientation '0 0 0 3.142', which x3d_mcp fa5dccf reports as rotation-zero-axis).
        # Take the axis from the symmetric part instead: m = 2aa^T - I at angle pi.
        ax = [math.sqrt(max(0.0, (m[i][i] + 1) / 2)) for i in range(3)]
        k = max(range(3), key=lambda i: ax[i])
        for j in range(3):
            if j != k:
                ax[j] = math.copysign(ax[j], m[k][j] + m[j][k])
        n = math.sqrt(sum(c * c for c in ax))
        return (ax[0] / n, ax[1] / n, ax[2] / n, ang)
    s = 2 * math.sin(ang)
    return ((m[2][1] - m[1][2]) / s, (m[0][2] - m[2][0]) / s, (m[1][0] - m[0][1]) / s, ang)


class Scene:
    def __init__(self):
        self.x = []
        self.seen = set()
        self.panel = {}
        self.sensors = collections.Counter()

    def add(self, s):
        self.x.append(s)

    def app(self, name, diffuse, emissive=None, transparency=0.0):
        """An Appearance, written once and USEd after."""
        if "A:" + name in self.seen:
            return f"<Appearance USE='A_{name}'/>"
        self.seen.add("A:" + name)
        e = emissive if emissive is not None else tuple(0.55 * c for c in diffuse)
        t = f" transparency='{f(transparency)}'" if transparency else ""
        return (f"<Appearance DEF='A_{name}'><Material DEF='M_{name}' diffuseColor='{v3(diffuse)}' "
                f"emissiveColor='{v3(e)}' specularColor='0.1 0.1 0.1'{t}/></Appearance>")

    def geom(self, name, xml):
        """A geometry node, written once and USEd after. xml is '<Tag ...>' with DEF inserted after the tag."""
        tag = re.match(r"<(\w+)", xml).group(1)
        if "G:" + name in self.seen:
            return f"<{tag} USE='G_{name}'/>"
        self.seen.add("G:" + name)
        return xml.replace(f"<{tag}", f"<{tag} DEF='G_{name}'", 1)

    def item(self, kind, node_id, pos, geom, app, desc, info, scale=None, rot=None):
        name = sid(node_id)
        if name in self.panel:
            raise SystemExit(f"two items share the sensor name {name}")
        self.panel[name] = info
        self.sensors[kind] += 1
        t = f" scale='{v3(scale)}'" if scale else ""
        t += f" rotation='{' '.join(f(c) for c in rot)}'" if rot else ""
        self.add(f"<Transform translation='{v3(pos)}'{t}><TouchSensor DEF='{name}' description={quoteattr(desc)}/>"
                 f"<Shape>{app}{geom}</Shape></Transform>")

    def label(self, pos, lines, size=1.0, color=(0.92, 0.94, 1.0), name="label"):
        strings = " ".join('"' + s.replace("\\", "").replace('"', "'") + '"' for s in lines)
        fs = ("<FontStyle USE='FS'/>" if "FS" in self.seen else
              "<FontStyle DEF='FS' family='\"SANS\"' justify='\"MIDDLE\" \"MIDDLE\"' size='1'/>")
        self.seen.add("FS")
        self.add(f"<Transform translation='{v3(pos)}' scale='{f(size)} {f(size)} {f(size)}'><Billboard axisOfRotation='0 0 0'>"
                 f"<Shape>{self.app(name, (0, 0, 0), color)}<Text string={quoteattr(strings)}>{fs}</Text></Shape>"
                 f"</Billboard></Transform>")

    def lines(self, segments, color, transparency=0.0, name=None):
        if not segments:
            return
        pts = " ".join(v3(p) for seg in segments for p in seg)
        idx = " ".join(f"{2 * i} {2 * i + 1} -1" for i in range(len(segments)))
        t = f" transparency='{f(transparency)}'" if transparency else ""
        d = f" DEF='M_{name}'" if name else ""
        self.add(f"<Shape><Appearance><Material{d} emissiveColor='{v3(color)}'{t}/></Appearance>"
                 f"<IndexedLineSet coordIndex='{idx}'><Coordinate point='{pts}'/></IndexedLineSet></Shape>")


def short(text, n):
    text = re.sub(r"\s+", " ", text)
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def build():
    A = Q.Atlas()
    findings = json.loads((OUT / "findings.json").read_text(encoding="utf-8"))
    S = Scene()
    pos = {}                                        # node id -> position, for the lines

    OCT = ("<IndexedFaceSet solid='false' coordIndex='0 2 4 -1 2 1 4 -1 1 3 4 -1 3 0 4 -1 2 0 5 -1 1 2 5 -1 3 1 5 -1 0 3 5 -1'>"
           "<Coordinate point='1 0 0 -1 0 0 0 0 1 0 0 -1 0 1 0 0 -1 0'/></IndexedFaceSet>")
    TET = ("<IndexedFaceSet solid='false' coordIndex='0 1 2 -1 0 3 1 -1 1 3 2 -1 2 3 0 -1'>"
           "<Coordinate point='1 1 1 -1 -1 1 -1 1 -1 1 -1 -1'/></IndexedFaceSet>")

    # ---- the ground, and two rings drawn on it ------------------------------------------------
    S.add(f"<Transform translation='0 -0.11 0'><Shape>{S.app('ground', (0.05, 0.06, 0.09), (0.012, 0.016, 0.03))}"
          f"<Cylinder radius='{f(R_GROUND)}' height='0.2' top='true' bottom='false' side='false'/></Shape></Transform>")
    for r in (R_COURT1 + 1.0, R_LAW, R_GATE):
        n = 96
        S.lines([(polar(r, 2 * math.pi * i / n, 0.02), polar(r, 2 * math.pi * (i + 1) / n, 0.02)) for i in range(n)],
                (0.16, 0.22, 0.36))

    # ---- laws: a ring of columns, by theme ----------------------------------------------------
    laws = sorted(A.of("Law"), key=lambda n: (A.out[n["id"]]["inTheme"][0], n["n"]))
    themes = sorted({A.out[n["id"]]["inTheme"][0] for n in laws})
    slots = len(laws) + len(themes)
    slot = 0
    law_fms = {n["id"]: sorted(A.law_failures(n["id"]), key=lambda x: A.n[x]["n"]) for n in laws}
    owner = {}                                      # failure mode -> the law whose path it lies on
    for n in sorted(laws, key=lambda n: n["n"]):
        for fm in law_fms[n["id"]]:
            owner.setdefault(fm, n["id"])
    S.add("<Group DEF='LAWS'>")
    law_angle = {}
    for th in themes:
        members = [n for n in laws if A.out[n["id"]]["inTheme"][0] == th]
        a0 = 2 * math.pi * slot / slots
        for n in members:
            a = 2 * math.pi * slot / slots
            slot += 1
            lid = n["id"]
            law_angle[lid] = a
            code = n.get("checkKind") == "code"
            h = 3.0 + 1.0 * len(law_fms[lid])
            col = (0.20, 0.72, 0.78) if code else (0.95, 0.62, 0.18)
            p = polar(R_LAW, a)
            pos[lid] = (p[0], h, p[2])
            desc = f"{n['label']}. {len(law_fms[lid])} failure modes linked. " + ("Mechanical check." if code else "Review only.")
            S.item("Law", lid, (p[0], h / 2, p[2]), S.geom("col", "<Cylinder radius='0.55' height='1'/>"),
                   S.app("law_code" if code else "law_process", col), desc,
                   {"kind": "Law", "title": n["label"], "body": A.how_do_we_know(lid)}, scale=(1, h, 1))
            S.add(f"<Transform translation='{v3((p[0], h + 0.15, p[2]))}' rotation='0 1 0 {f(-a)}'><Shape>"
                  f"{S.app('law_cap', (0.85, 0.9, 1.0), (0.5, 0.55, 0.65))}{S.geom('cap', '<Box size=\"1.5 0.3 1.5\"/>')}</Shape></Transform>")
            for k in range(len(A.out[lid]["caughtBy"])):
                S.add(f"<Transform translation='{v3((p[0], h - 0.45 - 0.3 * k, p[2]))}'><Shape>"
                      f"{S.app('collar', (1, 1, 1), (0.85, 0.9, 0.95))}{S.geom('collar', '<Cylinder radius=\"0.78\" height=\"0.1\"/>')}</Shape></Transform>")
            S.label((p[0], h + 1.25, p[2]), [str(n["n"])], 1.25)
            # the path of stones that leads to this law
            k = 0
            for fm in law_fms[lid]:
                if owner[fm] != lid:
                    continue
                q = polar(R_LAW - 1.5 - 0.82 * k, a, 0.16)
                k += 1
                pos[fm] = q
        am = (a0 + 2 * math.pi * (slot - 1) / slots) / 2
        S.label(polar(R_LAW + 3.6, am, 0.9), [A.n[th]["label"]], 0.8, (0.62, 0.72, 0.95), "label_theme")
        slot += 1
    S.add("</Group>")

    # ---- failure modes: stones on the paths, and loose in the courtyard by class --------------
    classes = sorted(A.of("FailureClass"), key=lambda n: int(n["code"][1:]))
    hue = {c["id"]: CLASS_HUES[i % len(CLASS_HUES)] for i, c in enumerate(classes)}
    fms = sorted(A.of("FailureMode"), key=lambda n: n["n"])
    loose = collections.defaultdict(list)
    for n in fms:
        if n["id"] not in pos:
            loose[A.out[n["id"]]["inClass"][0]].append(n["id"])
    total_loose = sum(len(v) for v in loose.values())
    a_cursor = 0.0
    S.add("<Group DEF='FAILURE_MODES'>")
    for c in classes:
        ids = loose[c["id"]]
        width = 2 * math.pi * len(ids) / total_loose
        usable = width * 0.86
        r, placed = R_COURT0, 0
        while placed < len(ids):
            cap = max(1, int(usable * r / 1.05))
            take = min(cap, len(ids) - placed)
            for j in range(take):
                a = a_cursor + width * 0.07 + usable * (j + 0.5) / take
                pos[ids[placed + j]] = polar(r, a, 0.16)
            placed += take
            r += 1.1
        members = len(A.inc[c["id"]]["inClass"])
        S.label(polar(R_COURT1 + 2.2, a_cursor + width / 2, 1.1),
                [short(c["label"], 40), f"{len(ids)} of {members} tied to no law"], 0.55, tuple(0.4 + 0.6 * x for x in hue[c["id"]]),
                "label_" + c["code"])
        a_cursor += width
    tops = {o for c in classes for o in A.out[c["id"]]["topOfClass"]}
    for n in fms:
        fid = n["id"]
        cid = A.out[fid]["inClass"][0]
        tied = fid in owner
        colr = hue[cid] if tied else tuple(0.42 * x for x in hue[cid])
        hgt = 0.6 if fid in tops else 0.3
        p = pos[fid]
        pos[fid] = (p[0], hgt, p[2])
        desc = f"Failure mode {n['n']}: {short(n['failure'], 110)}" + ("" if tied else " Tied to no law by number.")
        S.item("FailureMode", fid, (p[0], hgt / 2, p[2]), S.geom("stone", "<Box size='0.72 1 0.72'/>"),
               S.app(f"fm_{A.n[cid]['code']}_{'tied' if tied else 'loose'}", colr, tuple(0.5 * x for x in colr)), desc,
               {"kind": "Failure mode", "title": f"Failure mode {n['n']}", "body": A.failure(fid)}, scale=(1, hgt, 1),
               rot=(0, 1, 0, -math.atan2(p[2], p[0])))
    S.add("</Group>")
    extra = [(pos[fm], (polar(R_LAW, law_angle[l])[0], 0.3, polar(R_LAW, law_angle[l])[2]))
             for l, linked in law_fms.items() for fm in linked if owner[fm] != l]
    recur = [(tuple(map(sum, zip(pos[s], (0, 0.5, 0)))), tuple(map(sum, zip(pos[o], (0, 0.5, 0)))))
             for s in pos if s.startswith("fm/") for o in A.out[s]["recurredAs"]]

    # ---- chapters: a gate and an arm each ------------------------------------------------------
    chapters = sorted(A.of("Chapter"), key=lambda n: n["n"])
    by_ch = collections.defaultdict(lambda: collections.defaultdict(list))
    for t in ("Number", "Heuristic", "Drill"):
        for n in A.of(t):
            by_ch[A.out[n["id"]]["inChapter"][0]][t].append(n)

    def order(n):
        return int(n["label"].split()[0].split("-")[2])
    verified = {nid for nid in A.n if any(A.n[c]["verdict"] == "verified" for c in A.inc[nid]["supports"])}
    plates, ch_angle = [], {}
    S.add("<Group DEF='CHAPTERS'>")
    for i, ch in enumerate(chapters):
        a = 2 * math.pi * (i + 0.5) / len(chapters)
        ch_angle[ch["id"]] = a
        u, t = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
        cnt = {k: len(by_ch[ch["id"]][k]) for k in ("Number", "Heuristic", "Drill")}
        g = polar(R_GATE, a, 1.5)
        S.item("Chapter", ch["id"], g, S.geom("gate", "<Box size='0.5 3 2.4'/>"), S.app("gate", (0.25, 0.33, 0.6)),
               f"Chapter {ch['label']}: {cnt['Number']} numbers, {cnt['Heuristic']} heuristics, {cnt['Drill']} drills.",
               {"kind": "Chapter", "title": ch["label"], "body": {
                   "say it": ch.get("say"), "numbers": cnt["Number"], "heuristics": cnt["Heuristic"], "drills": cnt["Drill"],
                   "numbers with a verified quote": sum(1 for n in by_ch[ch["id"]]["Number"] if n["id"] in verified),
                   "requires": [A.n[o]["label"] for o in A.out[ch["id"]]["requires"]],
                   "pins cited": sorted(A.n[o]["label"] for o in A.out[ch["id"]]["citesPin"]), "at": ch["definedAt"]}},
               rot=(0, 1, 0, -a))
        S.label(polar(R_GATE, a, 4.0), [f"{ch['n']:02d}", short(ch["title"], 30)], 0.75)

        def grid(k, y):
            r = R_ARM + (k // WIDE) * STEP_R
            lat = (k % WIDE - (WIDE - 1) / 2) * STEP_T
            return (u[0] * r + t[0] * lat, y, u[1] * r + t[1] * lat)
        for k, n in enumerate(sorted(by_ch[ch["id"]]["Number"], key=order)):
            nid = n["id"]
            g_ = A.grade(nid)
            as_written = n.get("instrumentResolution") == "as written"
            s = 0.27 if as_written else 0.17
            p = grid(k, Y_NUM)
            pos[nid] = p
            desc = (f"{n['label']} [{g_}] {short(n['quantity'], 70)} = {short(n['value'], 40)}."
                    + ("" if as_written else " Instrument written as 'same'.") + (" Quote verified." if nid in verified else ""))
            S.item("Number", nid, p, S.geom("oct", OCT), S.app(f"num_{g_}", GRADE[g_]), desc,
                   {"kind": "Number", "title": n["label"], "body": A.how_do_we_know(nid)}, scale=(s, s, s))
            if nid in verified:
                plates.append(p)
        for k, n in enumerate(sorted(by_ch[ch["id"]]["Heuristic"], key=order)):
            hid = n["id"]
            g_ = A.grade(hid)
            tied = bool(A.out[hid]["evidencedBy"])
            p = grid(k, Y_HEU)
            pos[hid] = p
            S.item("Heuristic", hid, p, S.geom("tet", TET),
                   S.app(f"heu_{g_}_{'tied' if tied else 'free'}", GRADE[g_], None, 0.0 if tied else 0.62),
                   f"{n['label']} [{g_}] {short(n['rule'], 110)}" + ("" if tied else " Evidence cites no id."),
                   {"kind": "Heuristic", "title": n["label"], "body": A.how_do_we_know(hid)}, scale=(0.19, 0.19, 0.19))
        for k, n in enumerate(sorted(by_ch[ch["id"]]["Drill"], key=order)):
            did = n["id"]
            ran = n["status"] == "ran"
            p = grid(k, Y_DRL)
            pos[did] = p
            S.item("Drill", did, p, S.geom("cube", "<Box size='0.4 0.4 0.4'/>"),
                   S.app("drill_ran" if ran else "drill_not_run", (0.70, 0.82, 1.0) if ran else (0.95, 0.2, 0.2), None,
                         0.0 if ran else 0.35),
                   f"{n['label']} ({n.get('level', '?')}), {n['status']}.",
                   {"kind": "Drill", "title": n["label"], "body": A.how_do_we_know(did)})
    S.add("</Group>")
    S.add("<Group DEF='QUOTE_PLATES'>")
    for p in plates:
        S.add(f"<Transform translation='{v3((p[0], 0.05, p[2]))}'><Shape>{S.app('gold', (1.0, 0.8, 0.25), (0.8, 0.6, 0.1))}"
              f"{S.geom('plate', '<Cylinder radius=\"0.42\" height=\"0.06\"/>')}</Shape></Transform>")
    S.add("</Group>")

    # ---- the mast: X_ITE versions, and a thread to every number that stands on each ------------
    S.add("<Switch DEF='L_oracle' whichChoice='0'><Group>")
    S.add(f"<Transform translation='0 13 0'><Shape>{S.app('mast', (0.7, 0.75, 0.85), (0.3, 0.33, 0.4))}"
          f"<Cylinder radius='0.3' height='26'/></Shape></Transform>")
    xite = {}
    for n in A.of("ToolVersion"):
        if A.n[A.out[n["id"]]["ofTool"][0]]["label"] == "X_ITE":
            xite[n["version"]] = A.stands_on(n["label"])["numbers"].get(n["label"], [])
    order_v = sorted(xite, key=lambda v: tuple(int(x) for x in v.split(".")))
    for i, ver in enumerate(order_v):
        y = 13.0 + 2.6 * i
        colr = XITE_RAMP[min(i, len(XITE_RAMP) - 1)]
        S.item("ToolVersion", f"tool/x_ite@{ver}", (0, y, 0), S.geom("ring", "<Cylinder radius='1.6' height='0.3'/>"),
               S.app(f"xite_{i}", colr), f"X_ITE {ver}: {len(xite[ver])} numbers stand on it.",
               {"kind": "Tool version", "title": f"X_ITE {ver}", "body": {
                   "numbers that stand on it": len(xite[ver]), "ids": xite[ver],
                   "note": "A number holds at its own pin. This is the list to re-run at a newer version, not a list of errors."}})
        S.label((0, y + 0.9, 2.4), [f"X_ITE {ver}", f"{len(xite[ver])} numbers"], 0.7, colr, f"label_xite_{i}")
        segs = []
        for label in xite[ver]:
            q = pos[f"number/{label}"]
            d = math.hypot(q[0], q[2])
            segs.append(((1.6 * q[0] / d, y, 1.6 * q[2] / d), q))
        S.lines(segs, colr, 0.72)
    ds = A.n["dataset/atlas-v0"]
    S.item("Dataset", "dataset/atlas-v0", (0, 27.2, 0), "<Sphere radius='1.1'/>", S.app("atlas", (0.9, 0.95, 1.0), (0.75, 0.82, 1.0)),
           "The Atlas, version 0.", {"kind": "Dataset", "title": ds["label"], "body": {
               "inputs": A.meta["inputs"], "nodes": sum(A.meta["counts"].values()), "edges": sum(A.meta["edges"].values()),
               "counts": A.meta["counts"], "worklist": {k: v for k, v in A.worklist().items() if k != "source text to fix"}}})
    S.label((0, 29.4, 0), ["The Atlas, version 0"], 1.1)
    S.add("</Group></Switch>")

    # ---- joins: where one row cites another by id ----------------------------------------------
    S.add("<Switch DEF='L_joins' whichChoice='0'><Group>")
    tethers = [(pos[s], pos[o]) for s in pos for o in A.out[s]["evidencedBy"] if o in pos]
    mentions = [(pos[s], pos[o]) for s in pos for o in A.out[s]["mentions"] if o in pos and s.split("/")[0] != "law"]
    S.lines(tethers, (0.85, 0.9, 1.0), 0.25)
    S.lines(mentions, (0.45, 0.55, 0.8), 0.55)
    S.lines(extra, (0.55, 0.75, 0.8), 0.45)
    S.lines(recur, (1.0, 0.25, 0.2))
    S.add("</Group></Switch>")

    # ---- claims: gold threads from quoted numbers to the pins their quotes stand on ------------
    S.add("<Switch DEF='L_claims' whichChoice='0'><Group>")
    claim_pins = sorted({o for c in A.of("Claim") for o in A.out[c["id"]]["atPin"]})
    led = [ch_angle[c] for c in ch_angle if any(n["id"] in verified for n in by_ch[c]["Number"])]
    a_mid = sum(led) / len(led) if led else 0.0
    threads = []
    for i, pin in enumerate(claim_pins):
        a = a_mid + (i - (len(claim_pins) - 1) / 2) * 0.13
        p = polar(54.0, a, 14.0 + 2.6 * (i % 2))
        pos[pin] = p
        rows = sorted({A.n[o]["label"] for c in A.inc[pin]["atPin"] if c.startswith("claim/") for o in A.out[c]["supports"]})
        S.item("Pin", pin, p, S.geom("oct", OCT), S.app("gold", (1.0, 0.8, 0.25), (0.8, 0.6, 0.1)),
               f"Pin {A.n[pin]['label']}: {len(rows)} rows have a quote read at this commit.",
               {"kind": "Pin", "title": A.n[pin]["label"], "body": {"rows with a quote at this commit": rows,
                "claims": sum(1 for c in A.inc[pin]["atPin"] if c.startswith("claim/"))}}, scale=(0.6, 0.6, 0.6))
        S.label((p[0], p[1] + 1.2, p[2]), [A.n[pin]["label"]], 0.6, (1.0, 0.85, 0.4), "label_gold")
        for c in A.inc[pin]["atPin"]:
            if c.startswith("claim/"):
                threads += [(pos[o], p) for o in A.out[c]["supports"] if o in pos]
    S.lines(sorted(set(threads)), (1.0, 0.8, 0.25), 0.45, name="thread")
    S.add("</Group></Switch>")

    # ---- one clock: the gold of a verified quote breathes --------------------------------------
    S.add("<TimeSensor DEF='CLOCK' cycleInterval='4' loop='true'/>"
          "<ColorInterpolator DEF='GOLD' key='0 0.5 1' keyValue='0.55 0.4 0.05 1 0.85 0.3 0.55 0.4 0.05'/>"
          "<ROUTE fromNode='CLOCK' fromField='fraction_changed' toNode='GOLD' toField='set_fraction'/>"
          "<ROUTE fromNode='GOLD' fromField='value_changed' toNode='M_gold' toField='set_emissiveColor'/>")

    # ---- views ---------------------------------------------------------------------------------
    l44 = polar(R_LAW, law_angle["law/44"])
    c08 = ch_angle["chapter/08"]
    views = [
        ("V_overview", "The Atlas from above", (0, 74, 96), (0, 0, 8)),
        ("V_laws", "The ring of laws", (0, 11, -4), (0, 7, 30)),
        ("V_loose", "Stones that hold up nothing", (0, 19, 23), (0, 0, 3)),
        ("V_law44", "Law 44 and its stones", polar(21, law_angle["law/44"] + 0.72, 11), polar(24.5, law_angle["law/44"], 5)),
        ("V_quotes", "Where the quotes are", polar(80, a_mid, 24), polar(46, a_mid, 6)),
        ("V_ch08", "Chapter 08, the longest arm", polar(70, c08 + 0.16, 12), polar(48, c08, 2)),
        ("V_mast", "Under the mast", (10, 2.5, 12), (0, 17, 0)),
    ]
    vp = []
    for name, desc, eye, target in views:
        ax = look_at(eye, target)
        vp.append(f"<Viewpoint DEF='{name}' description={quoteattr(desc)} position='{v3(eye)}' "
                  f"orientation='{' '.join(f(c) for c in ax)}' centerOfRotation='{v3(target)}'/>")

    atlas_sha = hashlib.sha256((OUT / "atlas.json").read_bytes()).hexdigest()
    counts = dict(sorted(S.sensors.items()))
    head = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 4.0//EN" "https://www.web3d.org/specifications/x3d-4.0.dtd">
<X3D profile='Immersive' version='4.0' xmlns:xsd='http://www.w3.org/2001/XMLSchema-instance' xsd:noNamespaceSchemaLocation='https://www.web3d.org/specifications/x3d-4.0.xsd'>
<head>
<meta name='title' content='The Atlas, version 0: a walkable view'/>
<meta name='description' content='Laws, failure modes, numbers, heuristics, drills and pins of the X3D Loom as one scene. Drawn from atlas.json by fly_atlas.py; no Script node.'/>
<meta name='generator' content='fly_atlas.py (Atlas v0)'/>
<meta name='x3datlas.inputs' content='x3d.loom@{A.meta["inputs"]["x3d.loom"][:7]} x3d.docs@{A.meta["inputs"]["x3d.docs"][:7]}'/>
<meta name='x3datlas.atlas.sha256' content='{atlas_sha}'/>
<meta name='x3datlas.items' content={quoteattr(json.dumps(counts, sort_keys=True))}/>
</head>
<Scene>
<WorldInfo title='The Atlas, version 0' info='"A walkable view of the X3D Loom ledgers" "Every item has a TouchSensor whose description names it"'/>
<NavigationInfo type='"EXAMINE" "FLY" "WALK" "ANY"' speed='10' headlight='true' visibilityLimit='0'/>
<Background skyColor='0.004 0.006 0.02 0.02 0.035 0.09' skyAngle='1.5708' groundColor='0.004 0.006 0.02 0.02 0.035 0.09' groundAngle='1.5708'/>
<DirectionalLight direction='-0.4 -1 -0.3' intensity='0.55' ambientIntensity='0.35'/>
"""
    xml = head + "\n".join(vp) + "\n" + "\n".join(S.x) + "\n</Scene>\n</X3D>\n"
    (OUT / "atlas-world.x3d").write_text(xml, encoding="utf-8")
    (OUT / "atlas-panel.json").write_text(json.dumps({"views": [[n, d] for n, d, _, _ in views], "items": S.panel},
                                                     ensure_ascii=False) + "\n", encoding="utf-8")
    want = {t: A.meta["counts"][t] for t in ("Law", "FailureMode", "Chapter", "Number", "Heuristic", "Drill")}
    got = {t: counts.get(t, 0) for t in want}
    print(f"atlas-world.x3d {len(xml):,} bytes; items {counts}")
    print(("ok " if got == want else "RED") + f" every law, failure mode, chapter, number, heuristic and drill is in the scene: {got}")
    print(f"lines: tethers {len(tethers)}, mentions {len(mentions)}, second laws {len(extra)}, recurrences {len(recur)}, "
          f"claim threads {len(set(threads))}, X_ITE threads {sum(len(v) for v in xite.values())}; gold plates {len(plates)}")
    return 0 if got == want else 1


if __name__ == "__main__":
    sys.exit(build())
