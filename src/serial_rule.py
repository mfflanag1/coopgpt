"""Serial rule for veto-balanced games (Arin-Feltkamp-Montero 2012, Sec 3.2).
On veto-balanced games this COINCIDES with the SD-prenucleolus (Arin-Katsev),
so it doubles as validated SD-prenucleolus machinery on that subclass.

d_i = max_{S subseteq N\\{i}} v(S);  sort players by nondecreasing d;
d_{n+1} = v(N);  phi_l = sum_{i=l..n} (d_{i+1} - d_i)/i   (in sorted order).
"""
from fractions import Fraction as F
from tugame import Game

def strengths(game):
    n, N = game.n, game.N
    d = []
    for i in range(n):
        mask = N ^ (1 << i)
        best = F(0)
        S = mask
        while S:
            if game.v[S] > best:
                best = game.v[S]
            S = (S - 1) & mask
        d.append(best)
    return d

def serial_rule(game):
    """Returns payoff vector in ORIGINAL player order."""
    n = game.n
    d = strengths(game)
    order = sorted(range(n), key=lambda i: d[i])
    ds = [d[i] for i in order] + [game.v[game.N]]
    phi_sorted = []
    for l in range(n):
        phi_sorted.append(sum((ds[i + 1] - ds[i]) / F(i + 1) for i in range(l, n)))
    phi = [F(0)] * n
    for pos, orig in enumerate(order):
        phi[orig] = phi_sorted[pos]
    return phi

if __name__ == "__main__":
    # Example 2 from Arin-Feltkamp-Montero 2012 (verbatim unit test)
    v = [F(0)] * 16
    v[0b0111] = 8   # {1,2,3}
    v[0b1011] = 8   # {1,2,4}
    v[0b1101] = 6   # {1,3,4}
    v[0b1111] = 12
    g = Game(4, v)
    d = strengths(g)
    phi = serial_rule(g)
    print("d =", [str(x) for x in d], "(expect 0,6,8,8)")
    print("phi =", [str(x) for x in phi], "(expect 8,2,1,1)")
    assert d == [F(0), F(6), F(8), F(8)]
    assert phi == [F(8), F(2), F(1), F(1)]
    assert g.in_core(phi)
    print("SERIAL RULE VALIDATED against worked example; core membership exact")
