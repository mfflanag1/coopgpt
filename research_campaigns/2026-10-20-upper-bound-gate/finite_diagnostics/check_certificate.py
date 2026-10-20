"""Standard-library exact replay of exported finite lower certificates.

Reconstructs every weighted contract row from its semantic tag; independently
checks all stored production primal/dual witnesses; never imports the probe.
"""
from collections import defaultdict
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json, sys


def check(path):
    data=json.loads(Path(path).read_text());case=data['case'];d=case['d'];A=case['A'];pi=list(map(Q,case['pi']))
    if len(case['pairs'])!=4 or any(len(set(p))!=2 for p in case['pairs']):raise ValueError('ownership')
    if any(sum(A[a][e]>0 for a in range(d))!=3 for e in range(len(pi))):raise ValueError('arity')
    profiles=[tuple(p) for p in data['profiles']]
    if profiles!=list(product(range(4),repeat=4)):raise ValueError('incomplete lattice')
    states=data['owner_states'];bits=list(product((0,1),repeat=2))
    for i in range(4):
        for k in range(4):
            expected=[0]*d
            for j,a in enumerate(case['pairs'][i]):expected[a]=bits[k][j]*case['caps'][i][j]
            if states[i][k]!=expected:raise ValueError('bad report state')
    values={};prices={}
    for oracle in data['oracles']:
        cap=tuple(oracle['cap']);x=list(map(Q,oracle['x']));p=list(map(Q,oracle['p']));v=Q(oracle['value'])
        if min(x)<0 or min(p)<0:raise ValueError('negative production witness')
        if any(sum(A[a][e]*x[e] for e in range(len(pi)))>cap[a] for a in range(d)):raise ValueError('primal capacity')
        if any(sum(A[a][e]*p[a] for a in range(d))<pi[e] for e in range(len(pi))):raise ValueError('dual feasibility')
        if sum(pi[e]*x[e] for e in range(len(pi)))!=v or sum(p[a]*cap[a] for a in range(d))!=v:raise ValueError('value gap')
        values[cap]=v;prices[cap]=p
    b=[[tuple(states[i][profile[i]]) for i in range(4)] for profile in profiles]
    def cap(k,C):return tuple(sum(b[k][i][a] for i in C) for a in range(d))
    K=1024
    if data['K']!=K:raise ValueError('variable layout')
    combo=defaultdict(Q);rhs=Q(0);counts=defaultdict(int)
    L=D=positive=negative=coverage_slack=Q(0)
    for item in data['certificate']:
        w=Q(item['weight']);tag=item['tag'];kind=tag[0];row=defaultdict(Q)
        if w<0:raise ValueError('negative multiplier')
        counts[kind]+=1
        if kind=='budget':
            k=tag[1];v=values[cap(k,range(4))]
            for i in range(4):row[4*k+i]=1
            row[K]=-v;rb=Q(0);D+=w*v
        elif kind=='cover':
            _,k,C=tag
            if not C or len(set(C))!=len(C) or any(i not in range(4) for i in C):raise ValueError('coverage coalition')
            for i in C:row[4*k+i]=-1
            rb=-values[cap(k,C)];L-=w*rb
            p=prices[cap(k,range(4))]
            coverage_slack+=w*(sum(p[a]*b[k][i][a] for i in C for a in range(d))+rb)
        elif kind=='out':
            _,lo,hi,C=tag
            if not 1<=len(C)<=2 or len(set(C))!=len(C):raise ValueError('protected coalition')
            if any(b[lo][i]!=b[hi][i] for i in range(4) if i not in C):raise ValueError('outsider changed')
            if any(b[hi][i][a]<b[lo][i][a] for i in C for a in range(d)):raise ValueError('illegal restoration')
            for i in C:row[4*lo+i]+=1;row[4*hi+i]-=1
            delta=tuple(sum(b[hi][i][a]-b[lo][i][a] for i in C) for a in range(d))
            rb=-values[delta];L-=w*rb
            pl=prices[cap(lo,range(4))];ph=prices[cap(hi,range(4))]
            defect=sum(pl[a]*b[lo][i][a]-ph[a]*b[hi][i][a] for i in C for a in range(d))-rb
            positive+=w*max(0,defect);negative+=w*max(0,-defect)
        else:raise ValueError('unknown contract row')
        for j,v in row.items():combo[j]+=w*v
        rhs+=w*rb
    if combo[K]>=0 or any(v<0 for j,v in combo.items() if j!=K):raise ValueError('Farkas imbalance')
    bound=rhs/combo[K]
    if bound!=Q(data['exact_lower']):raise ValueError('bound mismatch')
    sigma_price=Q(0)
    for k in range(256):
        p=prices[cap(k,range(4))]
        for i in range(4):sigma_price+=combo[4*k+i]*sum(p[a]*b[k][i][a] for a in range(d))
    if L-D!=positive-negative-coverage_slack-sigma_price:raise ValueError('signed identity')
    return dict(seed=case['seed'],status='EXACT PASS',profiles=256,oracles=len(values),certificate_rows=dict(counts),lower=str(bound),L=str(L),D=str(D),positive_defect=str(positive),negative_defect=str(negative),coverage_slack=str(coverage_slack),nonnegative_slack=str(sigma_price))


if __name__=='__main__':
    results=[check(p) for p in sys.argv[1:]]
    print(json.dumps(results,indent=2))
