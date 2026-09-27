from pathlib import Path
import json,io,contextlib
import two_hub_blocks as tb
from balanced_conductance import run
records=json.loads(Path(__file__).with_name('BLOCK_STRESS_RESULTS.json').read_text());out=[]
for idx,rec in enumerate(records):
 m,P=tb.example(rec['same'],0);base=tb.structure(m,P);L=rec['L'];rb=[sum(L[b])+sum(b in bs for bs in base[6])-2 for b in range(5)];data=(*base[:3],rb,L,*base[5:])
 with contextlib.redirect_stdout(io.StringIO()):d=run(f"{rec['same']}_{rec['case']}",m,P,data)
 out.append(d)
 if d['worst_cut_gap']>1e-6 or d['max_residual']>1e-6 or d['min_leaf_deficit']< -1e-6:
  print(json.dumps(d),flush=True);break
 if idx%50==0:print(idx,'passed',flush=True)
Path(__file__).with_name('CONDUCTANCE_STRESS.json').write_text(json.dumps(out)+'\n');print('tested',len(out),flush=True)
