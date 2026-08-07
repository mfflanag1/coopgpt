from fractions import Fraction as F
import sys, audit, z3
from lmax import lmax
sys.path.insert(0,'/private/tmp/n6-tb-pr.tyMp8O/coopgames/src')
import verify_rich_block_family as RB

def exact_lp(n,v):
    full=(1<<n)-1
    x=[z3.Real(f"x{i}") for i in range(n)]
    base=[z3.Sum(x)==audit.to_z3(v[full])]+[
        z3.Sum([x[i] for i in range(n) if S>>i&1])>=audit.to_z3(v[S]) for S in range(1,full)]
    for S in range(1,full):
        o=z3.Optimize(); o.add(base)
        hh=o.minimize(z3.Sum([x[i] for i in range(n) if S>>i&1]))
        if o.check()!=z3.sat: return False
        if audit.rat(o.lower(hh))!=v[S]: return False
    return True

print(f"{'m,h':>6}{'n':>4}{'exact':>7}{'Lmin=claim':>11}{'Lmax=claim':>11}{'v(R)':>6}{'R slack':>9}{'L1':>9}{'=formula':>9}")
for (m,h) in [(4,1),(5,1),(6,1),(7,1),(5,2),(6,2),(6,3)]:
    pts=RB.generators(m,h); n=len(pts[0])
    v=[F(q) for q in RB.lower_envelope(pts)]
    full=(1<<n)-1; R=sum(1<<i for i in range(m,n))
    ex=exact_lp(n,v)
    mn=audit.lmin(n,v); mx=lmax(n,v)
    mn_claim=[F(h)]*m+[F(m-2)]*h
    c=F(h*(m-1),h+1); a=F(h*h*(m-1),(h+1)*(m-2))
    mx_claim=[(c if (i in (2,3) or i>=m) else a) for i in range(n)]
    l1=sum(abs(mn[i]-mx[i]) for i in range(n)); exp=F(4*h*(m-h-2),h+1)
    slack=sum(mn[i] for i in range(n) if R>>i&1)-v[R]
    print(f"{m},{h:>3}{n:>4}{str(ex):>7}{str(mn==mn_claim):>11}{str(mx==mx_claim):>11}"
          f"{str(v[R]):>6}{str(slack):>9}{str(l1):>9}{str(l1==exp):>9}")
