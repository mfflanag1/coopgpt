"""Fresh adversarial certificates; no imported selector or construction code."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
import z3

ROOT=Path(__file__).resolve().parent

def require(ok,msg):
    if not ok: raise RuntimeError(msg)

def Q(x):
    x=F(x); return z3.Q(x.numerator,x.denominator)

def verdict(cons,expected,label):
    s=z3.Solver();s.set(timeout=60000);s.add(*cons)
    actual=s.check();require(actual==expected,f'{label}: {actual}')
    return str(actual)

def sorted_expressions(items):
    items=list(items)
    for end in range(1,len(items)):
        for j in range(end,0,-1):
            a,b=items[j-1],items[j]
            items[j-1],items[j]=z3.If(a<=b,a,b),z3.If(a<=b,b,a)
    return items

def lex_better(expressions,reference,upward):
    prefix=[]; alternatives=[]
    for expression,value in zip(expressions,reference):
        better=expression>Q(value) if upward else expression<Q(value)
        alternatives.append(z3.And(*prefix,better))
        prefix.append(expression==Q(value))
    return z3.Or(*alternatives)

def independent_small_core(matrix):
    edges=[((0,2),matrix[0][0]),((0,3),matrix[0][1]),((1,2),matrix[1][0]),((1,3),matrix[1][1])]
    T=max(matrix[0][0]+matrix[1][1],matrix[0][1]+matrix[1][0])
    p=[z3.FreshReal('small') for _ in range(4)]
    cons=[sum(p)==Q(T)]
    for mask in range(1,16):
        worth=max([F(0)]+[F(w) for e,w in edges if all(mask>>i&1 for i in e)])
        if mask==15: worth=F(T)
        cons.append(sum(p[i] for i in range(4) if mask>>i&1)>=Q(worth))
    return p,cons,T

def sorted_recheck():
    data=json.loads((ROOT/'assignment_separation'/'two_by_two_calibration.json').read_text())
    records=data['cases']
    expected={tuple(vals) for vals in product(range(4),repeat=4) if any(vals)}
    actual={tuple(v for row in r['matrix'] for v in row) for r in records}
    require(len(records)==255 and actual==expected,'bounded coverage not exact')
    for number,record in enumerate(records,1):
        p,cons,T=independent_small_core(record['matrix'])
        expressions=sorted_expressions(p)
        for name,upward in [('Lmin',True),('Lmax',False)]:
            point=list(map(F,record[name]))
            require(sum(point)==T,'point total mismatch')
            substitutions=[(q,Q(v)) for q,v in zip(p,point)]
            require(all(z3.is_true(z3.simplify(z3.substitute(c,*substitutions))) for c in cons),'stored candidate infeasible')
            order=expressions if upward else expressions[::-1]
            target=sorted(point,reverse=not upward)
            verdict(cons+[lex_better(order,target,upward)],z3.unsat,f'{name} sorted-rank verification')
        if number%64==0: print('Sorted-rank checks',number,flush=True)
    p,cons,_=independent_small_core([[1,0],[0,0]])
    fake=[F(1),F(0),F(0),F(0)]
    verdict(cons+[lex_better(sorted_expressions(p),sorted(fake),True)],z3.sat,'reject first-stage-only fake')
    return dict(cases=255,method='Independent explicit4-player coalition values and insertion-sort SMT lex-improvement queries, without progressive-floor optimization',queries=510,negative_control='Strict sorted improvement over a first-stage maximin-only point: SAT')


def raw_game(L,R):
    require(isinstance(L,int) and L>=1 and isinstance(R,int) and R>=0,'invalid family parameters')
    names=[]; colors=[]; pair={}; triples={}; matching=[]
    def vertex(name,color):
        require(name not in names,'duplicate player')
        names.append(name);colors.append(color);return len(names)-1
    globalzero=[vertex(f'G{c}',c) for c in range(3)]
    def edge(ids,value,matched=False):
        require(len(set(ids))==3 and {colors[i] for i in ids}=={0,1,2},'invalid team coloring')
        key=tuple(sorted(ids)); require(key not in triples,'duplicate team in specification')
        triples[key]=value
        if matched: matching.append(key)
    for l in range(L+1+R):
        depth=min(l,L)
        for i in range(3):
            uc=(i+depth%2)%3;vc=(i+1-depth%2)%3;dc=(i+2)%3
            u=vertex(f'U{l}_{i}',uc);v=vertex(f'V{l}_{i}',vc);d=vertex(f'D{l}_{i}',dc)
            pair[l,i]=(u,v,d)
            edge((u,v,d),2 if l==0 else 1,True)
            edge((u,v,globalzero[dc]),2 if l==0 else 1)
    for i in range(3): edge((pair[0,i][0],*[globalzero[c] for c in range(3) if c!=i]),1)
    for l in range(1,L+1):
        for i in range(3):
            children=[j for j in range(3) if j!=i]
            edge((pair[l,i][0],*[pair[l-1,j][1] for j in children]),2)
            edge((pair[l,i][1],*[pair[l-1,j][0] for j in children]),3 if l==1 else 1)
    for l in range(L+1,L+1+R):
        for i in range(3):
            edge((pair[l,i][0],pair[L,i][1],globalzero[(i+2)%3]),1)
            edge((pair[l,i][1],pair[L,i][0],globalzero[(i+2)%3]),1)
    T=3*(L+R+2)
    p=[z3.FreshReal('triple') for _ in names]
    cons=[q>=0 for q in p]+[sum(p)==T]+[sum(p[i] for i in e)>=w for e,w in triples.items()]
    require(len(names)==9*(L+R)+12,'player count')
    require(len(triples)==12*(L+R)+9,'positive triple count')
    require([colors.count(c) for c in range(3)]==[3*(L+R)+4]*3,'sector count')
    matched=[i for e in matching for i in e]
    require(len(set(matched))==len(matched) and sum(triples[e] for e in matching)==T,'integral matching certificate')
    return names,colors,pair,triples,matching,globalzero,p,cons,T


def family_check(L,R,integer_optimum=False):
    names,colors,pair,triples,matching,globals_,p,cons,T=raw_game(L,R)
    t=F(1,2**L+2);eta=2*t
    x=[F(0)]*len(p);z=[F(0)]*len(p)
    for (l,i),(u,v,d) in pair.items():
        q=2**min(l,L)*t
        x[u]=q+int(l==0);x[v]=1-q
        z[u]=F(int(l==0));z[v]=F(1)
    for name,point in [('leximin',x),('minimax',z)]:
        subs=[(a,Q(b)) for a,b in zip(p,point)]
        require(all(z3.is_true(z3.simplify(z3.substitute(c,*subs))) for c in cons),name+' violates raw core')
    if integer_optimum:
        e=list(triples); chosen=[z3.FreshInt('choose') for _ in e]
        ip=[z3.Or(q==0,q==1) for q in chosen]
        ip += [sum(chosen[j] for j,edge in enumerate(e) if i in edge)<=1 for i in range(len(p))]
        ip += [sum(chosen[j]*triples[edge] for j,edge in enumerate(e))>T]
        verdict(ip,z3.unsat,'independent integer matching optimum')
    dummy=set(globals_)|{a[2] for a in pair.values()};active=[i for i in range(len(p)) if i not in dummy]
    verdict(cons+[z3.Or(*[p[i]!=0 for i in dummy])],z3.unsat,'dummy is not fixedzero')
    require(all(x[i]>0 for i in active),'some active player fixedzero')
    verdict(cons+[p[i]>Q(eta) for i in active],z3.unsat,'better positive floor')
    verdict(cons+[p[i]>=Q(eta) for i in active]+[z3.Or(*[q!=Q(a) for q,a in zip(p,x)])],z3.unsat,'different optimal positivefloor point')
    verdict(cons+[q<1 for q in p],z3.unsat,'better ceiling')
    verdict(cons+[q<=1 for q in p]+[z3.Or(*[q!=Q(a) for q,a in zip(p,z)])],z3.unsat,'different minimax point')
    topv=pair[L,0][1]
    verdict(cons+[p[topv]>1],z3.unsat,'top coordinate ideal bound')
    require(z[topv]==1,'coordinate ideal lower witness')
    # Entireness in both directions, with arbitrary asymmetric roots.
    roots=[p[pair[0,i][0]]-1 for i in range(3)]
    q=roots; required=[p[i]==0 for i in dummy]+[a>=0 for a in roots]
    for l in range(L+1):
        for i in range(3):
            u,v,d=pair[l,i];required += [p[u]==q[i]+int(l==0),p[v]==1-q[i]]
        if l<L:q=[sum(q[j] for j in range(3) if j!=i) for i in range(3)]
    for l in range(L+1,L+1+R):
        for i in range(3):
            u,v,d=pair[l,i];required += [p[u]==q[i],p[v]==1-q[i]]
    verdict(cons+[z3.Not(z3.And(*required))],z3.unsat,'raw core outside claimed parametrization')
    u0=[z3.FreshReal('root') for _ in range(3)];q=u0
    parameter=[F(0)]*len(p);domain=[]
    for l in range(L+1):
        for i in range(3):
            u,v,d=pair[l,i];parameter[u]=q[i]+int(l==0);parameter[v]=1-q[i]
            domain += [q[i]>=0,q[i]<=1]
        if l<L:q=[sum(q[j] for j in range(3) if j!=i) for i in range(3)]
    for l in range(L+1,L+1+R):
        for i in range(3):
            u,v,d=pair[l,i];parameter[u]=q[i];parameter[v]=1-q[i]
    sub=[(a,b if z3.is_expr(b) else Q(b)) for a,b in zip(p,parameter)]
    reconstructed=[z3.substitute(c,*sub) for c in cons]
    verdict(domain+[z3.Not(z3.And(*reconstructed))],z3.unsat,'claimed parametrization not within raw core')
    rho=sum(abs(a-b) for a,b in zip(x,z))/T
    require(rho==F(2*((R+2)*2**L-1),(2**L+2)*(L+R+2)),'distance formula')
    # Uniform raw witness proves sector root maximum is >1 but is NOT a maximizer.
    if L==2:
        uniform_increment=F(1,2**(L+1))
        verdict(cons+[p[pair[0,0][0]]>Q(1+uniform_increment)],z3.sat,'uniform interior root witness is not its core maximum')
    print('Raw family SAT certificates',L,R,len(p),str(rho),flush=True)
    return dict(L=L,R=R,n=len(p),T=T,positive_triples=len(triples),rho=str(rho),whole_core_both_inclusions=True,first_nonfixed_maximin_unique=True,minimax_unique=True,integer_matching_exceedance='UNSAT' if integer_optimum else 'equal integral matching and covering allocation certificates')


def padding_checks():
    counts=list(range(30,1001))+[9*(2**j)+offset+12 for j in (10,20,30,60) for offset in (-1,0,1,8)]
    for n in counts:
        k=(n-12)//9;L=(k-1).bit_length();R=k-L
        require(L>=1 and R>=0,'padding invalid parameters')
        require(0<=n-(9*(L+R)+12)<=8,'padding count')
        rho=F(2*((R+2)*2**L-1),(2**L+2)*(L+R+2))
        bound=F(2*L+4,k+2)+F(2,(k+2)**2)
        require(0<=2-rho<=bound,'finite player inequality')
    return dict(counts_checked=len(counts),maximum_n=max(counts))


if __name__=='__main__':
    result={}
    result['families']=[family_check(L,R,integer_optimum=L<=2) for L,R in [(1,0),(1,3),(2,1),(3,2),(4,0),(4,16)]]
    result['padding']=padding_checks()
    result['sorted_selector_recheck']=sorted_recheck()
    (ROOT/'hostile_check_results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS fresh hostile certificates',flush=True)
