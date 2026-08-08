"""d9: audit the fresh n=5 exact-domain corpus produced by d7.

Every record was already certified when it was found (v and v' exact on all
proper coalitions by exact z3 optimisation; phi and phi' by two independent
leximin algorithms with a uniqueness proof).  Here they are re-audited from the
generator rows and tabulated against C-C, the two auxiliary regularities, and
the structural facts the proof uses.

This corpus comes from a generator region the earlier campaign did not use
(five-player BT-shaped envelopes with small totals, and bumped coalitions with
two outsiders), so it is independent evidence, not more of the same.
"""
import sys, json, glob
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L

n = 5
FULL = 31
recs = []
for p in glob.glob("n5_hits_*.json"):
    recs += json.load(open(p))["hits"]
print("records:", len(recs))

t = dict(n=0, left=0, right=0, both=0, S_eq_Hstar=0, outsiders_ge2=0,
         frozen_above=0, outsider_below=0, propD=0, lemmaC=0,
         S_tight_in_v2=0, W_eq_Hstar=0, thmA=0, distinct_games=set(),
         distinct_S=set(), Hstar_sizes={}, reaudit_fail=0)
for r in recs:
    rows = [tuple(F(q) for q in row) for row in r["rows"]]
    v = L.envelope(n, rows)
    phi = L.lmin_staged(n, v)
    S = r["Smask"]
    al = F(r["alpha"])
    w = L.bumped(v, S, al)
    phi2 = L.lmin_staged(n, w)
    if [str(q) for q in phi] != r["phi"] or [str(q) for q in phi2] != r["phi2"]:
        t["reaudit_fail"] += 1
        continue
    H, js = L.hstar(n, v, phi)
    Wl = [i for i in L.members(n, S) if phi2[i] < phi[i]]
    Wm = sum(1 << i for i in Wl)
    D = [phi2[i] - phi[i] for i in range(n)]
    losers = [i for i in range(n) if D[i] < 0]
    lam = max(phi[i] for i in losers)
    ins = [phi[i] for i in Wl]
    outs = [phi[i] for i in losers if not S >> i & 1]
    t["n"] += 1
    t["distinct_games"].add(tuple(map(tuple, r["rows"])))
    t["distinct_S"].add((tuple(map(tuple, r["rows"])), S))
    t["left"] += (Wm & ~H) == 0
    t["right"] += (H & ~S) == 0
    t["both"] += ((Wm & ~H) == 0 and (H & ~S) == 0)
    t["S_eq_Hstar"] += (S == H)
    t["W_eq_Hstar"] += (Wm == H)
    t["outsiders_ge2"] += bin(FULL ^ S).count("1") >= 2
    t["frozen_above"] += all(D[i] == 0 for i in range(n) if phi[i] > lam)
    t["outsider_below"] += (not outs) or (max(outs) < min(ins))
    t["propD"] += all(L.xsum(D, n, T) >= 0 for T in L.masks(n)
                      if L.xsum(phi, n, T) == v[T])
    t["lemmaC"] += all(L.xsum(D, n, T) <= 0 for T in L.masks(n)
                       if T != S and L.xsum(phi2, n, T) == w[T])
    t["S_tight_in_v2"] += L.xsum(phi2, n, S) == w[S]
    t["thmA"] += (sum(phi[i] - phi2[i] for i in Wl) <= L.slack(n, v, phi, Wm))
    k = bin(H).count("1")
    t["Hstar_sizes"][k] = t["Hstar_sizes"].get(k, 0) + 1

t["distinct_games"] = len(t["distinct_games"])
t["distinct_S"] = len(t["distinct_S"])
print(json.dumps(t, indent=1))
print("\nC-C both halves: %d/%d" % (t["both"], t["n"]))
