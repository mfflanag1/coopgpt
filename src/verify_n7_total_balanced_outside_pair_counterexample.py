"""Exact verifier for the seven-player totally-balanced outside-pair escape.

Coalitions are bit masks on N={1,...,7}.  The integer game is v(A)=-s(A),
with the zero allocation as reference point, S={1,...,5}, and P={6,7}.
The witness table gives one core allocation for every proper subgame; omitted
coordinates are zero.  All checks below use integer arithmetic and no solver.
"""
from __future__ import annotations

import json
from fractions import Fraction


N = 7
FULL = (1 << N) - 1
S = (1 << 5) - 1
P = FULL ^ S

# Indexed by coalition mask from 0 through 127.
SLACK = (
    0, 2, 2, 1, 2, 1, 0, 0, 2, 1, 0, 0, 1, 1, 0, 0,
    2, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0,
    3, 3, 3, 3, 4, 3, 3, 2, 3, 3, 3, 2, 3, 3, 0, 1,
    3, 0, 2, 1, 3, 2, 2, 0, 3, 0, 2, 0, 3, 0, 1, 0,
    1, 1, 1, 1, 2, 0, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0,
    2, 1, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0,
    3, 3, 3, 3, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 1, 1,
    3, 1, 2, 1, 2, 1, 2, 1, 3, 1, 2, 1, 2, 1, 1, 0,
)

# Positive coefficients of a minimal balanced collection.  Its first member
# is S; deleting S gives a zero-cost eta dual with rho=11 and w=0.
BALANCED_SUPPORT = {
    S: 1,
    46: 7,   # 2346
    49: 5,   # 156
    69: 2,   # 137
    73: 4,   # 147
    82: 4,   # 257
    84: 2,   # 357
}

# For each subgame T, this stores the nonzero coordinates of an allocation in
# core(v|T) that is efficient on T.  Player labels are one-based.
WITNESS_NONZERO = {
    1: {1: -2}, 2: {2: -2}, 3: {1: -1}, 4: {3: -2},
    5: {1: -1}, 8: {4: -2}, 9: {1: -1}, 12: {3: -1},
    13: {1: -1}, 16: {5: -2}, 20: {3: -1}, 24: {4: -1},
    28: {3: -1}, 32: {6: -3}, 33: {1: -2, 6: -1},
    34: {2: -2, 6: -1}, 35: {1: -1, 6: -2},
    36: {3: -2, 6: -2}, 37: {1: -1, 6: -2}, 38: {6: -3},
    39: {6: -2}, 40: {4: -2, 6: -1}, 41: {1: -1, 6: -2},
    42: {6: -3}, 43: {6: -2}, 44: {3: -1, 6: -2},
    45: {3: -1, 6: -2}, 46: {2: 1, 3: -1},
    47: {1: -1, 2: 1, 6: -1}, 48: {5: -2, 6: -1},
    50: {6: -2}, 51: {2: -1, 5: 1, 6: -1},
    52: {3: -1, 6: -2}, 53: {1: 1, 3: -2, 5: 1, 6: -2},
    54: {2: 1, 3: -1, 6: -2}, 56: {4: -1, 6: -2},
    57: {1: 1, 5: -1}, 58: {2: 1, 4: -1, 6: -2},
    60: {4: -1, 6: -2}, 62: {2: 1, 5: -1, 6: -1},
    64: {7: -1}, 65: {1: -2, 7: 1}, 66: {2: -2, 7: 1},
    67: {1: -1}, 68: {3: -2}, 69: {1: -1, 7: 1},
    70: {7: -1}, 72: {4: -2}, 73: {1: -1, 7: 1},
    74: {7: -1}, 76: {3: -1, 7: -1}, 77: {1: -1, 7: 1},
    78: {2: 1, 3: -1, 7: -1}, 80: {5: -2}, 81: {7: -1},
    84: {3: -1, 7: 1}, 88: {4: -1, 7: -1},
    89: {1: 1, 5: -1, 7: -1}, 90: {2: 1, 5: -1},
    92: {5: -1, 7: 1}, 96: {6: -3}, 97: {6: -3},
    98: {6: -3}, 99: {1: -1, 6: -2}, 100: {6: -3},
    101: {6: -2}, 102: {6: -3}, 103: {6: -2}, 104: {6: -3},
    105: {6: -2}, 106: {6: -3}, 107: {6: -2},
    108: {3: -1, 6: -2}, 109: {4: -1, 6: -2, 7: 1},
    110: {7: -1}, 111: {1: -1, 3: 1, 4: 1, 6: -2},
    112: {6: -3}, 113: {7: -1}, 114: {6: -2},
    115: {2: -1, 5: 1, 6: -1}, 116: {6: -2},
    117: {1: 1, 3: -2, 5: 1, 6: -2, 7: 1},
    118: {6: -2}, 119: {1: 1, 5: 1, 6: -2, 7: -1},
    120: {4: -1, 6: -2}, 121: {1: 1, 5: -1, 7: -1},
    122: {6: -2}, 123: {1: 1, 5: 1, 6: -2, 7: -1},
    124: {4: -1, 6: -2, 7: 1},
    125: {1: 1, 5: 1, 6: -2, 7: -1},
    126: {2: 1, 3: 1, 5: -1, 6: -2},
}


def members(mask):
    return [i + 1 for i in range(N) if mask >> i & 1]


def payoff(allocation, coalition):
    return sum(allocation.get(i + 1, 0) for i in range(N) if coalition >> i & 1)


def submasks(mask):
    submask = mask
    while True:
        yield submask
        if submask == 0:
            return
        submask = (submask - 1) & mask


def incidence_rank(masks):
    matrix = [
        [Fraction(int(mask >> i & 1)) for i in range(N)]
        for mask in masks
    ]
    rank = 0
    for column in range(N):
        pivot = next((r for r in range(rank, len(matrix)) if matrix[r][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][column]
        matrix[rank] = [value / pivot_value for value in matrix[rank]]
        for row in range(len(matrix)):
            if row == rank or matrix[row][column] == 0:
                continue
            multiple = matrix[row][column]
            matrix[row] = [
                value - multiple * pivot_entry
                for value, pivot_entry in zip(matrix[row], matrix[rank])
            ]
        rank += 1
    return rank


def main():
    assert len(SLACK) == 1 << N
    assert SLACK[0] == SLACK[FULL] == 0
    assert all(value >= 0 for value in SLACK)

    # Exact total-balancedness certificate: one checked core point per subgame.
    for tight in range(1, FULL + 1):
        allocation = WITNESS_NONZERO.get(tight, {})
        assert all(tight >> (player - 1) & 1 for player in allocation)
        assert payoff(allocation, tight) == -SLACK[tight]
        for coalition in submasks(tight):
            assert payoff(allocation, coalition) >= -SLACK[coalition]

    carrier_differences = {
        coalition: SLACK[P | coalition] - SLACK[coalition]
        for coalition in range(1, S)
    }
    gamma = min(carrier_differences.values())
    assert gamma == 1

    degree = [
        sum(weight for coalition, weight in BALANCED_SUPPORT.items()
            if coalition >> player & 1)
        for player in range(N)
    ]
    assert degree == [12] * N
    assert incidence_rank(BALANCED_SUPPORT) == N
    assert all(SLACK[coalition] == 0 for coalition in BALANCED_SUPPORT)

    # For any full-game core point x, each support payoff x(T) is nonnegative.
    # Their positive weighted sum is 12*x(N)=0, so all seven are zero.  Full
    # incidence rank then forces x=0.  Hence eta=0, and v is not exact because
    # (for example) v({1})=-2 while the unique core allocation pays player 1 zero.
    eta = 0
    assert SLACK[1] == 2

    eta_dual = {coalition: weight for coalition, weight in BALANCED_SUPPORT.items()
                if coalition != S}
    eta_degree = [
        sum(weight for coalition, weight in eta_dual.items()
            if coalition >> player & 1)
        for player in range(N)
    ]
    assert eta_degree == [11] * 5 + [12] * 2
    assert sum(weight * SLACK[coalition] for coalition, weight in eta_dual.items()) == 0

    summary = {
        "status": "exact integer counterexample verified without optimization",
        "n": N,
        "S": members(S),
        "P": members(P),
        "game": "v(A) = -SLACK[A], with coalition A encoded as a bit mask",
        "totally_balanced": True,
        "subgame_core_witnesses_checked": FULL,
        "full_core": "singleton {0}, certified by the rank-seven zero-slack balanced support",
        "exact": False,
        "gamma_S": gamma,
        "eta_S": eta,
        "carrier_bound_violated": eta < gamma,
        "balanced_degree": degree[0],
        "balanced_support": [
            {"coalition": members(coalition), "coefficient": weight}
            for coalition, weight in BALANCED_SUPPORT.items()
        ],
        "eta_dual_cost": 0,
        "eta_dual_rho": 11,
        "tight_carrier_subsets": [
            members(coalition)
            for coalition, difference in carrier_differences.items()
            if difference == gamma
        ],
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
