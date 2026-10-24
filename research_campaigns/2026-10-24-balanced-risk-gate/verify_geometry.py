"""Exact finite corroboration of PROOF.txt; does not certify its general proof.
All squared-norm comparisons use Fraction. No float tolerance in exact checks.
"""
from fractions import Fraction as F
from pathlib import Path
import json
P=Path(__file__).parent

def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def s(q):return str(q)
def checked_book(name,A,b,delta=F(1,4)):
    n=len(A); assert n==len(b) and all(x>0 for x in b)
    assert tuple(map(sum,zip(*A)))==(0,0)
    assert all(dot(a,a)==z*z for a,z in zip(A,b))
    T=sum(b); G=[[sum(a[j]*a[k]/z for a,z in zip(A,b)) for k in range(2)] for j in range(2)]
    assert G[0][0]+G[1][1]==T
    sums=[(F(0),F(0))]
    for a in A:sums+= [add(x,a) for x in sums]
    norms2=[dot(a,a) for a in sums];D=max(norms2);w=sums[norms2.index(D)]
    q=[dot(w,a) for a in A]
    assert sum(abs(z) for z in q)==2*D
    assert sum(q)==0
    # k_i=q_i/sqrt(D), so checking every coalition constraint needs no roots.
    qs=[F(0)]
    for z in q:qs +=[x+z for x in qs]
    assert all(z*z<=D*r for z,r in zip(qs,norms2))
    # Spectral bound D_1^2=16D <=4T lambda_max(G), in exact arithmetic.
    disc=(G[0][0]-G[1][1])**2+4*G[0][1]**2
    lhs=8*D/T-T
    assert lhs<=0 or lhs*lhs<=disc
    H=(G[0][0]-delta*T,G[1][1]-delta*T,G[0][1])
    admissible_spectrum=H[0]>=0 and H[1]>=0 and H[0]*H[1]>=H[2]**2
    admissible_owners=max(b)<=T/10
    if admissible_spectrum:assert 16*D<=4*(1-delta)*T*T
    return {'name':name,'n':n,'coalitions':len(sums),'T':s(T),'G':[[s(z) for z in row] for row in G],
       'M_squared':s(D),'normalized_diameter_squared':s(16*D/T**2),
       'spectrum_gate':bool(admissible_spectrum),'owner_gate':bool(admissible_owners),
       'witness_w':[s(z) for z in w],'charge_numerators':[s(z) for z in q],
       'charge_denominator':'sqrt('+s(D)+')','exposures':[[s(z) for z in a] for a in A],'standalone':[s(z) for z in b]}

def conical(p,q,m):
    A=[(sx*p,sy*q) for sx,sy in [(1,1),(1,-1),(-1,1),(-1,-1)] for _ in range(m)]
    return A,[F(1)]*len(A)

def main():
    if not __debug__:
        raise RuntimeError("Exact verifier requires assertions; do not run with -O.")
    cases=[]
    for p,q,m in [(F(4,5),F(3,5),1),(F(4,5),F(3,5),3),(F(12,13),F(5,13),2),(F(20,29),F(21,29),3)]:
        A,b=conical(p,q,m);out=checked_book(f'cone_{p}_{q}_m{m}',A,b)
        assert F(out['normalized_diameter_squared'])==4*max(p*p,q*q)
        # The all-ones core allocation uniquely optimizes min and max at mean1.
        out['full_selectors_exact']='all ones; rho=0 by feasibility and average'
        cases.append(out)
    for m in (1,3):
        A=[(F(x),F(y)) for x,y in [(1,0),(-1,0),(0,1),(0,-1)] for _ in range(m)]
        cases.append(checked_book(f'axes_m{m}',A,[F(1)]*len(A)))
    bases=[[(3,4,5),(5,12,13),(0,2,2)],[(3,4,5),(5,-12,13),(8,15,17),(7,-24,25)],[(1,0,1),(0,1,1),(3,4,5),(5,-12,13),(8,15,17)]]
    for j,base in enumerate(bases):
        A=[];b=[]
        for x,y,z in base:A.extend([(F(x),F(y)),(F(-x),F(-y))]);b.extend([F(z),F(z)])
        cases.append(checked_book(f'mixed_antithetic_{j}',A,b))
    for name,A,b in [('triangle',[(F(3),F(0)),(F(0),F(4)),(F(-3),F(-4))],[F(3),F(4),F(5)]),('one_factor',[(F(x),F(0)) for x in [2,1,-1,-1,-1]],[F(x) for x in [2,1,1,1,1]])]:
        cases.append(checked_book(name,A,b))
    result={'evidence':'Exact rational finite checks; general and algebraic sharpness proofs are in PROOF.txt.','cases':cases,'total_coalitions':sum(x['coalitions'] for x in cases),'case_count':len(cases),'all_checks_passed':True}
    (P/'exact_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'}))
if __name__=='__main__':main()
