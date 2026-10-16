#!/usr/bin/env python3
"""Actual primitive replay with integer multiplicities; finite Decimal corroboration."""
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
from pathlib import Path
import json,hashlib
D=Decimal

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def primitive(a,b,counts):
    sa=sum(v*n for v,n in zip(a,counts));sb=sum(v*n for v,n in zip(b,counts))
    if min(sa,sb)==0:return [D(0)]*len(a)
    s,l=(a,b) if sa<=sb else (b,a);T=min(sa,sb)
    cap=[min(v,T) for v in l];q=(1-sum(v*n for v,n in zip(cap,counts))/T).exp()/2
    return [(1-q)*x+q*y for x,y in zip(s,cap)]

def run():
    e=D(1).exp();c=1/(2*e);K=e-1;C=1+c;tol=D('1e-80')
    gam=D(1)/4;v=D(1)/5;qs=(-gam).exp()/2;qr=(-v).exp()/2
    B=(1-v)*(2*v.exp()-(1+v-1/v).exp()-1)
    J=2*gam.exp()-(1+gam-1/gam).exp()-1
    F=J+(1-gam)*B
    require(F>2*B,'Shared response did not improve independent lower')
    coefficient=c*(F-2*e-K*D(2).ln());records=[]
    for lint in (8,12,20,40,80):
        L=D(lint);eps=(-L).exp();T=1/L;rho=1+(T/(2*eps)).ln();qc=eps/T;k=lint
        ts=eps/qs;er=(1-gam)*eps;tr=er/qr
        nf=int(rho.to_integral_value(rounding=ROUND_FLOOR));shares=[D(1)]*nf
        if rho!=nf:shares.append(rho-nf)
        m=max(2,int(((1-qc)*T/(k*eps)).to_integral_value(rounding=ROUND_CEILING)))
        counts=[];names=[]
        def add(name,n=1):
            names.append(name);counts.append(n);return len(names)-1
        core=[add('B'+str(i)) for i in range(len(shares))]
        hw=[add('core_h'+str(j),m) for j in range(k)]
        G=add('G');A=add('A');hs=add('shared_h',4);hr=add('response_h',5);rD=add('response_D')
        n=len(names);h=[[D(0)]*n for _ in range(k+3)];l=[[D(0)]*n for _ in range(k+3)]
        for j in range(k):
            h[j][hw[j]]=T/(k*m)
            for i,d in zip(core,shares):l[j][i]=d*T/k
        h[k][hs]=ts/4;l[k][A]=ts;l[k][G]=gam*ts
        h[k+1][hr]=tr/5;l[k+1][G]=tr;l[k+1][rD]=v*tr
        a=1-T-ts-tr;h[k+2][core[0]]=a
        require(a>0,'negative remaining hardware')
        Zcore=T+eps*(rho-1);Zs=ts+gam*eps;Zr=tr+v*er;Z=Zcore+Zs+Zr
        p=[D(0)]*n;p[G]=1;p[A]=1-Z+eps
        hardware=[sum(row[i] for row in h) for i in range(n)]
        require(abs(sum(x*n for x,n in zip(hardware,counts))-1)<tol,'H not one')
        def evaluate(owner=None,branches=()):
            z=[D(0)]*n
            for j in range(k+3):
                ll=l[j][:]
                if owner is not None and j in branches:ll[owner]=D(0)
                row=primitive(h[j],ll,counts)
                z=[x+y for x,y in zip(z,row)]
            b=[x+y for x,y in zip(p,z)];raw=primitive(hardware,b,counts)
            S=sum(min(x,D(1))*n for x,n in zip(b,counts))
            return z,b,raw,S
        z,b,raw,S=evaluate()
        require(abs(S-2)<tol,'full S not two')
        require(max(z)<=eps+tol,'full local-payment budget exceeded')
        require(abs(z[G]-eps)<tol and abs(z[A]-eps)<tol,'shared actual-owner budget wrong')
        require(sum(int(x>=1)*n for x,n in zip(b,counts))==1 and b[G]>1,'wrong cap count')
        require(p[A]>0 and b[A]<1,'A grid invalid')
        require(sum(x*n for x,n in zip(p,counts))+T+ts+tr>1,'physical hardware bottleneck failed')
        require(abs(sum(x*n for x,n in zip(raw,counts))-C)<tol,'raw C failed')
        delta=eps*(K*rho-(2*e-1))
        expected=[c*(a*(1-(-delta).exp())-eps),c*((B*er).exp()-1),c*(((1+J)*eps).exp()*(b[A]-eps)-b[A])]
        targetS=[2+delta,2-B*er,2-(1+J)*eps];gains=[]
        for owner,changed,eg,ss in zip((core[0],G,A),(range(k),(k+1,),(k,)),expected,targetS):
            zz,bb,rr,s=evaluate(owner,changed)
            gain=rr[owner]-raw[owner]
            require(abs(gain-eg)<tol,'actual unilateral gain identity')
            require(abs(s-ss)<tol and s>1,'actual capped total identity')
            require(bb[G]>=1 and 0<bb[A]<1,'designated cap changed')
            require(all(x<1 for j,x in enumerate(bb) if j not in (G,A)),'another account capped')
            require(gain>0,'report not profitable')
            gains.append(gain)
        records.append({'L':lint,'actual_owners':sum(counts),'productive_branches':k+2,
           'response_gain_over_epsilon':[str(x/eps) for x in gains[1:]],
           'centered_lower':str((sum(gains)-c*K*eps*(L-L.ln()))/eps)})
    source=Path(__file__).with_name('SHARED_RESPONSE_BRANCH_DIFFUSE_LOWER.txt')
    return {'status':'PASS','arithmetic':'110-digit Decimal direct actual-owner primitive replay; finite corroboration',
       'multiplicity_semantics':'each actual hardware owner capped before integer multiplication',
       'B':str(B),'J':str(J),'F':str(F),'F_minus_two_B':str(F-2*B),
       'new_lower_residual':str(coefficient),'profiles':records,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
if __name__=='__main__':
    with localcontext() as ctx:
        ctx.prec=110
        print(json.dumps(run(),indent=2,sort_keys=True))
