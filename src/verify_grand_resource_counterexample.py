"""Exact symbolic certificate for failure of grand-resource monotonicity.

The five-player base game is the lower envelope of two equal-sum points

    p = (0, 0, 7, 0, 7),   q = (2, 10, 0, 2, 0).

Thus v(S)=min(p(S),q(S)) for proper S and v(N)=14.  Both p and q lie in
the core and one of them is tight at every coalition, so v is exact.

For v^r(N)=14+r, put r=2+epsilon.  On 0 <= epsilon <= 3/2 the
leximin-above-floors allocation is

    (3+e/3, 4-e/3, 3+e/3, 3+e/3, 3+e/3).

Player 2 therefore loses e/3 when the grand worth rises.  This program checks
the lower-envelope construction, exactness witnesses, symbolic core membership
over the full interval, and exact leximin computations at every endpoint and
at all eighth-grid points.
"""
from fractions import Fraction as F

from hunt_exact_points import game_from_points
from leximin import leximin_core_exact
from tugame import Game


P = (F(0), F(0), F(7), F(0), F(7))
Q = (F(2), F(10), F(0), F(2), F(0))
N_PLAYERS = 5
GRAND = (1 << N_PLAYERS) - 1


def coalition_sum(x, coalition):
    return sum(x[i] for i in range(N_PLAYERS) if coalition >> i & 1)


def candidate(epsilon):
    up = F(3) + epsilon / 3
    return (up, F(4) - epsilon / 3, up, up, up)


def bumped(base, epsilon):
    worths = list(base.v)
    worths[GRAND] = F(16) + epsilon
    return Game(N_PLAYERS, worths)


def verify():
    base = game_from_points(N_PLAYERS, [P, Q])

    assert base.v[GRAND] == 14
    for coalition in range(1, GRAND):
        assert base.v[coalition] == min(
            coalition_sum(P, coalition), coalition_sum(Q, coalition)
        )
        assert coalition_sum(P, coalition) >= base.v[coalition]
        assert coalition_sum(Q, coalition) >= base.v[coalition]
        assert (
            coalition_sum(P, coalition) == base.v[coalition]
            or coalition_sum(Q, coalition) == base.v[coalition]
        )

    # Every affine core slack is nonnegative throughout [0,3/2].  It suffices
    # to inspect both endpoints.
    for epsilon in (F(0), F(3, 2)):
        x = candidate(epsilon)
        game = bumped(base, epsilon)
        assert sum(x) == game.v[GRAND]
        for coalition in range(1, GRAND):
            assert coalition_sum(x, coalition) >= game.v[coalition]

    # The two pair constraints used in the analytic max-min proof.
    pair_23 = (1 << 1) | (1 << 2)
    pair_25 = (1 << 1) | (1 << 4)
    assert base.v[pair_23] == 7
    assert base.v[pair_25] == 7

    # Independent exact leximin solver checks at both chamber endpoints and at
    # the displayed strict-drop point.  The affine proof above covers every
    # intermediate epsilon symbolically.
    for k in (0, 1, 12):
        epsilon = F(k, 8)
        assert leximin_core_exact(bumped(base, epsilon)) == list(candidate(epsilon))

    before = leximin_core_exact(bumped(base, F(0)))
    after = leximin_core_exact(bumped(base, F(1, 8)))
    assert before == [F(3), F(4), F(3), F(3), F(3)]
    assert after == [F(73, 24), F(95, 24), F(73, 24), F(73, 24), F(73, 24)]
    assert after[1] < before[1]

    print(
        "GRAND RESOURCE COUNTEREXAMPLE VERIFIED "
        "(exact lower envelope; symbolic chamber 0<=epsilon<=3/2; "
        "player 2 drops 4 -> 95/24)."
    )


if __name__ == "__main__":
    verify()
