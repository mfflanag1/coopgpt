"""Exact finite supplements to PROJECTIVE_CERTIFICATE_BASELINE.txt."""
from datetime import datetime, timezone
from fractions import Fraction
from functools import reduce
from itertools import combinations
from math import factorial
from pathlib import Path
import json


def circuit_count_checks():
    cases = []
    for dimension in range(2, 6):
        for arity in range(3, min(5, dimension + 1) + 1):
            degrees = [0] * (2**dimension)
            count = 0
            for edge in combinations(range(1, 2**dimension), arity):
                if reduce(int.__xor__, edge, 0):
                    continue
                if any(
                    reduce(int.__xor__, subset, 0) == 0
                    for size in range(1, arity)
                    for subset in combinations(edge, size)
                ):
                    continue
                count += 1
                for vertex in edge:
                    degrees[vertex] += 1
            numerator = 1
            for j in range(arity - 1):
                numerator *= 2**dimension - 2**j
            predicted = Fraction(numerator, factorial(arity))
            degree = predicted * arity / (2**dimension - 1)
            assert count == predicted
            assert all(value == degree for value in degrees[1:])
            cases.append(dict(dimension=dimension, arity=arity,
                              activities=count, common_degree=int(degree)))
    return cases


def exact_examples():
    examples = []
    for arity, branches in [(4, 1), (4, 2), (4, 3), (5, 2)]:
        dimension = 1 + (arity - 2) * branches
        owners = 1 + (arity - 1) * branches
        rows = 2**dimension - 1
        degree = Fraction(1, factorial(arity - 1))
        for j in range(1, arity - 1):
            degree *= 2**dimension - 2**j
        linear = Fraction(arity - 1, arity) * degree * owners
        constant = rows * linear
        product = Fraction(1)
        for m in range(2, branches + 1):
            product *= Fraction((arity - 1) * m, (arity - 1) * (m - 1) + 1)
        lower = 1 + Fraction((arity - 1) * (branches - 1), arity * branches) * product
        examples.append(dict(
            arity=arity, M=branches, D=dimension, owners=owners,
            row_degree=str(degree), B_linear=str(linear), B_constant=str(constant),
            original_lower=str(lower),
            linear_transfer=str((linear + lower) / (linear + 1)),
            constant_transfer=str((constant + lower) / (constant + 1)),
        ))
    return examples


if __name__ == '__main__':
    result = dict(
        status='PASS', timestamp=datetime.now(timezone.utc).isoformat(),
        scope='Finite exact supplements; analytic formulas prove the asymptotic consequence.',
        circuit_enumeration=circuit_count_checks(), exact_baseline_examples=exact_examples(),
    )
    Path(__file__).with_name('projective_baseline_checks.json').write_text(
        json.dumps(result, indent=2) + '\n'
    )
    print('PASS: 9 exact circuit enumerations and 4 rational baseline examples')
