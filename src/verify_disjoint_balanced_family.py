"""Exact verifier for a disjoint-arm balanced three-game obstruction at n=5."""
from fractions import Fraction as F

from family_infeasible import farkas_certificate, is_family_feasible
from hunt_sd import is_exact_game
from tugame import Game


N = 5
A = 0b00111
B = 0b11000
BASE_PROPER = {
    1: 0, 2: 0, 3: 0, 4: -1, 5: 1, 6: 1, 7: 1,
    8: -2, 9: 0, 10: 0, 11: 2, 12: -3, 13: -1, 14: -1, 15: 1,
    16: -2, 17: -2, 18: -2, 19: -2, 20: -1, 21: -1, 22: -1,
    23: -1, 24: -2, 25: 0, 26: 0, 27: 0, 28: -3, 29: -1, 30: -1,
}
CORE_POINTS = (
    (0, 0, 1, 2, -2),
    (2, 2, -1, -2, 0),
    (0, 0, 1, 2, -2),
)


def make_games():
    values = [F(0)] * (1 << N)
    for coalition, worth in BASE_PROPER.items():
        values[coalition] = F(worth)
    values[-1] = F(1)
    base = Game(N, values)
    arm_A = Game(N, list(values))
    arm_A.v[A] += 2
    arm_B = Game(N, list(values))
    arm_B.v[B] += 2
    return base, arm_A, arm_B


def verify():
    games = make_games()
    edges = [(0, 1, A), (0, 2, B)]
    for game, point in zip(games, CORE_POINTS):
        assert sum(point) == game.v[game.N] == 1
        assert not game.core_violations(point)

    feasible, _witness = is_family_feasible(games, edges)
    assert not feasible
    certificate = farkas_certificate(games, edges)
    assert certificate is not None
    assert certificate["rhs"] < 0

    exactness = [is_exact_game(game) for game in games]
    print("DISJOINT BALANCED FAMILY VERIFIED")
    print("  bump coalitions:", A, B, "increments: 2, 2")
    print("  balanced core witnesses:", CORE_POINTS)
    print("  exactness:", exactness)
    print("  exact Farkas rhs:", certificate["rhs"])
    print("  active inequalities:")
    for row, weight in certificate["active_ineq"]:
        print("   ", row, weight)


if __name__ == "__main__":
    verify()
