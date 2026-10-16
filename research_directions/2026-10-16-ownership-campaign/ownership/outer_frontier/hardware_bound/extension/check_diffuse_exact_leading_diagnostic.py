"""Floating replay of one explicit owner profile, plus aggregate formula diagnostics.
Neither floating component replaces the analytic all-epsilon proof.
"""
import math,json

def phi(a,b):
    A=sum(a);B=sum(b);T=min(A,B)
    if T<=0:return [0.0]*len(a)
    s,l=(a,b) if A<=B else (b,a)
    d=[min(x,T) for x in l];q=.5*math.exp(1-sum(d)/T)
    return [(1-q)*x+q*y for x,y in zip(s,d)]
def ck(v,msg):
    if not v:raise RuntimeError(msg)
n=k=8;m=3000;T=1/8;N=k*m+n+2
h=[[0.0]*N for _ in range(k+1)];l=[[0.0]*N for _ in range(k+1)]
for j in range(k):
    for a in range(m):h[j][j*m+a]=T/(k*m)
    for b in range(n):l[j][k*m+b]=T/k
h[k][k*m]=1-T
q=.5*math.exp(1-n);eps=q*T;Z=T+eps*(n-1);P=2-Z
p=[0.0]*N;p[-1]=p[-2]=P/2
z=[0.0]*N
for a,b in zip(h,l):
    row=phi(a,b);z=[x+y for x,y in zip(z,row)]
a=[sum(hh[i] for hh in h) for i in range(N)]
b=[p[i]+z[i] for i in range(N)];raw=phi(a,b)
ck(abs(sum(a)-1)<1e-10,'hardware normalization')
ck(abs(sum(z)-Z)<1e-10,'local aggregate formula')
ck(max(z)<=eps+1e-12,'all owners diffuse')
ck(all(a[i]+p[i]+sum(ll[i] for ll in l)>0 for i in range(N)),'all actual owners active')
ck(max(b)<1 and abs(sum(b)-2)<1e-10,'full cap and opposing total')
i=k*m
for j in range(k):l[j][i]=0.0
zp=[0.0]*N
for aa,bb in zip(h,l):
    row=phi(aa,bb);zp=[x+y for x,y in zip(zp,row)]
bp=[p[j]+zp[j] for j in range(N)];rawp=phi(a,bp)
Delta=eps*((math.e-1)*n-(2*math.e-1));c=1/(2*math.e)
gain=c*((1-T)*(-math.expm1(-Delta))-eps)
ck(max(bp)<1 and abs(sum(bp)-(2+Delta))<1e-10,'changed cap and opposing total')
ck(abs((rawp[i]-raw[i])-gain)<1e-11,'actual raw-payment gain formula')
ck(gain>0,'actual feasible deviation profitable')
ck(abs(sum(raw)-(1+c))<1e-10,'full raw funding C')
seq=[]
for L in [20,50,100,200,500]:
    epsi=math.exp(-L);nn=math.floor(L-math.log(L));qn=.5*math.exp(1-nn);tt=epsi/qn
    delta=epsi*((math.e-1)*nn-(2*math.e-1))
    witness=c*((1-tt)*(-math.expm1(-delta))-epsi)
    seq.append({'L':L,'n':nn,'T':tt,'witness_premium_over_epsilon_log':witness/(epsi*L)})
print(json.dumps({'status':'PASS','scope':'Floating finite replay and aggregate diagnostics only; analytic proof is load-bearing.','explicit_actual_owner_count':N,'productive_branches':k,'full_raw_funding':sum(raw),'epsilon':eps,'one_actual_owner_gain':gain,'one_owner_envelope_excess_lower_bound':gain,'all_small_epsilon_integer_sequence':seq,'limiting_witness_coefficient':c*(math.e-1)},indent=2))
