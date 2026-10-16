"""Floating attempted falsification only. Analytic proofs and exact constants are separate."""
import math,itertools,random,json

def phi(a,b):
    A=sum(a); B=sum(b); T=min(A,B)
    if T<=0:return [0.0]*len(a)
    s,l=(a,b) if A<=B else (b,a)
    d=[min(x,T) for x in l]
    q=.5*math.exp(1-sum(d)/T)
    return [(1-q)*x+q*y for x,y in zip(s,d)]
def req(test,msg):
    if not test:raise RuntimeError(msg)
K=math.e-1
local_count=0; local_max=0.0

def local_check(a,b,i,aa,bb):
    global local_count,local_max
    z=phi(a,b); zz=phi(aa,bb); M=min(sum(a),sum(b))
    inc=sum(max(zz[k]-z[k],0) for k in range(len(a)) if k!=i)
    rhs=K*z[i]*(1+math.log(M/z[i])) if z[i]>0 else 0
    req(inc<=rhs+1e-10*max(1,M),'incoming entropy violation')
    if rhs>1e-12:local_max=max(local_max,inc/rhs)
    local_count+=1
for n in range(1,5):
    for r in itertools.product(tuple(itertools.product((0.,1.,2.),repeat=2)),repeat=n):
        a=[x[0] for x in r]; b=[x[1] for x in r]
        for i in range(n):
            for ai in range(int(a[i])+1):
                for bi in range(int(b[i])+1):
                    aa=a.copy();bb=b.copy();aa[i]=float(ai);bb[i]=float(bi)
                    local_check(a,b,i,aa,bb)
rng=random.Random(20261016)
for it in range(15000):
    n=2+it%16
    a=[0 if rng.random()<.3 else 10**rng.uniform(-5,5) for _ in range(n)]
    b=[0 if rng.random()<.3 else 10**rng.uniform(-5,5) for _ in range(n)]
    i=it%n;aa=a.copy();bb=b.copy()
    aa[i]*=rng.choice((0.,1.,rng.random()));bb[i]*=rng.choice((0.,1.,rng.random()))
    local_check(a,b,i,aa,bb)
# Exact-form asymptotic incoming example, evaluated numerically only.
ratios=[]
for n in [3,5,10,30,100]:
    ratios.append({'n':n,'ratio_to_sharp_entropy_bound':(n-1)/(n+math.log(2))})

outer_profiles=0; outer_transitions=0; diffuse_profiles=0; max_sample_total=0
for it in range(200):
    n=20+it%31; m=1+it%7
    hs=[[rng.random() if rng.random()>.15 else 0.0 for _ in range(n)] for _ in range(m)]
    ls=[[rng.random() if rng.random()>.15 else 0.0 for _ in range(n)] for _ in range(m)]
    H=sum(map(sum,hs));hs=[[v/H for v in row] for row in hs]
    # Include both original pool orientations with substantial branch imbalance.
    ls=[[v/H*rng.choice((.4,1.,2.5)) for v in row] for row in ls]
    M=sum(min(sum(a),sum(b)) for a,b in zip(hs,ls))
    p=[0.0]*n
    if it%3==0:p[it%n]=rng.uniform(1.0,5.0) # arbitrary single-owner overflow
    elif it%3==1:
        p=[rng.random() for _ in range(n)];scale=max(1-M,0)+rng.random()*1.2
        p=[v/sum(p)*scale for v in p]
    else:
        p=[rng.random() for _ in range(n)];scale=2+rng.random()*3
        p=[v/sum(p)*scale for v in p]
    req(sum(p)+M>=1-1e-12,'physical hardware bottleneck')
    a=[sum(row[i] for row in hs) for i in range(n)]
    local=[phi(x,y) for x,y in zip(hs,ls)]
    z=[sum(row[i] for row in local) for i in range(n)]
    d=[min(1,p[i]+z[i]) for i in range(n)];S=sum(d);q=.5*math.exp(1-S)
    eps=max(z);A=math.exp(K*eps);J=K*eps*(1+math.log(1/eps));B=math.exp(-J)
    bound=1+.5*A*math.exp(-B/A)
    samples=phi(a,[p[i]+z[i] for i in range(n)])
    if eps<=.1:diffuse_profiles+=1
    for i in range(n):
        for rep in range(5):
            hp=[row.copy() for row in hs];lp=[row.copy() for row in ls];pp=p.copy()
            for j in range(m):
                hp[j][i]*=rng.choice((0.,1.,rng.random()))
                lp[j][i]*=rng.choice((0.,1.,rng.random()))
            pp[i]*=rng.choice((0.,1.,rng.random()))
            ap=[sum(row[k] for row in hp) for k in range(n)]
            locp=[phi(x,y) for x,y in zip(hp,lp)]
            zp=[sum(row[k] for row in locp) for k in range(n)]
            val=phi(ap,[pp[k]+zp[k] for k in range(n)])[i]
            comparison=a[i]+q*(A if d[i]>a[i] else B)*(d[i]-a[i])
            req(val<=comparison+1e-10,'actual outer comparison violation')
            samples[i]=max(samples[i],val);outer_transitions+=1
    req(sum(samples)<=bound+1e-10,'sampled envelope sum exceeds diffuse bound')
    if eps<=.1:req(sum(samples)<=12461/9005+1e-10,'threshold failure')
    max_sample_total=max(max_sample_total,sum(samples));outer_profiles+=1
print(json.dumps({'status':'PASS','scope':'Floating finite falsification only, not a general proof or exact envelope computation.','local_actual_transitions':local_count,'largest_incoming_ratio_to_bound':local_max,'sharpness_family_ratios':ratios,'outer_profiles':outer_profiles,'outer_actual_transitions':outer_transitions,'profiles_with_epsilon_at_most_one_tenth':diffuse_profiles,'maximum_sampled_envelope_funding':max_sample_total},indent=2))
