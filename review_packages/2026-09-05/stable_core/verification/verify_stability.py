"""Exact core-stability certificate for the reported six-player perturbation.

Run from any directory:

    python3 verify_stability.py

The verifier uses only the Python standard library.  For a segment core
[A,B], put d=B-A.  Domination by an endpoint is cut by the coordinate
hyperplanes y_i=A_i and y_i=B_i.  For a coalition tight along the whole
segment, feasibility of

    A_i + t*d_i > y_i  (i in S),  0 <= t <= 1

is cut, in addition, by

    d_j*(y_i-A_i) = d_i*(y_j-A_j)

for d_i>0>d_j.  Together with the individual-rationality floors, these
hyperplanes contain every vertex of the undominated-imputation set.

For the reported game and an equivalent alternate normalization retained as
a regression case, there are 12 distinct endpoint-coordinate planes and nine
opposite-sign pair planes.  The program enumerates all C(21,5)=20,349 bases
in the five-dimensional efficiency plane, solves them in exact rational
arithmetic, and constructs an exact dominating core point for every
outside-core imputation vertex.  Any failed structural check, changed count,
or undominated vertex makes the process exit nonzero.
"""

import itertools
import json
import math
import os
import sys
from data import strict_json_load
from fractions import Fraction as F


HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATHS = (
    os.path.join(HERE, "supplement_data.json"),
)
EXPECTED = {
    "stable_witness_1": {
        "planes": 21,
        "bases": 20349,
        "nonsingular_bases": 8264,
        "intersections": 230,
        "imputations": 104,
        "core_vertices": 2,
        "outside_core": 102,
        "dominated": 102,
    },
    "stable_witness_2": {
        "planes": 21,
        "bases": 20349,
        "nonsingular_bases": 8264,
        "intersections": 230,
        "imputations": 104,
        "core_vertices": 2,
        "outside_core": 102,
        "dominated": 102,
    },
}


def load_data():
    loaded = None
    for path in DATA_PATHS:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as stream:
                candidate = strict_json_load(stream)
            if loaded is None:
                loaded = candidate
            elif loaded != candidate:
                raise ValueError("the two supplement_data.json copies differ")
    if loaded is None:
        raise FileNotFoundError("supplement_data.json not found")
    return loaded


def members(coalition, n):
    return [i for i in range(n) if coalition >> i & 1]


def parse_set(name):
    coalition = 0
    text = name.strip("{}")
    if not text:
        return coalition
    for player in text.split(","):
        index = int(player)
        if index < 1 or index > 6 or coalition & (1 << (index - 1)):
            raise ValueError("invalid or repeated player in coalition")
        coalition |= 1 << (index - 1)
    return coalition


def parse_game(table, n):
    game = [F(0)] * (1 << n)
    seen = set()
    for name, value in table.items():
        coalition = parse_set(name)
        if coalition in seen:
            raise ValueError("duplicate coalition " + name)
        seen.add(coalition)
        game[coalition] = F(value)
    if any(coalition <= 0 or coalition >= 1 << n for coalition in seen):
        raise ValueError("game table contains an invalid coalition")
    if seen != set(range(1, 1 << n)):
        raise ValueError("game table must specify every nonempty coalition exactly once")
    return game


def coalition_sum(vector, coalition, n):
    return sum(vector[i] for i in range(n) if coalition >> i & 1)


def in_core(game, vector, n):
    grand = (1 << n) - 1
    return (
        sum(vector) == game[grand]
        and all(
            coalition_sum(vector, coalition, n) >= game[coalition]
            for coalition in range(1, grand)
        )
    )


def matrix_rank(rows):
    matrix = [[F(value) for value in row] for row in rows]
    if not matrix:
        return 0
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next(
            (row for row in range(rank, len(matrix)) if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][column]
        matrix[rank] = [value / scale for value in matrix[rank]]
        for row in range(len(matrix)):
            if row == rank or not matrix[row][column]:
                continue
            scale = matrix[row][column]
            matrix[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(matrix[row], matrix[rank])
            ]
        rank += 1
    return rank


def solve_square(rows, rhs):
    size = len(rhs)
    matrix = [
        [F(value) for value in rows[row]] + [F(rhs[row])]
        for row in range(size)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if matrix[row][column]),
            None,
        )
        if pivot is None:
            return None
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        scale = matrix[column][column]
        matrix[column] = [value / scale for value in matrix[column]]
        for row in range(size):
            if row == column or not matrix[row][column]:
                continue
            scale = matrix[row][column]
            matrix[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(matrix[row], matrix[column])
            ]
    return tuple(matrix[row][-1] for row in range(size))


def lcm(left, right):
    if not left or not right:
        return 0
    return abs(left * right) // math.gcd(left, right)


def canonical_plane(row, rhs):
    values = [F(value) for value in row] + [F(rhs)]
    common_denominator = 1
    for value in values:
        common_denominator = lcm(common_denominator, value.denominator)
    integers = [
        value.numerator * (common_denominator // value.denominator)
        for value in values
    ]
    divisor = 0
    for value in integers:
        divisor = math.gcd(divisor, abs(value))
    if not divisor or not any(integers[:-1]):
        raise ValueError("invalid hyperplane")
    integers = [value // divisor for value in integers]
    first = next(value for value in integers[:-1] if value)
    if first < 0:
        integers = [-value for value in integers]
    return tuple(integers)


def segment_core_certificate(game, endpoint_a, endpoint_b, n):
    grand = (1 << n) - 1
    direction = tuple(endpoint_b[i] - endpoint_a[i] for i in range(n))
    if endpoint_a == endpoint_b:
        raise ValueError("core endpoints coincide")
    if not in_core(game, endpoint_a, n) or not in_core(game, endpoint_b, n):
        raise ValueError("a stated endpoint is not in the core")

    fully_tight = [
        coalition
        for coalition in range(1, grand)
        if (
            coalition_sum(endpoint_a, coalition, n)
            == game[coalition]
            == coalition_sum(endpoint_b, coalition, n)
        )
    ]
    if any(
        game[coalition] + game[grand ^ coalition] != game[grand]
        for coalition in fully_tight
    ):
        raise ValueError("a fully-tight row is not a universal core equality")
    tight_rows = [[F(1)] * n] + [
        [F(1) if coalition >> i & 1 else F(0) for i in range(n)]
        for coalition in fully_tight
    ]
    if matrix_rank(tight_rows) != n - 1:
        raise ValueError("fully-tight equalities do not force an affine line")

    lower_bounds = []
    upper_bounds = []
    for coalition in range(1, grand):
        value_at_a = coalition_sum(endpoint_a, coalition, n)
        slope = coalition_sum(direction, coalition, n)
        offset = game[coalition] - value_at_a
        if slope > 0:
            lower_bounds.append(offset / slope)
        elif slope < 0:
            upper_bounds.append(offset / slope)
        elif offset > 0:
            raise ValueError("the asserted core line violates a core constraint")
    lower = max(lower_bounds)
    upper = min(upper_bounds)
    if lower != 0 or upper != 1:
        raise ValueError(
            "core interval on its affine line is "
            + str((lower, upper))
            + ", not [0,1]"
        )
    return direction, fully_tight


def build_planes(game, endpoint_a, endpoint_b, direction, n):
    planes = []
    seen = set()

    def add(row, rhs, tag):
        key = canonical_plane(row, rhs)
        if key not in seen:
            seen.add(key)
            planes.append((tuple(row), F(rhs), tag))

    for i in range(n):
        for label, value in (
            ("floor", game[1 << i]),
            ("A", endpoint_a[i]),
            ("B", endpoint_b[i]),
        ):
            row = [F(0)] * n
            row[i] = F(1)
            add(row, value, (label, i))

    increasing = [i for i in range(n) if direction[i] > 0]
    decreasing = [i for i in range(n) if direction[i] < 0]
    for i in increasing:
        for j in decreasing:
            row = [F(0)] * n
            row[i] = direction[j]
            row[j] = -direction[i]
            rhs = (
                direction[j] * endpoint_a[i]
                - direction[i] * endpoint_a[j]
            )
            add(row, rhs, ("cross", i, j))
    return planes


def exact_dominator(game, endpoint_a, endpoint_b, direction, y, n):
    """Return (coalition, t, x_t) if the segment core dominates y."""
    grand = (1 << n) - 1
    for coalition in range(1, grand):
        value_a = coalition_sum(endpoint_a, coalition, n)
        value_b = coalition_sum(endpoint_b, coalition, n)
        value = game[coalition]

        if value_a == value < value_b:
            if all(endpoint_a[i] > y[i] for i in members(coalition, n)):
                return coalition, F(0), endpoint_a
            continue
        if value_b == value < value_a:
            if all(endpoint_b[i] > y[i] for i in members(coalition, n)):
                return coalition, F(1), endpoint_b
            continue
        if value_a != value or value_b != value:
            continue

        lower = F(0)
        upper = F(1)
        possible = True
        for i in members(coalition, n):
            if direction[i] > 0:
                lower = max(lower, (y[i] - endpoint_a[i]) / direction[i])
            elif direction[i] < 0:
                upper = min(upper, (y[i] - endpoint_a[i]) / direction[i])
            elif not endpoint_a[i] > y[i]:
                possible = False
                break
        if not possible or not lower < upper:
            continue
        parameter = (lower + upper) / 2
        core_point = tuple(
            endpoint_a[i] + parameter * direction[i] for i in range(n)
        )
        if (
            F(0) <= parameter <= F(1)
            and in_core(game, core_point, n)
            and coalition_sum(core_point, coalition, n) == value
            and all(core_point[i] > y[i] for i in members(coalition, n))
        ):
            return coalition, parameter, core_point
        raise AssertionError("constructed domination certificate is invalid")
    return None


def verify_witness(name, block):
    n = int(block["n"])
    if n != 6:
        raise ValueError(name + " is not a six-player game")
    grand = (1 << n) - 1
    game = parse_game(block["game_v"], n)
    endpoint_a = tuple(F(value) for value in block["generator_points"]["A"])
    endpoint_b = tuple(F(value) for value in block["generator_points"]["B"])

    if not all(
        game[coalition]
        == min(
            coalition_sum(endpoint_a, coalition, n),
            coalition_sum(endpoint_b, coalition, n),
        )
        for coalition in range(1, grand + 1)
    ):
        raise ValueError("game is not the stated two-point lower envelope")

    direction, fully_tight = segment_core_certificate(
        game, endpoint_a, endpoint_b, n
    )
    stored_fully_tight = {
        parse_set(coalition) for coalition in block["fully_tight_coalitions"]
    }
    if set(fully_tight) != stored_fully_tight:
        raise ValueError("stored fully-tight coalition list is not exact")

    planes = build_planes(game, endpoint_a, endpoint_b, direction, n)
    intersections = {}
    nonsingular_bases = 0
    for basis in itertools.combinations(range(len(planes)), n - 1):
        point = solve_square(
            [planes[index][0] for index in basis] + [[F(1)] * n],
            [planes[index][1] for index in basis] + [game[grand]],
        )
        if point is None:
            continue
        nonsingular_bases += 1
        intersections.setdefault(point, basis)

    imputations = [
        point
        for point in intersections
        if all(point[i] >= game[1 << i] for i in range(n))
    ]
    core_vertices = [point for point in imputations if in_core(game, point, n)]
    outside_core = [
        point for point in imputations if not in_core(game, point, n)
    ]
    certificates = {}
    for point in outside_core:
        certificate = exact_dominator(
            game, endpoint_a, endpoint_b, direction, point, n
        )
        if certificate is None:
            coordinates = ", ".join(str(value) for value in point)
            raise ValueError("undominated arrangement vertex: (" + coordinates + ")")
        certificates[point] = certificate

    actual = {
        "planes": len(planes),
        "bases": math.comb(len(planes), n - 1),
        "nonsingular_bases": nonsingular_bases,
        "intersections": len(intersections),
        "imputations": len(imputations),
        "core_vertices": len(core_vertices),
        "outside_core": len(outside_core),
        "dominated": len(certificates),
    }
    if actual != EXPECTED[name]:
        raise ValueError(
            "deterministic certificate counts changed: "
            + repr(actual)
            + " != "
            + repr(EXPECTED[name])
        )
    stored = block["stability_certificate"]
    stored_counts = {
        "planes": stored["planes"],
        "bases": stored["vertex_bases_scanned"],
        "nonsingular_bases": stored["nonsingular_bases"],
        "intersections": stored["distinct_intersections"],
        "imputations": stored["imputations"],
        "core_vertices": stored["core_vertices"],
        "outside_core": stored["outside_core_vertices_dominated"],
        "dominated": stored["outside_core_vertices_dominated"],
    }
    if stored_counts != actual or stored["survivors"] != 0:
        raise ValueError("stored certificate counts do not match recomputation")
    parameters = sorted({certificate[1] for certificate in certificates.values()})
    return actual, parameters


def main():
    data = load_data()
    failures = []
    for name in ("stable_witness_1", "stable_witness_2"):
        print(name)
        try:
            counts, parameters = verify_witness(name, data[name])
            print(
                "  ok   exact segment core; "
                + str(counts["planes"])
                + " planes, "
                + str(counts["bases"])
                + " bases"
            )
            print(
                "  ok   "
                + str(counts["nonsingular_bases"])
                + " nonsingular bases, "
                + str(counts["intersections"])
                + " distinct intersections"
            )
            print(
                "  ok   "
                + str(counts["imputations"])
                + " imputations: "
                + str(counts["core_vertices"])
                + " in the core, "
                + str(counts["outside_core"])
                + " outside and exactly dominated"
            )
            print(
                "  ok   domination parameters: "
                + ", ".join(str(value) for value in parameters)
            )
        except Exception as error:
            failures.append((name, str(error)))
            print("  FAIL " + str(error))

    print()
    if failures:
        print("*** STABILITY CERTIFICATE FAILED ***")
        for name, message in failures:
            print("  " + name + ": " + message)
        return 1
    print(
        "STABILITY CERTIFICATE PASSED. Every arrangement vertex is classified "
        "in exact rational arithmetic, and every outside-core imputation "
        "vertex has an exact dominating point in the segment core."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
