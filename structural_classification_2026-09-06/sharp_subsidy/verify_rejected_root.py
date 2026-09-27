"""Verify the heterogeneous three-label counterexample to a root discount."""
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path


def require(ok, why):
    if not ok:raise ValueError(why)


def run():
    d=json.loads(Path(__file__).with_name('ROOT_COUNTEREXAMPLE.json').read_text())
    M=[[[F(v)for v in row]for row in mat]for mat in d['matrices']]
    ps=[[F(v)for v in p]for p in d['core_witnesses']]
    T=sum(M[k][i][i]for k in range(3)for i in range(3))
    require(T==1 and len(ps)==9 and min(v for mat in M for row in mat for v in row)>=0,'invalid market')
    for p in ps:
        require(len(p)==9 and min(p)>=0 and sum(p)==T,'core budget')
        for a,b,c in product(range(3),repeat=3):
            require(p[a]+p[3+b]+p[6+c]>=M[0][a][b]+M[1][a][c]+M[2][b][c],'core cover')
    P=[tuple(t)for t in d['partial_matching']]
    used=[k*3+t[k]for t in P for k in range(3)]
    require(len(set(used))==len(used),'overlap')
    U=set(range(9))-set(used)
    J=sum(M[0][a][b]+M[1][a][c]+M[2][b][c]for a,b,c in P)+sum(ps[i][i]for i in U)/3-T
    root=d['root'];root_worth=sum(M[k][root][root]for k in range(3))
    require(J+root_worth/3> T/3,'root bound not refuted')
    print(json.dumps({'status':'PASS','exact_obstruction_lower':str(J),'root_worth':str(root_worth),'enhanced_objective':str(J+root_worth/3),'refuted_upper':str(T/3)}))


if __name__=='__main__':run()
