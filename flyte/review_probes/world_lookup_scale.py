"""C algorithmic scale probe on 10k synthetic storage rows; not 10k admitted scenes."""
import argparse,hashlib,json,sys,tempfile,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--size',type=int,default=10000);a=p.parse_args()
sys.path.insert(0,str(a.repo/'flyte'))
from gobbler_flyte.accrete_bridge import World
with tempfile.TemporaryDirectory() as d:
 w=World(Path(d)/'world.sqlite')
 rows=[]
 for n in range(1,a.size+1):
  h=hashlib.sha256(str(n).encode()).hexdigest()
  body=json.dumps({'generation':{'op':f'bench-{n}'},'title':'synthetic storage fixture','plan':{}})
  rows.append((n,h,'0'*64,body,'<Group/>','<Group/>','<X3D/>','2026-11-18T00:00:00Z'))
 with w.store.connect() as db:
  db.executemany('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)',rows)
 calls=[0]
 def profile(frame,event,arg):
  if event=='call' and frame.f_code.co_name in ('strict_json','loads'):
   calls[0]+=1
 started=time.perf_counter();sys.setprofile(profile)
 found=w.find_op(f'bench-{a.size}')
 sys.setprofile(None);elapsed=time.perf_counter()-started
 print(json.dumps({'grade':'C','synthetic_rows':a.size,'found':found['n'],'json_parse_calls':calls[0],'seconds':elapsed,'scope':'lookup only; rows bypassed admission; no throughput or validity claim'}))
 assert found['n']==a.size
 assert calls[0]<=5, 'one operation lookup parses the whole archive'
