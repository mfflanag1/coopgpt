#!/usr/bin/env python3
"""Exact incidence census for the n=6 two-top sparse-cover frontier.

The four non-top roles are ``a,b,j,k``.  Only the role-preserving group
S_{a,b} x S_{j,k} is used: exchanging a gainer with an outsider, or the
root top with the heavy-gainer top, is not a symmetry of the allocation
cell.  Outsider singleton rows are included because they are tight when the
corresponding outsider payoff is zero.  All other singleton rows are
strictly slack in the stated strict-top/strict-subtop cell.

Every decision is exact.  Cover equations and ranks use Fraction Gaussian
elimination; the boundary no-go systems use the project's rational simplex.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from exactlp import exact_linprog  # noqa: E402


N = 6
R, H, A, B, J, K = range(N)
FULL = (1 << N) - 1
OUTSIDER_SINGLETONS = (1 << J, 1 << K)
EXPECTED_BOUNDARY_REPRESENTATIVES = (
    (7, 16, 43),
    (15, 16, 35),
    (5, 10, 16, 35),
    (5, 11, 16, 34),
    (5, 11, 16, 35),
    (6, 11, 16, 33),
    (6, 11, 16, 35),
    (7, 11, 16, 32),
    (7, 11, 16, 33),
    (7, 11, 16, 34),
    (7, 11, 16, 35),
    (15, 16, 39, 43),
    (15, 16, 39, 59),
    (16, 31, 39, 43),
)


def qstr(value: F) -> str:
    return str(value)


def rref(matrix: list[list[F]]) -> tuple[list[list[F]], tuple[int, ...]]:
    answer = [list(map(F, row)) for row in matrix]
    pivots = []
    cursor = 0
    width = len(answer[0]) if answer else 0
    for column in range(width):
        pivot = next(
            (row for row in range(cursor, len(answer)) if answer[row][column]),
            None,
        )
        if pivot is None:
            continue
        answer[cursor], answer[pivot] = answer[pivot], answer[cursor]
        divisor = answer[cursor][column]
        answer[cursor] = [value / divisor for value in answer[cursor]]
        for row in range(len(answer)):
            if row == cursor or not answer[row][column]:
                continue
            multiplier = answer[row][column]
            answer[row] = [
                left - multiplier * right
                for left, right in zip(answer[row], answer[cursor])
            ]
        pivots.append(column)
        cursor += 1
        if cursor == len(answer):
            break
    return answer, tuple(pivots)


def determinant(matrix: list[list[F]]) -> F:
    work = [list(map(F, row)) for row in matrix]
    size = len(work)
    answer = F(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return F(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            answer = -answer
        divisor = work[column][column]
        answer *= divisor
        for row in range(column + 1, size):
            if not work[row][column]:
                continue
            multiplier = work[row][column] / divisor
            for other in range(column, size):
                work[row][other] -= multiplier * work[column][other]
    return answer


def solve_unique(
    matrix: list[list[F]], rhs: list[F], width: int
) -> tuple[F, ...] | None:
    augmented = [list(map(F, row)) + [F(bound)] for row, bound in zip(matrix, rhs)]
    reduced, pivots = rref(augmented)
    if any(not any(row[:width]) and row[width] for row in reduced):
        return None
    coefficient_rank = sum(1 for pivot in pivots if pivot < width)
    if coefficient_rank != width:
        return None
    answer = [F(0)] * width
    for row in reduced:
        pivot = next((column for column in range(width) if row[column]), None)
        if pivot is not None:
            answer[pivot] = row[width] / row[pivot]
    return tuple(answer)


def cover_matrix(rows: tuple[int, ...], n: int = N) -> tuple[list[list[F]], list[F]]:
    matrix: list[list[F]] = []
    rhs: list[F] = []
    for player in range(2, n):
        matrix.append([
            *(F(int(bool(row >> player & 1))) for row in rows),
            F(-1),
        ])
        rhs.append(F(0))
    matrix.append([
        *(F(int(bool(row & 1)) + int(bool(row & 2))) for row in rows),
        F(-2),
    ])
    rhs.append(F(1))
    return matrix, rhs


def rank_witness(matrix: list[list[F]], width: int) -> tuple[tuple[int, ...], F]:
    for indices in itertools.combinations(range(len(matrix)), width):
        minor = [[matrix[row][column] for column in range(width)] for row in indices]
        value = determinant(minor)
        if value:
            return tuple(indices), value
    raise AssertionError(("full-column-rank witness missing", matrix, width))


def normalized_cover(rows: tuple[int, ...], n: int = N):
    matrix, rhs = cover_matrix(rows, n)
    width = len(rows) + 1
    solution = solve_unique(matrix, rhs, width)
    if solution is None:
        return None
    weights, eta = solution[:-1], solution[-1]
    if min(weights) <= 0 or eta < 0:
        return None
    loads = tuple(
        sum((weight for weight, row in zip(weights, rows) if row >> player & 1), F(0))
        for player in range(n)
    )
    alpha = (loads[R] - eta, loads[H] - eta)
    if min(alpha) <= 0 or sum(alpha, F(0)) != 1:
        return None
    expected = (eta + alpha[0], eta + alpha[1]) + (eta,) * (n - 2)
    if loads != expected:
        raise AssertionError(("cover replay failed", rows, loads, expected))
    witness_rows, minor = rank_witness(matrix, width)
    outsider_incidence = [
        [F(int(bool(row >> player & 1))) for row in rows]
        for player in range(2, n)
    ]
    if eta > 0:
        outsider_rank_rows, outsider_minor = rank_witness(
            outsider_incidence, len(rows)
        )
        outsider_rank = len(rows)
    else:
        # The sole zero-ambient cover is {r,h}; its outsider matrix is zero.
        outsider_rank_rows, outsider_minor, outsider_rank = (), F(0), 0
    return {
        "weights": weights,
        "eta": eta,
        "alpha": alpha,
        "loads": loads,
        "rank": width,
        "rank_rows": witness_rows,
        "rank_minor_determinant": minor,
        "outsider_incidence_rank": outsider_rank,
        "outsider_rank_rows": outsider_rank_rows,
        "outsider_rank_minor_determinant": outsider_minor,
    }


def permute_mask(mask: int, permutation: tuple[int, ...]) -> int:
    answer = 0
    for player in range(N):
        if mask >> player & 1:
            answer |= 1 << permutation[player]
    return answer


SAFE_GROUP = tuple(
    tuple(
        ({A: B, B: A}.get(player, player) if swap_ab else player)
        for player in range(N)
    )
    for swap_ab in (False, True)
)
SAFE_GROUP = tuple(
    tuple(
        ({J: K, K: J}.get(player, player) if swap_jk else player)
        for player in permutation
    )
    for permutation in SAFE_GROUP
    for swap_jk in (False, True)
)


def orbit(rows: tuple[int, ...]) -> frozenset[tuple[int, ...]]:
    return frozenset(
        tuple(sorted(permute_mask(row, permutation) for row in rows))
        for permutation in SAFE_GROUP
    )


def canonical_rows(rows: tuple[int, ...]) -> tuple[int, ...]:
    return min(orbit(rows))


def enumerate_covers():
    candidates = tuple(
        row for row in range(1, FULL)
        if row.bit_count() >= 2 or row in OUTSIDER_SINGLETONS
    )
    covers = {}
    for size in range(1, 5):
        for rows in itertools.combinations(candidates, size):
            certificate = normalized_cover(rows)
            if certificate is not None:
                covers[rows] = certificate
    return candidates, covers


def vec(**terms: int) -> list[F]:
    names = ("M", "q", "zj", "zk", "ell", "dh", "da", "db", "Lj", "Lk")
    index = {name: position for position, name in enumerate(names)}
    answer = [F(0)] * len(names)
    for name, coefficient in terms.items():
        answer[index[name]] = F(coefficient)
    return answer


def add(*rows: list[F]) -> list[F]:
    return [sum((row[column] for row in rows), F(0)) for column in range(10)]


def scale(row: list[F], coefficient: int | F) -> list[F]:
    return [F(coefficient) * value for value in row]


def x_minus_z(mask: int) -> list[F]:
    pieces = []
    if mask >> R & 1:
        pieces.append(vec(ell=1))
    if mask >> H & 1:
        pieces.append(vec(dh=-1))
    if mask >> A & 1:
        pieces.append(vec(da=-1))
    if mask >> B & 1:
        pieces.append(vec(db=-1))
    if mask >> J & 1:
        pieces.append(vec(Lj=1))
    if mask >> K & 1:
        pieces.append(vec(Lk=1))
    return add(*pieces) if pieces else [F(0)] * 10


def scalar_system(rows: tuple[int, ...] = ()):
    """Necessary allocation relaxation for a reserve-failing root.

    Strict homogeneous inequalities are normalized to common margin one.
    Deliberately no x-order inequalities are used, making boundary
    infeasibility stronger than the ordered-cell statement.
    """
    aub: list[list[F]] = []
    bub: list[F] = []
    aeq: list[list[F]] = []
    beq: list[F] = []

    def ge(row: list[F], rhs: int = 0):
        aub.append(scale(row, -1))
        bub.append(F(-rhs))

    ge(add(vec(M=1), vec(q=-1)), 1)
    ge(add(vec(q=1), vec(zj=-1)), 1)
    ge(add(vec(q=1), vec(zk=-1)), 1)
    ge(vec(zj=1))
    ge(vec(zk=1))
    for name in ("ell", "dh", "da", "db"):
        ge(vec(**{name: 1}), 1)
    ge(vec(Lj=1))
    ge(vec(Lk=1))
    # Nonnegative allocation x.
    ge(add(vec(M=1), vec(dh=-1)))
    ge(add(vec(q=1), vec(da=-1)))
    ge(add(vec(q=1), vec(db=-1)))
    # Efficiency.
    aeq.append(add(vec(dh=1), vec(da=1), vec(db=1),
                   vec(ell=-1), vec(Lj=-1), vec(Lk=-1)))
    beq.append(F(0))
    # Reserve failure E-ell>4 A_rho/3 implies every two-gain sum > ell.
    for left, right in (("dh", "da"), ("dh", "db"), ("da", "db")):
        ge(add(vec(**{left: 1}), vec(**{right: 1}), vec(ell=-1)), 1)
    for row in rows:
        if row == 1 << J:
            aeq.append(vec(zj=1))
            beq.append(F(0))
        elif row == 1 << K:
            aeq.append(vec(zk=1))
            beq.append(F(0))
        ge(x_minus_z(row))
    return aub, bub, aeq, beq


def exact_lp_status(rows: tuple[int, ...] = ()):
    status, optimum, point = exact_linprog(
        [F(0)] * 10, *scalar_system(rows)
    )
    return status, optimum, point


def root_witness_status(rows: tuple[int, ...]):
    """Add a nonnegative efficient witness with y_r=0 to scalar_system."""
    aub10, bub, aeq10, beq = scalar_system(rows)
    aub = [row + [F(0)] * 5 for row in aub10]
    aeq = [row + [F(0)] * 5 for row in aeq10]

    # Witness variables are (y_h,y_a,y_b,y_j,y_k).
    for offset in range(5):
        row = [F(0)] * 15
        row[10 + offset] = F(-1)
        aub.append(row)
        bub.append(F(0))
    total_row = vec(M=-2, q=-2, zj=-1, zk=-1) + [F(1)] * 5
    aeq.append(total_row)
    beq.append(F(0))

    for mask in rows:
        row = [F(0)] * 15
        if mask >> R & 1: row[0] += F(1)
        if mask >> H & 1: row[0] += F(1); row[10] -= F(1)
        if mask >> A & 1: row[1] += F(1); row[11] -= F(1)
        if mask >> B & 1: row[1] += F(1); row[12] -= F(1)
        if mask >> J & 1: row[2] += F(1); row[13] -= F(1)
        if mask >> K & 1: row[3] += F(1); row[14] -= F(1)
        aub.append(row)
        bub.append(F(0))

    status, optimum, point = exact_linprog([F(0)] * 15, aub, bub, aeq, beq)
    return status, optimum, point


def weighted_hypergraph_key(rows: tuple[int, ...], weights: tuple[F, ...]):
    """Canonical weighted non-top hypergraph, forgetting top decorations."""
    candidates = []
    for permutation in itertools.permutations(range(4)):
        decorated = []
        for row, weight in zip(rows, weights):
            trace = 0
            for old in range(4):
                if row >> (old + 2) & 1:
                    trace |= 1 << permutation[old]
            decorated.append((trace, weight))
        candidates.append(tuple(sorted(decorated)))
    return min(candidates)


def render_certificate(certificate: dict) -> dict:
    return {
        "weights": [qstr(value) for value in certificate["weights"]],
        "eta": qstr(certificate["eta"]),
        "alpha": [qstr(value) for value in certificate["alpha"]],
        "loads": [qstr(value) for value in certificate["loads"]],
        "rank": certificate["rank"],
        "rank_rows": list(certificate["rank_rows"]),
        "rank_minor_determinant": qstr(certificate["rank_minor_determinant"]),
        "outsider_incidence_rank": certificate["outsider_incidence_rank"],
        "outsider_rank_rows": list(certificate["outsider_rank_rows"]),
        "outsider_rank_minor_determinant": qstr(
            certificate["outsider_rank_minor_determinant"]
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    candidates, covers = enumerate_covers()
    size_counts = Counter(len(rows) for rows in covers)
    expected_sizes = {1: 1, 2: 7, 3: 96, 4: 703}
    if dict(size_counts) != expected_sizes or len(covers) != 807:
        raise AssertionError(("labelled cover census changed", size_counts, len(covers)))

    grouped: dict[tuple[int, ...], set[tuple[int, ...]]] = defaultdict(set)
    for rows in covers:
        grouped[canonical_rows(rows)].add(rows)
    orbit_sizes = Counter(len(rows) for rows in grouped)
    expected_orbit_sizes = {1: 1, 2: 4, 3: 37, 4: 217}
    if dict(orbit_sizes) != expected_orbit_sizes or len(grouped) != 259:
        raise AssertionError(("safe colored orbit census changed", orbit_sizes, len(grouped)))

    # Expansion is checked as a set identity, not merely by matching totals.
    expanded = set()
    for representative, members in grouped.items():
        reconstructed = set(orbit(representative))
        if reconstructed != members:
            raise AssertionError(("orbit expansion mismatch", representative,
                                  sorted(reconstructed ^ members)))
        expanded.update(reconstructed)
    if expanded != set(covers):
        raise AssertionError("safe-orbit expansion failed to recover labelled census")

    eta_zero = [rows for rows, certificate in covers.items() if certificate["eta"] == 0]
    if eta_zero != [(3,)]:
        raise AssertionError(("unexpected eta-zero covers", eta_zero))
    residual = {rows: certificate for rows, certificate in covers.items()
                if certificate["eta"] > 0}
    if any(certificate["outsider_incidence_rank"] != len(rows)
           for rows, certificate in residual.items()):
        raise AssertionError("positive-ambient extreme cover lost outsider column rank")
    residual_orbits = {canonical_rows(rows) for rows in residual}
    if len(residual) != 806 or len(residual_orbits) != 258:
        raise AssertionError(("pair-slack residual count changed",
                              len(residual), len(residual_orbits)))

    support_two_orbits = tuple(sorted(rows for rows in grouped if len(rows) == 2))
    expected_support_two = ((7, 59), (15, 51), (19, 47), (23, 43))
    if support_two_orbits != expected_support_two:
        raise AssertionError(("support-two colored classification changed",
                              support_two_orbits))
    support_two_status = {
        rows: exact_lp_status(rows)[0] for rows in support_two_orbits
    }
    expected_support_two_status = {
        (7, 59): "infeasible",
        (15, 51): "infeasible",
        (19, 47): "optimal",
        (23, 43): "optimal",
    }
    if support_two_status != expected_support_two_status:
        raise AssertionError(("support-two transition status changed",
                              support_two_status))

    support_three_scalar_feasible = tuple(sorted(
        rows for rows in grouped
        if len(rows) == 3 and exact_lp_status(rows)[0] == "optimal"
    ))
    expected_support_three_feasible = ((5, 18, 43), (5, 19, 42), (5, 19, 43))
    if support_three_scalar_feasible != expected_support_three_feasible:
        raise AssertionError(("support-three scalar boundary changed",
                              support_three_scalar_feasible))
    support_three_root_feasible = tuple(
        rows for rows in support_three_scalar_feasible
        if root_witness_status(rows)[0] == "optimal"
    )
    if support_three_root_feasible != ((5, 19, 42),):
        raise AssertionError(("support-three root boundary changed",
                              support_three_root_feasible))

    boundary = {
        representative: members for representative, members in grouped.items()
        if any(row in OUTSIDER_SINGLETONS for row in representative)
    }
    if tuple(sorted(boundary, key=lambda rows: (len(rows), rows))) != EXPECTED_BOUNDARY_REPRESENTATIVES:
        raise AssertionError(("outsider-singleton boundary orbit list changed",
                              sorted(boundary)))
    boundary_results = []
    for representative in EXPECTED_BOUNDARY_REPRESENTATIVES:
        status, _optimum, _point = exact_lp_status(representative)
        if status != "infeasible":
            raise AssertionError(("boundary cover survived reserve relaxation",
                                  representative, status, _point))
        boundary_results.append({
            "rows": list(representative),
            "orbit_size": len(boundary[representative]),
            "cover": render_certificate(covers[representative]),
            "scalar_system": {
                "status": status,
                "variables": ["M", "q", "zj", "zk", "ell", "dh", "da", "db", "Lj", "Lk"],
                "strict_margin": "1",
                "uses_x_order": False,
                "reserve_relaxation": "each two-gain sum - ell >= 1",
                "singleton_zero_equalities": [
                    name for row, name in ((1 << J, "zj=0"), (1 << K, "zk=0"))
                    if row in representative
                ],
            },
        })

    base_status, _base_optimum, base_point = exact_lp_status()
    if base_status != "optimal":
        raise AssertionError(("fail-open scalar base is infeasible", base_status))

    # Classify every balanced three-edge non-top hypergraph, independently of
    # its top decorations.  The key retains its exact edge weights.
    hypergraphs: dict[tuple, dict] = {}
    for rows, certificate in covers.items():
        if len(rows) != 3:
            continue
        key = weighted_hypergraph_key(rows, certificate["weights"])
        item = hypergraphs.setdefault(key, {
            "labelled_supports": 0,
            "colored_orbits": set(),
            "eta_values": set(),
            "alpha_values": set(),
        })
        item["labelled_supports"] += 1
        item["colored_orbits"].add(canonical_rows(rows))
        item["eta_values"].add(certificate["eta"])
        item["alpha_values"].add(certificate["alpha"])
        degrees = [
            sum((weight for row, weight in zip(rows, certificate["weights"])
                 if row >> player & 1), F(0))
            for player in range(2, N)
        ]
        if degrees != [certificate["eta"]] * 4:
            raise AssertionError(("three-edge hypergraph is not balanced", rows, degrees))
    if sum(item["labelled_supports"] for item in hypergraphs.values()) != 96:
        raise AssertionError("three-edge hypergraph classification lost a support")
    if len({orbit for item in hypergraphs.values() for orbit in item["colored_orbits"]}) != 37:
        raise AssertionError("three-edge hypergraph classification lost a colored orbit")
    rendered_hypergraphs = []
    for key, item in sorted(hypergraphs.items()):
        rendered_hypergraphs.append({
            "weighted_edges": [
                {"non_top_mask": trace, "weight": qstr(weight)}
                for trace, weight in key
            ],
            "labelled_supports": item["labelled_supports"],
            "colored_orbits": len(item["colored_orbits"]),
            "eta_values": sorted(map(qstr, item["eta_values"])),
            "alpha_values": sorted(
                ([qstr(left), qstr(right)] for left, right in item["alpha_values"])
            ),
        })

    calibrations = {}
    for name, rows, expected in (
        ("PXC88", (27, 39, 66), ((F(1, 3),) * 3, F(1, 3), (F(1, 3), F(2, 3)))),
        ("PXC90", (23, 27, 39, 75, 114),
         ((F(1, 7), F(1, 7), F(2, 7), F(2, 7), F(1, 7)),
          F(3, 7), (F(3, 7), F(4, 7)))),
    ):
        certificate = normalized_cover(rows, n=7)
        if certificate is None:
            raise AssertionError((name, "calibration cover missing"))
        observed = (certificate["weights"], certificate["eta"], certificate["alpha"])
        if observed != expected:
            raise AssertionError((name, "calibration changed", observed, expected))
        calibrations[name] = {"rows": list(rows), "cover": render_certificate(certificate)}

    orbit_records = []
    for representative, members in sorted(grouped.items(), key=lambda item: (len(item[0]), item[0])):
        orbit_records.append({
            "rows": list(representative),
            "orbit_size": len(members),
            "contains_outsider_singleton": any(
                row in OUTSIDER_SINGLETONS for row in representative
            ),
            "cover": render_certificate(covers[representative]),
        })

    payload = {
        "claim": "complete exact n=6 positive-extreme two-top cover rank census",
        "roles": ["r", "h", "a", "b", "j", "k"],
        "safe_symmetry": "S_{a,b} x S_{j,k}; r and h remain distinguished",
        "candidate_rows": len(candidates),
        "labelled_covers": len(covers),
        "labelled_size_counts": {str(size): count for size, count in sorted(size_counts.items())},
        "colored_orbits": len(grouped),
        "colored_orbit_size_counts": {
            str(size): count for size, count in sorted(orbit_sizes.items())
        },
        "orbit_expansion": {
            "checked_as_set_equality": True,
            "expanded_labelled_covers": len(expanded),
        },
        "pair_slack_residual": {
            "eta_zero_supports": [list(rows) for rows in eta_zero],
            "labelled_covers": len(residual),
            "colored_orbits": len(residual_orbits),
        },
        "small_support_colored_classification": {
            "support_two_orbits": [list(rows) for rows in support_two_orbits],
            "support_two_transition": [
                {
                    "rows": list(rows),
                    "scalar_status": support_two_status[rows],
                    "route": {
                        (7, 59): "scalar reserve/comparison no-go",
                        (15, 51): "scalar reserve/comparison no-go",
                        (19, 47): "zero-loss outsider-partition blocker audit",
                        (23, 43): "PXC93 split-cover blocker audit",
                    }[rows],
                }
                for rows in support_two_orbits
            ],
            "support_three_orbits": 37,
            "support_three_scalar_infeasible": 34,
            "support_three_scalar_feasible": [
                list(rows) for rows in support_three_scalar_feasible
            ],
            "support_three_root_witness_feasible": [
                list(rows) for rows in support_three_root_feasible
            ],
            "support_three_root_witness_infeasible": [
                list(rows) for rows in support_three_scalar_feasible
                if rows not in support_three_root_feasible
            ],
        },
        "rank_support_theorem": {
            "equation_rank_bound": 5,
            "positive_eta_consumes_one_basic_variable": True,
            "maximum_positive_row_support": 4,
            "all_positive_eta_covers_have_full_outsider_incidence_column_rank": True,
            "statement": (
                "after eliminating the two top coefficients, four ambient-load "
                "equations plus normalization have rank at most five; at a positive-eta "
                "extreme point eta is basic, so at most four row weights are positive; "
                "the outsider incidence columns of every such extreme cover are "
                "linearly independent"
            ),
        },
        "outsider_singleton_boundary": {
            "labelled_covers": sum(len(members) for members in boundary.values()),
            "colored_orbits": len(boundary),
            "all_scalar_reserve_infeasible": True,
            "orbits": boundary_results,
        },
        "scalar_fail_open_control": {
            "status": base_status,
            "witness": {
                name: qstr(value) for name, value in zip(
                    ("M", "q", "zj", "zk", "ell", "dh", "da", "db", "Lj", "Lk"),
                    base_point,
                )
            },
        },
        "size_three_balanced_hypergraphs": {
            "classes": len(rendered_hypergraphs),
            "labelled_supports": 96,
            "colored_orbits": 37,
            "classification": rendered_hypergraphs,
        },
        "seven_player_calibrations": calibrations,
        "orbits": orbit_records,
        "scope": (
            "complete incidence/rank theorem for positive extreme two-top covers "
            "in the colored n=6 role cell; boundary scalar LPs are necessary "
            "reserve relaxations, not a classification of later selector blockers"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
