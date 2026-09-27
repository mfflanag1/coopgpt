"""One serial pair-additive recurrence, exact first four depth checks.

All arithmetic is standard-library Fraction arithmetic. No LP solver or random
search is used. The general proof is in RECURRENCE.md.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import hashlib,json,runpy

ROOT=Path(__file__).resolve().parent
CAMPAIGN=Path('/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/pair_additive_campaign_2026-09-05')
if (ROOT.parents[1]/'cycle4'/'experiment').is_dir():CAMPAIGN=ROOT.parents[1]
SOURCE=CAMPAIGN/'cycle4'/'experiment'

def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def save(path,obj):path.write_text(json.dumps(obj,indent=2,default=str)+'\n')
def output(s):return 3*s-2
def left(s):return 0 if s==0 else 3*s-1
def right(s):return 3*s

def construct(q):
    require(isinstance(q,int) and q>=1,'positive integer depth')
    m=3*q+1;n=3*m;tau=F(1,3*q+3)
    A=[['0']*m for _ in range(m)];B=[['0']*m for _ in range(m)];C=[['0']*m for _ in range(m)]
    u=[[F(0)]*m for _ in range(3)];y=[[F(0)]*m for _ in range(3)]
    for s in range(q+1):
        ell=left(s);C[ell][ell]='1'
        u[0][ell]=tau;u[1][ell]=1-(3*s+2)*tau;u[2][ell]=(3*s+1)*tau
        y[2][ell]=1
    critical=[]
    for s in range(1,q+1):
        o,ell,r,prev=output(s),left(s),right(s),left(s-1)
        A[o][o]=B[o][o]='2';C[r][r]='1'
        A[o][r]=B[o][ell]='2';C[r][ell]='1';C[prev][o]='1'
        u[0][o]=4-(3*s-1)*tau;u[1][o]=tau;u[2][o]=(3*s-2)*tau
        u[0][r]=tau;u[1][r]=1-2*tau;u[2][r]=tau
        y[0][o]=3;y[2][o]=1;y[1][r]=1
        critical.extend([[o,r,ell],[prev,prev,o]])
    return dict(depth=q,m=m,matrices=[A,B,C],matching=[[i,i,i] for i in range(m)],critical_partial_matching=critical,T=str(6*q+1),first_floor=str(tau),target=2*m+left(0),target_ideal='1',ratio=str(tau),floor_witness=[str(v) for sector in u for v in sector],ideal_witness=[str(v) for sector in y for v in sector])

def verify(r):
    q=r['depth'];m=r['m'];n=3*m;require(m==3*q+1,'sector size')
    M=[[[F(v) for v in row] for row in mat] for mat in r['matrices']]
    require(len(M)==3 and all(len(mat)==m and all(len(row)==m and all(v.denominator==1 and 0<=v<=2 for v in row) for row in mat) for mat in M),'nonnegative integer pair matrices')
    def ids(t):i,j,k=t;return (i,m+j,2*m+k)
    def w(t):i,j,k=t;return M[0][i][j]+M[1][i][k]+M[2][j][k]
    matching=r['matching'];require(sorted(i for t in matching for i in ids(t))==list(range(n)),'perfect matching partition')
    T=sum(map(w,matching));require(T==6*q+1==F(r['T']),'matching total')
    u=list(map(F,r['floor_witness']));y=list(map(F,r['ideal_witness']));tau=F(1,3*q+3);checks=0
    for p in (u,y):
        require(len(p)==n and all(v>=0 for v in p) and sum(p)==T,'point total/nonnegativity')
        for t in product(range(m),repeat=3):
            require(sum(p[i] for i in ids(t))>=w(t),'mixed triple cover');checks+=1
        require(all(sum(p[i] for i in ids(t))==w(t) for t in matching),'matching efficiency')
    critical=r['critical_partial_matching'];covered=[i for t in critical for i in ids(t)]
    require(len(critical)==2*q and len(set(covered))==len(covered),'critical triples not a partial matching')
    require([w(t) for t in critical]==[5,1]*q,'critical matching weights')
    require(sum(map(w,critical))==6*q,'critical matching value')
    unmatched=sorted(set(range(n))-set(covered));require(len(unmatched)==3*q+3,'unmatched budget cardinality')
    target=r['target'];require(target==2*m and target in unmatched,'target not budgeted')
    require(all(v>=tau for v in u) and all(u[i]==tau for i in unmatched),'firstfloor attainment/pinning')
    require(y[target]==1 and all(y[i]==0 for i in unmatched if i!=target),'ideal attainment')
    require(w(matching[0])==1 and target in ids(matching[0]),'matching ideal upper bound')
    require(tau==F(r['first_floor'])==F(r['ratio']) and F(r['target_ideal'])==1,'reported quantities')
    return dict(status='PASS',depth=q,players=n,sector_size=m,nonzero_pair_entries=sum(v!=0 for mat in M for row in mat for v in row),T=str(T),all_triple_checks=checks,partial_matching_teams=2*q,partial_matching_value=str(6*q),unmatched_players=unmatched,budget_rhs='1',first_positive_floor=str(tau),full_leximin_target=str(tau),target_ideal='1',ratio=str(tau))

def calibrate():
    dest=ROOT/'calibration';dest.mkdir(exist_ok=True)
    source=SOURCE/'reduced_candidate.json';(dest/source.name).write_bytes(source.read_bytes())
    dependency=SOURCE/'verify_reduced.py';namespace=runpy.run_path(str(dependency));namespace['main'].__globals__['ROOT']=dest;namespace['main']()
    result=dict(status='PASS',source=str(source),ratio='1/9',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),verifier_sha256=hashlib.sha256(dependency.read_bytes()).hexdigest())
    save(ROOT/'calibration_summary.json',result)

def main():
    save(ROOT/'manifest.json',dict(scope='One corrected serial triangle recurrence; exact checks at first four positive integer depths only. General family is established separately by a symbolic whole-cover proof.',depths=[1,2,3,4],max_depth_settings=4,random_search=False,solver_search=False,stopping_rule='Stop after the four declared exact checks; no isolated-constant or alternative-support search.',definition='m3q+1. Teams L0 and(O_s,L_s,R_s). Output diagonal AB=AC=2; each leaf diagonal BC=1. Cross A(O,R)=2,B(O,L)=2,C(R,L)=1,C(L_previous,O)=1.',target='C_L0, first positive floor1/(3q+3), true ideal1, ratio tends0.'))
    calibrate();results=[]
    for q in (1,2,3,4):
        r=construct(q);save(ROOT/('depth_'+str(q)+'.json'),r);result=verify(r);save(ROOT/('depth_'+str(q)+'_verification.json'),result);results.append(result)
        print('PASS DEPTH',q,'PLAYERS',result['players'],'RATIO',result['ratio'],'TRIPLE CHECKS',result['all_triple_checks'],flush=True)
    save(ROOT/'summary.json',dict(status='PASS',calibration='21-player exact1/9',depth_settings_checked=4,all_triple_checks=sum(r['all_triple_checks'] for r in results),ratios=[r['ratio'] for r in results],general_claim='Symbolic proof, not extrapolation from these four depths: RECURRENCE.md.'))

if __name__=='__main__':main()
