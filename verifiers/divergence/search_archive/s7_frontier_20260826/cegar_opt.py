#!/usr/bin/env python3
"""Optimize-CEGAR upper bound for s(7) in one sign cell.
Relaxation (necessary conditions, from the s(6) proof architecture): x,z on the simplex with the cell's signs,
seven singleton-zero witnesses, anchors, and exchange-blocker implications.  Maximize D=||x-z||_1.
Each optimum model -> exact envelope game -> true selectors (independent exactsel) -> if x,z are the selectors,
the value is attained by a genuine game (sharp in cell); else add tangent-separator implications and repeat.
"""
import sys, json, time, importlib.util
from fractions import Fraction as F
from pathlib import Path
import z3
ARCH = Path('/private/tmp/coop-s7-20260825/coopgames/verifiers/divergence/search_archive')
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
RELAX = load('n7_relax', ARCH / 'n7_exchange_relaxation_scratch.py')
SEP = load('n7_sep', ARCH / 'n7_exchange_tangent_separator.py')
sys.path.insert(0, str(Path(__file__).resolve().parent))
from exactsel import analyze
N = 7

def build(pcount, mcount, bound, max_support, timeout_ms, threshold=None):
    positive = tuple(range(pcount)); negative = tuple(range(pcount, pcount + mcount)); tied = tuple(range(pcount + mcount, N))
    opt = z3.Optimize() if threshold is None else z3.SolverFor('QF_LRA')
    opt.set(timeout=timeout_ms)
    x = [z3.Real(f'x_{i}') for i in range(N)]; z = [z3.Real(f'z_{i}') for i in range(N)]
    opt.add(z3.Sum(*x) == 1, z3.Sum(*z) == 1, *[c >= 0 for c in x + z],
            *[x[i] > z[i] for i in positive], *[z[i] > x[i] for i in negative], *[x[i] == z[i] for i in tied])
    D = 2 * z3.Sum(*[x[i] - z[i] for i in positive])
    if threshold is not None: opt.add(D > z3.RealVal(threshold))
    RELAX.selection_anchors(opt, x, z)
    W = []
    for zero in range(N):
        w = [z3.Real(f'q_{zero}_{i}') for i in range(N)]
        opt.add(z3.Sum(*w) == 1, w[zero] == 0, *[c >= 0 for c in w]); W.append(w)
    dirs = RELAX.direction_pool(bound, max_support)
    atoms = {side: RELAX.blocker_atoms(opt, x, z, W, side) for side in ('min', 'max')}
    menu = set()
    def add(side, d):
        if (side, d) in menu: return
        menu.add((side, d)); point = x if side == 'min' else z
        opt.add(z3.Implies(RELAX.lex_improves(point, d, side), RELAX.blocker_formula(atoms[side], d)))
    for side in ('min', 'max'):
        for d in dirs: add(side, d)
    return opt, x, z, W, D, add, menu

def rat(model, v):
    r = model.eval(v, model_completion=True); return F(r.as_fraction())

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--p', type=int, default=3); ap.add_argument('--m', type=int, default=4)
    ap.add_argument('--bound', type=int, default=1); ap.add_argument('--max-support', type=int, default=None)
    ap.add_argument('--timeout-ms', type=int, default=1200000); ap.add_argument('--rounds', type=int, default=200)
    ap.add_argument('--threshold', default=None); ap.add_argument('--seed-menu', default=None)
    ap.add_argument('--output', required=True)
    a = ap.parse_args()
    opt, x, z, W, D, add, menu = build(a.p, a.m, a.bound, a.max_support, a.timeout_ms, a.threshold)
    if a.seed_menu:
        for item in json.load(open(a.seed_menu)): add(item[0], tuple(item[1]))
    if a.threshold is None: h = opt.maximize(D)
    log = {'cell': (a.p, a.m), 'bound': a.bound, 'max_support': a.max_support, 'threshold': a.threshold, 'rounds': []}
    best_game = None
    for rnd in range(a.rounds):
        t0 = time.time(); verdict = opt.check(); dt = time.time() - t0
        row = {'round': rnd, 'verdict': str(verdict), 'menu': len(menu), 'seconds': dt}
        if verdict != z3.sat:
            row['reason'] = opt.reason_unknown() if verdict == z3.unknown else None
            log['rounds'].append(row); log['terminal'] = str(verdict); break
        model = opt.model()
        mx = tuple(rat(model, v) for v in x); mz = tuple(rat(model, v) for v in z)
        mw = tuple(tuple(rat(model, v) for v in w) for w in W)
        Dval = sum(abs(p - q) for p, q in zip(mx, mz))
        row['D_relaxed'] = str(Dval); row['x'] = [str(v) for v in mx]; row['z'] = [str(v) for v in mz]
        gens = (mx, mz) + mw
        seps = {side: SEP.separate(pt, gens, side) for side, pt in (('min', mx), ('max', mz))}
        adds = []
        for side, res in seps.items():
            if res['direction'] is not None:
                d = tuple(res['primitive_direction']); add(side, d); adds.append([side, list(d)])
        row['additions'] = adds
        # true rho of the envelope game (float quick check via exact analyze is slow; do exact only when no additions)
        if not adds:
            r = analyze([list(g) for g in gens], verbose=False)
            row['true_rho'] = str(r['rho']); row['selectors_match'] = (r['x'] == list(mx) and r['z'] == list(mz))
            log['rounds'].append(row); log['terminal'] = 'GAME_ATTAINS_RELAXED_OPTIMUM' if row['selectors_match'] else 'SEPARATOR_MISS'
            best_game = {'gens': [[str(v) for v in g] for g in gens], 'rho': str(r['rho'])}
            print(json.dumps(row), flush=True); break
        log['rounds'].append(row); print(json.dumps({k: row[k] for k in ('round', 'verdict', 'menu', 'seconds', 'D_relaxed', 'additions')}), flush=True)
        json.dump(log, open(a.output, 'w'), indent=1)
    log['menu'] = [[s, list(d)] for s, d in sorted(menu)]
    log['game'] = best_game
    json.dump(log, open(a.output, 'w'), indent=1)
    print('terminal', log.get('terminal'))
if __name__ == '__main__': main()
