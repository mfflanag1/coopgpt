"""Alternate exact tangent-LP polish with float hill-climb."""
import sys, json, os, time, numpy as np
from fractions import Fraction as F
from search import mutate, evaluate, has_zero_per_player
from tangent_lp import cell_lp, integerize
from exactsel import analyze, target

def climb(G, rng, iters, T):
    cur = evaluate(G); best, bestG = cur, G.copy(); stall = 0
    for it in range(iters):
        H = mutate(G, rng, T)
        if H is None: continue
        val = evaluate(H)
        if val >= cur - 1e-12:
            stall = 0 if val > cur + 1e-12 else stall + 1
            G, cur = H, val
            if cur > best + 1e-12: best, bestG = cur, G.copy()
        else: stall += 1
        if stall > 3000: break
    return bestG, best

def main(seedfile, wid, rounds, outdir, climb_iters):
    rng = np.random.default_rng(777 + wid)
    G = np.array(json.load(open(seedfile))['gens']); n = G.shape[1]; tgt = float(target(n))
    log = open(os.path.join(outdir, f'alt{wid}.log'), 'a'); t0 = time.time()
    best_exact = F(0)
    for rnd in range(rounds):
        # exact polish
        try:
            newgens, lp_rho, old_rho = cell_lp([[int(a) for a in g] for g in G])
            Gi = integerize(newgens); r = analyze(Gi, verbose=False)
            if r['rho'] >= lp_rho - F(1, 10**9) and r['rho'] > best_exact:
                best_exact = r['rho']
                json.dump({'n': n, 'T': int(r['T']), 'gens': Gi, 'rho': float(r['rho']), 'rho_exact': str(r['rho'])}, open(os.path.join(outdir, f'altbest{wid}.json'), 'w'))
            log.write(f'round {rnd} t={time.time()-t0:.0f}s polish: {float(old_rho):.6f} -> LP {float(lp_rho):.6f} verified {float(r["rho"]):.6f} ({str(r["rho"])}) best_exact={float(best_exact):.6f} target={tgt:.6f}\n'); log.flush()
            G = np.array(Gi)
            # rescale so integers are moderate for the climber
            T = int(G[0].sum())
            if T > 10**6:
                s = 10**6 / T; G = np.round(G * s).astype(int)
                for row in G: row[np.argmax(row)] += 10**6 - row.sum()
                if not has_zero_per_player(G): G = np.array(Gi)
        except Exception as e:
            log.write(f'round {rnd} polish failed: {e!r}\n'); log.flush()
        T = int(G[0].sum())
        G, val = climb(G, rng, climb_iters, T)
        log.write(f'round {rnd} t={time.time()-t0:.0f}s climb -> {val:.6f}\n'); log.flush()

if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5]))
