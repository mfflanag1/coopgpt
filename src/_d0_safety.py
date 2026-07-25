"""PRIORITY-1 safety sweep: for EVERY exact-confirmed (KEY)-violation in the float logs,
compute d*(S) (float) and check d*<=0 (D0 route intact) and d*<=slack (theorem intact).
Any d*>1e-6 is flagged loudly. Uses float leximin (exact blows up on some biased games).
"""
import json, glob, re, sys
from fractions import Fraction as F
from scipy.optimize import linprog
from tugame import Game
from leximin import leximin_core_float
def members(S,n): return [i for i in range(n) if S>>i&1]
def P(*a): print(*a,flush=True)

def dstar_and_certs(n,N,vF,S,phi,tol=1e-6):
    A=[[-1.0 if U>>i&1 else 0.0 for i in range(n)] for U in range(1,N)]
    b=[-vF[U] for U in range(1,N)]
    best=None; certs=[]
    for C in range(1,N):
        if C==S: continue
        Aeq=[[1.0]*n,[1.0 if C>>i&1 else 0.0 for i in range(n)]]; beq=[vF[N],vF[C]]
        c=[-1.0 if S>>i&1 else 0.0 for i in range(n)]
        r=linprog(c,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=[(None,None)]*n,method='highs')
        if not r.success: continue
        m=-r.fun
        if best is None or m<best: best=m
        if abs(m-vF[S])<tol: certs.append(C)
    return best-vF[S], certs

cases=[]
for fn in glob.glob('../results/key_float_n*.log'):
    for line in open(fn):
        mm=re.search(r'VIOLATION \(exact\) \*\*\* (\{.*\})', line)
        if mm: cases.append(json.loads(mm.group(1)))
seen=set(); uniq=[]
for cs in cases:
    k=(tuple(cs['v']),tuple(cs['S']))
    if k in seen: continue
    seen.add(k); uniq.append(cs)
P(f"total KEY-violation log lines={len(cases)} distinct={len(uniq)}")
d0_bad=0; thm_bad=0; nocert=0
for cs in uniq:
    n=cs['n']; N=(1<<n)-1; vF=[float(x) for x in cs['v']]; S=0
    for i in cs['S']: S|=1<<i
    phi=leximin_core_float(n,[F(x) for x in cs['v']],tol=1e-9)
    if phi is None: P("  phi None, skip"); continue
    pS=sum(phi[i] for i in range(n) if S>>i&1); slack=pS-vF[S]
    d,certs=dstar_and_certs(n,N,vF,S,phi)
    flag=""
    if d>1e-6:
        d0_bad+=1; flag+=" *** D0 VIOLATION d*>0 ***"
        if d>slack+1e-6: thm_bad+=1; flag+=" *** THEOREM REFUTED d*>slack ***"
    if not certs: nocert+=1
    if flag or not certs:
        P(f"n={n} S={cs['S']} d*~{d:.4f} slack~{slack:.4f} #certC={len(certs)}{flag}")
P(f"\nSUMMARY over {len(uniq)} KEY-violations: D0-violations(d*>0)={d0_bad}  theorem-refutations(d*>slack)={thm_bad}  no-cert={nocert}")
if d0_bad==0: P("ALL KEY-violations have d*=0 -> (D0) intact, theorem intact.")
