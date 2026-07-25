"""FAST float probe of the co-singleton (m=n) star at n=5 on simplex-type bases.
Everything float (scipy). Answers: is each game exact? does the arm family LP
feasibly admit a monotonic core selection? do the arm cores intersect? what is
the min-monotonicity slack? Only a float census -- exact certification is a
separate one-shot step reserved for a genuine infeasible hit.
"""
from scipy.optimize import linprog
from floatscreen import is_exact_float, _core_min_xS_float, is_balanced_float

n = 5
N = (1 << n) - 1

def float_exactify(vf):
    v2 = [0.0] * (1 << n); v2[N] = vf[N]
    for S in range(1, N):
        m = _core_min_xS_float(n, vf, S)
        if m is None:
            return None
        v2[S] = m
    return v2

def family_slack(games_v, edges):
    m = len(games_v); nv = n * m + 1; ti = n * m
    A, b, Aeq, beq = [], [], [], []
    for k in range(m):
        row = [0.0] * nv
        for i in range(n):
            row[k * n + i] = 1.0
        Aeq.append(row); beq.append(games_v[k][N])
    for k in range(m):
        for T in range(1, N):
            row = [0.0] * nv
            for i in range(n):
                if T >> i & 1:
                    row[k * n + i] = -1.0
            A.append(row); b.append(-games_v[k][T])
    for (k, l, S) in edges:
        for i in range(n):
            if S >> i & 1:
                row = [0.0] * nv
                row[k * n + i] = 1.0; row[l * n + i] = -1.0; row[ti] = 1.0
                A.append(row); b.append(0.0)
    c = [0.0] * nv; c[ti] = -1.0
    r = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=[(None, None)] * nv, method="highs")
    return None if not r.success else -r.fun

def cores_intersect(games_v):
    A, b = [], []
    for gv in games_v:
        for T in range(1, N):
            A.append([-1.0 if T >> i & 1 else 0.0 for i in range(n)]); b.append(-gv[T])
    Aeq = [[1.0] * n]; beq = [games_v[0][N]]
    r = linprog([0.0] * n, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=[(None, None)] * n, method="highs")
    return bool(r.success)

def probe(tag, c, w, dks):
    vf = [0.0] * (1 << n); vf[N] = float(c)
    for S, val in w.items():
        vf[S] = float(val)
    base = float_exactify(vf)
    if base is None:
        print(f"{tag}: base unbalanced"); return
    arms = []
    for k in range(n):
        S = N ^ (1 << k)
        v2 = list(base); v2[S] += dks[k]
        arms.append((S, v2))
    games_v = [base] + [v for _, v in arms]
    exs = [is_exact_float(n, gv) for gv in games_v]
    if not all(exs):
        print(f"{tag}: c={c} d={dks} NOT all exact ({sum(exs)}/{len(exs)})"); return
    edges = [(0, j + 1, S) for j, (S, _) in enumerate(arms)]
    slack = family_slack(games_v, edges)
    inter = cores_intersect([v for _, v in arms])
    feas = slack is not None and slack >= -1e-7
    flag = "  <<< INFEASIBLE!!!" if not feas else ""
    print(f"{tag}: c={c} d={dks} all_exact=T arms_intersect={inter} slack={slack:.4f} feas={feas}{flag}")

print("=== pure simplex base (all proper 0) ===")
for c in [5, 6, 7, 8, 10, 12]:
    for d in [1, 2, 3]:
        probe(f"simplex", c, {}, [d] * n)
    probe(f"simplex-asym", c, {}, [1, 2, 3, 4, 5])
    if c > 2:
        probe(f"simplex-big", c, {}, [c - 1] * n)

print("\n=== near-simplex with small positive proper values ===")
probe("w1", 10, {0b00011: 2, 0b01100: 2}, [2, 2, 2, 2, 2])
probe("w2", 12, {0b00111: 3, 0b11000: 2, 0b10010: 1}, [3, 3, 3, 3, 3])
probe("w3", 8, {0b01010: 1, 0b00101: 1, 0b10001: 1}, [2, 2, 2, 2, 2])
probe("w4", 15, {0b00011: 3, 0b00110: 3, 0b01100: 3, 0b11000: 3, 0b10001: 3}, [4, 4, 4, 4, 4])
