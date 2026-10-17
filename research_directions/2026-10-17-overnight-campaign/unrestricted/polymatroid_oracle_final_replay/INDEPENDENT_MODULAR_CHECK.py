"""Six exact modular instances, using additive prices as an independent reference."""
from pathlib import Path
import importlib.util
import json
from fractions import Fraction as Q

B = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("oracle", B / "POLYMATROID_ORACLE_PRICES.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def modular_oracle(a, c, rank):
    return sum(1 << j for j in range(len(c)) if a * rank(1 << j) - c[j] <= 0)


def check(weights, common, capacities, expected_calls=None):
    def rank(mask):
        return sum((w for j, w in enumerate(weights) if mask >> j & 1), Q(0))

    got = module.polymatroid_prices(common, capacities, rank, modular_oracle)
    expected_value = sum((min(common * w, c) for w, c in zip(weights, capacities)), Q(0))
    prices = [Q(0)] * (len(capacities) + 1)
    if common:
        for j, (w, c) in enumerate(zip(weights, capacities)):
            if w and c:
                ratio = c / (common * w)
                probability = ratio / 2 if ratio <= 1 else 1 - 1 / (2 * ratio)
                prices[0] += w * probability
                prices[j + 1] = 1 - probability
    assert got["value"] == expected_value
    assert got["prices"] == tuple(prices)
    if expected_calls is not None:
        assert got["maximal_sfm_calls"] == expected_calls
    return {
        "m": len(capacities), "active": sum(c > 0 for c in capacities),
        "maximal_calls": got["maximal_sfm_calls"], "chain_length": len(got["chain"]),
    }


cases = [
    check([Q(1)] * 40, Q(1), [Q(j + 1) for j in range(40)], 79),
    check([Q(j + 1, 3) for j in range(40)], Q(7, 5), [Q(7 * (j + 1), 15) for j in range(40)], 1),
    check([Q(0), Q(0), Q(1), Q(2), Q(3), Q(4)], Q(3, 2), [Q(7), Q(1, 3), Q(0), Q(4), Q(3), Q(5)]),
    check([Q(0)] * 40, Q(1), [Q(1)] * 40, 0),
    check([Q(1)] * 40, Q(0), [Q(1)] * 40, 0),
    check([Q(1)] * 40, Q(1), [Q(0)] * 40, 0),
]
out = {
    "status": "PASS",
    "scope": "Six exact modular tests against direct additive prices: sharp forty-row oracle count, tied breakpoint, loops, inactive rows, zero faces. No all-profile proof claimed.",
    "cases": cases,
}
(B / "INDEPENDENT_MODULAR_CHECKS.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
