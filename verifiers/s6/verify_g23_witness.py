"""Exact end-to-end regression for the sharp six-player witness G(2,3).

The family theorem in the paper is the proof of the lower bound. This script
is a bug audit: it rebuilds the lower-envelope game, independently recomputes
both lexicographic core selections with the repository's exact-rational staged
LP implementation, and checks the displayed distance and exactness witnesses.
"""
from __future__ import annotations

import sys
from fractions import Fraction as F
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src"
SIMPLEX = Path(__file__).resolve().parents[1] / "divergence"
sys.path[:0] = (str(SIMPLEX), str(SRC))

from lexsimplex import sx_lmax, sx_lmin  # noqa: E402
from tugame import Game  # noqa: E402


N = 6
FULL = (1 << N) - 1
G = (4, 1, 1, 0, 0, 0)
H = (0, 0, 0, 2, 2, 2)
EXPECTED_LMIN = (F(8, 3), F(2, 3), F(2, 3), F(2, 3), F(2, 3), F(2, 3))
EXPECTED_LMAX = (F(4, 3), F(1, 3), F(1, 3), F(4, 3), F(4, 3), F(4, 3))


def coalition_sum(point, coalition):
    return sum(
        (point[player] for player in range(N) if coalition >> player & 1),
        F(0),
    )


def main():
    values = [F(0)] * (1 << N)
    for coalition in range(1, FULL + 1):
        values[coalition] = min(
            coalition_sum(generator, coalition) for generator in (G, H)
        )
    game = Game(N, values)

    if game.v[FULL] != 6:
        raise AssertionError("unexpected grand-coalition worth")
    if any(game.v[1 << player] != 0 for player in range(N)):
        raise AssertionError("the witness is not singleton-normalized")

    # Every envelope value is attained by a generator lying in the core,
    # which is the defining exactness certificate.
    for coalition in range(1, FULL + 1):
        if game.v[coalition] != min(
            coalition_sum(generator, coalition) for generator in (G, H)
        ):
            raise AssertionError(f"lower-envelope mismatch at {coalition}")
        if not any(
            coalition_sum(generator, coalition) == game.v[coalition]
            for generator in (G, H)
        ):
            raise AssertionError(f"no exactifying generator at {coalition}")

    computed_lmin = tuple(sx_lmin(N, game.v))
    computed_lmax = tuple(sx_lmax(N, game.v))
    if computed_lmin != EXPECTED_LMIN:
        raise AssertionError(f"unexpected Lmin: {computed_lmin}")
    if computed_lmax != EXPECTED_LMAX:
        raise AssertionError(f"unexpected Lmax: {computed_lmax}")

    distance = sum(abs(x - z) for x, z in zip(computed_lmin, computed_lmax))
    ratio = distance / game.v[FULL]
    if distance != 4 or ratio != F(2, 3):
        raise AssertionError(f"unexpected distance/ratio: {distance}, {ratio}")

    print("G(2,3) EXACT WITNESS VERIFIED")
    print(f"Lmin={computed_lmin}")
    print(f"Lmax={computed_lmax}")
    print(f"distance={distance}; T={game.v[FULL]}; rho={ratio}")


if __name__ == "__main__":
    main()
