"""Fresh-process verification of the SD-prekernel multi-valuedness witness.
Independent s_ij (does NOT import sdpk.py) built directly on sd.sd_satisfactions.
"""
import json
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from sd import sd_satisfactions, certified_sd_prenucleolus, sd_kohlberg_certify
from hunt_sd import is_exact_game, is_totally_balanced

def s_ij(game, x):
    """Independent reimplementation: s_ij = min_{S: i in S, j notin S} F(S;x)."""
    n, N = game.n, game.N
    Fx = sd_satisfactions(game, x)
    out = {}
    for i in range(n):
        for j in range(n):
            if i == j: continue
            vals = [Fx[S] for S in range(1, N) if (S >> i & 1) and not (S >> j & 1)]
            out[(i, j)] = min(vals)
    return out

def full_report(v, x_second, x_star_claimed):
    g = Game(4, [F(a) for a in v])
    N = g.N
    print("game v:", [str(x) for x in g.v])
    print("balanced:", is_balanced_game(g))

    # 1. recompute exact SD-prenucleolus from scratch
    xstar = certified_sd_prenucleolus(g)
    print("recomputed certified SD-prenucleolus:", [str(x) for x in xstar])
    print("  matches claimed x*:", list(xstar) == x_star_claimed)

    # 2. x* equalizes (theorem check)
    s0 = s_ij(g, xstar)
    imb0 = {(i,j): s0[(i,j)]-s0[(j,i)] for i in range(4) for j in range(i+1,4)}
    print("x* all pairs equalize:", all(d==0 for d in imb0.values()), imb0)

    # 3. the SECOND point
    x = x_second
    print("\nsecond point x:", [str(a) for a in x])
    print("efficient (sum == v(N)):", sum(x) == g.v[N], "sum =", sum(x), "v(N) =", g.v[N])
    s = s_ij(g, x)
    imb = {(i,j): s[(i,j)]-s[(j,i)] for i in range(4) for j in range(i+1,4)}
    print("all pairs s_ij==s_ji:", all(d==0 for d in imb.values()))
    for k,d in imb.items():
        print(f"   pair {k}: s_ij-s_ji = {d}")
    print("s_ij full matrix:")
    for i in range(4):
        for j in range(4):
            if i!=j: print(f"   s[{i}{j}] = {s[(i,j)]}")

    print("\nx != x* (distinct points):", list(x) != list(xstar))

    # 4. also confirm x is NOT the SD-prenucleolus via SD-Kohlberg (should be a
    #    prekernel point but generally NOT the prenucleolus)
    okx, _ = sd_kohlberg_certify(g, x)
    print("x passes SD-Kohlberg (would mean x is the SD-prenucleolus):", okx)
    okstar, _ = sd_kohlberg_certify(g, xstar)
    print("x* passes SD-Kohlberg:", okstar)

    # 5. classes / core
    print("\n--- class membership ---")
    print("superadditive:", g.is_superadditive())
    print("convex:", g.is_convex())
    print("exact:", is_exact_game(g))
    print("totally balanced:", is_totally_balanced(g))
    print("x in core:", g.in_core(x))
    print("x* in core:", g.in_core(xstar))
    if not g.in_core(x):
        print("  x core violations:", [(S, str(g.xS(x,S)), str(g.v[S])) for S in g.core_violations(x)])

if __name__ == "__main__":
    d = json.load(open("../results/agent_sdpk_witness.json"))
    v = [F(a) for a in d["v"]]
    x_second = [F(a) for a in d["second_prekernel_point_clean"]]
    x_star = [F(a) for a in d["sd_prenucleolus"]]
    full_report(v, x_second, x_star)
