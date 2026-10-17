from fractions import Fraction as Q
from random import Random
from pathlib import Path
import itertools,json
rng=Random(711017);checks=0;coalitions=0

def value(P,H,rs,vs,qs):
    # Exact dual breakpoints of min P*p+H*q+sum caps*(v-r*p-q)+.
    lines=[(Q(1),Q(0),Q(0)),(Q(0),Q(1),Q(0))]+[(r,Q(1),v) for r,v in zip(rs,vs)]
    pts=[(Q(0),Q(0))]
    for l,m in itertools.combinations(lines,2):
        a,b,c=l;d,e,f=m;det=a*e-b*d
        if not det:continue
        p=(c*e-b*f)/det;q=(a*f-c*d)/det
        if p>=0 and q>=0:pts.append((p,q))
    return min(P*p+H*q+sum(cap*max(Q(0),v-r*p-q) for r,v,cap in zip(rs,vs,qs)) for p,q in pts)

for trial in range(700):
    M=rng.randrange(1,9)
    aa=[Q(rng.randrange(1,10),rng.randrange(1,5)) for _ in range(M)]
    bb=[Q(rng.randrange(1,10),rng.randrange(1,5)) for _ in range(M)]
    vv=[Q(rng.randrange(1,8),rng.randrange(1,5)) for _ in range(M)]
    rs=[a/b for a,b in zip(aa,bb)];vs=[v/b for v,b in zip(vv,bb)]
    minimum=min(rs);rounded=[]
    for r in rs:
        x=minimum
        while 2*x<=r:x*=2
        assert x<=r<2*x
        rounded.append(x)
    groups={r:[j for j,x in enumerate(rounded) if x==r] for r in set(rounded)}
    T=len(groups)
    owners=[[Q(rng.randrange(6),rng.randrange(1,4)) for _ in range(2+M)] for _ in range(4)]
    for mask in (15,1,3,5,10):
        caps=[sum(owners[i][v] for i in range(4) if mask>>i&1) for v in range(2+M)]
        P,H=caps[:2];qs=[bb[j]*caps[j+2] for j in range(M)]
        original=value(P,H,rs,vs,qs);proxy=value(P,H,rounded,vs,qs)
        assert original<=proxy<=2*original
        isolated=Q(0);combined=[Q(0)]*M
        for r,inds in groups.items():
            budget=min(P/r,H);left=budget
            for j in sorted(inds,key=lambda j:-vs[j]):
                z=min(left,qs[j]);left-=z
                isolated+=vs[j]*z;combined[j]=z/T
        assert proxy<=isolated<=T*proxy
        assert sum(rounded[j]*combined[j] for j in range(M))<=P
        assert sum(combined)<=H
        assert all(combined[j]<=qs[j] for j in range(M))
        assert sum(rs[j]*combined[j]/2 for j in range(M))<=P
        assert sum(vs[j]*combined[j]/2 for j in range(M))==isolated/(2*T)
        checks+=1;coalitions+=mask!=15
out={'status':'PASS','exact_two_dimensional_LP_comparisons':checks,
 'proper_coalition_profiles':coalitions,'branches_up_to':8,
 'checks':['true<=rounded<=2true','isolated type value sandwich','weighted feasible true plan'],
 'limits':'Fixed-owner incentives use the cited exact three-pool/harmonic theorems, not these finite value checks.'}
Path(__file__).with_name('TWO_COMMON_RATIO_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
