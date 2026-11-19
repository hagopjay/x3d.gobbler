"""C probe: private-link redaction applies to a feed title as well as URL/summary."""
import argparse,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);a=p.parse_args()
sys.path.insert(0,str(a.repo/'flyte'))
from gobbler_flyte.sources import parse
body=json.dumps({'hits':[{'objectID':'test','title':('X3D https://' + 'claude.ai' + '/code/private-example'),'url':'https://example.org'}]}).encode()
item=parse('hn',{'id':'hn-x3d'},body)[0]
print(json.dumps({'grade':'C','title':item['title']}))
assert 'private-example' not in item['title'], 'private link survives in title'
