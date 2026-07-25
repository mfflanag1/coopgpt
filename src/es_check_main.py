"""Main session's independent egalitarian-procedure implementation (validated
on Dietzenbacher 2021 Examples 2 and 3). For witness verification."""
from fractions import Fraction as F

def egalitarian_procedure(n, v):
    N = (1 << n) - 1
    fixed = {}
    A = []
    for _round in range(n + 1):
        if len(fixed) == n:
            break
        chi = {}
        for S in range(1, N + 1):
            mem = [i for i in range(n) if S >> i & 1]
            free = [i for i in mem if i not in fixed]
            if free:
                share = (v[S] - sum(fixed[i] for i in mem if i in fixed)) / len(free)
                chi[S] = {i: (fixed[i] if i in fixed else share) for i in mem}
            else:
                chi[S] = {i: fixed[i] for i in mem}
        A = []
        for S in range(1, N + 1):
            mem = [i for i in range(n) if S >> i & 1]
            if sum(chi[S][i] for i in mem) != v[S]:
                continue
            ok = True
            for i in mem:
                for T in range(1, N + 1):
                    if T >> i & 1 and chi[T][i] > chi[S][i]:
                        ok = False; break
                if not ok: break
            if ok:
                A.append(S)
        for S in A:
            for i in range(n):
                if S >> i & 1 and i not in fixed:
                    fixed[i] = chi[S][i]
    return fixed, A, ((1 << n) - 1 in A)
