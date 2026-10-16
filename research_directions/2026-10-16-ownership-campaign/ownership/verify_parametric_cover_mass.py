#!/usr/bin/env python3
"""Independent exact DP corroboration of the all-parameter mass proof."""
from fractions import Fraction
import json


def require(test, message):
    if not test:
        raise ValueError(message)


def states(branching, height, diameter):
    """Maximum weight of a connected subtree containing its topmost root.

    A child's weights are divided by b. State keys are exact selected heights;
    every retained child subtree already satisfies the diameter constraint.
    """
    if height == 0:
        return {0: Fraction(1)}
    child = states(branching, height - 1, diameter)
    result = {0: Fraction(1)}
    for _ in range(branching):
        next_states = dict(result)  # This child branch may be omitted.
        for current_height, current_weight in result.items():
            for child_height, child_weight in child.items():
                if current_height + child_height + 1 <= diameter:
                    new_height = max(current_height, child_height + 1)
                    new_weight = current_weight + child_weight / branching
                    next_states[new_height] = max(next_states.get(new_height, 0), new_weight)
        result = next_states
    return result


def main():
    checks = 0
    sharp_checks = 0
    representative = []
    for b in (2, 3, 5, 11):
        for h in range(1, 11):
            for d in range(1, 11):
                r = d // 2
                bound = Fraction(r + 1) + (Fraction(1, b) if d % 2 else 0)
                actual = max(states(b, h, d).values())
                require(actual <= bound, f'mass violation b={b},h={h},D={d}')
                checks += 1
                required_height = r + (d % 2)
                if h >= required_height:
                    require(actual == bound, f'claimed sharp mass not attained b={b},h={h},D={d}')
                    sharp_checks += 1
                if h == 10:
                    representative.append({'b': b, 'diameter': d, 'maximum_mass': str(actual),
                                           'bound': str(bound), 'dual_cost_multiplier': str(bound / (bound - 1))})
    print(json.dumps({'status': 'PASS', 'arithmetic': 'exact Fraction/integer',
                      'branching_factors': [2, 3, 5, 11], 'heights': [1, 10],
                      'diameters': [1, 10], 'mass_checks': checks,
                      'sharp_attainment_checks': sharp_checks,
                      'representative_cases': representative}, indent=2))


if __name__ == '__main__':
    main()
