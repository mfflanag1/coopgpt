#!/usr/bin/env python3
"""Finite corroboration: actual-owner primitive, caps before multiplicities."""
from decimal import Decimal as D,localcontext,ROUND_FLOOR,ROUND_CEILING
from pathlib import Path
import json,hashlib

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def primitive(a,b,counts):
    sa=sum(x*n for x,n in zip(a,counts));sb=sum(x*n for x,n in zip(b,counts))
    if min(sa,sb)==0:return [D(0)]*len(a)
    s,l=(a,b) if sa<=sb else (b,a);T=min(sa,sb)
    caps=[min(x,T) for x in l];q=(1-sum(x*n for x,n in zip(caps,counts))/T).exp()/2
    return [(1-q)*x+q*y for x,y in zip(s,caps)]

def run():
    lo=D(1)/3;hi=D(2)/5
    for _ in range(400):
        mid=(lo+hi)/2
        if mid*mid.exp()<D(1)/2:lo=mid
        else:hi=mid
    v=(lo+hi)/2;q=(-v).exp()/2
    require(abs(q-v)<D('1e-100'),'root residual')
    e=D(1).exp();c=1/(2*e);K=e-1;C=1+c;Lam=(1-v)*(2*v.exp()-1);tol=D('1e-80')
    records=[]
    for lint in (8,12,20,40,80):
        L=D(lint);eps=(-L).exp();T=1/L;rho=1+(T/(2*eps)).ln();qc=eps/T;k=lint
        nf=int(rho.to_integral_value(rounding=ROUND_FLOOR));shares=[D(1)]*nf
        if rho!=nf:shares.append(rho-nf)
        m=max(2,int(((1-qc)*T/(k*eps)).to_integral_value(rounding=ROUND_CEILING)))
        names=[];counts=[]
        def add(name,count=1):names.append(name);counts.append(count);return len(names)-1
        core=[add('B'+str(j)) for j in range(len(shares))]
        hw=[add('hardware'+str(j),m) for j in range(k)]
        G=add('G');A=add('A');oppG=[add('DG'+str(j)) for j in range(3)];oppA=[add('DA'+str(j)) for j in range(3)]
        n=len(names);h=[[D(0)]*n for _ in range(k+7)];ell=[[D(0)]*n for _ in range(k+7)]
        for j in range(k):
            h[j][hw[j]]=T/(k*m)
            for i,d in zip(core,shares):ell[j][i]=d*T/k
        t=eps/(3*q);tau=3*t
        for j,other in enumerate(oppG):h[k+j][other]=t;ell[k+j][other]=v*t;ell[k+j][G]=t
        for j,other in enumerate(oppA):h[k+3+j][other]=t;ell[k+3+j][other]=v*t;ell[k+3+j][A]=t
        a=1-T-2*tau;h[k+6][core[0]]=a
        require(a>0,'negative stranded hardware')
        Z=T+eps*(rho-1)+2*(tau+v*eps)
        p=[D(0)]*n;p[G]=1;p[A]=1-Z+eps
        hardware=[sum(row[i] for row in h) for i in range(n)]
        require(abs(sum(x*n for x,n in zip(hardware,counts))-1)<tol,'H normalization')
        def evaluate(owner=None,branches=()):
            z=[D(0)]*n
            for j in range(k+7):
                l=ell[j][:]
                if owner is not None and j in branches:l[owner]=D(0)
                row=primitive(h[j],l,counts);z=[x+y for x,y in zip(z,row)]
            b=[x+y for x,y in zip(p,z)];raw=primitive(hardware,b,counts)
            S=sum(min(x,D(1))*n for x,n in zip(b,counts))
            return z,b,raw,S
        z,b,raw,S=evaluate()
        require(max(z)<=eps+tol,'actual local-payment diffuseness')
        require(abs(z[G]-eps)<tol and abs(z[A]-eps)<tol,'distinguished owner local mass')
        require(abs(S-2)<tol,'full capped total')
        require(sum(int(x>=1)*n for x,n in zip(b,counts))==1 and b[G]>1,'sole full cap')
        require(p[A]>0 and b[A]<1,'uncapped grid owner')
        require(sum(x*n for x,n in zip(p,counts))+T+2*tau>1,'hardware bottleneck')
        require(abs(sum(x*n for x,n in zip(raw,counts))-C)<tol,'full raw funding')
        delta=eps*(K*rho-(2*e-1))
        expect=[c*(a*(1-(-delta).exp())-eps),c*((Lam*eps).exp()-1),c*(((1+Lam)*eps).exp()*(b[A]-eps)-b[A])]
        targetS=[2+delta,2-Lam*eps,2-(1+Lam)*eps];gains=[]
        for owner,bs,eg,ss in zip((core[0],G,A),(range(k),range(k,k+3),range(k+3,k+6)),expect,targetS):
            zz,bb,rr,s=evaluate(owner,bs);gain=rr[owner]-raw[owner]
            require(abs(gain-eg)<tol,'unilateral gain exact identity')
            require(abs(s-ss)<tol and s>1,'changed capped-total exact identity')
            require(bb[G]>=1 and 0<bb[A]<1,'grid cap region')
            require(all(x<1 for i,x in enumerate(bb) if i not in(G,A)),'unexpected outer cap')
            require(gain>0,'exhibited report not beneficial')
            if owner in(G,A):
                loss=sum((x-y)*n for i,(x,y,n) in enumerate(zip(z,zz,counts)) if i!=owner)
                require(abs(loss-Lam*eps)<tol,'sharp signed OTHER identity')
            gains.append(gain)
        records.append({'L':lint,'actual_owners':sum(counts),'productive_branches':k+6,
            'centered_lower':str((sum(gains)-c*K*eps*(L-L.ln()))/eps),
            'response_gain_over_epsilon':[str(x/eps) for x in gains[1:]]})
    sources=['SHARP_SIGNED_OTHER_LOCAL_LOSS.txt','SHARP_SIGNED_RESPONSE_DIFFUSE_PAIR_LOWER.txt']
    return {'status':'PASS','arithmetic':'110-digit Decimal actual primitive replay; finite corroboration, not proof',
       'root':str(v),'Lambda':str(Lam),'two_Lambda':str(2*Lam),
       'lower_residual':str(c*(2*Lam-2*e-K*D(2).ln())),
       'profiles':records,'source_sha256':{s:hashlib.sha256(Path(__file__).with_name(s).read_bytes()).hexdigest() for s in sources}}
if __name__=='__main__':
    with localcontext() as ctx:
        ctx.prec=110
        print(json.dumps(run(),indent=2,sort_keys=True))
