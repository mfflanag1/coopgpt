"""Finite high-precision corroboration of the analytic owner-gap theorem."""
from decimal import Decimal, localcontext
from pathlib import Path
import hashlib,json,random

D=Decimal
TOL=D('1e-80')

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def primitive(a,b):
    T=min(sum(a),sum(b))
    if T==0:return [D(0)]*len(a),T,None
    short,long=(a,b) if sum(a)<=sum(b) else (b,a)
    caps=[min(x,T) for x in long]
    q=(1-sum(caps)/T).exp()/2
    return [(1-q)*x+q*y for x,y in zip(short,caps)],T,q

def run():
    rng=random.Random(2026101701);c=1/(2*D(1).exp());alpha=1-c
    counts={'profiles':0,'branch_owner_checks':0,'global_owner_checks':0,
            'support_checks':0,'sharp_family_checks':0}
    for n in (2,4,9):
      for m in (1,3,8):
       for trial in range(20):
        h=[[D(rng.randrange(9)) for _ in range(n)] for _ in range(m)]
        if sum(map(sum,h))==0:h[0][0]=D(1)
        norm=sum(map(sum,h));h=[[x/norm for x in row] for row in h]
        l=[[D(rng.randrange(13))/norm for _ in range(n)] for _ in range(m)]
        if trial%4==0:l[-1]=[D(0)]*n
        z=[D(0)]*n;M=D(0);qbmass=D(0);deficit=D(0)
        for hh,ll in zip(h,l):
            local,T,q=primitive(hh,ll)
            qb=max(c,q) if q is not None else D(0)
            for j in range(n):
                require(local[j]-alpha*hh[j]<=qb*T+sum(hh)-T+TOL,
                        'Branchwise own-role ceiling failed')
                counts['branch_owner_checks']+=1
            z=[x+y for x,y in zip(z,local)]
            M+=T;qbmass+=qb*T
            deficit+=(1+c)*T-sum(local)
        if M==0:continue
        Z=sum(z);require(abs(deficit-((1+c)*M-Z))<TOL,'Deficit identity')
        mean=qbmass/M
        require(M*(c+mean*(2*mean).ln())<=deficit+TOL,'Jensen inverse ceiling')
        lo,hi=c,D(1)/2
        for _ in range(350):
            mid=(lo+hi)/2
            if c+mid*(2*mid).ln()<max(D(0),deficit/M):lo=mid
            else:hi=mid
        Q=hi
        hardware=[sum(row[j] for row in h) for j in range(n)]
        p=[D(rng.randrange(9))/4 for _ in range(n)]
        for j in range(n):
            require(z[j]-alpha*hardware[j]<=1-M+M*Q+TOL,'Global own-role ceiling')
            g=min(p[j]+z[j],D(1))-hardware[j]
            if g>0:
                require(z[j]+alpha*g<=1+alpha-M+M*Q+TOL,'Positive-gap ceiling')
                for t in ((c+D(1)/2)/2,D(1)/2):
                    s=1+(2*t).ln()
                    bound=1+alpha-M+(deficit+M*(t-c))/s
                    require(z[j]+alpha*g<=bound+TOL,'Explicit tangent ceiling')
                    counts['support_checks']+=1
            counts['global_owner_checks']+=1
        counts['profiles']+=1
    for k in (1,3,10):
      for q in (c,D(1)/4,D(2)/5,D(1)/2):
        rho=1-(2*q).ln();T=D(1)/k
        z=[D(0)]*(k+2)
        for j in range(k):
            h=[D(0)]*(k+2);l=h[:]
            h[j]=T;l[k]=T;l[k+1]=(rho-1)*T
            zz,_,_=primitive(h,l)
            z=[x+y for x,y in zip(z,zz)]
        require(abs(z[k]-q)<TOL,'Sharp family distinguished account')
        require(abs((1+c)-sum(z)-(c+q*(2*q).ln()))<TOL,'Sharp family deficit')
        require(abs(z[k]+alpha-(alpha+q))<TOL,'Sharp gap equality')
        counts['sharp_family_checks']+=1
    source=Path(__file__).with_name('SHARP_DEFICIT_OWNER_GAP_CEILING.txt')
    return {'status':'PASS','arithmetic':'110-digit Decimal finite corroboration; the analytic proof supplies the universal claim',
            **counts,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}

if __name__=='__main__':
    with localcontext() as ctx:
        ctx.prec=110
        print(json.dumps(run(),indent=2,sort_keys=True))
