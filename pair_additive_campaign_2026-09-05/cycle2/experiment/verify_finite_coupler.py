"""Stdlib certificate for the18-player contraction's full-lex target coordinate."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def main():
    record=json.loads((ROOT/'candidate_exact.json').read_text())
    A,B,C=[[[F(v) for v in row] for row in mat] for mat in record['matrices']]
    teams={(i,6+j,12+k):A[i][j]+B[i][k]+C[j][k] for i,j,k in product(range(6),repeat=3)}
    matching=[tuple(t) for t in record['matching']]
    require(sorted(i for t in matching for i in t)==list(range(18)),'matching partition')
    require([teams[t] for t in matching]==[1,3,4,1,3,4],'matching weights')
    x=list(map(F,record['x']));z=list(map(F,record['z']))
    old_ideal=(0,0,0,3,1,1,3,0,0)
    y=[F(old_ideal[c*3+j]) for c in range(3) for block in range(2) for j in range(3)]
    for name,p in [('x',x),('z',z),('ideal_d0',y)]:
        require(all(v>=0 for v in p) and sum(p)==16,name+' nonnegative total')
        require(all(sum(p[i] for i in t)>=w for t,w in teams.items()),name+' complete triplecover')
        require(all(sum(p[i] for i in t)==teams[t] for t in matching),name+' matching equalities')
    first=matching[0]+matching[3]
    require(all(x[i]==F(1,3) for i in first),'firstfloor matching force')
    require(all(v>=F(1,3) for v in x),'firstfloor attainment')
    # Definitions of the three ordinary inequalities summed in the report.
    require(teams[(1,8,12)]==4,'firstblock crossing weight')
    require(teams[(4,11,15)]==4,'secondblock crossing weight')
    require(teams[(2,9,16)]==3,'new transfer triple weight')
    def basis(**vals):
        a=[F(0)]*18
        for i,v in vals.items():a[int(i)]=F(v)
        return a
    budget=basis(**{'2':1,'6':1,'7':1,'13':1,'8':-1})
    transfer=basis(**{'2':-1,'4':1})
    next_budget=basis(**{'4':-1,'11':-1,'5':1,'10':1})
    combined=[a+b+c for a,b,c in zip(budget,transfer,next_budget)]
    expected=basis(**{'5':1,'10':1,'6':1,'7':1,'13':1,'8':-1,'11':-1})
    require(combined==expected,'coefficient cancellation')
    pinned=(5,10,6,7,13)
    require(all(x[i]==F(11,15) for i in pinned),'secondfloor bound attained at each summand')
    require(all(x[i]>=F(11,15) for i in range(18) if i not in first),'remaining freepayoffs attain secondfloor')
    require(5*F(11,15)==3+2*F(1,3),'secondfloor budget equality')
    require(y[6]==3 and x[6]/y[6]==F(11,45),'target ideal witness and contraction')
    require(6 in matching[1] and teams[matching[1]]==3,'ideal upperbound matching')
    require(F(11,45)<F(5,18),'strict ratio contraction')
    rho=sum(abs(a-b) for a,b in zip(x,z))/16
    require(rho==F(91,240),'saved opposite-selector distance arithmetic')
    output=dict(status='PASS',scope='Conventional proof inputs for integral total16, firsttwo leximinfaces, targetd0 exactfulllex payoff11/15, exactideal3, and ratio11/45. Full vectorz is triple-feasible and distance arithmetic checked here; its lexicographic optimality is from the separate exact staged computation.',triple_checks=3*216,target_ratio='11/45',matching_value='16',second_floor='11/15',target_ideal='3')
    (ROOT/'finite_coupler_certificate.json').write_text(json.dumps(output,indent=2)+'\n')
    print('PASS finite coupler:648 exact triplechecks, two-stage target pinning, ideal3, ratio11/45')

if __name__=='__main__':main()
