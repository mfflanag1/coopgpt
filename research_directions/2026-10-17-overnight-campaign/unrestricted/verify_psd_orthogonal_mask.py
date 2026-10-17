"""Exact checks for scalar consequences of the PSD orthogonal-mask proof.

No sphere simulation: continuous Haar conditioning remains a mathematical proof.
Run with python3 -I; this checker uses only the standard library.
"""
from fractions import Fraction as F
from math import comb


def main():
    label_cases = eligible_cases = minimax_cases = 0
    for m in range(4, 151):
        L = 100 * m
        assert F(1, L) <= F(1, 4)  # t=1/sqrt(L)<=1/2.
        assert F(4 * m, L) == F(1, 25)  # tail <=1/5, after squaring.
        for retained in range(m + 1):
            missing = m - retained
            for low_owner_missing in (0, 1):
                if low_owner_missing <= missing and 1-low_owner_missing <= retained:
                    high_missing = missing - low_owner_missing
                    assert high_missing >= max(missing-1, 0)
                    eligible_cases += 1
            for J in range(2, m + 1):
                exact_inclusion = F(comb(retained, J), comb(m, J)) if retained >= J else F(0)
                union_lower = 1-F(J * missing, m)
                assert exact_inclusion >= union_lower
                label_cases += 1

        # The outer branches are checked algebraically against squared targets.
        assert F(m, 2)**2 >= F(m, 10)
        assert F(m, 5)**2 >= F(m, 10)
        # A finite rational suite checks the middle-branch integer choice.
        for denom in range(2, 81):
            for num in range(denom + 1):
                delta = F(num, denom)
                if delta <= F(1, 2*m):
                    assert m*(1-m*delta) >= F(m, 2)
                elif delta >= F(1, 4):
                    assert F(4, 5)*(m*delta-1) >= F(m, 5)-F(4, 5)
                else:
                    J = (1/(2*delta)).numerator // (1/(2*delta)).denominator
                    assert 2 <= J <= m
                    assert J*delta <= F(1, 2)
                    assert J >= 1/(4*delta)
                    assert J*(1-J*delta) >= 1/(8*delta)
                    a, b = F(4, 5)*m*delta, 1/(8*delta)
                    assert a*b == F(m, 10)
                    # max(a,b)>=sqrt(ab) verified by squaring nonnegative sides.
                    assert max(a,b)**2 >= F(m, 10)
                    assert max(a-F(4,5),b)+F(4,5) >= max(a,b)
                minimax_cases += 1

    print(f"PASS: {eligible_cases} eligible-owner counts; {label_cases} exact label-junta bounds; "
          f"{minimax_cases} rational minimax cases; cap-tail scalar constants.")


if __name__ == "__main__":
    main()
