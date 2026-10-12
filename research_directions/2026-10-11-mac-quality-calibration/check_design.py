"""Independent source-row/gold and cross-study table-disjointness checks."""
import hashlib,json,re
from pathlib import Path
BASE=Path(__file__).resolve().parent

def check(base=BASE):
 sets=[];counts=[]
 for name in ('development.json','confirmation.json'):
  jobs=json.loads((base/name).read_text());seen=set()
  for j in jobs:
   table='\n'.join(f"{r['id']} value={r['value']} flag={r['flag']}" for r in j['rows'])
   expected={'records':[{'id':a,'value':b} for a,b in re.findall(r'^(R\d{4}) value=(\d{3}) flag=KEEP$',table,re.M)]}
   if expected!=j['expected']:raise ValueError('gold mismatch')
   h=hashlib.sha256(table.encode()).hexdigest()
   if h in seen:raise ValueError('duplicate task')
   seen.add(h)
  sets.append(seen);counts.append(len(seen))
 if sets[0]&sets[1]:raise ValueError('development/confirmation overlap')
 old=base.parent/'2026-10-11-mac-mixed-energy'/'traces'
 if not old.is_dir():raise ValueError('Original trace directory missing')
 oldset=set()
 for p in old.glob('*.json'):
  for j in json.loads(p.read_text()):
   table='\n'.join(re.findall(r'^R\d{4} value=\d{3} flag=(?:KEEP|DROP)$',j['prompt'],re.M));oldset.add(hashlib.sha256(table.encode()).hexdigest())
 if any(s&oldset for s in sets):raise ValueError('overlap with originalstudy')
 return dict(development=counts[0],confirmation=counts[1],original_unique_tables=len(oldset),disjoint=True)
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
