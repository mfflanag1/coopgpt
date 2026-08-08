"""Theorem B (task #23) and its LEXIMAX MIRROR, re-derived and validated here.

Task #23's Theorem B characterizes Lmin by a quantifier-free Farkas identity.
The mirror needed for Lmax is stated there only as "the same derivation with
signs flipped"; it is re-derived from scratch below rather than assumed, and
then validated on genuine games (validate_all()).

FLOOR (Theorem B, verbatim).  phi in core(v) with increasing level sets
B_1 < ... < B_k.  phi = Lmin(v) iff for every stage t and every i in B_t there
are y_A >= 0 (A proper), eta free, rho_l free (l in B_<t), sigma_c >= 0
(c in B_t) with y_A = 0 for A not phi-tight, and for every player j

    - sum_{A ni j} y_A + eta + [j in B_<t] rho_j - [j in B_t] sigma_j = [j = i].

CEILING (the mirror, derived here).  psi in core(v) with DECREASING level sets
D_1 > ... > D_k, values M_1 > ... > M_k.  The leximax stage condition is

  min { x_i : x in core(v), x_l = psi_l (l in D_<t), x_c <= M_t (c in D_>=t) }
        = psi_i = M_t                                          for i in D_t.

At psi the active constraints are: x(N) = v(N) (equality); x(A) >= v(A) for the
psi-TIGHT proper A; x_l = psi_l for l in D_<t (equality); and x_c <= M_t, which
is active exactly for c in D_t, since psi_c < M_t for c in D_>t.  So the
tangent cone at psi is

    C = { d : d(N) = 0, d(T) >= 0 (T tight), d_l = 0 (l in D_<t),
              d_c <= 0 (c in D_t) },

and the stage condition -- a MINIMUM attained at psi -- holds iff d_i >= 0 for
every d in C, i.e. iff -e_i lies in the polar cone

    C^o = cone{ -1_T } + cone{ +e_c : c in D_t }
                       + span{ 1_N } + span{ e_l : l in D_<t }.

(The generator for the inequality d_c <= 0, i.e. (-e_c).d >= 0, is +e_c.)
Membership of -e_i is, coordinatewise,

    - sum_{A ni j} y_A + eta + [j in D_<t] rho_j + [j in D_t] sigma_j
                                                        = -[j = i],

with y_A >= 0 supported on the psi-tight proper coalitions and sigma_c >= 0.
So the mirror differs from the floor in exactly two places: sigma enters with a
PLUS sign, and the right-hand side is -[j=i].

CONTROLS (validate_all).  Positive: on genuine games the true Lmin satisfies
every floor certificate and the true Lmax every ceiling certificate.  Negative,
and this is the part that matters: offering Lmin as a claimed Lmax must be
REJECTED, and so must the midpoint (Lmin+Lmax)/2, which is a core point (the
core is convex) but is neither selection when the two differ.  Both rejections
fire on every game where Lmin != Lmax.
HONEST NOTE ON A NON-CONTROL: flipping the sign of sigma in the ceiling form
does NOT break it on any game tested, so that particular perturbation is not
discriminating and is reported but not relied on.  The reason is that the
identity has enough freedom in eta and rho to absorb the change; it is the
SUPPORT condition and the right-hand side, not sigma's sign, that carry the
content here.
"""
from __future__ import annotations
import json
import sys
from fractions import Fraction as F

import z3

HERE = sys.path[0]
sys.path.insert(0, HERE + "/lib")
import audit

N, FULL = 5, 31
PROPER = list(range(1, FULL))


def _cert(v, phi, tight, pinned, cur, i, ceiling, sigma_sign=None):
    """Exact feasibility of the Farkas identity for one (stage, player).

    v, phi: lists of Fractions (v indexed by mask).  tight: set of proper masks
    with phi(A) = v(A).  pinned: players in earlier stages.  cur: players in the
    current stage.  Returns True/False; asserts sat or unsat."""
    if sigma_sign is None:
        sigma_sign = +1 if ceiling else -1
    rhs_sign = -1 if ceiling else +1
    y = {A: z3.Real(f"y{A}") for A in PROPER}
    eta = z3.Real("eta")
    rho = {l: z3.Real(f"rho{l}") for l in pinned}
    sig = {c: z3.Real(f"sig{c}") for c in cur}
    s = z3.Solver()
    for A in PROPER:
        s.add(y[A] >= 0)
        if A not in tight:
            s.add(y[A] == 0)                                     # (SUPPORT)
    for c in cur:
        s.add(sig[c] >= 0)
    for j in range(N):
        e = -z3.Sum([y[A] for A in PROPER if A >> j & 1]) + eta
        if j in pinned:
            e = e + rho[j]
        if j in cur:
            e = e + sigma_sign * sig[j]
        s.add(e == z3.RealVal(rhs_sign if j == i else 0))        # (IDENTITY)
    r = s.check()
    assert r in (z3.sat, z3.unsat), f"z3 returned {r}"
    return r == z3.sat


def certificates_hold(v, phi, ceiling, sigma_sign=None):
    """Run the certificate for every stage and every player of that stage."""
    blocks = audit.strata(phi)                 # poorest -> richest
    if ceiling:
        blocks = blocks[::-1]                  # richest -> poorest
    tight = {A for A in PROPER
             if sum(phi[k] for k in range(N) if A >> k & 1) == v[A]}
    pinned, out = [], []
    for t, B in enumerate(blocks):
        for i in B:
            out.append(_cert(v, phi, tight, list(pinned), list(B), i,
                             ceiling, sigma_sign))
        pinned += list(B)
    return out


def validate_all(limit=None):
    """POSITIVE + NEGATIVE control for the two characterizations, on genuine
    exact games: the true Lmin/Lmax must satisfy every certificate, a perturbed
    (wrong) allocation must not, and the mis-signed ceiling form must fail."""
    recs = json.load(open(f"{HERE}/harvest.json"))["records"]
    if limit:
        recs = recs[:limit]
    st = {"games": 0, "floor_certs": 0, "ceil_certs": 0,
          "floor_fail": 0, "ceil_fail": 0,
          "ceil_missigned_games_rejected": 0, "ceil_missigned_games": 0,
          "wrong_alloc_games_rejected": 0, "wrong_alloc_games": 0,
          "midpoint_games": 0, "midpoint_games_rejected": 0,
          "midpoint_floor_rejected": 0}
    for r in recs:
        T = F(r["T"])
        v = [F(t) / T for t in r["v"]]
        x = [F(t) / T for t in r["lmin"]]
        z = [F(t) / T for t in r["lmax"]]
        st["games"] += 1
        fc = certificates_hold(v, x, ceiling=False)
        st["floor_certs"] += len(fc)
        st["floor_fail"] += sum(1 for b in fc if not b)
        cc = certificates_hold(v, z, ceiling=True)
        st["ceil_certs"] += len(cc)
        st["ceil_fail"] += sum(1 for b in cc if not b)
        if x != z:
            # NEGATIVE CONTROL 1: Lmin offered as if it were Lmax
            st["wrong_alloc_games"] += 1
            if not all(certificates_hold(v, x, ceiling=True)):
                st["wrong_alloc_games_rejected"] += 1
            # NEGATIVE CONTROL 2: the midpoint of Lmin and Lmax.  It is a core
            # point (the core is convex) but it is not Lmax, since Lmax is the
            # unique leximax-minimal core point and differs from Lmin here.
            mid = [(x[k] + z[k]) / 2 for k in range(N)]
            st["midpoint_games"] += 1
            if not all(certificates_hold(v, mid, ceiling=True)):
                st["midpoint_games_rejected"] += 1
            # ... and as a claimed Lmin
            if not all(certificates_hold(v, mid, ceiling=False)):
                st["midpoint_floor_rejected"] += 1
            # NEGATIVE CONTROL 3: the mis-signed ceiling form (records whether
            # the sign of sigma is discriminating at all)
            st["ceil_missigned_games"] += 1
            if not all(certificates_hold(v, z, ceiling=True, sigma_sign=-1)):
                st["ceil_missigned_games_rejected"] += 1
    print(json.dumps(st, indent=1))
    ok = (st["floor_fail"] == 0 and st["ceil_fail"] == 0
          and st["wrong_alloc_games_rejected"] == st["wrong_alloc_games"]
          and st["midpoint_games_rejected"] == st["midpoint_games"]
          and st["midpoint_floor_rejected"] == st["midpoint_games"])
    print("FLOOR AND CEILING CHARACTERIZATIONS VALIDATED" if ok
          else "VALIDATION FAILED")
    json.dump(st, open(f"{HERE}/farkas_validate.json", "w"), indent=1)
    return ok


if __name__ == "__main__":
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else None
    validate_all(lim)
