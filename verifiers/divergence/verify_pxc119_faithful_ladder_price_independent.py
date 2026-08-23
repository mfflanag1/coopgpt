#!/usr/bin/env python3
"""Independent coefficient audit of the PXC119 ladder identity.

This file imports neither the primary PXC119 verifier nor selector/cover code.
It treats the six affine equations as formal coefficient rows and checks the
claimed overlap and slack identities by exact Gaussian elimination.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


VARS = ("T", "A", "B", "C", "Dtop", "m", "ell", "p", "q", "delta", "O")


def vec(**entries):
    return [F(entries.get(name, 0)) for name in VARS]


def rank(rows):
    matrix = [list(map(F, row)) for row in rows]
    answer = 0
    for col in range(len(VARS)):
        pivot = next((i for i in range(answer, len(matrix)) if matrix[i][col]), None)
        if pivot is None:
            continue
        matrix[answer], matrix[pivot] = matrix[pivot], matrix[answer]
        q = matrix[answer][col]
        matrix[answer] = [v / q for v in matrix[answer]]
        for i in range(len(matrix)):
            if i != answer and matrix[i][col]:
                q = matrix[i][col]
                matrix[i] = [a - q * b for a, b in zip(matrix[i], matrix[answer])]
        answer += 1
    return answer


def audit_cell(n, s):
    g = n - s - 2
    if n < 6 or s < 2 or g < 1:
        raise AssertionError((n, s, g))
    # Every row is written as left-minus-right=0.
    ex = vec(T=1, A=-s, B=-g, C=-1, Dtop=-1)
    ez = vec(T=1, m=-2, ell=-g, p=-1, q=-(s - 1))
    large = vec(C=1, Dtop=1, A=1, m=-2, p=-1)
    small = vec(A=2, p=-1, q=-1)
    delta = vec(A=1, q=-1, delta=-1)
    overlap = vec(O=1, m=-2, B=-g, A=-1, q=-(s - 1))

    equations = [ex, ez, large, small, delta, overlap]
    base_rank = rank(equations)
    overlap_identity = vec(O=1, T=-1, delta=s)
    if rank(equations + [overlap_identity]) != base_rank:
        raise AssertionError("O=T-s delta is not in the affine row span")

    D = F(n + 1) + F(2 * (s - 1), g)
    # The exact nonnegative price certificate after affine elimination is
    # T-D delta = 2(m-ell)+(g+2)(B-A)+n q.
    price = vec(
        T=1, delta=-D, m=-2, ell=2,
        B=-(g + 2), A=g + 2, q=-n,
    )
    if rank(equations + [price]) != base_rank:
        raise AssertionError("price identity is not in the affine row span")
    # Evaluate the price identity on independently generated rational points
    # spanning the affine solution space; this catches coefficient/sign drift
    # without importing the primary derivation.
    samples = []
    for q0 in (F(0), F(1, 37), F(2, 41)):
        for gap in (F(1, 29), F(2, 31)):
            A = q0 + gap
            B = A + F(1, 43)
            ell = B + F(s - 1, g) * gap
            m = ell + F(1, 47)
            p = 2 * A - q0
            C = m + gap / 3
            E = 2 * m + p - A - C
            T = s * A + g * B + C + E
            O = 2 * m + g * B + A + (s - 1) * q0
            lhs = T - D * gap
            rhs = 2 * (m - ell) + (g + 2) * (B - A) + n * q0
            if lhs != rhs or O != T - s * gap:
                raise AssertionError((n, s, lhs, rhs, O, T - s * gap))
            samples.append((T, O))

    return {"n": n, "s": s, "g": g, "D": str(D), "samples": len(samples)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cells = [audit_cell(n, s) for n in range(6, 65) for s in range(2, n - 2)]
    payload = {
        "claim": "independent formal-coefficient audit of PXC119",
        "cells": len(cells),
        "n_range": [6, 64],
        "sample_count": sum(q["samples"] for q in cells),
        "first": cells[0],
        "last": cells[-1],
        "scope": (
            "independent exact coefficient/sign audit; the manuscript supplies "
            "the conventional all-n parity argument"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
