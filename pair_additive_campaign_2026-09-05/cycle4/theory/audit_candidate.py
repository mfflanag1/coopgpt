"""Independent Fraction-only audit; no solver or campaign verification imports."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
INPUT=ROOT.parent/'experiment'/'candidate.json'

def require(condition,message):
    if not condition: raise RuntimeError(message)

def main():
    raw=json.loads(INPUT.read_text())
    A,B,C=[[[F(v)for v in row]for row in matrix]for matrix in raw['matrices']]
    m=len(A);n=3*m
    require(m==21 and all(len(P)==m and all(len(row)==m for row in P)for P in [A,B,C]),'matrix shape')
    require(all(v>=0 for P in [A,B,C]for row in P for v in row),'negative pair entry')
    def worth(t):
        i,j,k=t;return A[i][j]+B[i][k]+C[j][k]
    matching=[tuple(t)for t in raw['matching']]
    require(len(matching)==m,'matching length')
    require(all(sorted(t[s]for t in matching)==list(range(m))for s in range(3)),'not a perfect matching')
    total=sum(map(worth,matching),F(0))
    covers={}
    for field,minimum in [('x',F(1)),('y',F(0))]:
        p=list(map(F,raw[field]));require(len(p)==n,'payoff length')
        require(min(p)>=minimum,'payoff lower bound')
        require(sum(p,F(0))==total,'payoff total')
        slacks=[p[i]+p[m+j]+p[2*m+k]-worth((i,j,k))for i,j,k in product(range(m),repeat=3)]
        require(min(slacks)>=0,'uncovered triple')
        require(all(p[i]+p[m+j]+p[2*m+k]==worth((i,j,k))for i,j,k in matching),'matching equality')
        covers[field]={'total':str(total),'minimum_payoff':str(min(p)),'checked_triples':len(slacks),'minimum_triple_slack':str(min(slacks))}
    # Independently spelled-out certificate; do not reuse the generated budget vector.
    match_terms=[(3,(0,2,2)),(1,(3,5,5)),(1,(4,3,4)),(1,(6,8,8)),(1,(11,11,9)),(1,(12,13,13)),(1,(17,17,15))]
    team_terms=[(0,3,8),(0,11,2),(0,13,2),(3,8,5),(4,5,13),(12,17,9)]
    coeff=[0]*n;constant=F(0)
    for mult,t in match_terms:
        require(t in matching,'certificate matching term absent')
        constant+=mult*worth(t)
        for idx in (t[0],m+t[1],2*m+t[2]):coeff[idx]+=mult
    for t in team_terms:
        constant-=worth(t)
        for idx in (t[0],m+t[1],2*m+t[2]):coeff[idx]-=1
    support={idx:value for idx,value in enumerate(coeff)if value}
    expected={6:1,11:1,17:1,23:3,44:1,46:1,57:1}
    require(support==expected,'budget support mismatch')
    require(all(v>=0 for v in coeff) and sum(coeff)==9 and constant==9,'nine budget invalid')
    p=list(map(F,raw['x']));y=list(map(F,raw['y']))
    require(sum(F(c)*v for c,v in zip(coeff,p))==constant,'floor cover does not saturate budget')
    require(raw['target']==6 and p[6]==1 and y[6]==9,'target mismatch')
    require(worth((6,8,8))==9,'target matched-team ideal upper bound')
    # Convert this upper budget into the residual-cover dual independently.
    lam={t:F(1) for t in matching}
    for mult,t in match_terms:lam[t]-=F(mult,3)
    for t in team_terms:lam[t]=lam.get(t,F(0))+F(1,3)
    require(all(v>=0 for v in lam.values()),'negative residual dual weight')
    loads=[F(0)]*n
    for t,value in lam.items():
        for idx in (t[0],m+t[1],2*m+t[2]):loads[idx]+=value
    deficit=[1-v for v in loads]
    require(deficit==[F(c,3) for c in coeff],'residual dual deficit mismatch')
    dual_value=sum(value*(worth(t)-3) for t,value in lam.items())
    require(dual_value==total-n,'residual primal/dual equality')
    require(sum(deficit)/deficit[6]==9,'residual certificate ratio')
    report={'status':'PASS','n':n,'sector_size':m,'integral_T':str(total),
            'positive_pair_entries':sum(v>0 for P in [A,B,C]for row in P for v in row),
            'maximum_pair_value':str(max(v for P in [A,B,C]for row in P for v in row)),
            'covers':covers,
            'budget':{'support':support,'coefficient_sum':sum(coeff),'upper_bound':str(constant)},
            'residual_dual':{'value':str(dual_value),'total_deficit':str(sum(deficit)),'target_deficit':str(deficit[6]),'deficit_ratio':str(sum(deficit)/deficit[6])},
            'certified_first_floor':'1','certified_target_full_leximin_payoff':'1','certified_target_ideal':'9','certified_ratio':'1/9',
            'method':'Fraction-only complete raw triple enumeration and explicit linear-combination budget; no solver imports',
            'limitations':['Only the designated full-leximin coordinate is proved; x is used as a floor-attaining cover, not asserted to be the complete final selector.','No minimality, novelty, or all-size vanishing claim.']}
    (ROOT/'CANDIDATE_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
