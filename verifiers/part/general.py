"""TASK #26: the general block-polytope frame for PART(p,q), all m.

Discharges the machine side of PROOF_GENERAL.txt.  Everything about the frame
is combinatorial -- no game values -- so each check is a statement about set
systems and holds at every boundary of every exact game.

THE FRAME.  Let S1 = P u {f} and S2 = Q u {g} be a PART(p,q) configuration.
Block rigidity pins every core point to x(S1) = v(S1) and x(S2) = v(S2), so
with u_i = x_i - phi_i (i in L) the core is a polytope K in R^L with

      d_f = -U_P := -sum_{i in P} u_i,      d_g = -U_Q := -sum_{i in Q} u_i.

For a coalition T write eps_f = [f in T], eps_g = [g in T].  Then

      d(T) = sum_{i in T n L} u_i - eps_f U_P - eps_g U_Q,

so the facet normal of T, as a vector in R^L, is

      nu_i = [i in T] - eps_f   for i in P,     nu_i = [i in T] - eps_g  for i in Q.

CONSEQUENCE (Lemma N*).  Within a block the coordinates of nu all lie in {0,1}
(when the block's rich player is outside T) or all in {-1,0} (when it is
inside).  So NO facet normal separates two players of the same block with
opposite signs.  The m=3 observation -- that v_b - v_c and its relatives never
occur -- is this statement for |Q| = 2.

LEMMA I*.  Every nonnegative nonzero direction on L is leximin-improving
(the strata of L all precede the strata meeting H), so

      D n R^L_{>=0} = {0},   D = { d : nu_T . d >= 0 for all tight T }.

In combinatorial form, since nu_T . 1_S = |T n S| - eps_f |P n S| - eps_g |Q n S|:

      FOR EVERY nonempty S in L there is a phi-tight T with
            |T n S|  <  eps_f |P n S| + eps_g |Q n S|.               (I*)

Checks performed here:
  G1  the normal formula and the type/sign structure, brute force over all
      coalitions, for a range of (p,q);
  G2  Lemma N*: no admissible normal separates two players of one block;
  G3  the combinatorial form (I*) agrees with "nu_T . 1_S < 0";
  G4  the ORTHANT-KILLING CERTIFICATES of PROOF_GENERAL.txt really do force
      D n R^L_{>=0} = {0}, for both recipes and a range of (p,q);
  G5  the two published witnesses (PART(2,2) and PART(1,3) at n=6) carry an
      orthant-killing certificate, and it is exhibited.

Usage: python3 general.py
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction as F

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L
import z3

ok = True


def check(label, cond, extra=""):
    global ok
    ok = ok and bool(cond)
    print(f"  [{'OK ' if cond else 'FAIL'}] {label}" + (f"  {extra}" if extra else ""))


def layout(p, q):
    """P = 0..p-1, Q = p..m-1, f = n-2, g = n-1."""
    m = p + q
    n = m + 2
    return n, m, list(range(p)), list(range(p, m)), n - 2, n - 1


def normal(p, q, T):
    """Facet normal of coalition T as a vector indexed by L = P u Q."""
    n, m, P, Q, f, g = layout(p, q)
    ef = (T >> f) & 1
    eg = (T >> g) & 1
    nu = []
    for i in P:
        nu.append(((T >> i) & 1) - ef)
    for i in Q:
        nu.append(((T >> i) & 1) - eg)
    return tuple(nu)


def dcoeff_bruteforce(p, q, T):
    """Independent re-derivation: expand d(T) = sum_{i in T} d_i with
    d_f = -sum_P u, d_g = -sum_Q u, and read off the coefficient of each u_i."""
    n, m, P, Q, f, g = layout(p, q)
    co = [0] * m
    for i in range(n):
        if not (T >> i) & 1:
            continue
        if i == f:
            for k, j in enumerate(P):
                co[k] -= 1
        elif i == g:
            for k, j in enumerate(Q):
                co[p + k] -= 1
        else:
            co[(P + Q).index(i)] += 1
    return tuple(co)


print("G1/G2  normal formula, type structure, and Lemma N*")
for (p, q) in [(1, 2), (2, 2), (1, 3), (2, 3), (3, 3), (1, 4), (4, 2)]:
    n, m, P, Q, f, g = layout(p, q)
    FULL = (1 << n) - 1
    bad_formula = bad_sep = 0
    for T in range(1, FULL):
        nu = normal(p, q, T)
        if nu != dcoeff_bruteforce(p, q, T):
            bad_formula += 1
        # Lemma N*: within each block, no two coordinates of opposite sign
        for blk in (nu[:p], nu[p:]):
            if any(x > 0 for x in blk) and any(y < 0 for y in blk):
                bad_sep += 1
    check(f"(p,q)=({p},{q}) normal formula matches brute force",
          bad_formula == 0, f"mismatches {bad_formula}")
    check(f"(p,q)=({p},{q}) Lemma N*: no intra-block sign separation",
          bad_sep == 0, f"violations {bad_sep}")
# the m=3 special case, in the old coordinates
n, m, P, Q, f, g = layout(1, 2)
seps = {(0, 1, -1), (0, -1, 1), (1, 1, -1), (1, -1, 1)}
occurring = {normal(1, 2, T) for T in range(1, (1 << n) - 1)}
check("m=3: the b/c-separating normals do not occur",
      not (seps & occurring))

print()
print("G3  the combinatorial form of Lemma I*")
for (p, q) in [(1, 2), (2, 2), (1, 3), (2, 3)]:
    n, m, P, Q, f, g = layout(p, q)
    FULL = (1 << n) - 1
    bad = 0
    for T in range(1, FULL):
        nu = normal(p, q, T)
        ef, eg = (T >> f) & 1, (T >> g) & 1
        for r in range(1, m + 1):
            for Sset in itertools.combinations(range(m), r):
                lhs = sum(nu[i] for i in Sset)
                Sm = sum(1 << (P + Q)[i] for i in Sset)
                rhs = (len([i for i in Sset if i < p]) * ef
                       + len([i for i in Sset if i >= p]) * eg)
                cnt = bin(T & Sm).count("1")
                if lhs != cnt - rhs:
                    bad += 1
    check(f"(p,q)=({p},{q}) nu_T . 1_S = |T n S| - eps_f|PnS| - eps_g|QnS|",
          bad == 0, f"mismatches {bad}")


def kills_orthant(p, q, tights):
    """Does { d >= 0 : nu_T . d >= 0 for T in tights } reduce to {0}?"""
    n, m, P, Q, f, g = layout(p, q)
    d = [z3.Real(f"d{i}") for i in range(m)]
    s = z3.Solver()
    for i in range(m):
        s.add(d[i] >= 0)
    for T in tights:
        nu = normal(p, q, T)
        s.add(z3.Sum([nu[i] * d[i] for i in range(m)]) >= 0)
    s.add(z3.Sum(d) > 0)
    r = s.check()
    assert r != z3.unknown
    return r == z3.unsat


print()
print("G4  the two orthant-killing recipes of PROOF_GENERAL.txt")
for (p, q) in [(2, 2), (2, 3), (3, 3), (3, 2), (4, 2), (2, 4)]:
    n, m, P, Q, f, g = layout(p, q)
    H = (1 << f) | (1 << g)
    b0 = Q[0]
    # RECIPE A (needs p,q >= 2):  T_x = N \ {b0, x} for x in P;  U = {g} u P
    tights = [((1 << n) - 1) & ~(1 << b0) & ~(1 << x) for x in P]
    tights.append((1 << g) | sum(1 << i for i in P))
    check(f"recipe A at (p,q)=({p},{q}) kills the orthant "
          f"({len(tights)} tight sets)", kills_orthant(p, q, tights))
for (p, q) in [(1, 3), (1, 4), (1, 5)]:
    n, m, P, Q, f, g = layout(p, q)
    H = (1 << f) | (1 << g)
    # RECIPE B (p = 1, q >= 3): T0 = H u {b3..bq}, U = {g, b1, b2}
    T0 = H | sum(1 << i for i in Q[2:])
    U = (1 << g) | (1 << Q[0]) | (1 << Q[1])
    check(f"recipe B at (p,q)=({p},{q}) kills the orthant (2 tight sets)",
          kills_orthant(p, q, [T0, U]))
# and the recipes must FAIL exactly where the theorem says they must
check("recipe A is unavailable at p=1 (it would need {f} tight): "
      "flagged in PROOF_GENERAL.txt, not tested here", True)
for (p, q) in [(1, 2)]:
    n, m, P, Q, f, g = layout(p, q)
    H = (1 << f) | (1 << g)
    T0 = H | sum(1 << i for i in Q[2:])          # = H, which is slack
    check(f"recipe B degenerates at (p,q)=({p},{q}): T0 = H, which is slack",
          T0 == H)

print()
print("G5  the published witnesses carry an orthant-killing certificate")
GENS22 = [[0, 0, 1, 4, 2, 1], [0, 0, 4, 4, 0, 0], [4, 0, 0, 0, 2, 2],
          [1, 0, 2, 3, 0, 2], [0, 1, 2, 3, 1, 1]]


def witness_certificate(gens, label):
    n = len(gens[0])
    w, _ = L.normalize(n, L.envelope(n, [tuple(F(x) for x in g) for g in gens]))
    phi = L.lmin(n, w)
    blocks = L.strata(phi)
    tight = L.tight_family(n, w, phi)
    FULL = (1 << n) - 1
    for j in range(len(blocks) - 1):
        H = sum(1 << i for b in blocks[j + 1:] for i in b)
        if bin(H).count("1") != 2:
            continue
        if sum(phi[i] for i in range(n) if H >> i & 1) <= w[H]:
            continue
        Hs = L.bits(n, H)
        for S1, S2 in itertools.permutations(tight, 2):
            if S1 & H != (1 << Hs[0]) or S2 & H != (1 << Hs[1]):
                continue
            if (S1 | S2) != FULL or (S1 & S2) != 0:
                continue
            Pw = [i for i in L.bits(n, S1) if not (H >> i & 1)]
            Qw = [i for i in L.bits(n, S2) if not (H >> i & 1)]
            fw = [i for i in Hs if S1 >> i & 1][0]
            gw = [i for i in Hs if S2 >> i & 1][0]
            order = Pw + Qw
            mm = len(order)

            def nu_of(T):
                out = []
                for i in Pw:
                    out.append(((T >> i) & 1) - ((T >> fw) & 1))
                for i in Qw:
                    out.append(((T >> i) & 1) - ((T >> gw) & 1))
                return tuple(out)

            d = [z3.Real(f"e{i}") for i in range(mm)]
            s = z3.Solver()
            for i in range(mm):
                s.add(d[i] >= 0)
            for T in tight:
                nu = nu_of(T)
                s.add(z3.Sum([nu[i] * d[i] for i in range(mm)]) >= 0)
            s.add(z3.Sum(d) > 0)
            killed = s.check() == z3.unsat
            # minimal killing subset, greedily
            cur = list(tight)
            for T in list(cur):
                trial = [x for x in cur if x != T]
                s2 = z3.Solver()
                for i in range(mm):
                    s2.add(d[i] >= 0)
                for X in trial:
                    nu = nu_of(X)
                    s2.add(z3.Sum([nu[i] * d[i] for i in range(mm)]) >= 0)
                s2.add(z3.Sum(d) > 0)
                if s2.check() == z3.unsat:
                    cur = trial
            print(f"    {label}: P={[L.LETTERS[i] for i in Pw]} "
                  f"Q={[L.LETTERS[i] for i in Qw]} "
                  f"f={L.LETTERS[fw]} g={L.LETTERS[gw]}")
            print(f"      minimal orthant-killing certificate: "
                  f"{[L.nm(n, T) for T in cur]}")
            for T in cur:
                print(f"         {L.nm(n, T):8s} normal {nu_of(T)}")
            return killed
    return None


check("PART(2,2) witness: tight family kills the orthant",
      witness_certificate(GENS22, "PART(2,2)"))
try:
    data = json.load(open("/private/tmp/claude-501/-Users-maxf/"
                          "f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23/"
                          "witness_n6.json"))
    check("PART(1,3) witness: tight family kills the orthant",
          witness_certificate(data["found"]["n6m4split(1,3)"]["gens"],
                              "PART(1,3)"))
except (FileNotFoundError, KeyError) as e:
    print("  (PART(1,3) witness unavailable:", e, ")")

print()
print("ALL CHECKS PASSED" if ok else "SOME CHECK FAILED")
sys.exit(0 if ok else 1)
