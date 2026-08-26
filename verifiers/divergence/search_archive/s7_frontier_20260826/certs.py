"""Extract sparse staged Farkas certificates for Lmin/Lmax of a lower-envelope game (exact).
Stage s (Lmin): with earlier blocks fixed, prove y_i <= t for each player i of the block via
  sum_S lam_S [y(S) >= v(S)]  +  mu [y(N) = T]  + fixed-coordinate equalities  ==>  y_i <= t.
Identity: -sum lam_S 1_S + mu 1_N + sum_{j fixed} nu_j e_j = e_i  (lam >= 0, mu, nu free), value: mu T - sum lam v(S) - sum nu x_j = t.
Minimizes sum lam (sparsity proxy) with exact LP."""
import sys, json
from fractions import Fraction as F
from exactsel import analyze, envelope, exact_lp

def members(S, n): return [i for i in range(n) if S >> i & 1]

def stage_certs(gens, mode):
    gens = [[F(a) for a in g] for g in gens]; n = len(gens[0]); T = sum(gens[0])
    r = analyze(gens, verbose=False); y = r['x'] if mode == 'min' else r['z']; blocks = r['xblocks'] if mode == 'min' else r['zblocks']
    v = envelope(gens); full = (1 << n) - 1
    tight = [S for S in range(1, full) if sum(y[i] for i in members(S, n)) == v[S]]
    zero = [i for i in range(n) if y[i] == 0]
    out = []; fixed = []
    for bl, t in blocks:
        for i in bl:
            # variables: lam_S (tight), mu+, mu-, nu_j+, nu_j- (j fixed), (mode max: prove y_i >= t: identity sum lam 1_S - mu 1_N - sum nu e_j = e_i)
            cols = []  # each col: (vector over n, cost)
            names = []
            sgn = -1 if mode == 'min' else 1
            for S in tight:
                cols.append([sgn * F(1 if S >> j & 1 else 0) for j in range(n)]); names.append(('row', S))
            if True:
                for j in zero: cols.append([sgn * F(1 if k == j else 0) for k in range(n)]); names.append(('nonneg', j))
            cols.append([-sgn * F(1)] * n); names.append(('eff+', None)); cols.append([sgn * F(1)] * n); names.append(('eff-', None))
            for j in fixed:
                cols.append([F(1 if k == j else 0) for k in range(n)]); names.append(('fix+', j))
                cols.append([F(-1 if k == j else 0) for k in range(n)]); names.append(('fix-', j))
            for j in range(n):
                if j in fixed or j == i: continue
                # stage row: y_j >= t (min) / y_j <= t (max); same sign role as a core row
                cols.append([F(-1 if k == j else 0) for k in range(n)]); names.append(('stage', j))
            # equality system: sum_c w_c col_c = e_i, w >= 0; minimize sum w over rows
            nv = len(cols); A = []; b = []
            for k in range(n):
                row = [cols[c][k] for c in range(nv)]; A.append(row); b.append(F(1 if k == i else 0)); A.append([-a for a in row]); b.append(-b[-1])
            def bound_coef(nm):
                kind, S = nm
                if kind == 'row': return sgn * v[S]
                if kind == 'nonneg': return F(0)
                if kind == 'eff+': return (-sgn) * T
                if kind == 'eff-': return sgn * T
                if kind == 'fix+': return y[S]
                if kind == 'fix-': return -y[S]
                if kind == 'stage': return -t
            # dual LP: minimize the implied bound on y_i (min mode) / maximize it (max mode)
            c = [(-1 if mode == 'min' else 1) * bound_coef(nm) for nm in names]
            st, val, w = exact_lp(A, b, c, list(range(len(A))))
            assert st == 'optimal', (st, mode, i)
            used = [(names[k], w[k]) for k in range(nv) if w[k] != 0]
            # value check
            # value check: identity  sum_c w_c col_c = e_i ; evaluating at y gives y_i = sum_c w_c (col_c . y) and each (col_c.y) equals the row's bound
            val_bound = F(0)
            for (kind, S), wk in used:
                if kind == 'row': val_bound += wk * sgn * v[S]
                elif kind == 'nonneg': val_bound += 0
                elif kind == 'eff+': val_bound += wk * (-sgn) * T
                elif kind == 'eff-': val_bound += wk * sgn * T
                elif kind == 'fix+': val_bound += wk * y[S]
                elif kind == 'fix-': val_bound += -wk * y[S]
                elif kind == 'stage': val_bound += -wk * t
            if val_bound != t:
                print('VALUE MISMATCH', mode, i, val_bound, t, used); raise SystemExit
            out.append({'player': i, 'level': t, 'certificate': used})
        fixed += bl
    return out, y, tight

def bundle(gens):
    n = len(gens[0]); out = {}
    for mode in ('min', 'max'):
        certs, y, tight = stage_certs(gens, mode)
        stages = []
        for c in certs:
            rows = {}; fixed = {}; stage = {}; eff = F(0); 
            for (kind, S), w in c['certificate']:
                if kind == 'row': rows[str(S)] = str(w)
                elif kind == 'eff+': eff += w
                elif kind == 'eff-': eff -= w
                elif kind == 'fix+': fixed[str(S)] = str(F(fixed.get(str(S), '0')) + (w if mode == 'min' else -w))
                elif kind == 'fix-': fixed[str(S)] = str(F(fixed.get(str(S), '0')) - (w if mode == 'min' else -w))
                elif kind == 'stage': stage[str(S)] = str(w)
                elif kind == 'nonneg': rows[str(1 << S)] = str(F(rows.get(str(1 << S), '0')) + w)
            stages.append({'player': c['player'], 'level': str(c['level']), 'rows': rows, 'eff': str(eff), 'fixed': fixed, 'stage': stage})
        out[mode] = {'point': [str(a) for a in y], 'certificates': stages}
    return out

if __name__ == '__main__':
    gens = json.loads(sys.argv[1]); n = len(gens[0])
    if len(sys.argv) > 2:
        json.dump(bundle(gens), open(sys.argv[2], 'w'), indent=1); print('bundle written', sys.argv[2]); raise SystemExit
    for mode in ('min', 'max'):
        certs, y, tight = stage_certs(gens, mode)
        print(f'== L{mode}: y = {[str(a) for a in y]}; tight rows: {[members(S,n) for S in tight]}')
        for c in certs:
            print(f"  player {c['player']} at level {c['level']}: " + ', '.join(f"{k[0]}{'' if k[1] is None else members(k[1],n) if k[0]=='row' else k[1]}x{w}" for k, w in c['certificate']))
