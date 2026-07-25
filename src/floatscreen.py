"""Fast FLOAT screening layer (scipy HiGHS) for the exact-family hunt.
Screening only -- every positive hit is re-confirmed with the exact tools
(exactlp / is_exact_game / Farkas). Cross-validated shape: same LPs as the exact
stack but in float, ~100x faster, used to prune the search space.
"""
import numpy as np
from scipy.optimize import linprog

def _core_min_xS_float(n, v, S):
    """min x(S) over core(v) (float). Returns None if core empty."""
    N=(1<<n)-1
    A=[]; b=[]
    for T in range(1,N):
        A.append([-1.0 if T>>i&1 else 0.0 for i in range(n)]); b.append(-v[T])
    Aeq=[[1.0]*n]; beq=[v[N]]
    c=[1.0 if S>>i&1 else 0.0 for i in range(n)]
    r=linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=[(None,None)]*n, method="highs")
    if not r.success: return None
    return r.fun

def is_balanced_float(n, v, tol=1e-7):
    N=(1<<n)-1
    A=[]; b=[]
    for S in range(1,N):
        A.append([-1.0 if S>>i&1 else 0.0 for i in range(n)]); b.append(-v[S])
    c=[1.0]*n
    r=linprog(c, A_ub=A, b_ub=b, bounds=[(None,None)]*n, method="highs")
    if not r.success: return False
    return r.fun <= v[N]+tol

def is_exact_float(n, v, tol=1e-6):
    N=(1<<n)-1
    for S in range(1,N):
        m=_core_min_xS_float(n, v, S)
        if m is None or abs(m - v[S])>tol: return False
    return True

def family_feasible_float(n, games_v, edges, tol=1e-6):
    """Float feasibility of the core+monotonicity family LP.
    games_v: list of v-lists. edges: (k,l,S). Returns True/False."""
    m=len(games_v); nv=n*m
    A=[]; b=[]
    Aeq=[]; beq=[]
    for k in range(m):
        row=[0.0]*nv
        for i in range(n): row[k*n+i]=1.0
        Aeq.append(row); beq.append(games_v[k][(1<<n)-1])
    N=(1<<n)-1
    for k in range(m):
        for T in range(1,N):
            row=[0.0]*nv
            for i in range(n):
                if T>>i&1: row[k*n+i]=-1.0
            A.append(row); b.append(-games_v[k][T])
    for (k,l,S) in edges:
        for i in range(n):
            if S>>i&1:
                row=[0.0]*nv; row[k*n+i]=1.0; row[l*n+i]=-1.0
                A.append(row); b.append(0.0)
    r=linprog([0.0]*nv, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq,
              bounds=[(None,None)]*nv, method="highs")
    return bool(r.success)
