"""Cross-validate exact_linprog against scipy HiGHS on random LPs,
including the LP sympy got wrong."""
import random
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog as flp
from exactlp import exact_linprog

# the sympy-buggy LP: min x+y+z, pairs >= 1, x,y,z >= 0 -> 3/2
st, opt, x = exact_linprog([1, 1, 1],
    A_ub=[[-1, -1, 0], [-1, 0, -1], [0, -1, -1], [-1, 0, 0], [0, -1, 0], [0, 0, -1]],
    b_ub=[-1, -1, -1, 0, 0, 0])
assert st == 'optimal' and opt == F(3, 2), (st, opt, x)
print("sympy-buggy LP: exact gives", opt, x, "OK")

random.seed(7)
mism = 0
for trial in range(400):
    nv = random.randint(1, 6)
    mu = random.randint(0, 6)
    me = random.randint(0, 2)
    c = [random.randint(-5, 5) for _ in range(nv)]
    A_ub = [[random.randint(-4, 4) for _ in range(nv)] for _ in range(mu)]
    b_ub = [random.randint(-6, 6) for _ in range(mu)]
    A_eq = [[random.randint(-4, 4) for _ in range(nv)] for _ in range(me)]
    b_eq = [random.randint(-6, 6) for _ in range(me)]
    st, opt, x = exact_linprog(c, A_ub or None, b_ub or None, A_eq or None, b_eq or None)
    res = flp(c, A_ub=np.array(A_ub) if mu else None, b_ub=np.array(b_ub, float) if mu else None,
              A_eq=np.array(A_eq) if me else None, b_eq=np.array(b_eq, float) if me else None,
              bounds=[(None, None)] * nv, method="highs")
    fstatus = {0: 'optimal', 2: 'infeasible', 3: 'unbounded'}.get(res.status, 'other')
    ok = (st == fstatus)
    if ok and st == 'optimal':
        ok = abs(float(opt) - res.fun) < 1e-6
        # feasibility of exact solution
        for r, b in zip(A_ub, b_ub):
            assert sum(F(a) * xi for a, xi in zip(r, x)) <= F(b), (trial, "ub violated")
        for r, b in zip(A_eq, b_eq):
            assert sum(F(a) * xi for a, xi in zip(r, x)) == F(b), (trial, "eq violated")
    if not ok:
        mism += 1
        print("MISMATCH", trial, st, fstatus, opt, res.fun if res.status == 0 else None)
print(f"{400 - mism}/400 agree with HiGHS")
