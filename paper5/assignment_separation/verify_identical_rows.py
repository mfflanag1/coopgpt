"""Exact finite checks from uncompressed matching-dual constraints.

Requires z3-solver. No pre-imposed common-payoff identity is used in selector
computation. Every unexpected SAT/UNKNOWN/selector value raises explicitly.
The conventional proof, not this finite check, establishes the theorem.
"""
from fractions import Fraction as F
from pathlib import Path
import json
import z3


def rational(value):
    value = z3.simplify(value)
    if z3.is_int_value(value):
        return F(value.as_long())
    if not z3.is_rational_value(value):
        raise RuntimeError(f"nonrational optimization result: {value}")
    return F(value.numerator_as_long(), value.denominator_as_long())


def Q(value):
    value = F(value)
    return z3.Q(value.numerator, value.denominator)


def optimum(constraints, expression, maximize):
    solver = z3.Optimize()
    solver.set(timeout=60000)
    solver.add(*constraints)
    handle = solver.maximize(expression) if maximize else solver.minimize(expression)
    verdict = solver.check()
    if verdict != z3.sat:
        raise RuntimeError(f"optimization failed: {verdict}")
    return rational(handle.value())


def selector(constraints, p, ascending):
    fixed = {}
    stages = []
    while len(fixed) < len(p):
        free = [i for i in range(len(p)) if i not in fixed]
        prefix = constraints + [p[i] == Q(value) for i, value in fixed.items()]
        t = z3.FreshReal("level")
        stage = [(p[i] >= t if ascending else p[i] <= t) for i in free]
        level = optimum(prefix + stage, t, ascending)
        face = prefix + [(p[i] >= Q(level) if ascending else p[i] <= Q(level)) for i in free]
        pinned = [i for i in free if optimum(face, p[i], ascending) == level]
        if not pinned:
            raise RuntimeError("no coordinate fixed on optimal stratum")
        fixed.update({i: level for i in pinned})
        stages.append({"level": str(level), "coordinates": pinned})
    return [fixed[i] for i in range(len(p))], stages


def require_unsat(constraints, purpose):
    solver = z3.Solver()
    solver.set(timeout=60000)
    solver.add(*constraints)
    verdict = solver.check()
    if verdict != z3.unsat:
        raise RuntimeError(f"{purpose}: expected UNSAT, received {verdict}")


def check(m, isolated=False, flat=False, diagonal=False):
    column = [2] * (m - 1) + [2 if flat else 4]
    T = sum(column)
    n = 2 * m + int(isolated)
    p = [z3.FreshReal("payoff") for _ in range(n)]
    constraints = [v >= 0 for v in p] + [sum(p) == T]
    for i in range(m):
        for j in range(m):
            if not diagonal or i == j:
                constraints.append(p[i] + p[m+j] >= column[j])
    # The optional isolated vertex has no edges; efficiency itself forces 0.
    x, lower_stages = selector(constraints, p, True)
    z, upper_stages = selector(constraints, p, False)
    if flat or diagonal:
        expected = [F(c, 2) for c in column] * 2
        if isolated:
            expected.append(F(0))
        if x != expected or z != expected:
            raise RuntimeError(("negative-control selector mismatch", m, flat, diagonal, x, z))
        expected_rho = F(0)
    else:
        expected_x = [F(1)] * m + [F(1)] * (m-1) + [F(3)]
        expected_z = [F(2)] * m + [F(0)] * (m-1) + [F(2)]
        if isolated:
            expected_x.append(F(0))
            expected_z.append(F(0))
        if x != expected_x or z != expected_z:
            raise RuntimeError(("attaining-family selector mismatch", m, isolated, x, z))
        expected_rho = F(m, m+1)
        t = p[0]
        identities = [p[i] == t for i in range(m)]
        identities += [p[m+j] == column[j] - t for j in range(m)]
        identities += [t >= 0, t <= 2]
        if isolated:
            identities.append(p[-1] == 0)
        require_unsat(constraints + [z3.Not(z3.And(*identities))], "core point outside claimed segment")
    actual_rho = sum(abs(a-b) for a, b in zip(x,z)) / T
    if actual_rho != expected_rho:
        raise RuntimeError(("divergence mismatch", actual_rho, expected_rho))
    return {"m":m, "n":n, "isolated":isolated, "flat":flat, "diagonal":diagonal,
            "T":T, "Lmin":[str(v) for v in x], "Lmax_min":[str(v) for v in z],
            "rho":str(actual_rho), "ascending_stages":lower_stages,
            "descending_stages":upper_stages}


if __name__ == "__main__":
    cases = []
    for m in range(2,7):
        for isolated in (False, True):
            result = check(m, isolated=isolated)
            cases.append(result)
            print("PASS", result["n"], result["rho"], flush=True)
    controls = [check(3, flat=True), check(3, diagonal=True)]
    payload = {"evidence":"exact finite checks; all-parameter proof separate",
               "z3_version":z3.get_version_string(), "cases":cases,
               "negative_controls":controls}
    Path(__file__).with_name("identical_rows_exact_results.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print("PASS", len(cases), "attaining-family cases and", len(controls), "negative controls")
