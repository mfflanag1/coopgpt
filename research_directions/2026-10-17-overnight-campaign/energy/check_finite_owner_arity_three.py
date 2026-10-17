"""Exact rational replay of the finite-owner common-cap obstruction.

Run with python3 -I, never -O. The theorem is analytic; this script checks
its coefficient identities and a compressed finite factor-two certificate.
"""
from fractions import Fraction as Q
import json
from pathlib import Path


def main():
    harmonic = [Q(0)]
    for j in range(1, 1001):
        harmonic.append(harmonic[-1] + Q(1, j))
    bootstrap_count = ladder_count = 0
    for K in range(2, 101):
        A = sum((Q(1) - (1 - Q(m * (K // m), K)) ** 2) / m
                for m in range(2, K + 1))
        delta = Q(K * (K + 1) // 2 - 1, K * K)
        assert A >= harmonic[K] - 1 - delta
        assert delta == Q(1, 2) + Q(1, 2 * K) - Q(1, K * K)
        for B in range(1, 13):
            L = 2 * B * K
            qsum = Q(0)
            R = Q(0)
            Qcoef = Q(0)
            for m in range(1, K + 1):
                k = K // m
                epsilon = Q(k, L)
                x = Q(m * k, K)
                assert 0 < epsilon and m * epsilon <= Q(1, 2 * B)
                # Actual coalition: two branch owners and k power owners.
                assert min(Q(k, L), epsilon) == epsilon
                bootstrap = m * epsilon * (1 - B * m * epsilon)
                exact = (1 - (1 - x) ** 2) / (4 * B)
                assert bootstrap == exact
                assert 0 <= 1 - x < Q(m, K)
                assert exact / (2 * m) >= Q(1, 8 * B * m) - Q(m, 8 * B * K * K)
                if m >= 2:
                    qsum += exact / (2 * m)
                    R += epsilon / 2
                    Qcoef += m * epsilon * epsilon / 2
                bootstrap_count += 1
            assert qsum == A / (8 * B)
            assert R - B * Qcoef == qsum
            for M in sorted({K + 1, 2 * K, 3 * K, min(9, max(2, B)) * K}):
                S = sum((Q(1, M - m + 1) for m in range(2, K + 1)), Q(0))
                assert S == harmonic[M - 1] - harmonic[M - K]
                assert S <= Q(K - 1, M - K + 1) < Q(K, M - K)
                assert A / (8 * (1 + S)) >= (harmonic[K] - 1 - delta) / (8 * (1 + S))
                assert R / (1 + S + Qcoef) - B == (qsum - B * (1 + S)) / (1 + S + Qcoef)
                ladder_count += 1

    # Six positive terms of the exact log2 expansion certify the stated bound.
    log2_lower = 2 * sum((Q(1, 3 ** (2 * r + 1) * (2 * r + 1))
                          for r in range(6)), Q(0))
    assert log2_lower > Q(6931, 10000)
    log2_upper = log2_lower + Q(2, 13 * 3 ** 13) / (1 - Q(1, 9))
    assert log2_upper < Q(6932, 10000)
    B, exponent, branch_multiple = 2, 49, 35
    K = 2 ** exponent
    M, L = branch_multiple * K, 2 * B * K
    n = 2 * M + L
    assert n == 41658296553177088
    denominator_bound = 1 + Q(1, branch_multiple - 1)
    logK_minus_one_lower = exponent * Q(6931, 10000) - 1
    necessary_B_squared_lower = logK_minus_one_lower / (8 * denominator_bound)
    assert necessary_B_squared_lower > B * B
    budget_slack = logK_minus_one_lower / (8 * B) - B * denominator_bound
    denominator_upper = denominator_bound + exponent * Q(6932, 10000) / (8 * B * B)
    funding_lower = B + budget_slack / denominator_upper
    assert budget_slack == Q(3523, 2720000)
    assert funding_lower == Q(11377879, 5687178) > Q(10003, 5000)

    # Elementary explicit family using rational log2 lower, no exp evaluation.
    family = []
    for B in range(2, 31):
        threshold = 8 * Q(B ** 3, B - 1) + 1
        exponent = threshold // Q(6931, 10000) + 1
        assert exponent * Q(6931, 10000) > threshold
        assert ((B - 1) * (exponent * Q(6931, 10000) - 1) / (8 * B)) > B * B
        family.append({"B": B, "K_power_of_two": exponent,
                       "owner_count_formula": f"{4*B}*2^{exponent}"})

    result = {
        "status": "PASS",
        "arithmetic": "fractions.Fraction; no floating point",
        "bootstrap_identities_checked": bootstrap_count,
        "finite_ladders_checked": ladder_count,
        "factor_two_certificate": {
            "power_owners": L, "branch_count": M, "actual_owners": n,
            "K": K, "log2_lower_numerator": log2_lower.numerator,
            "log2_lower_denominator": log2_lower.denominator,
            "necessary_B_squared_strict_lower": str(necessary_B_squared_lower),
            "contradiction_to_B_squared": 4,
            "strict_rational_funding_lower": str(funding_lower),
        },
        "finite_family": family,
        "scope": "Exact algebra replay; analytic note proves all profiles and asymptotic rate.",
    }
    target = Path(__file__).with_name("finite_owner_arity_three_checks.json")
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "finite_family"}, indent=2))


if __name__ == "__main__":
    main()
