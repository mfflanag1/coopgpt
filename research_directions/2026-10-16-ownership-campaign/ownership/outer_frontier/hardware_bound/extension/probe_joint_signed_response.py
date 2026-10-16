import math,random,json
rng=random.Random(81751)
LAM=1.194793583015429

def rule(h,l):
    H=sum(h);L=sum(l);T=min(H,L)
    if T==0:return [0.]*len(h)
    s,ll=(h,l) if H<=L else(l,h);ds=[min(x,T) for x in ll]
    q=.5*math.exp(1-sum(ds)/T)
    return [(1-q)*x+q*y for x,y in zip(s,ds)]

best=None
for k in range(80000):
    n=rng.randrange(3,7)
    if k%3==0:h=[0.,0.]+[rng.random() for _ in range(n-2)]
    else:h=[rng.random() if rng.random()<.6 else 0. for _ in range(n)]
    if sum(h)==0:continue
    h=[x/sum(h) for x in h]
    l=[rng.choice([0.,.1,.2,.35,.5,1.,2.]) if k%4==0 else rng.random()*2 for _ in range(n)]
    z=rule(h,l);den=z[0]+z[1]
    if den<1e-12:continue
    results=[]
    for i in(1,0):
        vals=[l[i]*j/16 for j in range(17)]+[0.,l[i],max(0.,1-sum(l[j] for j in range(n) if j!=i))]
        vals=[v for v in vals if 0<=v<=l[i]]
        mx=0.;at=l[i]
        for val in vals:
            ll=l[:];ll[i]=val;zz=rule(h,ll)
            loss=sum(z[j]-zz[j] for j in range(n) if j!=i and not(i==0 and j==1))
            if loss>mx:mx=loss;at=val
        results.append((mx,at))
    ratio=sum(x[0] for x in results)/den
    if best is None or ratio>best['ratio']:
        best={'ratio':ratio,'h':h,'l':l,'z':z,'reports_G_then_A':results,'k':k}
        if ratio>LAM+1e-7:break
print(json.dumps(best,indent=2))
