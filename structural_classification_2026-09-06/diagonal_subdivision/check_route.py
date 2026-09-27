from pathlib import Path
from fractions import Fraction as F
from itertools import product
import json,sys
import source_family

ROOT=Path(__file__).resolve().parent
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def instance(q,M):
    r=source_family.construct(q);source_family.verify(r);m=r['m']
    A,B,C=[[[F(v)for v in row]for row in mat]for mat in r['matrices']]
    mats=[A,C,[[M*int(i==j)for j in range(m)]for i in range(m)],B]
    T=F(r['T'])+m*M
    # Edge matching worth <= sum of row maxima; all four diagonal matchings attain it.
    require(sum(max(row)for mat in mats for row in mat)==T,'Row-bound integral worth proof')
    return r,mats,T
def main():
    result=ROOT/'VERIFICATION.json';result.write_text('{"status":"RUNNING"}\n');rows=[]
    for q in range(1,5):
        for M in (F(1,4),F(1,2),F(1),F(2),F(4)):
            r,A,T=instance(q,M);m=r['m']
            if M>=2:p=[F(v)+M/4 for v in r['floor_witness']]+[M/4]*m
            else:
                p0=[max(A[0][i])+max(A[3][i])for i in range(m)]+[max(A[1][j])for j in range(m)]+[F(0)]*(2*m)
                p2=[F(v)+F(1,2)for v in r['floor_witness']]+[F(1,2)]*m
                p=[(1-M/2)*a+(M/2)*b for a,b in zip(p0,p2)]
            require(sum(p)==T and min(p)==M/4,'Uniform floor cover totals')
            count=0
            for a,b,c,d in product(range(m),repeat=4):
                w=A[0][a][b]+A[1][b][c]+A[2][c][d]+A[3][a][d]
                require(p[a]+p[m+b]+p[2*m+c]+p[3*m+d]>=w,'Uncovered lifted team');count+=1
            diag=[A[0][j][j]+A[1][j][j]+A[2][j][j]+A[3][j][j]for j in range(m)]
            require(sum(diag)==T and max(diag)==4+M,'Ideal bound from tight matching')
            O,L,R=source_family.output,source_family.left,source_family.right
            partial=[(O(s),R(s),L(s),L(s))for s in range(1,q)]
            partial += [(O(q),R(q),R(q),L(q))]
            partial += [(L(s-1),L(s-1),O(s),O(s))for s in range(1,q+1)]
            partial += [(L(q),L(q),L(q),R(q))]
            partial += [(R(s),O(s),R(s),R(s))for s in range(1,q)]
            used=[s*m+t[s]for t in partial for s in range(4)]
            require(len(partial)==3*q and len(set(used))==len(used),'Target partial matching disjointness')
            require(set(range(4*m))-set(used)=={R(q),m+O(q),2*m+L(0),3*m+L(0)},'Target unmatched set')
            value=sum(A[0][a][b]+A[1][b][c]+A[2][c][d]+A[3][a][d]for a,b,c,d in partial)
            require(value==T-3*M,'Target ideal budget')
            rows.append({'q':q,'M':str(M),'covers':count,'floor_lower_bound':str(M/4),'ideal_upper_bound':str(4+M),'ratio_lower_bound':str(M/(4*(4+M))),'source_target_ideal_bound':str(3*M),'source_target_ratio_lower_bound':'1/12','target_partial_matching':partial})
    numerical=[]
    if '--smt'in sys.argv:
        from raw_core import solve
        for q in (1,2):
            for M in (F(1,4),F(1,2),F(1),F(2)):
                r,A,T=instance(q,M);sol=solve([(0,1),(1,2),(2,3),(0,3)],A,r['m'],known_T=T)
                require(sol is not None,'Unexpected empty core')
                require(F(sol['ratio'])>=M/(4*(4+M)),'Certified global no-go bound violated')
                target=2*r['m']
                require(F(sol['x'][target])/F(sol['H'][target])>=F(1,12),'Source-target bound violated')
                numerical.append({'q':q,'M':str(M),**sol})
                print(json.dumps({'q':q,'M':str(M),'minimum_ratio':sol['ratio']}),flush=True)
    result.write_text(json.dumps({'status':'PASS','scope':'Specific diagonal subdivision: fixed-bonus global bound and all-positive-bonus source-target bound; not a theorem for arbitrary C4','cover_cases':rows,'total_covers':sum(r['covers']for r in rows),'numerical_profiles':numerical},indent=2,default=str)+'\n')
    print(json.dumps({'status':'PASS','full_team_covers':sum(r['covers']for r in rows),'profiles':len(numerical)}))
if __name__=='__main__':main()
