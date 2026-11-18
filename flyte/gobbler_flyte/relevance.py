"""Is this about the X3D file format, or one of its namesakes?

Measured on the 18 Nov 2026 01:46Z snapshot in fixtures/feeds (counts in DESIGN.md):
an HN title search for "x3d" is mostly AMD Ryzen X3D chips, the arXiv query is
mostly the X3D video-recognition network, and an HN date search for "x3d"
returns stories that only contain "3D". The rules below are that lesson turned
into code: the Scout's first flywheel turn was a rule, not a scene.
"""
from __future__ import annotations

import re

STRONG = re.compile(r"\b(x_ite|x3dom|vrml|web3d|extensible 3d|castle game engine|h-?anim|humanoid animation|"
                    r"iso/iec 1977[5-7]|declarative 3d|x3dv|x3dj|\.x3d\b)", re.I)
WEAK = re.compile(r"\bx3d (?:scene|file|format|standard|spec|exporter|importer|model|world|browser|node)s?\b", re.I)
BARE = re.compile(r"(?<![\w-])x3d(?![\w-])", re.I)
AMD = re.compile(r"\b(ryzen|amd|v-?cache|cache|cpu|chip|epyc|zen ?\d|\d{3,4}x3d|x3d cpu|laptop|sku|gaming)\b", re.I)
VIDEO = re.compile(r"\b(action recognition|video|kinetics|x3d-(?:xs|s|m|l|xl)|feichtenhofer|temporal|clip|"
                   r"spatiotemporal|activity recognition)\b", re.I)
VARIANT = re.compile(r"\bx3d-(?:xs|s|m|l|xl|ugt|style|slowfast)\b|\bx3d (?:cnn|backbone|network|dataset)\b", re.I)
GRAPHICS = re.compile(r"\b(webgpu|webgl|three\.js|babylon|gltf|gaussian splat|blender|usd|openusd|scene graph|3d web)\b", re.I)


def classify(text: str, trust: str = "open") -> dict:
    """Return {'label', 'score', 'why'}. Labels: x3d, adjacent, amd-x3d, x3d-video-net, noise."""
    t = text or ""
    why = []
    if trust in ("x3d-home", "family"):
        return {"label": "x3d", "score": 0.9 if trust == "x3d-home" else 0.8, "why": [f"trusted source ({trust})"]}
    strong, weak = STRONG.findall(t), WEAK.findall(t)
    bare = bool(BARE.search(t))
    amd = AMD.findall(t)
    vid = VIDEO.findall(t)
    gfx = GRAPHICS.findall(t)
    if VARIANT.search(t) and not strong:
        return {"label": "x3d-video-net", "score": 0.0, "why": ["X3D model variant or dataset name: " + VARIANT.search(t).group(0)]}
    if weak and not strong and (vid or amd):
        weak = []                         # "X3D models" next to video or chip words is the namesake, not the format
    fmt = strong + weak
    if fmt:
        why.append("format words: " + ", ".join(sorted({f.lower() for f in fmt})[:4]))
        return {"label": "x3d", "score": min(1.0, 0.7 + 0.1 * len(fmt)), "why": why}
    if (bare or re.search(r"\d{3,4}x3d\b", t, re.I)) and amd:
        return {"label": "amd-x3d", "score": 0.0, "why": ["X3D next to chip words: " + ", ".join(sorted({a.lower() for a in amd})[:3])]}
    if bare and vid:
        return {"label": "x3d-video-net", "score": 0.0, "why": ["X3D next to video-recognition words: " + ", ".join(sorted({v.lower() for v in vid})[:3])]}
    if bare:
        return {"label": "x3d", "score": 0.55, "why": ["bare 'X3D' with no namesake words (weak)"]}
    if gfx:
        return {"label": "adjacent", "score": 0.35 + 0.05 * min(len(gfx), 3), "why": ["graphics words: " + ", ".join(sorted({g.lower() for g in gfx})[:3])]}
    return {"label": "noise", "score": 0.0, "why": ["no X3D or graphics words"]}
