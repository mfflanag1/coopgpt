"""Is the eta < 0 branch ever ACTIVE?

Lemma D: any dual-feasible (eta, gamma) with eta >= 0 already certifies (R).
So (R) holds whenever the dual optimum is attained at some eta >= 0.  If that
is ALWAYS the case, Lemma D closes (R) and mu = lambda follows by hand.
Test: compare the unrestricted dual optimum with the dual optimum restricted to
eta >= 0, on genuine exact five-player games and all ordered pairs.
    dual:  min eta*T + sum_S gamma_S f(S)
           s.t. gamma >= 0,  eta + sum_{S ni k} gamma_S >= w_k,  w = 2e_p + e_q.
"""
import sys, random
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L, z3
n, FULL = 5, 31
PROPER = [S for S in range(1, FULL)]

def dual_opt(w, T, f, p, q, force_nonneg_eta):
    eta = z3.Real("eta")
    g = {S: z3.Real(f"g{S}") for S in PROPER}
    o = z3.Optimize()
    for S in PROPER:
        o.add(g[S] >= 0)
    if force_nonneg_eta:
        o.add(eta >= 0)
    for k in range(n):
        wk = 2 if k == p else (1 if k == q else 0)
        o.add(eta + z3.Sum([g[S] for S in PROPER if S >> k & 1]) >= wk)
    obj = eta * L.to_z3(T) + z3.Sum([g[S] * L.to_z3(f[S]) for S in PROPER])
    h = o.minimize(obj)
    if o.check() != z3.sat:
        return None
    return L.rat(o.lower(h))

rng = random.Random(41)
tested = same = diff = 0
worst = None
while tested < 60:
    total = rng.randint(4, 14)
    gens = []
    for _ in range(rng.randint(2, 5)):
        cuts = sorted(rng.randrange(total + 1) for _ in range(n - 1))
        gens.append(tuple(F(b - a) for a, b in zip([0] + cuts, cuts + [total])))
    if any(min(gg[i] for gg in gens) != 0 for i in range(n)):
        continue
    w, sh = L.normalize(n, L.envelope(n, gens))
    T = w[FULL]
    if T <= 0:
        continue
    tested += 1
    f = {S: T - w[FULL ^ S] for S in PROPER}
    lam = min(F(f[S], bin(S).count("1")) for S in PROPER)
    for p in range(n):
        for q in range(n):
            if p == q:
                continue
            free = dual_opt(w, T, f, p, q, False)
            nn = dual_opt(w, T, f, p, q, True)
            if free == nn:
                same += 1
            else:
                diff += 1
                d = (free, nn, T, p, q, lam)
                if worst is None or (free - 3*lam) < (worst[0] - 3*worst[5]):
                    worst = d
print(f"games {tested}, ordered pairs {same + diff}")
print(f"  dual optimum unchanged by forcing eta >= 0 : {same}")
print(f"  strictly better with eta < 0 allowed       : {diff}")
if diff == 0:
    print("  => the eta < 0 branch is NEVER active: Lemma D alone certifies (R),")
    print("     which would CLOSE mu = lambda at n = 5 by hand.")
else:
    print(f"  => eta < 0 IS active; example free={worst[0]} vs eta>=0 {worst[1]},"
          f" 3*lambda={3*worst[5]} (T={worst[2]}, p={worst[3]}, q={worst[4]})")
    print(f"     free optimum still >= 3*lambda: {worst[0] >= 3*worst[5]}")
