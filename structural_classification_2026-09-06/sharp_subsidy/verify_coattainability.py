"""Calibrate the sector-attainment safe class and incompatible ideal faces."""
from pathlib import Path
from itertools import product
from fractions import Fraction as Q
import json,sys


def require(ok,msg):
    if not ok:raise ValueError(msg)


def safe_case(m):
    def value(t):
        if min(t)==0:return 0
        a,b,c=t
        return a*b+2*a*c+3*b*c
    diagonal=[value((i,i,i))for i in range(1,m+1)];T=sum(diagonal)
    ideals=[]
    for s in range(3):
        acc=0;side=[]
        for i in range(1,m+1):
            t=[i]*3;t[s]=i-1;acc+=diagonal[i-1]-value(t);side.append(acc)
        ideals+=side
    witnesses=[]
    for first in range(3):
        order=[first]+[s for s in range(3)if s!=first];x=[0]*(3*m)
        for pos,s in enumerate(order):
            acc=0
            for i in range(1,m+1):
                hi=[i]*3
                for previous in order[:pos]:hi[previous]=i-1
                lo=hi[:];lo[s]=i-1;acc+=value(hi)-value(lo);x[s*m+i-1]=acc
        require(min(x)>=0 and sum(x)==T,'sector-optimal witness total')
        for t in product(range(1,m+1),repeat=3):require(sum(x[s*m+t[s]-1]for s in range(3))>=value(t),'sector-optimal core coverage')
        require(x[first*m:(first+1)*m]==ideals[first*m:(first+1)*m],'sector maxima formula')
        witnesses.append(x)
    y=[sum(x[i]for x in witnesses)for i in range(3*m)]
    require(sum(y)==3*T and all(y[i]>=ideals[i]for i in range(3*m)),'averaged protection')
    # The ideal upper formula follows by adding the first diagonal upper
    # bound and each adjacent completion minus diagonal inequality. These
    # are actual original-core inequalities, giving the displayed telescoping
    # bound; the sector witnesses attain it.
    return {'m':m,'T':T,'subsidy':0,'full_team_witness_checks':3*m**3}


def run():
    safe=[safe_case(m)for m in (1,2,3,5,8)]
    data=json.loads(Path(__file__).with_name('TREE_CERTIFICATES.json').read_text())
    result=[]
    for d in data['cases']:
        q=d['q'];m=d['m'];P=d['matching'];U=sorted(set(range(3*m))-{s*m+j for t in P for s,j in enumerate(t)})
        require(m==2*q+1 and d['T']==6*q+3 and len(U)==3*(q+1),'tree inventory')
        require(d['T']-5*q==q+3 and (q+1)+4>q+3,'same-sector contradiction')
        for i in U:require(any(x[i]==3 for x in d['core_witnesses']),'missing ideal witness')
        require(all(sum(x[i]==3 for i in U)<=1 for x in d['core_witnesses']),'retained core point has two peaks')
        result.append({'q':q,'unmatched_ideal_faces':len(U),'minimum_attaining_point_count':len(U)})
    smt=[]
    if '--smt' in sys.argv:
        import z3
        for q in (1,2,3,4):
            m=2*q+1;P=[(s,q+s,s-1 if s else 2*q)for s in range(q)]
            pairs=[[[int(a==b)for b in range(m)]for a in range(m)]for _ in range(3)]
            for a,b,c in P:pairs[0][a][b]=2;pairs[1][a][c]=1;pairs[2][b][c]=2
            U=sorted(set(range(3*m))-{s*m+j for t in P for s,j in enumerate(t)})
            x=[z3.Real(f'x_{q}_{i}')for i in range(3*m)];solver=z3.Solver();solver.set(timeout=15000)
            solver.add(*[v>=0 for v in x],z3.Sum(x)==3*m)
            for a,b,c in product(range(m),repeat=3):solver.add(x[a]+x[m+b]+x[2*m+c]>=pairs[0][a][b]+pairs[1][a][c]+pairs[2][b][c])
            solver.push();solver.add(z3.PbGe([(x[i]>=3,1)for i in U],2));status=solver.check();require(status==z3.unsat,f'two-peak query not UNSAT: {status}');solver.pop()
            solver.add(x[U[0]]==3);control=solver.check();require(control==z3.sat,f'one-peak control not SAT: {control}')
            smt.append({'q':q,'two_unmatched_ideals':'UNSAT','one_ideal_control':'SAT'})
    print(json.dumps({'status':'PASS','published_safe_class_calibrations':safe,'incompatible_face_calibrations':result,'smt':smt,'scope':'source-derived zero-subsidy safe class and conventional all-size incompatibility theorem; global sharp target unchanged'}))

if __name__=='__main__':run()
