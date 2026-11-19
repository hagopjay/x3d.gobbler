import argparse, json, sys, tempfile
from pathlib import Path

ap=argparse.ArgumentParser(); ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]); args=ap.parse_args()
sys.path.insert(0,str(args.repo/'flyte'))
from recovery_common import provenance_loss
with tempfile.TemporaryDirectory(prefix='gobbler-recovery-provenance-') as d:
    print(json.dumps(provenance_loss(Path(d)),indent=2))
