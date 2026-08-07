"""Search over the FULL space of exact games at n=5, via core polytopes.

Key fact (used to make the search complete): for ANY vector c indexed by the
proper nonempty coalitions, the polytope
      P(c) = { x : x(N) = T, x(S) >= c_S for all proper S }
if nonempty is EXACTLY the core of the exact game  v(S) = min_{x in P(c)} x(S),
and core(v) = P(c).  So every exact game arises this way, and no exactness test
is needed: "core-closing" an arbitrary c always lands in the exact class.
This search space therefore covers exact games whose core has arbitrarily many
vertices -- unlike a search over <= k generators.

usage: python3 cspace.py <seed> <nsteps> <nrestarts> [tag]
"""
import sys, json, random, time
from fractions import Fraction as F
import z3
import lib, audit

N = 5
FULL = (1 << N) - 1
SUBS = [S for S in range(1, FULL)]


def core_close(c, T):
    """v(S) = min over P(c) of x(S); returns None if P(c) empty."""
    x = [z3.Real(f"x{i}") for i in range(N)]
    base = [z3.Sum(x) == audit.to_z3(T)] + [
        z3.Sum([x[i] for i in range(N) if S >> i & 1]) >= audit.to_z3(c[S])
        for S in SUBS]
    s = z3.Solver(); s.add(base)
    if s.check() != z3.sat:
        return None
    v = [F(0)] * (1 << N)
    v[FULL] = F(T)
    for S in SUBS:
        o = z3.Optimize(); o.add(base)
        h = o.minimize(z3.Sum([x[i] for i in range(N) if S >> i & 1]))
        if o.check() != z3.sat:
            return None
        v[S] = audit.rat(o.lower(h))
    return v


def evaluate(c, T):
    """Return (v, lmin, lmax, l1, ratio) after core-closing and singleton-normalising."""
    v = core_close(c, T)
    if v is None:
        return None
    w, _ = lib.normalize(N, v)
    if w[FULL] == 0:
        return None
    mn = lib.lmin(N, w); mx = lib.lmax(N, w)
    if mn is None:
        return None
    l1 = sum(abs(mn[i] - mx[i]) for i in range(N))
    return w, mn, mx, l1, F(l1, 1) / w[FULL]


def random_c(rng, T):
    c = [F(0)] * (1 << N)
    style = rng.choice(["sparse", "dense", "size"])
    for S in SUBS:
        k = bin(S).count("1")
        if style == "sparse":
            c[S] = F(rng.choice([0, 0, 0, rng.randint(0, T)]))
        elif style == "dense":
            c[S] = F(rng.randint(0, T))
        else:
            c[S] = F(rng.randint(0, max(1, (k * T) // N)))
    return c


def climb(c, T, rng, nsteps, best_ratio):
    cur = list(c)
    r = evaluate(cur, T)
    if r is None:
        return None, F(-1), 0
    best = r[4]; bestv = r
    steps = 0
    deltas = [F(1), F(-1), F(1, 2), F(-1, 2), F(2), F(-2)]
    while steps < nsteps:
        improved = False
        order = SUBS[:]
        rng.shuffle(order)
        for S in order:
            for d in deltas:
                steps += 1
                if steps > nsteps:
                    break
                if cur[S] + d < 0:
                    continue
                trial = list(cur)
                trial[S] = cur[S] + d
                rr = evaluate(trial, T)
                if rr is None:
                    continue
                if rr[4] > best:
                    best = rr[4]; bestv = rr; cur = trial; improved = True
                    break
            if improved or steps > nsteps:
                break
        if not improved:
            break
    return cur, best, steps


def main():
    seed = int(sys.argv[1]); nsteps = int(sys.argv[2]); nrestarts = int(sys.argv[3])
    tag = sys.argv[4] if len(sys.argv) > 4 else "cs"
    rng = random.Random(seed)
    overall = F(0); best_rec = None
    t0 = time.time(); recs = []
    for rs in range(nrestarts):
        T = rng.choice([4, 6, 8, 12])
        c = random_c(rng, T)
        cur, br, steps = climb(c, T, rng, nsteps, overall)
        if cur is None:
            continue
        r = evaluate(cur, T)
        if r is None:
            continue
        w, mn, mx, l1, ratio = r
        recs.append(dict(T=T, ratio=str(ratio), steps=steps,
                         v=[str(q) for q in w], lmin=lib.s(mn), lmax=lib.s(mx),
                         l1=str(l1), total=str(w[FULL])))
        print(f"restart {rs}: T={T} ratio={ratio} ({float(ratio):.5f}) steps={steps}")
        if ratio > overall:
            overall = ratio; best_rec = recs[-1]
            print(f"  *** NEW OVERALL {ratio}  Lmin={lib.s(mn)} Lmax={lib.s(mx)} "
                  f"total={w[FULL]}")
    print(f"[cspace seed={seed}] restarts={nrestarts} MAX={overall} "
          f"({float(overall):.6f})  {time.time()-t0:.1f}s")
    recs.sort(key=lambda z: -F(z["ratio"]))
    with open(f"cspace_{tag}_{seed}.json", "w") as f:
        json.dump(dict(seed=seed, max_ratio=str(overall), best=best_rec,
                       top=recs[:15]), f, indent=1)


if __name__ == "__main__":
    main()
