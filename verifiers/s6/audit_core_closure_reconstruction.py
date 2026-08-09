#!/usr/bin/env python3
"""Independent exact reconstruction control for the core-closure encoding."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import z3


COOPGAMES = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(COOPGAMES / "verifiers" / "divergence"))

from audit_two_packet_exactification import independent_lex  # noqa: E402
from core_closure_pipeline import pipeline2_core_closure  # noqa: E402
from lexsimplex import lex_point_with_trace  # noqa: E402


def as_fraction(value):
    value = z3.simplify(value)
    if not z3.is_rational_value(value):
        raise TypeError(f"model value is not rational: {value}")
    return F(value.numerator_as_long(), value.denominator_as_long())


def coalition_sum(point, coalition):
    return sum((point[i] for i in range(6) if coalition >> i & 1), F(0))


def lower_envelope(rows):
    return tuple(
        min(coalition_sum(row, coalition) for row in rows)
        for coalition in range(1 << 6)
    )


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, tuple):
        return [encode(item) for item in value]
    if isinstance(value, list):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        return {key: encode(item) for key, item in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    # This is the stratum/table type of an archived 4|2 equality game.  The
    # solver is not given that game: it constructs a fresh boundary model from
    # the reduced constraints, which is then exactified using only its eight
    # displayed points.
    r, c = (5, 1), (2, 4)
    table = [[2, 3], [0, 1]]
    data = pipeline2_core_closure(6, r, c, table, F(2, 3), fail=False)
    data["solver"].add(data["distance"] == z3.RealVal("2/3"))
    data["solver"].set(timeout=120000)
    assert data["solver"].check() == z3.sat
    model = data["solver"].model()

    claimed_lmin = tuple(as_fraction(model.eval(q)) for q in data["lmin"])
    claimed_lmax = tuple(as_fraction(model.eval(q)) for q in data["lmax"])
    witnesses = tuple(
        tuple(as_fraction(model.eval(q)) for q in witness)
        for witness in data["singleton_witnesses"]
    )
    # Keep a smallest subfamily whose zero coordinates cover all players.  The
    # discarded witnesses are unnecessary for singleton normalization, while
    # x and z themselves retain every staged-certificate tight coalition.
    witness_cover = None
    for size in range(1, len(witnesses) + 1):
        for chosen in itertools.combinations(range(len(witnesses)), size):
            if all(any(witnesses[k][i] == 0 for k in chosen) for i in range(6)):
                witness_cover = chosen
                break
        if witness_cover is not None:
            break
    assert witness_cover is not None
    selected_witnesses = tuple(witnesses[k] for k in witness_cover)
    generators = (claimed_lmin, claimed_lmax) + selected_witnesses
    assert all(all(q >= 0 for q in row) and sum(row) == 1 for row in generators)
    assert all(witness[i] == 0 for i, witness in enumerate(witnesses))

    game = lower_envelope(generators)
    assert all(game[1 << i] == 0 for i in range(6))
    assert all(
        any(coalition_sum(row, coalition) == game[coalition] for row in generators)
        for coalition in range(1 << 6)
    )

    selections = {}
    for mode, claimed in (("min", claimed_lmin), ("max", claimed_lmax)):
        simplex_point, simplex_trace = lex_point_with_trace(6, game, mode)
        independent_point, independent_trace = independent_lex(game, mode)
        assert tuple(simplex_point) == independent_point == claimed
        assert simplex_trace == independent_trace
        selections[mode] = {"point": claimed, "trace": independent_trace}

    overlap = sum((min(a, b) for a, b in zip(claimed_lmin, claimed_lmax)), F(0))
    distance = sum((abs(a - b) for a, b in zip(claimed_lmin, claimed_lmax)), F(0))
    assert overlap == F(2, 3) and distance == F(2, 3)

    report = {
        "status": "exact reconstruction control; not an exhaustive theorem",
        "source_configuration": {"lmin": r, "lmax": c, "table": table},
        "encoded_singleton_witness_count": len(witnesses),
        "selected_witness_indices": witness_cover,
        "generators": generators,
        "singleton_normalized": True,
        "exactness_certificate": "finite lower envelope; every coalition attained by a displayed generator",
        "lmin": selections["min"],
        "lmax": selections["max"],
        "overlap": overlap,
        "l1_distance": distance,
        "independent_selection_encodings": 2,
    }
    rendered = json.dumps(encode(report), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
