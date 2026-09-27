"""Solver-free affine certificates for the all-q cover and ideal witnesses."""
from fractions import Fraction as F
from itertools import product
import json

A=((0,0,0),(2,0,1),(0,1,0))
B=((0,0,1),(1,0,0),(0,0,0))
C=((0,1,0),(3,0,0),(2,0,0))


def require(value,message):
    if not value: raise RuntimeError(message)


def nonnegative_local(p):
    slacks=[p[i]+p[3+j]+p[6+k]-A[i][j]-B[i][k]-C[j][k]
            for i,j,k in product(range(3),repeat=3)]
    require(min(slacks)>=0,'local cover')
    require(p[0]+p[5]+p[8]==1 and p[1]+p[3]+p[7]==3 and p[2]+p[4]+p[6]==4,
            'matching equalities')
    return slacks


def pair_requirements(p,third_floor):
    for matrix,offset1,offset2 in ((A,0,3),(B,0,6),(C,3,6)):
        for i,j in product(range(3),repeat=2):
            if matrix[i][j]>0:
                require(p[offset1+i]+p[offset2+j]+third_floor>=matrix[i][j],
                        'nonlocal single-pair cover')


block0=tuple(map(F,('1/3','5/3','4/3','2/3','2/3','1/3','2','2/3','1/3')))
nonnegative_local(block0);pair_requirements(block0,F(1,3))
# r=1/q, theta=s/q. The closed polygon 0<=r<=1/3, r<=theta<=1-r
# has exactly these four vertices. Each checked inequality is affine in r,theta.
vertices=((F(0),F(0)),(F(0),F(1)),(F(1,3),F(1,3)),(F(1,3),F(2,3)))
for r,theta in vertices:
    t=F(1,3)+r;c=F(4,3)-theta;b=c+r
    p=(F(1,3),b,c,(3-b)/2,t,F(1,3),4-c-t,(3-b)/2,F(1,3))
    nonnegative_local(p);pair_requirements(p,F(1,3))
    require(all(p[i]>=t for i in (1,2,3,4,6,7)),'second floor witness')
    require(all(block0[i]>=t for i in (1,2,3,4,6,7)),'block0 floor')
    require(p[1]-p[2]-p[4]+F(1,3)==0,'local budget equality')
# Coupler cover: c+d_next=(3+c)/2; adding any non-h payoff at least1/3
# leaves slack (c-1/3)/2 against value2, nonnegative for c>=1/3.
require((F(3)+F(1,3))/2+F(1,3)-2==0,'coupler boundary')

states={'P':tuple(map(F,(0,1,1,1,1,1,2,1,0))),
        'E':tuple(map(F,(0,1,0,1,2,1,2,1,0))),
        'D':tuple(map(F,(0,0,0,2,1,1,3,1,0)))}
for name,p in states.items():
    nonnegative_local(p)
    require(min(p)>=0 and min(p[3:6])>=1,'ideal nonnegativity/middle floor')
    for matrix,offset1,offset2 in ((A,0,3),(B,0,6),(C,3,6)):
        for i,j in product(range(3),repeat=2):
            if matrix[i][j]>0 and not (matrix is B and i==0 and j==2):
                require(p[offset1+i]+p[offset2+j]>=matrix[i][j],name+' ideal pair cover')
    require(p[0]+p[8]+1==B[0][2],name+' exceptional B_ai cover')
for left,right in (('P','P'),('P','E'),('E','D'),('D','D')):
    require(states[left][2]+states[right][3]==2,'ideal bridge pair')
    require(states[right][7]==1,'ideal bridge extra C value')
print(json.dumps({'status':'PASS','arithmetic':'standard-library Fraction',
                  'affine_polygon_vertices':[[str(r),str(t)] for r,t in vertices],
                  'local_and_pair_cover_states':5,'ideal_states':3,
                  'ideal_bridge_types':4,
                  'scope':'Exact affine vertex checks plus explicit nonlocal/coupler classification; q>=3'},indent=2))
