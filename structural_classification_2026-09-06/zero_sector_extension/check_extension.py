"""Exact lifted covers and graph classification, optionally raw-core SMT queries."""
from fractions import Fraction as F
from itertools import product,combinations
from pathlib import Path
import json,sys
import source_family

ROOT=Path(__file__).resolve().parent
def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def build(q,K):
    source=source_family.construct(q);source_family.verify(source)
    m=source['m'];tau=F(source['first_floor']);t=3*tau/K;shift=(K-3)*tau/K
    u=[F(v)-shift for v in source['floor_witness']]+[t]*((K-3)*m)
    y=list(map(F,source['ideal_witness']))+[F(0)]*((K-3)*m)
    return {'q':q,'K':K,'m':m,'T':source['T'],'target':source['target'],'floor':str(t),'old_floor':str(tau),'old_shift':str(shift),'target_ideal':'1','matrices':source['matrices'],'floor_witness':list(map(str,u)),'ideal_witness':list(map(str,y))}

def check(row):
    q,K,m=row['q'],row['K'],row['m'];T=F(row['T']);t=F(row['floor']);target=row['target']
    require(K>=4 and m==3*q+1 and t==F(1,K*(q+1)),'Parameters')
    A=[[[F(v)for v in line]for line in B]for B in row['matrices']]
    w=lambda team:A[0][team[0]][team[1]]+A[1][team[0]][team[2]]+A[2][team[1]][team[2]]
    require(sum(w((j,)*K)for j in range(m))==T==6*q+1,'Integral matching total')
    count=0
    for name in ('floor_witness','ideal_witness'):
        p=list(map(F,row[name]));require(len(p)==K*m and min(p)>=0 and sum(p)==T,'Payoff totals')
        for team in product(range(m),repeat=K):
            require(sum(p[s*m+team[s]]for s in range(K))>=w(team),'Lifted full-team cover');count+=1
        if name=='floor_witness':require(min(p)==p[target]==t>0,'Floor witness')
        else:require(p[target]==1,'Ideal attainment')
    return {'q':q,'K':K,'players':K*m,'covers':count,'floor':str(t),'ideal':'1'}

def smt(row):
    import z3
    m,K=row['m'],row['K'];n=m*K;target=row['target'];t=F(row['floor']);T=F(row['T'])
    A=[[[F(v)for v in line]for line in B]for B in row['matrices']]
    zq=lambda v:z3.Q(v.numerator,v.denominator)
    w=lambda team:A[0][team[0]][team[1]]+A[1][team[0]][team[2]]+A[2][team[1]][team[2]]
    p=[z3.Real(f'p{i}')for i in range(n)]
    raw=[v>=0 for v in p]+[z3.Sum(p)==zq(T)]
    raw += [z3.Sum([p[s*m+team[s]]for s in range(K)])>=zq(w(team))for team in product(range(m),repeat=K)]
    def unsat(extra,base=raw):
        s=z3.Solver();s.set(timeout=30000);s.add(base+extra);require(s.check()==z3.unsat,'Required exact UNSAT query failed')
    uniform=[p[s*m+j]==p[s*m]for s in range(3,K)for j in range(1,m)]
    R=z3.Sum([p[s*m]for s in range(3,K)])
    affine=[v>=0 for v in p]+[z3.Sum(p)==zq(T)]+uniform
    affine += [p[i]+p[m+j]+p[2*m+k]+R>=zq(w((i,j,k)))for i,j,k in product(range(m),repeat=3)]
    unsat([z3.Not(z3.And(affine))]);unsat([z3.Not(z3.And(raw))],affine)
    unsat([v>zq(t)for v in p]);unsat([v>=zq(t)for v in p]+[p[target]>zq(t)])
    unsat([p[target]>1])
    return {'q':row['q'],'K':K,'exact_unsat_queries':5}

def graphs():
    possible=list(combinations(range(4),2));counts={'tree':0,'triangle':0,'C4':0};rows=[]
    for mask in range(1<<len(possible)):
        E={possible[j]for j in range(len(possible))if mask>>j&1};seen={0}
        while True:
            old=set(seen)
            for a,b in E:
                if a in seen or b in seen:seen.update((a,b))
            if seen==old:break
        if len(seen)<4:continue
        tri=any(all(tuple(sorted(e))in E for e in combinations(triple,2))for triple in combinations(range(4),3))
        if len(E)==3:kind='tree'
        elif tri:kind='triangle'
        else:
            require(len(E)==4 and all(sum(v in e for e in E)==2 for v in range(4)),'Unclassified four-vertex graph');kind='C4'
        counts[kind]+=1;rows.append({'edges':sorted(E),'class':kind})
    require(counts=={'tree':16,'triangle':19,'C4':3},'Graph coverage')
    return {'all_edge_masks':64,'connected_labeled_graphs':38,'counts':counts,'graphs':rows}

def main():
    output=ROOT/'VERIFICATION.json';output.write_text('{"status":"RUNNING"}\n')
    params=[(1,4),(2,4),(3,4),(4,4),(1,5),(2,5),(1,6)]
    cases=[build(q,K)for q,K in params];checks=[check(row)for row in cases]
    solver=[smt(build(q,K))for q,K in [(1,4),(2,4),(1,5)]]if '--smt'in sys.argv else []
    result={'status':'PASS','scope':'Finite exact corroboration of the symbolic sector-extension theorem','lifted_cases':checks,'total_full_team_covers':sum(c['covers']for c in checks),'solver_cases':solver,'four_vertex_graph_classification':graphs()}
    (ROOT/'LIFTED_WITNESSES.json').write_text(json.dumps(cases,indent=2)+'\n');output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'PASS','lifted_cases':len(checks),'full_team_covers':result['total_full_team_covers'],'smt_unsat_queries':sum(c['exact_unsat_queries']for c in solver),'four_vertex_graphs':38}))
if __name__=='__main__':main()
