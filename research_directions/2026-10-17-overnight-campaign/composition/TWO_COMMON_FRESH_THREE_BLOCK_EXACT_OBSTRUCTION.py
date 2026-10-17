from fractions import Fraction as Q
from itertools import combinations
import random,json
from pathlib import Path
R=random.Random(314171)
def dot(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))
def det(a,b,c):return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
def solve(mat,rhs):
 D=det(*mat)
 if not D:return None
 return tuple(det(*[tuple(rhs[i] if k==j else mat[i][k] for k in range(3)) for i in range(3)])/D for j in range(3))
def hull2(points):
    # Exact monotone-chain convex hull. The mapping to the two projected
    # coordinates is injective on a plane with nonzero omitted normal.
    pts=sorted(points)
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[]
    for p in pts:
        while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
        lo.append(p)
    up=[]
    for p in reversed(pts):
        while len(up)>=2 and cross(up[-2],up[-1],p)<=0:up.pop()
        up.append(p)
    return lo[:-1]+up[:-1]
def volume(hs):
    vs=set()
    for trip in combinations(hs,3):
        x=solve([a for a,b in trip],[b for a,b in trip])
        if x is not None and all(dot(a,x)<=b for a,b in hs):vs.add(x)
    vs=sorted(vs)
    if len(vs)<4:return Q(0)
    origin=vs[0]
    if not any(det(*[tuple(v[j]-origin[j] for j in range(3)) for v in tri]) for tri in combinations(vs[1:],3)):
        return Q(0)
    center=tuple(sum(v[j] for v in vs)/len(vs) for j in range(3))
    facets=[];seen=set();edges={};total=Q(0)
    for normal,bound in hs:
        active=[i for i,v in enumerate(vs) if dot(normal,v)==bound]
        if len(active)<3 or not any(normal):continue
        omit=next(j for j in range(3) if normal[j]);axes=[j for j in range(3) if j!=omit]
        projection={tuple(vs[i][j] for j in axes):i for i in active}
        polygon=[projection[p] for p in hull2(projection)]
        if len(polygon)<3:continue
        key=frozenset(polygon)
        if key in seen:continue
        seen.add(key);facets.append(polygon)
        assert dot(normal,center)<bound
        for u,v in zip(polygon,polygon[1:]+polygon[:1]):
            e=tuple(sorted((u,v)));edges[e]=edges.get(e,0)+1
        for k in range(1,len(polygon)-1):
            tri=(polygon[0],polygon[k],polygon[k+1])
            vec=[tuple(vs[i][j]-center[j] for j in range(3)) for i in tri]
            total+=abs(det(*vec))/6
    assert all(n==2 for n in edges.values())
    assert len(vs)-len(edges)+len(facets)==2
    return total

def vertices(a,b,w):
 lines=[(Q(1),Q(0),Q(0)),(Q(0),Q(1),Q(0)),*zip(a,b,w)];vs=set()
 for (aa,bb,ww),(aaa,bbb,www) in combinations(lines,2):
  D=aa*bbb-aaa*bb
  if D:
   p=(ww*bbb-www*bb)/D;q=(aa*www-aaa*ww)/D
   if min(p,q)>=0:vs.add((p,q))
 return [(p,q)+tuple(max(Q(0),wj-aj*p-bj*q) for aj,bj,wj in zip(a,b,w)) for p,q in sorted(vs)]
def rule(C,gs):
 P,Qq,*c=C
 aff=[(P*g[0],Qq*g[1],dot(c,g[2:])) for g in gs]
 ans=[Q(0)]*len(C);vv=[]
 cube=[]
 for j in range(3):
  cube.append((tuple(Q(k==j) for k in range(3)),Q(1)))
  cube.append((tuple(Q(-1 if k==j else 0) for k in range(3)),Q(0)))
 for idx,g in enumerate(gs):
  hs=cube+[(tuple(x-y for x,y in zip(aff[idx],aa)),Q(0)) for k,aa in enumerate(aff) if k!=idx]
  v=volume(hs);vv.append(v)
  for j in range(len(C)):ans[j]+=v*g[j]
 assert sum(vv)==1,(C,vv)
 return ans,vv
A=(Q(1,100),Q(1,100),Q(1,400));B=(Q(1),Q(1,4),Q(1));W=tuple(a+b for a,b in zip(A,B));gs=vertices(A,B,W)
C=(Q(1,100),Q(1),Q(1,4),Q(4),Q(1));CC=(Q(1,75),Q(1),Q(1,4),Q(4),Q(1))
p,v=rule(C,gs);pp,vv=rule(CC,gs)
a=(C[0],Q(0),Q(0),Q(0),Q(1));aa=(CC[0],Q(0),Q(0),Q(0),Q(1))
old=dot(a,p);new=dot(aa,pp)
assert old>new
assert v==[Q(5,54),Q(4,459),Q(1,408),Q(11,96),Q(11383,24480),Q(1,5),Q(1,30),Q(1,12)]
assert vv==[Q(28,243),Q(64,4131),Q(2,459),Q(4,27),Q(151931,330480),Q(206,1215),Q(1,40),Q(1,16)]
result={'status':'PASS','method':'Exact rational halfspace-intersection vertices, rational projected convex facet hulls, closed boundary checks, exact tetrahedral determinants. No floating-point geometry.',
'activity_a':list(map(str,A)),'activity_b':list(map(str,B)),'profits':list(map(str,W)),
'old_profile':list(map(str,C)),'new_profile':list(map(str,CC)),
'dual_gradients':[list(map(str,g)) for g in gs],
'old_cell_volumes':list(map(str,v)),'new_cell_volumes':list(map(str,vv)),
'old_prices':list(map(str,p)),'new_prices':list(map(str,pp)),
'owner_A_old_bundle':list(map(str,a)),'owner_A_new_bundle':list(map(str,aa)),
'owner_A_old_payment':str(old),'owner_A_new_payment':str(new),'strict_incentive_loss':str(old-new)}
Path(__file__).with_name('TWO_COMMON_FRESH_THREE_BLOCK_EXACT_OBSTRUCTION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
