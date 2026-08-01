"""Exact certificates for the quantitative carrier--star frontier.

Checks three distinct claims:
1. sharp equality eta=gamma in an exact two-player-coalition fixture;
2. sharp equality eta=gamma in a richer five-generator, three-player fixture;
3. failure of the coefficient-one inequality at the leximin point of a
   balanced non-exact game (eta/gamma=1/7).
"""
from __future__ import annotations

from fractions import Fraction as F

from hunt_exact_points import game_from_points
from hunt_off_side_carrier import carrier_score
from hunt_sd import is_exact_game
from lemD import core_max_xS, core_min_xT, star_holds, xS
from leximin import leximin_core_exact
from tugame import Game


def quantitative_record(game, target):
    phi = leximin_core_exact(game)
    phi_s = xS(phi, target, game.n)
    gamma, face, carrier = carrier_score(game, phi, target)
    holds, star_maximum, witness = star_holds(game, phi, target)
    eta = star_maximum - phi_s
    return phi, gamma, eta, face, carrier, holds, witness


def verify_exact_pair_equality():
    points = [
        [-1, 0, 31, -7],
        [1, 0, 31, -9],
        [-1, 0, 35, -11],
    ]
    game = game_from_points(4, points)
    target = 12  # {3,4}
    phi, gamma, eta, _face, _carrier, holds, witness = quantitative_record(
        game, target
    )
    assert phi == [F(1, 3), F(0), F(97, 3), F(-29, 3)]
    assert gamma == eta == F(4, 3)
    assert holds and game.in_core(witness)
    assert all(witness[i] >= phi[i] for i in (2, 3))
    return gamma, eta


def verify_exact_rich_equality():
    points = [
        [-2, 32, -8, -7, 3],
        [1, 34, -8, -16, 7],
        [6, 28, -11, -11, 6],
        [-2, 36, -10, -11, 5],
        [1, 39, -4, -17, -1],
    ]
    game = game_from_points(5, points)
    target = 11  # {1,2,4}
    phi, gamma, eta, _face, _carrier, holds, witness = quantitative_record(
        game, target
    )
    assert phi == [F(11, 5), F(161, 5), F(-34, 5), F(-64, 5), F(16, 5)]
    assert gamma == eta == F(7, 5)
    assert holds and game.in_core(witness)
    assert all(witness[i] >= phi[i] for i in (0, 1, 3))
    return gamma, eta


def verify_nonexact_failure():
    worths = [
        0, -7, 5, 4, 1, -12, 14, 2,
        3, 7, 17, 8, 11, 1, 11, 19,
        -15, -12, -15, -11, -15, -14, -6, -2,
        -5, -14, -4, 0, 4, -7, 11, 13,
    ]
    game = Game(5, [F(value) for value in worths])
    target = 14  # {2,3,4}
    phi, gamma, eta, face, carrier, holds, witness = quantitative_record(
        game, target
    )
    assert phi == [F(-3, 2), F(10), F(6), F(17, 2), F(-10)]
    assert game.in_core(phi)  # balancedness certificate
    assert not is_exact_game(game)
    assert core_min_xT(game, 2) == 6 > game.v[2] == 5
    assert core_max_xS(game, target) - xS(phi, target, 5) == F(1, 2)
    assert gamma == F(7, 2) and eta == F(1, 2)
    assert eta / gamma == F(1, 7)
    assert (face, carrier) == (4, 21)
    assert holds and game.in_core(witness)
    return gamma, eta


def main():
    pair = verify_exact_pair_equality()
    rich = verify_exact_rich_equality()
    nonexact = verify_nonexact_failure()
    print(
        "QUANTITATIVE CARRIER FRONTIER VERIFIED: "
        f"exact pair eta/gamma=({pair[1]})/({pair[0]})=1; "
        f"exact rich eta/gamma=({rich[1]})/({rich[0]})=1; "
        f"balanced nonexact eta/gamma=({nonexact[1]})/({nonexact[0]})=1/7."
    )


if __name__ == "__main__":
    main()
