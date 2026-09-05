"""Sparse integer 3-sided assignment family with full-selector distance tending to 2.

Raw model includes all unlisted complete triples at value zero.  Every player,
including the forced-zero local and global dummies, is counted.  Dependencies:
standard Python only.  The proof does not rely on numerical optimization.
"""
from fractions import Fraction as F


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def build_family(levels, copies):
    """Return sectors, sparse weights, matching, and exact proposed selectors.

    levels >= 1, copies >= 0. Each copy duplicates all three top-level pairs.
    Labels are strings; sparse weights map ordered (A-label,B-label,C-label).
    """
    require(isinstance(levels, int) and levels >= 1, 'levels must be an integer >= 1')
    require(isinstance(copies, int) and copies >= 0, 'copies must be an integer >= 0')
    sectors = [[], [], []]
    color = {}
    weights = {}
    matching = []
    pairs = {}
    metadata = {}

    def player(name, sector):
        require(name not in color, 'duplicate player')
        sectors[sector].append(name)
        color[name] = sector
        return name

    def edge(names, value):
        require(len(set(names)) == 3 and {color[n] for n in names} == {0, 1, 2}, 'invalid colored triple')
        ordered = tuple(sorted(names, key=color.__getitem__))
        require(value >= 0, 'negative weight')
        require(ordered not in weights or weights[ordered] == value, 'conflicting duplicate weights')
        weights[ordered] = value
        return ordered

    globals_ = [player(f'G:{i}', i) for i in range(3)]

    def pair(block, i, parity, total, source_level):
        ucolor, vcolor = ((i, (i+1) % 3) if parity == 0 else ((i+1) % 3, i))
        dcolor = (i+2) % 3
        u = player(f'U:{block}:{i}', ucolor)
        v = player(f'V:{block}:{i}', vcolor)
        d = player(f'D:{block}:{i}', dcolor)
        matching.append(edge((u, v, d), total))
        edge((u, v, globals_[dcolor]), total)
        pairs[block, i] = (u, v, d)
        metadata[u] = ('U', source_level, i)
        metadata[v] = ('V', source_level, i)
        metadata[d] = ('D', source_level, i)
        return u, v, d

    for level in range(levels+1):
        for i in range(3):
            u, v, d = pair(f'L{level}', i, level % 2, 2 if level == 0 else 1, level)
            if level == 0:
                edge((u, *[globals_[j] for j in range(3) if j != color[u]]), 1)
            else:
                children = [j for j in range(3) if j != i]
                edge((u, *[pairs[f'L{level-1}', j][1] for j in children]), 2)
                edge((v, *[pairs[f'L{level-1}', j][0] for j in children]), 3 if level == 1 else 1)

    for copy in range(copies):
        for i in range(3):
            u, v, d = pair(f'R{copy}', i, levels % 2, 1, levels)
            top_u, top_v, _ = pairs[f'L{levels}', i]
            g = globals_[(i+2) % 3]
            edge((u, top_v, g), 1)
            edge((v, top_u, g), 1)

    total = 3*(levels+copies+2)
    t = F(1, 2**levels+2)
    lmin, lmax = {}, {}
    for name in color:
        if name in globals_ or metadata[name][0] == 'D':
            lmin[name] = lmax[name] = F(0)
            continue
        kind, level, _ = metadata[name]
        q = 2**level*t
        baseline = 1 if kind == 'V' or level == 0 else 0
        lmin[name] = F(baseline) + (q if kind == 'U' else -q)
        lmax[name] = F(baseline)
    expected_rho = F(2*((copies+2)*2**levels-1), (2**levels+2)*(levels+copies+2))
    require(sum(lmin.values()) == total and sum(lmax.values()) == total, 'selector total mismatch')
    require(sum(abs(lmin[n]-lmax[n]) for n in color)/total == expected_rho, 'distance formula mismatch')
    covered = [name for e in matching for name in e]
    require(len(set(covered)) == len(covered), 'matching overlaps')
    require(sum(weights[e] for e in matching) == total, 'matching value mismatch')
    for label, p in [('lmin', lmin), ('lmax', lmax)]:
        require(all(value >= 0 for value in p.values()), f'{label} violates nonnegativity')
        require(all(sum(p[n] for n in e) >= value for e, value in weights.items()), f'{label} violates a raw triple constraint')
    return dict(sectors=sectors, weights=weights, matching=matching, total=total,
                lmin=lmin, lmax=lmax, rho=expected_rho, pairs=pairs,
                globals=globals_, levels=levels, copies=copies)


if __name__ == '__main__':
    for levels, copies in [(1, 0), (2, 1), (3, 9), (4, 16), (8, 64), (12, 144), (16, 256), (32, 1024)]:
        game = build_family(levels, copies)
        print(dict(levels=levels, copies=copies, n=sum(map(len, game['sectors'])), T=game['total'],
                   edges=len(game['weights']), rho=str(game['rho']), approx=float(game['rho'])))
