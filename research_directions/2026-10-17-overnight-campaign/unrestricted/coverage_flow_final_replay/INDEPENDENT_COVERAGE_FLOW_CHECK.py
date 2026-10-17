"""Adversarial exact fixtures and a non-enumerated 137-job analytic reference."""
from pathlib import Path
from fractions import Fraction as Q
import importlib.util
import json

B = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("flow", B / "COVERAGE_POLYMATROID_FLOW_BACKEND.py")
flow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flow)


def direct_rank(mask, masks, weights):
    return sum((w for feature, w in zip(masks, weights) if mask & feature), Q(0))


def fixture(a, capacities, masks, weights):
    m = len(capacities)
    rank = flow.WeightedCoverageRank(m, masks, weights)
    values = [a * direct_rank(S, masks, weights) - sum(
        (c for j, c in enumerate(capacities) if S >> j & 1), Q(0))
        for S in range(1 << m)]
    optimum = min(values)
    expected = 0
    for S, value in enumerate(values):
        if value == optimum:
            expected |= S
    got = flow.coverage_maximal_minimizer(a, capacities, rank)
    assert got["mask"] == expected
    assert got["objective"] == optimum
    assert got["flow"] == optimum + sum(capacities, Q(0))
    return {"jobs": m, "maximal_mask": expected, "flow": str(got["flow"]),
            "augmentations": got["augmentations"]}


# The first augmenting path sends job0 to feature0; the second must reroute
# through the reverse feature0->job0 edge to use feature1. Both jobs are tied
# at the optimum, so recovering only source-reachable vertices would fail.
fixtures = [fixture(Q(1), [Q(1), Q(1)], [0b11, 0b01], [Q(1), Q(1)])]
# Mixed tied and untied components, a zero-capacity loop, duplicate features,
# empty features and zero-weight incidences.
fixtures.append(fixture(Q(3, 7), [Q(3, 7), Q(0), Q(9, 7), Q(0), Q(2, 11)],
                        [0b00011, 0b00100, 0b00100, 0, 0b11111],
                        [Q(1), Q(1), Q(2), Q(900), Q(0)]))
# The finite infinity only needs to exceed sum(c), even when feature-sink
# capacities exceed it by many orders of magnitude.
fixtures.append(fixture(Q(10**9, 3), [Q(1, 10**9), Q(2, 10**9), Q(0)],
                        [0b011, 0b001], [Q(10**6, 7), Q(13, 11)]))
fixtures.append(fixture(Q(0), [Q(0), Q(1, 11), Q(0)],
                        [0b011, 0b110], [Q(7, 13), Q(17, 19)]))
fixtures.append(fixture(Q(5, 3), [Q(0)] * 4, [0b0011, 0b0010, 0],
                        [Q(2), Q(0), Q(3)]))
fixtures.append(fixture(Q(7, 3), [], [0], [Q(1000)]))

# Disjoint noncontiguous coverage groups have an additive min formula. This
# supplies a fully independent price reference without enumerating 2^137 sets.
groups, n_jobs, P = 32, 137, Q(7, 5)
masks, weights, capacities = [], [], [Q(0)] * n_jobs
group_data = []
for g in range(groups):
    jobs = [g + k * groups for k in range(4)]
    mask = sum(1 << j for j in jobs)
    w = Q(g + 1, 7)
    eligible = jobs[1:] if g % 5 == 0 else jobs
    group_capacity = P * w * Q(g + 1, 3)
    for j in eligible:
        capacities[j] = group_capacity / len(eligible)
    masks.extend([mask, mask])
    weights.extend([w / 3, 2 * w / 3])
    group_data.append((jobs, w, group_capacity))
for j in range(128, n_jobs):
    capacities[j] = Q(j - 127, 13) if j != 132 else Q(0)
masks.extend([0, (1 << n_jobs) - 1])
weights.extend([Q(9999), Q(0)])
rank = flow.WeightedCoverageRank(n_jobs, masks, weights)
got = flow.coverage_polymatroid_prices(P, capacities, rank)
expected_prices = [Q(0)] * (n_jobs + 1)
expected_value = Q(0)
for jobs, w, group_capacity in group_data:
    ratio = group_capacity / (P * w)
    probability = ratio / 2 if ratio <= 1 else 1 - 1 / (2 * ratio)
    expected_prices[0] += w * probability
    expected_value += min(P * w, group_capacity)
    for j in jobs:
        if capacities[j]:
            expected_prices[j + 1] = 1 - probability
assert got["prices"] == tuple(expected_prices)
assert got["value"] == expected_value
assert got["maximal_sfm_calls"] == 2 * groups - 1
assert len(got["chain"]) == groups + 1
standalone_checks = 0
for z in [Q(0), Q(1, 3), Q(11, 3), Q(32, 3), Q(97, 9), Q(10**8)]:
    a = P * z
    expected_mask = sum(1 << j for j in range(128, n_jobs))
    expected_minimum = -sum(capacities[128:], Q(0))
    for jobs, w, group_capacity in group_data:
        if a * w <= group_capacity:
            expected_mask |= sum(1 << j for j in jobs)
        expected_minimum += min(Q(0), a * w - group_capacity)
    answer = flow.coverage_maximal_minimizer(a, capacities, rank)
    assert answer["mask"] == expected_mask
    assert answer["objective"] == expected_minimum
    standalone_checks += 1

indices = [136, 1, 64, 0, 128, 33]
restricted = rank.restrict(indices)
for S in range(1 << len(indices)):
    original = sum(1 << j for k, j in enumerate(indices) if S >> k & 1)
    assert restricted(S) == direct_rank(original, masks, weights)

out = {"status": "PASS", "small_adversarial_fixtures": fixtures,
       "large_analytic_reference": {"jobs": n_jobs, "nonempty_positive_features": 64,
         "distinct_groups": groups, "standalone_tie_and_scale_checks": standalone_checks,
         "permuted_restriction_checks": 64, "value": str(got["value"]),
         "chain_length": len(got["chain"]), **got["flow_stats"]},
       "scope": "Exact implementation tests, including reverse-edge rerouting and a 137-job direct additive price reference. No new mechanism, all-profile proof or measured-performance claim."}
(B / "INDEPENDENT_COVERAGE_FLOW_CHECKS.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
