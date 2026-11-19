import argparse, json, sys, tempfile
from pathlib import Path

ap=argparse.ArgumentParser(); ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]); args=ap.parse_args()
sys.path.insert(0,str(args.repo/'flyte'))
from recovery_common import stop_batch
with tempfile.TemporaryDirectory(prefix='gobbler-recovery-stop-') as d:
    print(json.dumps(stop_batch(Path(d)),indent=2))
