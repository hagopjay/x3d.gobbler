#!/usr/bin/env python3
"""Fail if tracked text contains things that must not be published: session links, local home paths in code, key-shaped strings."""
import pathlib, re, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
PATTERNS = {
    "claude.ai session/project link": r"claude\.ai/(code|project|artifact)/",
    "key-shaped string": r"(AIza[0-9A-Za-z_-]{30,}|sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY)",
    "local home path in code": r"/Users/[a-z]+/",
}
CODE = {".py", ".js", ".cjs", ".html", ".yml", ".sh", ".css"}
files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
bad = []
for f in files:
    p = ROOT / f
    if f.startswith("vendor/") or p.suffix in {".png", ".wav", ".jpg", ".webp"} or not p.is_file() or p.stat().st_size > 8_000_000:
        continue
    t = p.read_text(encoding="utf-8", errors="ignore")
    for name, pat in PATTERNS.items():
        if name == "local home path in code" and p.suffix not in CODE:
            continue            # archived receipts keep their original strings; they are hash-bound and not code
        for m in re.finditer(pat, t):
            bad.append(f"{f}: {name}: {t[max(0, m.start()-20):m.end()+20]!r}")
print("\n".join(bad) or "leak sweep clean: %d tracked files" % len(files))
sys.exit(1 if bad else 0)
