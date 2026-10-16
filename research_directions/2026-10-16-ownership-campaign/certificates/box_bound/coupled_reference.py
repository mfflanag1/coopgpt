#!/usr/bin/env python3
"""Independent floating evaluator for the coupled-domain theorem.
Finite scalar root searches and long-pool vertex enumeration; no generic solver.
"""
import math,itertools,sys
sys.path.insert(0,'/private/tmp/coopgpt-ownership-20261016/mixed')
from owner_box_reference import counterfactual_ranges
from verify_envelope_bounds import evaluate
from verify_local_total_envelope import local_ceiling
from check_cyclic_obstruction import primitive

def eta(k):
    if k==0:return 1.
    target=.5*math.exp(1-k);l=0.;u=1.
    for _ in range(70):
        m=(l+u)/2
        if m*math.exp(m)<target:l=m
        else:u=m
    t=(l+u)/2
    return k*t/(1-t)**2

def kappa(k):return 1. if k==0 else k/(2*math.exp(k-1)-1)

def interval_ge(bounds,A,B):
    """Intersect bounds with A*x+B>=0 (floating discovery/check evaluator)."""
    l,u=bounds
    if abs(A)<1e-14:return (l,u) if B>=-1e-12 else None
    cut=-B/A
    if A>0:l=max(l,cut)
    else:u=min(u,cut)
    return (l,u) if l<=u+1e-12 else None

def optimize_coupled(a,lo,up,beta,K,p,i,gamma):
    n=len(a);H=sum(a);own=a[i];others=[t for t in range(n) if t!=i]
    if H<=0:return 0.,lo.copy(),'zero'
    if n==1:return min(H,beta),[beta],'single'
    pi=p[i];Pm=sum(p[t] for t in others);L=sum(lo[t] for t in others);U=sum(up[t] for t in others)
    candidates=[];tol=1e-8*max(1,H,K)
    def put(w,mode):
        if any(w[t]<lo[t]-tol or w[t]>up[t]+tol for t in range(n)) or sum(w)>K+tol:
            raise ArithmeticError(('infeasible endpoint',mode,w,lo,up,K))
        if sum(w[t]-p[t] for t in others)<gamma*(w[i]-pi-own)-tol:
            raise ArithmeticError(('coupling failure',mode,w,gamma))
        candidates.append((primitive(a,w)[i],w,mode))
    # Short pool: split all affine/cap boundaries and at the sole f'' root.
    tl=pi+L;tu=min(H,K,beta+U)
    if tl<=tu+1e-12:
        lines=[(0.,beta),(1.,-L),(1/(1+gamma),(gamma*(pi+own)-Pm)/(1+gamma))]
        cuts=[tl,tu]+[v for v in a if tl<v<tu]
        for (v,w),(vv,ww) in itertools.combinations(lines,2):
            if abs(v-vv)>1e-14:
                t=(ww-w)/(v-vv)
                if tl<t<tu:cuts.append(t)
        cuts=sorted(set(cuts))
        tcandidates=list(cuts)
        for left,right in zip(cuts,cuts[1:]):
            if right-left<1e-14:continue
            mid=(left+right)/2
            v,w=min(lines,key=lambda z:z[0]*mid+z[1])
            tau=1. if mid<own else 0.;offset=0. if mid<own else own
            d=tau-v;e=offset-w
            capcount=sum(t>=mid for t in a);C=sum(t for t in a if t<mid)
            if C<=0:continue
            def deriv(t):
                q=.5*math.exp(1-capcount-C/t)
                return v+q*(d+d*C/t+e*C/t**2)
            parts=[left,right]
            den=2*e-d*C
            if abs(den)>1e-14:
                turn=e*C/den
                if left<turn<right:parts.append(turn);tcandidates.append(turn)
            parts.sort()
            for l,u in zip(parts,parts[1:]):
                if l<=0:continue
                dl,du=deriv(l),deriv(u)
                if dl*du<0:
                    ll,uu=l,u
                    for _ in range(65):
                        mm=(ll+uu)/2;dm=deriv(mm)
                        if dl*dm<=0:uu=mm
                        else:ll=mm;dl=dm
                    tcandidates.append((ll+uu)/2)
        for T in tcandidates:
            x=min(v*T+w for v,w in lines);x=max(pi,min(beta,x))
            witness=lo.copy();witness[i]=x;remain=max(0.,T-sum(witness))
            for t in others:
                step=min(remain,max(0.,up[t]-witness[t]));witness[t]+=step;remain-=step
            put(witness,'short')
    # Long pool.
    if K>=H-1e-12 and beta+U>=H-1e-12:
        xl=max(pi,H-U);xu=beta
        x=min(own,xu)
        if xl<=x+1e-12:
            witness=lo.copy();witness[i]=x;remain=max(0.,K-sum(witness))
            for t in others:
                step=min(remain,max(0.,min(up[t],H)-witness[t]));witness[t]+=step;remain-=step
            needed=max(L,H-x,Pm+gamma*(x-pi-own))
            deficit=max(0.,needed-sum(witness[t] for t in others))
            for t in others:
                step=min(deficit,max(0.,up[t]-witness[t]));witness[t]+=step;deficit-=step
            put(witness,'long-negative')
        base=(max(xl,own),xu)
        s_lines=[(0.,L),(-1.,H),(gamma,Pm-gamma*(pi+own))]
        if base[0]<=base[1]+1e-12:
            for pivot in others:
                fixed=[t for t in others if t!=pivot]
                for bits in itertools.product([0,1],repeat=len(fixed)):
                    fv={t:(up[t] if bit else lo[t]) for t,bit in zip(fixed,bits)}
                    D=sum(fv.values());E=sum(min(v,H) for v in fv.values())
                    for r,t0 in s_lines:
                        common=base
                        for rr,tt in s_lines:
                            if common is None:break
                            common=interval_ge(common,r-rr,t0-tt)
                        if common is None:continue
                        common=interval_ge(common,r,t0-D-lo[pivot])
                        if common is None:continue
                        common=interval_ge(common,-r,up[pivot]-t0+D)
                        if common is None:continue
                        for ocap in [False,True]:
                            ownpart=interval_ge(common,1.,-H) if ocap else interval_ge(common,-1.,H)
                            if ownpart is None:continue
                            nu,xi=(0.,H) if ocap else (1.,0.)
                            for pcap in [False,True]:
                                part=interval_ge(ownpart,r,t0-D-H) if pcap else interval_ge(ownpart,-r,H-t0+D)
                                if part is None:continue
                                sigma,zeta=(0.,H) if pcap else (r,t0-D)
                                lam=nu+sigma
                                l,u=part
                                vals=[l,u]
                                if nu==1 and lam>1e-14:
                                    critical=own+H/lam
                                    if l<=critical<=u:vals.append(critical)
                                for xx in vals:
                                    witness=lo.copy();witness[i]=xx
                                    for owner,value in fv.items():witness[owner]=value
                                    witness[pivot]=r*xx+t0-D
                                    put(witness,'long-positive')
    if not candidates:raise ArithmeticError('no coupled candidate')
    return max(candidates,key=lambda c:c[0])

def coupled_rule(rows,boundary=True):
    v=evaluate(rows);n=v['n'];m=v['d'];K=v['P']+local_ceiling(rows)
    mins,maxs=counterfactual_ranges(rows);answers=[];witnesses=[];gammas=[]
    for i in range(n):
        k=max((sum(rows[t][1+j]>0 for t in range(n) if t!=i) for j in range(m)),default=0)
        gamma=kappa(k) if boundary and v['a'][i]==0 else eta(k)
        lo=[v['p'][t]+mins[i][t] for t in range(n)]
        up=[v['p'][t]+maxs[i][t] for t in range(n)];up[i]=v['B'][i]
        val,w,_=optimize_coupled(v['a'],lo,up,v['B'][i],K,v['p'],i,gamma)
        answers.append(val);witnesses.append(w);gammas.append(gamma)
    return answers,witnesses,gammas,v
