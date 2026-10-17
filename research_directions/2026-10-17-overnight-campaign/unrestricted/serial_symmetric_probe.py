"""Discovery: serial allocation for symmetric min-linear technologies."""
import random, json
from fractions import Fraction as Q
from pathlib import Path

def f(c,W):
    c=sorted(c)
    return min(sum(a*b for a,b in zip(w,c)) for w in W)
def serial(c,W):
    y=[Q(0)]*len(c);last=Q(0);old=Q(0)
    for t in sorted(set(c)):
        if t<=0: continue
        active=[i for i,x in enumerate(c) if x>=t]
        now=f([min(t,x) for x in c],W)
        for i in active:y[i]+=(now-old)/len(active)
        last=t;old=now
    return y
def run(seed=173,trials=10000):
    rng=random.Random(seed);out={'seed':seed,'trials':trials,'status':'NUMERICAL_OR_EXACT_FINITE_DISCOVERY'}
    for it in range(trials):
        n=rng.randrange(3,9);W=[sorted([Q(rng.randrange(0,21),rng.randrange(1,6)) for _ in range(n)],reverse=True) for __ in range(rng.randrange(1,9))]
        c=[Q(rng.randrange(0,31),rng.randrange(1,6)) for _ in range(n)];y=serial(c,W)
        if sum(y)!=f(c,W):raise RuntimeError('budget')
        for mask in range(1,1<<n):
            v=f([c[i] if mask>>i&1 else 0 for i in range(n)],W)
            paid=sum(y[i] for i in range(n) if mask>>i&1)
            if paid<v:
                out.update({'failure':'coverage','iteration':it,'W':W,'c':c,'y':y,'coalition':mask,'value':v,'paid':paid});return out
        for i in range(n):
            bigger=c.copy();bigger[i]+=Q(rng.randrange(1,10),rng.randrange(1,6))
            yy=serial(bigger,W)
            if yy[i]<y[i]:
                out.update({'failure':'own_monotonicity','iteration':it,'W':W,'c':c,'y':y,'bigger':bigger,'yy':yy,'owner':i});return out
    out['failure']=None;return out
if __name__=='__main__':
    out=run();s=json.dumps(out,default=str,indent=2);print(s)
    Path(__file__).with_suffix('.json').write_text(s+'\n')
