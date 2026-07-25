"""Hill-climbing hunt for entry-monotonicity violations of the nucleolus
in assignment games. Objective for a matrix A and bump (i,j,d):
    f = max over p in {row i, col j} of  x_p(A) - x_p(A + d*E_ij)
Violation iff f > 0. Climb f by +-1 mutations of entries, random restarts.
"""
import random, sys, json
from fractions import Fraction as F
from assignment import assignment_game
from nucleolus import prenucleolus_float, certified_prenucleolus

def payoff(A):
    g = assignment_game(A)
    return prenucleolus_float(g)

def margin(A, i, j, d):
    x = payoff(A)
    if x is None:
        return None
    A2 = [r[:] for r in A]; A2[i][j] += d
    y = payoff(A2)
    if y is None:
        return None
    m = len(A)
    return max(x[i] - y[i], x[m + j] - y[m + j])

def climb(m, mp, restarts, steps, seed, vmax=15):
    rng = random.Random(seed)
    best_global = None
    for r in range(restarts):
        A = [[rng.randint(0, vmax) for _ in range(mp)] for _ in range(m)]
        i, j, d = rng.randrange(m), rng.randrange(mp), rng.choice([1, 2])
        f = margin(A, i, j, d)
        if f is None:
            continue
        for s in range(steps):
            a, b = rng.randrange(m), rng.randrange(mp)
            delta = rng.choice([-2, -1, 1, 2])
            A2 = [row[:] for row in A]
            A2[a][b] = max(0, A2[a][b] + delta)
            f2 = margin(A2, i, j, d)
            if f2 is not None and f2 > f:
                A, f = A2, f2
            if f > 1e-6:
                break
        if best_global is None or f > best_global[0]:
            best_global = (f, [row[:] for row in A], i, j, d)
            print(f"[restart {r}] best margin {f:.5f} bump=({i},{j})+{d} A={A}")
        if f > 1e-6:
            print("FLOAT VIOLATION, certifying...")
            gx = certified_prenucleolus(assignment_game(A))
            A2 = [row[:] for row in A]; A2[i][j] += d
            gy = certified_prenucleolus(assignment_game(A2))
            if gx and gy:
                ed = [(p, gx[p] - gy[p]) for p in (i, m + j) if gx[p] > gy[p]]
                if ed:
                    print("CERTIFIED entry-monotonicity violation:")
                    print(json.dumps({"A": A, "bump": [i, j, d],
                                      "x": [str(u) for u in gx], "y": [str(u) for u in gy],
                                      "drops": [(p, str(dd)) for p, dd in ed]}, indent=1))
                    return
            print("certification failed — recording as false positive")
    print("best margin overall:", best_global[0] if best_global else None)
    if best_global:
        print("A =", best_global[1], "bump", best_global[2:])

if __name__ == "__main__":
    m, mp = int(sys.argv[1]), int(sys.argv[2])
    restarts, steps = int(sys.argv[3]), int(sys.argv[4])
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    climb(m, mp, restarts, steps, seed)
