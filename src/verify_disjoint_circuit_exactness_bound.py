"""Exact dual proof that a full orbit of disjoint n=5 circuits is harmless.

The circuit exists in the family Farkas cone, but its negative right-hand-side
inequality is incompatible with exactness.  The certificate below is a sparse
dual of the LP that encodes one tight core witness for every coalition.
"""
from fractions import Fraction as F
from itertools import permutations

import numpy as np

import construct_exact_disjoint_circuit as model
from search_both_sensitive_circuits import eliminated_matrix, exactify_support


# Nonzero inequality duals are stored with positive signs mu=-y, since the
# primal core-witness rows are A z <= 0 and SciPy's minimization dual has y<=0.
INEQUALITY_MULTIPLIERS = {
    502: F(1, 6), 504: F(1, 6), 580: F(5, 6),
    635: F(1, 6), 647: F(1, 6), 649: F(1, 6),
    664: F(1, 6), 665: F(1, 6), 670: F(1, 6), 675: F(1, 3),
    966: F(1), 984: F(1, 2), 985: F(1, 2),
    1371: F(1, 3), 1374: F(1, 3),
    1864: F(1, 2), 1885: F(1, 2),
    2312: F(1, 2), 2314: F(1, 3), 2315: F(2, 3),
    2326: F(1, 6), 2333: F(1),
}
EQUALITY_MULTIPLIERS = {
    32: -F(1, 6), 33: -F(1, 6),
    38: -F(5, 6), 39: F(5, 6), 43: -F(1, 3),
    44: -F(1, 6), 45: -F(1, 6),
    64: -F(1), 65: -F(1, 2),
    90: -F(1, 3), 91: -F(1, 3),
    124: -F(1, 2),
    154: -F(1), 155: -F(1, 6),
}


def decode_inequality(index):
    game, remainder = divmod(index, len(model.PROPER) ** 2)
    tight_offset, coalition_offset = divmod(remainder, len(model.PROPER))
    return game, tight_offset + 1, coalition_offset + 1


def decode_equality(index):
    witness_offset, kind = divmod(index, 2)
    game, tight_offset = divmod(witness_offset, len(model.PROPER))
    return game, tight_offset + 1, ("efficiency" if kind == 0 else "tightness")


def encode_inequality(game, tight, coalition):
    return (game * len(model.PROPER) + tight - 1) * len(model.PROPER) + coalition - 1


def encode_equality(game, tight, kind):
    return 2 * (game * len(model.PROPER) + tight - 1) + (kind == "tightness")


def preserving_permutations():
    for perm_A in permutations((0, 1, 2)):
        for perm_B in permutations((3, 4)):
            yield tuple(perm_A + perm_B)


def permute_mask(mask, permutation):
    result = 0
    for player in range(model.N):
        if mask >> player & 1:
            result |= 1 << permutation[player]
    return result


def mapped_circuit(permutation):
    core_rows = tuple(
        (game, permute_mask(coalition, permutation))
        for game, coalition in model.CIRCUIT_CORE_ROWS
    )
    mono_rows = (
        ("mono", 0, 1, permutation[2], model.A),
        ("mono", 0, 2, permutation[4], model.B),
    )
    return core_rows, mono_rows


def verify_circuit(permutation):
    matrix, _inequalities, _equalities, rowmeta = eliminated_matrix(
        model.N, model.A, model.B
    )
    core_rows, mono_rows = mapped_circuit(permutation)
    target = set(core_rows)
    support = [
        index
        for index, meta in enumerate(rowmeta)
        if (meta[0] == "core" and (meta[1], meta[2]) in target)
        or meta in mono_rows
    ]
    weights = exactify_support(matrix, support)
    assert weights == [1] * 10
    exact = np.asarray(matrix[:, support], dtype=int)
    assert np.linalg.matrix_rank(exact.astype(float)) == 9
    return support


def verify_exactness_dual(permutation):
    A_ub, b_ub, A_eq, b_eq, _bounds = model.build_lp()
    A_ub = A_ub[:-1]
    b_ub = b_ub[:-1]
    combined = [F(0)] * model.VARIABLE_COUNT
    for row_index, mu in INEQUALITY_MULTIPLIERS.items():
        game, tight, coalition = decode_inequality(row_index)
        mapped_index = encode_inequality(
            game,
            permute_mask(tight, permutation),
            permute_mask(coalition, permutation),
        )
        assert mu > 0 and b_ub[mapped_index] == 0
        for column, coefficient in enumerate(A_ub[mapped_index]):
            combined[column] -= mu * int(coefficient)
    for row_index, beta in EQUALITY_MULTIPLIERS.items():
        game, tight, kind = decode_equality(row_index)
        mapped_index = encode_equality(
            game, permute_mask(tight, permutation), kind
        )
        for column, coefficient in enumerate(A_eq[mapped_index]):
            combined[column] += beta * int(coefficient)
    target = [F(0)] * model.VARIABLE_COUNT
    core_rows, _mono_rows = mapped_circuit(permutation)
    for game, coalition in core_rows:
        target[model.worth_index(coalition)] -= 1
        bump = model.bump_index(game, coalition)
        if bump is not None:
            target[bump] -= 1
    assert combined == target

    dual_bound = sum(
        beta * F(int(b_eq[row_index]))
        for row_index, beta in EQUALITY_MULTIPLIERS.items()
    )
    assert dual_bound == -model.EFFICIENCY_TOTAL
    return dual_bound


def verify():
    supports = set()
    for permutation in preserving_permutations():
        support = verify_circuit(permutation)
        supports.add(tuple(support))
        bound = verify_exactness_dual(permutation)
    print("DISJOINT CIRCUIT ORBIT AND EXACTNESS BOUNDS VERIFIED")
    print("  arm-preserving permutations checked:", 12)
    print("  distinct exact unit circuits in orbit:", len(supports))
    print("  exact unit circuit support size:", len(next(iter(supports))))
    print("  exactness dual: circuit objective >=", bound)
    print("  hence Farkas margin >= 0 for every exact endpoint triple")
    print("  core-witness inequalities used:")
    for index, multiplier in INEQUALITY_MULTIPLIERS.items():
        print("   ", decode_inequality(index), multiplier)
    print("  efficiency/tightness equalities used:")
    for index, multiplier in EQUALITY_MULTIPLIERS.items():
        print("   ", decode_equality(index), multiplier)


if __name__ == "__main__":
    verify()
