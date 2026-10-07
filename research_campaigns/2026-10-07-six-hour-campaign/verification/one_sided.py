"""Exact support for the hybrid-rule obstruction, standard library only."""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import json


def _verify_assert(condition, message=None):
    """Always-active assertion; evaluate an optional message only on failure."""
    if not condition:
        if message is None:
            raise AssertionError
        raise AssertionError(message())

REPO=Path(__file__).resolve().parents[3]
dependency=REPO/'research_campaigns/2026-10-06-monotone-envelope/verification/verify.py'
if not dependency.is_file():
    raise FileNotFoundError(f'Required verifier dependency not found: {dependency}')
spec=importlib.util.spec_from_file_location('v',dependency)
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

def run():
    profiles=0;cut_families=0;conditional=0
    beta=Q(1,2)
    _verify_assert((beta/2-beta*beta/6-beta/3==Q(1,24)))
    for k in range(1,9):
        n=k+3;A=k;B=k+1;t=k+2
        edges=[(i,i+1) for i in range(k)]+[(0,B),(A,t),(A,B),(B,t)]
        b,a,g,h=range(k,k+4)
        c=[Q(1)]*k+[beta,Q(1),Q(1),Q(1)]
        expected=sorted([((1<<i)|(1<<j)) for i in range(k) for j in (b,h)]
                        +[(1<<a)|(1<<h),(1<<a)|(1<<b)|(1<<g)])
        _verify_assert((v.cutsets(n,edges)==expected))
        _verify_assert((v.path_blockers(v.paths(n,edges))==expected))
        _verify_assert((len(expected)==2*k+2))
        _verify_assert((v.maxflow(n,edges,c)==1+beta))
        _verify_assert((v.effective(n,edges,c)==c))
        cut_families+=1
        for i in range(k):
            for own in (Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)):
                report=c.copy();report[i]=own
                D=v.effective(n,edges,report)
                _verify_assert((D==[own]*k+[beta,own,own,min(Q(1),beta+own)]))
                profiles+=1
            for Ub in (Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)):
                for Uh in (Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)):
                    lo=min(beta*Ub,Uh)-beta*min(Ub,Uh)
                    _verify_assert((0<=lo<=beta))
                    conditional+=1
    return dict(status='PASS',cut_families=cut_families,exact_profiles=profiles,
                conditional_grid_checks=conditional,per_owner_lower_bound='1/24',
                normalized_K_coefficient='1/72',scope='Finite support, not the universal proof.')

if __name__=='__main__':print(json.dumps(run(),indent=2))
