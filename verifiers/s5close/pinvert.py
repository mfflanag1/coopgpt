"""PARAMETRIC pinning-certificate vertex enumerator (task #22, stage-1 machinery).

Discharges: the "finite disjunction" step used by every pinning hypothesis in
this program, on BOTH sides, for an ARBITRARY pinned set D.

FLOOR SIDE (the Lmin bottom stratum D sits at mu).  With y = x - mu*1 >= 0,
    max { y(D) : y >= 0, y(N) = c := T - 5 mu, y(S) <= f'(S) } = 0,
    f'(S) = f(S) - mu|S|,  f(S) = T - v(N\\S).
CEILING SIDE (the Lmax top stratum D sits at M).  With u = M*1 - x >= 0,
    max { u(D) : u >= 0, u(N) = c_M := 5M - T, u(S) <= h(S) } = 0,
    h(S) = M|S| - v(S).
The two are the SAME linear program with (c, f') replaced by (c_M, h), so the
dual polyhedron

    D_D = { (alpha, beta) : beta >= 0,  alpha + sum_{S ni k} beta_S >= [k in D]
                            for every k in N },        S over PROPER nonempty

is game-free and depends only on D.  Pinning holds iff the dual objective
    c * alpha + sum_S beta_S * f'(S)          (resp. c_M, h)
is <= 0 at SOME vertex of D_D.  D_D is pointed (its recession cone is
{alpha + sum_{S ni k} beta_S >= 0, beta >= 0}, which contains no line), the
primal is feasible (y = 0 is feasible when c = 0; in general feasible because
the Lmin/Lmax vector itself supplies a point) and bounded, so the dual optimum
is attained at a vertex and the disjunction over vertices is exhaustive.

A vertex has |supp(beta)| = k <= 4 and needs k+1 tight rows.

REGRESSION: for D = {0,1,2} this must reproduce, exactly, the 354 vertices
stored in verifiers/o2/pinverts.json (the polyhedron of Theorem thm:cfg).
"""
from __future__ import annotations
import itertools
import json
import sys
from fractions import Fraction as F

N, FULL = 5, 31
PROPER = list(range(1, FULL))            # 30 proper nonempty subsets


def solve(A, b):
    """Exact Gaussian elimination on a square system; None if singular."""
    k = len(A)
    nc = len(A[0])
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
        piv.append(c)
        rr += 1
    if len(piv) != nc:
        return None
    return [M[i][nc] for i in range(nc)]


def pinverts(D, verbose=False):
    """Vertices of D_D as a sorted list of (alpha, ((S, beta_S), ...))."""
    rhs = [1 if k in D else 0 for k in range(N)]
    verts = set()
    for k in range(0, 5):                                  # |supp(beta)|
        for W in itertools.combinations(PROPER, k):
            for I in itertools.combinations(range(N), k + 1):
                A = [[1] + [1 if S >> i & 1 else 0 for S in W] for i in I]
                sol = solve(A, [rhs[i] for i in I])
                if sol is None:
                    continue
                al, be = sol[0], sol[1:]
                if any(x <= 0 for x in be):
                    continue
                if all(al + sum(be[j] for j, S in enumerate(W) if S >> kk & 1)
                       >= rhs[kk] for kk in range(N)):
                    verts.add((al, tuple(sorted((S, be[j])
                                                for j, S in enumerate(W)))))
        if verbose:
            print(f"    |supp(beta)|={k}: {len(verts)} vertices so far", flush=True)
    return sorted(verts)


def dump(verts):
    return [[str(al), [[S, str(x)] for S, x in be]] for al, be in verts]


def load(path):
    raw = json.load(open(path))
    return sorted((F(al), tuple((int(S), F(x)) for S, x in be)) for al, be in raw)


if __name__ == "__main__":
    here = sys.path[0]
    out = {}
    # --- REGRESSION against the stored 354-vertex polyhedron of thm:cfg ---
    v012 = pinverts([0, 1, 2], verbose=True)
    ref = load(f"{here}/lib/pinverts_L012.json")
    same = ([(a, tuple(b)) for a, b in v012] == ref)
    print(f"D={{0,1,2}}: {len(v012)} vertices; matches stored pinverts.json: {same}")
    assert len(v012) == 354 and same, "REGRESSION FAILED"
    out["012"] = {"n": len(v012)}
    json.dump(dump(v012), open(f"{here}/pinverts_D3.json", "w"))

    # --- the sets this task needs ---
    for name, D in [("D1", [0]), ("D2", [0, 1]), ("D4", [0, 1, 2, 3]),
                    ("D5", [0, 1, 2, 3, 4])]:
        vs = pinverts(D)
        print(f"D={D}: {len(vs)} vertices", flush=True)
        out[name] = {"D": D, "n": len(vs)}
        json.dump(dump(vs), open(f"{here}/pinverts_{name}.json", "w"))
    json.dump(out, open(f"{here}/pinvert_counts.json", "w"), indent=1)
