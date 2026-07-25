"""Hunt EXACT games with BS strictly containing the core, using SYMMETRY.

Insight: the 2025 Atay-Nunez-Solymosi BS-not-core point relied on player symmetry
(2 symmetric firms, 3 symmetric workers) so every objection is mirror-countered.
Generic random exact games lack this. So: build SYMMETRIC exact games via a
symmetric point set (min-of-points generator, orbit-closed), then probe the
symmetric segment {type-a players get alpha, type-b get beta} for a point that is
outside the core but in the DM bargaining set (certified by the exact oracle).

An orbit-closed point set => v is invariant under the type-preserving permutations,
so the whole symmetric segment inherits mirror-counterability of objections.
"""
import random, sys, json, itertools
from fractions import Fraction as F
from tugame import Game
from hunt_sd import is_exact_game
from bargaining_set import in_bargaining_set


def orbit(pt, perms):
    return {tuple(pt[p[i]] for i in range(len(pt))) for p in perms}


def type_perms(types):
    """All permutations of players that preserve the type partition `types`
    (list assigning each player a type label)."""
    n = len(types)
    groups = {}
    for i, t in enumerate(types):
        groups.setdefault(t, []).append(i)
    ranges = [g for g in groups.values()]
    out = []
    # cartesian product of independent permutations within each type group
    perm_lists = [list(itertools.permutations(g)) for g in ranges]
    for combo in itertools.product(*perm_lists):
        p = list(range(n))
        for g, pg in zip(ranges, combo):
            for src, dst in zip(g, pg):
                p[src] = dst
        out.append(p)
    return out


def game_from_points(n, pts):
    N = (1 << n) - 1
    c = sum(pts[0])
    v = [0] * (1 << n)
    for S in range(1, N):
        v[S] = min(sum(pts[j][i] for i in range(n) if S >> i & 1) for j in range(len(pts)))
    v[N] = c
    return Game(n, [F(x) for x in v])


def symmetric_exact_game(n, types, rng, cmax=12, kbase=2):
    """Build an orbit-closed (=> type-symmetric) exact game from a random base
    point set. Returns Game or None."""
    perms = type_perms(types)
    # base points, then close under the symmetry group
    ptset = set()
    c = rng.randint(n, cmax)
    for _ in range(kbase):
        # random composition of c into n parts
        cuts = sorted(rng.randint(0, c) for _ in range(n - 1))
        prev = 0; p = []
        for x in cuts:
            p.append(x - prev); prev = x
        p.append(c - prev)
        ptset |= orbit(p, perms)
    pts = [list(p) for p in ptset]
    if not all(sum(p) == c for p in pts):
        return None
    return game_from_points(n, pts)


def symmetric_segment_points(game, types):
    """Yield rational imputations constant within each type, on a grid, IR+efficient."""
    n = game.n
    groups = {}
    for i, t in enumerate(types):
        groups.setdefault(t, []).append(i)
    labels = list(groups.keys())
    sizes = [len(groups[l]) for l in labels]
    vN = game.v[game.N]
    # enumerate per-type payoff alpha_l on a rational grid with sum size_l*alpha_l = vN
    # 2 or 3 types: grid search over alpha for all but last type
    G = 12  # grid resolution
    ivals = {l: game.v[1 << groups[l][0]] for l in labels}   # symmetric singleton value
    def rec(idx, remaining, chosen):
        if idx == len(labels) - 1:
            l = labels[idx]
            if remaining < 0:
                return
            alpha = F(remaining, sizes[idx])
            if alpha < ivals[l]:
                return
            chosen2 = dict(chosen); chosen2[l] = alpha
            x = [F(0)] * n
            for ll in labels:
                for i in groups[ll]:
                    x[i] = chosen2[ll]
            yield x
            return
        l = labels[idx]
        for step in range(G + 1):
            alpha = ivals[l] + (vN) * F(step, G) / sizes[idx]
            used = alpha * sizes[idx]
            if used > remaining + F(1, 1):
                break
            if alpha < ivals[l]:
                continue
            yield from rec(idx + 1, remaining - used, {**chosen, l: alpha})
    yield from rec(0, vN, {})


def probe_game(game, types):
    """Return a certified BS-outside-core witness x or None."""
    for x in symmetric_segment_points(game, types):
        if sum(x) != game.v[game.N]:
            continue
        if any(x[i] < game.v[1 << i] for i in range(game.n)):
            continue
        viol = game.core_violations(x)
        if not viol:
            continue
        inbs, _ = in_bargaining_set(game, x)
        if inbs:
            return x, viol
    return None


def hunt(n, types, trials, seed):
    rng = random.Random(seed)
    LOG = f"/Users/maxf/projects/counterexample-hunt/coopgames/results/wildcard_bssym_n{n}_s{seed}.txt"
    def log(m):
        print(m, flush=True)
        with open(LOG, "a") as f:
            f.write(m + "\n")
    seen = 0; nonconvex = 0
    for t in range(trials):
        g = symmetric_exact_game(n, types, rng)
        if g is None:
            continue
        if not is_exact_game(g):
            continue
        seen += 1
        if g.is_convex():
            continue
        nonconvex += 1
        res = probe_game(g, types)
        if res is not None:
            x, viol = res
            rep = {"n": n, "types": types, "seed": seed, "trial": t,
                   "v": [str(a) for a in g.v], "witness_x": [str(a) for a in x],
                   "is_exact": True, "is_convex": False,
                   "core_violations": [{"S": S, "members": [i for i in range(n) if S >> i & 1],
                                        "v(S)": str(g.v[S]),
                                        "x(S)": str(sum(x[i] for i in range(n) if S >> i & 1))}
                                       for S in viol]}
            log("*** CERTIFIED: exact non-convex SYMMETRIC game with BS point outside core ***")
            log(json.dumps(rep, indent=1))
            with open(f"/Users/maxf/projects/counterexample-hunt/coopgames/results/WITNESS_bs_exact_sym.json", "w") as f:
                json.dump(rep, f, indent=1)
            return rep
        if t % 500 == 0 and t:
            log(f"... t={t} exact_seen={seen} nonconvex={nonconvex}")
    log(f"DONE n={n} types={types} seed={seed}: trials={trials} exact_seen={seen} "
        f"nonconvex={nonconvex} NO witness")
    return None


if __name__ == "__main__":
    n = int(sys.argv[1]); trials = int(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    types = [int(c) for c in sys.argv[4]] if len(sys.argv) > 4 else [0, 0, 1, 1, 1]
    hunt(n, types, trials, seed)
