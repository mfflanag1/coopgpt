#!/usr/bin/env python3
"""Independently exactify and recompute every SAT equality-census model.

The census solver supplies only rational generators.  This audit builds the
finite lower-envelope game from those displayed generators and then recomputes
Lmin and Lmax with two exact LP implementations.  It also emits complete
per-player staged pinning certificates and solves the Lmax top-over-cover LP
over the reconstructed game using exact rational arithmetic.

This validates the displayed equality games.  It does not turn UNSAT verdicts
for the other support types into independently checked proof certificates.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(COOPGAMES / "verifiers" / "divergence"))

from audit_two_packet_exactification import (  # noqa: E402
    all_staged_pinning_certificates,
    independent_lex,
)
from audit_lmax_overcover import top_certificate  # noqa: E402
from lexsimplex import lex_point_with_trace  # noqa: E402


N = 6
FULL = (1 << N) - 1


def point(raw):
    return tuple(F(value) for value in raw)


def coalition_sum(payoff, coalition):
    return sum(
        (payoff[i] for i in range(N) if coalition >> i & 1), F(0)
    )


def lower_envelope(rows):
    return tuple(
        min(coalition_sum(row, coalition) for row in rows)
        for coalition in range(1 << N)
    )


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, tuple):
        return [encode(item) for item in value]
    if isinstance(value, list):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    return value


def smallest_zero_cover(witnesses):
    for size in range(1, len(witnesses) + 1):
        for chosen in itertools.combinations(range(len(witnesses)), size):
            if all(any(witnesses[k][i] == 0 for k in chosen) for i in range(N)):
                return chosen
    raise AssertionError("singleton witnesses do not cover all coordinates")


def stratum_sizes(payoff):
    values = sorted(set(payoff))
    return tuple(sum(value == level for value in payoff) for level in values)


def two_stratum_table(x, z):
    x_levels = sorted(set(x))
    z_levels = sorted(set(z))
    assert len(x_levels) == len(z_levels) == 2
    return [
        [
            sum(x[i] == x_level and z[i] == z_level for i in range(N))
            for z_level in z_levels
        ]
        for x_level in x_levels
    ]


def audit_model(row):
    claimed_lmin = point(row["candidate_lmin"])
    claimed_lmax = point(row["candidate_lmax"])
    witnesses = tuple(point(raw) for raw in row["candidate_singleton_witnesses"])
    assert all(len(payoff) == N for payoff in (claimed_lmin, claimed_lmax) + witnesses)
    assert all(
        all(value >= 0 for value in payoff) and sum(payoff) == 1
        for payoff in (claimed_lmin, claimed_lmax) + witnesses
    )
    assert all(witnesses[i][i] == 0 for i in range(N))
    assert stratum_sizes(claimed_lmin) == tuple(row["lmin"])
    assert stratum_sizes(claimed_lmax) == tuple(row["lmax"])
    assert two_stratum_table(claimed_lmin, claimed_lmax) == row["table"]

    witness_cover = smallest_zero_cover(witnesses)
    selected_witnesses = tuple(witnesses[k] for k in witness_cover)
    generators = (claimed_lmin, claimed_lmax) + selected_witnesses
    game = lower_envelope(generators)
    assert game[FULL] == 1
    assert all(game[1 << i] == 0 for i in range(N))
    assert all(
        coalition_sum(payoff, coalition) >= game[coalition]
        for payoff in generators
        for coalition in range(1 << N)
    )
    assert all(
        any(
            coalition_sum(payoff, coalition) == game[coalition]
            for payoff in generators
        )
        for coalition in range(1 << N)
    )

    selections = {}
    for mode, claimed in (("min", claimed_lmin), ("max", claimed_lmax)):
        simplex_point, simplex_trace = lex_point_with_trace(N, game, mode)
        independent_point, independent_trace = independent_lex(game, mode)
        assert tuple(simplex_point) == independent_point == claimed
        assert simplex_trace == independent_trace
        certificates = all_staged_pinning_certificates(
            game, claimed, independent_trace, mode
        )
        assert len(certificates) == N
        selections[mode] = {
            "point": claimed,
            "trace": independent_trace,
            "pinning_certificates": certificates,
        }

    overlap = sum(
        (min(a, b) for a, b in zip(claimed_lmin, claimed_lmax)), F(0)
    )
    distance = sum(
        (abs(a - b) for a, b in zip(claimed_lmin, claimed_lmax)), F(0)
    )
    assert overlap == distance == F(2, 3)
    top = {i for i, value in enumerate(claimed_lmax) if value == max(claimed_lmax)}
    tight_top_triples = tuple(
        sum(1 << i for i in triple)
        for triple in itertools.combinations(sorted(top), 3)
        if coalition_sum(
            claimed_lmax, sum(1 << i for i in triple)
        )
        == game[sum(1 << i for i in triple)]
    )
    reported_tight_top_triples = tuple(row["candidate_tight_lmax_top_triples"])
    assert set(reported_tight_top_triples) <= set(tight_top_triples)
    common_tight_top_triples = tuple(
        coalition
        for coalition in tight_top_triples
        if coalition_sum(claimed_lmin, coalition)
        == coalition_sum(claimed_lmax, coalition)
    )
    assert common_tight_top_triples

    anchor = top_certificate(game, claimed_lmax)
    assert anchor["theta"] == F(1, 3)
    assert max(anchor["alpha"]) == F(1, 3)
    assert sum(anchor["alpha"]) == 1

    return {
        "census_index": row["index"],
        "source_configuration": {
            "lmin": row["lmin"],
            "lmax": row["lmax"],
            "table": row["table"],
        },
        "encoded_singleton_witness_count": len(witnesses),
        "selected_witness_indices": witness_cover,
        "generators": generators,
        "characteristic_function": game,
        "singleton_normalized": True,
        "exactness_certificate": (
            "finite lower envelope; every coalition is attained by a displayed generator"
        ),
        "lmin": selections["min"],
        "lmax": selections["max"],
        "overlap": overlap,
        "l1_distance": distance,
        "solver_reported_tight_lmax_top_triples": reported_tight_top_triples,
        "all_reconstructed_tight_lmax_top_triples": tight_top_triples,
        "common_lmin_lmax_tight_top_triples": common_tight_top_triples,
        "exact_dispersion_optimal_lmax_anchor": anchor,
        "independent_selection_encodings": 2,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--census", type=Path, default=HERE / "equality_triple_census.json"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    census = json.loads(args.census.read_text())
    assert census["mode"] == "equality-triple"
    assert census["tally"]["unknown"] == 0
    sat_rows = [row for row in census["rows"] if row["result"] == "sat"]
    assert len(sat_rows) == census["tally"]["sat"]
    audited = [audit_model(row) for row in sat_rows]
    report = {
        "status": (
            "exact reconstruction of every displayed equality-census SAT model; "
            "not independent certificates for the census UNSAT rows"
        ),
        "source_census": str(args.census),
        "source_tally": census["tally"],
        "audited_sat_indices": [row["index"] for row in sat_rows],
        "all_displayed_sat_models_recomputed": len(audited) == len(sat_rows),
        "models": audited,
    }
    rendered = json.dumps(encode(report), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
