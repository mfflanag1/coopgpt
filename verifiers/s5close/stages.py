"""MULTI-STAGE pinning certificates, both sides -- the machinery s5full/REPORT.txt
section 7 named as the missing piece.

Discharges: the hypothesis "the Lmax stratum at level M_l really is pinned
there" (ceiling stage B-1-l) and "the Lmin stratum at level m_k really is
pinned there" (floor stage k), for EVERY stratum, not just the extreme one.

DERIVATION (ceiling; T = 1, players carry their Lmax level z_i).
Fix a stratum index l.  Let Dhigh = the players in strata above l, whose Lmax
values are already pinned, and F = the players in strata 0..l.  On the face
    P_l = { x in Core : x_i = z_i for i in Dhigh }
the constraints x(S) >= v(S) collapse, for A = S cap F, to
    x(A) >= v_l(A) := max { v(S) - z(S cap Dhigh) : S cap F = A }
                    = max_{B subset Dhigh} ( v(A u B) - z(B) ),
together with x(F) = T_l := 1 - z(Dhigh).  So P_l restricted to F is exactly
Core(v_l), a game on |F| < 5 players.

WARNING (a) OF REPORT SECTION 7, HEEDED.  A3 does NOT recurse: v_l need not be
exact, so M_l is NOT read off an anchor of v_l.  M_l enters only as the free
level variable of the configuration, and the statement encoded is purely the
pinning
    min { x(D_l) : x in Core(v_l),  x <= M_l * 1_F }  =  |D_l| M_l ,
which is what the leximax algorithm actually asserts at stage l.  (It also
implies that the stage level cannot be lowered: a point of Core(v_l) with
max_F x < M_l would be feasible with x(D_l) < |D_l| M_l.)

Substituting u = M_l * 1_F - x >= 0 turns it into
    max { u(D_l) : u >= 0,  u(F) = c_l := |F| M_l - T_l,
                   u(A) <= h_l(A) := M_l|A| - v_l(A) }  =  0,
whose LP dual is the game-free polyhedron
    D = { (alpha,beta>=0) : alpha + sum_{A ni k} beta_A >= [k in D_l], k in F }
over the PROPER nonempty A subset F, and the pinning holds iff
    alpha * c_l + sum_A beta_A h_l(A) <= 0
at some vertex.  l = B-1 (Dhigh empty, F = N, v_l = v) is stage 1 and
reproduces pinvert.pinverts exactly.

WARNING (b) OF REPORT SECTION 7, HEEDED.  h_l(A) is a MIN over the preimages
B subset Dhigh.  It is encoded exactly, with one fresh variable per A carrying
    h_A <= (every preimage value)   AND   Or_B ( h_A == (that preimage value) ),
so no preimage choice is silently fixed and no relaxation is introduced.  This
keeps the disjunction additive (2^|Dhigh| per A) instead of multiplicative
across the support of beta.

The floor side is the mirror image: Dlow = strata below k, G = strata k..,
    w_k(A) = max_{B subset Dlow} ( v(A u B) - x(B) ),   T_k = 1 - x(Dlow),
    f_k(A) = T_k - w_k(G \\ A),
    max { y(D_k) : y >= 0, y(G) = T_k - |G| m_k, y(A) <= f_k(A) - m_k|A| } = 0,
and f_k(A) is again a MIN over preimages, encoded the same way.  k = 0 gives
the floor stage 1 used by Theorem thm:cfg.
"""
from __future__ import annotations
import itertools
from fractions import Fraction as F

import z3

N, FULL = 5, 31
SZ = [bin(S).count("1") for S in range(32)]
_CACHE = {}


def q(x):
    x = F(x)
    return z3.RealVal(f"{x.numerator}/{x.denominator}")


def subsets(mask):
    """All submasks of mask, including 0 and mask itself."""
    out, s = [], mask
    while True:
        out.append(s)
        if s == 0:
            break
        s = (s - 1) & mask
    return out


def _solve(A, b):
    k, nc = len(A), len(A[0])
    M = [[F(x) for x in A[r]] + [F(b[r])] for r in range(k)]
    piv, rr = [], 0
    for c in range(nc):
        p = next((r for r in range(rr, k) if M[r][c] != 0), None)
        if p is None:
            return None
        M[rr], M[p] = M[p], M[rr]
        pv = M[rr][c]
        M[rr] = [t / pv for t in M[rr]]
        for r in range(k):
            if r != rr and M[r][c] != 0:
                f = M[r][c]
                M[r] = [M[r][j] - f * M[rr][j] for j in range(nc + 1)]
        piv.append(c)
        rr += 1
    return [M[i][nc] for i in range(nc)] if len(piv) == nc else None


def pinverts_ground(ground, D):
    """Vertices of the dual pinning polyhedron on ground set `ground` (a mask)
    for the pinned set `D` (a submask).  Returns [(alpha, ((A, beta_A), ...))].

    |supp(beta)| <= |ground| - 1 (a vertex needs |supp|+1 tight rows out of
    |ground|), so the enumeration is over proper nonempty A subset ground."""
    key = (ground, D)
    if key in _CACHE:
        return _CACHE[key]
    players = [i for i in range(N) if ground >> i & 1]
    g = len(players)
    proper = [A for A in subsets(ground) if A not in (0, ground)]
    rhs = {i: (1 if D >> i & 1 else 0) for i in players}
    verts = set()
    for k in range(0, g):
        for W in itertools.combinations(proper, k):
            for I in itertools.combinations(players, k + 1):
                A = [[1] + [1 if S >> i & 1 else 0 for S in W] for i in I]
                sol = _solve(A, [rhs[i] for i in I])
                if sol is None:
                    continue
                al, be = sol[0], sol[1:]
                if any(x <= 0 for x in be):
                    continue
                if all(al + sum(be[j] for j, S in enumerate(W) if S >> kk & 1)
                       >= rhs[kk] for kk in players):
                    verts.add((al, tuple(sorted((S, be[j])
                                                for j, S in enumerate(W)))))
    out = sorted(verts)
    _CACHE[key] = out
    return out


def _minvar(name, exprs):
    """Fresh z3 real constrained to equal min(exprs), exactly."""
    h = z3.Real(name)
    cons = [h <= e for e in exprs]
    cons.append(z3.Or([h == e for e in exprs]))
    return h, cons


def ceiling_stage(v, z, mask_by_stratum, l, Ml, tag):
    """Constraints asserting that Lmax stratum l is pinned at level Ml.

    v: list of 32 z3 reals.  z: list of 5 z3 level expressions (z_i).
    mask_by_stratum[l]: player mask of Lmax stratum l (0 = poorest).
    Returns (constraints, n_vertices) or (None, 0) if the stage is vacuous."""
    B = len(mask_by_stratum)
    Dhigh = 0
    for j in range(l + 1, B):
        Dhigh |= mask_by_stratum[j]
    Fm = FULL ^ Dhigh
    Dl = mask_by_stratum[l]
    if bin(Fm).count("1") < 2 or Dl == Fm:
        return None, 0            # nothing to certify (see module docstring)
    zsum = lambda m: z3.Sum([z[i] for i in range(N) if m >> i & 1] or [q(0)])
    Tl = 1 - zsum(Dhigh)
    cl = q(bin(Fm).count("1")) * Ml - Tl
    cons, hv = [], {}
    for A in subsets(Fm):
        if A in (0, Fm):
            continue
        exprs = [q(SZ[A]) * Ml + zsum(Bm) - v[A | Bm] for Bm in subsets(Dhigh)]
        h, c = _minvar(f"{tag}h{A}", exprs)
        hv[A] = h
        cons += c
    verts = pinverts_ground(Fm, Dl)
    disj = [q(al) * cl + z3.Sum([q(b) * hv[A] for A, b in be] or [q(0)]) <= 0
            for al, be in verts]
    if not disj:
        return None, 0
    cons.append(z3.Or(disj))
    return cons, len(verts)


def floor_stage(v, x, mask_by_stratum, k, mk, tag):
    """Constraints asserting that Lmin stratum k is pinned at level mk."""
    A_ = len(mask_by_stratum)
    Dlow = 0
    for j in range(k):
        Dlow |= mask_by_stratum[j]
    Gm = FULL ^ Dlow
    Dk = mask_by_stratum[k]
    if bin(Gm).count("1") < 2 or Dk == Gm:
        return None, 0
    xsum = lambda m: z3.Sum([x[i] for i in range(N) if m >> i & 1] or [q(0)])
    Tk = 1 - xsum(Dlow)
    c = Tk - q(bin(Gm).count("1")) * mk
    cons, fv = [], {}
    for A in subsets(Gm):
        if A in (0, Gm):
            continue
        comp = Gm ^ A                      # G \ A, nonempty and proper
        # f_k(A) = T_k - w_k(G\A),  w_k(G\A) = max_B ( v((G\A) u B) - x(B) )
        exprs = [Tk - (v[comp | Bm] - xsum(Bm)) - q(SZ[A]) * mk
                 for Bm in subsets(Dlow)]
        f, cc = _minvar(f"{tag}f{A}", exprs)
        fv[A] = f
        cons += cc
    verts = pinverts_ground(Gm, Dk)
    disj = [q(al) * c + z3.Sum([q(b) * fv[A] for A, b in be] or [q(0)]) <= 0
            for al, be in verts]
    if not disj:
        return None, 0
    cons.append(z3.Or(disj))
    return cons, len(verts)


if __name__ == "__main__":
    import json
    import sys
    sys.path.insert(0, sys.path[0])
    import pinvert
    # REGRESSION 1: on the full ground set the general enumerator must agree
    # with pinvert.pinverts (which itself matches the stored 354 of thm:cfg).
    for D in ([0], [0, 1], [0, 1, 2], [0, 1, 2, 3]):
        a = pinvert.pinverts(D)
        b = pinverts_ground(FULL, sum(1 << i for i in D))
        assert [(al, tuple(be)) for al, be in a] == b, D
        print(f"  ground=N, D={D}: {len(b)} vertices, agrees with pinvert.py")
    # vertex counts on the reduced ground sets the stages need
    counts = {}
    for g in (2, 3, 4):
        gm = (1 << g) - 1
        for d in range(1, 1 << g):
            if d == gm:
                continue
            counts[f"g{g}_D{d}"] = len(pinverts_ground(gm, d))
    print("reduced-ground vertex counts:", counts)
    json.dump(counts, open(sys.path[0] + "/stage_vertex_counts.json", "w"),
              indent=1)
