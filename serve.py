#!/usr/bin/env python3
"""Serve the entire archive layout on loopback; no installation or internet needed."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8831)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    print(f'Gobbler: http://localhost:{args.port}/gobbler-flyte/', flush=True)
    print(f'Atlas:   http://localhost:{args.port}/flywheel-review/ATLAS-INSIGHTS.html', flush=True)
    try:
        ThreadingHTTPServer(('127.0.0.1', args.port), partial(SimpleHTTPRequestHandler, directory=str(root))).serve_forever()
    except KeyboardInterrupt:
        pass
