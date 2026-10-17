"""Exact rational min-cut backend for public weighted-coverage polymatroids.

Only the Python standard library is used. This is established max-flow machinery,
specialized to the accepted price evaluator; it does not prove new incentives.
Inputs must be int/Fraction. Floating values and negative capacities are rejected.
"""

from collections import deque
from fractions import Fraction
import importlib.util
from pathlib import Path

Q = Fraction


def _q(value):
    if not isinstance(value, (int, Q)) or isinstance(value, bool):
        raise TypeError("Use exact int/Fraction values")
    return Q(value)


class WeightedCoverageRank:
    """r(S) = sum(weight[f] for f if S & feature_masks[f]).

    A mask's bit j denotes the ORIGINAL job j. Empty features, zero weights,
    repeated feature masks, and jobs incident to no positive-weight feature are
    allowed. Such jobs are public loops. Masks and weights are stored as tuples.
    """

    __slots__ = ("n_jobs", "feature_masks", "weights")

    def __init__(self, n_jobs, feature_masks, weights):
        if not isinstance(n_jobs, int) or isinstance(n_jobs, bool) or n_jobs < 0:
            raise ValueError("n_jobs must be a nonnegative integer")
        masks = tuple(feature_masks)
        ww = tuple(_q(w) for w in weights)
        if len(masks) != len(ww):
            raise ValueError("One weight is required per feature mask")
        full = (1 << n_jobs) - 1
        if any(not isinstance(mask, int) or isinstance(mask, bool)
               or mask < 0 or mask & ~full for mask in masks):
            raise ValueError("Feature mask outside the job universe")
        if any(w < 0 for w in ww):
            raise ValueError("Coverage feature weights must be nonnegative")
        self.n_jobs = n_jobs
        self.feature_masks = masks
        self.weights = ww

    def __call__(self, mask):
        if not isinstance(mask, int) or mask < 0 or mask >> self.n_jobs:
            raise ValueError("Rank query outside the job universe")
        return sum((w for feature, w in zip(self.feature_masks, self.weights)
                    if mask & feature), Q(0))

    def restrict(self, job_indices):
        """Return the rank on LOCAL indices in the supplied original-index order."""
        indices = tuple(job_indices)
        if len(set(indices)) != len(indices) or any(
                not isinstance(j, int) or isinstance(j, bool)
                or not 0 <= j < self.n_jobs for j in indices):
            raise ValueError("Restriction indices must be distinct original jobs")
        masks = tuple(sum(1 << local for local, original in enumerate(indices)
                          if feature >> original & 1)
                      for feature in self.feature_masks)
        return WeightedCoverageRank(len(indices), masks, self.weights)


def coverage_maximal_minimizer(coefficient, capacities, coverage):
    """Solve min_S coefficient*r(S)-sum_{j in S} capacities[j] exactly.

    Return a dictionary including the inclusion-MAXIMAL minimizer bit mask,
    objective, max-flow value, and operation counts. `coverage` and capacities
    use the SAME local job indices. The coefficient and all capacities must be
    nonnegative. This routine handles zeros without an active-face restriction.

    Network: source -> job c_j; job -> incident feature sum(c)+1;
    feature -> sink coefficient*w_f. Maximal source side is the complement of
    vertices with a positive-residual path TO the sink after maximum flow.
    """
    if not isinstance(coverage, WeightedCoverageRank):
        raise TypeError("coverage must be a WeightedCoverageRank")
    a = _q(coefficient)
    cc = tuple(_q(c) for c in capacities)
    if len(cc) != coverage.n_jobs:
        raise ValueError("Capacity count must match local job count")
    if a < 0 or any(c < 0 for c in cc):
        raise ValueError("Nonnegative coefficient and capacities required")

    # Empty or zero-weight features have no effect on any rank or objective.
    features = [(mask, w) for mask, w in zip(coverage.feature_masks, coverage.weights)
                if mask and w]
    m = len(cc)
    source, sink = 0, 1 + m + len(features)
    residual = [dict() for _ in range(sink + 1)]
    original_edges = []

    def add_edge(u, v, capacity):
        if not capacity:
            return
        residual[u][v] = residual[u].get(v, Q(0)) + capacity
        residual[v].setdefault(u, Q(0))
        original_edges.append((u, v, capacity))

    total_capacity = sum(cc, Q(0))
    finite_infinity = total_capacity + 1
    for j, c in enumerate(cc):
        add_edge(source, 1 + j, c)
    for f, (mask, w) in enumerate(features):
        feature_vertex = 1 + m + f
        add_edge(feature_vertex, sink, a * w)
        for j in range(m):
            if mask >> j & 1:
                add_edge(1 + j, feature_vertex, finite_infinity)

    flow = Q(0)
    augmentations = bfs_calls = 0
    while True:
        bfs_calls += 1
        parent = [-1] * len(residual)
        parent[source] = source
        queue = deque([source])
        while queue and parent[sink] == -1:
            u = queue.popleft()
            for v, capacity in residual[u].items():
                if capacity > 0 and parent[v] == -1:
                    parent[v] = u
                    queue.append(v)
                    if v == sink:
                        break
        if parent[sink] == -1:
            break
        v = sink
        bottleneck = None
        while v != source:
            u = parent[v]
            cap = residual[u][v]
            bottleneck = cap if bottleneck is None else min(bottleneck, cap)
            v = u
        if bottleneck is None or bottleneck <= 0:
            raise AssertionError("Invalid augmenting path")
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= bottleneck
            residual[v][u] += bottleneck
            v = u
        flow += bottleneck
        augmentations += 1

    # Reverse reachability, not source reachability: ties require MAX source side.
    reaches_sink = {sink}
    queue = deque([sink])
    while queue:
        v = queue.popleft()
        for u in residual[v]:
            if residual[u][v] > 0 and u not in reaches_sink:
                reaches_sink.add(u)
                queue.append(u)
    if source in reaches_sink:
        raise AssertionError("Augmenting path remains")
    source_side = set(range(len(residual))) - reaches_sink
    mask = sum(1 << j for j in range(m) if 1 + j in source_side)
    cut_value = sum((capacity for u, v, capacity in original_edges
                     if u in source_side and v not in source_side), Q(0))
    objective = a * coverage(mask) - sum(
        (c for j, c in enumerate(cc) if mask >> j & 1), Q(0))
    if cut_value != flow or objective + total_capacity != flow:
        raise AssertionError("Flow, cut, and coverage objective disagree")
    return {
        "mask": mask, "objective": objective, "flow": flow,
        "vertices": len(residual), "edges": len(original_edges),
        "augmentations": augmentations, "bfs_calls": bfs_calls,
        "maximal_source_side": tuple(sorted(source_side)),
    }


def _load_generic_evaluator():
    filename = Path(__file__).with_name("POLYMATROID_ORACLE_PRICES.py")
    spec = importlib.util.spec_from_file_location("_coverage_generic_prices", filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def coverage_polymatroid_prices(common, capacities, coverage):
    """Exact public-coverage specialization of polymatroid_prices.

    Inputs use original job indices. Restricting zero-capacity jobs is performed
    in the same order as the existing evaluator; public loops stay in the local
    universe. The returned prices use original indices (common, job0, job1,...).
    Additional `flow_stats` contain actual network counts, not oracle estimates.
    No subset enumeration is used here or in the flow backend.
    """
    if not isinstance(coverage, WeightedCoverageRank):
        raise TypeError("coverage must be a WeightedCoverageRank")
    P = _q(common)
    cc = tuple(_q(c) for c in capacities)
    if len(cc) != coverage.n_jobs:
        raise ValueError("Capacity count must match original job count")
    if P < 0 or any(c < 0 for c in cc):
        raise ValueError("Nonnegative capacities required")
    active = tuple(j for j, c in enumerate(cc) if c > 0)
    local_rank = coverage.restrict(active)
    stats = {"calls": 0, "augmentations": 0, "bfs_calls": 0,
             "maximum_vertices": 0, "maximum_edges": 0}

    def maximal_sfm(a, local_capacities, rank_callback):
        # This closure binds the same explicit rank as the generic evaluator.
        # The full/empty/mask checks detect mapping mistakes; they do not purport
        # to certify an arbitrary black-box rank as a weighted coverage rank.
        expected_capacities = tuple(cc[j] for j in active)
        if tuple(local_capacities) != expected_capacities:
            raise AssertionError("Generic evaluator active-index mapping changed")
        answer = coverage_maximal_minimizer(a, local_capacities, local_rank)
        for mask in (0, (1 << len(active)) - 1, answer["mask"]):
            if rank_callback(mask) != local_rank(mask):
                raise AssertionError("Generic evaluator rank mapping changed")
        stats["calls"] += 1
        for key in ("augmentations", "bfs_calls"):
            stats[key] += answer[key]
        for key in ("vertices", "edges"):
            name = "maximum_" + key
            stats[name] = max(stats[name], answer[key])
        return answer["mask"]

    generic = _load_generic_evaluator()
    result = generic.polymatroid_prices(P, cc, coverage, maximal_sfm)
    if stats["calls"] != result["maximal_sfm_calls"]:
        raise AssertionError("Flow call count disagrees with evaluator")
    return {**result, "flow_stats": stats}
