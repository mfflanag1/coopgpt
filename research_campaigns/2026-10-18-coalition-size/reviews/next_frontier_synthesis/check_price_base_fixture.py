#!/usr/bin/env python3
"""Exact risk check on the sealed twelve-profile min3 fixture; no search."""
from collections import defaultdict
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
CAMP = HERE.parents[1]
SOURCE = CAMP / "reviews/three_portfolio_certificate.json"
BUNDLE = {"0": (0, 0, 0), "L": (1, 0, 1), "R": (0, 1, 1)}
OWNERS = tuple(range(3))
COALITIONS = tuple(C for k in range(1, 4) for C in combinations(OWNERS, k))
PROTECTED = tuple(C for C in COALITIONS if len(C) <= 2)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def ykey(p, i):
    return "y:" + "".join(p) + ":" + str(i)


def pkey(p, a):
    return "p:" + "".join(p) + ":" + str(a)


def bundle(p, C):
    return tuple(sum(BUNDLE[p[i]][a] for i in C) for a in range(3))


def worth(p, C):
    return min(bundle(p, C))


def legal(low, high, C):
    return (all(low[i] == high[i] for i in OWNERS if i not in C)
            and all(BUNDLE[high[i]][a] >= BUNDLE[low[i]][a]
                    for i in C for a in range(3)))


def add_row(proof, kind, coeff, rhs, weight=Q(1), equality=False):
    weight, rhs = Q(weight), Q(rhs)
    require(equality or weight >= 0, "negative inequality multiplier")
    proof.append({"kind": kind, "equality": equality, "weight": str(weight),
                  "rhs": str(rhs), "coeff": {k: str(Q(v)) for k, v in coeff.items() if v}})


def sum_proof(proof, expected_rhs):
    total = defaultdict(Q)
    rhs = Q(0)
    for row in proof:
        w = Q(row["weight"])
        require(row["equality"] or w >= 0, "bad multiplier sign")
        rhs += w * Q(row["rhs"])
        for key, val in row["coeff"].items():
            total[key] += w * Q(val)
    total = {k: v for k, v in total.items() if v}
    require(total == {"K": Q(6)}, "not every actual payment/price variable cancels")
    require(rhs == expected_rhs, "unexpected dual objective")
    return {"remaining_coefficients": {k: str(v) for k, v in total.items()},
            "rhs": str(rhs), "lower": str(rhs/6), "row_count": len(proof)}


def main():
    source_data = json.loads(SOURCE.read_text())
    profiles = sorted({tuple(t["profile"]) for row in source_data["rows"] for t in row["terms"]})
    lows = [p for p in profiles if "0" in p]
    highs = [p for p in profiles if "0" not in p]
    require(len(profiles) == 12 and len(lows) == len(highs) == 6, "fixture changed")
    require(all(sorted(p) == ["0", "L", "R"] for p in lows), "low profile mismatch")
    require(all(sorted(p) in (["L", "L", "R"], ["L", "R", "R"]) for p in highs),
            "high profile mismatch")
    require(all(worth(p, OWNERS) == 1 for p in profiles), "fixture production differs")
    require(all(all(0 <= c <= 1 for c in BUNDLE[t]) for p in profiles for t in p),
            "not in fixed unit boxes")
    edges = [(low, high, C) for low in profiles for high in profiles for C in PROTECTED
             if legal(low, high, C)]
    proper_edges = [(l, h, C) for l, h, C in edges if l != h]
    require(len(edges) == 108 and len(proper_edges) == 36, "comparison closure changed")
    require(sum(any(l[i] == h[i] for i in C) for l, h, C in proper_edges) == 24,
            "passive protected members omitted")

    pay = {name: {} for name in ("unrestricted", "price_base")}
    prices = {}
    for p in profiles:
        if p in lows:
            for name in pay:
                pay[name][p] = tuple(Q(0) if t == "0" else Q(1, 2) for t in p)
            prices[p] = (Q(1, 2), Q(1, 2), Q(0))
        else:
            majority = "L" if p.count("L") == 2 else "R"
            pay["unrestricted"][p] = tuple(Q(1, 4) if t == majority else Q(3, 4) for t in p)
            pay["price_base"][p] = tuple(Q(1, 4) if t == majority else Q(1) for t in p)
            prices[p] = (Q(0), Q(1), Q(0)) if majority == "L" else (Q(1), Q(0), Q(0))
    results = {}
    for name, K in (("unrestricted", Q(5, 4)), ("price_base", Q(3, 2))):
        for p in profiles:
            require(all(v >= 0 for v in pay[name][p]), "negative payment")
            require(sum(pay[name][p]) <= K*worth(p, OWNERS), "funding failure")
            for C in COALITIONS:
                require(sum(pay[name][p][i] for i in C) >= worth(p, C), "coverage failure")
            if name == "price_base":
                price = prices[p]
                require(all(v >= 0 for v in price) and sum(price) >= 1, "price infeasibility")
                require(sum(price[a]*bundle(p, OWNERS)[a] for a in range(3)) == 1,
                        "price not efficient")
                for i in OWNERS:
                    require(pay[name][p][i] >= sum(price[a]*BUNDLE[p[i]][a] for a in range(3)),
                            "price-base domination failure")
        for low, high, C in edges:
            delta = tuple(sum(BUNDLE[high[i]][a]-BUNDLE[low[i]][a] for i in C) for a in range(3))
            require(min(delta) == 0, "OUT differs from TCWM on this finite fixture")
            require(sum(pay[name][high][i]-pay[name][low][i] for i in C) >= min(delta),
                    "incentive failure")
        results[name] = {"upper": str(K), "coverage_rows": 84, "funding_rows": 12,
                         "nonnegative_payments": 36, "protected_rows_including_reflexive": len(edges)}

    unrestricted = []
    for row in source_data["rows"]:
        terms = row["terms"]
        coeff = defaultdict(Q)
        for t in terms:
            coeff[ykey(tuple(t["profile"]), t["owner"])] += Q(t["coefficient"])
        if "coverage" in row["kind"]:
            p = tuple(terms[0]["profile"])
            C = tuple(t["owner"] for t in terms)
            require(all(tuple(t["profile"]) == p and Q(t["coefficient"]) == 1 for t in terms),
                    "sealed coverage row shape")
            require(Q(row["rhs"]) == worth(p, C), "sealed coverage RHS")
        elif row["kind"] == "low_zero_owner_nonnegative":
            require(len(terms) == 1 and Q(terms[0]["coefficient"]) == 1 and Q(row["rhs"]) == 0,
                    "sealed nonnegative row shape")
        else:
            positive = [t for t in terms if Q(t["coefficient"]) == 1]
            negative = [t for t in terms if Q(t["coefficient"]) == -1]
            h, l = tuple(positive[0]["profile"]), tuple(negative[0]["profile"])
            C = tuple(sorted(t["owner"] for t in positive))
            require(tuple(sorted(t["owner"] for t in negative)) == C and (l, h, C) in edges,
                    "sealed transition not actual coalition row")
            require(all(tuple(t["profile"]) == h for t in positive)
                    and all(tuple(t["profile"]) == l for t in negative), "sealed endpoint mismatch")
        add_row(unrestricted, row["kind"], coeff, row["rhs"], Q(row["weight"]))

    restricted = []
    selected = 0
    for low, high, C in proper_edges:
        restorer = low.index("0")
        if len(C) != 2:
            continue
        old = next(i for i in C if i != restorer)
        if high[restorer] != low[old]:
            continue
        coeff = {ykey(high, i): Q(1) for i in C}
        coeff.update({ykey(low, i): Q(-1) for i in C})
        add_row(restricted, "actual_pair_tcwm", coeff, 0, Q(1, 2))
        selected += 1
    require(selected == 12, "missing same-type protected transitions")
    for low in lows:
        C = tuple(i for i in OWNERS if low[i] != "0")
        add_row(restricted, "active_pair_coverage", {ykey(low, i): 1 for i in C}, worth(low, C), Q(1, 2))
        add_row(restricted, "zero_owner_nonnegative", {ykey(low, low.index("0")): 1}, 0)
    for high in highs:
        minority = next(i for i in OWNERS if high.count(high[i]) == 1)
        dominance = {ykey(high, minority): Q(1)}
        dominance.update({pkey(high, a): -Q(BUNDLE[high[minority]][a]) for a in range(3)})
        # D + 2*dual_feasibility - efficient_price_equality + 2*p_third = y_minority - 1.
        add_row(restricted, "minority_price_domination", dominance, 0)
        add_row(restricted, "production_dual_feasibility", {pkey(high, a): 1 for a in range(3)}, 1, 2)
        add_row(restricted, "efficient_price_equality", {pkey(high, a): bundle(high, OWNERS)[a]
                                                       for a in range(3)}, 1, -1, equality=True)
        add_row(restricted, "third_price_nonnegative", {pkey(high, 2): 1}, 0, 2)
    for proof in (unrestricted, restricted):
        for high in highs:
            coeff = {"K": Q(1), **{ykey(high, i): Q(-1) for i in OWNERS}}
            add_row(proof, "high_total_budget", coeff, 0)
    results["unrestricted"]["dual"] = sum_proof(unrestricted, Q(15, 2))
    results["price_base"]["dual"] = sum_proof(restricted, Q(9))
    output = {"status": "PASS", "arithmetic": "exact fractions; no solver or numerical search",
              "scope": "Only the sealed twelve-profile, three-fixed-owner min3 fixture at s=2; not all-real optima.",
              "technology": {"A": [[1], [1], [1]], "profit": [1]},
              "owner_boxes": "three actual owners, each [0,1]^3",
              "source": str(SOURCE), "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "arity3_embedding_source": str(CAMP / "reviews/cardinality_rigidity_audit/DUAL_CYCLE_LEMMAS.txt"),
              "profiles": [list(p) for p in profiles], "nontrivial_protected_rows": len(proper_edges),
              "nontrivial_rows_with_unchanged_member": 24,
              "results": results,
              "primal_payments": {name: {"".join(p): list(map(str, values)) for p, values in rule.items()}
                                  for name, rule in pay.items()},
              "restricted_primal_prices": {"".join(p): list(map(str, price)) for p, price in prices.items()},
              "dual_certificates": {"unrestricted": unrestricted, "price_base": restricted},
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    Path(__file__).with_suffix(".json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "profiles": len(profiles), "results": results,
                      "proper_comparisons": len(proper_edges), "with_unchanged_member": 24}, indent=2))


if __name__ == "__main__":
    main()
