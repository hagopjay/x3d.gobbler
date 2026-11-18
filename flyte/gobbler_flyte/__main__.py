"""python -m gobbler_flyte tick|answer|status ...  (run from the flyte/ folder)"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runner import tick, utc_now
from .budget import parse_allowance


def main(argv=None):
    ap = argparse.ArgumentParser(prog="gobbler_flyte")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tick", help="one clock tick: resume answered cycles, start a new one")
    t.add_argument("--state", default="state")
    t.add_argument("--mode", choices=["live", "offline"], default="offline")
    t.add_argument("--loom", default=None, help="path to an x3d.loom checkout for Witness target probes")
    a = sub.add_parser("answer", help="local mode: answer a waiting cycle as an authorized human")
    a.add_argument("cycle", type=int)
    a.add_argument("text", help="A, B, C, ok, 'A send', or 'OK $0.03/day'")
    a.add_argument("--by", required=True)
    a.add_argument("--state", default="state")
    s = sub.add_parser("status")
    s.add_argument("--state", default="state")
    args = ap.parse_args(argv)
    if args.cmd == "tick":
        print(json.dumps(tick(args.state, mode=args.mode, loom_dir=args.loom), indent=1))
    elif args.cmd == "answer":
        d = Path(args.state) / "answers"
        d.mkdir(parents=True, exist_ok=True)
        name = "allowance.json" if parse_allowance(args.text) is not None else f"{args.cycle:05d}.json"
        (d / name).write_text(json.dumps({"by": args.by, "text": args.text, "utc": utc_now()}))
        print("recorded; the next tick reads it")
    else:
        m = json.loads((Path(args.state) / "memory.json").read_text())
        print(json.dumps({"cycles": m["cycles"], "waiting": [k for k, v in m["threads"].items() if v["status"] == "waiting"]}, indent=1))


if __name__ == "__main__":
    main()
