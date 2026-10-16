"""Independent partition S>=2; deliberately excludes all one-cap rows."""
from fractions import Fraction as F
from pathlib import Path
import importlib.util,json,time
BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('extended',BASE/'build_certificate.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.CAP_US=[]
start=time.monotonic();cells=[];ns=64;nd=32
for si in range(ns):
 lo=2+(b.PB+b.CB-2)*F(si,ns);hi=2+(b.PB+b.CB-2)*F(si+1,ns)
 for di in range(nd):
  dl=b.DB*F(di,nd)**2;dh=b.DB*F(di+1,nd)**2
  cells.append(b.solve(lo,hi,dl,dh))
 if si%8==7:print(json.dumps({'S_done':si+1,**b.STATS,'max':float(b.MAXIMUM),'elapsed':time.monotonic()-start}),flush=True)
result={'target':'8/5','NS':ns,'ND':nd,'delta_partition':'quadratic','S_lower':'2','S_upper':str(b.PB+b.CB),'CAP_US':[],'CAP_SS':list(map(str,b.CAP_SS)),'ETAS':list(map(str,b.ETAS)),'base_rows':len(b.base_rows(F(2),b.PB+b.CB,F(0),b.DB)[0]),'statistics':b.STATS,'max_upper':str(b.MAXIMUM),'cells':cells}
(BASE/'high_S_certificate.json').write_text(json.dumps(result,separators=(',',':')))
print(json.dumps({'finished':True,**b.STATS,'max':float(b.MAXIMUM),'elapsed':time.monotonic()-start},indent=2))
