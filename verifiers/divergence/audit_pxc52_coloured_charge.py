#!/usr/bin/env python3
r"""Exact audit of the two-colour root-packet charge identities (PXC52).

This is a discovery and regression audit, not a proof of root selection.  For
each selected control and maximum-overlap root it lexicographically maximizes
root load and then the total comparison charge on the full tagged Lmin/Lmax
tight menu.  The dimension-free statement checked for the returned packet is

  A = S + delta*z_r - sum_{i != r} q_i*z_i,
  B = S + delta*x_r - sum_{i != r} q_i*x_i,

where A is the z-minus-x charge on x-tight rows, B is the x-minus-z charge on
z-tight rows, the root load is 1+delta, and q completes each offroot load to
one.  The hand proof evaluates the tagged incidence completion at z and x
and subtracts the mixed core budget supplied by a root-zero exactness
witness and S is its unused mixed core budget.  Exact finite optimization
only hostilely checks signs and scope.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_carrier_separator_payment import full_tight_support  # noqa: E402
from audit_labelled_facet_cover_duality import maximum_overlap_roots  # noqa: E402
from audit_lmax_overcover import coalition_sum, records  # noqa: E402
from exactlp import exact_linprog  # noqa: E402


SIX_PLAYER_TRAILS = {
    "$.records[17]",
    "$.records[51]",
    "$.records[67]",
    "$.records[110]",
    "$.records[118]",
    "$.records[162]",
}


def fractions(values):
    return tuple(F(value) for value in values)


def lower_envelope(generators):
    n = len(generators[0])
    return tuple(
        min(
            sum(
                (
                    generator[player]
                    for player in range(n)
                    if coalition >> player & 1
                ),
                F(0),
            )
            for generator in generators
        )
        for coalition in range(1 << n)
    )


def best_coloured_packet(x, z, support_x, support_z, root, mode):
    n = len(x)
    tagged = tuple(("x", coalition) for coalition in support_x) + tuple(
        ("z", coalition) for coalition in support_z
    )
    inequalities = []
    rhs = []
    for player in range(n):
        if player == root:
            continue
        inequalities.append(
            [F((coalition >> player) & 1) for _, coalition in tagged]
        )
        rhs.append(F(1))
    for variable in range(len(tagged)):
        inequalities.append(
            [F(-1 if other == variable else 0) for other in range(len(tagged))]
        )
        rhs.append(F(0))

    root_row = [F((coalition >> root) & 1) for _, coalition in tagged]
    status, negative_load, _ = exact_linprog(
        [-entry for entry in root_row], inequalities, rhs
    )
    if status != "optimal":
        raise AssertionError(f"root-load optimization returned {status}")
    maximum_load = -negative_load
    if maximum_load < 1:
        return {"root": root, "maximum_root_load": maximum_load}

    charges = []
    for tag, coalition in tagged:
        if tag == "x":
            charge = coalition_sum(z, coalition) - coalition_sum(x, coalition)
        else:
            charge = coalition_sum(x, coalition) - coalition_sum(z, coalition)
        if charge < 0:
            raise AssertionError("tagged tight-row comparison charge is negative")
        charges.append(charge)
    if mode == "maximum_root_load_face":
        fixed_inequalities = list(inequalities) + [
            root_row,
            [-q for q in root_row],
        ]
        fixed_rhs = list(rhs) + [maximum_load, -maximum_load]
    elif mode == "maximum_charge_rooted_face":
        fixed_inequalities = list(inequalities) + [[-q for q in root_row]]
        fixed_rhs = list(rhs) + [F(-1)]
    else:
        raise ValueError(f"unknown coloured-packet mode {mode}")
    status, negative_charge, weights = exact_linprog(
        [-charge for charge in charges], fixed_inequalities, fixed_rhs
    )
    if status != "optimal":
        raise AssertionError(f"charge optimization returned {status}")

    loads = tuple(
        sum(
            (
                weight
                for weight, (_, coalition) in zip(weights, tagged)
                if coalition >> player & 1
            ),
            F(0),
        )
        for player in range(n)
    )
    delta = loads[root] - 1
    q = tuple(F(0) if player == root else 1 - loads[player] for player in range(n))
    if delta < 0 or any(value < 0 for value in q):
        raise AssertionError("invalid rooted incidence completion")
    a_charge = sum(
        (
            weight * charge
            for weight, charge, (tag, _) in zip(weights, charges, tagged)
            if tag == "x"
        ),
        F(0),
    )
    b_charge = sum(
        (
            weight * charge
            for weight, charge, (tag, _) in zip(weights, charges, tagged)
            if tag == "z"
        ),
        F(0),
    )
    a_floor = delta * z[root] - sum(
        (q[player] * z[player] for player in range(n) if player != root), F(0)
    )
    b_floor = delta * x[root] - sum(
        (q[player] * x[player] for player in range(n) if player != root), F(0)
    )
    if a_charge < a_floor or b_charge < b_floor:
        raise AssertionError("PXC52 two-colour root-budget inequality failed")

    mixed_core_budget = sum(
        (
            weight
            * coalition_sum(x if tag == "x" else z, coalition)
            for weight, (tag, coalition) in zip(weights, tagged)
        ),
        F(0),
    )
    total = sum(x, F(0))
    if total != sum(z, F(0)) or mixed_core_budget > total:
        raise AssertionError("root-zero mixed core budget failed")
    mixed_core_slack = total - mixed_core_budget
    if a_charge != mixed_core_slack + a_floor:
        raise AssertionError("PXC52 x-tag charge/slack conservation failed")
    if b_charge != mixed_core_slack + b_floor:
        raise AssertionError("PXC52 z-tag charge/slack conservation failed")
    positive = tuple(
        {
            "tag": tag,
            "coalition": coalition,
            "weight": str(weight),
            "charge": str(charge),
        }
        for weight, charge, (tag, coalition) in zip(weights, charges, tagged)
        if weight
    )
    return {
        "mode": mode,
        "root": root,
        "maximum_root_load": str(maximum_load),
        "selected_root_load": str(loads[root]),
        "root_excess": str(delta),
        "x_tag_charge": str(a_charge),
        "z_tag_charge": str(b_charge),
        "total_coloured_charge": str(-negative_charge),
        "x_tag_floor": str(a_floor),
        "z_tag_floor": str(b_floor),
        "mixed_core_budget": str(mixed_core_budget),
        "mixed_core_slack": str(mixed_core_slack),
        "total": str(total),
        "offroot_completion": {
            str(player): str(value) for player, value in enumerate(q) if value
        },
        "positive_rows": positive,
    }


def selected_six_player_rows(path):
    payload = json.loads(path.read_text())
    selected = []
    for source, trail, values, x, z in records(payload, path):
        if trail not in SIX_PLAYER_TRAILS:
            continue
        selected.append((source.name, trail, values, x, z))
    if {trail for _, trail, _, _, _ in selected} != SIX_PLAYER_TRAILS:
        raise AssertionError("selected six-player hostile rows changed")
    return selected


def neutral_row(path):
    payload = json.loads(path.read_text())
    generators = tuple(fractions(row) for row in payload["game"]["generators"])
    return (
        path.name,
        "neutral-seven-player-control",
        lower_envelope(generators),
        fractions(payload["selections"]["lmin"]),
        fractions(payload["selections"]["lmax"]),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--six-player", required=True, type=Path)
    parser.add_argument("--neutral-control", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    cases = selected_six_player_rows(args.six_player) + [
        neutral_row(args.neutral_control)
    ]
    rows = []
    for source, trail, values, x, z in cases:
        support_x = tuple(full_tight_support(values, x))
        support_z = tuple(full_tight_support(values, z))
        roots = tuple(maximum_overlap_roots(x, z))
        packets = tuple(
            best_coloured_packet(x, z, support_x, support_z, root, mode)
            for root in roots
            for mode in (
                "maximum_root_load_face",
                "maximum_charge_rooted_face",
            )
        )
        rows.append(
            {
                "source": source,
                "trail": trail,
                "maximum_overlap_roots": roots,
                "packets": packets,
            }
        )

    neutral_packets = rows[-1]["packets"]
    if tuple(packet["total_coloured_charge"] for packet in neutral_packets) != (
        "0",
        "0",
    ):
        raise AssertionError("neutral control unexpectedly gained comparison charge")
    if tuple(packet["mixed_core_slack"] for packet in neutral_packets) != (
        "125/19046",
        "53/107",
    ):
        raise AssertionError("neutral charge/slack handover changed")
    maximum_charge_packets = tuple(
        packet
        for row in rows[:-1]
        for packet in row["packets"]
        if packet["mode"] == "maximum_charge_rooted_face"
    )
    if any(packet["root_excess"] != "0" for packet in maximum_charge_packets):
        raise AssertionError("six-player charge maximizer retained positive excess")

    report = {
        "status": "exact PXC52 two-colour charge/slack audit verified",
        "six_player_rows": len(rows) - 1,
        "neutral_seven_player_rows": 1,
        "six_player_charge_maximizers_with_zero_root_excess": len(
            maximum_charge_packets
        ),
        "neutral_maximum_comparison_charge": "0",
        "neutral_positive_core_slacks": ["125/19046", "53/107"],
        "rows": rows,
        "scope": (
            "dimension-free identities plus selected exact hostile controls; "
            "actual-selection comparison charge does not capture the packet "
            "cut against a hypothetical bad branch point, and this audit does "
            "not prove a target-priced root-selection theorem"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
