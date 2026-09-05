from fractions import Fraction as F
from itertools import combinations
import json
from pathlib import Path

def need(c,msg):
    if not c: raise RuntimeError(msg)
def sums(v):
    return {S:sum((v[i] for i in S),F(0)) for size in range(len(v)+1) for S in combinations(range(len(v)),size)}
U=(F(2),F(0),F(0));V=(F(0),F(1),F(1));Y=(F(1),F(1),F(0))
a,b,c=map(sums,(U,V,Y));worth={S:min(a[S],b[S]) for S in a}
need(all(c[S]>=worth[S] for S in a) and sum(Y)==2,'witness not core')
need(Y[1]!=Y[2],'witness on generator segment')
# Convexity removed: both points attain each first-stage objective in the 2-point set.
x=(F(1,2),F(1,2),F(0),F(0));z=(F(0),F(0),F(1,2),F(1,2))
need(min(x)==min(z)==0 and max(x)==max(z)==F(1,2),'wrong first stages')
need(sum(min(a,b) for a,b in zip(x,z))<F(1,3),'not a counterexample')
# Nonnegativity removed: translate every coordinate of the valid m=2,r=3 segment.
x0=[F(2,3)]+[F(1,3)]*7
z0=[F(1,2)]+[F(1,4)]*4+[F(1,2)]*3
xs=[a-F(1,3) for a in x0];zs=[a-F(1,3) for a in z0]
T=sum(xs); overlap=sum(min(a,b) for a,b in zip(xs,zs))
need(T==sum(zs)==F(1,3) and overlap==F(-1,6),'translation arithmetic failed')
result={'status':'PASS','generating_hull_failure':{'U':list(map(str,U)),'V':list(map(str,V)),'off_segment_core_point':list(map(str,Y)),'worth':{str(S):str(v) for S,v in worth.items()}},'nonconvex_overlap_failure':{'x':list(map(str,x)),'z':list(map(str,z)),'overlap':'0','required_lower_bound':'1/3'},'signed_convex_overlap_failure':{'x':list(map(str,xs)),'z':list(map(str,zs)),'total':str(T),'overlap':str(overlap),'required_lower_bound':'1/21','why_optimal':'Uniform coordinate translation preserves sorted lexicographic comparisons and each first-stage arg optimum on the translated valid segment.'}}
Path(__file__).with_name('hypothesis_controls.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
