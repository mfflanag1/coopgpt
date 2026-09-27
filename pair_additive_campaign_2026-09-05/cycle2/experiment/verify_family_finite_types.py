"""Standard-library-only finite-type cover checks for the proposed path family."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
A=((0,0,0),(2,0,1),(0,1,0))
B=((0,0,1),(1,0,0),(0,0,0))
C=((0,1,0),(3,0,0),(2,0,0))
TEAMS={(i,3+j,6+k):A[i][j]+B[i][k]+C[j][k] for i,j,k in product(range(3),repeat=3)}
MATCH=((0,5,8),(1,3,7),(2,4,6))

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def point_check(label,p,sector_minima):
    p=tuple(map(F,p));require(all(v>=0 for v in p) and sum(p)==8,label+' nonnegativity/total')
    require(all(sum(p[i] for i in t)>=w for t,w in TEAMS.items()),label+' originaltriple')
    require(all(sum(p[i] for i in t)==w for t,w in zip(MATCH,(1,3,4))),label+' matching equality')
    require(all(p[s*3+i]>=sector_minima[s] for s in range(3) for i in range(3)),label+' global sector minima')
    require(all(p[i]+p[3+j]+sector_minima[2]>=A[i][j] for i,j in product(range(3),repeat=2)),label+' mixedA')
    require(all(p[i]+p[6+k]+sector_minima[1]>=B[i][k] for i,k in product(range(3),repeat=2)),label+' mixedB')
    require(all(p[3+j]+p[6+k]+sector_minima[0]>=C[j][k] for j,k in product(range(3),repeat=2)),label+' mixedC')
    return dict(label=label,p=list(map(str,p)),triple_checks=27,mixed_pair_checks=27)

def floor_internal(u,v):
    return (F(1,3),F(4,3)-v+u,F(4,3)-v,F(5,6)+(v-u)/2,F(1,3)+u,F(1,3),F(7,3)+v-u,F(5,6)+(v-u)/2,F(1,3))

def main():
    records=[];floor_min=(F(1,3),)*3
    first=(F(1,3),F(5,3),F(4,3),F(2,3),F(2,3),F(1,3),F(2),F(2,3),F(1,3))
    records.append(point_check('first_floor_block',first,floor_min))
    require(all(first[i]>=F(2,3) for i in (1,2,3,4,6,7)),'firstblock attains every t<=2/3')
    # Exact vertices of 0<=u<=1/3, u<=v<=1-u. Every internal
    # block has u=1/q,v=s/q in this polygon; each constraint is affine.
    vertices=((F(0),F(0)),(F(0),F(1)),(F(1,3),F(1,3)),(F(1,3),F(2,3)))
    for u,v in vertices:
        p=floor_internal(u,v)
        records.append(point_check(f'internal_floor_vertex_u{u}_v{v}',p,floor_min))
        require(all(p[i]>=F(1,3)+u for i in (1,2,3,4,6,7)),'internal nonanchors attain secondfloor')
    # For each link c_previous=b_next and d_next=h_next=(3-b_next)/2.
    # Non-h thirds have value at least1/3; only h_next adds C_dh=1.
    for b in (F(1,3),F(4,3)):
        d=h=(3-b)/2
        require(b+d+F(1,3)>=2,'floor interface ordinarythird')
        require(b+d+h==3,'floor interface hthird')
    require(B[2]==(0,0,0) and C[0]==(0,1,0),'interface third cases exhaust nonzero inherited pair contributions')
    P=(0,1,1,1,1,1,2,1,0)
    E=(0,1,0,1,2,1,2,1,0)
    D=(0,0,0,2,1,1,3,1,0)
    for label,p in [('prefix',P),('target',E),('suffix',D)]:
        records.append(point_check(label,p,(F(0),F(1),F(0))))
    for before,after,label in ((P,P,'P_to_P'),(P,E,'P_to_E'),(E,D,'E_to_D'),(D,D,'D_to_D')):
        require(before[2]+after[3]>=2,label+' ordinarythird')
        require(before[2]+after[3]+after[7]>=3,label+' hthird')
        require(before[2]>=after[1],label+' transfer inequality')
    # Saved bounded instances must match the claimed stage and ideal values.
    for q in (3,4):
        record=json.loads((ROOT/f'fixed_one_chain_{q}.json').read_text())
        require(F(record['second_fulllex_floor'])==F(1,3)+F(1,q),'bounded floor mismatch')
        require(F(record['target_ideal'])==2 and F(record['target_ratio'])==F(1,6)+F(1,2*q),'bounded corrected ideal/ratio mismatch')
    output=dict(status='PASS',scope='Finite affine-type cover proof inputs, not a numerical all-q census. Polygon vertices certify every internal floor block; sector-minimum pair inequalities certify all old mixed triples; interface cases exhaust new cross-entry triples; prefix/target/suffix types certify ideal2 for all positions with an incoming link.',records=records,total_original_triple_checks=27*len(records),total_mixed_pair_checks=27*len(records),floor_interface_endpoint_checks=4,ideal_interface_checks=12,novelty='not assessed')
    (ROOT/'family_finite_types.json').write_text(json.dumps(output,indent=2)+'\n')
    print('PASS finite affine-type covers:',len(records),'types;',27*len(records),'old triple and',27*len(records),'mixed-pair checks; all interface cases')

if __name__=='__main__':main()
