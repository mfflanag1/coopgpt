"""Independent raw pair-matrix and exact-rational checks of the q-block family."""
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import z3


def require(value, message):
    if not value:
        raise RuntimeError(message)


def family(q):
    m = 3*q
    A = [[0]*m for _ in range(m)]
    B = [[0]*m for _ in range(m)]
    C = [[0]*m for _ in range(m)]
    a0 = ((0,0,0),(2,0,1),(0,1,0))
    b0 = ((0,0,1),(1,0,0),(0,0,0))
    c0 = ((0,1,0),(3,0,0),(2,0,0))
    for s in range(q):
        for i,j in product(range(3),repeat=2):
            A[3*s+i][3*s+j] = a0[i][j]
            B[3*s+i][3*s+j] = b0[i][j]
            C[3*s+i][3*s+j] = c0[i][j]
    for s in range(q-1):
        A[3*s+2][3*(s+1)] = 2
    return A,B,C


def full_floor_witness(q):
    blocks = [(F(1,3),F(5,3),F(4,3),F(2,3),F(2,3),F(1,3),F(2),F(2,3),F(1,3))]
    t = F(1,3)+F(1,q)
    for s in range(1,q):
        c = F(4,3)-F(s,q)
        b = F(4,3)-F(s-1,q)
        blocks.append((F(1,3),b,c,(3-b)/2,t,F(1,3),4-c-t,(3-b)/2,F(1,3)))
    return tuple(blocks[s][3*sector+r] for sector in range(3) for s in range(q) for r in range(3))


def ideal_witness(q,target):
    P=(0,1,1,1,1,1,2,1,0)
    E=(0,1,0,1,2,1,2,1,0)
    D=(0,0,0,2,1,1,3,1,0)
    blocks=[P if s<target else E if s==target else D for s in range(q)]
    return tuple(F(blocks[s][3*sector+r]) for sector in range(3) for s in range(q) for r in range(3))


def check_point(q,matrices,point,name):
    A,B,C=matrices;m=3*q
    require(len(point)==9*q and min(point)>=0 and sum(point)==8*q,name+' efficiency')
    slacks=[point[i]+point[m+j]+point[2*m+k]-A[i][j]-B[i][k]-C[j][k]
            for i,j,k in product(range(m),repeat=3)]
    require(min(slacks)>=0,name+' raw triple cover')
    return len(slacks)


def solver_checks(q,matrices):
    A,B,C=matrices;m=3*q
    p=z3.Reals(' '.join('p'+str(i) for i in range(9*q)))
    base=[v>=0 for v in p]+[z3.Sum(p)==8*q]
    base += [p[i]+p[m+j]+p[2*m+k]>=A[i][j]+B[i][k]+C[j][k]
             for i,j,k in product(range(m),repeat=3)]
    count=0
    def no(constraints,bad,label):
        nonlocal count
        solver=z3.Solver();solver.set(timeout=30000)
        solver.add(*constraints,bad)
        status=solver.check();count+=1
        require(status==z3.unsat,label+':'+str(status))
    first=[p[i]>=z3.RealVal('1/3') for i in range(9*q)]
    anchors=[3*s+r+sector*m for s in range(q) for sector,r in ((0,0),(1,2),(2,2))]
    no(base,z3.And([v>z3.RealVal('1/3') for v in p]),'first floor')
    no(base+first,z3.Or([p[i]!=z3.RealVal('1/3') for i in anchors]),'anchors forced')
    remaining=[i for i in range(9*q) if i not in anchors]
    t=z3.RealVal(str(F(1,3)+F(1,q)))
    no(base+first,z3.And([p[i]>t for i in remaining]),'second floor')
    second=[p[i]>=t for i in remaining]
    targets=[m+3*s+1 for s in range(1,q)]
    no(base+first+second,z3.Or([p[i]!=t for i in targets]),'all internal e forced at second floor')
    no(base,z3.Or([p[i]>2 for i in targets]),'all internal e ideal upper bound')
    return count


result=[];totalcovers=0;totalqueries=0
for q in (3,4,5,6,8,12,20):
    matrices=family(q)
    m=3*q;A,B,C=matrices
    matching=[(3*s,m+3*s+2,2*m+3*s+2) for s in range(q)]
    matching += [(3*s+1,m+3*s,2*m+3*s+1) for s in range(q)]
    matching += [(3*s+2,m+3*s+1,2*m+3*s) for s in range(q)]
    require(sorted(i for team in matching for i in team)==list(range(9*q)),'matching partition')
    require(sum(A[i][j-m]+B[i][k-2*m]+C[j-m][k-2*m] for i,j,k in matching)==8*q,'matching value')
    covercount=check_point(q,matrices,full_floor_witness(q),'floor witness')
    for target in range(1,q):
        point=ideal_witness(q,target)
        require(point[m+3*target+1]==2,'ideal attained')
        covercount+=check_point(q,matrices,point,'ideal witness '+str(target))
    queries=solver_checks(q,matrices) if q<=6 else 0
    totalcovers+=covercount;totalqueries+=queries
    result.append({'q':q,'players':9*q,'T':8*q,'target_e_floor':str(F(1,3)+F(1,q)),
                   'target_e_ideal':2,'fraction':str(F(1,6)+F(1,2*q)),
                   'raw_triple_checks':covercount,'unsat_queries':queries,'status':'PASS'})
print(json.dumps({'status':'PASS','cases':result,'raw_triple_checks':totalcovers,
                  'unsat_queries':totalqueries,'solver':z3.get_version_string(),
                  'scope':'Finite independent raw pair-matrix exact-cover and LRA checks; any non-UNSAT rejected'},indent=2))
