"""Re-verify the stored route2 witnesses and confirm the star normal form.

For each realized row the witness is a list of generator rows; the game is the
lower envelope (exact), normalized, Lmin recomputed exactly with z3, the slack
boundary located, and every packet of Theorem 3 enumerated and matched against
  St(H,Q) = 1_{H u Q} + sum_{i in L\\Q} 1_{H u i} - (m-|Q|) 1_H = 1_N.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F

SCR = "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0, SCR)
import audit
import catalogue
import pack


def nm(n, mask):
    return "".join("abcdefgh"[i] for i in range(n) if mask >> i & 1) or "0"


def star(n, H, Q):
    L = [i for i in range(n) if not H >> i & 1]
    lam = {}
    lam[H | Q] = lam.get(H | Q, 0) + 1
    for i in L:
        if not Q >> i & 1:
            lam[H | (1 << i)] = lam.get(H | (1 << i), 0) + 1
    lam[H] = lam.get(H, 0) - (len(L) - bin(Q).count("1"))
    return {S: c for S, c in lam.items() if c}


def main():
    n = 5
    table, _ = catalogue.index(n)
    cov = json.load(open(f"{SCR}/route2/coverage.json"))
    report = []
    ok = True
    for key, rec in sorted(cov["types"].items(), key=lambda kv: int(kv[0])):
        if rec["status"] != "REALIZED":
            continue
        w = rec["witness"]
        gens = [tuple(F(x) for x in g) for g in w["gens"]]
        Hmask = w["H"]
        v = audit.envelope(n, gens)
        vn, _ = audit.normalize(n, v)
        assert all(vn[1 << i] == 0 for i in range(n))
        assert audit.is_exact(n, vn), "not exact"
        phi = audit.lmin(n, vn)
        assert phi is not None
        assert [str(x) for x in phi] == w["lmin"], (phi, w["lmin"])
        blocks = audit.strata(phi)
        Hs = [sum(1 << i for b in blocks[k + 1:] for i in b)
              for k in range(len(blocks) - 1)]
        assert Hmask in Hs, "H is not a cumulative richer suffix"
        s = sum(phi[i] for i in range(n) if Hmask >> i & 1) - vn[Hmask]
        assert s > 0
        pks, tight = pack.packets(n, vn, phi, Hmask)
        rows_here, stars_here = set(), True
        for pk in pks:
            k = catalogue.canon(n, pk["lam"])
            rows_here |= set(table.get(k, {-1}))
            # star match
            hit = None
            L = [i for i in range(n) if not Hmask >> i & 1]
            for qm in range(1, 1 << len(L)):
                Q = sum(1 << L[t] for t in range(len(L)) if qm >> t & 1)
                if catalogue.canon(n, star(n, Hmask, Q)) == k:
                    hit = Q
                    break
            if hit is None:
                stars_here = False
        good = int(key) in rows_here and stars_here
        ok &= good
        print(f"row {key:>2}: H={nm(n,Hmask)} m={n-bin(Hmask).count('1')} "
              f"phi={[str(x) for x in phi]} s={s}  packets={len(pks)} "
              f"rows={sorted(rows_here)}  all-star={stars_here}  {'OK' if good else 'FAIL'}")
        report.append({"row": int(key), "H": nm(n, Hmask),
                       "phi": [str(x) for x in phi], "slack": str(s),
                       "packets": len(pks), "rows_at_boundary": sorted(rows_here),
                       "all_packets_are_stars": stars_here})
    print("ALL WITNESSES CONFIRM THE STAR NORMAL FORM" if ok else "MISMATCH")
    with open(f"{SCR}/sel/witness_check.json", "w") as fh:
        json.dump({"ok": ok, "witnesses": report}, fh, indent=1)


if __name__ == "__main__":
    main()
