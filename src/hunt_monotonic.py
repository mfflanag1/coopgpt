"""Monotonicity violation hunter for the (pre)nucleolus.

Modes:
  aggregate  : v'(N) = v(N) + delta, all else equal. Violation: some x_i strictly drops.
  coalitional: v'(S) = v(S) + delta for one proper S, all else equal.
               Violation: some i in S with x'_i < x_i.

Search with float nucleolus; certify candidates exactly (Kohlberg on both games,
exact payoff comparison, exact class membership checks).
"""
import random, sys, json
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from nucleolus import prenucleolus_float, certified_prenucleolus

def rand_game(n, rng, kind="general", vmax=20):
    """Random zero-normalized integer game, superadditive-ish by construction."""
    Nm = (1 << n) - 1
    v = [F(0)] * (1 << n)
    if kind == "convex":
        # random supermodular: sum of unanimity games with nonneg weights + noise fixed up
        v = [F(0)] * (1 << n)
        for _ in range(rng.randint(2, 6)):
            T = rng.randint(1, Nm)
            w = rng.randint(1, 5)
            for S in range(1, 1 << n):
                if S & T == T:
                    v[S] += w
        # zero-normalize
        base = [v[1 << i] for i in range(n)]
        for S in range(1, 1 << n):
            v[S] -= sum(base[i] for i in range(n) if S >> i & 1)
        return Game(n, v)
    if kind == "veto":
        # player 0 is a veto player: v(S) = 0 unless 0 in S
        g = rand_game(n, rng, "general", vmax)
        v = list(g.v)
        for S in range(1, Nm + 1):
            if not (S & 1):
                v[S] = F(0)
        return Game(n, v)
    order = sorted(range(1, Nm + 1), key=popcount_key)
    for S in order:
        if popcount(S) == 1:
            v[S] = F(0)
            continue
        lo = 0
        T = (S - 1) & S
        while T:
            lo = max(lo, v[T] + v[S ^ T])
            T = (T - 1) & S
        v[S] = F(lo + rng.randint(0, vmax))
    return Game(n, v)

def popcount(m): return bin(m).count("1")
def popcount_key(m): return popcount(m)

def float_prenuc_or_none(g):
    try:
        return prenucleolus_float(g)
    except Exception:
        return None

def hunt(n, mode, kind, trials, seed, require_balanced=True):
    rng = random.Random(seed)
    found = []
    for t in range(trials):
        g = rand_game(n, rng, kind)
        x = float_prenuc_or_none(g)
        if x is None:
            continue
        Nm = g.N
        if mode == "aggregate":
            bumps = [(Nm, rng.choice([1, 2, 5]))]
        else:
            S = rng.randint(1, Nm - 1)
            bumps = [(S, rng.choice([1, 2, 5]))]
        for S, d in bumps:
            v2 = list(g.v); v2[S] += d
            # keep superadditivity for the bumped game when S != N? (bump can break it; allow both, record)
            g2 = Game(n, v2)
            y = float_prenuc_or_none(g2)
            if y is None:
                continue
            watchers = range(n) if S == Nm else [i for i in range(n) if S >> i & 1]
            drop = [(i, x[i] - y[i]) for i in watchers if x[i] - y[i] > 1e-6]
            if drop:
                found.append((g.v, S, d, drop))
                print(f"[cand] trial={t} S={S:b} d={d} drops={[(i, round(dd,4)) for i,dd in drop]}")
                if len(found) >= 3:
                    return found
    return found

def certify(n, vlist, S, d, require_balanced=True):
    g = Game(n, vlist)
    v2 = list(g.v); v2[S] += d
    g2 = Game(n, v2)
    x = certified_prenucleolus(g)
    y = certified_prenucleolus(g2)
    if x is None or y is None:
        return None
    watchers = range(n) if S == g.N else [i for i in range(n) if S >> i & 1]
    drops = [(i, x[i] - y[i]) for i in watchers if x[i] > y[i]]
    if not drops:
        return None
    rep = {
        "n": n, "v": [str(t) for t in g.v], "bumped_S": S, "delta": str(d),
        "x": [str(t) for t in x], "y": [str(t) for t in y],
        "drops": [(i, str(dd)) for i, dd in drops],
        "balanced_before": is_balanced_game(g), "balanced_after": is_balanced_game(g2),
        "superadditive_before": g.is_superadditive(), "superadditive_after": g2.is_superadditive(),
        "convex_before": g.is_convex(), "convex_after": g2.is_convex(),
    }
    return rep

if __name__ == "__main__":
    n = int(sys.argv[1]); mode = sys.argv[2]; kind = sys.argv[3]
    trials = int(sys.argv[4]); seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    cands = hunt(n, mode, kind, trials, seed)
    print(f"{len(cands)} float candidates")
    for vlist, S, d, _ in cands:
        rep = certify(n, vlist, S, d)
        if rep:
            print("CERTIFIED VIOLATION:")
            print(json.dumps(rep, indent=1))
            break
    else:
        print("no certified violation")
