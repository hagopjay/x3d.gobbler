#!/usr/bin/env python3
"""Import the glass Gobbler into Blender through the x3d-blender-io add-on and count what arrives.

    python mascot/glass/blender/import_count.py --addon ../x3d-blender-io --scene mascot/glass/gobbler-glass.x3d \
        --blend /tmp/gobbler-glass.blend --out mascot/glass/receipts/blender-import.json
"""
import argparse, json, sys, tempfile, subprocess, collections, hashlib
from pathlib import Path
import xml.etree.ElementTree as ET
import bpy


def register(addon: Path):
    tmp = tempfile.mkdtemp(); (Path(tmp) / "io_scene_x3d").symlink_to(addon / "source", target_is_directory=True)
    sys.path.insert(0, tmp)
    import importlib
    m = importlib.import_module("io_scene_x3d"); m.register(); return m


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--addon", type=Path, required=True); ap.add_argument("--scene", type=Path, required=True)
    ap.add_argument("--blend", type=Path, required=True); ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    register(a.addon.resolve())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    res = bpy.ops.import_scene.x3d(filepath=str(a.scene.resolve()))
    root = ET.parse(a.scene).getroot()
    src = collections.Counter(e.tag for e in root.iter())
    src_faces = sum(e.get("coordIndex", "").split().count("-1") for e in root.iter("IndexedFaceSet"))
    objs = list(bpy.data.objects)
    kinds = collections.Counter(o.type for o in objs)
    meshes = [o for o in objs if o.type == "MESH"]
    named = {}
    for o in meshes:
        me = o.data
        named[o.name] = {"verts": len(me.vertices), "polys": len(me.polygons), "color_attrs": [c.name + ":" + c.domain + ":" + c.data_type for c in me.color_attributes],
                         "materials": [m.name if m else None for m in me.materials], "parent": o.parent.name if o.parent else None}
    mats = {}
    for m in bpy.data.materials:
        b = m.node_tree.nodes.get("Principled BSDF") if m.node_tree else None
        mats[m.name] = {"alpha": round(b.inputs["Alpha"].default_value, 4), "emission": [round(x, 3) for x in b.inputs["Emission Color"].default_value[:3]],
                        "emission_strength": round(b.inputs["Emission Strength"].default_value, 3)} if b else {}
    head = subprocess.run(["git", "-C", str(a.addon), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    anim = sum(1 for o in objs if o.animation_data and o.animation_data.action)
    rec = {"schema": "gobbler.blender-import/1", "blender": bpy.app.version_string, "addon_commit": head, "operator_result": sorted(res), "scene": a.scene.name, "scene_sha256": hashlib.sha256(a.scene.read_bytes()).hexdigest(),
           "source": {"Shape": src["Shape"], "IndexedFaceSet": src["IndexedFaceSet"], "ifs_faces": src_faces, "Sphere": src["Sphere"], "IndexedLineSet": src["IndexedLineSet"],
                      "PointSet": src["PointSet"], "Viewpoint": src["Viewpoint"], "lights": src["DirectionalLight"] + src["PointLight"] + src["SpotLight"],
                      "ROUTE": src["ROUTE"], "TimeSensor": src["TimeSensor"], "Material": src["Material"]},
           "arrived": {"objects": len(objs), "by_type": dict(kinds), "mesh_polys": sum(v["polys"] for v in named.values()), "materials": len(mats),
                       "animated_objects": anim, "actions": len(bpy.data.actions)},
           "meshes": {k: v for k, v in named.items() if not k.startswith("Gem_")}, "gem_meshes": sum(1 for k in named if k.startswith("Gem_")), "materials": mats,
           "other_objects": {o.name: o.type for o in objs if o.type != "MESH"},
           "cameras": {o.name: {"lens_mm": round(o.data.lens, 2), "sensor_mm": o.data.sensor_width, "fit": o.data.sensor_fit} for o in objs if o.type == "CAMERA"},
           "lost": ["ROUTE P_red.value_changed -> L_red.set_location", "ROUTE P_blue.value_changed -> L_blue.set_location", "ROUTE P_gold.value_changed -> L_gold.set_location"],
           "lost_note": "the three lines the importer itself printed as 'X3D import loss ... ROUTE not imported'; copied here by hand from its output"}
    a.out.parent.mkdir(parents=True, exist_ok=True); a.out.write_text(json.dumps(rec, indent=1) + "\n")
    bpy.ops.wm.save_as_mainfile(filepath=str(a.blend))
    print(json.dumps({k: rec[k] for k in ("source", "arrived", "other_objects")}, indent=1)); 

main()
