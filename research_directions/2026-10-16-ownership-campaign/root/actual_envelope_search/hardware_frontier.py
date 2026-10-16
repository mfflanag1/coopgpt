"""Hardware-bottleneck-only search. Numerical lower witnesses, never upper proofs."""
import argparse
import json
import time
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution
from probe_v2 import actual


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, default=5)
    parser.add_argument('--m', type=int, default=3)
    parser.add_argument('--seconds', type=float, default=600)
    parser.add_argument('--seed', type=int, default=1924)
    parser.add_argument('--grid-owner', type=int, default=-1)
    args = parser.parse_args()
    n, m, seed = args.n, args.m, args.seed
    width = 2*m+1
    size = n*width
    start = time.monotonic()
    best = [0., None]
    runs = []
    dest = Path(__file__).with_name(f'hardware_frontier_{n}_{m}_{seed}.json')

    def unpack(raw):
        x = np.asarray(raw)
        x = x.T if x.ndim == 2 else x[None, :]
        base = x[:, :size].reshape(-1, n, width).copy()
        frac = x[:, size:].reshape(-1, n, width)
        # Absolute report capacities remain nonnegative; normalize full hardware.
        hardware = base[:, :, :m].sum(axis=(1, 2))
        base[:, :, :m] /= np.maximum(hardware[:, None, None], 1e-15)
        local = np.minimum(base[:, :, :m].sum(axis=1),
                           base[:, :, m:2*m].sum(axis=1)).sum(axis=1)
        p = base[:, :, -1]
        if args.grid_owner >= 0:
            total = p.sum(axis=1)
            p[:] = 0
            p[:, args.grid_owner] = 1-local+total
        else:
            total = p.sum(axis=1)
            weights = np.divide(p, total[:, None], out=np.full_like(p, 1/n),
                                where=total[:, None] > 0)
            p[:] += weights * (1-local[:, None])
        return base, frac

    def objective(raw):
        base, frac = unpack(raw)
        _, pay, F = actual(base, frac, n, m)
        _, full, _ = actual(base, np.ones_like(frac), n, m)
        value = np.maximum(pay, full).sum(axis=1)/np.maximum(F, 1e-15)
        at = int(np.argmax(value))
        if value[at] > best[0]:
            x = np.asarray(raw)
            x = x.T if x.ndim == 2 else x[None, :]
            best[:] = [float(value[at]), x[at].copy()]
        return -value if np.asarray(raw).ndim == 2 else -float(value[0])

    def save():
        if best[1] is None:
            return
        base, frac = unpack(best[1])
        _, pay, F = actual(base, frac, n, m)
        _, full, _ = actual(base, np.ones_like(frac), n, m)
        chosen = np.where((pay >= full)[:, :, None], base*frac, base)
        data = dict(status='numerical lower witness; not a universal bound',
                    n=n, m=m, seed=seed, elapsed=time.monotonic()-start,
                    ratio=best[0], F=float(F[0]), base=base[0].tolist(),
                    own_underreports=chosen[0].tolist(),
                    payments_at_distinct_profiles=np.maximum(pay, full)[0].tolist(),
                    raw_sum=float(full[0].sum()), runs=runs)
        dest.write_text(json.dumps(data, indent=2)+'\n')

    for rep in range(100):
        def callback(x, convergence):
            save()
            return time.monotonic()-start >= args.seconds
        result = differential_evolution(
            objective, [(0., 1.)]*(2*size), seed=seed+rep, popsize=6,
            maxiter=1800, polish=False, vectorized=True, updating='deferred',
            callback=callback, tol=1e-8)
        runs.append(dict(rep=rep, ratio=-float(result.fun), nit=int(result.nit)))
        save()
        print(json.dumps(dict(rep=rep, best=best[0], elapsed=time.monotonic()-start)),
              flush=True)
        if time.monotonic()-start >= args.seconds:
            break
    print(dest, flush=True)


if __name__ == '__main__':
    main()
