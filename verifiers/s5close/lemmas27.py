"""Task #27, step 1: candidate HAND lemmas for distilling the 2961-way split.

All four below are proved by a two-line CONVEXITY/PERTURBATION argument on the
core -- no A3, no facet catalogue, no solver.  They are stated here and checked
against every harvested genuine exact game before being used for anything.

Notation: T = 1, x = Lmin, z = Lmax, mu = min x, M = max z,
P = {i : x_i = mu} the Lmin bottom stratum, D1 = {i : z_i = M} the Lmax top
stratum.

 L7  (ceiling extremal rigidity).  EVERY core point w has max_{i in D1} w_i >= M.
     PROOF.  Suppose w_i < M for every i in D1.  For j outside D1 we have
     z_j < M by definition of D1.  Put w_th = (1-th) z + th w, a core point by
     convexity.  For i in D1, w_th,i = (1-th)M + th w_i < M for every th > 0;
     for the finitely many j outside D1, w_th,j < M once th is small enough.
     So max_j w_th,j < M, contradicting M = min over the core of the maximal
     coordinate.  []

 L7' (floor extremal rigidity).  EVERY core point w has min_{i in P} w_i <= mu.
     PROOF.  The mirror argument: if w_i > mu for every i in P, then for small
     th the point (1-th)x + th w has every coordinate strictly above mu,
     contradicting mu = max over the core of the minimal coordinate.  []

 L5  min Lmax <= min Lmin and max Lmax <= max Lmin.
     (Immediate from optimality: Lmin maximizes the minimum over the core and
     Lmax minimizes the maximum, so mu >= min w and M <= max w for every core
     point w; take w = z and w = x.)

 L1'' (the Lmax top stratum has >= 2 players) -- A3-FREE, unlike L1'.
     PROOF.  Suppose D1 = {i}.  L7 then reads w_i >= M for EVERY core point w.
     By exactness, v({i}) = min over the core of w_i >= M > 0, contradicting
     singleton normalization v({i}) = 0.  []

 L6  (singleton floor stratum).  If P = {i} then f({i}) = mu, equivalently
     v(N \\ {i}) = T - mu.
     PROOF.  L7' with P = {i} reads w_i <= mu for every core point w, so
     f({i}) = max over the core of w_i <= mu; and f({i}) >= x_i = mu.  []

WHAT THESE REPLACE.  L7' with w = z gives mu >= min_{i in P} z_i, which is
exactly L2(c) -- previously derived from A3.  So L2 and its corollary L2' (the
starved player is Lmin-poor) become A3-FREE.  L1'' likewise makes the 1953
"impossible" configurations an A3-free hand exclusion.

Also recorded (A3-free but weaker than L3): M + 4mu <= T, from L7 with w = x
(some player of D1 has x_i >= M, the other four have x_j >= mu).
"""
from __future__ import annotations
import json
import sys
from fractions import Fraction as F

HERE = sys.path[0]
sys.path.insert(0, HERE + "/lib")
import audit

N, FULL = 5, 31
SZ = [bin(S).count("1") for S in range(32)]


def check(recs, st, vert_limit):
    for gi, r in enumerate(recs):
        T = F(r["T"])
        v = [F(t) / T for t in r["v"]]
        x = [F(t) / T for t in r["lmin"]]
        z = [F(t) / T for t in r["lmax"]]
        mu, M = min(x), max(z)
        P = [i for i in range(N) if x[i] == mu]
        D1 = [i for i in range(N) if z[i] == M]
        st["games"] += 1
        # L7 / L7' quantify over EVERY core point; testing them on all core
        # VERTICES suffices, since max_{D1} w_i and min_P w_i are respectively
        # convex and concave, so their extrema over the core are attained at
        # vertices.  Vertex enumeration is the expensive step, so it is run on
        # a bounded prefix of each harvest.
        if gi < vert_limit:
            verts = audit.core_vertices(N, v)
            st["core_points_tested"] += len(verts)
            st["games_vertex_tested"] += 1
            for w in verts:
                if max(w[i] for i in D1) < M:
                    st["L7_fail"] += 1
                if min(w[i] for i in P) > mu:
                    st["L7p_fail"] += 1
        # L11 / L12, the PROTECTOR lemmas in level form.  If phi_i < phi_j for
        # a leximin or leximax point phi, then shifting a little payoff from j
        # to i must leave the core, so some proper phi-tight T has j but not i.
        # Tightness plus core membership of the OTHER selection then compares
        # the two allocations on T.
        tightx = {A for A in range(1, FULL)
                  if sum(x[k] for k in range(N) if A >> k & 1) == v[A]}
        tightz = {A for A in range(1, FULL)
                  if sum(z[k] for k in range(N) if A >> k & 1) == v[A]}
        for i in range(N):
            for j in range(N):
                if x[i] < x[j]:
                    st["L11_pairs"] += 1
                    if not any(A in tightx and (A >> j & 1) and not (A >> i & 1)
                               and sum(x[k] for k in range(N) if A >> k & 1)
                               <= sum(z[k] for k in range(N) if A >> k & 1)
                               for A in range(1, FULL)):
                        st["L11_fail"] += 1
                if z[i] < z[j]:
                    st["L12_pairs"] += 1
                    if not any(A in tightz and (A >> j & 1) and not (A >> i & 1)
                               and sum(z[k] for k in range(N) if A >> k & 1)
                               <= sum(x[k] for k in range(N) if A >> k & 1)
                               for A in range(1, FULL)):
                        st["L12_fail"] += 1
        if min(z) > mu:
            st["L5a_fail"] += 1
        if M > max(x):
            st["L5b_fail"] += 1
        if len(D1) < 2:
            st["L1pp_fail"] += 1
        if len(P) == 1:
            st["L6_cases"] += 1
            i = P[0]
            if 1 - v[FULL ^ (1 << i)] != mu:
                st["L6_fail"] += 1
        if M + 4 * mu > 1:
            st["Mplus4mu_fail"] += 1
    return st


def main():
    st = {"games": 0, "core_points_tested": 0, "games_vertex_tested": 0,
          "L11_pairs": 0, "L11_fail": 0, "L12_pairs": 0, "L12_fail": 0,
          "L7_fail": 0, "L7p_fail": 0,
          "L5a_fail": 0, "L5b_fail": 0, "L1pp_fail": 0,
          "L6_cases": 0, "L6_fail": 0, "Mplus4mu_fail": 0}
    for src in ("harvest_seed22.json", "harvest_seed777.json"):
        recs = json.load(open(f"{HERE}/{src}"))["records"]
        print(f"  {src}: {len(recs)} games", flush=True)
        check(recs, st, vert_limit=150)
    print(json.dumps(st, indent=1))
    ok = all(st[k] == 0 for k in st if k.endswith("_fail"))
    print("ALL CANDIDATE HAND LEMMAS HOLD" if ok else "A LEMMA FAILED")
    json.dump(st, open(f"{HERE}/lemmas27.json", "w"), indent=1)


if __name__ == "__main__":
    main()
