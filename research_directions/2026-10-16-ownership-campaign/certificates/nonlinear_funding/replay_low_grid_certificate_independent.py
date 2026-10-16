#!/usr/bin/env python3
"""Independent optimizer-free replay of the continuum low-grid dual certificate.

The interval/dual numbers are untrusted proposal data. This file reconstructs
the LP relaxation from the mathematical constraints, recomputes all interval
coefficient bounds with Fraction arithmetic, and verifies weak duality with
explicit nonnegative-coordinate residual caps. It never imports the builder.
"""
from fractions import Fraction as R
from math import factorial
from pathlib import Path
import hashlib
import json


def require(ok, label):
    if not ok:
        raise RuntimeError(label)


def negative_exp_polynomial(x, degree):
    require(x >= 0, "Taylor argument must be nonnegative")
    return sum(((-x) ** k / factorial(k) for k in range(degree + 1)), R(0))


def independent_data(s_left, s_right, u):
    require(1 <= s_left <= s_right, "capped-total interval")
    require(0 < u < 1, "support parameter")
    argument = 1 / u - 1
    q_below = negative_exp_polynomial(argument, 25) / 2
    q_above = negative_exp_polynomial(argument, 24) / 2
    a_below = 1 - q_above * (1 + 1 / u)
    a_above = 1 - q_below * (1 + 1 / u)
    require(q_below > 0 and a_below > 0, "positive denominators")
    require(q_below <= q_above and a_below <= a_above, "coefficient intervals")
    lambda_above = 1 - q_below * (1 + 1 / u - 1 / s_left)
    eta_above = q_above / s_left
    linear_response_above = R(7, 4) * eta_above
    quadratic_response_above = 3 * eta_above ** 2 / (4 * a_below)
    saving_below = R(2, 5) * negative_exp_polynomial(s_right - 1 + R(23, 125), 25)
    require(lambda_above > 0 and saving_below > 0, "positive aggregate coefficients")
    # Variables: (M, Z, negative_gap_total, negative_local_total, response_remainder).
    rows = []
    rhs = []
    def add(row, bound):
        rows.append(tuple(map(R, row)))
        rhs.append(R(bound))
    add((1, -1, 0, 0, 0), 0)                         # Z >= M
    add((-R(148, 125), 1, 0, 0, 0), 0)              # Z <= C_bar M
    add((0, -1, 0, 0, 0), 1 - s_left)                # P <= 1, S <= P+Z
    add((-1, 1, 1, 0, 0), 1)                        # Z+v <= 1+M
    add((0, 1, 1, 0, 0), R(3, 2))                   # Z+v <= 3/2
    add((0, 0, 1, 1, 0), 1)                         # v+Z_minus <= 1
    add((R(4, 3), 0, 1, -1, 0), R(4, 3))           # subset hardware-role floor
    add((0, -1, 0, 1, 0), 0)                        # Z_minus <= Z
    add((0, -linear_response_above, 0, linear_response_above, 1), 0)
    add((0, -quadratic_response_above-a_above, 0, quadratic_response_above, 1),
        a_above * (1 - s_left))                     # W_plus <= 1+Z-S
    add((1, 0, 0, 0, 0), 1)                         # M <= H = 1
    objective = (R(0), R(0), lambda_above-saving_below, R(0), R(1))
    upper_caps = (R(1), R(148, 125), R(1), R(148, 125),
                  linear_response_above * R(148, 125))
    constant = 1 + lambda_above * (s_right - 1)
    return rows, rhs, objective, upper_caps, constant


def main():
    root = Path('/private/tmp/coopgpt-ownership-20261016')
    certificate_path = root / 'root/general_funding/low_grid_certificate.json'
    proposal = json.loads(certificate_path.read_text())
    # Independent rational bounds on e imply every c,C,K bound used above.
    lower_e = sum((R(1, factorial(k)) for k in range(13)), R(0))
    upper_e = lower_e + R(1, factorial(13)) / (1 - R(1, 14))
    require(lower_e > R(125, 46), "c < 23/125 and C < 148/125")
    require(upper_e < R(87, 32), "e upper bound")
    require(upper_e - 1 < R(7, 4), "K < 7/4")
    require((upper_e - 1) ** 2 < 3, "K squared < 3")
    require(upper_e < R(25, 9), "L(3/4)=4/(3sqrt(e)) > 4/5")
    records = proposal['intervals']
    require(len(records) == 128, "expected interval count")
    previous = R(1)
    largest = R(0)
    positive_residual_coordinates = 0
    for index, record in enumerate(records):
        left, right, u = map(R, (record['lo'], record['hi'], record['u']))
        require(left == previous and right > left, f"partition cell {index}")
        rows, rhs, objective, caps, constant = independent_data(left, right, u)
        dual = list(map(R, record['dual']))
        require(len(dual) == len(rows) and min(dual) >= 0, f"dual signs {index}")
        residual = [max(R(0), objective[j] - sum((dual[k]*rows[k][j]
                    for k in range(len(rows))), R(0))) for j in range(5)]
        bound = constant + sum((dual[k]*rhs[k] for k in range(len(rows))), R(0))
        bound += sum((residual[j]*caps[j] for j in range(5)), R(0))
        require(bound == R(record['upper']), f"stored upper mismatch {index}")
        require(residual == list(map(R, record['residual'])), f"residual mismatch {index}")
        require(bound < R(8, 5), f"funding target {index}")
        largest = max(largest, bound)
        positive_residual_coordinates += sum(x > 0 for x in residual)
        previous = right
    require(previous == 1 + R(148, 125), "entire possible S range covered")
    require(largest == R(proposal['max_upper']), "stored maximum mismatch")
    sources = [certificate_path,
               root / 'root/general_funding/build_low_grid_certificate.py',
               Path(__file__).resolve()]
    print(json.dumps({
        'status': 'PASS', 'intervals': len(records),
        'proof_scope': 'Exact weak-duality bounds on every real S in [1,1+148/125]; no optimizer or report sampling.',
        'largest_bound_exact': str(largest), 'largest_bound_display': float(largest),
        'exact_margin_to_8_over_5': str(R(8, 5)-largest),
        'positive_rounding_residual_coordinates': positive_residual_coordinates,
        'sha256': {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources},
    }, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
