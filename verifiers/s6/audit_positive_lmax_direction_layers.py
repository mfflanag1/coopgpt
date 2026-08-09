#!/usr/bin/env python3
"""Ablate distance and exactness witnesses in the Lmax direction layer.

This is a structural dependency audit, not an independent proof.  It rebuilds
each of the 109 positive-residue rows handled by one explicit Lmax direction
and asks which premises are actually needed to exclude every blocker.
"""

from __future__ import annotations

import argparse
import collections
import itertools
import json
import sys
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from search_positive_handover_directions import (  # noqa: E402
    blocker_formula,
    critical_all_witness_solver,
    point_sum,
)
import nsix  # noqa: E402


EXPECTED = {
    "N(0,0)_P(-1,0,0)_r1": {
        "rows": 80,
        "full": {"unsat": 80},
        "without_distance": {"unsat": 80},
        "without_witness_blockers": {"sat": 80},
        "without_distance_or_witness_blockers": {"sat": 80},
    },
    "N(1,1)_P(-2,-2,-1)_r3": {
        "rows": 21,
        "full": {"unsat": 21},
        "without_distance": {"unsat": 21},
        "without_witness_blockers": {"unsat": 21},
        "without_distance_or_witness_blockers": {"unsat": 21},
    },
    "N(-1,1)_P(0,0,0)_r0": {
        "rows": 8,
        "full": {"unsat": 8},
        "without_distance": {"sat": 8},
        "without_witness_blockers": {"sat": 8},
        "without_distance_or_witness_blockers": {"sat": 8},
    },
}


def template(row: dict) -> str:
    direction = row["direction"]
    poor = tuple(sorted(direction[i] for i in row["poor_players"]))
    middle = tuple(sorted(direction[i] for i in row["P_players"]))
    rich = direction[row["rich_player"]]
    return (
        f"N({','.join(map(str, poor))})_"
        f"P({','.join(map(str, middle))})_r{rich}"
    )


def verdict(configuration, index, direction, include_distance, use_witnesses):
    solver, _, witnesses = critical_all_witness_solver(
        index, configuration, include_distance=include_distance
    )
    blocker, _ = blocker_formula(
        index,
        configuration,
        direction,
        "max",
        witnesses if use_witnesses else (),
    )
    solver.add(blocker)
    return str(solver.check())


def dominant_template_residue(configuration, index, row):
    """Locate the payoff-only blocker and its canonical low P player."""
    solver, labels, _ = critical_all_witness_solver(
        index, configuration, include_distance=False
    )
    cell = nsix.layout(
        6,
        tuple(configuration[0]),
        tuple(configuration[1]),
        tuple(tuple(values) for values in configuration[2]),
    )
    x = [z3.Real(f"m{cell[i][0]}") for i in range(6)]
    z = [z3.Real(f"M{cell[i][1]}") for i in range(6)]
    decreased = next(
        player for player in labels["P_players"] if row["direction"][player] == -1
    )
    eligible = []
    for mask in range(1, (1 << 6) - 1):
        if not (mask >> decreased & 1) or mask >> labels["rich_player"] & 1:
            continue
        coalition = tuple(player for player in range(6) if mask >> player & 1)
        solver.push()
        solver.add(point_sum(x, coalition) >= point_sum(z, coalition))
        result = solver.check()
        solver.pop()
        if result == z3.sat:
            eligible.append(mask)
        else:
            assert result == z3.unsat
    expected_mask = sum(
        1 << player for player in (*labels["poor_players"], decreased)
    )
    assert eligible == [expected_mask]

    forced_low = []
    selected = tuple(labels["poor_players"]) + (decreased,)
    for candidate in labels["P_players"]:
        if candidate == decreased:
            continue
        comparison = tuple(labels["poor_players"]) + (candidate,)
        solver.push()
        solver.add(point_sum(z, selected) <= point_sum(x, comparison))
        result = solver.check()
        solver.pop()
        if result == z3.unsat:
            forced_low.append(candidate)
    assert len(forced_low) == 1
    low = forced_low[0]
    assert cell[low][0] < cell[decreased][0]
    assert cell[low][1] < cell[decreased][1]
    return expected_mask, low


def common_pair_template_structure(configuration, index, row):
    """Check the shared-stratum/common-pair structure of the 21-row class."""
    solver, labels, _ = critical_all_witness_solver(
        index, configuration, include_distance=False
    )
    cell = nsix.layout(
        6,
        tuple(configuration[0]),
        tuple(configuration[1]),
        tuple(tuple(values) for values in configuration[2]),
    )
    common_pair = [
        player for player in labels["P_players"] if row["direction"][player] == -2
    ]
    high = next(
        player for player in labels["P_players"] if row["direction"][player] == -1
    )
    assert len(common_pair) == 2
    assert cell[common_pair[0]] == cell[common_pair[1]]
    assert cell[high][0] > cell[common_pair[0]][0]
    assert cell[high][1] == cell[common_pair[0]][1]
    x = [z3.Real(f"m{cell[i][0]}") for i in range(6)]
    z = [z3.Real(f"M{cell[i][1]}") for i in range(6)]
    for excluded in common_pair:
        triple = tuple(
            player for player in labels["P_players"] if player != excluded
        ) + (labels["rich_player"],)
        solver.push()
        solver.add(point_sum(z, triple) != point_sum(x, triple))
        result = solver.check()
        solver.pop()
        assert result == z3.unsat
    return common_pair, high


def boundary_template_structure(configuration, index, row):
    """Map each of the eight distance-sensitive rows to four abstract blockers."""
    solver, labels, witnesses = critical_all_witness_solver(
        index, configuration, include_distance=False
    )
    cell = nsix.layout(
        6,
        tuple(configuration[0]),
        tuple(configuration[1]),
        tuple(tuple(values) for values in configuration[2]),
    )
    decreased = next(
        player for player in labels["poor_players"] if row["direction"][player] == -1
    )
    increased = next(
        player for player in labels["poor_players"] if row["direction"][player] == 1
    )
    j, k, ell = sorted(labels["P_players"], key=lambda player: cell[player][0])
    rich = labels["rich_player"]
    assert cell[decreased][0] <= cell[j][0] < cell[increased][0]
    assert cell[increased][0] <= cell[k][0] < cell[ell][0] < cell[rich][0]
    assert cell[increased][1] < cell[decreased][1] < cell[j][1]
    assert cell[j][1] <= cell[rich][1] < cell[k][1] == cell[ell][1]

    x = [z3.Real(f"m{cell[i][0]}") for i in range(6)]
    z = [z3.Real(f"M{cell[i][1]}") for i in range(6)]
    for excluded in (j, k):
        triple = tuple(
            player for player in labels["P_players"] if player != excluded
        ) + (rich,)
        solver.push()
        solver.add(point_sum(z, triple) != point_sum(x, triple))
        result = solver.check()
        solver.pop()
        assert result == z3.unsat

    feasible = []
    for mask in range(1, (1 << 6) - 1):
        if not (mask >> decreased & 1) or mask >> increased & 1:
            continue
        coalition = tuple(player for player in range(6) if mask >> player & 1)
        solver.push()
        solver.add(
            point_sum(x, coalition) >= point_sum(z, coalition),
            *[
                point_sum(witness, coalition) >= point_sum(z, coalition)
                for witness in witnesses
            ],
        )
        result = solver.check()
        solver.pop()
        if result == z3.sat:
            feasible.append(mask)
        else:
            assert result == z3.unsat
    expected_coalitions = (
        (decreased, ell),
        (decreased, j, k, rich),
        (decreased, j, ell, rich),
        (decreased, k, ell, rich),
    )
    expected_masks = sorted(
        sum(1 << player for player in coalition)
        for coalition in expected_coalitions
    )
    assert feasible == expected_masks
    return {
        "decreased_poor_player": decreased,
        "increased_poor_player": increased,
        "common_P_players": [j, k],
        "third_P_player": ell,
        "distance_free_feasible_blocker_masks": feasible,
    }


def check_critical_boundary_structure(configuration, index):
    solver, labels, _ = critical_all_witness_solver(
        index, configuration, include_distance=False
    )
    cell = nsix.layout(
        6,
        tuple(configuration[0]),
        tuple(configuration[1]),
        tuple(tuple(values) for values in configuration[2]),
    )
    n0, n1 = labels["poor_players"]
    j, k, ell = sorted(labels["P_players"], key=lambda player: cell[player][0])
    rich = labels["rich_player"]
    assert cell[n0][0] <= cell[n1][0] <= cell[j][0]
    assert cell[j][0] < cell[k][0] < cell[ell][0] < cell[rich][0]
    assert cell[n0][1] <= cell[j][1]
    assert cell[n1][1] <= cell[j][1]
    assert cell[j][1] <= cell[rich][1] < cell[k][1] == cell[ell][1]
    x = [z3.Real(f"m{cell[i][0]}") for i in range(6)]
    z = [z3.Real(f"M{cell[i][1]}") for i in range(6)]
    for excluded in (j, k):
        triple = tuple(
            player for player in labels["P_players"] if player != excluded
        ) + (rich,)
        solver.push()
        solver.add(point_sum(z, triple) != point_sum(x, triple))
        result = solver.check()
        solver.pop()
        assert result == z3.unsat
    return [j, k]


def feasible_common_pairs(configuration, index, require_third_comparison):
    solver, labels, _ = critical_all_witness_solver(
        index,
        configuration,
        include_distance=False,
        include_witnesses=False,
        include_triple_comparisons=require_third_comparison,
    )
    cell = nsix.layout(
        6,
        tuple(configuration[0]),
        tuple(configuration[1]),
        tuple(tuple(values) for values in configuration[2]),
    )
    x = [z3.Real(f"m{cell[i][0]}") for i in range(6)]
    z = [z3.Real(f"M{cell[i][1]}") for i in range(6)]
    triples = []
    for excluded in labels["P_players"]:
        triple = tuple(
            player for player in labels["P_players"] if player != excluded
        ) + (labels["rich_player"],)
        triples.append((excluded, triple))
    feasible = []
    for first, second in itertools.combinations(triples, 2):
        solver.push()
        solver.add(
            point_sum(z, first[1]) == point_sum(x, first[1]),
            point_sum(z, second[1]) == point_sum(x, second[1]),
        )
        result = solver.check()
        solver.pop()
        if result == z3.sat:
            feasible.append(sorted((first[0], second[0])))
        else:
            assert result == z3.unsat
    return feasible


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    parser.add_argument(
        "--directions",
        type=Path,
        default=HERE / "positive_lmax_handover_directions.json",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    survivors = json.loads(args.triage.read_text())["survivors"]
    source = json.loads(args.directions.read_text())["rows"]
    critical_rows = [
        row for row in source if row.get("critical_algebra_verdict") == "unsat"
    ]
    critical_classes = collections.Counter()
    critical_boundary_rows = []
    critical_payoff_rows = []
    for row in critical_rows:
        index = row["survivor_index"]
        configuration = survivors[index]
        variants = {}
        for name, distance, witnesses, comparisons in (
            ("without_distance", False, True, True),
            ("without_witnesses", True, False, True),
            ("payoff_critical", False, False, True),
            ("common_sign_only", False, False, False),
        ):
            candidate, _, _ = critical_all_witness_solver(
                index,
                configuration,
                include_distance=distance,
                include_witnesses=witnesses,
                include_triple_comparisons=comparisons,
            )
            variants[name] = str(candidate.check())
        if variants["common_sign_only"] == "unsat":
            assert feasible_common_pairs(configuration, index, False) == []
            critical_classes["common_sign_only"] += 1
        elif variants["payoff_critical"] == "unsat":
            candidate_pairs = feasible_common_pairs(configuration, index, False)
            assert len(candidate_pairs) == 1
            assert feasible_common_pairs(configuration, index, True) == []
            critical_classes["needs_third_triple_comparison"] += 1
            critical_payoff_rows.append(
                {
                    "survivor_index": index,
                    "unique_order_feasible_common_pair": candidate_pairs[0],
                }
            )
        else:
            assert set(variants.values()) == {"sat"}
            critical_classes["needs_distance_and_witnesses"] += 1
            common_pair = check_critical_boundary_structure(configuration, index)
            critical_boundary_rows.append(
                {"survivor_index": index, "forced_common_P_players": common_pair}
            )
    assert dict(critical_classes) == {
        "common_sign_only": 68,
        "needs_third_triple_comparison": 146,
        "needs_distance_and_witnesses": 16,
    }
    rows = []
    for row in source:
        if row.get("selected_side") != "max" or row.get("direction") is None:
            continue
        index = row["survivor_index"]
        configuration = survivors[index]
        assert configuration == row["configuration"]
        direction = tuple(row["direction"])
        results = {
            "full": verdict(configuration, index, direction, True, True),
            "without_distance": verdict(
                configuration, index, direction, False, True
            ),
            "without_witness_blockers": verdict(
                configuration, index, direction, True, False
            ),
            "without_distance_or_witness_blockers": verdict(
                configuration, index, direction, False, False
            ),
        }
        extra = {}
        if template(row) == "N(0,0)_P(-1,0,0)_r1":
            mask, low = dominant_template_residue(configuration, index, row)
            extra = {
                "unique_payoff_comparison_eligible_mask": mask,
                "forced_low_P_player": low,
            }
        if template(row) == "N(1,1)_P(-2,-2,-1)_r3":
            common_pair, high = common_pair_template_structure(
                configuration, index, row
            )
            extra = {
                "forced_common_excluded_players": common_pair,
                "higher_x_same_z_P_player": high,
            }
        if template(row) == "N(-1,1)_P(0,0,0)_r0":
            extra = boundary_template_structure(configuration, index, row)
        rows.append(
            {
                "survivor_index": index,
                "template": template(row),
                "direction": list(direction),
                **results,
                **extra,
            }
        )

    summary = {}
    for name in sorted({row["template"] for row in rows}):
        selected = [row for row in rows if row["template"] == name]
        summary[name] = {"rows": len(selected)}
        for mode in (
            "full",
            "without_distance",
            "without_witness_blockers",
            "without_distance_or_witness_blockers",
        ):
            summary[name][mode] = dict(
                sorted(collections.Counter(row[mode] for row in selected).items())
            )
    assert summary == EXPECTED
    payload = {
        "schema": "positive-lmax-direction-dependency-audit-v1",
        "scope": "exact QF_LRA dependency audit; solver evidence, not proof objects",
        "summary": summary,
        "critical_algebra_dependency_summary": dict(critical_classes),
        "critical_boundary_rows": critical_boundary_rows,
        "critical_payoff_rows": critical_payoff_rows,
        "rows": rows,
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
