"""Independent exact replay of the supplied family; no campaign imports.

Fraction checks are fail-closed and remain active under python -O.
Optional --smt runs three exact raw-core queries for q=4 using Z3.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def instance(q):
    require(isinstance(q, int) and q >= 1, "q domain")
    labels = [("L", 0)] + [(kind, s) for s in range(1, q + 1) for kind in ("L", "R", "O")]
    A, B, C = {}, {}, {}
    for s in range(q + 1):
        C[(("L", s), ("L", s))] = 1
    for s in range(1, q + 1):
        l, r, o, prev = ("L", s), ("R", s), ("O", s), ("L", s - 1)
        C[(r, r)] = 1
        A[(o, o)] = B[(o, o)] = 2
        A[(o, r)] = B[(o, l)] = 2
        C[(r, l)] = C[(prev, o)] = 1
    def worth(t):
        i, j, k = t
        return A.get((i, j), 0) + B.get((i, k), 0) + C.get((j, k), 0)
    tau = F(1, 3 * (q + 1))
    floor, ideal = {}, {}
    for kind, s in labels:
        if kind == "L":
            u, y = (tau, 1 - (3*s+2)*tau, (3*s+1)*tau), (0, 0, 1)
        elif kind == "R":
            u, y = (tau, 1 - 2*tau, tau), (0, 1, 0)
        else:
            u, y = (4 - (3*s-1)*tau, tau, (3*s-2)*tau), (3, 0, 1)
        for sector in range(3):
            floor[(sector, (kind, s))] = F(u[sector])
            ideal[(sector, (kind, s))] = F(y[sector])
    matching = [(t, t, t) for t in labels]
    critical = []
    for s in range(1, q + 1):
        critical += [(("O", s), ("R", s), ("L", s)),
                     (("L", s-1), ("L", s-1), ("O", s))]
    return labels, (A, B, C), worth, tau, floor, ideal, matching, critical


def check(q):
    labels, matrices, worth, tau, u, y, matching, critical = instance(q)
    players = {(s, t) for s in range(3) for t in labels}
    require(len(labels) == 3*q+1 and len(players) == 9*q+3, "player count")
    require(sum(len(P) for P in matrices) == 8*q+1, "pair-entry count")
    require(all(v in (1, 2) for P in matrices for v in P.values()), "pair values")
    T = sum(worth(t) for t in matching)
    require(T == 6*q+1, "diagonal value")
    reports = {}
    for name, p, bound in [("floor", u, tau), ("ideal", y, F(0))]:
        require(set(p) == players and min(p.values()) >= bound, "cover coordinates")
        require(sum(p.values()) == T, "cover total")
        slacks = []
        for t in product(labels, repeat=3):
            slack = sum(p[(s, t[s])] for s in range(3)) - worth(t)
            require(slack >= 0, f"uncovered {name} triple: q={q}, {t}")
            slacks.append(slack)
        require(all(sum(p[(s, t[s])] for s in range(3)) == worth(t) for t in matching), "matching equality")
        reports[name] = {"checked_triples": len(slacks), "minimum_slack": str(min(slacks)), "total": str(sum(p.values()))}
    used = [((s, t[s])) for t in critical for s in range(3)]
    require(len(used) == len(set(used)) == 6*q, "critical collection not disjoint")
    require(sum(worth(t) for t in critical) == 6*q, "critical value")
    unmatched = players - set(used)
    expected = {(2, ("L", 0)), (0, ("L", q)), (1, ("L", q))}
    for s in range(1, q + 1):
        expected |= {(0, ("R", s)), (1, ("O", s)), (2, ("R", s))}
    require(unmatched == expected and len(unmatched) == 3*q+3, "unmatched player identity")
    require(all(u[i] == tau for i in unmatched) and sum(u[i] for i in unmatched) == 1, "critical budget saturation")
    require(all(sum(u[(s, t[s])] for s in range(3)) == worth(t) for t in critical), "critical equality")
    target = (2, ("L", 0))
    require(u[target] == tau and y[target] == 1 and worth((("L", 0),)*3) == 1, "target certificate")
    return {"q": q, "players": len(players), "T": T, "tau": str(tau), "ideal": "1", "ratio": str(tau), "unmatched": len(unmatched), "covers": reports}


def smt_check(q=4):
    import z3
    labels, matrices, worth, tau, u, y, matching, critical = instance(q)
    p = {(s, t): z3.Real(f"p_{s}_{t[0]}{t[1]}") for s in range(3) for t in labels}
    T = sum(worth(t) for t in matching)
    constraints = [v >= 0 for v in p.values()] + [z3.Sum(list(p.values())) == T]
    constraints += [z3.Sum([p[(s, t[s])] for s in range(3)]) >= worth(t) for t in product(labels, repeat=3)]
    t = z3.Q(tau.numerator, tau.denominator)
    target = p[(2, ("L", 0))]
    cases = {
        "larger_common_floor": [v > t for v in p.values()],
        "target_above_tau_on_whole_first_face": [v >= t for v in p.values()] + [target > t],
        "target_ideal_above_one": [target > 1],
    }
    outcomes = {}
    for name, extra in cases.items():
        solver = z3.Solver(); solver.set(timeout=60000)
        solver.add(constraints + extra)
        result = solver.check()
        require(result == z3.unsat, f"SMT query {name} returned {result}")
        outcomes[name] = str(result)
    return {"q": q, "z3_version": z3.get_version_string(), "queries_use_only_raw_full_core": True, "outcomes": outcomes}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--smt", action="store_true")
    args = parser.parse_args()
    result = {"status": "PASS", "method": "independent Fraction construction and every raw triple, plus a disjoint-partial-matching certificate", "checks": [check(q) for q in range(1, 5)]}
    if args.smt:
        result["smt"] = smt_check()
    (ROOT/"FAMILY_AUDIT.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))
