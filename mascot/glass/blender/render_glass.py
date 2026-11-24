#!/usr/bin/env python3
"""Shade, light and render the imported glass Gobbler in Cycles.

    python mascot/glass/blender/render_glass.py --blend /tmp/gobbler-glass.blend --out mascot/glass/stills \
        --views V_Face,V_Wide,V_Heart --w 1920 --h 1080 --samples 160 [--save /tmp/gobbler-glass-lit.blend]

Reads the .blend written by import_count.py. Every mesh, colour, camera and animation in it came through the
x3d-blender-io importer. What THIS script adds is listed in ADDED and written into every render receipt, so nobody
mistakes the Blender pass for the X3D scene: materials rebuilt as glass and metal on the imported colours, a mirror
floor, three area lights, a procedural night sky, a bevel on the lattice curve, spheres on the star points.
"""
import argparse, json, math, time
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

ADDED = ["Principled glass and metal materials driven by the imported per-corner colours",
         "weld + 0.035 m Solidify on the vanes so the glass has two surfaces", "mirror floor disc (radius 70 m)",
         "four area lights (back-left magenta, back-right cyan, front warm key, small face fill)", "camera rays pass through lattice bars nearer than 9 m (fading in to 17 m)", "procedural noise night sky in the world shader",
         "bevel 0.018 m on the imported lattice curve", "geometry-node spheres on the imported star points",
         "depth of field on the cameras", "AgX view transform"]
ATTR = "ColorPerCorner"


def principled(name, *, attr=True, base=None, metallic=0.0, rough=0.2, trans=0.0, ior=1.45, emis=0.0, emis_col=None, sat=1.0, coat=0.0, lift=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    if attr:
        a = nt.nodes.new("ShaderNodeAttribute"); a.attribute_name = ATTR
        h = nt.nodes.new("ShaderNodeHueSaturation"); h.inputs["Saturation"].default_value = sat
        nt.links.new(a.outputs["Color"], h.inputs["Color"])
        if lift:   # a paler tint for the glass body so light gets through; the emission keeps the full colour
            mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs["Factor"].default_value = lift
            mx.inputs["B"].default_value = (1, 1, 1, 1); nt.links.new(h.outputs["Color"], mx.inputs["A"])
            nt.links.new(mx.outputs["Result"], b.inputs["Base Color"])
        else:
            nt.links.new(h.outputs["Color"], b.inputs["Base Color"])
        if emis and emis_col is None: nt.links.new(h.outputs["Color"], b.inputs["Emission Color"])
    elif base is not None:
        b.inputs["Base Color"].default_value = (*base, 1)
        if emis and emis_col is None: b.inputs["Emission Color"].default_value = (*base, 1)
    if emis_col is not None: b.inputs["Emission Color"].default_value = (*emis_col, 1)
    b.inputs["Metallic"].default_value = metallic; b.inputs["Roughness"].default_value = rough
    b.inputs["Transmission Weight"].default_value = trans; b.inputs["IOR"].default_value = ior
    b.inputs["Emission Strength"].default_value = emis; b.inputs["Coat Weight"].default_value = coat
    return m


def assign(obj, mat):
    obj.data.materials.clear(); obj.data.materials.append(mat)


def weld(obj, dist=1e-5):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bm.to_mesh(obj.data); bm.free()


def area(name, loc, target, size, energy, color):
    d = bpy.data.lights.new(name, "AREA"); d.shape = "DISK"; d.size = size; d.energy = energy; d.color = color
    o = bpy.data.objects.new(name, d); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o


def stars_group(mat, radius):
    ng = bpy.data.node_groups.new("StarPoints", "GeometryNodeTree")
    ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    i = ng.nodes.new("NodeGroupInput"); o = ng.nodes.new("NodeGroupOutput")
    p = ng.nodes.new("GeometryNodeMeshToPoints"); p.inputs["Radius"].default_value = radius
    s = ng.nodes.new("GeometryNodeSetMaterial"); s.inputs["Material"].default_value = mat
    ng.links.new(i.outputs[0], p.inputs["Mesh"]); ng.links.new(p.outputs["Points"], s.inputs["Geometry"]); ng.links.new(s.outputs["Geometry"], o.inputs[0])
    return ng


def world():
    w = bpy.data.worlds.new("Night"); w.use_nodes = True; nt = w.node_tree; bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = 1.6; n.inputs["Detail"].default_value = 9; n.inputs["Roughness"].default_value = 0.62
    r = nt.nodes.new("ShaderNodeValToRGB"); e = r.color_ramp.elements
    e[0].position = 0.38; e[0].color = (0.0015, 0.002, 0.008, 1); e[1].position = 0.78; e[1].color = (0.10, 0.012, 0.16, 1)
    mid = r.color_ramp.elements.new(0.6); mid.color = (0.004, 0.02, 0.07, 1)
    nt.links.new(tc.outputs["Generated"], n.inputs["Vector"]); nt.links.new(n.outputs["Fac"], r.inputs["Fac"]); nt.links.new(r.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0
    bpy.context.scene.world = w


def shade():
    D = bpy.data.objects
    gold = (1.0, 0.72, 0.28)
    vane = principled("G_VaneGlass", rough=0.025, trans=1.0, ior=1.38, emis=0.16, sat=1.3, coat=0.12, lift=0.22)
    weld(D["Vanes"]); assign(D["Vanes"], vane)
    sm = D["Vanes"].modifiers.new("Glass thickness", "SOLIDIFY"); sm.thickness = 0.03; sm.offset = 0
    assign(D["Shafts"], principled("G_ShaftGold", attr=False, base=gold, metallic=1.0, rough=0.22, emis=0.25))
    assign(D["Beads"], principled("G_BeadGlow", rough=0.1, trans=0.6, emis=1.6, sat=1.3))
    assign(D["Loom"], principled("G_LoomGold", metallic=1.0, rough=0.24, emis=0.5, sat=1.1))
    weld(D["Body"]); assign(D["Body"], principled("G_BodyGlass", rough=0.08, trans=1.0, ior=1.5, emis=0.5, sat=1.25, coat=0.5, lift=0.3))
    assign(D["Beak"], principled("G_Beak", attr=False, base=gold, metallic=1.0, rough=0.18, emis=0.6))
    assign(D["Wattle"], principled("G_Wattle", rough=0.1, trans=0.8, emis=1.6))
    assign(D["Legs"], principled("G_Legs", attr=False, base=gold, metallic=1.0, rough=0.3, emis=0.1))
    assign(D["WheelRing"], principled("G_Wheel", metallic=1.0, rough=0.2, emis=1.2))
    assign(D["FailureModes"], principled("G_Modes", rough=0.12, trans=0.5, emis=2.2, sat=1.25))
    assign(D["Heart"], principled("G_Heart", attr=False, base=(1.0, 0.55, 0.12), rough=0.3, emis=38.0))
    for n in ("Shape", "Shape.001"):
        assign(D[n], principled("G_Eye", attr=False, base=(1.0, 0.85, 0.4), emis=22.0))
    for n in ("B_red", "B_blue", "B_gold"):
        col = tuple(D[n].data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value[:3])
        assign(D[n], principled("G_" + n, attr=False, base=col, emis=14.0))
    gems = 0
    for m in bpy.data.materials:
        if m.name.startswith("Gem_"):
            b = m.node_tree.nodes["Principled BSDF"]; col = b.inputs["Emission Color"].default_value[:]
            b.inputs["Base Color"].default_value = col; b.inputs["Transmission Weight"].default_value = 0.9
            b.inputs["Roughness"].default_value = 0.05; b.inputs["Emission Strength"].default_value = 2.4; gems += 1
    for o in D:
        if o.type == "MESH" and (o.name.startswith("Gem_") or o.name in ("Heart", "Shape", "Shape.001")):
            for p in o.data.polygons: p.use_smooth = True
    lat = D["Lattice"]; lat.data.bevel_depth = 0.007; lat.data.bevel_resolution = 2
    lm = principled("G_Lattice", attr=False, base=(0.15, 0.45, 1.0), rough=0.3, emis=1.3)
    # the lattice is a sphere the cameras sit just outside of: let the camera see through the bars nearest to it
    nt = lm.node_tree; lp = nt.nodes.new("ShaderNodeLightPath"); mr = nt.nodes.new("ShaderNodeMapRange"); tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mr.inputs["From Min"].default_value = 9.0; mr.inputs["From Max"].default_value = 17.0
    cm = nt.nodes.new("ShaderNodeMath"); cm.operation = "MAXIMUM"; nt.links.new(mr.outputs["Result"], cm.inputs[0])
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0; nt.links.new(lp.outputs["Is Camera Ray"], inv.inputs[1])
    nt.links.new(inv.outputs[0], cm.inputs[1]); nt.links.new(lp.outputs["Ray Length"], mr.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMixShader"); nt.links.new(cm.outputs[0], mix.inputs["Fac"]); nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(nt.nodes["Principled BSDF"].outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    lat.data.materials.clear(); lat.data.materials.append(lm)
    star = principled("G_Star", attr=False, base=(0.85, 0.9, 1.0), emis=14.0)
    for i, n in enumerate(("Shape.002", "Shape.003", "Shape.004")):
        md = D[n].modifiers.new("Star spheres", "NODES"); md.node_group = stars_group(star, (0.07, 0.12, 0.22)[i])
    # floor
    bpy.ops.mesh.primitive_circle_add(vertices=128, radius=70, fill_type="NGON", location=(0, 0, -0.03))
    fl = bpy.context.object; fl.name = "MirrorFloor"
    assign(fl, principled("G_Floor", attr=False, base=(0.004, 0.005, 0.01), metallic=0.0, rough=0.07, coat=1.0))
    fl.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 1.0
    light_rig()
    return {"gem_materials": gems}


def light_rig():
    """The lights and sky of the Blender pass, apart from the materials, so the bake (mascot/baked) uses the same light."""
    D = bpy.data.objects
    # the imported point lights keep their colours; soften them and bring them into a film range
    for n, e in (("L_red", 900), ("L_blue", 900), ("L_gold", 700), ("PointLight", 420)):
        D[n].data.energy = e; D[n].data.shadow_soft_size = 0.35
    for o in (area("Back_magenta", (-12, 14, 9), (0, 1.5, 6.5), 16, 5200, (1.0, 0.3, 0.8)), area("Back_cyan", (12, 14, 10), (0, 1.5, 6.5), 16, 5200, (0.25, 0.8, 1.0))):
        o.visible_glossy = False     # they light the glass from behind without printing two discs on the floor
    area("Key_warm", (-6, -14, 15), (0, -1, 5), 14, 2200, (1.0, 0.86, 0.7))
    area("Face_fill", (2.5, -9, 8.5), (0, -2.6, 7.1), 2.5, 500, (1.0, 0.9, 0.8)).visible_glossy = False
    world()


def camera(name, w, h):
    cam = bpy.data.objects[name]; bpy.context.scene.camera = cam
    focus = {"V_Heart": (0, -0.1, 3.3), "V_Face": (0, -2.4, 7.0), "V_Wide": (0, -1.5, 6.0), "V_Fan": (0, 1.5, 7), "V_Above": (0, 0, 3), "V_Hero": (0, -1.5, 7), "V_Low": (0, -1.2, 5)}[name]
    cam.data.dof.use_dof = True; cam.data.dof.focus_distance = (Vector(focus) - cam.matrix_world.translation).length
    cam.data.dof.aperture_fstop = {"V_Heart": 2.0}.get(name, 4.0)
    return cam


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--blend", required=True); ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--views", default="V_Face,V_Wide,V_Heart"); ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
    ap.add_argument("--samples", type=int, default=160); ap.add_argument("--save"); ap.add_argument("--frame", type=int, default=1)
    ap.add_argument("--exposure", type=float, default=0.0)
    a = ap.parse_args()
    bpy.ops.wm.open_mainfile(filepath=a.blend)
    sc = bpy.context.scene; sc.frame_set(a.frame)
    info = shade()
    sc.render.engine = "CYCLES"; c = sc.cycles; c.device = "CPU"; c.samples = a.samples; c.use_denoising = True; c.denoiser = "OPENIMAGEDENOISE"
    c.max_bounces = 14; c.transmission_bounces = 12; c.glossy_bounces = 6; c.diffuse_bounces = 3; c.blur_glossy = 0.6
    c.caustics_reflective = False; c.caustics_refractive = True; c.sample_clamp_indirect = 8.0; c.use_adaptive_sampling = True; c.adaptive_threshold = 0.02
    sc.render.resolution_x = a.w; sc.render.resolution_y = a.h; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"; sc.view_settings.exposure = a.exposure
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "16"
    a.out.mkdir(parents=True, exist_ok=True)
    if a.save: bpy.ops.wm.save_as_mainfile(filepath=a.save)
    recs = []
    for v in a.views.split(","):
        camera(v, a.w, a.h)
        path = a.out / f"glass-{v[2:].lower()}-raw.png"; sc.render.filepath = str(path)
        t = time.time(); bpy.ops.render.render(write_still=True); dt = round(time.time() - t, 1)
        recs.append({"view": v, "file": path.name, "seconds": dt}); print("RENDERED", v, dt, "s", flush=True)
    rec = {"schema": "gobbler.blender-render/1", "blender": bpy.app.version_string, "engine": "Cycles", "device": "CPU", "samples_max": a.samples,
           "adaptive_threshold": 0.02, "denoiser": "OpenImageDenoise", "resolution": [a.w, a.h], "frame": a.frame, "view_transform": "AgX, Medium High Contrast",
           "exposure": a.exposure, "added_in_blender": ADDED, "renders": recs, **info}
    (a.out / "blender-render.json").write_text(json.dumps(rec, indent=1) + "\n")


if __name__ == "__main__":
    main()
