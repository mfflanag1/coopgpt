"""Standalone Fraction verification of synthesis outputs; no solver dependency."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json,sys

def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def check(r):
    require(r['status'] in ('sat','candidate'),'No candidate witness')
    k=4;m=r['m'];n=k*m;target=r['target']
    E=list(map(tuple,r['edges']));A=[[[F(v)for v in row]for row in B]for B in r['matrices']]
    require(set(E)=={(0,1),(1,2),(2,3),(0,3)} and len(E)==len(A)==4,'Not C4')
    require(all(len(B)==m and all(len(row)==m and min(row)>=0 and max(row)<=r.get('matrix_bound',20) for row in B)for B in A),'Matrix shape or range')
    if r.get('integer_pair_values',False):require(all(v.denominator==1 for B in A for row in B for v in row),'Noninteger pair value')
    T=F(r['T']);tau=F(r.get('floor','1'));x=list(map(F,r['x']));y=list(map(F,r['y']));teams=list(product(range(m),repeat=k))
    w=lambda t:sum(B[t[a]][t[b]]for (a,b),B in zip(E,A))
    require(sum(w((i,)*k)for i in range(m))==T>0,'Integral diagonal matching worth')
    for p in (x,y):
        require(len(p)==n and sum(p)==T and min(p)>=0,'Cover totals')
        for t in teams:require(sum(p[v*m+t[v]]for v in range(k))>=w(t),'Uncovered team')
    require(min(x)==x[target]==tau>0,'Floor normalization')
    load=[F(0)]*n;objective=F(0)
    for row in r['dual']:
        t=tuple(row['team']);weight=F(row['weight']);require(t in teams and weight>0,'Invalid dual')
        require(sum(x[v*m+t[v]]for v in range(k))==w(t),'Complementarity fails')
        for v in range(k):load[v*m+t[v]]+=weight
        objective+=weight*w(t)
    d=[1-v for v in load];require(min(d)>=0 and d[target]>0,'Target deficit')
    require(all(di==0 or xi==tau for di,xi in zip(d,x)),'Unpinned deficit coordinate')
    require(T-objective==tau*sum(d)>0,'First-floor dual identity')
    require(y[target]>r['threshold']*tau,'Target ideal lower bound')
    exact=False
    if 'ideal_dual' in r:
        dual=r['ideal_dual'];mu=F(dual['mu']);coeff=[mu]*n;upper=mu*T
        for row in dual['teams']:
            t=tuple(row['team']);weight=F(row['weight']);require(t in teams and weight>=0,'Invalid ideal dual')
            upper-=weight*w(t)
            for v in range(k):coeff[v*m+t[v]]-=weight
        require(all(c>=int(i==target)for i,c in enumerate(coeff)),'Ideal dual coefficient')
        require(upper==y[target],'Ideal dual objective');exact=True
    return {'status':'PASS','players':n,'covers':2*len(teams),'floor':str(tau),'ideal_lower_bound':str(y[target]),'ideal_proved_exact':exact,'ratio_upper_bound':str(tau/y[target]),'dual_terms':len(r['dual']),'target_deficit':str(d[target]),'scope':'Target pinned on entire first optimal face; optional ideal dual proves exact ideal; no all-size claim.'}
if __name__=='__main__':
    p=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent/'C4_INTEGER_CERTIFICATE.json'
    print(json.dumps(check(json.loads(p.read_text()))))
