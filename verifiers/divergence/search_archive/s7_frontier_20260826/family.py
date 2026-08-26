from fractions import Fraction as F
from exactsel import analyze
import sys, time, json
def H(m):
    n=m+6; a=[0]*m
    x=[1]*m+[3*m,5*m,1,1,1,1]
    B=[0]*m+[0,0,4*m+1,2*m+1,2*m+1,m+1]
    C=[0]*m+[3*m+2,6*m+2,0,0,0,0]
    D=[0]*m+[0,F(7*m+1,2),F(m+1,2),2*m+1,2*m+1,m+1]
    # integer scaling
    return [[2*a for a in x],[2*a for a in B],[2*a for a in C],[int(2*a) for a in D]]
def predicted(m):
    n=m+6; T=9*m+4
    x=[F(1)]*m+[F(3*m),F(5*m),F(1),F(1),F(1),F(1)]
    z=[F(1,5*m)]*m+[F(3,5)]+[F(10*m+3,5)]*4+[F(5*m+4,5)]
    return x,z,F(14*(5*m-1),5*(9*m+4))
for m in [int(a) for a in sys.argv[1:]]:
    t=time.time(); G=H(m); r=analyze(G,verbose=False); x,z,rho=predicted(m)
    ok = ([a/2 for a in r['x']]==x and [a/2 for a in r['z']]==z and r['rho']==rho)
    print(f"m={m} n={m+6} T={9*m+4}: rho={r['rho']} predicted={rho} match={ok} time={time.time()-t:.0f}s", flush=True)
    if not ok: print('  got x',[str(a/2) for a in r['x']],'z',[str(a/2) for a in r['z']])
