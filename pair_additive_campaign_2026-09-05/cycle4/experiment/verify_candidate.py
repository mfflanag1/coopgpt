"""Independent standard-library proof of full-leximin target ratio1/9.

The saved x is a first-floor witness, not claimed to be the complete selector.
The exact budget pins the target on the entire first optimal face.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import json

ROOT=Path(__file__).resolve().parent
def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def main():
    r=json.loads((ROOT/'candidate.json').read_text());M=[[[F(v) for v in row] for row in mat] for mat in r['matrices']]
    m=21;n=63;require(len(M)==3 and all(len(mat)==m and all(len(row)==m and all(v>=0 for v in row) for row in mat) for mat in M),'pair matrix shape/nonnegativity')
    teams=list(product(range(m),repeat=3))
    def weight(t):i,j,k=t;return M[0][i][j]+M[1][i][k]+M[2][j][k]
    def players(t):i,j,k=t;return (i,m+j,2*m+k)
    matching=r['matching'];require(sorted(i for t in matching for i in players(t))==list(range(n)),'matching partition')
    T=sum(map(weight,matching));require(T==87,'total')
    u=list(map(F,r['x']));y=list(map(F,r['y']));checks=0
    for p in (u,y):
        require(len(p)==n and all(v>=0 for v in p) and sum(p)==T,'point total/nonnegativity')
        for t in teams:
            require(sum(p[i] for i in players(t))>=weight(t),'mixed triple cover');checks+=1
        require(all(sum(p[i] for i in players(t))==weight(t) for t in matching),'matching equalities')
    # The matching coefficients and six covers are read here as explicit
    # arithmetic, independently of both the inverse LP and its saved dual.
    matching_terms=[(0,3),(3,1),(4,1),(6,1),(9,1),(13,1),(15,1)]
    triple_terms=[(0,3,8),(0,11,2),(0,13,2),(3,8,5),(4,5,13),(12,17,9)]
    coefficient=[0]*n;rhs=F(0)
    for idx,mult in matching_terms:
        for i in players(matching[idx]):coefficient[i]+=mult
        rhs+=mult*weight(matching[idx])
    for t in triple_terms:
        for i in players(t):coefficient[i]-=1
        rhs-=weight(t)
    expected={6:1,11:1,17:1,23:3,44:1,46:1,57:1}
    require(coefficient==[expected.get(i,0) for i in range(n)],'universal budget coefficient identity')
    require(rhs==9 and sum(coefficient)==9,'nine-unit budget')
    target=6;require(r['target']==target and coefficient[target]==1,'target support')
    require(all(v>=1 for v in u) and all(u[i]==1 for i in expected),'firstfloor attainment')
    require(y[target]==rhs==9 and all(y[i]==0 for i in expected if i!=target),'ideal attainment')
    require(all(v.denominator==1 and v%3==0 for mat in M for row in mat for v in row),'integer reduction by3')
    result=dict(status='PASS',players=n,sector_size=m,all_triple_checks=checks,T='87',target=target,first_positive_floor='1',full_leximin_target='1',ideal='9',ratio='1/9',below_one_sixth=True,budget_coefficients=expected,budget_rhs='9',scaled_by_one_third=dict(T='29',first_positive_floor='1/3',full_leximin_target='1/3',ideal='3',nonzero_pair_values=sorted({str(v/3) for mat in M for row in mat for v in row if v})),proof='Matching minus six valid triple inequalities gives nonnegative budget<=9. All players>=t gives9t<=9; saved u attains t1 and the entire first face pins each positive-budget player to1. Nonnegativity gives H_target<=9, attained by saved y. Matching and both whole covers certify integral T and the whole core.')
    (ROOT/'candidate_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':main()
