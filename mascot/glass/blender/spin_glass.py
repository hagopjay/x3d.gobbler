#!/usr/bin/env python3
"""Turntable of the glass Gobbler in Cycles: one camera on a circle, the bird's own animation running.

    python mascot/glass/blender/spin_glass.py --blend /tmp/gobbler-glass.blend --out /tmp/spin --frames 144 [--only 0,36]

Same import, materials and light as the stills (render_glass.shade). Added here and listed in the receipt: the orbit
camera (the X3D has no such path). The scene clock runs 216 frames over the turn, so the fan's 9 s sway closes the loop.
"""
import argparse, json, math, sys, time
from pathlib import Path
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_glass as rg  # noqa: E402

RADIUS, HEIGHT, TARGET, LENS = 22.5, 7.6, (0.0, 0.0, 7.0), 26.9


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--blend", required=True); ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--frames", type=int, default=144); ap.add_argument("--w", type=int, default=960); ap.add_argument("--h", type=int, default=540)
    ap.add_argument("--samples", type=int, default=64); ap.add_argument("--only", default="")
    a = ap.parse_args()
    bpy.ops.wm.open_mainfile(filepath=a.blend)
    sc = bpy.context.scene; rg.shade()
    cd = bpy.data.cameras.new("Spin"); cd.lens = LENS; cd.dof.use_dof = True; cd.dof.aperture_fstop = 4.0; cd.dof.focus_distance = RADIUS
    cam = bpy.data.objects.new("Spin", cd); sc.collection.objects.link(cam); sc.camera = cam
    sc.render.engine = "CYCLES"; c = sc.cycles; c.device = "CPU"; c.samples = a.samples; c.use_denoising = True; c.denoiser = "OPENIMAGEDENOISE"
    c.max_bounces = 12; c.transmission_bounces = 10; c.glossy_bounces = 5; c.diffuse_bounces = 2; c.blur_glossy = 0.6; c.seed = 7
    c.caustics_reflective = False; c.caustics_refractive = True; c.sample_clamp_indirect = 8.0; c.use_adaptive_sampling = True; c.adaptive_threshold = 0.03
    sc.render.resolution_x = a.w; sc.render.resolution_y = a.h; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "8"
    a.out.mkdir(parents=True, exist_ok=True)
    todo = [int(x) for x in a.only.split(",")] if a.only else range(a.frames)
    secs = []
    for i in todo:
        path = a.out / f"spin-{i:04d}-raw.png"
        if path.exists() and not a.only: continue
        sc.frame_set(1 + round(i * 216 / a.frames))
        th = 2 * math.pi * i / a.frames - math.pi / 2          # start in front of the bird (-Y) and walk round it
        cam.location = (RADIUS * math.cos(th), RADIUS * math.sin(th), HEIGHT)
        cam.rotation_euler = (Vector(TARGET) - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = str(path); t = time.time(); bpy.ops.render.render(write_still=True); secs.append(round(time.time() - t, 1))
        print("SPIN", i, secs[-1], "s", flush=True)
    if not a.only:
        rec = {"schema": "gobbler.blender-spin/1", "blender": bpy.app.version_string, "engine": "Cycles", "device": "CPU", "frames": a.frames,
               "resolution": [a.w, a.h], "samples_max": a.samples, "adaptive_threshold": 0.03, "denoiser": "OpenImageDenoise", "seed": 7,
               "camera": {"radius_m": RADIUS, "height_m": HEIGHT, "target": TARGET, "lens_mm": LENS, "fstop": 4.0},
               "scene_clock": "216 scene frames over the turn", "added_in_blender": rg.ADDED + ["the orbit camera"],
               "seconds_this_run": {"frames_rendered": len(secs), "total": round(sum(secs), 1), "mean": round(sum(secs) / max(1, len(secs)), 1)}}
        (a.out / "blender-spin.json").write_text(json.dumps(rec, indent=1) + "\n")


if __name__ == "__main__":
    main()
