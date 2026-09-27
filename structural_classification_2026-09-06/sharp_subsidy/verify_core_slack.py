"""Independent exact checks of core-slack discovery certificates."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import json
from sector_min_core import core_rows
from tree_certificate import check_cover, require, market
from mixed_donor_template import construct


def dual_upper(d):
    m=d['m'];P=[tuple(e) for e in d['P']];U=d['U']
    edges,rows,_=core_rows(m,P);idx={e:k for k,e in enumerate(edges)}
    off=len(edges);stride=3*m+3
    res=[F(0)]*(off+len(U)*stride)
    z=list(map(F,d['dual_eq']))
    require(len(z)==1+len(U),'dual equality size')
    for j in range(m):
        for p in range(3):res[idx[p,j,j]]+=z[0]
    for k in range(len(U)):
        for v in range(3*m):res[off+k*stride+v]+=z[k+1]
    seen=set()
    for row,val in d['dual_ineq']:
        require(row not in seen and 0<=row<len(U)*len(rows),'dual row inventory')
        seen.add(row);val=F(val);require(val>=0,'dual sign')
        k,r=divmod(row,len(rows));es,coef=rows[r]
        for e in es:res[e]+=val
        for v,c in coef.items():res[off+k*stride+v]+=val*c
    for a,b,c in P:
        for e in ((0,a,b),(1,a,c),(2,b,c)):res[idx[e]]-=1
    for k,i in enumerate(U):res[off+k*stride+i]-=F(1,3)
    # Every normalized pair weight, payoff and sector minimum lies in [0,1].
    correction=sum(max(F(0),-v) for v in res)
    require(correction==F(d['box_correction']),'box correction mismatch')
    return sum(z)-1+correction


def check(d):
    m=d['m'];P=[tuple(e) for e in d['P']];U=d['U'];T=d['T']
    used={s*m+e[s] for e in P for s in range(3)}
    require(U==sorted(set(range(3*m))-used),'unmatched inventory')
    edges=[tuple(e) for e in d['edges']];weights=dict(zip(edges,d['weights']))
    require(len(weights)==len(edges) and min(weights.values())>=0,'weights')
    mats=[[[0]*m for _ in range(m)] for _ in range(3)]
    for (p,a,b),v in weights.items():mats[p][a][b]=v
    diagonal=[sum(mats[p][j][j] for p in range(3)) for j in range(m)]
    require(sum(diagonal)==T,'original diagonal worth')
    xs=dict(zip(U,d['witnesses']));require(len(xs)==len(U),'core witnesses')
    for i in U:
        x=xs[i];require(sum(x)==T,'original core total');check_cover(x,mats,m)
        require(x[i]==diagonal[i%m],'original ideal attained at diagonal cap')
    W=sum(mats[0][a][b]+mats[1][a][c]+mats[2][b][c] for a,b,c in P)
    J=F(W)+sum(F(xs[i][i],3) for i in U)-T
    upper=dual_upper(d)
    require(upper==F(d['fixed_P_upper']),'upper record')
    require(J/T<=upper<F(1,3),'fixed-P bound')
    pack=construct(m,P);loads={i:[F(0)]*(3*m) for i in U}
    coverage=defaultdict(F);team_slack=F(0)
    for i,e,mass in pack['packings']:
        mass=F(mass);a,b,c=e
        ep=((0,a,b),(1,a,c),(2,b,c))
        for s,j in enumerate(e):loads[i][s*m+j]+=mass
        for edge in ep:coverage[edge]+=mass
        slack=sum(xs[i][s*m+j] for s,j in enumerate(e))-sum(weights.get(edge,0) for edge in ep)
        require(slack>=0,'coalition slack');team_slack+=mass*slack
    capacity=F(0);hub_capacity=F(0)
    degree=[sum(s*m+j in used for s in range(3)) for j in range(m)]
    for i in U:
        require(loads[i][i]==0,'excluded player')
        for v,load in enumerate(loads[i]):
            require(load<=1,'packing capacity')
            if v!=i:
                term=(1-load)*xs[i][v];capacity+=term
                if degree[v%m]==3:hub_capacity+=term
    target=defaultdict(F)
    for j in range(m):
        for p in range(3):target[p,j,j]+=F(len(U))-F(21,5)
    for a,b,c in P:
        for edge in ((0,a,b),(1,a,c),(2,b,c)):target[edge]+=3
    pair_slack=F(0)
    for edge,w in weights.items():
        excess=coverage[edge]-target[edge]
        require(excess>=0,'pair domination');pair_slack+=excess*w
    require(capacity+team_slack+pair_slack==3*(F(2,5)*T-J),'slack identity')
    hubs=[j for j in range(m) if degree[j]==3]
    require(set(degree)<={1,3},'balanced leaf/hub class')
    Dh=sum(diagonal[j] for j in hubs);Dl=T-Dh;h=m-len(P)
    y=[[sum(F(xs[i][v],h) for i in U if i//m==s) for v in range(3*m)] for s in range(3)]
    Q=sum(Dh-sum(y[s][s*m+j] for j in hubs) for s in range(3))
    B3=sum(min(diagonal[j] for j in e) for e in P if all(degree[j]==3 for j in e))
    require(Q>=0 and W<=Dl+B3+Q,'three-core compatibility')
    require(B3<=F(Dh,2),'weighted forest layer-cake bound')
    e=max(F(0),F(1,5)-F(2,h))
    require(hub_capacity==e*h/len(hubs)*Q,'hub leakage coefficient')
    return {'b':d['b'],'m':m,'lower':str(J/T),'upper':str(upper),
            'capacity_slack_over_T':str(capacity/T),'team_slack_over_T':str(team_slack/T),
            'pair_slack_over_T':str(pair_slack/T),'Q_over_T':str(Q/T)}


def all_hub_calibrations():
    count=0
    for q in (1,2,3):
        b,_,baseP=market(q)
        P=list(baseP);used={(s,e[s]) for e in P for s in range(3)};m=b
        for j in range(b):
            for s in range(3):
                if (s,j) in used:continue
                e=[None]*3;e[s]=j
                for t in range(3):
                    if t!=s:e[t]=m;m+=1
                P.append(tuple(e))
        mats=[[[int(a==c) for c in range(m)] for a in range(m)] for _ in range(3)]
        for a,c,d in P:mats[0][a][c]=1;mats[1][a][d]=1;mats[2][c][d]=1
        for s in range(3):
            x=[3*int(t==s) for t in range(3) for j in range(m)]
            check_cover(x,mats,m);count+=m**3
        # These three original core points have Q=0, and q all-hub teams.
        require(3*len(P)<=3*(m-b)+3*q,'all-hub compatibility branch')
        for d in ([1]*b,list(range(b)),[int(j==0) for j in range(b)]):
            B3=sum(min(d[j] for j in e) for e in baseP)
            require(2*B3<=sum(d),'weighted forest check')
    return count


def main():
    rows=json.loads(Path(__file__).with_name('CORE_SLACK_CERTIFICATES.json').read_text())
    require([d['b'] for d in rows]==[2,4,8,12],'case inventory')
    result=[check(d) for d in rows]
    hub_checks=all_hub_calibrations()
    bad=dict(rows[0],dual_ineq=[])
    try:dual_upper(bad)
    except ValueError:pass
    else:raise ValueError('empty dual accepted')
    print(json.dumps({'status':'PASS','cases':result,'full_team_checks':sum(len(d['U'])*d['m']**3 for d in rows),'all_hub_branch_team_checks':hub_checks,'negative_controls':1}))

if __name__=='__main__':main()
