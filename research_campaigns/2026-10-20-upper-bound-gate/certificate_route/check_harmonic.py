from fractions import Fraction as Q
import json


def check(m):
    assert m >= 2
    H = [Q(0)]
    for k in range(1, m):
        H.append(H[-1] + Q(1, k))
    t = [1 + Q(k, m - 1) for k in range(m)]
    div = [H[k] - H[m - 1 - k] for k in range(m)]
    nu = [max(Q(1), d) for d in div]
    rest = [Q(0)] * m
    gross_in = Q(0)
    gross_out = Q(0)
    mass = Q(0)
    delta = Q(0)
    passive_count = 0
    for i in range(m):
        for j in range(i + 1, m):
            mu = Q(1, j - i)
            rest[i] -= mu
            rest[j] += mu
            # The actual owner a_ij occurs in exactly this one edge;
            # its only two nonzero balance coordinates are -mu, +mu.
            assert -mu <= nu[i] and mu <= nu[j]
            gross_in += mu * t[j]
            gross_out += mu * t[i]
            mass += mu
            delta += mu * (t[j] - t[i])
            passive_count += 1
    assert rest == div
    rest[0] += 1  # coverage of the restorer and cap at the first profile
    assert all(g <= v for g, v in zip(rest, nu))
    assert nu[0] >= 1  # cap-owner coverage coefficient
    D = sum(v * x for v, x in zip(nu, t))
    sigma_u = sum((v - g) * x for v, g, x in zip(nu, rest, t))
    assert mass == m * H[-1] - (m - 1)
    assert delta == Q(m, 2)
    assert gross_in - gross_out == delta
    assert gross_in >= mass
    assert sum(nu) <= 2 * m - 1
    assert D <= 4 * m - 2
    assert 1 - D == -delta - sigma_u
    assert D - delta >= 0  # first resource coordinate of RC
    return {
        'profiles': m,
        'actual_owners': 2 + passive_count,
        'shared_coalition_edges': passive_count,
        'arity': 3,
        'protection_size': 2,
        'dual_objective': '1',
        'D_exact': str(D),
        'incoming_surplus_exact': str(gross_in),
        'outgoing_surplus_exact': str(gross_out),
        'incoming_surplus_over_D': float(gross_in / D),
        'proved_ratio_lower_bound': float(mass / (4 * m - 2)),
        'actual_weighted_price_defect_exact': str(-delta),
        'all_checks_passed': True,
    }

if __name__ == '__main__':
    results = [check(m) for m in [2, 3, 4, 8, 16, 32, 64, 128, 256]]
    print(json.dumps({'evidence': 'exact finite checks supplementing the symbolic proof', 'results': results}, indent=2))
