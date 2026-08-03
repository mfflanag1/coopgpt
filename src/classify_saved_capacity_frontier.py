"""Classify saved exact witnesses against the proved capacity certificates.

The scan is exact.  It does not recompute every exposed-face maximum; it asks
only whether a star-failure instance is covered by (i) the two-level residual
theorem or (ii) the off-side slack-domination theorem.  Cases covered by
neither are the next symbolic targets.
"""
from __future__ import annotations

import argparse
import glob
import json
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from functools import partial
from pathlib import Path

from scipy.optimize import linprog

from lemD import residual_cover, star_holds, xS
from leximin import leximin_core_exact, leximin_core_float
from tugame import Game


def members(mask, n):
    return [i + 1 for i in range(n) if mask >> i & 1]


def residual_cover_float(game, phi, target, tolerance=1e-6):
    """Screening analogue of lemD.residual_cover; returns residual coordinates."""
    tights = [
        coalition
        for coalition in range(1, game.N)
        if abs(xS(phi, coalition, game.n) - float(game.v[coalition])) <= tolerance
    ]
    players = [i for i in range(game.n) if target >> i & 1]
    count = len(tights)
    residual_index = {player: count + 1 + index for index, player in enumerate(players)}
    variable_count = count + 1 + len(players)
    equalities = []
    for player in range(game.n):
        row = [0.0] * variable_count
        for index, coalition in enumerate(tights):
            if coalition >> player & 1:
                row[index] = -1.0
        row[count] = 1.0
        if target >> player & 1:
            row[residual_index[player]] = -1.0
        equalities.append(row)
    bounds = [(0, None)] * count + [(None, None)] + [(1, None)] * len(players)
    result = linprog(
        [0.0] * variable_count,
        A_eq=equalities,
        b_eq=[0.0] * game.n,
        bounds=bounds,
        method="highs",
    )
    if not result.success:
        return None
    return {player: result.x[residual_index[player]] for player in players}


def classify(path_string, use_float=False):
    path = Path(path_string)
    payload = json.loads(path.read_text())
    n = payload["n"]
    game = Game(n, [F(value) for value in payload["v"]])
    raw_cases = payload.get("cases")
    if raw_cases is None:
        raw_cases = [{"S": payload["S"]}]
    phi = (
        leximin_core_float(n, game.v, tol=1e-9)
        if use_float
        else leximin_core_exact(game)
    )
    if phi is None:
        return [{"path": path_string, "error": "leximin failed"}]

    output = []
    for case_index, raw_case in enumerate(raw_cases):
        target = sum(1 << player for player in raw_case["S"])
        target_slack = xS(phi, target, n) - game.v[target]
        if use_float:
            float_residuals = residual_cover_float(game, phi, target)
            holds = float_residuals is None
        else:
            holds, _, _ = star_holds(game, phi, target)
        if holds:
            output.append(
                {
                    "path": path_string,
                    "case": case_index,
                    "S": members(target, n),
                    "slack": str(target_slack),
                    "star_holds": True,
                }
            )
            continue

        if use_float:
            levels = sorted({round(value, 7) for value in float_residuals.values()})
        else:
            cover = residual_cover(game, phi, target)
            levels = sorted(set(cover["r"].values())) if cover is not None else []
        off_side = game.N ^ target
        carrier_certificates = []
        carrier_margins = []
        for face in range(1, game.N):
            if face & target != face or face == target:
                continue
            carrier = off_side | face
            face_slack = xS(phi, face, n) - game.v[face]
            carrier_slack = xS(phi, carrier, n) - game.v[carrier]
            carrier_margins.append(carrier_slack - face_slack)
            if carrier_slack <= face_slack + (1e-6 if use_float else 0):
                carrier_certificates.append(
                    {
                        "face": members(face, n),
                        "carrier": members(carrier, n),
                        "face_slack": str(face_slack),
                        "carrier_slack": str(carrier_slack),
                        "carrier_tight": carrier_slack == 0,
                    }
                )
        output.append(
            {
                "path": path_string,
                "case": case_index,
                "S": members(target, n),
                "slack": str(target_slack),
                "star_holds": False,
                "residual_levels": [str(value) for value in levels],
                "two_level_covered": len(levels) <= 2,
                "off_side_covered": bool(carrier_certificates),
                "carrier_escape_margin": str(min(carrier_margins)),
                "off_side_certificates": carrier_certificates,
                "uncovered": len(levels) >= 3 and not carrier_certificates,
            }
        )
    return output


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "patterns",
        nargs="*",
        default=[
            "results/WITNESS_KEY_CX_n6*.json",
            "results/WITNESS_KEY_CX_n7*.json",
            "results/WITNESS_KEY_FALSE_n6.json",
        ],
    )
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--frontier-only", action="store_true")
    parser.add_argument(
        "--float-screen",
        action="store_true",
        help="Use scipy screening arithmetic; exactify any reported frontier separately.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    paths = sorted({path for pattern in args.patterns for path in glob.glob(pattern)})
    classifier = partial(classify, use_float=args.float_screen)
    if args.jobs == 1:
        nested = list(map(classifier, paths))
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            nested = list(pool.map(classifier, paths))
    cases = [case for group in nested for case in group]
    star_failures = [case for case in cases if case.get("star_holds") is False]
    summary = {
        "files": len(paths),
        "cases": len(cases),
        "star_failures": len(star_failures),
        "two_level_covered": sum(case["two_level_covered"] for case in star_failures),
        "off_side_covered": sum(case["off_side_covered"] for case in star_failures),
        "covered_by_union": sum(
            case["two_level_covered"] or case["off_side_covered"]
            for case in star_failures
        ),
        "uncovered": sum(case["uncovered"] for case in star_failures),
    }
    if star_failures:
        closest = max(star_failures, key=lambda case: F(case["carrier_escape_margin"]))
        summary["largest_carrier_escape_margin"] = closest["carrier_escape_margin"]
        summary["closest_case"] = {
            "path": closest["path"],
            "case": closest["case"],
            "S": closest["S"],
            "slack": closest["slack"],
        }
        positive_slack = [case for case in star_failures if F(case["slack"]) > 0]
        if positive_slack:
            closest_positive = max(
                positive_slack, key=lambda case: F(case["carrier_escape_margin"])
            )
            summary["largest_margin_with_positive_slack"] = closest_positive[
                "carrier_escape_margin"
            ]
            summary["closest_positive_slack_case"] = {
                "path": closest_positive["path"],
                "case": closest_positive["case"],
                "S": closest_positive["S"],
                "slack": closest_positive["slack"],
            }
    reported_cases = (
        [case for case in cases if case.get("uncovered")]
        if args.frontier_only
        else cases
    )
    print(json.dumps({"summary": summary, "cases": reported_cases}, indent=2))
