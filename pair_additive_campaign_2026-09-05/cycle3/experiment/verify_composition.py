"""Standard-library-only verification of all composition LP certificates.

Every upper bound is a nonnegative sum of saved inequalities plus matching
equalities. No optimization package or candidate-generation code is imported.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import json,sys

ROOT=Path(__file__).resolve().parent
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def unit(n,i,v=1):
    row=[F(0)]*n;row[i]=F(v);return row
def verify_dual(cert,A,b,E,e,objective,bound,nonnegative_count=None):
    n=len(objective);combined=[F(0)]*n;rhs=F(0)
    if nonnegative_count is None:nonnegative_count=n
    for name,rows,values,nonnegative in [('inequalities',A,b,True),('equalities',E,e,False)]:
        ids=[]
        for index,mult in cert[name]:
            require(index not in ids,'repeated dual index');ids.append(index);mult=F(mult)
            require(not nonnegative or mult>=0,'negative inequality dual')
            rhs+=mult*values[index]
            for i,v in enumerate(rows[index]):combined[i]+=mult*v
    for index,mult in cert['lower']:
        mult=F(mult);require(0<=index<nonnegative_count and mult>=0,'invalid lower bound dual');combined[index]-=mult
    require(combined==objective,'dual coefficient identity failed')
    require(rhs==bound,'dual RHS does not equal claimed optimum')

def main(tag):
    prefix='composition' if tag=='201' else 'composition_'+tag
    cert=json.loads((ROOT/(prefix+'_exact.json')).read_text());source=json.loads((ROOT/cert['input_file']).read_text())
    M=source['matrices'];m=len(M[0]);n=3*m;T=F(cert['T']);teams=list(product(range(m),repeat=3))
    require(all(len(mat)==m and all(len(row)==m and all(isinstance(v,int) and v>=0 for v in row) for row in mat) for mat in M),'invalid pair matrices')
    weights=[M[0][i][j]+M[1][i][k]+M[2][j][k] for i,j,k in teams]
    A=[];b=[]
    for (i,j,k),w in zip(teams,weights):
        if w:
            row=[F(0)]*n;row[i]=row[m+j]=row[2*m+k]=F(-1);A.append(row);b.append(F(-w))
    E=[];e=[];covered=[]
    for i,j,k in source['matching']:
        row=[F(0)]*n;row[i]=row[m+j]=row[2*m+k]=F(1);E.append(row)
        e.append(F(M[0][i][j]+M[1][i][k]+M[2][j][k]));covered.extend((i,m+j,2*m+k))
    require(sorted(covered)==list(range(n)) and sum(e)==T,'integral matching does not certify lower bound')
    checks=0
    def point(q):
        nonlocal checks
        require(len(q)==n and all(a>=0 for a in q) and sum(q)==T,'invalid core point')
        for (i,j,k),w in zip(teams,weights):
            require(q[i]+q[m+j]+q[2*m+k]>=w,'mixed triple fails');checks+=1
    x=list(map(F,cert['x']));H=list(map(F,cert['H']));point(x)
    fixed=[];last=None;queries=0
    for stage in cert['x_stages']:
        value=F(stage['level']);free=[i for i in range(n) if i not in fixed]
        require(last is None or value>last,'stage order');last=value
        require(stage['players'] and sorted(stage['players'])==sorted(i for i in free if x[i]==value),'incorrect stage partition')
        require(all(x[i]>=value for i in free),'stage witness fails floor')
        AA=A+[unit(n,i,-1) for i in free];bb=b+[-value]*len(free)
        EE=E+[unit(n,i) for i in fixed];ee=e+[x[i] for i in fixed]
        require([c['player'] for c in stage['certificates']]==stage['players'],'certificate/player mismatch')
        for q in stage['certificates']:
            verify_dual(q['dual'],AA,bb,EE,ee,unit(n,q['player']),value);queries+=1
        fixed+=stage['players']
    require(sorted(fixed)==list(range(n)),'full leximin incomplete')
    for i,h in enumerate(H):
        y=list(map(F,cert['ideal_witnesses'][i]));point(y);require(y[i]==h,'ideal not attained')
        verify_dual(cert['ideal_certificates'][i],A,b,E,e,unit(n,i),h);queries+=1
    floor=F(cert['first_floor'])
    AA=[row+[F(0)] for row in A]+[unit(n,i,-1)+[F(1)] for i in range(n)]
    verify_dual(cert['first_floor_dual'],AA,b+[F(0)]*n,[row+[F(0)] for row in E],e,unit(n+1,n),floor,nonnegative_count=n);queries+=1
    require(min(x)==floor,'floor attainment')
    minimum=min(a/h for a,h in zip(x,H) if h)
    require(minimum==F(cert['minimum_fraction']),'minimum fraction')
    central=cert['central_b'];require(x[central]/H[central]==F(cert['central_b_fraction']),'central fraction')
    report=dict(rotation=tag,status='PASS',all_triple_checks=checks,rational_dual_certificates=queries,T=str(T),full_leximin_stages=len(cert['x_stages']),minimum_fraction=str(minimum),first_floor=str(floor),central_b=str(x[central]),central_H=str(H[central]),central_fraction=str(x[central]/H[central]))
    (ROOT/(prefix+'_verification.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else '201')
