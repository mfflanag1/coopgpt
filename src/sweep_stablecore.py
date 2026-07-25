"""Focused sweep for stable-core non-ES assignment games.
Float-screen exactness (fast) to isolate the NON-large (strictly stable-core)
subclass, then run the EXACT egalitarian procedure on those. Any non-ES prints
and is returned. Also tries hub-column dominant-diagonal structures.
"""
import random, sys, json
from fractions import Fraction as F
from assignment import assignment_game
from eshunt import is_ES
from es_float import core_min_all
from hunt_stablecore import gen_dominant, dominant_diagonal, certify_witness


def exact_float(g):
    v = [float(x) for x in g.v]; n = g.n
    ve = core_min_all(n, v)
    if ve is None:
        return None
    return all(abs(ve[S] - v[S]) < 1e-7 for S in range(1, (1 << n) - 1))


def gen_hub_dominant(rng, m=3, dmax=10):
    """Dominant-diagonal matrix with a 'hub' column c*: every seller's second-best
    partner is the same buyer c*, i.e. a_i,c* pushed to its max min(d_i,d_c*) while
    other off-diagonals are small. Mimics the hub-over-cover mechanism."""
    d = [rng.randint(2, dmax) for _ in range(m)]
    A = [[0] * m for _ in range(m)]
    for i in range(m):
        A[i][i] = d[i]
    c = rng.randrange(m)
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            cap = min(d[i], d[j])
            if j == c:
                A[i][j] = cap                      # saturate the hub column
            else:
                A[i][j] = rng.randint(0, cap)
    return A


def run(gen, trials, seed, m, dmax, tag):
    rng = random.Random(seed)
    valid = nonlarge = nonES = 0
    for t in range(trials):
        A = gen(rng, m, dmax)
        if not dominant_diagonal(A):
            continue
        valid += 1
        g = assignment_game(A)
        ex = exact_float(g)
        is_nonlarge = (ex is False)
        if is_nonlarge:
            nonlarge += 1
        es, gamma = is_ES(g)
        if not es:
            nonES += 1
            print(f"[NON-ES] {tag} seed={seed} t={t} nonlarge={is_nonlarge} A={A} "
                  f"claims={[str(x) for x in gamma]} vN={g.v[g.N]}", flush=True)
            return A
    print(f"{tag} m={m} dmax={dmax} seed={seed} trials={trials} valid={valid} "
          f"nonlarge={nonlarge} nonES={nonES} (all ES)", flush=True)
    return None


if __name__ == "__main__":
    configs = [
        (gen_dominant, 3, 8), (gen_dominant, 3, 15), (gen_dominant, 3, 30),
        (gen_hub_dominant, 3, 12),
        (gen_dominant, 4, 6), (gen_hub_dominant, 4, 8),
    ]
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    nseeds = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    for gen, m, dmax in configs:
        tag = f"{gen.__name__}"
        for seed in range(nseeds):
            w = run(gen, trials, seed, m, dmax, tag)
            if w:
                print("WITNESS:", json.dumps(certify_witness(w), indent=1), flush=True)
                sys.exit(0)
