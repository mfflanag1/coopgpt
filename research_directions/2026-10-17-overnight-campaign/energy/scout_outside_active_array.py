"""Necessary active-count inequalities only; no finite-N scale invariance.

Finite exact duals, when replayed, are valid unrestricted OUT lower bounds.
Floating solutions alone are discovery diagnostics.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json
import time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def solve(N, limit):
    started = time.monotonic()
    ki = N * N
    rows, columns, values, rhs, tags = [], [], [], [], []

    def index(a, b):
        return (a - 1) * N + b - 1

    def add(terms, bound, tag):
        coeff = {}
        for a, b, v in terms:
            if a > 0 and b > 0 and v:
                j = index(a, b)
                coeff[j] = coeff.get(j, 0) + v
        if tag[0] == "budget":
            coeff[ki] = -min(tag[1], tag[2])
        row = len(rhs)
        for j, v in coeff.items():
            if v:
                rows.append(row)
                columns.append(j)
                values.append(v)
        rhs.append(bound)
        tags.append(tag)

    for m in range(1, N + 1):
        for n in range(1, m + 1):
            add([(m, n, m), (n, m, n)], 0, ["budget", m, n])
            add([(m, n, -1), (n, m, -1)], -1, ["cover", m, n])
            for u in range(m + 1):
                for v in range(n + 1):
                    if u + v == 0:
                        continue
                    for r in set([u, m]):
                        for s in set([v, n]):
                            add([(m, n, -r), (n, m, -s),
                                 (m - u, n - v, r - u),
                                 (n - v, m - u, s - v)],
                                -min(u, v), ["outside", m, n, u, v, r, s])
    matrix = coo_matrix((values, (rows, columns)), shape=(len(rhs), ki + 1)).tocsr()
    objective = np.zeros(ki + 1)
    objective[ki] = 1
    answer = linprog(objective, A_ub=matrix, b_ub=rhs, bounds=(0, None),
                     options={"time_limit": limit})
    result = {"N_per_role": N, "actual_owners": 2 * N,
              "variables": ki + 1, "rows": len(rhs),
              "status": int(answer.status), "message": answer.message,
              "seconds": time.monotonic() - started,
              "scope": "Necessary active-count relaxation; finite scale invariance NOT imposed."}
    if answer.success:
        combination = {}
        right = Q(0)
        certificate = []
        for row, raw in enumerate(answer.ineqlin.marginals):
            if raw >= -1e-9:
                continue
            weight = Q(float(-raw)).limit_denominator(10**9)
            for at in range(matrix.indptr[row], matrix.indptr[row + 1]):
                j = int(matrix.indices[at])
                combination[j] = combination.get(j, Q(0)) + weight * int(matrix.data[at])
            right += weight * rhs[row]
            certificate.append({"weight": str(weight), "tag": tags[row]})
        valid = combination.get(ki, Q(0)) < 0 and all(v >= 0 for j, v in combination.items() if j != ki)
        result.update(floating_optimum=float(answer.fun), exact_dual_valid=valid,
                      exact_bound=str(right / combination[ki]) if valid else None,
                      certificate_rows=len(certificate))
        payload = dict(result, certificate=certificate,
                       floating_prices={f"{m},{n}": float(answer.x[index(m, n)])
                                        for m in range(1, N + 1) for n in range(1, N + 1)})
    else:
        payload = result
    Path(__file__).with_name(f"outside_active_array_{N}.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--N", type=int, default=20)
    parser.add_argument("--limit", type=int, default=60)
    args = parser.parse_args()
    solve(args.N, args.limit)
