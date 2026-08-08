"""IS THE FRONTIER EQUALITY FORCED AT m = 4?

The threshold sharpness recorded in PROOF_M3.txt was an OBSERVATION about one
harvested witness: at PART(1,3) the crossing budget

        phi_f  <=  phi(Q \ T)        for a phi-tight T containing H, a not in T

held with EQUALITY (7/4 <= 7/4).  If that equality were forced, the sharpness
of the threshold would be a theorem, not a coincidence.  This script decides
it.

SETUP.  PART(1,3): P = {a}, Q = {b,c,d}, H = {f,g}, n = 6.  For a phi-tight
T containing H with a not in T, (KEY) of PROOF_GENERAL.txt forces
|Q \ T| >= 2; and T = H itself is slack, so |Q \ T| = 3 is out too.  Hence the
only candidates are

        T_j = H u {j},      j in Q,        with  phi_f <= phi(Q \ {j}).

Three questions, each decided over ALL 60 stratifications with the full
decisive encoding (exactness by attaining core points, leximin by Farkas):

  Q1  MUST such a T_j exist at all?          -- forbid every tight T over H
                                                that omits a, and ask SAT.
  Q2  CONTROL.  With T_j merely tight (no equality imposed), is it SAT?
                A no here would make Q3 vacuous.
  Q3  Can the budget be STRICT?              -- impose T_j tight AND
                                                phi_f < phi(Q \ {j}), ask SAT.

UNSAT on Q3 across all stratifications and all j = the equality is forced.

Usage: python3 frontier_forced.py
"""
from __future__ import annotations

import sys
import time

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L
import decisive as D
import z3

p, q = 1, 3
n = p + q + 2
m = p + q
P = list(range(p))
Q = list(range(p, m))
f, g = n - 2, n - 1
H = (1 << f) | (1 << g)
a = P[0]
FULL = (1 << n) - 1


def tot(vec, S):
    return z3.Sum([vec[i] for i in range(n) if S >> i & 1])


def over_H_missing_a():
    """Proper phi-tight candidates T with H in T and a not in T."""
    out = []
    for S in range(0, 1 << q):
        T = H | sum(1 << Q[k] for k in range(q) if S >> k & 1)
        if T != FULL and T != H:
            out.append(T)
    return out


CAND = over_H_missing_a()
print(f"candidates T over H omitting a: {[L.nm(n, T) for T in CAND]}")
print(f"(KEY) admits only those with |Q \\ T| >= 2, i.e. "
      f"{[L.nm(n, T) for T in CAND if bin(T & ~H).count('1') <= q - 2]}")
print()

strats = D.stratifications(n, p, q)
summary = {"Q1": {"sat": 0, "unsat": 0}, "Q2": {"sat": 0, "unsat": 0},
           "Q3": {"sat": 0, "unsat": 0}}
sat_models = []

t_start = time.time()
for idx, (blocks, tag) in enumerate(strats):
    # ---- Q1: no tight T over H omitting a
    s, v, phi, cfg = D.build(n, p, q, blocks)
    s.set("timeout", 900 * 1000)
    for T in CAND:
        s.add(tot(phi, T) > v[T])
    r = s.check()
    assert r != z3.unknown, "unknown"
    summary["Q1"]["sat" if r == z3.sat else "unsat"] += 1
    if r == z3.sat:
        aud = D.audit_model(n, p, q, s.model(), v)
        sat_models.append(("Q1", tag, aud))

    # ---- Q2 (control) and Q3, per choice of j
    for j in Q:
        Tj = H | (1 << j)
        rest = [k for k in Q if k != j]
        # Q2 control: Tj tight, no equality imposed
        s2, v2, phi2, _ = D.build(n, p, q, blocks)
        s2.set("timeout", 900 * 1000)
        s2.add(tot(phi2, Tj) == v2[Tj])
        r2 = s2.check()
        assert r2 != z3.unknown
        summary["Q2"]["sat" if r2 == z3.sat else "unsat"] += 1
        if r2 == z3.sat:
            aud = D.audit_model(n, p, q, s2.model(), v2)
            if aud["verdict"] != "GENUINE WITNESS":
                sat_models.append(("Q2-BADAUDIT", tag, aud))
        # Q3: Tj tight AND the budget strict
        s3, v3, phi3, _ = D.build(n, p, q, blocks)
        s3.set("timeout", 900 * 1000)
        s3.add(tot(phi3, Tj) == v3[Tj])
        s3.add(phi3[f] < z3.Sum([phi3[k] for k in rest]))
        r3 = s3.check()
        assert r3 != z3.unknown
        summary["Q3"]["sat" if r3 == z3.sat else "unsat"] += 1
        if r3 == z3.sat:
            aud = D.audit_model(n, p, q, s3.model(), v3)
            sat_models.append(("Q3", f"{tag} j={L.LETTERS[j]}", aud))
    if idx % 10 == 0:
        print(f"  ... {idx+1}/{len(strats)} stratifications, "
              f"{round(time.time()-t_start,1)}s", flush=True)

print()
print(f"Q1  no tight T over H omitting a      : "
      f"sat={summary['Q1']['sat']} unsat={summary['Q1']['unsat']}")
print(f"Q2  control, T_j tight (no equality)  : "
      f"sat={summary['Q2']['sat']} unsat={summary['Q2']['unsat']}")
print(f"Q3  T_j tight AND budget STRICT       : "
      f"sat={summary['Q3']['sat']} unsat={summary['Q3']['unsat']}")
print()
for kind, tag, aud in sat_models[:12]:
    print(f"  {kind:12s} {tag:34s} {aud['verdict']}")
    if aud.get("lmin"):
        print(f"       Lmin = {aud['lmin']}")
print()
if summary["Q3"]["sat"] == 0 and summary["Q2"]["sat"] > 0:
    print("VERDICT: the crossing budget is FORCED TIGHT at m = 4 "
          "(threshold sharpness is a theorem).")
elif summary["Q3"]["sat"] > 0:
    print("VERDICT: the budget can be STRICT -- the observed equality was "
          "a property of that witness, not forced.")
else:
    print("VERDICT: inconclusive -- the control Q2 found nothing, so Q3 is "
          "vacuous.")
