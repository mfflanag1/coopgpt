from pathlib import Path
from fractions import Fraction as F
from itertools import product
import json,sys,copy
from certificates import *
from family import construct
OUT=Path(__file__).resolve().parent

def check_embeddings():
    results=[];count=0
    cases=[(1,4,[0,1,2,3]),(2,5,[0,1,2,3,4]),(1,6,[0,1,2,3,4,5]),(1,8,[0,1,2,3,4,5,6,7]),(1,5,[4,3,2]),(2,6,[5,4,3,2])]
    for q,K,cycle in cases:
        # Complete allowed graph also tests zero-valued chords and extra edges.
        allowed=[(i,j)for i in range(K)for j in range(i+1,K)]
        g=construct(q,K,cycle,allowed);m=g['m'];a,b,c=cycle[:3];high={3*s-2 for s in range(1,q+1)}|{3*s-1 for s in range(1,q+1)}
        def lift(old):
            p=[F(0)]*(K*m)
            for oldside,newside in enumerate((a,b,c)):
                p[newside*m:(newside+1)*m]=old[oldside*m:(oldside+1)*m]
            for side in cycle[3:]:
                p[side*m:(side+1)*m]=[F(2*int(j in high))for j in range(m)]
            return p
        U,delta=unmatched(g);require(delta==1,'lost extension budget')
        old=independent_triangle(q);oldU,_=unmatched(old)
        selected=[(b if i//m==1 else c)*m+i%m for i in oldU if i>=m]
        require(len(selected)==2*q+2 and set(selected)<=set(U),'lost original unmatched players')
        vs=vertices(q)
        for i in [i for i in oldU if i>=m]:
            v=next(v for v in vs if v[i]==1)
            p=lift(v);count+=check_cover(g,p)
            newi=(b if i//m==1 else c)*m+i%m;require(p[newi]==1,'ideal witness lift')
        positive=list(map(F,g['x_floor']));count+=check_cover(g,positive);require(min(positive)>0,'positive core witness')
        results.append({'q':q,'K':K,'cycle':cycle,'certified_rho_upper':str(F(1,2*q+2)),'ideal_lower_witnesses':len(selected),'status':'PASS'})
    return results,count

def smt_checks():
    import z3
    results=[]
    for q in range(1,5):
        g=independent_triangle(q);m=g['m'];p=[z3.Real(f'p{i}')for i in range(3*m)]
        raw=[v>=0 for v in p]+[z3.Sum(p)==g['T']]
        for a,b,c in product(range(m),repeat=3):
            A,B,C=g['matrices'];raw.append(p[a]+p[m+b]+p[2*m+c]>=A[a][b]+B[a][c]+C[b][c])
        alpha=p[0];l0=p[2*m];ds=[];rs=[];es=[];fs=[]
        compact=[alpha>=0,l0>=0]
        for j in range(m):
            if j%3!=1:compact.append(p[j]==alpha)
            val=4 if j%3==1 else 1
            compact.append(p[j]+p[m+j]+p[2*m+j]==val)
        for s in range(1,q+1):
            O,L,R,P=3*s-2,3*s-1,3*s,(0 if s==1 else 3*s-4)
            d=p[m+O];r=p[2*m+R];e=p[2*m+O]-p[2*m+P]
            f=p[2*m+L]-alpha-r-d-p[2*m+O]
            ds.append(d);rs.append(r);es.append(e);fs.append(f)
            compact.extend([d>=0,r>=0,e>=0,f>=0])
        compact.append((q+1)*alpha+l0+z3.Sum(ds+rs+es+fs)<=1)
        H=ideals(q);t=z3.Real('t')
        bounds=[p[i]>=z3.Q(h.numerator,h.denominator)*t for i,h in enumerate(H)]
        tests=[('raw_implies_simplex',raw+[z3.Not(z3.And(compact))]),('simplex_implies_raw',compact+[z3.Not(z3.And(raw))]),('ideal_upper',raw+[z3.Or([v>z3.Q(h.numerator,h.denominator)for v,h in zip(p,H)])]),('rho_upper',raw+bounds+[t>z3.Q(1,2*q+3)])]
        for label,cons in tests:
            solver=z3.Solver();solver.set(timeout=60000);solver.add(cons);answer=solver.check()
            require(answer==z3.unsat,f'SMT {label} {q}: {answer}')
            results.append({'q':q,'query':label,'result':'UNSAT'})
    return results

def main():
    (OUT/'VERIFICATION.json').write_text('{"status":"RUNNING"}\n')
    triangles=[verify_triangle(q)for q in range(1,9)]
    for rec in triangles: print(json.dumps({k:rec[k]for k in ('q','rho','cover_checks','status')}),flush=True)
    embeddings,extra=check_embeddings()
    negatives=[]
    badH=ideals(1);badH[0]=F(1)
    badx=optimal(1);badx[0]+=F(1,100)
    badg=independent_triangle(1);badg['partial_matching']+=badg['partial_matching'][:1]
    for label,args in [('inflated_ideal',{'H':badH}),('inefficient_cover',{'x':badx}),('overlapping_matching',{'market':badg})]:
        try:verify_triangle(1,**args)
        except ValueError:negatives.append(label)
        else:raise ValueError('negative control accepted '+label)
    queries=smt_checks()if '--smt'in sys.argv else []
    output={'status':'PASS','triangles':triangles,'embeddings':embeddings,'total_cover_checks':sum(r['cover_checks']for r in triangles)+extra,'smt_queries':queries,'negative_controls_rejected':negatives}
    (OUT/'CERTIFICATES.json').write_text(json.dumps({'triangles':triangles,'embeddings':embeddings},indent=2)+'\n')
    (OUT/'VERIFICATION.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'status':'PASS','covers':output['total_cover_checks'],'smt_queries':len(queries),'negative_controls':len(negatives)}))
if __name__=='__main__':
    try:main()
    except BaseException as err:
        (OUT/'VERIFICATION.json').write_text(json.dumps({'status':'FAILED','error':str(err)})+'\n');raise
