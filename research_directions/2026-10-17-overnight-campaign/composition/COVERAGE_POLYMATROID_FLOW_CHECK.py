"""Dependency-free exact checks; small exhaustive references and larger real flows.

Run python3 -I COVERAGE_POLYMATROID_FLOW_CHECK.py. Checks explicitly raise on
failure, so they also remain active under -O (ordinary -I is recommended).
"""

from datetime import datetime, timezone
from fractions import Fraction as Q
import importlib.util
from itertools import product
import json
from pathlib import Path
import random
import time

B = Path(__file__).resolve().parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, B / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


flow = load("coverage_flow", "COVERAGE_POLYMATROID_FLOW_BACKEND.py")
generic = load("generic_prices", "POLYMATROID_ORACLE_PRICES.py")
R = random.Random(202610171043)
COUNTS = {"exhaustive_two_job_oracles": 0, "random_small_oracles": 0,
          "generic_price_comparisons": 0, "small_coalition_covers": 0,
          "holding_box_restorations": 0, "restriction_masks": 0,
          "input_rejections": 0, "large_profiles": 0}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def dot(x, y):
    return sum((a * b for a, b in zip(x, y)), Q(0))


def expect_error(fn, exception):
    try:
        fn()
    except exception:
        COUNTS["input_rejections"] += 1
    else:
        raise AssertionError("Invalid input was accepted")


def check_oracle(a, c, rank):
    got = flow.coverage_maximal_minimizer(a, c, rank)
    expected = generic.exhaustive_maximal_sfm(a, c, rank)
    require(got["mask"] == expected, (a, c, rank.feature_masks, rank.weights, got, expected))
    expected_objective = a * rank(expected) - sum(
        (x for j, x in enumerate(c) if expected >> j & 1), Q(0))
    require(got["objective"] == expected_objective, "Oracle objective mismatch")
    require(got["flow"] == sum(c, Q(0)) + expected_objective, "Cut offset mismatch")
    return got


def check_prices(P, c, rank):
    got = flow.coverage_polymatroid_prices(P, c, rank)
    expected = generic.polymatroid_prices(P, c, rank, generic.exhaustive_maximal_sfm)
    for key, value in expected.items():
        require(got[key] == value, (key, got, expected))
    require(dot((P, *c), got["prices"]) <= Q(3, 2) * got["value"], "Funding bound")
    require(all(q >= 0 for q in got["prices"]), "Negative price")
    require(got["flow_stats"]["calls"] == got["maximal_sfm_calls"], "Call count")
    COUNTS["generic_price_comparisons"] += 1
    return got


# An exact tie: source-reachability alone gives the empty set; MAX must be {0}.
tie_rank = flow.WeightedCoverageRank(1, [1], [1])
require(check_oracle(Q(1), (Q(1),), tie_rank)["mask"] == 1, "Maximal tie failed")

# Exhaustive small representation/capacity grid includes empty/zero features,
# duplicate features, loops, zero coefficients, zero capacities and exact ties.
for masks in product(range(4), repeat=2):
    for weights in product((Q(0), Q(1, 2), Q(1)), repeat=2):
        rank = flow.WeightedCoverageRank(2, masks, weights)
        for c in product((Q(0), Q(1, 2), Q(1)), repeat=2):
            for a in (Q(0), Q(1, 2), Q(1), Q(2)):
                check_oracle(a, c, rank)
                COUNTS["exhaustive_two_job_oracles"] += 1

for m in range(9):
    for trial in range(36):
        nf = R.randrange(m + 6)
        rank = flow.WeightedCoverageRank(
            m, [R.randrange(1 << m) for _ in range(nf)],
            [Q(R.randrange(8), R.randrange(1, 6)) for _ in range(nf)])
        c = tuple(Q(R.randrange(8), R.randrange(1, 6)) for _ in range(m))
        a = Q(R.randrange(9), R.randrange(1, 7))
        check_oracle(a, c, rank)
        COUNTS["random_small_oracles"] += 1
        if trial < 18:
            check_prices(Q(R.randrange(10), R.randrange(1, 5)), c, rank)
        # Check a deliberately permuted restriction, not just increasing indices.
        indices = list(range(m))
        R.shuffle(indices)
        indices = indices[:R.randrange(m + 1)]
        restricted = rank.restrict(indices)
        for local in range(1 << len(indices)):
            original = sum(1 << j for k, j in enumerate(indices) if local >> k & 1)
            require(restricted(local) == rank(original), "Restriction rank mismatch")
            COUNTS["restriction_masks"] += 1

# Actual fixed mixed owners: compare all coalitions' production to their payments.
for trial in range(24):
    m, n_owners = 4, 4
    rank = flow.WeightedCoverageRank(
        m, [R.randrange(1 << m) for _ in range(6)],
        [Q(R.randrange(5), R.randrange(1, 4)) for _ in range(6)])
    bundles = [tuple(Q(R.randrange(5), R.randrange(1, 4)) for _ in range(m + 1))
               for _ in range(n_owners)]
    C = tuple(sum((b[j] for b in bundles), Q(0)) for j in range(m + 1))
    result = check_prices(C[0], C[1:], rank)
    payments = [dot(b, result["prices"]) for b in bundles]
    for coalition in range(1 << n_owners):
        bundle = tuple(sum((b[j] for i, b in enumerate(bundles)
                            if coalition >> i & 1), Q(0)) for j in range(m + 1))
        worth = generic.polymatroid_prices(
            bundle[0], bundle[1:], rank, generic.exhaustive_maximal_sfm)["value"]
        pay = sum((y for i, y in enumerate(payments) if coalition >> i & 1), Q(0))
        require(pay >= worth, "Coalition coverage failure")
        COUNTS["small_coalition_covers"] += 1
    # Exact holding-box criterion for a single-coordinate restoration: it checks
    # every low-profile coalition holding vector in its coordinate box at once.
    for j in range(m + 1):
        delta = Q(1, 3)
        high = list(C)
        high[j] += delta
        new = flow.coverage_polymatroid_prices(high[0], high[1:], rank)
        worst_old_loss = sum((C[k] * max(Q(0), result["prices"][k] - new["prices"][k])
                              for k in range(m + 1)), Q(0))
        require(delta * new["prices"][j] >= worst_old_loss, "Holding-box TCWM failure")
        COUNTS["holding_box_restorations"] += 1

expect_error(lambda: flow.WeightedCoverageRank(1, [2], [1]), ValueError)
expect_error(lambda: flow.WeightedCoverageRank(1, [1], [-1]), ValueError)
expect_error(lambda: flow.WeightedCoverageRank(1, [1], [0.5]), TypeError)
expect_error(lambda: flow.WeightedCoverageRank(1, [1], []), ValueError)
expect_error(lambda: tie_rank.restrict([0, 0]), ValueError)
expect_error(lambda: tie_rank.restrict([1]), ValueError)
expect_error(lambda: flow.coverage_maximal_minimizer(-1, [1], tie_rank), ValueError)
expect_error(lambda: flow.coverage_maximal_minimizer(1, [-1], tie_rank), ValueError)
expect_error(lambda: flow.coverage_maximal_minimizer(1, [0.1], tie_rank), TypeError)
expect_error(lambda: flow.coverage_polymatroid_prices(1, [], tie_rank), ValueError)


def stress_case(m, nf, seed):
    rng = random.Random(seed)
    # Three public eligibility edges per job; arbitrary n grows with the input.
    features = [0] * nf
    for j in range(m):
        for f in rng.sample(range(nf), min(3, nf)):
            features[f] |= 1 << j
    rank = flow.WeightedCoverageRank(
        m, features, [Q(rng.randrange(1, 8), rng.randrange(1, 5)) for _ in features])
    c = tuple(Q(rng.randrange(1, 13), rng.randrange(1, 5)) for _ in range(m))
    common = Q(5, 7)
    start = time.perf_counter()
    result = flow.coverage_polymatroid_prices(common, c, rank)
    elapsed = time.perf_counter() - start
    require(result["maximal_sfm_calls"] <= 2 * m - 1, "Oracle count bound")
    total = dot((common, *c), result["prices"])
    require(result["value"] <= total <= Q(3, 2) * result["value"], "Large funding bound")
    # Independent evaluation at z=1 uses one real flow, never subset enumeration.
    at_one = flow.coverage_maximal_minimizer(common, c, rank)
    require(result["value"] == at_one["flow"], "Large value mismatch")
    COUNTS["large_profiles"] += 1
    return {"jobs": m, "features": nf, "public_incidence_edges": 3 * m,
            "value": str(result["value"]), "funding_ratio": str(total / result["value"]),
            "positive_interval_sets": len(result["chain"]),
            "elapsed_seconds_diagnostic": round(elapsed, 6), **result["flow_stats"]}


# These runs use no exponential reference, rank-subset table, or dummy oracle.
large = [stress_case(24, 16, 171024), stress_case(72, 48, 171072),
         stress_case(160, 112, 171160)]
out = {
    "status": "PASS", "completed_utc": datetime.now(timezone.utc).isoformat(),
    "counts": COUNTS, "large_actual_flow_runs": large,
    "arithmetic": "Exact fractions.Fraction for every capacity, cut, breakpoint and price",
    "tie_rule": "Complement of residual reverse reachability from sink: maximal minimum cut",
    "complexity": "At most 2m-1 exact Edmonds-Karp calls; each O(V E^2) arithmetic operations",
    "scope": "Finite implementation evidence. Analytic guarantees are inherited from the accepted identical price rule; no full-OUT or empirical pooling claim.",
}
(B / "COVERAGE_POLYMATROID_FLOW_CHECKS.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
