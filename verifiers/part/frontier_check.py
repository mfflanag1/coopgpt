"""Confirms the diagnosis in PROOF_M3.txt of WHERE the m=3 proof breaks.

The claim: Lemma 3 ("no phi-tight T contains H and omits the unique member a of
P") is the first step to fail as m grows, because its proof needs |Q \ T| <= 1.
At a realizable PART(1,3) configuration (m = 4, |Q| = 3) there must therefore
exist a phi-tight coalition containing H and omitting a -- otherwise the whole
m=3 argument would carry over verbatim and contradict realizability.
"""
import sys, json, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L

data = json.load(open("witness_n6.json"))
for key in ("n6m4split(1,3)", "n6m4split(3,1)"):
    wit = data["found"][key]
    n = wit["n"]
    gens = [tuple(F(x) for x in g) for g in wit["gens"]]
    w, _ = L.normalize(n, L.envelope(n, gens))
    phi = L.lmin(n, w)
    tight = L.tight_family(n, w, phi)
    H, S1, S2 = wit["Hmask"], wit["S1mask"], wit["Hmask"] ^ 0  # recompute below
    S2 = wit["S2mask"]
    p, q = wit["split"]
    # a = the unique poorer member of the singleton side
    single = S1 if p == 1 else S2
    other = S2 if p == 1 else S1
    a = [i for i in L.bits(n, single) if not (H >> i & 1)][0]
    Q = [i for i in L.bits(n, other) if not (H >> i & 1)]
    f_ = [i for i in L.bits(n, single) if H >> i & 1][0]
    viol = [T for T in tight if (T & H) == H and not (T >> a & 1)]
    print(f"{key}: phi={[str(x) for x in phi]}  a={L.LETTERS[a]} "
          f"Q={[L.LETTERS[i] for i in Q]} f={L.LETTERS[f_]}")
    print(f"   tight sets containing H and omitting a: "
          f"{[L.nm(n, T) for T in viol]}  -> Lemma 3 "
          f"{'FAILS (as predicted)' if viol else 'still holds (!)'}")
    for T in viol:
        QT = [i for i in Q if not (T >> i & 1)]
        print(f"      T={L.nm(n,T)}: Q\\T = {[L.LETTERS[i] for i in QT]} "
              f"(size {len(QT)}); crossing gives phi_f={phi[f_]} <= "
              f"{sum(phi[i] for i in QT)}  -- no contradiction since |Q\\T|>=2")
