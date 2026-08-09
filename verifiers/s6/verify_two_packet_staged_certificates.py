#!/usr/bin/env python3
"""Independently replay every staged pinning certificate in the boundary audit."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


N = 6
FULL = (1 << N) - 1
HERE = Path(__file__).resolve().parent


def q(value) -> F:
    return F(value)


def point(raw) -> tuple[F, ...]:
    return tuple(q(value) for value in raw)


def coalition_sum(x, coalition):
    return sum((x[i] for i in range(N) if coalition >> i & 1), F(0))


def lower_envelope(rows):
    return tuple(
        min(coalition_sum(row, coalition) for row in rows)
        for coalition in range(1 << N)
    )


def weighted_pairs(raw):
    return tuple((int(index), q(weight)) for index, weight in raw)


def replay_mode(game, selection, mode):
    selected = point(selection["point"])
    trace = selection["trace"]
    certificates = selection["pinning_certificates"]
    expected = {
        (stage, int(player))
        for stage, row in enumerate(trace)
        for player in row["newly_pinned"]
    }
    observed = {(int(row["stage"]), int(row["player"])) for row in certificates}
    assert observed == expected
    assert len(certificates) == N

    old = set()
    for stage, trace_row in enumerate(trace):
        level = q(trace_row["level"])
        block = {int(i) for i in trace_row["newly_pinned"]}
        assert block
        assert all(selected[i] == level for i in block)
        assert not (old & block)
        for certificate in (
            row for row in certificates if int(row["stage"]) == stage
        ):
            player_index = int(certificate["player"])
            assert player_index in block
            assert q(certificate["level"]) == level
            lambdas = weighted_pairs(certificate["coalition_weights"])
            old_weights = weighted_pairs(certificate["old_pin_weights"])
            side_weights = weighted_pairs(certificate["level_side_weights"])
            efficiency = q(certificate["efficiency_weight"])
            assert all(0 < coalition < FULL and weight > 0 for coalition, weight in lambdas)
            assert all(coalition_sum(selected, coalition) == game[coalition]
                       for coalition, _ in lambdas)
            assert all(i in old and weight != 0 for i, weight in old_weights)
            assert all(i in block and weight > 0 for i, weight in side_weights)

            for i in range(N):
                load = sum(
                    (weight for coalition, weight in lambdas if coalition >> i & 1),
                    F(0),
                ) + sum((weight for j, weight in old_weights if j == i), F(0))
                side = sum((weight for j, weight in side_weights if j == i), F(0))
                if mode == "min":
                    load += side + F(int(i == player_index))
                else:
                    load -= side + F(int(i == player_index))
                assert load == efficiency

            if mode == "min":
                objective = (
                    efficiency * game[FULL]
                    - sum((weight * game[S] for S, weight in lambdas), F(0))
                    - sum((weight * selected[i] for i, weight in old_weights), F(0))
                    - level * sum((weight for _, weight in side_weights), F(0))
                )
                assert certificate["incidence_sign"] == "+e_i"
            else:
                objective = (
                    sum((weight * game[S] for S, weight in lambdas), F(0))
                    + sum((weight * selected[i] for i, weight in old_weights), F(0))
                    - level * sum((weight for _, weight in side_weights), F(0))
                    - efficiency * game[FULL]
                )
                assert certificate["incidence_sign"] == "-e_i"
            assert objective == level
        old.update(block)
    assert old == set(range(N))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=HERE / "two_packet_exactification_audit.json",
    )
    args = parser.parse_args()
    report = json.loads(args.input.read_text())
    checked = []
    for key in ("abstract", "exactified"):
        record = report[key]
        generators = tuple(point(row) for row in record["generators"])
        game = lower_envelope(generators)
        assert all(sum(row) == game[FULL] for row in generators)
        assert tuple(str(game[1 << i]) for i in range(N)) == tuple(
            record["singleton_values"]
        )
        replay_mode(game, record["lmin"], "min")
        replay_mode(game, record["lmax"], "max")
        checked.append(
            {
                "game": key,
                "lmin_certificates": len(record["lmin"]["pinning_certificates"]),
                "lmax_certificates": len(record["lmax"]["pinning_certificates"]),
            }
        )
    print(json.dumps({"status": "PASS", "checked": checked}, indent=2))


if __name__ == "__main__":
    main()
