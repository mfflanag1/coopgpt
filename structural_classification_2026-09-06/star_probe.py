"""Bounded exact screen of larger stars; discovery only, not exhaustive evidence."""
from fractions import Fraction as F
from pathlib import Path
import json, random
from probe import solve

root=Path(__file__).resolve().parent
rng=random.Random(6072319);edges=[(0,1),(0,2),(0,3)];records=[];best=F(1)
out=root/'STAR_PROBE.json';out.write_text('{"status":"RUNNING"}\n')
for trial in range(120):
    m=4
    alphabet=([0,1,2] if trial%3==0 else ([0,0,0,1]if trial%3==1 else [0,1,2,5,11,20]))
    matrices=[[[rng.choice(alphabet)for _ in range(m)]for _ in range(m)]for _ in edges]
    row=solve(edges,matrices,m)
    if row is not None:
        records.append(row)
        if F(row['ratio'])<best:
            best=F(row['ratio']);print(json.dumps({'trial':trial,'ratio':str(best)}),flush=True)
    out.write_text(json.dumps({'status':'RUNNING','seed':6072319,'attempts':trial+1,'records':records},indent=2)+'\n')
    if best<F(1,4):break
out.write_text(json.dumps({'status':'PASS','scope':'non-exhaustive seeded exact screen','seed':6072319,'attempts':trial+1,'minimum_ratio':str(best),'records':records},indent=2)+'\n')
print(json.dumps({'status':'PASS','attempts':trial+1,'minimum_ratio':str(best)}))
