#!/usr/bin/env python3
"""Independent exact replay: no imported pilot code/data and no dependencies."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json


def triples(n):
    return tuple(sorted({tuple(sorted((a, b, a ^ b)))
                         for a in range(1, n + 1)
                         for b in range(a + 1, n + 1)}))


QEDGES = triples(7)


def oracle(mask):
    """Explicit independently checked Fano primal/dual witnesses."""
    active = {q for q in range(1, 8) if mask & (1 << (q - 1))}
    es = [e for e in QEDGES if set(e) <= active]
    p = {q: F(q not in active) for q in range(1, 8)}
    x = {e: F(0) for e in QEDGES}
    common = set.intersection(*(set(e) for e in es)) if es else set()
    if not es:
        value = F(0)
    elif common:
        p[min(common)] = F(1)
        x[es[0]] = F(1)
        value = F(1)
    elif len(active) == 6:
        for q in active:
            p[q] = F(1, 3)
        for e in es:
            x[e] = F(1, 2)
        value = F(2)
    elif len(active) == 7:
        p = {q: F(1, 3) for q in active}
        x = {e: F(1, 3) for e in es}
        value = F(7, 3)
    else:
        raise AssertionError((mask, active, es))
    assert all(sum(p[q] for q in e) >= 1 for e in QEDGES)
    assert all(sum(x[e] for e in QEDGES if q in e) <= (q in active)
               for q in range(1, 8))
    assert sum(x.values()) == sum(p[q] for q in active) == value
    return value, x, p, es, common


ORACLES = {S: oracle(S) for S in range(128)}
IDEAL = tuple(S for S in ORACLES if ORACLES[S][0] <= 1)


def qsequence(R, s, M):
    q = {1: F(1, 3)}
    for m in range(2, M + 1):
        L = min(s - R, 2 * R * (m - 1))
        q[m] = F(L, R + L) * q[m - 1]
    return q


def embedding(x, R):
    # Involutive linear shear makes W non-coordinate when R>1.
    return x ^ (R if R > 1 and x & 1 else 0)


def rule(S, R, s):
    value, _, p, es, common = ORACLES[S]
    y = {q: F(0) for q in range(1, 8)}
    if s < R:
        for q in range(1, 8):
            if S & (1 << (q - 1)):
                y[q] = p[q]
        factor = F(1)
    else:
        peak = max(1, (s + R - 1) // R)
        seq = qsequence(R, s, max(peak + 2, 3))
        factor = max(1 + 2 * (m - 1) * qm for m, qm in seq.items())
        if value:
            m, cap = len(es), min(common)
            for e in es:
                for q in e:
                    y[q] = seq[m]
            y[cap] = 1 - 2 * seq[m]
    out = {u: F(0) for u in range(1, 8 * R)}
    for q in range(1, 8):
        for w in range(R):
            out[embedding(q * R + w, R)] = y[q]
    return out, factor


def apply_columns(q, cols):
    out = 0
    for k in range(3):
        if q & (1 << k):
            out ^= cols[k]
    return out


class DSU:
    def __init__(self, n):
        self.p = list(range(n + 1))
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x
    def union(self, x, y):
        self.p[self.find(x)] = self.find(y)


def main():
    counts = {k: 0 for k in ("projection_primal_dual_pairs", "rule_funding_profiles",
              "actual_supported_triple_covers", "all_coalition_OUT_endpoints",
              "nontrivial_OUT_endpoints", "stabilizer_actions",
              "scaled_lower_certificates", "peak_checks")}
    symmetry = []
    gl = [cols for cols in product(range(1, 8), repeat=3)
          if len({apply_columns(q, cols) for q in range(8)}) == 8]
    assert len(gl) == 168
    for R in (1, 2, 4, 8):
        n, edges = 8 * R - 1, triples(8 * R - 1)
        fibers = {q: {embedding(q * R + w, R) for w in range(R)}
                  for q in range(1, 8)}
        W = {embedding(w, R) for w in range(1, R)}
        assert len(W) == R - 1
        for S, (value, qx, qp, _, _) in ORACLES.items():
            active = set().union(*(fibers[q] for q in range(1, 8)
                                  if S & (1 << (q - 1))))
            lifted = {e: F(0) for e in edges}
            for (a, b, c), intensity in qx.items():
                for u in fibers[a]:
                    for v in fibers[b]:
                        lifted[tuple(sorted((u, v, u ^ v)))] += intensity / R
            price = {u: (F(1) if u in W else qp[embedding(u, R) // R])
                     for u in range(1, n + 1)}
            loads = {u: F(0) for u in range(1, n + 1)}
            for e, intensity in lifted.items():
                for u in e:
                    loads[u] += intensity
            assert all(loads[u] <= (u in active) for u in loads)
            assert all(sum(price[u] for u in e) >= 1 for e in edges)
            assert sum(lifted.values()) == sum(price[u] for u in active) == R * value
            counts["projection_primal_dual_pairs"] += 1

        for s in range(1, 3 * R + 2):
            ys = {}
            for S in IDEAL:
                y, factor = rule(S, R, s)
                ys[S] = y
                assert min(y.values()) >= 0
                assert sum(y.values()) <= factor * R * ORACLES[S][0]
                counts["rule_funding_profiles"] += 1
                active = {u for u in range(1, n + 1)
                          if embedding(u, R) // R and
                          S & (1 << (embedding(u, R) // R - 1))}
                for e in edges:
                    if set(e) <= active:
                        assert sum(y[u] for u in e) == 1
                        counts["actual_supported_triple_covers"] += 1
            for T in IDEAL:
                S = T
                while True:
                    D = T ^ S
                    changed = set().union(*(fibers[q] for q in range(1, 8)
                                           if D & (1 << (q - 1))))
                    if len(changed) <= s:
                        deltas = {u: ys[T][u] - ys[S][u] for u in range(1, n + 1)}
                        forced = sum((deltas[u] for u in changed), F(0))
                        negative = sorted(deltas[u] for u in deltas
                                          if u not in changed and deltas[u] < 0)
                        worst = forced + sum(negative[:s - len(changed)], F(0))
                        assert worst >= R * ORACLES[D][0]
                        counts["all_coalition_OUT_endpoints"] += 1
                        counts["nontrivial_OUT_endpoints"] += bool(D)
                    if S == 0:
                        break
                    S = (S - 1) & T

        for stage, S, target_q in ((1, {1, 2, 3, 4}, {1, 2, 3}),
                                   (2, {1, 2, 3, 4, 5}, {2, 3, 4, 5})):
            stabilizers = [A for A in gl if {apply_columns(q, A) for q in S} == S]
            assert len(stabilizers) == (6 if stage == 1 else 8)
            dsu = DSU(n)
            action_count = 0
            for A in stabilizers:
                for Tcols in product(range(R), repeat=3):
                    images = {}
                    for u in range(1, n + 1):
                        raw = embedding(u, R)
                        q, w = divmod(raw, R)
                        shift = apply_columns(q, Tcols)
                        image = embedding(apply_columns(q, A) * R + (w ^ shift), R)
                        images[u] = image
                        dsu.union(u, image)
                    assert len(set(images.values())) == n
                    assert {images[u] for u in W} == W
                    old = set().union(*(fibers[q] for q in S))
                    assert {images[u] for u in old} == old
                    action_count += 1
            target = set().union(*(fibers[q] for q in target_q))
            assert len({dsu.find(u) for u in target}) == 1
            if stage == 2:
                assert len({dsu.find(u) for u in fibers[1]}) == 1
                assert dsu.find(next(iter(target))) != dsu.find(next(iter(fibers[1])))
            counts["stabilizer_actions"] += action_count
            symmetry.append({"R": R, "stage": stage, "quotient_stabilizers": len(stabilizers),
                             "actions": action_count, "target_orbit_size": len(target)})

        for s in range(R, 65):
            peak = (s + R - 1) // R
            seq = qsequence(R, s, max(peak + 3, 4))
            funding = {m: 1 + 2 * (m - 1) * qm for m, qm in seq.items()}
            if s == R:
                assert set(funding.values()) == {F(1)}
            else:
                maxima = [m for m in funding if funding[m] == max(funding.values())]
                expect = [peak, peak + 1] if s % R == 0 else [peak]
                assert maxima == expect
            counts["peak_checks"] += 1
            for M in range(1, 25):
                seq = qsequence(R, s, M)
                coeff = {m: F(0) for m in range(1, M + 1)}
                # Budget divided by R plus one actual-triple coverage.
                coeff[M] -= 2 * (M - 1)
                residual = F(2 * (M - 1))
                nonnegative_restorer_weights = []
                for m in range(M, 1, -1):
                    L = min(s - R, 2 * R * (m - 1))
                    weight = residual / (R + L)
                    assert weight >= 0
                    coeff[m] += weight * (R + L)
                    coeff[m - 1] -= weight * L
                    # The -weight on each old restoring owner's payment is
                    # canceled by that owner's genuine nonnegative-payment row.
                    nonnegative_restorer_weights.append(weight)
                    residual = weight * L
                seed_weight = residual / 3
                coeff[1] += 3 * seed_weight
                assert all(c == 0 for c in coeff.values())
                rhs = 1 + seed_weight
                assert rhs == 1 + 2 * (M - 1) * seq[M]
                counts["scaled_lower_certificates"] += 1

    result = {"status": "PASS", "no_external_inputs": True,
              "quotient": "Fano; exact independently constructed primal/dual witnesses",
              "R": [1, 2, 4, 8], "noncoordinate_W": "R>1 uses an involutive linear shear",
              "quotient_profiles": len(ORACLES), "ideal_profiles": len(IDEAL),
              "s_ranges_for_endpoint_checks": "1..3R+1, including s<R",
              "counts": counts, "symmetry": symmetry,
              "scope": "Complete binary fibers only; no partial-fiber or all-real upper claim."}
    target = Path(__file__).with_suffix('.json')
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
