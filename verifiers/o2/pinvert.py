"""Vertices of the dual polyhedron certifying that the whole poor set is PINNED.

In CFG the three players of L sit at the leximin level mu, i.e.
    max { x(L) : x in Core, x >= mu*1 } = 3 mu.
Substituting y = x - mu*1 >= 0 (so y(N) = c := 1 - 5mu and
y(S) <= f'(S) := f(S) - mu|S|) this reads

    max { y(L) : y >= 0, y(N) = c, y(S) <= f'(S) for proper nonempty S } = 0.

Its LP dual is   min { c*alpha + sum_S beta_S f'(S) }  subject to
    alpha + sum_{S ni k} beta_S >= [k in L]   for every k in N,   beta >= 0,
so the pinning holds iff SOME dual-feasible (alpha, beta) has objective <= 0.
The dual feasible region D_L does not involve the game at all, the objective is
linear in (v, mu), and the optimum is attained at a vertex (D_L is pointed and
the primal is feasible and bounded).  So enumerating the vertices of D_L turns
the pinning into a finite disjunction of linear conditions.

A vertex needs 31 active constraints out of 5 rows and 30 sign constraints, so
|supp(beta)| <= 4 and the active rows number |supp(beta)| + 1.
route1's remark (iii) is the sub-case |supp(beta)| = 1: a single tight cap.
"""
from __future__ import annotations
import itertools, json
from fractions import Fraction as F

N = 5
FULL = 31
L = [0, 1, 2]
PROPER = [S for S in range(1, FULL)]        # 30 proper nonempty subsets


def solve(A, b):
    k = len(A); nc = len(A[0])
    M = [[F(x) for x in A[r]] + [F(b[r])] for r in range(k)]
    piv, rr = [], 0
    for c in range(nc):
        p = next((r for r in range(rr, k) if M[r][c] != 0), None)
        if p is None:
            return None
        M[rr], M[p] = M[p], M[rr]
        pv = M[rr][c]
        M[rr] = [q / pv for q in M[rr]]
        for r in range(k):
            if r != rr and M[r][c] != 0:
                f = M[r][c]
                M[r] = [M[r][j] - f * M[rr][j] for j in range(nc + 1)]
        piv.append(c); rr += 1
    if len(piv) != nc:
        return None
    return [M[i][nc] for i in range(nc)]


def main():
    rhs = [1 if k in L else 0 for k in range(N)]
    verts = set()
    for k in range(0, 5):                    # |supp(beta)|
        for W in itertools.combinations(PROPER, k):
            for I in itertools.combinations(range(N), k + 1):
                # unknowns: alpha, beta_W ; equations: rows I active
                A = [[1] + [1 if S >> i & 1 else 0 for S in W] for i in I]
                b = [rhs[i] for i in I]
                sol = solve(A, b)
                if sol is None:
                    continue
                al, be = sol[0], sol[1:]
                if any(x <= 0 for x in be):
                    continue
                ok = True
                for kk in range(N):
                    if al + sum(be[j] for j, S in enumerate(W) if S >> kk & 1) < rhs[kk]:
                        ok = False; break
                if ok:
                    verts.add((al, tuple(sorted((S, be[j]) for j, S in enumerate(W)))))
        print(f"  |supp(beta)| = {k}: {len(verts)} vertices so far", flush=True)
    print(f"total vertices of D_L: {len(verts)}")
    json.dump([[str(al), [[S, str(x)] for S, x in be]] for al, be in sorted(verts)],
              open("/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/"
                   "scratchpad/sel/o2/pinverts.json", "w"))
    onecap = sum(1 for al, be in verts if len(be) == 1)
    print(f"  of which single-cap certificates (route1 remark (iii)): {onecap}")


if __name__ == "__main__":
    main()
