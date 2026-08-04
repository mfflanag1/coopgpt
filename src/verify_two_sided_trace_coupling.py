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

from verify_three_trace_half_integral_family import defining_coalitions, mask


def vector(n, coalition):
    return tuple(F(int(coalition >> i & 1)) for i in range(n))


def add(*vectors):
    return tuple(sum(entries, F(0)) for entries in zip(*vectors))


def scale(coefficient, values):
    return tuple(F(coefficient) * value for value in values)


def members(n, coalition):
    return [i + 1 for i in range(n) if coalition >> i & 1]


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
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
