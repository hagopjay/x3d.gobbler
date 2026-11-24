#!/usr/bin/env python3
"""Count what the mascot wears from the Loom itself, so the bird grows when the Loom does.

    python3 mascot/loom_counts.py --loom ../x3d.loom --out mascot/glass/counts.json

laws            rows of the table in LOOM-v1.md section 3
failure_modes   rows of the table in LOOM-v1.md section 8 (a repeated number is refused; a gap is reported)
theses          THESES in the pinned AI Engineering Atlas (flyte/atlas/aie-atlas.json)
Standard library only. The Loom checkout's commit is recorded beside the counts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROW = re.compile(r"^\|\s*(\d+)\s*\|")


def section(text: str, start: str, end: str) -> list[str]:
    lines = text.splitlines()
    a = next(i for i, l in enumerate(lines) if l.startswith(start))
    b = next(i for i, l in enumerate(lines) if i > a and l.startswith(end))
    return lines[a:b]


def numbered_rows(lines: list[str]) -> list[int]:
    return [int(m.group(1)) for l in lines if (m := ROW.match(l))]


def count(loom: Path) -> dict:
    raw = (loom / "LOOM-v1.md").read_bytes()
    text = raw.decode("utf-8")
    laws = numbered_rows(section(text, "## 3. ", "## 4. "))
    modes = numbered_rows(section(text, "## 8. ", "## 9. "))
    gaps = {}
    for name, rows in (("laws", laws), ("failure_modes", modes)):
        if len(set(rows)) != len(rows):
            raise SystemExit(f"{name}: a number is used twice: {sorted(n for n in set(rows) if rows.count(n) > 1)}")
        gaps[name] = sorted(set(range(1, max(rows) + 1)) - set(rows))   # two lanes can land out of order: a gap is reported, not refused
    atlas = json.loads((ROOT / "flyte" / "atlas" / "aie-atlas.json").read_text(encoding="utf-8"))
    head = subprocess.run(["git", "-C", str(loom), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() or None
    return {"schema": "gobbler.loom-counts/1", "laws": len(laws), "failure_modes": len(modes), "theses": len(atlas["THESES"]),
            "highest": {"laws": max(laws), "failure_modes": max(modes)}, "gaps": gaps,
            "source": {"loom_commit": head, "loom_file": "LOOM-v1.md", "loom_file_sha256": hashlib.sha256(raw).hexdigest(),
                       "atlas_rev": atlas["rev"]}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--loom", type=Path, required=True); ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    c = count(a.loom)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(c, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(c))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
