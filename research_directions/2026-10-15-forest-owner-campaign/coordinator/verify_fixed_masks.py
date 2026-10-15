"""Exact independent checks for FIXED_MASK_THEOREM; standard library only."""
from fractions import Fraction as Q
from itertools import product
from math import comb
import json, random

def need(x,msg):
    if not x:raise RuntimeError(msg)

def value(forms,c):return min(sum(a*b for a,b in zip(w,c)) for w in forms)
def agg(b,mask):return tuple(sum(row[j] for i,row in enumerate(b) if mask>>i&1) for j in range(len(b[0])))
def law(n,m):
    h=sum((Q(1,s) for s in range(n-m+1,n+1)),Q(0))
    return {mask:Q(1,mask.bit_count())/h/comb(n,mask.bit_count()) for mask in range(1<<n) if mask.bit_count()>n-m}
def costs(n):
    h=Q(0);result=[]
    for m in range(1,n+1):
        h+=Q(1,n-m+1);result.append(n-Q(m-1)/h)
    return result

def pay(forms,b,nu):
    n=len(b);T=value(forms,agg(b,(1<<n)-1));ys=[Q(0)]*n
    for mask,prob in nu.items():
        x=agg(b,mask);v=value(forms,x)
        w=min(enumerate(forms),key=lambda z:(sum(a*b for a,b in zip(z[1],x)),z[0]))[1]
        for i,row in enumerate(b):
            if mask>>i&1:yi=v-value(forms,agg(b,mask^(1<<i)))
            else:yi=min(T,sum(a*b for a,b in zip(w,row)))
            ys[i]+=prob*yi
    return tuple(ys)

def main():
    counts=dict(profiles=0,coalitions=0,own_increases=0,budgets=0,mask_identities=0,lower_profile_averages=0)
    for forms in (((1,0),(0,1)),((2,0),(1,1),(0,3)),((1,1),),((0,0),(1,2))):
        n=3;cs=costs(n);m=min(range(1,n+1),key=lambda j:cs[j-1]);nu=law(n,m)
        need(sum(nu.values())==1,'probability normalization')
        for flat in product((Q(0),Q(1)),repeat=2*n):
            b=tuple(tuple(flat[2*i:2*i+2]) for i in range(n));ys=pay(forms,b,nu);T=value(forms,agg(b,7))
            need(all(v>=0 for v in ys),'nonnegative');need(sum(ys)<=cs[m-1]*T,'budget')
            counts['profiles']+=1;counts['budgets']+=1
            for mask in range(1<<n):
                need(sum(ys[i] for i in range(n) if mask>>i&1)>=value(forms,agg(b,mask)),'coalition')
                counts['coalitions']+=1
            for i in range(n):
                for j in range(2):
                    bb=[list(v) for v in b];bb[i][j]+=Q(1,2)
                    need(pay(forms,tuple(map(tuple,bb)),nu)[i]>=ys[i],'own increase')
                    counts['own_increases']+=1
    rng=random.Random(20261015)
    for n in range(1,8):
        forms=tuple(tuple(Q(rng.randrange(4)) for e in range(3)) for _ in range(5))
        b=tuple(tuple(Q(rng.randrange(7),3) for e in range(3)) for _ in range(n))
        gs=[sum((value(forms,agg(b,mask)) for mask in range(1<<n) if mask.bit_count()==s),Q(0))/comb(n,s) for s in range(n+1)]
        for s in range(1,n+1):
            direct=sum((sum(value(forms,agg(b,mask))-value(forms,agg(b,mask^(1<<i))) for i in range(n) if mask>>i&1) for mask in range(1<<n) if mask.bit_count()==s),Q(0))/comb(n,s)
            need(direct==s*(gs[s]-gs[s-1]),'endpoint identity');counts['mask_identities']+=1
        for m in range(1,n+1):
            nu=law(n,m);need(sum(nu.values())==1,'probability');ys=pay(forms,b,nu)
            need(sum(ys)<=costs(n)[m-1]*gs[n],'random budget');counts['budgets']+=1
    for n in range(3,101):
        m=1
        while m*(m-1)<2*n:m+=1
        need(m<=n,'fixed technology dimension');S=Q(m*(m+1),2);L=Q(2*n,m+1)
        for l in range(n+1):
            direct=sum((Q(k)/S*(l+(Q(n-l,k) if l<k else Q(0))) for k in range(1,m+1)),Q(0))
            need(direct==l+Q(n-l)/S*max(m-l,0),'profile average formula')
            need(direct>=L,'fixedmask lower');counts['lower_profile_averages']+=1
    examples=[]
    for n in (1,2,3,4,5,10,20,50,100,1000):
        cs=costs(n);m=min(range(1,n+1),key=lambda j:cs[j-1])
        examples.append(dict(n=n,m=m,factor=str(cs[m-1]),decimal=float(cs[m-1])))
    print(json.dumps(dict(status='PASS',arithmetic='exact fractions',counts=counts,examples=examples,limitation='Finite checks supplement analytic all-profile proofs; no historical novelty or unrestricted lower claimed.'),indent=2))
if __name__=='__main__':main()
