#!/usr/bin/env python3
"""Independent dimension-free algebra audit for PXC106.

No project LP, selector, cover, family, or discovery module is imported.
The exact n=6 active-set calibration is supplied separately by PXC104/105.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path


def players_mask(players):
    answer = 0
    for player in players:
        answer |= 1 << player
    return answer


def positive_part(value):
    return max(F(0), F(value))


def trace_value(A, p, q, include_a, include_b, full_J, full_K):
    candidates = [F(12)]
    if include_a or include_b:
        candidates.append(F(16))
    if full_J:
        candidates.append(F(12 + p))
    if include_a and full_J:
        candidates.append(F(12 + p) + A)
    if full_K:
        candidates.append(F(12 + q))
    if include_a and full_K:
        candidates.append(F(12 + q) + A)
    return max(candidates)


def explicit_trace_minimizer(n, p, q, A, J, K, selected):
    """Construct the promised lower-envelope minimizer for rh union U.

    Selected members of a non-full block receive zero; the required aggregate
    block mass is concentrated on one omitted member.  All remaining efficient
    mass is then placed on any omitted non-top coordinate.
    """
    full_J = all(i in selected for i in J)
    full_K = all(i in selected for i in K)
    include_a, include_b = 2 in selected, 3 in selected
    level = trace_value(A, p, q, include_a, include_b, full_J, full_K)
    point = [F(0)] * n
    point[0] = level
    if not include_a:
        point[2] = A
    if not include_b:
        point[3] = positive_part(16 - level)
    if not full_J:
        omitted = next(i for i in J if i not in selected)
        point[omitted] = max(
            F(0), F(12 + p) - level,
            F(12 + p) + A - level - point[2],
        )
    if not full_K:
        omitted = next(i for i in K if i not in selected)
        point[omitted] = max(
            F(0), F(12 + q) - level,
            F(12 + q) + A - level - point[2],
        )
    used = sum(point)
    total = F(16 + p + q) + A
    if used > total:
        raise AssertionError(("attainment mass budget", p, q, A, selected, used, total))
    omitted = next(i for i in range(2, n) if i not in selected)
    point[omitted] += total - used
    return level, tuple(point)


def verify_dimension(n):
    m = n - 4
    p, q = 1, m - 1
    A = 4 + F(1, m + 1)
    J = tuple(range(4, 4 + p))
    K = tuple(range(4 + p, n))
    rh = (0, 1)
    row_a = players_mask(rh + (2,))
    row_b = players_mask(rh + (3,))
    row_J = players_mask(rh + J)
    row_aJ = players_mask(rh + (2,) + J)
    row_K = players_mask(rh + K)
    row_aK = players_mask(rh + (2,) + K)
    pair = players_mask(rh)
    rows = (pair, row_b, row_J, row_aJ, row_K, row_aK)
    covers = ((pair,), (row_b, row_J, row_aK),
              (row_b, row_aJ, row_K))

    total = 16 + A + m
    u = (A + m) / (m + 1)
    top = (16 - u) / 2
    x = (top, top) + (u,) * (m + 2)
    z = (F(6), F(6), A, F(4)) + (F(1),) * m
    if sum(x) != total or sum(z) != total or not top > u > 0:
        raise AssertionError(("selector totals/order", n))

    slack_J = p * (A - 1) / (m + 1) - (A - 4)
    slack_K = q * (A - 1) / (m + 1) - (A - 4)
    if not (4 < A < 6 and slack_J > 0 and slack_K > 0):
        raise AssertionError(("chamber", n, A, slack_J, slack_K))

    def coal(point, row):
        return sum(point[i] for i in range(n) if row >> i & 1)

    bounds = {
        row_a: F(16), row_b: F(16),
        row_J: F(12 + p), row_aJ: F(12 + p) + A,
        row_K: F(12 + q), row_aK: F(12 + q) + A,
    }
    if coal(x, row_a) != 16 or coal(x, row_b) != 16:
        raise AssertionError(("Cx tightness", n))
    if any(coal(x, row) <= bound for row, bound in bounds.items()
           if row not in (row_a, row_b)):
        raise AssertionError(("other x row not strict", n))
    if any(coal(z, row) != bound for row, bound in bounds.items()
           if row != row_a) or not coal(z, row_a) > 16:
        raise AssertionError(("z menu", n))

    # Explicit singleton witnesses.
    witness_r = (F(0), F(12), A, F(4)) + (F(1),) * m
    witness_h = (F(12), F(0), A, F(4)) + (F(1),) * m
    all_root = (total,) + (F(0),) * (n - 1)
    for witness in (witness_r, witness_h, all_root):
        if sum(witness) != total or any(coal(witness, row) < bound
                                        for row, bound in bounds.items()):
            raise AssertionError(("singleton witness", n, witness))

    # Both positive covers partition the non-top players and contain both tops
    # three times. Thus weights 1/4 give eta=1/4 and alpha=(1/2,1/2).
    for cover in covers[1:]:
        for player in range(2, n):
            if sum((row >> player) & 1 for row in cover) != 1:
                raise AssertionError(("outsider load", n, cover, player))
        for player in (0, 1):
            if sum((row >> player) & 1 for row in cover) != 3:
                raise AssertionError(("top load", n, cover, player))

    avg_all = 1 + (A - 4) / m
    avg_J = 1 + (A - 4) / p
    avg_K = 1 + (A - 4) / q
    reduced = (
        (F(6), F(6), F(4), F(4)) + (avg_all,) * m,
        (F(6), F(6), F(4), F(4)) + (F(1),) * p + (avg_K,) * q,
        (F(6), F(6), F(4), F(4)) + (avg_J,) * p + (F(1),) * q,
    )
    for point in reduced:
        if sum(point) != total or point == z:
            raise AssertionError(("reduced selector", n, point))
        if any(coal(point, row) < bound for row, bound in bounds.items()
               if row in (row_a, row_b)):
            raise AssertionError(("Cx feasibility", n, point))

    # Cross blocking: cover 1 shifts A-4 from a to K; cover 2 shifts it to J.
    d_left = tuple(reduced[1][i] - z[i] for i in range(n))
    d_right = tuple(reduced[2][i] - z[i] for i in range(n))
    if not (coal(d_left, row_aJ) < 0 and coal(d_left, row_aK) == 0
            and coal(d_right, row_aK) < 0 and coal(d_right, row_aJ) == 0):
        raise AssertionError(("cross blockers", n))

    return {
        "n": n, "p": p, "q": q, "A": str(A),
        "total": str(total), "u": str(u), "top": str(top),
        "slack_J": str(slack_J), "slack_K": str(slack_K),
        "rows": list(rows), "covers": [list(c) for c in covers],
        "reduced_lmax": [list(map(str, point)) for point in reduced],
        "cover_union_exhausts_z_tight_menu": True,
        "common_staged_descent": False,
    }


def verify_attainment_recipe(p, q, A):
    n = p + q + 4
    J = tuple(range(4, 4 + p))
    K = tuple(range(4 + p, n))
    rh = (0, 1)
    bounds = {
        players_mask(rh + (2,)): F(16),
        players_mask(rh + (3,)): F(16),
        players_mask(rh + J): F(12 + p),
        players_mask(rh + (2,) + J): F(12 + p) + A,
        players_mask(rh + K): F(12 + q),
        players_mask(rh + (2,) + K): F(12 + q) + A,
    }

    def representatives(block):
        answer = [()]
        if len(block) > 1:
            answer.append((block[0],))
        answer.append(block)
        return tuple(answer)

    count = 0
    for include_a, include_b, part_J, part_K in product(
        (False, True), (False, True), representatives(J), representatives(K)
    ):
        selected = set(part_J) | set(part_K)
        if include_a:
            selected.add(2)
        if include_b:
            selected.add(3)
        if len(selected) == n - 2:
            continue
        level, point = explicit_trace_minimizer(
            n, p, q, A, J, K, frozenset(selected)
        )
        if sum(point) != F(16 + p + q) + A:
            raise AssertionError(("attainment total", p, q, A, selected))
        if any(
            sum(point[i] for i in range(n) if mask >> i & 1) < bound
            for mask, bound in bounds.items()
        ):
            raise AssertionError(("attainment feasibility", p, q, A, selected, point))
        objective = point[0] + point[1] + sum(point[i] for i in selected)
        if objective != level:
            raise AssertionError(("attainment objective", p, q, A, selected, point))
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    dimensions = [verify_dimension(n) for n in range(6, 65)]
    attainment_grid_cases = 0
    attainment_trace_classes = 0
    for p in range(1, 9):
        for q in range(1, 9):
            m = p + q
            for A in (F(17, 4), F(9, 2), F(5), F(21, 4), F(11, 2)):
                if not (
                    4 < A < 6
                    and p * (A - 1) > (m + 1) * (A - 4)
                    and q * (A - 1) > (m + 1) * (A - 4)
                ):
                    continue
                attainment_grid_cases += 1
                attainment_trace_classes += verify_attainment_recipe(p, q, A)
    payload = {
        "claim": "independent algebraic PXC106 all-n cross-cover audit",
        "dimensions_checked": [6, 64],
        "explicit_specialization": "p=1, q=n-5, A=4+1/(n-3)",
        "checks": dimensions,
        "explicit_minimizer_recipe": {
            "description": (
                "put L on r; put A on omitted a; put (16-L)_+ on "
                "omitted b; for each non-full block put the maximum row "
                "deficit on one omitted member; put all unused total mass "
                "on an omitted coordinate"
            ),
            "grid_parameter_cases": attainment_grid_cases,
            "grid_trace_classes": attainment_trace_classes,
            "grid_scope": "1<=p,q<=8 at five rational A anchors inside the chamber",
        },
        "non_null_witnesses": {
            "r,h": "v(N)-v(N\\{r or h})=16+A+p+q>0",
            "a,b": "v(rha)-v(rh)=v(rhb)-v(rh)=4>0",
            "each i in J": "v(rhJ)-v(rh(J\\{i}))=p>0",
            "each i in K": "v(rhK)-v(rh(K\\{i}))=q>0",
        },
        "proof_interfaces": {
            "lmin": (
                "R-sum(JK)>=16-A-(p+q) gives floor "
                "u=(A+p+q)/(p+q+1); equality pins every non-top coordinate"
            ),
            "lmax": (
                "either three-row cover gives R>=12; residual row bounds "
                "pin b=4, a=A, sum(J)=p, sum(K)=q and block equalization"
            ),
            "classification": (
                "the cover union exhausts the z-tight menu; its equations pin "
                "a,b and both block sums, leaving no staged descent"
            ),
        },
        "independence": (
            "standalone Fraction incidence/algebra checker; no project LP, "
            "selector, cover, family, or discovery imports"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
