"""Exact audit of the two-sided trace-coupling normal form.

The theorem is a coordinatewise identity.  This script checks its forward
and reverse forms on symbolic obstruction families; it is not independent
proof evidence.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from verify_three_trace_half_integral_family import (
    coalition_sum as three_coalition_sum,
    defining_coalitions,
    lower_envelope as three_lower_envelope,
    mask,
    vertices as three_vertices,
)
from verify_two_poorer_rich_family import (
    coalition_sum as internal_coalition_sum,
    generators as internal_generators,
    lower_envelope as internal_lower_envelope,
)


def vector(n, coalition):
    return tuple(F(int(coalition >> i & 1)) for i in range(n))


def add(*vectors):
    return tuple(sum(entries, F(0)) for entries in zip(*vectors))


def scale(coefficient, values):
    return tuple(F(coefficient) * value for value in values)


def members(n, coalition):
    return [i + 1 for i in range(n) if coalition >> i & 1]


def canonical_packet(name, poor_loads, root_slack=None, completion_slacks=None):
    loads = tuple(F(value) for value in poor_loads)
    maximum = max(loads)
    completion = tuple(maximum - value for value in loads)
    excess = F(1) + (len(loads) - 1) * maximum - sum(loads, F(0))
    if excess != F(1) - maximum + sum(completion, F(0)):
        raise AssertionError(f"{name}: canonical excess identity failed")
    if excess <= 0:
        raise AssertionError(f"{name}: packet does not have positive excess")
    result = {
        "name": name,
        "poor_loads": [str(value) for value in loads],
        "maximum_poor_load": str(maximum),
        "canonical_completion": [str(value) for value in completion],
        "canonical_rooted_excess": str(excess),
    }
    completion_mass = sum(completion, F(0))
    if maximum < 1:
        if completion_mass <= 0:
            raise AssertionError(f"{name}: underloaded packet cannot transfer slack")
        result["strict_slack_amplification_factor"] = str(excess / completion_mass)
    if root_slack is not None or completion_slacks is not None:
        if root_slack is None or completion_slacks is None:
            raise AssertionError(f"{name}: incomplete slack-transfer audit")
        root_slack = F(root_slack)
        completion_slacks = tuple(F(value) for value in completion_slacks)
        if len(completion_slacks) != len(loads):
            raise AssertionError(f"{name}: wrong completion-slack dimension")
        weighted = sum(
            weight * slack
            for weight, slack in zip(completion, completion_slacks)
        )
        required = excess * root_slack
        if weighted < required:
            raise AssertionError(f"{name}: exact-balanced slack transfer failed")
        result["root_slack"] = str(root_slack)
        result["completion_slacks"] = [str(value) for value in completion_slacks]
        result["weighted_completion_slack"] = str(weighted)
        result["required_rooted_slack"] = str(required)
        result["slack_transfer_saturated"] = weighted == required
    return result


def realized_slack_transfer_audits():
    """Recompute the sharp packet slacks from the two exact-game families."""
    three_points = three_vertices(1, 2, 2)
    three_game = three_lower_envelope(three_points)
    three_phi = tuple([F(1), F(1)] + [F(2)] * 5)
    three_root = mask(range(2, 7))
    three_root_slack = (
        three_coalition_sum(three_phi, three_root) - three_game.v[three_root]
    )
    three_completion = three_root | 1
    three_completion_slack = (
        three_coalition_sum(three_phi, three_completion)
        - three_game.v[three_completion]
    )

    m, h = 2, 4
    scale = (h - 2) * (h - 3)
    internal_points = internal_generators(m, h)
    internal_values = internal_lower_envelope(internal_points)
    internal_phi = tuple([scale] * m + [2 * scale] * h)
    internal_root = mask(range(m, m + h))
    internal_root_slack = (
        internal_coalition_sum(internal_phi, internal_root)
        - internal_values[internal_root]
    )
    # Player 2 is absent from every gaining-labeled co-singleton and is the
    # unique losing-player completion in the canonical packet.
    internal_completion = internal_root | (1 << 1)
    internal_completion_slack = (
        internal_coalition_sum(internal_phi, internal_completion)
        - internal_values[internal_completion]
    )

    three_audit = canonical_packet(
        "three_trace_minimal_packet",
        (0, F(1, 2)),
        root_slack=three_root_slack,
        completion_slacks=(three_completion_slack, 0),
    )
    three_marginal = three_game.v[three_completion] - three_game.v[three_root]
    three_bound = F(1) - (1 - F(1, 2)) / F(1, 2) * three_root_slack
    if three_marginal > three_bound:
        raise AssertionError("three-trace marginal-deficit bound failed")
    three_audit.update(
        {
            "losing_poorer_payoff": "1",
            "coalition_marginal": str(three_marginal),
            "marginal_deficit_upper_bound": str(three_bound),
            "marginal_deficit_saturated": three_marginal == three_bound,
        }
    )

    internal_audit = canonical_packet(
        "four_cosingleton_minimal_packet",
        (0, F(2, 3)),
        root_slack=internal_root_slack,
        completion_slacks=(internal_completion_slack, 0),
    )
    internal_marginal = (
        internal_values[internal_completion] - internal_values[internal_root]
    )
    internal_bound = F(scale) - (1 - F(2, 3)) / F(2, 3) * internal_root_slack
    if internal_marginal > internal_bound:
        raise AssertionError("co-singleton marginal-deficit bound failed")
    internal_audit.update(
        {
            "losing_poorer_payoff": str(scale),
            "coalition_marginal": str(internal_marginal),
            "marginal_deficit_upper_bound": str(internal_bound),
            "marginal_deficit_saturated": internal_marginal == internal_bound,
        }
    )
    return [three_audit, internal_audit]


def audit(name, n, root, positive, gamma, beta):
    """Audit one identity and recover its two trace covers exactly."""
    full = (1 << n) - 1
    poor = full ^ root
    poor_players = [i for i in range(n) if poor >> i & 1]
    spokes = {}
    protectors = []
    for coalition, coefficient in positive:
        coefficient = F(coefficient)
        matched = [i for i in poor_players if coalition == root | (1 << i)]
        if matched:
            i = matched[0]
            spokes[i] = spokes.get(i, F(0)) + coefficient
        else:
            protectors.append((coalition, coefficient))

    lhs = add(
        *(scale(weight, vector(n, coalition)) for coalition, weight in positive),
        scale(-F(gamma), vector(n, root)),
    )
    rhs = scale(F(beta), vector(n, full))
    if lhs != rhs:
        raise AssertionError(f"{name}: rooted identity failed")

    rich_players = [i for i in range(n) if root >> i & 1]
    rich_loads = {
        sum(weight for coalition, weight in protectors if coalition >> i & 1)
        for i in rich_players
    }
    if len(rich_loads) != 1:
        raise AssertionError(f"{name}: nonuniform rich trace cover")
    alpha = rich_loads.pop()
    poor_loads = []
    for i in poor_players:
        load = sum(
            weight for coalition, weight in protectors if coalition >> i & 1
        ) + spokes.get(i, F(0))
        poor_loads.append(load)
    if any(load != F(beta) for load in poor_loads):
        raise AssertionError(f"{name}: poor trace completion failed")
    tau = sum(spokes.values(), F(0))
    if F(gamma) != alpha - F(beta) + tau:
        raise AssertionError(f"{name}: scalar coupling failed")

    # Reconstruct the full identity using only the two cover equations.
    reconstructed = [F(beta)] * n
    for i in rich_players:
        reconstructed[i] = alpha + tau - F(gamma)
    if tuple(reconstructed) != rhs:
        raise AssertionError(f"{name}: reverse reconstruction failed")

    return {
        "name": name,
        "player_count": n,
        "root": members(n, root),
        "protector_count": len(protectors),
        "spoke_count": len(spokes),
        "alpha_rich_cover_load": str(alpha),
        "beta_poor_cover_load": str(F(beta)),
        "tau_spoke_mass": str(tau),
        "gamma_exceptional_coefficient": str(F(gamma)),
        "coupling_equation": f"{gamma} = {alpha} - {F(beta)} + {tau}",
        "pure_block_star": not protectors,
    }


def five_player():
    n = 5
    left = mask((0, 2, 4))
    right = mask((2, 3, 4))
    root = left & right
    exterior = ((1 << n) - 1) & ~(left | right)
    positive = [(left, 1), (right, 1), (root | exterior, 1)]
    return audit("five_player_rooted_broken_diamond", n, root, positive, 2, 1)


def universal_star(m, h):
    n = m + h
    root = mask(range(m, n))
    positive = [(root | (1 << i), 1) for i in range(m)]
    return audit(f"universal_block_star_m{m}_h{h}", n, root, positive, m - 1, 1)


def three_trace():
    (poor_a, _), _C, _A, _B, constraints = defining_coalitions(1, 2, 2)
    n = 7
    root = mask(range(2, 7))
    traces = [mask(coalition) for coalition, _ in constraints]
    positive = [(coalition, 1) for coalition in traces]
    positive.append((root | (1 << poor_a), 1))
    return audit("seven_player_rooted_three_trace", n, root, positive, 2, 1)


def synthetic_rich_active():
    """A non-family coupling with alpha>0, generated from both covers."""
    n = 5
    root = mask((0, 1))
    first = mask((0, 2, 3))
    second = mask((1, 3, 4))
    positive = [
        (first, 1),
        (second, 1),
        (root | (1 << 2), 1),
        (root | (1 << 4), 1),
    ]
    return audit("synthetic_rich_active_reverse_case", n, root, positive, 1, 2)


def synthetic_rich_null():
    """Audit the abstract alpha=0 branch excluded after Lmin pruning."""
    n = 5
    root = mask((0, 1))
    poor_pair = mask((2, 3))
    positive = [
        (poor_pair, F(1, 2)),
        (root | (1 << 2), F(1, 2)),
        (root | (1 << 3), F(1, 2)),
        (root | (1 << 4), 1),
    ]
    return audit("synthetic_rich_null_reverse_case", n, root, positive, 1, 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-poorer-side", type=int, default=7)
    parser.add_argument("--max-richer-side", type=int, default=6)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = [
        five_player(),
        three_trace(),
        synthetic_rich_active(),
        synthetic_rich_null(),
    ]
    cases.extend(
        universal_star(m, h)
        for m in range(2, args.max_poorer_side + 1)
        for h in range(1, args.max_richer_side + 1)
    )
    payload = {
        "status": "two-sided trace-coupling normal form audited",
        "arithmetic": "exact rational",
        "finite_audit_is_not_proof": True,
        "case_count": len(cases),
        "cases": cases,
        "single_packet_excess_audits": [
            *realized_slack_transfer_audits(),
            canonical_packet("synthetic_partition_packet", (1, 2, 1)),
        ],
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
