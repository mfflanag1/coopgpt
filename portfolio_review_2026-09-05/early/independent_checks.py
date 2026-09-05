"""Fresh full-core checks; no imports from the CoopGPT project."""
from fractions import Fraction as F
from pathlib import Path
import json
import z3

def require(ok, msg):
    if not ok:
        raise RuntimeError(msg)

def members(s,n): return [i for i in range(n) if s>>i&1]
def total(x,s): return sum((x[i] for i in members(s,len(x))),F())
def envelope(rows):
    n=len(rows[0]); rows=[list(map(F,r)) for r in rows]
    require(len({sum(r) for r in rows})==1,'different generator totals')
    return [min(total(r,s) for r in rows) for s in range(1<<n)]
def rat(q): return z3.RealVal(str(q))
def val(q):
    return F(q.as_long()) if z3.is_int_value(q) else F(q.numerator_as_long(),q.denominator_as_long())

def lex(v,normalize=False):
    n=(len(v)-1).bit_length(); x=z3.Reals(' '.join('x'+str(i) for i in range(n)))
    floors=[v[1<<i] if normalize else F() for i in range(n)]
    base=[sum(x)==rat(v[-1])]+[sum(x[i] for i in members(s,n))>=rat(v[s]) for s in range(1,len(v)-1)]
    fixed={}; stages=[]
    while len(fixed)<n:
        free=[i for i in range(n) if i not in fixed]
        op=z3.Optimize(); op.add(base); t=z3.Real('t')
        for i in free: op.add(x[i]-rat(floors[i])>=t)
        h=op.maximize(t); require(op.check()==z3.sat,'lex stage not sat')
        level=val(h.value()); atlevel=[x[i]>=rat(level+floors[i]) for i in free]
        pinned=[]
        for i in free:
            oo=z3.Optimize(); oo.add(base+atlevel); hh=oo.maximize(x[i])
            require(oo.check()==z3.sat,'pin stage not sat')
            if val(hh.value())==level+floors[i]: pinned.append(i)
        require(bool(pinned),'no pin')
        for i in pinned:
            fixed[i]=level+floors[i]; base.append(x[i]==rat(fixed[i]))
        stages.append({'level':str(level),'players':[i+1 for i in pinned]})
    return [fixed[i] for i in range(n)], stages

def pes(v):
    n=(len(v)-1).bit_length(); fixed={}; trace=[]
    for _ in range(n+1):
        chi={}; maxima=[None]*n
        for s in range(1,len(v)):
            ids=members(s,n); free=[i for i in ids if i not in fixed]
            rate=(v[s]-sum((fixed[i] for i in ids if i in fixed),F()))/len(free) if free else None
            chi[s]={i:fixed[i] if i in fixed else rate for i in ids}
            for i in ids:
                q=chi[s][i]
                if maxima[i] is None or q>maxima[i]: maxima[i]=q
        adm=[s for s,c in chi.items() if sum(c.values(),F())==v[s] and all(q==maxima[i] for i,q in c.items())]
        new={i:maxima[i] for s in adm for i in members(s,n) if i not in fixed}
        trace.append({'admissible':adm,'new':{str(i+1):str(q) for i,q in new.items()}})
        fixed.update(new)
        if len(fixed)==n: return [fixed[i] for i in range(n)],trace
        require(bool(new),'PES stalled')
    raise RuntimeError('PES rounds exhausted')

def sd_levels(v,x):
    n=len(x);done={}; coal=list(range(1,len(v)-1))
    while len(done)<len(coal):
        candidates={}
        for s in coal:
            if s in done: continue
            ids=members(s,n); covered={i:min(done[t] for t in done if t&s==t and t>>i&1) for i in ids if any(t&s==t and t>>i&1 for t in done)}
            residual=total(x,s)-v[s]-sum(covered.values(),F())
            candidates[s]=residual/(len(ids)-len(covered)) if len(covered)<len(ids) else residual+max(covered.values())
        low=min(candidates.values())
        done.update({s:q for s,q in candidates.items() if q==low})
    for q in sorted(set(done.values())):
        ss=[s for s in coal if done[s]<=q]
        weights=[z3.Real('w'+str(j)) for j in range(len(ss))]
        so=z3.Solver();so.add([w>0 for w in weights])
        for i in range(n): so.add(sum(weights[j] for j,s in enumerate(ss) if s>>i&1)==1)
        require(so.check()==z3.sat,'SD level not strictly balanced')
    return {str(s):str(q) for s,q in done.items()}

def check_exact(v):
    n=(len(v)-1).bit_length(); x=z3.Reals(' '.join('a'+str(i) for i in range(n)))
    cons=[sum(x)==rat(v[-1])]+[sum(x[i] for i in members(s,n))>=rat(v[s]) for s in range(1,len(v)-1)]
    for s in range(1,len(v)-1):
        so=z3.Solver();so.add(cons+[sum(x[i] for i in members(s,n))==rat(v[s])])
        require(so.check()==z3.sat,'coalition not exact '+str(s))

out={}
def checklex(name,v,expected,normalize=False):
    x,stages=lex(v,normalize)
    require(x==list(map(F,expected)),name+' wrong selector '+str(x))
    out[name]={'payoff':list(map(str,x)),'stages':stages}

# Exact independently recomputed procedural claims, including all chambers.
U=[0,1,0,1,2,0]; V=[1,0,1,0,0,2]
for t in map(F,['0','1/3','2/3','4/5','1','2','10']):
    rows=[[F(r[i])+ (t if i in [0,4] else 0) for i in range(6)] for r in [U,V]]
    x,trace=pes(envelope(rows))
    if t<=F(2,3): expected=[F(1,2)+F(3,4)*t,F(1,2)+t/4,F(1,2)+3*t/4,F(1,2)+t/4,1+t/2,1+t/2]
    elif t<=1: expected=[3*t/2,1-t/2,1,1-t/2,1+t/2,1+t/2]
    else: expected=[t+F(1,2),F(1,2),1,F(1,2),t+F(1,2),F(3,2)]
    require(x==expected,'paper2 ray '+str(t))
    out['paper2_ray_'+str(t)]={'claims':list(map(str,x)),'excess':str(sum(x)-sum(rows[0])),'trace':trace}

# Paper3 endpoint and continuous proper-bump path, with entire core selectors.
A=[2,0,12,6,0]; B=[0,0,0,0,20]; P=[0,2,10,4,4]
v=envelope([A,B,P]); w=envelope([A,B]); S=1+4+8+16
require([s for s in range(len(v)) if v[s]!=w[s]]==[S],'not a single bump')
for tau in map(F,['18','19','39/2','20']):
    vt=v[:];vt[S]=tau
    expected=[1,1,F(13,2),5,F(13,2)] if tau<=19 else [tau-18,20-tau,16-tau/2,tau-14,16-tau/2]
    checklex('paper3_proper_'+str(tau),vt,expected)

vg=envelope([[0,0,7,0,7],[2,10,0,2,0]])
for eps in [F(),F(1,8),F(3,2)]:
    vv=vg[:];vv[-1]=16+eps;s=3+eps/3
    checklex('paper3_grand_'+str(eps),vv,[s,7-s,s,s,s])

av=[-3,1,3,-1,2,-1,-1];bv=[3,-2,0,-1,-1,-1,2]
checklex('paper3_n7',envelope([[0]*7,av,bv]),[F(a,4) for a in av],True)

# The concrete normalization scope error.
two=[F(0),F(10),F(0),F(12)]
checklex('ordinary_Lmin_convex_control',two,[10,2])
checklex('normalized_Lmin_convex_control',two,[11,1],True)
claims,_=pes(two);require(claims==[10,2],'convex PES control')
out['convex_PES_control']=list(map(str,claims))

# Paper1: exactness and full satisfaction-level balancedness, from raw values.
sdv=[F() for _ in range(16)]
for s,q in {6:1,7:1,10:13,11:15,13:14,14:13,15:30}.items():sdv[s]=F(q)
for delta,payoff in [(0,['53/12','19/4','15/4','205/12']),(1,['35/8','33/8','33/8','139/8'])]:
    vv=sdv[:];vv[13]+=delta;xx=list(map(F,payoff));check_exact(vv)
    require(sum(xx)==vv[-1] and all(total(xx,s)>=vv[s] for s in range(16)),'SD core check')
    out['paper1_SD_'+str(delta)]={'payoff':payoff,'satisfaction':sd_levels(vv,xx),'every_coalition_exact':True}

# Paper4: representatives of all three all-parameter realizing families.
for m in [4,5,6,7]:
    n=m+1;r=m;rows=[]
    a=[0]*n;a[3]=a[r]=m-1;rows.append(a)
    a=[0]*n;a[2]=a[3]=m-1;rows.append(a)
    a=[0]*n;a[0]=a[1]=a[2]=1;a[r]=m-1
    if m>=5:a[4]=m-4
    rows.append(a);phi=[1]*m+[m-2];rows.append(phi)
    checklex('paper4_unique_rich_'+str(m),envelope(rows),phi)
for m,h in [(2,4),(3,4),(2,5)]:
    n=m+h;D=(h-2)*(h-3);r=h-2;Q=list(range(2,m));a=m;b=m+1;K=list(range(m+2,n))
    phi=[D]*m+[2*D]*h;rows=[]
    u=[0]*n;u[1]=D;u[a]=u[b]=3*D
    for j in Q:u[j]=D
    for k in K:u[k]=(2*r-1)*(r-1)
    rows.append(u)
    z=[0]*n;z[0]=4*D
    for j in Q:z[j]=D
    for k in K:z[k]=2*(r*r-1)
    rows.append(z)
    for k in K:
        w=[0]*n;w[0]=D;w[a]=w[b]=3*D
        for j in Q:w[j]=D
        for kk in K:
            if kk!=k:w[kk]=r*(2*r-1)
        rows.append(w)
    rows.append(phi)
    for j in Q:
        w=phi[:];w[0]+=D;w[j]-=D;rows.append(w)
    vv=envelope(rows);checklex('paper4_two_poor_'+str((m,h)),vv,phi)
    require(vv[sum(1<<i for i in range(m,n))]==2*D*(h-1),'two-poor slack')
for m,h in [(3,2),(4,2),(3,3)]:
    n=m+h;Q=list(range(3,m));H=list(range(m,n));phi=[1,1,2]+[1]*(m-3)+[3]*h
    a=[0]*n;a[0]=2;a[2]=3;a[H[0]]=5
    for j in Q:a[j]=1
    for j in H[1:-1]:a[j]=3
    b=[0]*n;b[1]=2;b[2]=1;b[H[0]]=4
    for j in Q:b[j]=1
    for j in H[1:]:b[j]=3
    c=[0]*n;c[H[-1]]=3*h+4
    for j in Q:c[j]=1
    rows=[a,b,c,phi]
    for j in Q:
        w=phi[:];w[0]+=1;w[j]-=1;rows.append(w)
    vv=envelope(rows);checklex('paper4_three_poor_'+str((m,h)),vv,phi)
    require(vv[sum(1<<i for i in H)]==3*h-1,'three-poor slack')

# Paper6 two families: full core is generated from all coalition minima.
for p,q in [(2,2),(2,3),(3,2),(3,3)]:
    pi=[2,2]+[1]*(p-2); sa=[0,2]+[1]*(q-2); sb=[0,4]+[1]*(q-2)
    phi=[1]*(p+q)+[2,2]
    rows=[phi,pi+sa+[0,2],pi+sb+[0,0]]
    for i in range(p):
        rr=[1]*p;rr[i]=0;rr[(i+1)%p]=2;rows.append(rr+sa+[2,2])
    for j in range(1,q):
        qq=[1]*q;qq[0]=qq[j]=0;rows.append(pi+qq+[0,4])
    vv=envelope(rows);checklex('paper6_A_'+str((p,q)),vv,phi)
    require(vv[(1<<(p+q))+(1<<(p+q+1))]==0,'family A H slack')
for q in [3,4,5]:
    c=q-1;phi=[1]*(q+1)+[c,c]
    rows=[phi,[0,q,q-1]+[0]*(q-2)+[q,0],[q,0,q-1]+[0]*(q-2)+[0,q],[1,1,0]+[1]*(q-2)+[c,q]]
    vv=envelope(rows);checklex('paper6_B_'+str(q),vv,phi)
    require(vv[(1<<(q+1))+(1<<(q+2))]==q,'family B H slack')

Path(__file__).with_name('independent_results.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS:',len(out),'independent exact checks; fresh Z3 full-core staged LP and Fraction PES.')
