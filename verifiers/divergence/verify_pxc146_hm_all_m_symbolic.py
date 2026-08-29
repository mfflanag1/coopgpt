#!/usr/bin/env python3
"""Symbolic stdlib audit of the all-m H_m selector theorem (PXC146).

The proof is conventional and appears in the paper.  This script is a
transcription audit: affine functions of m are represented exactly as
coefficient/constant pairs, and every critical lower-envelope value and
coalition-incidence identity is checked coefficient by coefficient.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


class A(tuple):
    """Affine function a*m+b."""
    def __new__(cls, a=0, b=0): return tuple.__new__(cls, (F(a), F(b)))
    def __add__(self, other):
        other = aff(other); return A(self[0] + other[0], self[1] + other[1])
    __radd__ = __add__
    def __neg__(self): return A(-self[0], -self[1])
    def __sub__(self, other): return self + (-aff(other))
    def __rsub__(self, other): return aff(other) - self
    def __mul__(self, scalar): return A(self[0] * F(scalar), self[1] * F(scalar))
    __rmul__ = __mul__
    def at(self, m): return self[0] * m + self[1]
    def text(self):
        a, b = self
        if not a: return str(b)
        if not b: return "m" if a == 1 else f"{a}*m"
        return f"{a}*m+{b}"


def aff(value): return value if isinstance(value, A) else A(0, value)


ROLES = ("U", "b", "c", "d", "e", "f", "g")
U, B, C, D, E, F_, G = range(7)
T = A(9, 4)

# A role vector records the coefficient of y(U) followed by the six labelled
# coordinates.  Thus it is independent of the number m of players in U.
def row(*roles): return tuple(F(int(i in roles)) for i in range(7))
EFF = row(*range(7))
R1 = row(U, C, D, E)          # U c d e
R2 = row(U, C, D, F_)         # U c d f
R3 = row(B, C, D, E, F_)      # b c d e f
R4 = row(C, D, G)             # c d g
R5 = row(B, E, G)             # b e g
R6 = row(B, F_, G)            # b f g
R7 = row(C, E, F_, G)         # c e f g
Q1 = row(C, D, F_)            # c d f

VALUES = {
    "R1_Ucde": A(6, 2), "R2_Ucdf": A(6, 2),
    "R3_bcdef": A(8, 3), "R4_cdg": A(5, 2),
    "R5_beg": A(3, 2), "R6_bfg": A(3, 2),
    "R7_cefg": A(5, 3), "Q1_cdf": A(5, 2),
}
ROWS = {"R1_Ucde": R1, "R2_Ucdf": R2, "R3_bcdef": R3,
        "R4_cdg": R4, "R5_beg": R5, "R6_bfg": R6,
        "R7_cefg": R7, "Q1_cdf": Q1}

# Per-player entries, with U denoting one coordinate in the U block.
X = (A(0, 1), A(3), A(5), A(0, 1), A(0, 1), A(0, 1), A(0, 1))
GB = (A(), A(), A(), A(4, 1), A(2, 1), A(2, 1), A(1, 1))
GC = (A(), A(3, 2), A(6, 2), A(), A(), A(), A())
GD = (A(), A(), A(F(7, 2), F(1, 2)), A(F(1, 2), F(1, 2)),
      A(2, 1), A(2, 1), A(1, 1))
GENS = (X, GB, GC, GD)


def total(point): return point[U] * 1 + point[B] + point[C] + point[D] + point[E] + point[F_] + point[G]


def coalition(point, incidence):
    # U in a critical row always means all m U-players, so its contribution
    # is m times the per-U entry.  Only X has a nonzero U entry.
    ans = A()
    for i, bit in enumerate(incidence):
        if bit:
            ans += A(point[U][0], 0) if i == U else point[i]
            if i == U and point[U][1]: ans += A(point[U][1], 0)
    return ans


def vadd(*vectors): return tuple(sum((v[i] for v in vectors), F(0)) for i in range(7))
def vscale(c, vector): return tuple(F(c) * q for q in vector)
def vsub(a, *bs): return vadd(a, *(vscale(-1, b) for b in bs))


def padd(*polys):
    width=max(map(len,polys)); return tuple(sum((p[i] if i<len(p) else F(0) for p in polys),F(0)) for i in range(width))


def pmul(a,b):
    out=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): out[i+j]+=x*y
    while len(out)>1 and out[-1]==0: out.pop()
    return tuple(out)


def apoly(a): return (a[1],a[0])


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path); args = parser.parse_args()

    # Totals: U contributes m copies.  Audit directly rather than through the
    # compressed helper above.
    for point in GENS:
        got = A(point[U][0], 0) + A(point[U][1], 0)
        got += sum(point[1:], A())
        assert got == T, (point, got)

    lower_envelope = {}
    for name, incidence in ROWS.items():
        sums = [coalition(point, incidence) for point in GENS]
        want = VALUES[name]
        # Each affine difference is nonnegative for every integer m>=1.
        for delta in (value - want for value in sums):
            assert delta.at(1) >= 0 and delta[0] >= 0, (name, delta)
        assert want in sums, (name, sums)
        lower_envelope[name] = {"value": want.text(), "generator_sums": [q.text() for q in sums]}

    identities = {
        "floor_U_partition": vsub(EFF, Q1, R5),
        "floor_g": vsub(EFF, R3),
        "floor_e": vsub(vscale(2, EFF), R3, R4, R6),
        "floor_f": vsub(vscale(2, EFF), R3, R4, R5),
        "floor_d": vsub(vscale(4, EFF), vscale(2, R3), R4, R5, R6, R7),
        "stage_b": vsub(EFF, R4),
        "ceiling_e": vsub(vadd(R1, R3, R4), EFF),
        "ceiling_f": vsub(vadd(R2, R3, R4), EFF),
        "stage_b_lower": vsub(vadd(R1, R3, R5), EFF),
    }
    expected = {
        "floor_U_partition": row(U),
        "floor_g": row(U, G),
        "floor_e": (F(2), 0, 0, 0, 1, 0, 0),
        "floor_f": (F(2), 0, 0, 0, 0, 1, 0),
        "floor_d": (F(4), 0, 0, 1, 0, 0, 0),
        "stage_b": row(U, B, E, F_),
        "ceiling_e": (0, 0, 2, 2, 1, 0, 0),
        "ceiling_f": (0, 0, 2, 2, 0, 1, 0),
        "stage_b_lower": (0, 1, 1, 1, 2, 0, 0),
    }
    assert identities == expected

    # Check every right-hand side used in the hand proof.
    rhs = {
        "U_upper": T - VALUES["Q1_cdf"] - VALUES["R5_beg"],
        "U_plus_g_upper": T - VALUES["R3_bcdef"],
        "2U_plus_e_upper": 2*T-VALUES["R3_bcdef"]-VALUES["R4_cdg"]-VALUES["R6_bfg"],
        "2U_plus_f_upper": 2*T-VALUES["R3_bcdef"]-VALUES["R4_cdg"]-VALUES["R5_beg"],
        "4U_plus_d_upper": 4*T-2*VALUES["R3_bcdef"]-VALUES["R4_cdg"]-VALUES["R5_beg"]-VALUES["R6_bfg"]-VALUES["R7_cefg"],
        "top_five_load": VALUES["R1_Ucde"]+VALUES["R3_bcdef"]+VALUES["R4_cdg"]-T,
        "b_lower_load": VALUES["R1_Ucde"]+VALUES["R3_bcdef"]+VALUES["R5_beg"]-T,
    }
    expected_rhs = {"U_upper": A(1), "U_plus_g_upper": A(1,1),
                    "2U_plus_e_upper": A(2,1), "2U_plus_f_upper": A(2,1),
                    "4U_plus_d_upper": A(4,1), "top_five_load": A(10,3),
                    "b_lower_load": A(8,3)}
    assert rhs == expected_rhs

    # z is a positive convex combination of X, B and D.  Clear the common
    # denominator 5m(7m+1) and check every resulting polynomial identity.
    den=(F(0),F(5),F(35))
    nx=(F(1),F(7))                         # 7m+1
    nb=(F(-1),F(2),F(15))                  # (3m+1)(5m-1)
    nd=(F(0),F(-4),F(20))                  # 4m(5m-1)
    assert padd(nx,nb,nd)==den
    z_numerators=(nx, pmul((0,3),(1,7)), pmul((0,3,10),(1,7)),
                  pmul((0,3,10),(1,7)), pmul((0,3,10),(1,7)),
                  pmul((0,3,10),(1,7)), pmul((0,4,5),(1,7)))
    for i in range(7):
        got=padd(pmul(nx,apoly(X[i])),pmul(nb,apoly(GB[i])),pmul(nd,apoly(GD[i])))
        assert got==z_numerators[i],(i,got,z_numerators[i])

    comparisons = []
    for m in range(1, 17):
        n=m+6
        rho=F(14*(5*m-1), 5*(9*m+4))
        gbest=F(2)-F(8*n,n*n-(n%2))
        comparisons.append({"m":m,"n":n,"rho":str(rho),"G_best":str(gbest),"difference":str(rho-gbest)})
        assert (rho > gbest) == (m <= 8)
    even_numerator=lambda m:10*m*m-93*m+82
    odd_numerator=lambda m:10*m**3-33*m*m-486*m+465
    assert all(even_numerator(m)<0 for m in (2,4,6,8))
    assert even_numerator(10)>0 and 20*10-93>0
    assert all(odd_numerator(m)<0 for m in (1,3,5,7))
    assert odd_numerator(9)>0 and 30*9*9-66*9-486>0 and 60*9-66>0

    payload = {
        "claim": "PXC146 symbolic all-m proof of the H_m selectors and distance",
        "domain": "every integer m>=1; n=m+6",
        "construction": {"total": T.text(), "roles": list(ROLES),
                         "generators": [[q.text() for q in point] for point in GENS]},
        "critical_lower_envelope_rows": lower_envelope,
        "incidence_identities": {k:list(map(str,v)) for k,v in identities.items()},
        "proof_rhs": {k:v.text() for k,v in rhs.items()},
        "selectors": {"Lmin":"(1^m;3m,5m;1,1,1,1)",
                      "Lmax":"((1/(5m))^m;3/5,((10m+3)/5)^4,(5m+4)/5)"},
        "Lmax_core_feasibility":"coefficientwise polynomial audit of the positive convex combination of X, B, D",
        "distance": {"rho":"14(5m-1)/(5(9m+4))", "overlap":"(10m+27)/5",
                     "limit_rho":"14/9"},
        "comparison": {"beats_balanced_G_exactly_for":"1<=m<=8 (7<=n<=14)",
                       "eventual_sign_gate":"even quadratic increasing positive from m=10; odd cubic increasing positive from m=9",
                       "table":comparisons},
        "scope": "symbolic transcription audit of the conventional proof; no sharp s(n) or novelty claim",
    }
    rendered=json.dumps(payload,indent=2)+"\n"
    if args.output: args.output.write_text(rendered)
    print(rendered,end="")


if __name__ == "__main__": main()
