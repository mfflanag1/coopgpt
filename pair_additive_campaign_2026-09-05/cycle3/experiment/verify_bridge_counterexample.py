"""Stdlib-only certificate of finite1/6 attainment and failed R_i bridge."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def main():
    r=json.loads((ROOT/'finite_attainment_exact.json').read_text());A,B,C=r['matrices'];m=9;n=27
    teams={(i,m+j,2*m+k):A[i][j]+B[i][k]+C[j][k] for i,j,k in product(range(m),repeat=3)}
    matching=[(3*s+i,m+3*s+j,2*m+3*s+k) for s in range(3) for i,j,k in ((0,2,2),(1,0,1),(2,1,0))]
    require([teams[t] for t in matching]==[1,3,4]*3,'old matching weights')
    x=list(map(F,r['x']));y=list(map(F,r['target_ideal_witness']))
    for name,p in [('leximin',x),('ideal',y)]:
        require(all(v>=0 for v in p) and sum(p)==24,name+' total/nonnegative')
        require(all(sum(p[i] for i in t)>=w for t,w in teams.items()),name+' fulltriplecover')
        require(all(sum(p[i] for i in t)==teams[t] for t in matching),name+' matching equalities')
    target=4;anchor_left=0;center_d=12;anchor_right=26;center_h=22
    require(teams[(anchor_left,center_d,anchor_right)]==3,'new three-interface triple')
    require((target,center_d,center_h)==matching[4],'central target matching')
    require(anchor_left in matching[0] and anchor_right in matching[6],'independent unit-team anchors')
    require(all(v>=F(1,3) for v in x),'firstfloor attained')
    require(x[anchor_left]==x[anchor_right]==x[target]==x[center_h]==F(1,3),'forced firstfloor coordinates')
    require(x[center_d]==3-2*F(1,3)==F(7,3),'central floor budget')
    require(y[target]==2 and y[anchor_left]==y[anchor_right]==1,'ideal upperbound attained')
    same_sector_reference=2
    require(y[same_sector_reference]==0 and target//m==same_sector_reference//m,'same-sector comparison')
    require(y[target]-y[same_sector_reference]==2>3*x[target]==1,'strict failure of proposed R_i<=3x_i bridge')
    require(F(2)==F(r['H'][target]),'saved ideal agrees with ordinary upperbound')
    result=dict(status='PASS',triple_checks=1458,T=24,target=target,fulllex_target='1/3',ideal='2',fraction='1/6',same_sector_reference=same_sector_reference,exact_R_target='2',three_times_fulllex_target='1',bridge='refuted',scope='Matching/unit-anchor bounds prove ideal<=2 and firstfloor pins target1/3. Ideal witness also attains same-sector difference2, while nonnegativity and ideal upperbound give R<=2.')
    (ROOT/'bridge_counterexample.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS finite1/6 attainment and bridge counterexample:1458 exacttriple checks, R=2>3x=1')

if __name__=='__main__':main()
