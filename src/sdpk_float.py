"""Float version of SD-satisfaction + s_ij, for fast smooth local search only.
All CERTIFICATION goes through the exact sdpk.py / sd.py path."""
import numpy as np

def sd_satisfactions_float(n, N, vf, xf):
    """vf: array len 2^n floats; xf: array len n floats. Returns dict S->float."""
    proper = list(range(1, N))
    fixed = {}
    xs = {}
    for S in proper:
        acc = 0.0
        for i in range(n):
            if S >> i & 1:
                acc += xf[i]
        xs[S] = acc
    pc = [bin(S).count("1") for S in range(N + 1)]
    while len(fixed) < len(proper):
        best = None
        arg = []
        for S in proper:
            if S in fixed:
                continue
            fvals = {}
            for T, FT in fixed.items():
                if T & ~S == 0:
                    m = T
                    while m:
                        i = (m & -m).bit_length() - 1
                        if i not in fvals or FT < fvals[i]:
                            fvals[i] = FT
                        m &= m - 1
            surplus = xs[S] - vf[S]
            free = pc[S] - len(fvals)
            sv = 0.0
            for val in fvals.values():
                sv += val
            if free > 0:
                cand = (surplus - sv) / free
            else:
                cand = surplus - sv + max(fvals.values())
            if best is None or cand < best - 1e-15:
                best = cand
                arg = [S]
            elif abs(cand - best) <= 1e-12:
                arg.append(S)
        for S in arg:
            fixed[S] = best
    return fixed

def s_pairs_float(n, N, vf, xf):
    """Return (residual_vec, s) : list of s_ij-s_ji for i<j."""
    Fx = sd_satisfactions_float(n, N, vf, xf)
    s = {}
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            best = None
            for S in range(1, N):
                if (S >> i & 1) and not (S >> j & 1):
                    v = Fx[S]
                    if best is None or v < best:
                        best = v
            s[(i, j)] = best
    res = []
    for i in range(n):
        for j in range(i + 1, n):
            res.append(s[(i, j)] - s[(j, i)])
    return res, s
