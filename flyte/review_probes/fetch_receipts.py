"""C probe: every configured fetch has an auditable destination, without network."""
import argparse,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);a=p.parse_args()
sys.path.insert(0,str(a.repo/'flyte'))
from gobbler_flyte.sources import fetch
cfg=json.loads((a.repo/'flyte/config/flyte.json').read_text())
rows=[fetch(s,'offline') for s in cfg['sources']]
missing=[r['source'] for r in rows if not r.get('fetch_url') or r.get('transport')!='fixture']
print(json.dumps({'grade':'C','configured':len(rows),'missing_receipts':missing}))
assert not missing, 'fetches have no per-attempt destination/transport receipts'
