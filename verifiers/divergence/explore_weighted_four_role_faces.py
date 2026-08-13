#!/usr/bin/env python3
"""Exact discovery census for the unresolved weighted four-role faces.

The script samples deterministic lower-envelope role games.  Every sampled
game is exact by construction, and all selector computations use rational
LPs.  The census is discovery evidence only: it groups examples by the pair
slab endpoint equalities shared by weighted Lmin and weighted Lmax so that the
remaining human face classification can attack the right cases.
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))
from exactlp import exact_linprog  # noqa: E402

PAIR_REPRESENTATIVES = (0b0011, 0b0101, 0b1001)
NORMALIZED_OBSTRUCTION_GENERATORS = (
    (0, 5, 3, 4),
    (1, 3, 3, 5),
    (2, 4, 3, 3),
    (5, 0, 7, 0),
    (0, 6, 0, 6),
)


def compositions(total, parts=4):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in compositions(total - first, parts - 1):
            yield (first,) + tail


def coalition_sum(point, coalition):
    return sum((point[i] for i in range(4) if coalition >> i & 1), F(0))


def role_values(generators):
    return tuple(
        min(coalition_sum(point, coalition) for point in generators)
        for coalition in range(16)
    )


def core_lp(values, objective):
    aub, bub = [], []
    for coalition in range(1, 15):
        aub.append([F(-1 if coalition >> i & 1 else 0) for i in range(4)])
        bub.append(-values[coalition])
    return exact_linprog(
        list(map(F, objective)),
        aub,
        bub,
        [[F(1)] * 4],
        [values[15]],
    )


def exact_role_game(values):
    for coalition in range(16):
        objective = [F(1 if coalition >> i & 1 else 0) for i in range(4)]
        status, optimum, _ = core_lp(values, objective)
        if status != "optimal" or optimum != values[coalition]:
            return False
    return True


def exactify_role_game(values):
    """Replace every worth by its exact core minimum without changing core."""

    exact = []
    for coalition in range(16):
        objective = [F(1 if coalition >> i & 1 else 0) for i in range(4)]
        status, optimum, _ = core_lp(values, objective)
        if status != "optimal":
            return None
        exact.append(optimum)
    return tuple(exact)


def stage_rows(values, weights, pinned, free, mode):
    aub, bub = [], []
    for coalition in range(1, 15):
        aub.append(
            [F(-1 if coalition >> i & 1 else 0) for i in range(4)] + [F(0)]
        )
        bub.append(-values[coalition])
    aeq = [[F(1)] * 4 + [F(0)]]
    beq = [values[15]]
    for role, payoff in pinned.items():
        row = [F(0)] * 5
        row[role] = F(1)
        aeq.append(row)
        beq.append(payoff)
    for role in free:
        row = [F(0)] * 5
        if mode == "min":
            row[role], row[4] = F(-1), F(weights[role])
        else:
            row[role], row[4] = F(1), F(-weights[role])
        aub.append(row)
        bub.append(F(0))
    return aub, bub, aeq, beq


def weighted_lex_point(values, weights, mode):
    pinned, free, trace = {}, set(range(4)), []
    while free:
        aub, bub, aeq, beq = stage_rows(values, weights, pinned, free, mode)
        objective = [F(0)] * 5
        objective[4] = F(-1 if mode == "min" else 1)
        status, optimum, _ = exact_linprog(objective, aub, bub, aeq, beq)
        if status != "optimal":
            raise AssertionError((mode, status))
        level = -optimum if mode == "min" else optimum
        level_row = [F(0)] * 5
        level_row[4] = F(1)
        aeq.append(level_row)
        beq.append(level)
        newly = []
        for role in sorted(free):
            direction = [F(0)] * 5
            direction[role] = F(-1 if mode == "min" else 1)
            status, extreme, _ = exact_linprog(direction, aub, bub, aeq, beq)
            if status != "optimal":
                raise AssertionError((mode, role, status))
            forced = -extreme if mode == "min" else extreme
            if forced == weights[role] * level:
                newly.append(role)
        if not newly:
            raise AssertionError((mode, "stage pinned nobody", level))
        for role in newly:
            pinned[role] = weights[role] * level
            free.remove(role)
        trace.append((level, tuple(newly)))
    return tuple(pinned[i] for i in range(4)), tuple(trace)


def active_pair_endpoints(values, point):
    total = values[15]
    labels = set()
    for index, coalition in enumerate(PAIR_REPRESENTATIVES):
        value = coalition_sum(point, coalition)
        lower = values[coalition]
        upper = total - values[15 ^ coalition]
        if value == lower:
            labels.add((index, "L"))
        if value == upper:
            labels.add((index, "U"))
    return labels


def common_face_unit_minima(values, weights, common):
    labels = []
    for label in sorted(common):
        if label[0] not in {partition for partition, _ in labels}:
            labels.append(label)
        if len(labels) == 2:
            break
    if len(labels) < 2:
        return None
    aub, bub = [], []
    for coalition in range(1, 15):
        aub.append([F(-1 if coalition >> i & 1 else 0) for i in range(4)])
        bub.append(-values[coalition])
    aeq = [[F(1)] * 4]
    beq = [values[15]]
    for partition, endpoint in labels:
        coalition = PAIR_REPRESENTATIVES[partition]
        aeq.append([F(1 if coalition >> i & 1 else 0) for i in range(4)])
        beq.append(
            values[coalition]
            if endpoint == "L"
            else values[15] - values[15 ^ coalition]
        )
    minima = {}
    for role, weight in enumerate(weights):
        if weight != 1:
            continue
        objective = [F(1 if i == role else 0) for i in range(4)]
        status, optimum, _ = exact_linprog(objective, aub, bub, aeq, beq)
        if status != "optimal":
            raise AssertionError(("common face", labels, role, status))
        minima[role] = optimum
    return labels, minima


def common_face_ambient_endowments(point, labels):
    coalitions = [PAIR_REPRESENTATIVES[partition] for partition, _ in labels]
    directions = []
    for candidate in itertools.product((-1, 1), repeat=4):
        if sum(candidate) != 0:
            continue
        if all(
            sum(candidate[i] for i in range(4) if coalition >> i & 1) == 0
            for coalition in coalitions
        ):
            directions.append(candidate)
    if not directions:
        raise AssertionError(("common face direction", labels))
    direction = min(directions, key=lambda row: tuple(-value for value in row))
    lower = -min(point[i] for i in range(4) if direction[i] == 1)
    upper = min(point[i] for i in range(4) if direction[i] == -1)
    endowments = tuple(
        point[i] + (lower if direction[i] == 1 else -upper) for i in range(4)
    )
    return direction, endowments, upper - lower


def target(n):
    return F(4 * n, n * n - (n % 2))


def pair_coordinates(point):
    return (point[0] + point[1], point[0] + point[2], point[0] + point[3])


def pair_coordinate_distance(left, right):
    delta = tuple(a - b for a, b in zip(pair_coordinates(left), pair_coordinates(right)))
    return max(sum(abs(value) for value in delta), 2 * max(abs(value) for value in delta))


def encode_trace(trace):
    return [
        {"level": str(level), "roles": list(roles)} for level, roles in trace
    ]


def encode_row(row):
    encoded = {
        "n": row["n"],
        "weights": list(row["weights"]),
        "total": str(row["total"]),
        "generators": [list(point) for point in row["generators"]],
        "values": [str(value) for value in row["values"]],
        "lmin": [str(value) for value in row["lmin"]],
        "lmax": [str(value) for value in row["lmax"]],
        "lmin_trace": encode_trace(row["lmin_trace"]),
        "lmax_trace": encode_trace(row["lmax_trace"]),
        "active_lmin": [list(label) for label in sorted(row["active_lmin"])],
        "active_lmax": [list(label) for label in sorted(row["active_lmax"])],
        "common_pair_endpoints": [
            list(label) for label in sorted(row["common_pair_endpoints"])
        ],
        "face_class": row["face_class"],
        "overlap_ratio": str(row["ratio"]),
        "atomic_target": str(row["target"]),
        "target_margin": str(row["ratio"] - row["target"]),
        "pair_coordinates_lmin": [str(value) for value in pair_coordinates(row["lmin"])],
        "pair_coordinates_lmax": [str(value) for value in pair_coordinates(row["lmax"])],
    }
    if "unit_role_minima_on_common_face" in row:
        encoded["common_face_labels_audited"] = [
            list(label) for label in row["common_face_labels_audited"]
        ]
        encoded["unit_role_minima_on_common_face"] = {
            str(role): str(value)
            for role, value in row["unit_role_minima_on_common_face"].items()
        }
        encoded["common_face_direction"] = list(row["common_face_direction"])
        encoded["ambient_nonnegative_endowments"] = [
            str(value) for value in row["ambient_nonnegative_endowments"]
        ]
        encoded["ambient_nonnegative_width"] = str(row["ambient_nonnegative_width"])
    return encoded


def sample_game(rng, total, generator_count, weights):
    pool = list(compositions(total))
    selected = []
    for role, weight in enumerate(weights):
        if weight == 1:
            choices = [point for point in pool if point[role] == 0]
            point = rng.choice(choices)
            if point not in selected:
                selected.append(point)
    remaining = [point for point in pool if point not in selected]
    selected.extend(rng.sample(remaining, max(0, generator_count - len(selected))))
    return tuple(selected)


def sample_slab_values(rng, total, weights):
    """Sample the complete four-role interval/slab representation."""

    center = rng.choice(list(compositions(total)))
    lower = [
        0 if weights[i] == 1 else rng.randint(0, center[i]) for i in range(4)
    ]
    upper = [rng.randint(center[i], total) for i in range(4)]
    values = [F(0)] * 16
    for i in range(4):
        values[1 << i] = F(lower[i])
        values[15 ^ (1 << i)] = F(total - upper[i])
    for coalition in PAIR_REPRESENTATIVES:
        amount = sum(center[i] for i in range(4) if coalition >> i & 1)
        low = rng.randint(0, amount)
        high = rng.randint(amount, total)
        values[coalition] = F(low)
        values[15 ^ coalition] = F(total - high)
    values[15] = F(total)
    if any(value < 0 for value in values):
        return None
    return tuple(values)


def mutate_generators(rng, generators, weights):
    points = [list(point) for point in generators]
    for _ in range(rng.randint(1, 6)):
        point = rng.choice(points)
        donors = [i for i, amount in enumerate(point) if amount > 0]
        donor = rng.choice(donors)
        receiver = rng.choice([i for i in range(4) if i != donor])
        point[donor] -= 1
        point[receiver] += 1
    result = tuple(tuple(point) for point in points)
    if any(
        weights[role] == 1 and min(point[role] for point in result) != 0
        for role in range(4)
    ):
        return None
    return result


def classify(common):
    independent_partitions = len({partition for partition, _ in common})
    return {0: "common-zero", 1: "common-one", 2: "common-two"}.get(
        independent_partitions, "common-three"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260812)
    parser.add_argument("--games-per-weight", type=int, default=12)
    parser.add_argument("--slab-games-per-weight", type=int, default=24)
    parser.add_argument("--mutations-per-weight", type=int, default=24)
    parser.add_argument("--max-n", type=int, default=9)
    parser.add_argument(
        "--weights",
        type=lambda text: tuple(map(int, text.split(","))),
        help="optional single positive four-weight vector",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    rng = random.Random(args.seed)

    counts = Counter()
    minima = {}
    checked = 0
    distance_identities_checked = 0
    violations = []
    face_unit_endowment_violations = []
    ambient_unit_endowment_violations = []
    weight_levels = (
        [(sum(args.weights), [args.weights])]
        if args.weights
        else [
            (n, [row for row in compositions(n) if all(row)])
            for n in range(6, args.max_n + 1)
        ]
    )
    if args.weights and (len(args.weights) != 4 or not all(args.weights)):
        parser.error("--weights requires four positive comma-separated integers")
    for n, positive_weights in weight_levels:
        for weights in positive_weights:
            total = rng.randint(5, 12)
            candidate_rows = []
            for _ in range(args.games_per_weight):
                generators = sample_game(
                    rng,
                    total,
                    max(rng.randint(5, 9), sum(w == 1 for w in weights)),
                    weights,
                )
                candidate_rows.append((role_values(generators), generators))
            for _ in range(args.slab_games_per_weight):
                values = sample_slab_values(rng, total, weights)
                if values is not None:
                    values = exactify_role_game(values)
                if values is not None:
                    candidate_rows.append((values, ()))
            for _ in range(args.mutations_per_weight):
                generators = mutate_generators(
                    rng, NORMALIZED_OBSTRUCTION_GENERATORS, weights
                )
                if generators is not None:
                    candidate_rows.append((role_values(generators), generators))
            for values, generators in candidate_rows:
                # Canonical expansion requires zero singleton worth on every
                # unit role.  Positive singleton endowments remain allowed on
                # nonunit roles.
                if any(weights[i] == 1 and values[1 << i] != 0 for i in range(4)):
                    continue
                lmin, lmin_trace = weighted_lex_point(values, weights, "min")
                lmax, lmax_trace = weighted_lex_point(values, weights, "max")
                if lmin == lmax:
                    counts["coincident"] += 1
                    continue
                active_lmin = active_pair_endpoints(values, lmin)
                active_lmax = active_pair_endpoints(values, lmax)
                common = active_lmin & active_lmax
                face_class = classify(common)
                overlap = sum(min(a, b) for a, b in zip(lmin, lmax))
                direct_distance = sum(abs(a - b) for a, b in zip(lmin, lmax))
                transformed_distance = pair_coordinate_distance(lmin, lmax)
                if direct_distance != transformed_distance:
                    raise AssertionError(
                        ("pair-coordinate distance", lmin, lmax, direct_distance, transformed_distance)
                    )
                distance_identities_checked += 1
                ratio = overlap / values[15]
                row = {
                    "n": n,
                    "weights": weights,
                    "total": values[15],
                    "generators": generators,
                    "values": values,
                    "lmin": lmin,
                    "lmax": lmax,
                    "lmin_trace": lmin_trace,
                    "lmax_trace": lmax_trace,
                    "active_lmin": active_lmin,
                    "active_lmax": active_lmax,
                    "common_pair_endpoints": common,
                    "face_class": face_class,
                    "ratio": ratio,
                    "target": target(n),
                }
                if face_class in ("common-two", "common-three"):
                    face_minima = common_face_unit_minima(values, weights, common)
                    if face_minima is not None:
                        labels, minima_on_face = face_minima
                        row["common_face_labels_audited"] = labels
                        row["unit_role_minima_on_common_face"] = minima_on_face
                        direction, ambient_endowments, ambient_width = (
                            common_face_ambient_endowments(lmin, labels)
                        )
                        row["common_face_direction"] = direction
                        row["ambient_nonnegative_endowments"] = ambient_endowments
                        row["ambient_nonnegative_width"] = ambient_width
                        if any(
                            minimum != values[1 << role]
                            for role, minimum in minima_on_face.items()
                        ):
                            face_unit_endowment_violations.append(row)
                        if any(
                            weights[role] == 1 and ambient_endowments[role] != 0
                            for role in range(4)
                        ):
                            ambient_unit_endowment_violations.append(row)
                checked += 1
                counts[face_class] += 1
                if ratio < row["target"]:
                    violations.append(row)
                key = (face_class, n)
                if key not in minima or ratio < minima[key]["ratio"]:
                    minima[key] = row

    report = {
        "status": "exact rational discovery census; not proof evidence",
        "seed": args.seed,
        "games_per_weight": args.games_per_weight,
        "slab_games_per_weight": args.slab_games_per_weight,
        "mutations_per_weight": args.mutations_per_weight,
        "max_n": args.max_n,
        "noncoincident_games_checked": checked,
        "pair_coordinate_distance_identities_checked": distance_identities_checked,
        "counts": dict(sorted(counts.items())),
        "target_violations": [encode_row(row) for row in violations],
        "common_face_unit_endowment_violations": [
            encode_row(row) for row in face_unit_endowment_violations
        ],
        "ambient_unit_endowment_violations": [
            encode_row(row) for row in ambient_unit_endowment_violations
        ],
        "minimum_by_face_class_and_n": [
            encode_row(minima[key]) for key in sorted(minima)
        ],
        "scope": (
            "deterministic sampled lower envelopes; exact games and rational "
            "selectors, used only to discover the remaining human cases"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    if args.quiet:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "noncoincident_games_checked": checked,
                    "counts": report["counts"],
                    "target_violation_count": len(violations),
                },
                indent=2,
            )
        )
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
