#!/usr/bin/env python3
"""Materialise the pinned x3d.docs tree that the full Atlas witness needs.

The Atlas reads `docs/learn` and the stdlib helpers in `docs/tools-shared` from x3d.docs at the commit written in
flywheel-review/atlas/src/DOCS.sha. That tree is 28 MB, so it is not committed; this script rebuilds it:

    python3 tools/fetch_pins.py                    # shallow-fetch the pin from GitHub (public repo, no token)
    python3 tools/fetch_pins.py --from ~/x3d.docs  # or take it from a local clone that has the commit

Result: flywheel-review/src/x3d.docs/docs/...   (git-ignored). Idempotent; verifies the sha it extracted.
"""
import argparse, io, pathlib, shutil, subprocess, sys, tarfile, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PIN = (ROOT / "flywheel-review/atlas/src/DOCS.sha").read_text().strip()
DEST = ROOT / "flywheel-review/src/x3d.docs"
URL = "https://github.com/hagopjay/x3d.docs.git"
WANT = ["docs/learn", "docs/tools-shared"]     # what build_atlas.py and check_atlas.py read; add paths here if they grow


def run(*a, **k):
    return subprocess.run(a, check=True, capture_output=True, **k)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", help="a local clone of x3d.docs containing the pinned commit")
    a = ap.parse_args()
    if (DEST / ".pin").is_file() and (DEST / ".pin").read_text().strip() == PIN:
        print(f"already at {PIN[:7]}: {DEST}")
        return 0
    with tempfile.TemporaryDirectory() as td:
        repo = pathlib.Path(a.src).expanduser() if a.src else pathlib.Path(td) / "docs.git"
        if not a.src:
            run("git", "init", "-q", "--bare", str(repo))
            run("git", "-C", str(repo), "fetch", "-q", "--depth=1", URL, PIN)    # fetching a sha needs a server that allows it (GitHub does)
        tar = run("git", "-C", str(repo), "archive", PIN, *WANT).stdout
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(DEST, filter="data")
    (DEST / ".pin").write_text(PIN + "\n")
    print(f"x3d.docs@{PIN[:7]} -> {DEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
