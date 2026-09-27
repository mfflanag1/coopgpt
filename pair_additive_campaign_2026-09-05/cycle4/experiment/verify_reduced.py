"""Standalone rational proof for the21-player strict pair-additive witness."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import json

ROOT=Path(__file__).resolve().parent
def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def main():
    r=json.loads((ROOT/'reduced_candidate.json').read_text());M=[[[F(v) for v in row] for row in mat] for mat in r['matrices']];m=7;n=21
    require(len(M)==3 and all(len(mat)==m and all(len(row)==m and all(v.denominator==1 and 0<=v<=3 for v in row) for row in mat) for mat in M),'integer pair matrices')
    def players(t):i,j,k=t;return i,m+j,2*m+k
    def weight(t):i,j,k=t;return M[0][i][j]+M[1][i][k]+M[2][j][k]
    matching=r['matching'];require(len(matching)==m and sorted(i for t in matching for i in players(t))==list(range(n)),'matching partition')
    T=sum(map(weight,matching));require(T==15==F(r['T']),'matching optimum')
    u=list(map(F,r['floor_witness']));y=list(map(F,r['ideal_witness']));checks=0
    for p in (u,y):
        require(len(p)==n and all(v>=0 for v in p) and sum(p)==T,'point total/nonnegativity')
        for t in product(range(m),repeat=3):
            require(sum(p[i] for i in players(t))>=weight(t),'complete triple cover');checks+=1
        require(all(sum(p[i] for i in players(t))==weight(t) for t in matching),'matching equalities')
    coeff=[0]*n;rhs=F(0)
    require(len(r['budget_matching_multipliers'])==len(matching),'matching budget length')
    for t,mult in zip(matching,r['budget_matching_multipliers']):
        for i in players(t):coeff[i]+=mult
        rhs+=mult*weight(t)
    for t in r['budget_triples']:
        for i in players(t):coeff[i]-=1
        rhs-=weight(t)
    target=r['target'];require(target==3 and coeff[target]==1 and all(v>=0 for v in coeff) and sum(coeff)==9,'nonnegative nine-unit budget')
    require(rhs==3==F(r['budget_rhs']),'budget RHS')
    floor=F(1,3);require(all(v>=floor for v in u) and u[target]==floor,'positive firstfloor attainment')
    require(all(u[i]==floor for i,v in enumerate(coeff) if v),'whole firstface support')
    require(y[target]==3 and all(y[i]==0 for i,v in enumerate(coeff) if v and i!=target),'ideal bound attained')
    require(floor/3==F(1,9)<F(1,6),'strict counterexample ratio')
    result=dict(status='PASS',players=n,sector_size=m,pair_values=sorted({int(v) for mat in M for row in mat for v in row}),nonzero_pair_entries=sum(bool(v) for mat in M for row in mat for v in row),all_triple_checks=checks,T=str(T),full_leximin_target=str(floor),target_ideal='3',ratio='1/9',budget_coefficients=coeff,budget_rhs=str(rhs),proof='The whole-core budget has nonnegative coefficients summing9 and RHS3. It forces common floor<=1/3; u attains it, and each positive-budget coordinate is fixed1/3 on the entire optimal face. The target coefficient1 bounds its ideal by3; y attains3. Matching plus whole covers certify T and all coalitions.')
    (ROOT/'reduced_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
