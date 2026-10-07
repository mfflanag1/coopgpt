"""Independent exact replay of finite-profile LP dual certificates.

Does not import the discovery LP or scipy. Reconstructs every used inequality
from original fixed-owner reports and an exact augmenting-path maxflow oracle.
"""
from pathlib import Path
from fractions import Fraction as Q
import importlib.util,json,copy


def helper():
    parents=Path(__file__).resolve().parents
    repo=parents[3] if len(parents)>3 else Path('/Users/maxf/projects/economics-research/game-theory/coopgpt')
    p=repo/'research_campaigns/2026-10-06-monotone-envelope/verification/verify.py'
    s=importlib.util.spec_from_file_location('flow',p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
    return v


def check(row,v):
    cert=row['certificate'];assert cert is not None
    n=row['n'];es=row['edges'];m=len(es);beta=(1<<m)*m
    totals={};constant=Q(0)
    for key,wtext in cert['multipliers'].items():
        w=Q(wtext);assert w>=0
        desc=row['certificate_rows'][key];kind=desc['type'];p=kind[1]
        assert 0<=p<1<<m
        c=[Q(row['high'][e] if p>>e&1 else row['low'][e]) for e in range(m)]
        if kind[0]=='cover':
            S=kind[2];assert 0<S<1<<m
            coeff=[(p*m+e,-1) for e in range(m) if S>>e&1]
            rhs=-v.maxflow(n,es,[ce if S>>e&1 else Q(0) for e,ce in enumerate(c)])
        elif kind[0]=='budget':
            coeff=[(p*m+e,1) for e in range(m)]+[(beta,-v.maxflow(n,es,c))];rhs=Q(0)
        else:
            assert kind[0]=='monotone';e=kind[2]
            assert 0<=e<m and not p>>e&1 and row['low'][e]<row['high'][e]
            coeff=[(p*m+e,1),((p|(1<<e))*m+e,-1)];rhs=Q(0)
        assert coeff==[tuple(pair) for pair in desc['coeff']]
        assert rhs==Q(desc['rhs'])
        constant-=w*rhs
        for col,a in coeff:totals[col]=totals.get(col,Q(0))+w*a
    assert all(a>=0 for col,a in totals.items() if col!=beta)
    assert totals[beta]<0 and constant>0
    bound=constant/-totals[beta]
    assert bound==Q(cert['bound'])
    return bound


def run(data):
    v=helper();checked=corruptions=0;best=Q(0)
    for row in data:
        if row.get('certificate') is None:continue
        best=max(best,check(row,v));checked+=1
        bad=copy.deepcopy(row);key=next(iter(bad['certificate']['multipliers']))
        bad['certificate']['multipliers'][key]='-1'
        try:check(bad,v)
        except AssertionError:corruptions+=1
        else:raise AssertionError('negative multiplier accepted')
        bad=copy.deepcopy(row)
        key=next(k for k,d in bad['certificate_rows'].items() if d['type'][0]=='cover')
        bad['certificate_rows'][key]['rhs']-=1
        try:check(bad,v)
        except AssertionError:corruptions+=1
        else:raise AssertionError('invented coalition worth accepted')
        bad=copy.deepcopy(row);bad['certificate']['bound']=str(Q(bad['certificate']['bound'])+Q(1,100))
        try:check(bad,v)
        except AssertionError:corruptions+=1
        else:raise AssertionError('inflated ratio accepted')
    assert checked and corruptions==3*checked
    return dict(status='PASS',certificates=checked,rejected_corruptions=corruptions,max_certified_bound=str(best),
                scope='Finite report restrictions only; no all-profile mechanism or new growing-family bound.')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('path');a=parser.parse_args()
    print(json.dumps(run(json.loads(Path(a.path).read_text())),indent=2))
