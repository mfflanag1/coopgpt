"""Exact support for the hybrid-rule obstruction, standard library only."""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import json

REPO=next((p for p in Path(__file__).resolve().parents if (p/'research_campaigns').is_dir()),
          Path('/Users/maxf/projects/economics-research/game-theory/coopgpt'))
spec=importlib.util.spec_from_file_location('v',REPO/'research_campaigns/2026-10-06-monotone-envelope/verification/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

def run():
    profiles=0;cut_families=0;conditional=0
    beta=Q(1,2)
    assert beta/2-beta*beta/6-beta/3==Q(1,24)
    for k in range(1,9):
        n=k+3;A=k;B=k+1;t=k+2
        edges=[(i,i+1) for i in range(k)]+[(0,B),(A,t),(A,B),(B,t)]
        b,a,g,h=range(k,k+4)
        c=[Q(1)]*k+[beta,Q(1),Q(1),Q(1)]
        expected=sorted([((1<<i)|(1<<j)) for i in range(k) for j in (b,h)]
                        +[(1<<a)|(1<<h),(1<<a)|(1<<b)|(1<<g)])
        assert v.cutsets(n,edges)==expected
        assert v.path_blockers(v.paths(n,edges))==expected
        assert len(expected)==2*k+2
        assert v.maxflow(n,edges,c)==1+beta
        assert v.effective(n,edges,c)==c
        cut_families+=1
        for i in range(k):
            for own in (Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)):
                report=c.copy();report[i]=own
                D=v.effective(n,edges,report)
                assert D==[own]*k+[beta,own,own,min(Q(1),beta+own)]
                profiles+=1
            for Ub in (Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)):
                for Uh in (Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)):
                    lo=min(beta*Ub,Uh)-beta*min(Ub,Uh)
                    assert 0<=lo<=beta
                    conditional+=1
    return dict(status='PASS',cut_families=cut_families,exact_profiles=profiles,
                conditional_grid_checks=conditional,per_owner_lower_bound='1/24',
                normalized_K_coefficient='1/72',scope='Finite support, not the universal proof.')

if __name__=='__main__':print(json.dumps(run(),indent=2))
