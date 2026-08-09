"""Positive controls for lib24's simplex, BEFORE any claim rests on it.

  C1  core_max(w = 1_S) must return exactly f(S) on an exact game
      (that IS exactness) -- and must NOT on a deliberately non-exact game.
  C2  core_max against brute-force vertex enumeration of the core
      (all 4-subsets of the 30 caps, exact 5x5 solves) on small games.
  C3  the returned y is primal feasible and attains the value (asserted
      inside core_max), and the dual (eta, gamma) is dual feasible with the
      same value -- checked here explicitly.
  C4  core_feasible agrees with core_max on a linear test.
"""
import itertools
import random
from fractions import Fraction as F

import lib24 as L
from lib24 import F as _F  # noqa


def brute_core_vertices(f, T):
    """All vertices of {y(N)=T, y(S) <= f(S)} by exact enumeration."""
    verts = set()
    caps = L.PROPER
    for combo in itertools.combinations(caps, 4):
        M = [[F(1)] * 5]
        rhs = [F(T)]
        for S in combo:
            M.append([F(1) if S >> k & 1 else F(0) for k in range(5)])
            rhs.append(F(f[S]))
        # gaussian elimination
        A = [row[:] + [rhs[i]] for i, row in enumerate(M)]
        r = 0
        piv = []
        for c in range(5):
            p = next((i for i in range(r, 5) if A[i][c] != 0), None)
            if p is None:
                continue
            A[r], A[p] = A[p], A[r]
            d = A[r][c]
            A[r] = [t / d for t in A[r]]
            for i in range(5):
                if i != r and A[i][c] != 0:
                    fac = A[i][c]
                    A[i] = [A[i][j] - fac * A[r][j] for j in range(6)]
            piv.append(c)
            r += 1
        if r < 5:
            continue
        y = [A[i][5] for i in range(5)]
        if sum(y) != T:
            continue
        if all(sum(y[k] for k in L.bits(S)) <= f[S] for S in L.PROPER):
            verts.add(tuple(y))
    return sorted(verts)


def rand_game(rng, maxtotal=8, maxrows=4):
    while True:
        total = rng.randint(3, maxtotal)
        gens = []
        for _ in range(rng.randint(2, maxrows)):
            cuts = sorted(rng.randrange(total + 1) for _ in range(4))
            gens.append(tuple(F(b - a) for a, b in zip([0] + cuts, cuts + [total])))
        if all(min(g[i] for g in gens) == 0 for i in range(5)):
            return gens


def main():
    rng = random.Random(2402)
    ok = True

    # ---- C1 exactness round-trip
    for _ in range(15):
        gens = rand_game(rng)
        v = L.envelope(gens)
        f, T = L.fvec(v)
        for S in L.PROPER:
            w = [1 if S >> k & 1 else 0 for k in range(5)]
            val, y, eta, gam, _ = L.core_max(f, T, w)
            assert val == f[S], f"C1 FAIL max y({L.nm(S)}) = {val} != {f[S]}"
    print("C1 exact games: max_core y(S) == f(S) for all 30 S, 15 games  OK")

    # C1' negative control: a non-exact game must fail the round trip
    #     v(S)=0 except v(N)=1 and v(ab)=1/2 raised to 3/4 (core unchanged? no)
    v = [F(0)] * 32
    v[31] = F(1)
    v[0b00011] = F(3, 4)   # ab
    f = [v[31] - v[31 ^ S] for S in range(32)]
    T = v[31]
    bad = [S for S in L.PROPER
           if L.core_max(f, T, [1 if S >> k & 1 else 0 for k in range(5)])[0]
           != f[S]]
    # f(S) here is derived from v, so caps are consistent; exactness fails iff
    # some min_core y(S) > v(S).  Check directly:
    nonexact = []
    for S in L.PROPER:
        w = [-1 if S >> k & 1 else 0 for k in range(5)]
        val, *_ = L.core_max(f, T, w)
        if -val != v[S]:
            nonexact.append(S)
    assert nonexact, "C1' FAIL: designed non-exact game came out exact"
    print(f"C1' negative control: non-exact game detected at "
          f"{[L.nm(S) for S in nonexact][:6]}...  OK")

    # ---- C2 against brute force
    for t in range(4):
        gens = rand_game(rng, maxtotal=6, maxrows=3)
        v = L.envelope(gens)
        f, T = L.fvec(v)
        verts = brute_core_vertices(f, T)
        assert verts, "C2 FAIL: empty core"
        for _ in range(6):
            w = [rng.randint(-2, 3) for _ in range(5)]
            val, y, *_ = L.core_max(f, T, w)
            bf = max(sum(w[k] * ver[k] for k in range(5)) for ver in verts)
            assert val == bf, f"C2 FAIL {val} != {bf} w={w}"
    print("C2 core_max == brute-force vertex maximum, 4 games x 6 objectives  OK")

    # ---- C3 dual feasibility of the returned certificate
    for _ in range(8):
        gens = rand_game(rng)
        v = L.envelope(gens)
        f, T = L.fvec(v)
        w = [2, 1, 0, 0, 0]
        val, y, eta, gam, _ = L.core_max(f, T, w)
        for k in range(5):
            Gk = sum(g for S, g in gam.items() if S >> k & 1)
            assert eta + Gk >= w[k], "C3 FAIL dual infeasible"
        assert eta * T + sum(g * f[S] for S, g in gam.items()) == val, \
            "C3 FAIL dual value mismatch"
    print("C3 returned dual (eta, gamma) feasible with matching value  OK")

    # ---- C4 core_feasible vs core_max
    for _ in range(8):
        gens = rand_game(rng)
        v = L.envelope(gens)
        f, T = L.fvec(v)
        lam = L.lam_of(f, T)
        for p in range(5):
            got = L.core_feasible(f, T, [lam if k == p else F(0)
                                         for k in range(5)])
            want = f[1 << p] >= lam
            assert got == want, "C4 FAIL"
    print("C4 core_feasible agrees with the f-value test  OK")

    print("\nALL SELFTESTS PASSED" if ok else "FAILURES")


if __name__ == "__main__":
    main()
