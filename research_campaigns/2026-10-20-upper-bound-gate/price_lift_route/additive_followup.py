"""Exact checks for the sharp min_r TCWM-correction coefficient."""
from fractions import Fraction as Q
from itertools import combinations, product
import json


GRID = (Q(0), Q(1, 2), Q(1))


def coalitions(n):
    return [frozenset(c) for k in range(n + 1) for c in combinations(range(n), k)]


def cea(claims, estate):
    remaining = estate
    for k, claim in enumerate(sorted(claims)):
        level = remaining / (len(claims) - k)
        if level <= claim:
            awards = tuple(min(c, level) for c in claims)
            assert sum(awards) == estate
            return awards
        remaining -= claim
    raise AssertionError("Infeasible estate")


def total(b):
    return tuple(map(sum, zip(*b)))


def cea_rule(b):
    E = min(total(b))
    rows = [cea(claims, E) for claims in zip(*b)]
    return tuple(map(sum, zip(*rows)))


def mixed_checks(n, r):
    reports = list(product(GRID, repeat=r))
    profiles = list(product(reports, repeat=n))
    uppers = {lo: [hi for hi in reports if all(a <= b for a, b in zip(lo, hi))]
              for lo in reports}
    cs = coalitions(n)
    values = {b: cea_rule(b) for b in profiles}
    counts = {"profiles": len(profiles), "coverage_rows": 0, "out_rows": 0,
              "price_domination_rows": 0}
    for b, z in values.items():
        B = total(b)
        E = min(B)
        h = B.index(E)
        assert sum(z) == r * E
        for i in range(n):
            assert z[i] >= b[i][h]
            counts["price_domination_rows"] += 1
        for c in cs:
            bc = tuple(sum(b[i][a] for i in c) for a in range(r))
            assert sum(z[i] for i in c) >= min(bc)
            counts["coverage_rows"] += 1
        for hi in product(*(uppers[b[i]] for i in range(n))):
            changed = {i for i in range(n) if b[i] != hi[i]}
            zh = values[hi]
            for c in cs:
                if not changed.issubset(c):
                    continue
                delta = tuple(sum(hi[i][a] - b[i][a] for i in c) for a in range(r))
                assert sum(zh[i] - z[i] for i in c) >= min(delta)
                counts["out_rows"] += 1
    return counts


def selected_rule(c):
    winner = max(range(len(c)), key=lambda i: (c[i], -i))
    return tuple(min(c) if i == winner else Q(0) for i in range(len(c)))


def pure_checks(r):
    profiles = list(product(GRID, repeat=r))
    cs = coalitions(r)
    counts = {"profiles": len(profiles), "coverage_rows": 0, "out_rows": 0,
              "repaired_out_rows": 0, "correction_tcwm_failures": 0}
    for lo in profiles:
        yl = selected_rule(lo)
        assert sum(yl) == min(lo)
        wl = (min(lo),) * r
        zl = tuple(wl[i] - yl[i] for i in range(r))
        assert min(zl) >= 0 and sum(zl) == (r - 1) * min(lo)
        for c in cs:
            worth = min(lo) if len(c) == r else Q(0)
            assert sum(yl[i] for i in c) >= worth
            counts["coverage_rows"] += 1
        for hi in profiles:
            if not all(a <= b for a, b in zip(lo, hi)):
                continue
            yh = selected_rule(hi)
            wh = (min(hi),) * r
            zh = tuple(wh[i] - yh[i] for i in range(r))
            changed = {i for i in range(r) if hi[i] != lo[i]}
            for c in cs:
                if changed.issubset(c):
                    delta = tuple(hi[i] - lo[i] if i in c else Q(0) for i in range(r))
                    assert sum(yh[i] - yl[i] for i in c) >= min(delta)
                    assert sum(wh[i] - wl[i] for i in c) >= min(delta)
                    counts["out_rows"] += 1
                    counts["repaired_out_rows"] += 1
                    if sum(zh[i] - zl[i] for i in c) < 0:
                        counts["correction_tcwm_failures"] += 1
    assert counts["correction_tcwm_failures"] > 0
    return counts


def lower_certificates():
    out = []
    for r in (2, 3, 4):
        for m in (2, 3, 10, 100, 1000):
            t = 1 - Q(1, m)
            for i in range(r):
                lo = tuple(t if j == i else Q(1) for j in range(r))
                assert selected_rule(lo)[i] == 0
                assert lo.count(min(lo)) == 1 and min(lo) == t
                # Unique efficient price e_i forces Z_i(lo)>=t; singleton
                # TCWM carries it to the common terminal profile (1,...,1).
            out.append({"arity": r, "t": str(t), "terminal_value": 1,
                        "forced_terminal_tcwm_correction": str(r * t),
                        "forced_terminal_price_dominating_payment": str(r * t),
                        "forced_terminal_sum_only_correction": str(r * t - 1)})
    return out


if __name__ == "__main__":
    result = {"pure_input_rule": {str(r): pure_checks(r) for r in (2, 3, 4)},
              "mixed_cea": {f"n{n}_r{r}": mixed_checks(n, r) for n, r in ((3, 2), (2, 3))},
              "lower_certificates": lower_certificates(),
              "scope": "Sharp universal min_r TCWM-correction coefficient r; pure-owner all-real optimized architecture gap 1 versus r; sharp sum-only correction r-1 for the specified pure-owner input rule."}
    print(json.dumps(result, indent=2))
