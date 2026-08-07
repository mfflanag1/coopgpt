"""Abstract enumeration of the systems (P) that Theorem 3 can possibly produce
at n=5, using ONLY structural constraints (no games).

Constraints used, all forced by the statement of Theorem 3 plus two facts:
  * H carries positive slack, so H itself is not phi-tight;
  * every j in H has phi_j > phi_i >= 0 for i in L, so no singleton {j}, j in H,
    is phi-tight (a singleton-normalized game has v({j}) = 0).

Everything else is free: the traces range over all minimal balanced collections
on H and each lift over every set with the prescribed trace.
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction as F

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad")

import catalogue
import pack


def nm(n, mask):
    return "".join("abcdefgh"[i] for i in range(n) if mask >> i & 1) or "0"


def enumerate_packets(n, Hmask):
    """All abstract packet systems with delta>0 for the boundary L|H."""
    full = (1 << n) - 1
    L = [i for i in range(n) if not Hmask >> i & 1]
    Hset = [i for i in range(n) if Hmask >> i & 1]
    out = []
    for coll, beta in pack.min_balanced(Hset):
        options = []
        ok = True
        for R in coll:
            opts = []
            for extra in range(1 << len(L)):
                T = R | sum(1 << L[k] for k in range(len(L)) if extra >> k & 1)
                if T == full:                     # lift must be proper
                    continue
                if T == Hmask:                    # H is slack, never tight
                    continue
                if bin(T).count("1") == 1 and T & Hmask:
                    continue                      # singleton inside H: never tight
                opts.append(T)
            if not opts:
                ok = False
                break
            options.append(opts)
        if not ok:
            continue
        for lift in itertools.product(*options):
            r = {i: sum(beta[R] for R, S in zip(coll, lift) if S >> i & 1) for i in L}
            b = max(r.values())
            u = {i: b - r[i] for i in L}
            delta = 1 + sum(u.values()) - b
            if delta <= 0:
                continue
            lam = {}
            for R, S in zip(coll, lift):
                lam[S] = lam.get(S, F(0)) + beta[R]
            for i in L:
                if u[i]:
                    lam[Hmask | (1 << i)] = lam.get(Hmask | (1 << i), F(0)) + u[i]
            lam[Hmask] = lam.get(Hmask, F(0)) - delta
            lam = {S: c for S, c in lam.items() if c != 0}
            den = 1
            for c in lam.values():
                den = den * c.denominator // _gcd(den, c.denominator)
            lam = {S: int(c * den) for S, c in lam.items()}
            load = [sum(c for S, c in lam.items() if S >> i & 1) for i in range(n)]
            assert len(set(load)) == 1, (lam, load)
            out.append({
                "traces": coll, "lift": lift, "beta": beta, "r": r,
                "b": b, "u": u, "delta": delta, "lam": lam, "rload": load[0],
                "full_trace": len(coll) == 1 and coll[0] == Hmask,
            })
    return out


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def main():
    n = 5
    table, rows = catalogue.index(n)
    results = {}
    for m, h in ((4, 1), (3, 2)):
        Hmask = sum(1 << i for i in range(m, n))
        pks = enumerate_packets(n, Hmask)
        byty = {}
        for p in pks:
            key = catalogue.canon(n, p["lam"])
            byty.setdefault(key, []).append(p)
        print(f"\n=== (m,h) = ({m},{h}),  H = {nm(n, Hmask)} ===")
        print(f"  {len(pks)} packets with delta>0, {len(byty)} permutational types")
        info = []
        for key, grp in sorted(byty.items(), key=lambda kv: -len(kv[1])):
            p = grp[0]
            rowids = table.get(key, [])
            ft = all(q["full_trace"] for q in grp)
            anyft = any(q["full_trace"] for q in grp)
            kind = "FULL-TRACE" if ft else ("mixed" if anyft else "SPLIT/proper-trace")
            print(f"   [{len(grp):3d}] {catalogue.pretty(n, p['lam'])} = {p['rload']}*1_N"
                  f"   rows={rowids or 'NOT CATALOGUED'}   {kind}")
            print(f"        e.g. traces {[nm(n,R) for R in p['traces']]} "
                  f"lift {[nm(n,S) for S in p['lift']]} b={p['b']} delta={p['delta']}")
            info.append({
                "system": catalogue.pretty(n, p["lam"]),
                "rows": rowids, "count": len(grp), "kind": kind,
                "b": str(p["b"]), "delta": str(p["delta"]),
            })
        results[f"m{m}h{h}"] = info
    with open("/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/sel/enum_packets.json", "w") as fh:
        json.dump(results, fh, indent=1)


if __name__ == "__main__":
    main()
