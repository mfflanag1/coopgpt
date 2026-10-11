"""Synthetic colocated energy-limited capacity production; exact small LPs.

H/L each represent complete, interchangeable warm nodes within one local type.
Continuous output is service-capacity value, not a request-level serving claim.
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations
from payments import aggregate, dot, rational

MATRIX = ((Q(1), Q(0)), (Q(0), Q(1)), (Q(2), Q(1)))
PRICES = (Q(6), Q(2))
IDLE_KW = Q(1, 10)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def solve(matrix, rhs):
    """Gaussian elimination, with exact arithmetic and singular-basis detection."""
    n = len(rhs)
    a = [[Q(x) for x in row] + [Q(b)] for row, b in zip(matrix, rhs)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i][j]), None)
        if pivot is None:
            return None
        a[j], a[pivot] = a[pivot], a[j]
        divisor = a[j][j]
        a[j] = [x / divisor for x in a[j]]
        for i in range(n):
            if i != j:
                factor = a[i][j]
                a[i] = [x - factor * y for x, y in zip(a[i], a[j])]
    return tuple(row[-1] for row in a)


def vertices(rows, rhs, dimension):
    points = set()
    for active in combinations(range(len(rows)), dimension):
        x = solve([rows[i] for i in active], [rhs[i] for i in active])
        if x is not None and all(dot(row, x) <= b for row, b in zip(rows, rhs)):
            points.add(x)
    return tuple(sorted(points))


class Technology:
    """Independent primal vertex and dual vertex certificates for fixed A,p."""
    def __init__(self):
        self.matrix, self.prices = MATRIX, PRICES
        dual_rows = [tuple(-MATRIX[e][j] for e in range(3)) for j in range(2)]
        dual_rows += [tuple(-int(e == k) for e in range(3)) for k in range(3)]
        self.dual_vertices = vertices(dual_rows, tuple(-p for p in PRICES)+(0,)*3, 3)
        require(bool(self.dual_vertices), 'No dual vertices')
        self.solution = lru_cache(None)(self._solution)

    def _solution(self, capacity):
        c = tuple(map(rational, capacity))
        if len(c) != 3 or min(c) < 0:
            raise ValueError('Expected three nonnegative capacities')
        points = vertices(MATRIX + ((-1, 0), (0, -1)), c + (0, 0), 2)
        require(bool(points), 'No primal vertices')
        chosen = max(points, key=lambda x: (dot(PRICES, x), x))
        value = dot(PRICES, chosen)
        dual_value = min(dot(w, c) for w in self.dual_vertices)
        require(value == dual_value, 'Independent primal/dual certificate mismatch')
        return value, chosen

    def value(self, capacity):
        return self.solution(tuple(capacity))[0]

    @property
    def value_count(self):
        return self.solution.cache_info().currsize

    def schedule(self, bundles, installed):
        """Allocate pooled runtimes to named nodes; check peak and energy exactly.

        Each reported node-hour is flexible within [0,1]. A one-mode node starts
        at zero and runs for its allocated duration. Installed counts remain
        fixed when checking underreports within the same physical scenario.
        """
        bundles = tuple(tuple(map(rational, b)) for b in bundles)
        c = aggregate(bundles)
        total, plan = self.solution(c)
        if (len(installed) != len(bundles) or any(len(row) != 2 for row in installed)
                or any(not isinstance(n, int) or n < 0 for row in installed for n in row)):
            raise ValueError('Installed node counts must be nonnegative integers per owner/type')
        if any(b[k] > row[k] for b, row in zip(bundles, installed) for k in range(2)):
            raise ValueError('Reported time exceeds installed node-hour capacity')
        intervals = []
        node_type = ('H', 'L')
        kw = (Q(2), Q(1))
        for k in range(2):
            remaining = plan[k]
            for i, b in enumerate(bundles):
                quota = b[k]
                for node in range(installed[i][k]):
                    local_quota = min(Q(1), quota)
                    duration = min(local_quota, remaining)
                    require(0 <= duration <= local_quota <= 1, 'Invalid node duration')
                    quota -= local_quota
                    remaining -= duration
                    intervals.append(dict(owner=i, type=node_type[k], node=node,
                                          start=Q(0), end=duration, reported_quota=local_quota,
                                          incremental_kw=kw[k]))
                require(quota == 0, 'Unallocated reported node time')
            require(remaining == 0, 'Unscheduled production activity')
        actual = tuple(sum((r['end']-r['start'] for r in intervals if r['type']==t), Q(0))
                       for t in node_type)
        require(actual == plan, 'Duration schedule does not realize the LP plan')
        used_energy = sum(((r['end']-r['start'])*r['incremental_kw'] for r in intervals), Q(0))
        require(used_energy <= c[2], 'Energy entitlement exceeded')
        idle_kw = IDLE_KW * sum(sum(row) for row in installed)
        safe_peak = idle_kw + sum(2*row[0]+row[1] for row in installed)
        event_times = sorted({Q(0), Q(1)} | {r['start'] for r in intervals} | {r['end'] for r in intervals})
        peaks = [idle_kw + sum((r['incremental_kw'] for r in intervals
                              if r['start'] <= t < r['end']), Q(0)) for t in event_times]
        peak = max(peaks)
        require(peak <= safe_peak, 'Engineering peak capacity exceeded')
        require(total == dot(PRICES, actual), 'Scheduled value mismatch')
        return dict(installed=installed, intervals=intervals, plan=plan,
                    service_capacity_value=total, incremental_energy_kwh=used_energy,
                    incremental_energy_entitlement_kwh=c[2], warm_baseline_energy_kwh=idle_kw,
                    total_node_energy_kwh=idle_kw+used_energy, peak_node_kw=peak,
                    safe_nonbinding_feeder_kw=safe_peak, capacity_schedule_verified=True,
                    request_level_SLA_verified=False)


def standalone_first(technology, bundles):
    """Feasible standalone plans, then pool only their unused capacity."""
    c = aggregate(bundles)
    solo = tuple(technology.solution(tuple(b)) for b in bundles)
    autarky = sum((answer[0] for answer in solo), Q(0))
    used = tuple(sum((dot(row, answer[1]) for answer in solo), Q(0)) for row in MATRIX)
    remaining = tuple(x-y for x, y in zip(c, used))
    require(min(remaining) >= 0, 'Standalone plans exceed total resources')
    first = autarky + technology.value(remaining)
    joint = technology.value(c)
    require(autarky <= first <= joint, 'Dispatch comparison violates feasibility/order')
    return dict(autarky=autarky, standalone_first=first, joint=joint,
                pooling_gain=joint-autarky, standalone_first_loss=joint-first)
