from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json,sys,copy
from family import construct
ROOT=Path(__file__).resolve().parent

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def check(r):
    q=r['q'];m=r['m'];n=4*m
    require(isinstance(q,int)and q>=1 and m==3*q+1 and r['k']==4,'family dimensions')
    edges=[tuple(e)for e in r['edges']];require(edges==[(0,1),(1,2),(2,3),(0,3)],'C4 support')
    A=r['matrices'];require(len(A)==4 and all(len(B)==m and all(len(row)==m and all(isinstance(v,int)and v in (0,1,2)for v in row)for row in B)for B in A),'pair alphabet')
    def ids(t):return [a*m+t[a]for a in range(4)]
    def w(t):return sum(A[h][t[a]][t[b]]for h,(a,b)in enumerate(edges))
    matching=r['matching'];require(len(matching)==m and sorted(i for t in matching for i in ids(t))==list(range(n)),'perfect matching')
    T=sum(map(w,matching));require(T==r['T']==10*q+1,'worth formula')
    p=list(map(F,r['x_floor']));y=list(map(F,r['y_ideal']));t=F(1,4*(q+1));target=r['target']
    require(len(p)==len(y)==n and sum(p)==sum(y)==T and min(p)>=t and min(y)>=0,'cover totals and signs')
    require(target==2*m and F(r['floor'])==F(r['ratio'])==t,'target/floor formula')
    covers=0
    for team in product(range(m),repeat=4):
        v=w(team)
        for point in (p,y):require(sum(point[i]for i in ids(team))>=v,'uncovered full team');covers+=1
    partial=r['partial_matching'];used=[i for team in partial for i in ids(team)]
    require(len(partial)==2*q and len(used)==len(set(used)),'partial matching disjointness')
    require(sum(map(w,partial))==T-1,'unit residual budget')
    missing=sorted(set(range(n))-set(used));require(len(missing)==4*(q+1)and target in missing,'unmatched cardinality/target')
    require(all(p[i]==t for i in missing),'whole first-face attainment')
    target_team=next(team for team in matching if target in ids(team));require(w(target_team)==1 and y[target]==F(r['target_ideal'])==1,'ideal sandwich')
    return {'q':q,'m':m,'T':T,'full_team_covers':covers,'partial_teams':len(partial),'unmatched':missing,'first_face_target':str(t),'entire_core_ideal':'1','ratio':str(t),'status':'PASS'}

def smt(records):
    import z3
    rows=[]
    for r in records[:3]:
        m=r['m'];p=[z3.Real(f'p{i}')for i in range(4*m)];A=r['matrices'];t=F(r['floor']);target=r['target'];z=z3.Q(t.numerator,t.denominator)
        cons=[v>=0 for v in p]+[z3.Sum(p)==r['T']]
        for team in product(range(m),repeat=4):
            val=sum(A[h][team[a]][team[b]]for h,(a,b)in enumerate(r['edges']));cons.append(z3.Sum([p[a*m+team[a]]for a in range(4)])>=val)
        for label,extra in [('strictly larger common floor',[v>z for v in p]),('target increases on first face',[v>=z for v in p]+[p[target]>z]),('target ideal exceeds one',[p[target]>1])]:
            s=z3.Solver();s.set(timeout=30000);s.add(cons+extra);answer=s.check();require(answer==z3.unsat,f'{label}: {answer}')
            rows.append({'q':r['q'],'query':label,'answer':'unsat'});print(json.dumps(rows[-1]),flush=True)
    return rows

def main():
    path=ROOT/'VERIFICATION.json';path.write_text('{"status":"RUNNING"}\n')
    records=[construct(q)for q in range(1,7)];rows=[check(r)for r in records]
    bad=[]
    for mode in ('cover','partial','bonus','ideal'):
        r=copy.deepcopy(records[0])
        if mode=='cover':r['x_floor'][0]='-1'
        if mode=='partial':r['partial_matching'][1]=r['partial_matching'][0]
        if mode=='bonus':r['matrices'][2][0][0]=2
        if mode=='ideal':r['target_ideal']='2'
        try:check(r)
        except RuntimeError:bad.append(mode)
        else:raise RuntimeError('Corruption accepted')
    extra=smt(records)if '--smt'in sys.argv else []
    (ROOT/'CERTIFICATES.json').write_text(json.dumps(records,indent=2)+'\n')
    result={'status':'PASS','scope':'All-q proof is conventional; exact finite calibration q1..6; raw-core solver q1..3','cases':rows,'full_team_covers':sum(r['full_team_covers']for r in rows),'negative_checks':bad,'raw_core_queries':extra}
    path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','full_team_covers':result['full_team_covers'],'raw_core_queries':len(extra)}))
if __name__=='__main__':
    try:main()
    except Exception as e:
        (ROOT/'VERIFICATION.json').write_text(json.dumps({'status':'FAILED','error':str(e)})+'\n');raise
