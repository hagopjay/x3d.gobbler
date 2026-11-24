#!/usr/bin/env python3
"""Bake the Blender pass's light onto every face of the bird and write one display colour per face.

    python mascot/baked/blender/bake_light.py --blend /tmp/prebake.blend --scene /tmp/prebake.x3d --out mascot/baked/bake.json

The .blend is the pre-bake scene (`build_mascot.py baked` with no --bake) imported by mascot/glass/blender/import_count.py.
The light rig is the one the Cycles stills used (render_glass.light_rig). Glass and metal cannot be baked, because what
they show depends on where the eye is, so each part gets a view-free stand-in: a matt surface in its own colour, a share
of light let through from behind for the glass parts, and a share of its own glow. Cycles bakes that to face corners
(COMBINED without the glossy pass); the corners of a face are averaged, exposed, rolled off and given the sRGB curve.
The builder then draws those colours unlit. Polygon order is checked against the X3D face order before anything is written.
"""
import argparse, hashlib, json, math, sys, time
from pathlib import Path
import xml.etree.ElementTree as ET
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "glass" / "blender"))
import render_glass as rg  # noqa: E402

#           name: (light let through from behind, own glow, saturation)
STANDIN = {"Vanes": (0.55, 0.14, 1.25), "Body": (0.30, 0.20, 1.2), "Loom": (0.0, 0.06, 1.15), "Shafts": (0.0, 0.04, 1.1),
           "Beads": (0.2, 0.45, 1.3), "FailureModes": (0.2, 0.35, 1.3), "WheelRing": (0.0, 0.08, 1.1), "Beak": (0.0, 0.08, 1.1),
           "Wattle": (0.3, 0.5, 1.0), "Legs": (0.0, 0.03, 1.1), "Floor": (0.0, 0.0, 1.0)}
SAMPLES, SEED, CLAMP = 128, 7, 4.0
ANCHOR = ("Vanes", 85, 0.65)        # exposure: the 85th-percentile vane face lands at 0.65 linear, before the roll-off


def standin(name, through, glow, sat):
    m = bpy.data.materials.new("Bake_" + name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    a = nt.nodes.new("ShaderNodeAttribute"); a.attribute_name = rg.ATTR
    h = nt.nodes.new("ShaderNodeHueSaturation"); h.inputs["Saturation"].default_value = sat; nt.links.new(a.outputs["Color"], h.inputs["Color"])
    nt.links.new(h.outputs["Color"], b.inputs["Base Color"]); nt.links.new(h.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Roughness"].default_value = 1.0; b.inputs["Specular IOR Level"].default_value = 0.0; b.inputs["Emission Strength"].default_value = glow
    if through:
        t = nt.nodes.new("ShaderNodeBsdfTranslucent"); nt.links.new(h.outputs["Color"], t.inputs["Color"])
        mx = nt.nodes.new("ShaderNodeMixShader"); mx.inputs["Fac"].default_value = through
        nt.links.new(b.outputs[0], mx.inputs[1]); nt.links.new(t.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    return m


def emitters():
    """The parts that stay as they are in the X3D (spheres) still have to shine on their neighbours during the bake."""
    D = bpy.data.objects
    rg.assign(D["Heart"], rg.principled("E_Heart", attr=False, base=(1.0, 0.55, 0.12), emis=38.0))
    for m in bpy.data.materials:
        if m.name.startswith("Gem_"): m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.4


def srgb(x): return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055
WHITE = 6.0                         # linear luminance that maps to display white


def tone(col):
    """Roll the highlights off on luminance and keep the hue: a bright gold face stays gold and keeps its gradient,
    where a per-channel clip turned every lit gold face the same lemon yellow (first bake) and a pull toward grey turned
    them white (second bake); both were seen in the browser."""
    L = lum(col)
    if L <= 1e-6: return (0.0, 0.0, 0.0)
    Lo = L * (1 + L / WHITE ** 2) / (1 + L)
    out = [ch * Lo / L for ch in col]; m = max(out)
    if m > 1.0: out = [ch / m for ch in out]   # still past 1 in one channel: dim the face, keep its hue and saturation
    return tuple(srgb(max(0.0, min(1.0, ch))) for ch in out)
def lum(c): return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def pct(v, q): v = sorted(v); return v[min(len(v) - 1, int(q / 100 * len(v)))]


def x3d_centres(scene: Path):
    out = {}
    for sh in ET.parse(scene).getroot().iter("Shape"):
        ifs = sh.find("IndexedFaceSet")
        if ifs is None or sh.get("DEF") not in STANDIN: continue
        p = [float(v) for v in ifs.find("Coordinate").get("point").split()]; pts = [p[i:i + 3] for i in range(0, len(p), 3)]
        faces, cur = [], []
        for t in ifs.get("coordIndex").split():
            if t == "-1": faces.append(cur); cur = []
            else: cur.append(int(t))
        out[sh.get("DEF")] = [[sum(pts[i][k] for i in fc) / len(fc) for k in range(3)] for fc in faces]
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--blend", required=True); ap.add_argument("--scene", type=Path, required=True); ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    bpy.ops.wm.open_mainfile(filepath=a.blend)
    sc = bpy.context.scene; sc.frame_set(1); D = bpy.data.objects
    rg.light_rig(); emitters()
    sc.render.engine = "CYCLES"; c = sc.cycles; c.device = "CPU"; c.samples = SAMPLES; c.seed = SEED; c.use_denoising = False
    c.sample_clamp_indirect = CLAMP; c.max_bounces = 8; c.use_adaptive_sampling = False
    bk = sc.render.bake; bk.target = "VERTEX_COLORS"; bk.use_pass_direct = True; bk.use_pass_indirect = True; bk.use_pass_diffuse = True
    bk.use_pass_transmission = True; bk.use_pass_emit = True; bk.use_pass_glossy = False
    for n, (through, glow, sat) in STANDIN.items(): rg.assign(D[n], standin(n, through, glow, sat))
    want = x3d_centres(a.scene); raw, order, secs = {}, {}, {}
    for n in STANDIN:
        o = D[n]; me = o.data
        ca = me.color_attributes.new("Bake", "FLOAT_COLOR", "CORNER"); me.color_attributes.active_color = ca
        bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
        t = time.time(); bpy.ops.object.bake(type="COMBINED"); secs[n] = round(time.time() - t, 1)
        data = me.color_attributes["Bake"].data; cols = []; worst = 0.0
        for i, poly in enumerate(me.polygons):
            cs = [data[li].color[:3] for li in poly.loop_indices]
            cols.append(tuple(max(0.0, sum(ch[k] for ch in cs) / len(cs)) for k in range(3)))
            w = o.matrix_world @ poly.center; y_up = (w.x, w.z, -w.y)          # Blender Z-up back to X3D Y-up
            worst = max(worst, max(abs(y_up[k] - want[n][i][k]) for k in range(3)))
        if len(cols) != len(want[n]): raise SystemExit(f"{n}: {len(cols)} polygons for {len(want[n])} X3D faces")
        raw[n] = cols; order[n] = round(worst, 5); print("BAKED", n, len(cols), secs[n], "s, order check", order[n], flush=True)
    if max(order.values()) > 2e-3: raise SystemExit(f"polygon order does not match the X3D face order: {order}")
    k = ANCHOR[2] / max(1e-6, pct([lum(col) for col in raw[ANCHOR[0]]], ANCHOR[1]))
    colours, stats = {}, {}
    for n, cols in raw.items():
        colours[n] = [[round(ch, 3) for ch in tone(tuple(c * k for c in col))] for col in cols]
        L = [lum(col) for col in cols]; Ld = [lum(col) for col in colours[n]]
        stats[n] = {"faces": len(cols), "bake_seconds": secs[n], "linear_luminance_p5_p50_p95": [round(pct(L, q), 4) for q in (5, 50, 95)],
                    "display_luminance_p5_p50_p95": [round(pct(Ld, q), 3) for q in (5, 50, 95)], "order_check_max_m": order[n]}
    rec = {"schema": "gobbler.bake/1", "blender": bpy.app.version_string, "engine": "Cycles CPU", "bake": "COMBINED to face corners, glossy pass off, averaged per face",
           "samples": SAMPLES, "seed": SEED, "indirect_clamp": CLAMP, "denoise": False, "light_rig": "mascot/glass/blender/render_glass.py light_rig()",
           "standins_through_glow_saturation": STANDIN, "exposure": {"anchor": f"{ANCHOR[1]}th percentile {ANCHOR[0]} face luminance -> {ANCHOR[2]} linear", "gain": round(k, 5)},
           "finish": f"gain, hue-keeping roll-off on luminance (white at {WHITE}), sRGB curve, 3 decimals", "scene_sha256": hashlib.sha256(a.scene.read_bytes()).hexdigest(),
           "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "meshes": stats, "colours": colours}
    a.out.parent.mkdir(parents=True, exist_ok=True); a.out.write_text(json.dumps(rec, separators=(",", ":")) + "\n")
    print(json.dumps({"gain": rec["exposure"]["gain"], "meshes": stats}, indent=1))


if __name__ == "__main__":
    main()
