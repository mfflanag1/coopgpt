from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json,sys
import source_family as sf
ROOT=Path(__file__).resolve().parent

def require(ok,msg):
    if not ok: raise RuntimeError(msg)

def instance(q):
    r=sf.construct(q);m=r['m'];A,B,C=[[[F(v) for v in row] for row in mat] for mat in r['matrices']]
    return r,m,A,B,C

def weak(q,m):
    O,L,R=sf.output,sf.left,sf.right
    return set([j for j in range(m) if j not in {O(s) for s in range(1,q+1)}]+[m+O(s) for s in range(1,q+1)]+[2*m+O(s) for s in range(1,q+1)]+[2*m+L(s) for s in range(q)]+[2*m+R(s) for s in range(1,q)]+list(range(3*m,4*m)))

def gadgets(q,m):
    O,L,R=sf.output,sf.left,sf.right
    diag=[(j,j,j,j) for j in range(m)]
    def U(s):return [t for t in diag if t[0] not in (L(s-1),O(s),L(s),R(s))]+[(O(s),R(s),R(s),L(s)),(L(s-1),L(s-1),O(s),O(s)),(L(s),L(s),L(s),R(s))]
    def V(s):return [t for t in diag if t[0] not in (O(s),L(s),R(s))]+[(O(s),R(s),R(s),L(s)),(L(s),L(s),L(s),R(s))]
    result=[]
    for s in range(1,q+1):
        result.extend([(f'U{s}',U(s)),(f'V{s}',V(s))])
        g=V(s);g[-1]=(*g[-1][:3],O(s));result.append((f'V{s}_omit_dR',g))
        g=V(s);g[-2]=(*g[-2][:3],O(s));result.append((f'V{s}_omit_dL',g))
    for s in range(1,q):
        g=U(s+1);j=g.index((R(s),)*4);g[j]=(R(s),R(s),L(s),L(s));result.append((f'U{s+1}_omit_cR{s}',g))
    for j in range(m):
        if j in {O(s) for s in range(1,q+1)}:continue
        g=V(1)
        if j!=R(1):
            h=next(h for h,t in enumerate(g) if t[0]==j);g[h]=(R(1),*g[h][1:])
        result.append((f'null_a{j}',g))
    return result

def structural_checks():
    rows=[];total=0
    for q in range(1,13):
        r,m,A,B,C=instance(q);W=weak(q,m);covered=set();certs=[]
        if q<=4:sf.verify(r)
        require(sum(max(row) for mat in (A,B,C) for row in mat)==6*q+1,'row maximum worth')
        for name,g in gadgets(q,m):
            ids=[s*m+t[s] for t in g for s in range(4)]
            require(len(g)==m-1 and len(ids)==len(set(ids)),'partial matching disjointness')
            missing=set(range(4*m))-set(ids)
            base=sum(A[a][b]+C[b][c]+B[a][d] for a,b,c,d in g)
            coeff=sum(c==d for a,b,c,d in g)
            require(base==6*q+1 and coeff==m-3,'symbolic T-3M budget')
            covered.update(missing);certs.append({'name':name,'teams':g,'missing':sorted(missing),'base':str(base),'M_coefficient':coeff})
        require(W<=covered,'weak players lack ideal certificate')
        require(covered<=W,'unexpected strong ideal certificate')
        case_counts={}
        if q<=4:
            L,R=sf.left(q),sf.right(q)
            for a,b,c,d in product(range(m),repeat=4):
                if b not in (L,R) and c not in (L,R):case='unchanged'
                elif b==c and b in (L,R):case='fixed_sum'
                elif b==R and c==L:
                    case='positive_cross';require(C[b][c]==1,'cross value')
                else:
                    case='zero_C';require(C[b][c]==0,'unhandled positive C interaction')
                require(A[a][b]+B[a][d]<=4,'strong a row bound')
                if a not in {sf.output(s) for s in range(1,q+1)}:require(A[a][b]+B[a][d]==0,'null a row bound')
                case_counts[case]=case_counts.get(case,0)+1
            total+=m**4
        rows.append({'q':q,'m':m,'weak_players':sorted(W),'partial_matchings':certs,'team_case_counts':case_counts})
    require(F(1,2)-12*F(1,42)==9*F(1,42)==F(3,14),'replacement threshold')
    require(F(3,14)/(4+F(1,42))==F(9,169),'small-M strong ratio')
    require(F(1,42)/(4*(4+F(1,42)))==F(1,676),'large-M ratio')
    return rows,total

def smt_checks():
    import z3
    checks=[]
    for q in (1,2,3):
        _,m,A,B,C=instance(q);W=weak(q,m);p=[z3.Real(f'p{i}') for i in range(4*m)];M=z3.Real('M')
        teams=list(product(range(m),repeat=4));T=6*q+1+m*M
        raw=[M>0,*[v>=0 for v in p],z3.Sum(p)==T]
        raw += [z3.Sum([p[a],p[m+b],p[2*m+c],p[3*m+d]])>=A[a][b]+C[b][c]+B[a][d]+M*int(c==d) for a,b,c,d in teams]
        def unsat(label,extra):
            s=z3.Solver();s.set(timeout=120000);s.add(raw+extra);ans=s.check()
            require(ans==z3.unsat,f'{label}: expected unsat, received {ans}')
            checks.append({'q':q,'query':label,'result':'unsat','team_constraints':len(teams)})
            print(json.dumps(checks[-1]),flush=True)
        unsat('some weak ideal exceeds 3M for any positive M',[z3.Or([p[i]>3*M for i in W])])
        L,R=sf.left(q),sf.right(q);y=p.copy();y[2*m+L]=z3.Q(1,2)+7*M;y[2*m+R]=z3.Q(1,2)-7*M
        y[m+L]=p[m+L]+p[2*m+L]-y[2*m+L];y[m+R]=p[m+R]+p[2*m+R]-y[2*m+R]
        bad=[v<0 for v in y]+[z3.Sum(y)!=T]+[y[i]<z3.Q(3,14) for i in (m+L,m+R,2*m+L,2*m+R)]
        bad += [z3.Sum([y[a],y[m+b],y[2*m+c],y[3*m+d]])<A[a][b]+C[b][c]+B[a][d]+M*int(c==d) for a,b,c,d in teams]
        derived=[p[i]<=3*M for i in W]+[z3.Sum([p[s*m+j] for s in range(4)])==A[j][j]+B[j][j]+C[j][j]+M for j in range(m)]
        unsat('terminal replacement fails somewhere in 0<M<=1/42',[M<=z3.Q(1,42),*derived,z3.Or(bad)])
        checks[-1]['derived_constraints']='Weak bounds proved by preceding raw-core UNSAT query; tight diagonal equalities follow from covers and sum(diagonal values)=T'
    return checks

def main():
    target=ROOT/'VERIFICATION.json';target.write_text('{"status":"RUNNING"}\n')
    rows,total=structural_checks();smt=smt_checks() if '--smt' in sys.argv else []
    out={'status':'PASS','scope':'Uniform 1/676 for this exact diagonal-subdivision family, not general C4','depths':rows,'partial_matchings':sum(len(r['partial_matchings']) for r in rows),'classified_teams':total,'smt_queries':smt}
    target.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ('depths','smt_queries')}),flush=True)
if __name__=='__main__':
    try:main()
    except Exception as error:
        (ROOT/'VERIFICATION.json').write_text(json.dumps({'status':'FAILED','error':str(error)},indent=2)+'\n')
        raise
