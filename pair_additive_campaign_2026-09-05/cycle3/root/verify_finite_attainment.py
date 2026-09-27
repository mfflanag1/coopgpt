"""Independent exact checks for the finite 1/6 example; standard library only.

The conventional proof in FINITE_ATTAINMENT.md identifies the full leximin
target using its first optimal face. Other final selector coordinates are not
asserted by this verifier. Input matrices and witnesses are constructed here.
"""
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

def require(ok,msg):
    if not ok: raise RuntimeError(msg)

def data():
    base=(((0,0,0),(2,0,1),(0,1,0)),
          ((0,0,1),(1,0,0),(0,0,0)),
          ((0,1,0),(3,0,0),(2,0,0)))
    matrices=[[[0]*9 for _ in range(9)] for _ in range(3)]
    for r in range(3):
        for s in range(3):
            for i,j in product(range(3),repeat=2):
                matrices[r][3*s+i][3*s+j]=base[r][i][j]
    matrices[0][0][3]=1
    matrices[1][0][8]=1
    matrices[2][3][8]=1
    outside=tuple(map(F,('1/3','4/3','5/6','5/6','5/6','1/3','7/3','5/6','1/3')))
    middle=tuple(map(F,('1/3','1/3','1/3','7/3','1/3','1/3','10/3','1/3','1/3')))
    ideal=((1,2,0,0,2,0,2,1,0),(0,2,1,1,0,0,3,0,1),(0,2,1,0,0,0,3,1,1))
    def embed(blocks): return [F(blocks[s][3*r+i]) for r in range(3) for s in range(3) for i in range(3)]
    return matrices,embed((outside,middle,outside)),embed(ideal)

def main():
    matrices,floor,ideal=data();A,B,C=matrices
    def w(i,j,k):return A[i][j]+B[i][k]+C[j][k]
    matching=[(3*s+i,3*s+j,3*s+k) for s in range(3) for i,j,k in ((0,2,2),(1,0,1),(2,1,0))]
    require(all(sorted(t[r] for t in matching)==list(range(9)) for r in range(3)), 'not a perfect matching')
    require(sum(w(*t) for t in matching)==24,'matching value changed')
    checks=0
    for name,p in (('floor',floor),('ideal',ideal)):
        require(len(p)==27 and min(p)>=0 and sum(p)==24,'bad '+name+' totals')
        for i,j,k in product(range(9),repeat=3):
            require(p[i]+p[9+j]+p[18+k]>=w(i,j,k), 'uncovered '+name+' triple '+str((i,j,k)))
            checks+=1
    require(min(floor)==F(1,3),'floor changed')
    require(floor[4]==F(1,3) and ideal[4]==2,'target values changed')
    require(ideal[3]==0,'spread witness changed')
    # The rows used in the target proof: small matching teams0 and2,
    # middle large matching team, and the three-interface triangle.
    require(w(0,2,2)==w(6,8,8)==1,'anchor team values changed')
    require(w(4,3,4)==w(0,3,8)==3,'target/coupling values changed')
    # Independent symbolic row identities in coefficient-vector form.
    def row(*ids):return [F(int(i in ids)) for i in range(27)]
    a0,f0,i0=0,11,20
    a2,f2,i2=6,17,26
    b1,d1,h1=4,12,22
    # Matching(target) - coupling + two anchor matching equations:
    # b1+h1+f0+i0+a2+f2 <=2, all terms nonnegative.
    lhs=[r-s+t+u for r,s,t,u in zip(row(b1,d1,h1),row(a0,d1,i2),row(a0,f0,i0),row(a2,f2,i2))]
    require(lhs==row(b1,h1,f0,i0,a2,f2),'ideal dual identity failed')
    require(3-3+1+1==2,'ideal RHS identity failed')
    report=dict(status='PASS',evidence='exact arithmetic plus conventional first-face proof',n=27,T=24,positive_pair_entries=sum(v>0 for M in matrices for rr in M for v in rr),whole_triple_checks=checks,target='b_1',target_x='1/3',target_H='2',target_fraction='1/6',spread_R='2',spread_over_x='6',all_other_full_selector_coordinates_certified=False)
    Path(__file__).with_name('finite_attainment_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))

if __name__=='__main__': main()
