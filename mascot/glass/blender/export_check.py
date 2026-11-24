#!/usr/bin/env python3
"""Export the lit glass Gobbler from Blender to glTF and USD, read each back, and count what survived.

    python mascot/glass/blender/export_check.py --blend /tmp/gobbler-glass-lit.blend --outdir mascot/glass/exports \
        --receipt mascot/glass/receipts/blender-exports.json
"""
import argparse, collections, hashlib, json
from pathlib import Path
import bpy


def census():
    dg = bpy.context.evaluated_depsgraph_get()
    objs = list(bpy.data.objects); kinds = collections.Counter(o.type for o in objs)
    polys = 0; colored = 0
    for o in objs:
        if o.type == "MESH":
            me = o.evaluated_get(dg).data; polys += len(me.polygons); colored += bool(me.color_attributes)
    mats = [m for m in bpy.data.materials if m.users]
    def p(m): return m.node_tree.nodes.get("Principled BSDF") if m.node_tree else None
    glass = sum(1 for m in mats if p(m) and p(m).inputs["Transmission Weight"].default_value > 0.4)
    glow = sum(1 for m in mats if p(m) and p(m).inputs["Emission Strength"].default_value > 0 and (p(m).inputs["Emission Color"].is_linked or max(p(m).inputs["Emission Color"].default_value[:3]) > 0))
    return {"objects": len(objs), "by_type": dict(sorted(kinds.items())), "mesh_polys": polys, "meshes_with_colour_attribute": colored, "materials_in_use": len(mats),
            "materials_with_transmission": glass, "materials_with_emission": glow,
            "animated_objects": sum(1 for o in objs if o.animation_data and o.animation_data.action), "actions": len(bpy.data.actions),
            "nla_tracks": sum(len(o.animation_data.nla_tracks) for o in objs if o.animation_data),
            "transform_cache_constraints": sum(1 for o in objs for c in o.constraints if c.type == "TRANSFORM_CACHE")}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--blend", required=True); ap.add_argument("--outdir", type=Path, required=True); ap.add_argument("--receipt", type=Path, required=True)
    a = ap.parse_args(); a.outdir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=a.blend)
    rec = {"schema": "gobbler.blender-exports/1", "blender": bpy.app.version_string, "in_blender": census(), "formats": {}}
    glb = a.outdir / "gobbler-glass.glb"; usd = a.outdir / "gobbler-glass.usdc"
    r1 = bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", export_apply=True, export_cameras=True, export_lights=True, export_animations=True, export_yup=True)
    r2 = bpy.ops.wm.usd_export(filepath=str(usd), export_animation=True, export_materials=True, export_lights=True, export_cameras=True, evaluation_mode="RENDER")
    for name, path, res, reader in (("glTF 2.0 binary", glb, r1, lambda p: bpy.ops.import_scene.gltf(filepath=p)), ("OpenUSD crate", usd, r2, lambda p: bpy.ops.wm.usd_import(filepath=p))):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        back = reader(str(path))
        rec["formats"][name] = {"file": path.name, "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "export_result": sorted(res),
                                "import_result": sorted(back), "read_back": census()}
    a.receipt.parent.mkdir(parents=True, exist_ok=True); a.receipt.write_text(json.dumps(rec, indent=1) + "\n"); print(json.dumps(rec, indent=1))


main()
