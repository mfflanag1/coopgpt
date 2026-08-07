"""Decide, from the catalogue's own definitions, whether a set system is
semi-balanced / minimal / indecomposable.  Exact rational feasibility via z3.

  semi-balanced : some semi-conic combination (at most one negative
                  coefficient) with ALL coefficients nonzero is constant;
  minimal       : no proper nonempty subsystem is semi-balanced;
  decomposable  : some nonempty proper E not in S admits sigma with
                  sigma_E < 0, sigma_S >= 0 on S, sum constant.
"""
from __future__ import annotations

import itertools
import z3


def _const_combo(n, sets, signs):
    """signs[k] in {+1,-1,0}: +1 means coefficient>0, -1 means <0,
    0 means >=0.  True if such a constant combination exists."""
    lam = [z3.Real(f"l{k}") for k in range(len(sets))]
    r = z3.Real("r")
    s = z3.Solver()
    for k, sg in enumerate(signs):
        if sg > 0:
            s.add(lam[k] >= 1)
        elif sg < 0:
            s.add(lam[k] <= -1)
        else:
            s.add(lam[k] >= 0)
    for i in range(n):
        s.add(z3.Sum([lam[k] for k, S in enumerate(sets) if S >> i & 1]) == r)
    return s.check() == z3.sat


def is_semi_balanced(n, sets):
    sets = list(sets)
    k = len(sets)
    for neg in [None] + list(range(k)):
        signs = [1] * k
        if neg is not None:
            signs[neg] = -1
        if _const_combo(n, sets, signs):
            return True
    return False


def is_minimal(n, sets):
    sets = list(sets)
    for size in range(1, len(sets)):
        for sub in itertools.combinations(sets, size):
            if is_semi_balanced(n, sub):
                return False, list(sub)
    return True, None


def is_indecomposable(n, sets):
    sets = list(sets)
    full = (1 << n) - 1
    for E in range(1, full):
        if E in sets:
            continue
        cand = sets + [E]
        signs = [0] * len(sets) + [-1]
        if _const_combo(n, cand, signs):
            return False, E
    return True, None


def classify(n, sets):
    mn, wit = is_minimal(n, sets)
    if not mn:
        return "not minimal", wit
    ind, E = is_indecomposable(n, sets)
    if not ind:
        return "minimal but decomposable", E
    return "indecomposable min-semi-balanced", None


if __name__ == "__main__":
    import catalogue
    # Validation: every catalogued row must classify as indecomposable.
    for n in (4, 5, 6):
        letters, rows = catalogue.load(n)
        bad = []
        for k, row in enumerate(rows, 1):
            verdict, _ = classify(n, list(row["lam"]))
            if verdict != "indecomposable min-semi-balanced":
                bad.append((k, verdict))
        print(f"n={n}: {len(rows)} catalogued rows, misclassified = {bad}")
