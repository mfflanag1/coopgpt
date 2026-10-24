#!/usr/bin/env python3
"""Independent stdlib semantic replay; imports no discovery or solver code."""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import json, sys

Q=Fraction


def verify(path):
    obj=json.loads(Path(path).read_text())
    R=Q(obj['R']); assert R>0
    assert obj['profiles']==list(range(256))
    # Independent specification by owner's binary state, not stored resources.
    states=[]
    for i in range(4):
        a=[]
        for s in range(4):
            a.append(tuple((R if v==i and s&1 else Q(0))+
                           (Q(1) if v==(i+1)%4 and s&2 else Q(0)) for v in range(4)))
        states.append(a)
    b={p:tuple(states[i][(p//(4**i))%4] for i in range(4)) for p in range(256)}
    assert [[int(x) for x in row] for row in b[255]]==obj['owner_full_bundles']
    def aggregate(p,S):
        return tuple(sum(b[p][i][v] for i in range(4) if S & (1<<i)) for v in range(4))
    def worth(x):
        # The three minimal vertex covers of 0--1--2--3.
        return min(sum(x[v] for v in cover) for cover in ((0,2),(1,3),(1,2)))
    def row(tag):
        kind=tag[0];a={}
        if kind=='budget':
            _,p=tag; assert p in b
            a={4*p+i:Q(1) for i in range(4)}
            a[1024]=-worth(aggregate(p,15));r=Q(0)
        elif kind=='cover':
            _,p,S=tag;assert p in b and 1<=S<16
            a={4*p+i:Q(-1) for i in range(4) if S & (1<<i)}
            r=-worth(aggregate(p,S))
        elif kind=='out':
            _,lo,hi,S=tag;assert lo in b and hi in b and lo!=hi and 1<=S<16
            for i in range(4):
                if S & (1<<i):
                    assert all(x<=y for x,y in zip(b[lo][i],b[hi][i]))
                    a[4*lo+i]=Q(1);a[4*hi+i]=Q(-1)
                else:assert b[lo][i]==b[hi][i]
            delta=tuple(sum(b[hi][i][v]-b[lo][i][v] for i in range(4)) for v in range(4))
            r=-worth(delta)
        else:raise AssertionError('unknown constraint kind')
        return {k:v for k,v in a.items() if v},r
    # Rebuild ALL constraints by coalition first, distinct from the discovery
    # enumerator's changed-owner-superset loop. Includes unchanged members.
    tags=[]
    for p in range(256):
        tags.append(['budget',p])
        tags += [['cover',p,S] for S in range(1,16)]
    for S in range(1,16):
        for lo in range(256):
            lowstates=[(lo//(4**i))%4 for i in range(4)]
            choices=[]
            for i,s in enumerate(lowstates):
                choices.append([t for t in range(4) if s&t==s] if S&(1<<i) else [s])
            for highstates in product(*choices):
                hi=sum(t*4**i for i,t in enumerate(highstates))
                if hi!=lo: tags.append(['out',lo,hi,S])
    assert len(tags)==13**4
    assert len(set(tuple(t) for t in tags))==len(tags)
    counts=Counter(t[0] for t in tags)
    assert counts==Counter(obj['row_types'])
    digests=[]; primal=list(map(Q,obj['primal'])); assert len(primal)==1025
    primal_bad=[]
    for tag in tags:
        a,r=row(tag)
        payload=[tag,[[k,str(v)] for k,v in sorted(a.items())],str(r)]
        digests.append(sha256(json.dumps(payload,separators=(',',':')).encode()).hexdigest())
        gap=sum(v*primal[k] for k,v in a.items())-r
        if gap>0:primal_bad.append([tag,str(gap)])
    digest=sha256(''.join(sorted(digests)).encode()).hexdigest()
    assert digest==obj['semantic_row_digest']
    combo=defaultdict(Q);right=Q(0);seen=set(); certcounts=Counter()
    passive=positiveout=0
    for item in obj['certificate']:
        tag=item['tag'];w=Q(item['weight']);assert w>0 and tuple(tag) not in seen
        seen.add(tuple(tag));a,r=row(tag);certcounts[tag[0]]+=1
        for k,v in a.items():combo[k]+=w*v
        right+=w*r
        if tag[0]=='out':
            _,lo,hi,S=tag
            passive+=any(b[lo][i]==b[hi][i] for i in range(4) if S&(1<<i))
            positiveout+=r<0
    assert combo[1024]<0 and all(v>=0 for k,v in combo.items() if k!=1024)
    lower=right/combo[1024];assert lower==Q(obj['exact_lower'])
    primal_ok=not primal_bad and min(primal)>=0
    return {'path':str(path),'status':'EXACT LOWER AND COMPLETE ROW CATALOG PASS',
            'R':str(R),'row_count':len(tags),'row_types':dict(counts),
            'exact_lower':str(lower),'decimal_lower':float(lower),
            'exact_primal_feasible':primal_ok,'primal_objective':str(primal[-1]),
            'exact_optimum':primal_ok and primal[-1]==lower,
            'primal_violations':len(primal_bad),'first_primal_violations':primal_bad[:3],
            'dual_row_types':dict(certcounts),'dual_passive_out_rows':passive,
            'dual_positive_outside_rows':positiveout,
            'dual_L':str(-right),'dual_D':str(-combo[1024])}


if __name__=='__main__':
    for p in sys.argv[1:]: print(json.dumps(verify(p)),flush=True)
