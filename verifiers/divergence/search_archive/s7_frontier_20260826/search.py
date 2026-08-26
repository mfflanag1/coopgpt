import sys, json, time, os, random
import numpy as np
from fastsel import rho_float
from fractions import Fraction as F

def target(n): return F(2) - F(8*n, n*n - (n % 2))

def has_zero_per_player(G):
    return bool(np.all((G == 0).any(axis=0)))

def G_family(p, k, scale):
    g = [p*(k-1)] + [1]*p + [0]*k; h = [0]*(p+1) + [p]*k
    return np.array([g, h]) * scale

def seed_from(name, rng):
    if name == 'pxc143':
        return np.array([[8507,24825,41719,17026,8555,8519,10225],[36,132,25137,25137,25125,25113,18696],[0,132,25233,25209,25077,24993,18732],[180,0,25029,25413,25077,25137,18540],[48,0,0,50310,25281,25065,18672],[8483,25293,58733,0,8231,8399,10237],[60,41575,66880,8507,0,312,2042],[8207,33596,58685,8543,96,0,10249],[60,43785,68754,6501,132,144,0]])
    if name.startswith('G'):
        p, k = map(int, name[1:].split(','))
        base = G_family(p, k, 1000)
        gens = [base[0], base[1]]
        # perturbed copies preserving zeros
        for _ in range(rng.integers(2, 6)):
            b = base[rng.integers(0, 2)].copy()
            nz = np.where(b > 0)[0]
            for _ in range(rng.integers(1, 4)):
                i, j = rng.choice(nz, 2, replace=False)
                d = int(rng.integers(1, max(2, b[i] // 3)))
                b[i] -= d; b[j] += d
            gens.append(b)
        return np.array(gens)
    if name.startswith('file:'):
        return np.array(json.load(open(name[5:]))['gens'])
    if name.startswith('rand'):
        n = int(name[4:]); T = 1000; m = int(rng.integers(2, 6))
        gens = []
        for _ in range(m):
            w = rng.random(n); w[rng.integers(0, n)] = 0
            g = np.floor(w / w.sum() * T).astype(int); g[np.argmax(g)] += T - g.sum(); gens.append(g)
        G = np.array(gens)
        for i in range(n):
            if not (G[:, i] == 0).any():
                r = rng.integers(0, m); G[r, np.argmax(G[r])] += G[r, i]; G[r, i] = 0
        return G
    raise ValueError(name)

def evaluate(G):
    r = rho_float(G)
    return -1.0 if r is None else r[0]

def mutate(G, rng, T):
    G = G.copy(); m, n = G.shape
    u = rng.random()
    if u < 0.85 or m == 1:
        r = int(rng.integers(0, m)); i, j = rng.choice(n, 2, replace=False)
        if G[r, i] <= 0: return None
        d = int(min(G[r, i], 2 ** rng.integers(0, 12), max(1, T // 50)))
        d = int(rng.integers(1, d + 1))
        G[r, i] -= d; G[r, j] += d
    elif u < 0.93 and m < 12:
        r = int(rng.integers(0, m)); b = G[r].copy()
        for _ in range(int(rng.integers(1, 4))):
            i, j = rng.choice(n, 2, replace=False)
            if b[i] > 0:
                d = int(rng.integers(1, max(2, min(b[i], T // 20)))); b[i] -= d; b[j] += d
        G = np.vstack([G, b])
    else:
        if m <= 2: return None
        r = int(rng.integers(0, m)); G = np.delete(G, r, axis=0)
    if (G < 0).any() or not has_zero_per_player(G): return None
    return G

def worker(seedname, wid, iters, outdir):
    rng = np.random.default_rng(1000 * wid + 7)
    G = seed_from(seedname, rng); T = int(G[0].sum()); n = G.shape[1]
    cur = evaluate(G); best = cur; bestG = G.copy()
    tgt = float(target(n)); t0 = time.time(); stall = 0
    log = open(os.path.join(outdir, f'w{wid}_{seedname}.log'), 'a')
    log.write(f'start seed={seedname} n={n} T={T} rho0={cur:.9f} target={tgt:.9f}\n'); log.flush()
    for it in range(iters):
        H = mutate(G, rng, T)
        if H is None: continue
        val = evaluate(H)
        if val >= cur - 1e-12:
            if val > cur + 1e-12: stall = 0
            else: stall += 1
            G, cur = H, val
            if cur > best + 1e-12:
                best, bestG = cur, G.copy()
                log.write(f'it={it} t={time.time()-t0:.0f}s best={best:.9f} (target {tgt:.9f}, excess {best-tgt:+.3e}) m={G.shape[0]}\n'); log.flush()
                json.dump({'seed': seedname, 'n': n, 'T': T, 'rho': best, 'gens': bestG.tolist()}, open(os.path.join(outdir, f'best_w{wid}_{seedname}.json'), 'w'))
        else:
            stall += 1
        if stall > 4000:  # restart from best with a kick
            G = bestG.copy(); cur = best; stall = 0
            for _ in range(20):
                H = mutate(G, rng, T)
                if H is not None: G = H
            cur = evaluate(G)
    log.write(f'done best={best:.9f}\n'); log.close()

if __name__ == '__main__':
    seedname, wid, iters, outdir = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    os.makedirs(outdir, exist_ok=True)
    worker(seedname, wid, iters, outdir)
