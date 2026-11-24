#!/usr/bin/env python3
"""Finish the Cycles frames: a soft glow on the brightest parts, then WebP. Declared post, not render.

    python3 mascot/glass/blender/finish_stills.py --raw /tmp/final --out mascot/glass/stills

The glow is a screen blend of two Gaussian blurs of the pixels above 0.72 luminance (radii 0.6% and 2.2% of the
width, strengths 0.55 and 0.35). Needs Pillow and numpy. The raw frame's SHA-256 goes into the receipt.
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter


def glow(img: Image.Image) -> Image.Image:
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    lum = a @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    mask = np.clip((lum - 0.72) / 0.28, 0, 1)[..., None]
    hi = Image.fromarray((a * mask * 255).astype(np.uint8))
    out = a
    for frac, k in ((0.006, 0.55), (0.022, 0.35)):
        b = np.asarray(hi.filter(ImageFilter.GaussianBlur(img.width * frac)), dtype=np.float32) / 255.0 * k
        out = 1 - (1 - out) * (1 - np.clip(b, 0, 1))
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raw", type=Path, required=True); ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(); a.out.mkdir(parents=True, exist_ok=True)
    rec = json.loads((a.raw / "blender-render.json").read_text())
    for r in rec["renders"]:
        raw = a.raw / r["file"]; name = r["file"].replace("-raw.png", ".webp")
        r["raw_sha256"] = hashlib.sha256(raw.read_bytes()).hexdigest()
        im = glow(Image.open(raw)); im.save(a.out / name, "WEBP", quality=90, method=6)
        r["file"] = name; r["bytes"] = (a.out / name).stat().st_size
    rec["post"] = "glow: screen blend of two Gaussian blurs of pixels above 0.72 luminance (finish_stills.py); WebP quality 90"
    (a.out / "blender-render.json").write_text(json.dumps(rec, indent=1) + "\n"); print(json.dumps(rec["renders"]))


main()
