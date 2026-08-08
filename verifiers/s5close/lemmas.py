"""Verification of the four structural lemmas this task proves, against every
harvested genuine exact 5-player game.

These are PROOFS (see PROOF.txt sections L1-L4); the run here is the positive
control that the statements are not vacuous and that no arithmetic slip was
made in stating them.

 L1 (ceiling anchor localization).  nu = M is attained only at coalitions of
    size >= 2 lying inside the Lmax TOP stratum.  Corollary: the Lmax top
    stratum has at least two players, so every Lmax stratum composition
    ending in 1 is impossible.
 L2 (floor anchor localization).  lambda = mu is attained only at coalitions
    lying inside the Lmin BOTTOM stratum P, and every such coalition obeys
    z(S) <= mu|S|.  Corollary: mu >= min_{i in P} Lmax_i, which sharpens
    cor:floorceiling (min over ALL i) to a min over the Lmin-poor stratum.
 L3.  2M + 3mu <= T.
 L4.  ratio <= 2|Abar|(M - mu) where Abar = {i : Lmax_i > Lmin_i}.
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


def main():
    d = json.load(open(f"{HERE}/harvest.json"))
    recs = d["records"]
    st = {k: 0 for k in ("games", "L1_anchor_off_top", "L1_anchor_small",
                         "L1_top_singleton", "L2_anchor_off_bottom",
                         "L2_z_violation", "L2_corollary", "L3", "L4",
                         "nu_ne_M", "lambda_ne_mu")}
    for r in recs:
        v = [F(t) for t in r["v"]]
        T = F(r["T"])
        x = [F(t) for t in r["lmin"]]
        z = [F(t) for t in r["lmax"]]
        mu, M = min(x), max(z)
        st["games"] += 1
        nu = max(F(v[S], SZ[S]) for S in range(1, FULL + 1))
        lam = min(F(T - v[FULL ^ S], SZ[S]) for S in range(1, FULL + 1))
        if nu != M:
            st["nu_ne_M"] += 1
        if lam != mu:
            st["lambda_ne_mu"] += 1
        top = [i for i in range(N) if z[i] == M]
        bot = [i for i in range(N) if x[i] == mu]
        if len(top) < 2:
            st["L1_top_singleton"] += 1
        for S in range(1, FULL + 1):
            if F(v[S], SZ[S]) == nu:                      # a ceiling anchor
                if any(z[i] != M for i in range(N) if S >> i & 1):
                    st["L1_anchor_off_top"] += 1
                if SZ[S] < 2:
                    st["L1_anchor_small"] += 1
            if F(T - v[FULL ^ S], SZ[S]) == lam:          # a floor anchor
                if any(x[i] != mu for i in range(N) if S >> i & 1):
                    st["L2_anchor_off_bottom"] += 1
                if sum(z[i] for i in range(N) if S >> i & 1) > mu * SZ[S]:
                    st["L2_z_violation"] += 1
        if mu < min(z[i] for i in bot):
            st["L2_corollary"] += 1
        if 2 * M + 3 * mu > T:
            st["L3"] += 1
        ab = [i for i in range(N) if z[i] > x[i]]
        ratio = sum(abs(x[i] - z[i]) for i in range(N))
        if ratio > 2 * len(ab) * (M - mu):
            st["L4"] += 1
    print(json.dumps(st, indent=1))
    ok = all(st[k] == 0 for k in st if k != "games")
    print("ALL LEMMAS HOLD ON EVERY HARVESTED GAME" if ok else "VIOLATION FOUND")
    json.dump(st, open(f"{HERE}/lemmas.json", "w"), indent=1)


if __name__ == "__main__":
    main()
