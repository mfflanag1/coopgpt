from fractions import Fraction as F
from pathlib import Path
from itertools import product
import json,z3
from independent_audit import Q,query,require
OUT=Path(__file__).resolve().parent

def additive(sectors,sharp=False):
    m=len(sectors[0]);mins=list(map(min,sectors));S=sum(mins)
    require(all(len(s)==m for s in sectors) and S>=0,'invalid parameters')
    b=[[F(a)-min(s) for a in s] for s in sectors];T=sum(map(sum,sectors));require(T>0,'zero total')
    p=[[z3.FreshReal('add') for i in s] for s in sectors];flat=sum(p,[])
    cs=[a>=0 for a in flat]+[sum(flat)==Q(T)]
    cs += [p[0][i]+p[1][j]+p[2][k]>=Q(sectors[0][i]+sectors[1][j]+sectors[2][k]) for i,j,k in product(range(m),repeat=3)]
    ts=[p[s][0]-Q(b[s][0]) for s in range(3)]
    form=[ts[s]>=0 for s in range(3)]+[sum(ts)==Q(S)]
    form += [p[s][i]==Q(b[s][i])+ts[s] for s in range(3) for i in range(m)]
    query(cs+[z3.Not(z3.And(*form))],z3.unsat,'additive core outside simplex')
    query(form+[z3.Not(z3.And(*cs))],z3.unsat,'additive simplex outside core')
    x=[[a+F(S,3) for a in row] for row in b];xf=sum(x,[])
    query(cs+[a>Q(F(S,3)) for a in flat],z3.unsat,'additive floor improvement')
    query(cs+[a>=Q(F(S,3)) for a in flat]+[z3.Or(*[a!=Q(v) for a,v in zip(flat,xf)])],z3.unsat,'additive floor nonunique')
    caps=[a+S for a in sum(b,[])]
    query(cs+[z3.Or(*[a>Q(v) for a,v in zip(flat,caps)])],z3.unsat,'additive caps')
    for s in range(3):
        witness=[p[t][i]==Q(b[t][i]+(S if s==t else 0)) for t in range(3) for i in range(m)]
        query(cs+witness,z3.sat,'simultaneous same sector extrema')
    dist=sum(z3.If(a>=Q(v),a-Q(v),Q(v)-a) for a,v in zip(flat,xf))
    query(cs+[dist>Q(F(4*m*S,3))],z3.unsat,'additive all core distance')
    if sharp:
        z=[[F(int(i==0)) for i in range(m)]]*2+[[F(1)]*m]
        zf=sum(z,[])
        query(cs+[a<1 for a in flat],z3.unsat,'sharp better minimax')
        query(cs+[a<=1 for a in flat]+[z3.Or(*[a!=Q(v) for a,v in zip(flat,zf)])],z3.unsat,'sharp minimax nonunique')
        rho=sum(abs(a-v) for a,v in zip(xf,zf))/T
        require(rho==F(4*m,3*(m+2)),'sharp rho')
    return {'m':m,'S':str(S),'T':str(T),'sharp':sharp,'status':'PASS'}

cases=[additive(s) for s in [ [[2],[3],[4]], [[0,2],[0,1],[0,3]], [[-3,4,1],[2,5,3],[2,2,3]], [[1,6,2],[3,3,4],[0,2,0]] ]]
for m in (2,3,4,8):cases.append(additive([[2]+[1]*(m-1),[1]+[0]*(m-1),[0]*m],True))
counts=list(range(30,10001))+[9*2**e+d+12 for e in (10,20,30,60,100,200) for d in (-1,0,1,8)]
for n in counts:
    k=(n-12)//9;L=(k-1).bit_length();R=k-L;a=2**L
    require(L>=1 and R>=0 and 0<=n-9*(L+R)-12<=8,'padding')
    rho=F(2*((R+2)*a-1),(a+2)*(k+2))
    expanded=F(2*L*a,(a+2)*(k+2))+F(4,a+2)+F(2,(a+2)*(k+2))
    require(2-rho==expanded,'deficit identity')
    require(0<=2-rho<=F(2*L+4,k+2)+F(2,(k+2)**2),'padding bound')
result={'status':'PASS','additive':cases,'padding_counts':len(counts),'maximum_n':max(counts)}
(OUT/'additive_padding_results.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
