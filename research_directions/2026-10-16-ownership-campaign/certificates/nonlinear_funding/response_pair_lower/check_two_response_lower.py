#!/usr/bin/env python3
"""Direct multiplicity-aware primitive replay; numerical corroboration only."""
from decimal import Decimal, localcontext, ROUND_CEILING, ROUND_FLOOR
from pathlib import Path
from fractions import Fraction
import hashlib
import json

BASE=Path(__file__).resolve().parent
D=Decimal
TOL=D('1e-80')


def require(ok,message):
    if not ok:
        raise RuntimeError(message)


def primitive(a,b,counts):
    sa=sum(x*m for x,m in zip(a,counts))
    sb=sum(x*m for x,m in zip(b,counts))
    if min(sa,sb)==0:
        return [D(0)]*len(a)
    short,long=(a,b) if sa<=sb else (b,a)
    t=min(sa,sb)
    caps=[min(x,t) for x in long]
    q=(1-sum(x*m for x,m in zip(caps,counts))/t).exp()/2
    return [(1-q)*x+q*y for x,y in zip(short,caps)]


def run():
    e=D(1).exp(); c=1/(2*e); C=1+c; K=e-1
    v=D(1)/5; q=(-v).exp()/2; qnew=(-D(4)).exp()/2
    B=(1-v)*((1-qnew)/q-1)
    require(Fraction(46,25)>Fraction(7,4), 'Exact coefficient comparison failed')
    coefficient=c*(2*B-2*e-K*D(2).ln())
    outputs=[]
    for lint in (8,12,20,40,80):
        L=D(lint); eps=(-L).exp(); T=1/L; t=eps/q
        rho=1+(T/(2*eps)).ln(); qc=eps/T; k=lint
        nf=int(rho.to_integral_value(rounding=ROUND_FLOOR))
        ds=[D(1)]*nf
        if rho!=nf:
            ds.append(rho-nf)
        m=max(2,int(((1-qc)*T/(k*eps)).to_integral_value(rounding=ROUND_CEILING)))
        names=[]; counts=[]
        def add(name,count=1):
            names.append(name); counts.append(count); return len(names)-1
        core=[add('B'+str(j)) for j in range(len(ds))]
        hardware=[add('core_h'+str(j),m) for j in range(k)]
        G=add('G'); A=add('A')
        tinyh=[add('tiny_h'+str(j),5) for j in range(2)]
        tinyl=[add('tiny_l'+str(j)) for j in range(2)]
        n=len(names); branches=k+3
        h=[[D(0)]*n for _ in range(branches)]
        l=[[D(0)]*n for _ in range(branches)]
        for j in range(k):
            h[j][hardware[j]]=T/(k*m)
            for owner,d in zip(core,ds):
                l[j][owner]=d*T/k
        for jj,owner in enumerate((G,A)):
            j=k+jj; h[j][tinyh[jj]]=t/5
            l[j][owner]=t; l[j][tinyl[jj]]=v*t
        h[-1][core[0]]=1-T-2*t
        require(h[-1][core[0]]>0,'Residual hardware nonpositive')
        p=[D(0)]*n
        Zcore=T+eps*(rho-1); Ztiny=t+v*eps
        p[G]=1; p[A]=1-Zcore-2*Ztiny+eps
        require(p[A]>0,'Near-cap grid negative')
        a=[sum(row[i] for row in h) for i in range(n)]
        require(abs(sum(x*m for x,m in zip(a,counts))-1)<TOL,'Hardware normalization')

        def evaluate(changed=None):
            z=[D(0)]*n
            for j in range(branches):
                ll=l[j][:]
                if changed is not None:
                    ll[changed]=D(0)
                local=primitive(h[j],ll,counts)
                z=[x+y for x,y in zip(z,local)]
            b=[x+y for x,y in zip(p,z)]
            raw=primitive(a,b,counts)
            s=sum(min(x,D(1))*m for x,m in zip(b,counts))
            return z,b,raw,s

        z,b,raw,s=evaluate()
        require(abs(s-2)<TOL,'Full capped sum not two')
        require(max(z)<=eps+TOL and abs(z[G]-eps)<TOL,'Full local diffuseness')
        require(sum(min(bi,D(1))!=bi for bi in b)==1 and b[G]>1,'Wrong full overflow')
        require(0<b[A]<1,'Near-cap account invalid')
        rawtotal=sum(x*m for x,m in zip(raw,counts))
        require(abs(rawtotal-C)<TOL,'Raw baseline not C')
        physical=sum(x*m for x,m in zip(p,counts))+T+2*t
        require(physical>1,'Physical hardware bottleneck missing')
        delta=eps*(K*rho-(2*e-1))
        expected=[c*((1-T-2*t)*(1-(-delta).exp())-eps),
                  c*((B*eps).exp()-1),
                  c*(((1+B)*eps).exp()*(b[A]-eps)-b[A])]
        sdeltas=[delta,-B*eps,-(1+B)*eps]
        actualgains=[]
        for owner,eg,sd in zip((core[0],G,A),expected,sdeltas):
            zz,bb,rr,ss=evaluate(owner)
            gain=rr[owner]-raw[owner]
            require(abs(gain-eg)<TOL,'Actual own gain formula failed: '+names[owner])
            require(abs(ss-(2+sd))<TOL,'Actual capped-total change failed')
            require(ss>1,'Outer side changed unexpectedly')
            require(bb[G]>=1 and bb[A]<1,'Designated cap status changed')
            require(all(bi<1 for j,bi in enumerate(bb) if j not in (G,A)),
                    'Undesignated account became capped')
            require(gain>0,'Exhibited report did not improve own payment')
            actualgains.append(gain)
        centered=(sum(actualgains)-c*K*eps*(L-L.ln()))/eps
        outputs.append({'L':lint,'productive_branches':k+2,
                        'actual_owners':sum(counts),'represented_types':n,
                        'centered_lower_coefficient':str(centered),
                        'distance_to_asymptotic_coefficient':str(centered-coefficient),
                        'response_gain_over_epsilon':[str(g/eps) for g in actualgains[1:]]})
    source=BASE/'TWO_RESPONSE_BRANCH_DIFFUSE_LOWER.txt'
    return {'status':'PASS','arithmetic':'110-digit Decimal direct actual-owner primitive replay with exact integer multiplicities; finite corroboration, not a proof',
            'multiplicity_semantics':'Caps are applied to each actual owner before multiplying by its count; only resource-identical hardware owners are compressed for evaluation',
            'B':str(B),'two_B_minus_K':str(2*B-K),
            'asymptotic_coefficient':str(coefficient),
            'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'profiles':outputs}


if __name__=='__main__':
    with localcontext() as ctx:
        ctx.prec=110
        print(json.dumps(run(),indent=2,sort_keys=True))
