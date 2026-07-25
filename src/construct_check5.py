"""Validate the constructive lower bound (proof skeleton) for the co-singleton
family on general exact bases:

  x^b := maximin core point (argmax_core min_i (x_i - m_i)), m_i = v({i}).
  For arm k (bump N\\{k}), y^k := x^b + t*(1_{N\\{k}} - (n-1) e_k).
  Claim: with t = min_i(x^b_i - m_i)/(n-1) >= min_w/(n(n-1)), each y^k lies in
  core(t_k) and dominates x^b off coordinate k -> family feasible with slack t.

We check, per base: the achieved constructive t, whether (x^b,{y^k}) is a valid
feasible point, and t vs the empirical floor min_w/(n(n-1)).
"""
import random
from scipy.optimize import linprog
from widthslack5 import seed_gen, float_exactify, arm_pool, coord_widths, family_slack
from floatscreen import is_balanced_float, is_exact_float

n = 5; N = 31

def core_point_maximin_over_m(vf, m):
    """argmax_core min_i (x_i - m_i): max s s.t. x in core, x_i - m_i >= s."""
    nv = n + 1; si = n
    A, b = [], []
    for T in range(1, N):
        row = [0.0] * nv
        for i in range(n):
            if T >> i & 1:
                row[i] = -1.0
        A.append(row); b.append(-vf[T])
    for i in range(n):  # x_i - s >= m_i  -> -x_i + s <= -m_i
        row = [0.0] * nv; row[i] = -1.0; row[si] = 1.0
        A.append(row); b.append(-m[i])
    Aeq = [[1.0] * n + [0.0]]; beq = [vf[N]]
    c = [0.0] * nv; c[si] = -1.0
    r = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=[(None, None)] * nv, method="highs")
    if not r.success:
        return None, None
    return r.x[:n], -r.fun  # x^b, s = min_i(x_i-m_i)

def in_core(vf, x, tol=1e-7):
    if abs(sum(x) - vf[N]) > 1e-6:
        return False
    for T in range(1, N):
        if sum(x[i] for i in range(n) if T >> i & 1) < vf[T] - tol:
            return False
    return True

rng = random.Random(909)
checked = 0; ok_feasible = 0; ok_bound = 0
min_construct_ratio = 1e9
worst = None
for t in range(600):
    kind = ['simplex', 'neardegen', 'asym'][t % 3]
    s = seed_gen(rng, kind)
    if not is_balanced_float(n, s):
        continue
    b = float_exactify(s)
    if b is None or not is_exact_float(n, b):
        continue
    pool = arm_pool(b, 3)
    cos = [(N ^ (1 << k), pool[N ^ (1 << k)]) for k in range(n) if (N ^ (1 << k)) in pool]
    if len(cos) < 2:
        continue
    m = [b[1 << i] for i in range(n)]           # m_i = v({i})
    w = coord_widths(b); min_w = min(w)
    if min_w < 1e-9:
        continue
    xb, sval = core_point_maximin_over_m(b, m)
    if xb is None:
        continue
    tc = sval / (n - 1)                          # constructive t
    # build y^k and verify
    feasible = True
    for (S, d) in cos:
        k = [i for i in range(n) if not (S >> i & 1)][0]  # excluded player
        y = list(xb)
        for i in range(n):
            if i != k:
                y[i] += tc
        y[k] -= tc * (n - 1)
        vt = list(b); vt[S] += d                  # arm game
        if not in_core(vt, y):
            feasible = False; break
        if any(y[i] < xb[i] - 1e-9 for i in range(n) if i != k):
            feasible = False; break
    checked += 1
    if feasible:
        ok_feasible += 1
    floor = min_w / (n * (n - 1))
    if tc >= floor - 1e-9:
        ok_bound += 1
    ratio = tc / min_w
    if ratio < min_construct_ratio:
        min_construct_ratio = ratio
        worst = (kind, round(tc, 4), round(min_w, 4), round(ratio, 5), feasible)
    if checked >= 200:
        break

print(f"checked={checked} bases")
print(f"construction FEASIBLE (valid core+monotone point): {ok_feasible}/{checked}")
print(f"construction t >= min_w/(n(n-1)) floor: {ok_bound}/{checked}")
print(f"min constructive t/min_w = {min_construct_ratio:.5f} (floor 1/(n(n-1))={1/(n*(n-1)):.5f})")
print(f"worst (kind,tc,min_w,ratio,feasible) = {worst}")
